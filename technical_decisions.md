# Technical Decisions Log

This document records all architectural and technical decisions made during the development of the Playstats dashboard.

| ID | Date | Decision | Rationale | Impact / Scope |
|---|---|---|---|---|
| TD-001 | 2026-09-25 | Use `genre_map.json` instead of `genre_map.py` | Static JSON configuration allows user editing without modifying Python code and keeps data mapping decoupled from logic. | Replaces `genre_map.py` with `genre_map.json`. Loaded in `data_processing.py`. |
| TD-002 | 2026-09-25 | Mandatory Technical & Bug Logging | Maintain explicit markdown logs (`technical_decisions.md` and `bug_log.md`) across all implementation phases. | Ensures full auditability, reproducibility, and tracking of development choices and issues. |
| TD-003 | 2026-09-25 | Flexible JSON Genre Lookup Format | Support both single genre strings and list of genres in `genre_map.json` (`games` dict), while ensuring `data_processing.py` extracts the primary genre (first element if list). | Prevents key errors / mapping errors regardless of user formatting in `genre_map.json`. |
| TD-004 | 2026-09-25 | Multi-Genre Playtime Attribution for Radar Chart (Option B) | If a game is mapped to multiple genres in `genre_map.json` (e.g. `["Action", "RPG"]`), the session's duration is credited to each listed genre in the Radar chart calculation. | Reflects full time investment in each genre. Donut chart remains game-based (single 100% total). |
