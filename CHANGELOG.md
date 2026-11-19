# CHANGELOG

All notable changes to the Sales Analytics Workbench are documented here.
Format follows Keep a Changelog; versions follow Semantic Versioning.

## [0.1.0] — 2026-11-19

### Increment 1A — Project Foundation and Runnable Streamlit Shell

#### Added
- `pyproject.toml` — Ruff and Black configuration (Python 3.14, line length 88,
  rules E/F/W/I/B/UP/TID; Streamlit banned in `services/`, `models/`, `database/`;
  per-file TID251 exemption for presentation layers and tests).
- `requirements.txt` — pinned runtime dependencies: streamlit 1.49.1, pandas 2.3.3,
  numpy 2.5.5, plotly 7.1.0, scipy 1.18.1, openpyxl 3.1.5.
- `requirements-dev.txt` — pinned dev tooling: pytest 9.2.0, ruff 0.17.5, black 26.10.1.
- `app/__init__.py` and package `__init__.py` files for `utils/`, `pages/`,
  `services/`, `database/`, `models/`, `components/`.
- `app/main.py` — entry point: `st.set_page_config`, five-page `st.navigation`
  registry in approved order, dark navy theme injection, sidebar identity,
  session-state seeding (`raw_df`, `active_df`, `cleaning_history`, `db_conn`),
  landing content.
- `app/utils/styling.py` — dark navy executive theme tokens and CSS.
- `app/utils/logger.py` — structured logging configuration.
- `app/pages/01_data_immersion.py` … `app/pages/05_statistical_validation.py` —
  five module stubs; each renders an empty state when `active_df` is `None`.
- `tests/unit/test_app_smoke.py` — genuine Streamlit `AppTest` smoke suite (6 tests).

#### Changed
- `.gitignore` — added `!app/assets/power_bi/*.png` exception so the approved
  Power BI dashboard screenshot can be committed while all other image and
  data exclusions are preserved.

#### Corrected during implementation
- `st.Page()` paths are resolved relative to the main script directory
  (`app/main.py`), so paths are `pages/*.py`, not `app/pages/*.py`.

### Verification (Increment 1A)

| Gate | Command | Result |
|---|---|---|
| Lint | `ruff check app tests` | ✅ All checks passed |
| Format (ruff) | `ruff format --check app tests` | ✅ 16 files already formatted |
| Format (black) | `black --check app tests` | ✅ 14 files would be left unchanged |
| Tests | `pytest tests/unit/test_app_smoke.py` | ✅ 6 passed |

Smoke test coverage (all verified passing):
1. `test_main_app_runs_without_exception` — main script runs with no exception.
2. `test_pages_run_headlessly` — all five page scripts run with seeded session state.
3. `test_navigation_registry_order` — AST parse of `main.py` confirms the five
   `st.Page` titles are declared in the approved order.
4. `test_empty_state_and_theme` — theme CSS (`#0B132B`) injected as HTML; landing
   title rendered; "No dataset loaded" empty state present.
5. `test_no_streamlit_import_in_non_presentation_modules` — AST scan of
   `services/`, `models/`, `database/` finds zero Streamlit imports.
6. `test_approved_paths_exist` — `main.py` and all five page scripts exist.

Environment verified unchanged: Python 3.14.6; no runtime package upgraded;
ruff 0.17.5 and black 26.10.1 installed into `.venv` only.

### Git status
- Nothing staged; nothing committed; nothing pushed.
- Proceeding to the ten-step Git checkpoint for explicit authorization.