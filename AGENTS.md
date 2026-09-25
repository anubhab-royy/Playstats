# AGENTS.md

Instructions for any AI coding agent (Claude Code, Cursor, Copilot Workspace,
etc.) working on this repository. Read this before writing or changing code.

## Project intent

A **simple, minimalistic** single-page gaming dashboard. "Simple" is a
requirement, not a placeholder — resist the urge to add features, pages,
auth, databases, or configuration options that were not asked for.

## Hard scope boundaries

Do NOT add, unless explicitly asked:
- A database (SQLite/Postgres/etc.) — the CSV file is the only data store.
- User authentication / login / multi-user support.
- A backend API (Flask/FastAPI) separate from Streamlit — Streamlit is both
  frontend and app logic here.
- Extra pages, tabs, or navigation — this is a single-view dashboard.
- Additional chart types beyond: Donut, Radar, Histogram (x2), and the
  textual insight blocks specified in `architecture.md`.
- Real-time/auto-refresh, websockets, or polling.
- External API calls (e.g. calling out to a game-genre lookup service).
  Genre mapping is a static JSON file — see `genre_map.json`.

## Data contract

Only these 4 columns from the source CSV are used, regardless of what else
exists in the export:
- `Session ID` (or `ID`)
- `Game Name`
- `Started At` (ISO 8601 timestamp, may include timezone offset)
- `Ended At` (ISO 8601 timestamp, may include timezone offset)

Duration is always derived (`Ended At - Started At`), never read from a
precomputed column, to keep the data contract minimal and self-consistent.

Timestamps may or may not carry a UTC offset (`+00:00`) within the same
file. Normalize all timestamps to a single timezone (naive local time, or
UTC — pick one in `data_processing.py` and apply it consistently) before
any date-based grouping (month/week/day-of-week/hour-of-day).

## Genre mapping

There is no reliable free API for game→genre lookup at the scale/cost this
project justifies. Genre is resolved via a manual JSON file: `genre_map.json`.

Structure:

```json
{
  "games": {
    "Valorant": "Shooter",
    "Counter Strike 2": "Shooter",
    "Ghost of Tsushima": "Action",
    "Robolox": "Simulation",
    "Life Is Strange": "Adventure"
  },
  "genres": ["Action", "Adventure", "RPG", ...],
  "fallback": "Unmapped"
}
```

Agents should:
- Add new games to the `"games"` dict when encountered in sample data, using
  best judgement for the primary genre (one genre per game, not multiple).
- Never invent a genre-detection heuristic (string matching, ML classifier,
  web lookup) unless the user explicitly requests it.
- Leave unmapped games bucketed as `"Unmapped"` rather than guessing loudly
  or crashing.
- Keep the `"genres"` array (10 fixed categories) in the same order across
  all code — it defines the Radar chart axis order and ensures consistency
  month to month.

## Coding conventions

- **Language:** Python 3.11+
- **Formatting:** follow `black` defaults (no custom line-length rules).
- **File separation is intentional** — keep it exactly as in `README.md`'s
  repo structure:
  - `app.py` — layout/composition only (Streamlit calls, `st.columns`, etc.)
  - `data_processing.py` — all pandas transforms and metric calculations
  - `charts.py` — all Plotly figure-building functions, one function per
    chart, each returning a `go.Figure`
  - `genre_map.json` — the static game→genre lookup (user-editable)
- Do not put data logic inside `app.py` and do not put Streamlit calls
  (`st.*`) inside `data_processing.py` or `charts.py`. This separation
  keeps the app testable and keeps agent edits localized.
- Keep functions small and named after the metric they compute, e.g.
  `get_top_n_games_by_month(df, n=3)`, `get_longest_streak(df)`.

## Visual style

- Minimalistic: no heavy borders, no drop shadows, no animated transitions.
- A single consistent color per game across the Donut and Radar charts
  (define a shared color map once, reuse everywhere) so the same game is
  visually identifiable in both charts.
- Use Streamlit's default theme unless the user asks for custom theming.
- Do not add a sidebar unless asked — layout is a fixed 2-column grid as
  described in `README.md` and `architecture.md`.

## When making changes

1. Check `implementation_plan.md` for current build phase/status before
   adding new work — don't jump ahead or redo completed phases.
2. If a request conflicts with a "hard scope boundary" above, flag the
   conflict to the user instead of silently expanding scope.
3. Update `implementation_plan.md`'s status checklist when a phase is
   completed.
4. Do not modify the data contract (the 4-column assumption) without the
   user confirming the source CSV format has changed.
