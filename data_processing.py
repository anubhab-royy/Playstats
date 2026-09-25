import json
import os
from typing import Dict, List, Union
import pandas as pd


def load_genre_map(genre_map_path: str = "genre_map.json") -> Dict:
    """Loads genre mapping configuration from a JSON file."""
    if not os.path.exists(genre_map_path):
        return {
            "games": {},
            "genres": [
                "Action", "Adventure", "RPG", "Strategy", "Simulation",
                "Sports", "Racing", "Puzzle", "Shooter", "Fighting"
            ],
            "fallback": "Unmapped"
        }
    with open(genre_map_path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_data(
    source: Union[str, pd.DataFrame],
    genre_map_path: str = "genre_map.json",
    tz: str = "Asia/Kolkata"
) -> pd.DataFrame:
    """
    Reads CSV or DataFrame, enforces the 4-column data contract, normalizes timestamps,
    and derives Duration, Duration_Hours, Genres, Hour, Weekday, Date, and Month.
    """
    if isinstance(source, pd.DataFrame):
        df = source.copy()
    else:
        df = pd.read_csv(source)

    # Standardize column names (Session ID vs ID)
    col_map = {}
    for col in df.columns:
        c_lower = col.strip().lower()
        if c_lower in ["session id", "id"]:
            col_map[col] = "Session ID"
        elif c_lower == "game name":
            col_map[col] = "Game Name"
        elif c_lower == "started at":
            col_map[col] = "Started At"
        elif c_lower == "ended at":
            col_map[col] = "Ended At"

    df = df.rename(columns=col_map)
    required_cols = ["Session ID", "Game Name", "Started At", "Ended At"]
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise ValueError(f"CSV is missing required contract columns: {missing}")

    df = df[required_cols].copy()

    # Parse and normalize timestamps to localized naive datetime
    started_dt = pd.to_datetime(df["Started At"], utc=True)
    ended_dt = pd.to_datetime(df["Ended At"], utc=True)

    if tz:
        df["Started At"] = started_dt.dt.tz_convert(tz).dt.tz_localize(None)
        df["Ended At"] = ended_dt.dt.tz_convert(tz).dt.tz_localize(None)
    else:
        df["Started At"] = started_dt.dt.tz_localize(None)
        df["Ended At"] = ended_dt.dt.tz_localize(None)

    # Compute duration
    df["Duration"] = df["Ended At"] - df["Started At"]
    df["Duration_Hours"] = df["Duration"].dt.total_seconds() / 3600.0

    # Load genre map
    genre_config = load_genre_map(genre_map_path)
    games_map = genre_config.get("games", {})
    fallback = genre_config.get("fallback", "Unmapped")

    def map_genres(game_name: str) -> List[str]:
        if not isinstance(game_name, str):
            return [fallback]
        res = games_map.get(game_name, games_map.get(game_name.strip(), fallback))
        if isinstance(res, str):
            return [res]
        elif isinstance(res, list) and len(res) > 0:
            return res
        return [fallback]

    df["Genres"] = df["Game Name"].apply(map_genres)
    df["Primary_Genre"] = df["Genres"].apply(lambda g: g[0] if isinstance(g, list) and len(g) > 0 else fallback)

    # Derived time dimensions
    df["Hour"] = df["Started At"].dt.hour
    df["Weekday"] = df["Started At"].dt.day_name()
    df["Date"] = df["Started At"].dt.date
    df["Month"] = df["Started At"].dt.to_period("M")

    return df


def _get_target_month(df: pd.DataFrame) -> pd.Period:
    """Helper to return current calendar month if present, else latest month in df."""
    if df.empty:
        return pd.Period.now("M")
    current_month = pd.Timestamp.now().to_period("M")
    if current_month in df["Month"].values:
        return current_month
    return df["Month"].max()


def get_top_n_games_current_month(df: pd.DataFrame, n: int = 3) -> pd.DataFrame:
    """Returns top N games by total duration in hours for the target month."""
    if df.empty:
        return pd.DataFrame(columns=["Game Name", "Duration_Hours"])
    target_month = _get_target_month(df)
    m_df = df[df["Month"] == target_month]
    top_df = (
        m_df.groupby("Game Name")["Duration_Hours"]
        .sum()
        .reset_index()
        .sort_values(by="Duration_Hours", ascending=False)
        .head(n)
    )
    return top_df


def get_playtime_share_all_games(df: pd.DataFrame) -> pd.DataFrame:
    """Groups all-time playtime by game name."""
    if df.empty:
        return pd.DataFrame(columns=["Game Name", "Duration_Hours"])
    share_df = (
        df.groupby("Game Name")["Duration_Hours"]
        .sum()
        .reset_index()
        .sort_values(by="Duration_Hours", ascending=False)
    )
    return share_df


def get_genre_playtime_current_month(
    df: pd.DataFrame, genre_map_path: str = "genre_map.json"
) -> pd.Series:
    """
    Computes total playtime per genre for the target month.
    Implements Option B: credits full session hours to each genre in session's genre list.
    Always returns all 10 fixed genres in exact order.
    """
    genre_config = load_genre_map(genre_map_path)
    fixed_genres = genre_config.get(
        "genres",
        [
            "Action", "Adventure", "RPG", "Strategy", "Simulation",
            "Sports", "Racing", "Puzzle", "Shooter", "Fighting"
        ],
    )
    fallback = genre_config.get("fallback", "Unmapped")

    if df.empty:
        return pd.Series(0.0, index=fixed_genres)

    target_month = _get_target_month(df)
    m_df = df[df["Month"] == target_month]

    genre_totals = {g: 0.0 for g in fixed_genres}
    if fallback not in genre_totals:
        genre_totals[fallback] = 0.0

    for _, row in m_df.iterrows():
        hrs = row["Duration_Hours"]
        genres = row["Genres"]
        for g in genres:
            genre_totals[g] = genre_totals.get(g, 0.0) + hrs

    # Return series ordered by fixed_genres (plus fallback if present and > 0)
    series_data = {g: genre_totals.get(g, 0.0) for g in fixed_genres}
    return pd.Series(series_data)


def get_total_playtime(df: pd.DataFrame, period: str = "month") -> float:
    """Calculates total playtime in hours for current month or ISO week."""
    if df.empty:
        return 0.0
    if period == "month":
        target_month = _get_target_month(df)
        sub_df = df[df["Month"] == target_month]
    elif period == "week":
        # Target latest ISO week in df or current week
        now_week = pd.Timestamp.now().isocalendar()
        df_weeks = df["Started At"].dt.isocalendar()
        target_year_week = (now_week.year, now_week.week)
        match = df[(df_weeks["year"] == target_year_week[0]) & (df_weeks["week"] == target_year_week[1])]
        if not match.empty:
            sub_df = match
        else:
            latest_idx = df["Started At"].idxmax()
            latest_row_week = df.loc[latest_idx, "Started At"].isocalendar()
            sub_df = df[(df_weeks["year"] == latest_row_week.year) & (df_weeks["week"] == latest_row_week.week)]
    else:
        sub_df = df

    return float(sub_df["Duration_Hours"].sum())


def get_longest_streak_current_month(df: pd.DataFrame) -> int:
    """Calculates longest consecutive calendar days streak with at least 1 session in target month."""
    if df.empty:
        return 0
    target_month = _get_target_month(df)
    m_df = df[df["Month"] == target_month]
    if m_df.empty:
        return 0

    unique_dates = sorted(m_df["Date"].unique())
    if not unique_dates:
        return 0

    max_streak = 1
    current_streak = 1

    for i in range(1, len(unique_dates)):
        delta = (unique_dates[i] - unique_dates[i - 1]).days
        if delta == 1:
            current_streak += 1
            max_streak = max(max_streak, current_streak)
        elif delta > 1:
            current_streak = 1

    return max_streak


def get_sessions_by_hour(df: pd.DataFrame) -> pd.Series:
    """Session count per hour (0–23) for the target month."""
    hours = list(range(24))
    if df.empty:
        return pd.Series(0, index=hours)
    target_month = _get_target_month(df)
    m_df = df[df["Month"] == target_month]
    counts = m_df["Hour"].value_counts().reindex(hours, fill_value=0)
    return counts


def get_sessions_by_weekday(df: pd.DataFrame) -> pd.Series:
    """Session count per day of week (Mon–Sun) for the target month."""
    weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    if df.empty:
        return pd.Series(0, index=weekdays)
    target_month = _get_target_month(df)
    m_df = df[df["Month"] == target_month]
    counts = m_df["Weekday"].value_counts().reindex(weekdays, fill_value=0)
    return counts
