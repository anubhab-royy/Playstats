# Implementation Plan

Build order for an agent to follow. Do phases in sequence — don't start
Phase 3 chart work before Phase 2 data functions exist and are correct,
since every chart consumes a specific data function's output.

## Open questions to confirm before/while building

These are assumptions made in `architecture.md`. Flag them to the user
if not yet answered, rather than silently picking one:

1. **Donut scope:** all-time playtime share (current assumption) or
   current-month only, to match Top-3/Radar framing?
2. **Lower histograms scope:** current month (current assumption) or
   all-time?
3. **Local timezone constant:** which timezone should calendar grouping
   (month/week/weekday/hour) use? Needed because source timestamps are
   inconsistently UTC-offset-tagged.
4. **Data source:** is the CSV a static file committed to the repo, or
   should the dashboard support re-uploading a fresh export via
   `st.file_uploader`? Affects `app.py` and whether the CSV is committed
   at all (a personal data file probably should NOT be committed to a
   public GitHub repo — see Phase 5).

## Phase 0 — Setup

- [ ] Initialize repo with `requirements.txt`:
  ```
  streamlit
  pandas
  plotly
  ```
- [ ] Create empty module files: `app.py`, `data_processing.py`,
      `charts.py`, `genre_map.json`.
- [ ] Confirm the 4 open questions above with the user, or proceed with
      commit message.

## Phase 1 — Genre map

- [x] Ensure `genre_map.json` is in the repo root (pre-populated with ~300
      games and all 10 fixed genres).
- [x] Verify initial entries match known games in the sample data
      (Counter Strike 2, Life Is Strange, Valorant, Ghost of Tsushima,
      Robolox, eFootball).
- [x] Note: the JSON is user-editable and can be updated without touching
      code. Agents should add new games as they appear in Phase 2 testing.

## Phase 2 — Data processing

- [x] `load_data()` — read CSV, keep 4 contract columns only, parse +
      normalize timestamps (resolve open question #3 first), derive
      `Duration`, `Duration_Hours`, `Genre`, `Hour`, `Weekday`, `Month`.
- [x] `get_top_n_games_current_month()`
- [x] `get_playtime_share_all_games()` (or month-scoped, per open
      question #1)
- [x] `get_genre_playtime_current_month()` — must return all 10 fixed
      genres even at zero, for a stable Radar shape.
- [x] `get_total_playtime(period="month")` and `period="week"`
- [x] `get_longest_streak_current_month()`
- [x] `get_sessions_by_hour()`
- [x] `get_sessions_by_weekday()`
- [x] Sanity-check each function manually against the sample CSV
      (`sessionist_export.csv`) before moving to Phase 3 — e.g. hand-
      verify the Top-3 ranking and the longest streak by eye.

## Phase 3 — Charts

- [x] Define a shared `GAME_COLOR_MAP` (consistent color per game name)
      used by any chart that breaks down by game.
- [x] `build_donut()` — labels = game names, values = hours, shows %
      share on hover/label.
- [x] `build_radar()` — one axis per genre (fixed order from
      `genre_map.GENRES`), values = hours this month.
- [x] `build_hour_histogram()` — x = hour (0–23), y = session count.
- [x] `build_weekday_histogram()` — x = weekday (Mon–Sun, fixed order),
      y = session count.
- [x] Keep all chart styling minimal: no legends cluttering small chart
      space unless needed, consistent font size, transparent/plain
      background matching Streamlit's default theme.

## Phase 4 — Layout (`app.py`)

- [ ] `@st.cache_data`-wrap the data load call.
- [ ] Build the 2-column x 3-row grid per the layout table in
      `architecture.md`.
- [ ] Upper-left: render Top-3 as plain text/`st.metric` ranking
      (Game — hours), not a chart.
- [ ] Upper-right: `st.plotly_chart(build_donut(...))`.
- [ ] Middle-left: `st.plotly_chart(build_radar(...))`.
- [ ] Middle-rest: three `st.metric()` calls — Month total, Week total,
      Longest streak.
- [ ] Lower-left / lower-right: the two histograms.
- [ ] Page title + minimal page config (`st.set_page_config(layout="wide")`
      recommended so the 2-column grid isn't cramped).

## Phase 5 — Data handling & privacy

- [ ] Decide (per open question #4): commit `sessionist_export.csv`
      directly, or gitignore it and require local placement / upload.
      **Recommendation:** gitignore the real CSV if this repo is public,
      commit a small anonymized/sample CSV instead so the app runs
      out-of-the-box for anyone cloning it, and let the real personal
      data be supplied locally or via `st.file_uploader`.
- [ ] If uploader is added: guard against missing/malformed columns with
      a clear `st.error()` message, not a stack trace.

## Phase 6 — Deployment

- [ ] Push repo to GitHub.
- [ ] Connect repo on [share.streamlit.io](https://share.streamlit.io),
      set entry point to `app.py`.
- [ ] Verify the deployed app loads the correct CSV (committed sample or
      upload flow) and all 6 layout regions render without errors.
- [ ] Confirm auto-redeploy works on a trivial follow-up commit.

## Status

_(Agent: update this checklist as phases complete. Do not mark a phase
done until its own checklist items are all checked.)_

- [x] Phase 0 — Setup
- [x] Phase 1 — Genre map
- [x] Phase 2 — Data processing
- [x] Phase 3 — Charts
- [ ] Phase 4 — Layout
- [ ] Phase 5 — Data handling & privacy
- [ ] Phase 6 — Deployment
