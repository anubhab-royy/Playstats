# Architecture

## Overview

Single-process Streamlit app. No backend, no database, no API layer.
Data flows one direction: CSV → pandas DataFrame → derived metrics →
Plotly figures → Streamlit layout.

```
sessionist_export.csv
        │
        ▼
data_processing.load_data()          # read, normalize timezones, derive Duration
        │
        ▼
data_processing.<metric functions>   # filtered/aggregated DataFrames or scalars
        │
        ▼
charts.<chart builder functions>     # go.Figure objects
        │
        ▼
app.py                               # st.columns() layout, calls above, renders
```

## Data contract (input)

Source: `sessionist_export.csv` (or user upload via `st.file_uploader`,
if that's enabled — optional, see `implementation_plan.md`).

Columns consumed:

| Column       | Type              | Notes                                   |
|--------------|-------------------|------------------------------------------|
| `Session ID` | int               | unique identifier, not used in charts    |
| `Game Name`  | string            | used for grouping in Top-3, Donut, color |
| `Started At` | ISO 8601 datetime | may or may not include UTC offset        |
| `Ended At`   | ISO 8601 datetime | same format caveats as above             |

All other columns in the source export (e.g. `Duration (Seconds)`,
`Duration (Formatted)`, `Notes`) are **ignored on load** — duration is
always recomputed from `Ended At - Started At` to keep a single source
of truth.

## Module responsibilities

### `data_processing.py`

- `load_data(path_or_buffer) -> pd.DataFrame`
  Reads CSV, keeps only the 4 contract columns, parses timestamps,
  normalizes timezone (strip/convert to a single consistent zone),
  adds derived columns: `Duration` (timedelta), `Duration_Hours` (float),
  `Genre` (via lookup from `genre_map.json`), `Hour` (0–23), `Weekday`
  (Mon–Sun), `Month` (period). Genre lookup uses the `games` dict from
  the JSON file, with unmapped games falling back to `"Unmapped"`.

- `get_top_n_games_current_month(df, n=3) -> pd.DataFrame`
  Filters to current calendar month, groups by `Game Name`, sums
  `Duration_Hours`, returns top N sorted descending.

- `get_playtime_share_all_games(df) -> pd.DataFrame`
  Groups by `Game Name` across all data (all-time), sums
  `Duration_Hours` — feeds the Donut chart.
  *(Decision: Donut is all-time, per the layout spec, distinct from the
  "current month" framing used in Top-3 and Radar — this is intentional,
  not an inconsistency. See open question note in
  `implementation_plan.md` if this should instead be month-scoped.)*

- `get_genre_playtime_all_time(df) -> pd.Series`
  Maps `Game Name` → `Genre` across all-time data, groups by genre, and
  sums hours. Always returns all 10 fixed genre categories (Action,
  Adventure, RPG, Strategy, Simulation, Sports, Racing, Puzzle, Shooter,
  Fighting) even if some are zero, so the Radar chart shape stays
  consistent.

- `get_total_playtime(df, period="month"|"week") -> float`
  Sums `Duration_Hours` for the current month or current ISO week.

- `get_longest_streak_current_month(df) -> int`
  Longest run of **consecutive calendar days** with at least one session,
  within the current month. Returns an integer day count.

- `get_sessions_by_hour(df) -> pd.Series`
  All-time session count per hour bucket (0–23), for the Hour-of-Day histogram.

- `get_sessions_by_weekday(df) -> pd.Series`
  All-time session count per weekday (Mon–Sun), for the Day-of-Week histogram.

### `genre_map.json` (loaded by `data_processing.py`)

Structure:
```json
{
  "games": { "Game Name": "Genre", ... },
  "genres": ["Action", "Adventure", "RPG", ...],
  "fallback": "Unmapped"
}
```

Loaded once on app startup (cached with `@st.cache_data`):
- `GAME_GENRE_MAP: dict[str, str]` from `games` field
- `GENRES: list[str]` from `genres` field (fixed 10-category list, in order)
- `GENRE_FALLBACK: str` from `fallback` field

The `genres` array order is locked — it defines the Radar chart axis order
and must remain consistent to keep the chart shape recognizable month to
month.

### `charts.py`

- `build_donut(playtime_share_df) -> go.Figure`
- `build_radar(genre_playtime_series) -> go.Figure`
- `build_hour_histogram(hourly_series) -> go.Figure`
- `build_weekday_histogram(weekday_series) -> go.Figure`

Each function takes already-computed data (never raw DataFrames straight
from `load_data`) and returns a ready-to-render `go.Figure`. A shared
`GAME_COLOR_MAP` (built once from the sorted list of distinct game names)
is passed in or imported so the Donut and any per-game coloring stay
consistent.

### `app.py`

- Calls `load_data()` once (cached with `@st.cache_data`).
- Lays out a 2-column, 3-row grid via `st.columns` / `st.container`
  matching the layout below.
- Calls the relevant `data_processing` function, then the relevant
  `charts` function, for each cell. No computation happens in `app.py`
  itself beyond simple formatting (e.g. rounding a number for display).

## Layout → module mapping

| Position       | Content                                   | Data function                              | Chart function          |
|----------------|--------------------------------------------|---------------------------------------------|--------------------------|
| Upper-left     | Top 3 games this month (text ranking)      | `get_top_n_games_current_month`             | — (`st.markdown`/`st.metric`) |
| Upper-right    | Donut — playtime share by game             | `get_playtime_share_all_games`              | `build_donut`            |
| Middle-left    | Radar — playtime by genre, current month   | `get_genre_playtime_current_month`          | `build_radar`            |
| Middle-rest    | Month total / Week total / Longest streak  | `get_total_playtime` (x2), `get_longest_streak_current_month` | — (`st.metric` x3) |
| Lower-left     | Histogram — sessions by hour of day        | `get_sessions_by_hour`                      | `build_hour_histogram`   |
| Lower-right    | Histogram — sessions by day of week        | `get_sessions_by_weekday`                   | `build_weekday_histogram`|

## Timezone normalization

Some rows in the source data carry a `+00:00` UTC offset, others don't
(mixed within the same file — confirmed from the sample export). Rule:
on load, parse all timestamps with `pd.to_datetime(..., utc=True)` to
force a consistent UTC baseline, then convert to the user's intended
local timezone (hardcode one, e.g. `Asia/Kolkata`, or read from a config
constant) before any calendar-based grouping (month, week, weekday,
hour). This avoids off-by-one-hour bugs in the histograms and off-by-one
day bugs in streak/week calculations.

## Caching

`load_data()` is wrapped in `@st.cache_data` so the CSV is only re-parsed
when the file changes or the app restarts — keeps the dashboard fast on
every interaction (Streamlit reruns the whole script on each widget
interaction).
