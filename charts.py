from typing import Dict, List, Optional
import pandas as pd
import plotly.graph_objects as go

# Curated harmonious color palette for consistent game identification
PALETTE = [
    "#6366F1",  # Indigo
    "#10B981",  # Emerald
    "#F59E0B",  # Amber
    "#EF4444",  # Red
    "#8B5CF6",  # Purple
    "#EC4899",  # Pink
    "#14B8A6",  # Teal
    "#F97316",  # Orange
    "#06B6D4",  # Cyan
    "#3B82F6",  # Blue
]


def get_game_color_map(game_names: List[str]) -> Dict[str, str]:
    """Returns a deterministic mapping of game names to colors."""
    sorted_games = sorted(list(set(game_names)))
    color_map = {}
    for idx, game in enumerate(sorted_games):
        color_map[game] = PALETTE[idx % len(PALETTE)]
    return color_map


def build_donut(
    share_df: pd.DataFrame,
    game_color_map: Optional[Dict[str, str]] = None
) -> go.Figure:
    """
    Builds a minimalistic Donut chart showing playtime share by game (all-time).
    """
    fig = go.Figure()

    if share_df.empty or "Duration_Hours" not in share_df.columns:
        fig.update_layout(
            annotations=[
                dict(
                    text="No session data available",
                    x=0.5,
                    y=0.5,
                    font_size=14,
                    showarrow=False,
                )
            ],
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        )
        return fig

    labels = share_df["Game Name"].tolist()
    values = share_df["Duration_Hours"].tolist()

    colors = None
    if game_color_map:
        colors = [game_color_map.get(g, "#6366F1") for g in labels]

    fig.add_trace(
        go.Pie(
            labels=labels,
            values=values,
            hole=0.55,
            textinfo="percent+label",
            textposition="inside",
            hovertemplate="<b>%{label}</b><br>Playtime: %{value:.2f} hrs (%{percent})<extra></extra>",
            marker=dict(colors=colors) if colors else None,
            showlegend=False,
        )
    )

    fig.update_layout(
        margin=dict(l=10, r=10, t=25, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="sans-serif", size=12),
        height=280,
    )
    return fig


def build_radar(genre_series: pd.Series) -> go.Figure:
    """
    Builds a minimalistic Radar chart of playtime by genre for the target month.
    """
    fig = go.Figure()

    if genre_series.empty:
        fig.update_layout(
            annotations=[
                dict(
                    text="No genre data available",
                    x=0.5,
                    y=0.5,
                    font_size=14,
                    showarrow=False,
                )
            ],
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        )
        return fig

    categories = list(genre_series.index)
    values = list(genre_series.values)

    # Close the polygon loop for radar chart
    categories_closed = categories + [categories[0]]
    values_closed = values + [values[0]]

    fig.add_trace(
        go.Scatterpolar(
            r=values_closed,
            theta=categories_closed,
            fill="toself",
            fillcolor="rgba(99, 102, 241, 0.25)",
            line=dict(color="#6366F1", width=2),
            marker=dict(size=4, color="#6366F1"),
            hovertemplate="<b>%{theta}</b><br>Playtime: %{r:.2f} hrs<extra></extra>",
            showlegend=False,
        )
    )

    max_val = max(values) if values and max(values) > 0 else 1.0

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, max_val * 1.15],
                showticklabels=False,
                ticks="",
                linecolor="rgba(150,150,150,0.2)",
                gridcolor="rgba(150,150,150,0.2)",
            ),
            angularaxis=dict(
                tickfont=dict(size=11),
                rotation=90,
                direction="clockwise",
                linecolor="rgba(150,150,150,0.2)",
                gridcolor="rgba(150,150,150,0.2)",
            ),
            bgcolor="rgba(0,0,0,0)",
        ),
        margin=dict(l=35, r=35, t=25, b=25),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="sans-serif", size=11),
        height=280,
    )
    return fig


def build_hour_histogram(hourly_series: pd.Series) -> go.Figure:
    """
    Builds a bar chart showing sessions by hour of day (0–23).
    """
    fig = go.Figure()

    hours = list(range(24))
    counts = [hourly_series.get(h, 0) for h in hours]
    hour_labels = [f"{h:02d}:00" for h in hours]

    fig.add_trace(
        go.Bar(
            x=hour_labels,
            y=counts,
            marker_color="#8B5CF6",
            hovertemplate="<b>%{x}</b><br>Sessions: %{y}<extra></extra>",
            showlegend=False,
        )
    )

    fig.update_layout(
        title=dict(text="Sessions by Hour of Day (All-Time)", font=dict(size=13)),
        margin=dict(l=20, r=20, t=35, b=30),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(
            title="",
            tickmode="linear",
            dtick=3,
            showgrid=False,
            zeroline=False,
            tickfont=dict(size=10),
        ),
        yaxis=dict(
            title="Sessions",
            showgrid=True,
            gridcolor="rgba(150,150,150,0.15)",
            zeroline=False,
            dtick=1 if max(counts + [1]) <= 10 else None,
            tickfont=dict(size=10),
        ),
        font=dict(family="sans-serif", size=11),
        height=240,
    )
    return fig


def build_weekday_histogram(weekday_series: pd.Series) -> go.Figure:
    """
    Builds a bar chart showing sessions by day of week (Mon–Sun).
    """
    fig = go.Figure()

    days_full = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    days_short = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

    counts = [weekday_series.get(day, 0) for day in days_full]

    fig.add_trace(
        go.Bar(
            x=days_short,
            y=counts,
            marker_color="#10B981",
            hovertemplate="<b>%{x}</b><br>Sessions: %{y}<extra></extra>",
            showlegend=False,
        )
    )

    fig.update_layout(
        title=dict(text="Sessions by Day of Week (All-Time)", font=dict(size=13)),
        margin=dict(l=20, r=20, t=35, b=30),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(
            title="",
            showgrid=False,
            zeroline=False,
            tickfont=dict(size=10),
        ),
        yaxis=dict(
            title="Sessions",
            showgrid=True,
            gridcolor="rgba(150,150,150,0.15)",
            zeroline=False,
            dtick=1 if max(counts + [1]) <= 10 else None,
            tickfont=dict(size=10),
        ),
        font=dict(family="sans-serif", size=11),
        height=240,
    )
    return fig
