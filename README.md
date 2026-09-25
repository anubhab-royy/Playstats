# Gaming Sessions Dashboard

A simple, minimalistic dashboard that turns a personal gaming-session log
(`Session ID`, `Game Name`, `Started At`, `Ended At`) into a handful of
clear insights: top games this month, playtime split, genre balance,
totals, and play-time patterns by hour and weekday.

Live version: `https://playstats.streamlit.app`

---

## What this is

- **Stack:** Python, pandas, Plotly, Streamlit
- **Hosting:** Streamlit Community Cloud (free tier)
- **Data:** a single CSV export (`sessionist_export.csv`) with 4 columns used:
  `ID`, `Game Name`, `Started At`, `Ended At`
- **Design intent:** minimal — one screen, no scrolling drilldowns, no login,
  no database. Re-running the app re-reads the CSV.

## Dashboard layout

```
┌─────────────────────────┬─────────────────────────┐
│ Top 3 Games (this month)│ Donut: playtime share    │
│ textual ranking by hrs  │ by game (all-time)       │
├─────────────────────────┼─────────────────────────┤
│ Radar: playtime by genre│ Totals:                  │
│ (this month)            │  - Month total           │
│                         │  - Week total             │
│                         │  - Longest streak (month) │
├─────────────────────────┴─────────────────────────┤
│ Histogram: sessions by  │ Histogram: sessions by    │
│ hour of day             │ day of week               │
└─────────────────────────┴─────────────────────────┘
```

## Repo structure

```
.
├── app.py                 # Streamlit entry point — layout only
├── data_processing.py     # All pandas logic: loading, filtering, metrics
├── charts.py              # All Plotly figure builders
├── genre_map.json         # Manual Game Name -> Genre lookup (user-editable)
├── sessionist_export.csv  # Data file (or user-uploaded via UI)
├── requirements.txt
├── README.md
├── AGENTS.md
├── architecture.md
└── implementation_plan.md
```

## Running locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploying (free, always-on)

1. Push this repo to GitHub (public or private).
2. Go to [share.streamlit.io](https://share.streamlit.io), sign in with GitHub.
3. Pick the repo, branch, and `app.py` as the entry point → Deploy.
4. Every `git push` to the connected branch auto-redeploys.

Note: free-tier Streamlit Cloud apps sleep after a period of inactivity and
wake on the next visit (a few seconds delay) — this is expected, not a bug.

## For AI coding agents

If you are an agent (Claude Code, Cursor, etc.) working on this repo, read
**`AGENTS.md` first** — it defines scope boundaries, coding conventions, and
what NOT to add. Then read `architecture.md` for how data flows through the
app, and `implementation_plan.md` for the build order and current status.
