# Bug & Debugging Log

This document records all bugs, runtime errors, data edge cases, and unexpected behaviors encountered during development, along with their root causes and resolutions.

| Bug ID | Phase / Date | Symptoms / Error Message | Root Cause | Resolution / Fix |
|---|---|---|---|---|
| BUG-000 | Phase 0 (2026-09-25) | Initial log setup | Baseline initialized | Operational tracking ready. |
| BUG-001 | Phase 1 (2026-09-25) | Potential key mismatches and duplicate game keys in `genre_map.json` | Sample export uses `Counter Strike 2` (no hyphen), while some logs use `Counter-Strike 2` | Added both variations (`Counter Strike 2` & `Counter-Strike 2`) and cleaned up duplicate JSON keys. |
| BUG-002 | Phase 2 (2026-09-25) | `ModuleNotFoundError: No module named 'pandas'` when executing `python` command | System path default `python` targeted Python 3.9 without installed packages, whereas `py` targeted Python 3.14 where requirements were installed | Executed installations and running commands via `py` launcher to target Python 3.14 environment. |
| BUG-003 | Phase 3 (2026-09-25) | Potential empty dataset / zero-duration rendering crashes in chart builders | Direct array indexing and max range calculation on empty DataFrames/Series | Implemented fallback annotations and non-zero max range guards across all 4 chart functions in `charts.py`. |
| BUG-004 | Phase 4 (2026-09-25) | Bare python module import warning for Streamlit runtime script context | Direct import of `app.py` in test scripts outside of `streamlit run` context | Encapsulated app execution inside `main()` entrypoint block and verified execution via `streamlit run`. |
| BUG-005 | Phase 4 (2026-09-25) | `ValueError: unconverted data remains when parsing with format "%Y-%m-%dT%H:%M:%S.%f": "+00:00"` | `pd.to_datetime` failed when CSV rows had mixed ISO 8601 timezone offsets (`+00:00`) | Added `_safe_parse_dt` helper in `data_processing.py` trying `format="ISO8601"` then `format="mixed"`. |
| BUG-006 | Phase 6 (2026-09-25) | `ModuleNotFoundError: No module named 'plotly'` on Streamlit Cloud deployment | Dependencies file was named `requirement.txt` (singular) instead of standard `requirements.txt` (plural), causing Streamlit Cloud builder to skip package installation | Created standard `requirements.txt` containing `streamlit`, `pandas`, `plotly` and removed legacy `requirement.txt`. |
