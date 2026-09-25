# Technical Decisions Log

This document records all architectural and technical decisions made during the development of the Playstats dashboard.

| ID | Date | Decision | Rationale | Impact / Scope |
|---|---|---|---|---|
| TD-001 | 2026-09-25 | Use `genre_map.json` instead of `genre_map.py` | Static JSON configuration allows user editing without modifying Python code and keeps data mapping decoupled from logic. | Replaces `genre_map.py` with `genre_map.json`. Loaded in `data_processing.py`. |
| TD-002 | 2026-09-25 | Mandatory Technical & Bug Logging | Maintain explicit markdown logs (`technical_decisions.md` and `bug_log.md`) across all implementation phases. | Ensures full auditability, reproducibility, and tracking of development choices and issues. |
