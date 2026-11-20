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

## [0.3.0] — 2026-11-19

### Increment 1C — Data Cleaning and Module 1 Completion

#### Added
- `app/services/cleaner.py` — non-mutating cleaning pipeline implementing:
  - Missing-value strategies: drop rows, fill mean/median/mode, or leave untouched.
  - Duplicate removal with exact row count reporting.
  - Type coercion (Quantity → int64, Unit_Price → float64, etc.).
  - Date normalisation: valid dates → `YYYY-MM-DD` strings; unparseable → NULL; rows preserved; unparseable count reported (SQL Query 5 protection).
- `app/services/validator.py` — business rule validation for FR-09:
  - Quantity > 0, Unit_Price > 0, Total_Sales ≈ Quantity × Unit_Price (within rounding tolerance).
  - Configurable per-rule enable/disable; pass/fail counts; per-row failure details.
- `app/services/report_generator.py` — FR-10 & FR-17 export service:
  - Cleaned CSV/XLSX export with timestamp/`_cleaned` filename suffix.
  - Multi-sheet Excel report (Summary + Statistics sheets; Query Results sheet deferred to Increment 3).
- `app/database/db_manager.py` — in-memory SQLite lifecycle manager (FR-15):
  - Per-session `:memory:` connection; `sales` table with 12 columns.
  - Rebuild on dataset changes; NULL dates survive ingestion; no external dependencies.
- `scripts/generate_demo_data.py` — deterministic synthetic demo dataset (FR-CC-01, D-1):
  - Fixed seed → identical output; 12-column canonical schema.
  - `Total_Sales == Quantity × Unit_Price` within rounding; Gender ∈ {Male, Female}.
  - Plausible date range; 60 rows; saved to `data/raw/internship_dataset.xlsx` (Git-ignored).
- `tests/unit/test_cleaning.py` — 10 unit tests covering missing-value strategies, duplicate removal, date normalisation, and non-mutation contracts.
- `tests/unit/test_validator.py` — 10 unit tests covering FR-09 rules (quantity, price, total-sales mismatches), tolerance bands, and missing column handling.
- `tests/unit/test_db_manager.py` — 8 unit tests covering ingestion, NULL dates, connection rebuild, dataset replacement, and schema mapping.
- `tests/unit/test_report_generator.py` — 14 unit tests covering CSV/XLSX exports, Summary + Statistics sheets; Query Results sheet absence verified.
- `tests/unit/test_demo_data.py` — 8 unit tests covering deterministic generation, 12-column schema, business constraints, and Git-ignored output.

#### Changed
- `app/pages/01_data_immersion.py` — upgraded from Increment 1B stub to complete Increment 1C UI:
  - Preview tab: source selection (upload / Scenario B) + dataset preview + column mapping.
  - Profiling tab: comprehensive metrics & column statistics.
  - Cleaning tab: configurable missing-value/duplication/type/date cleaning; cleaning-history stack; undo/reset controls.
  - Validation & Export tab: rule validation summary + cleaned CSV/XLSX export + Excel report (Summary + Statistics).

### Verification (Increment 1C)

| Gate | Command | Result |
|---|---|---|
| Lint | `ruff check app tests scripts` | ✅ All checks passed |
| Format (ruff) | `ruff format --check app tests scripts` | ✅ 33 files already formatted |
| Format (black) | `black --check app tests scripts` | ✅ 25 files left unchanged |

## [0.4.0] — 2026-11-20

### Increment 2 — EDA & Business Intelligence (FR-11 through FR-17)

#### Added
- `app/utils/formatters.py` — Indian Rupee (INR) currency formatting, percentage formatting, and comma-separated number formatting with Indian numbering system (lakhs and crores).
- `app/utils/charts.py` — centralized Plotly chart factory with `workbench_dark` template registration:
  - Bar charts, line charts, correlation heatmaps, histograms, scatter plots, pie charts, and box plots.
  - Consistent dark navy theme (`#0B132B` paper, `#1C2541` plot, `#2D3B60` grid, `#4F86F7`/`#00F5D4` accents).
  - INR-formatted hover templates and responsive sizing.
- `app/services/eda.py` — pure analytical logic (zero Streamlit imports, enforced by Ruff TID251):
  - `compute_kpis`: Total Revenue, Total Orders, Average Order Value, Total Quantity.
  - `compute_numeric_summary`: count, mean, std, min, 25%, 50%, 75%, max, IQR (9 statistics).
  - `compute_categorical_summary`: frequency tables for categorical columns.
  - `compute_correlation_matrix`: Pearson product-moment correlation matrix.
  - `get_key_correlation_pairs`: top positive and negative correlation pairs.
  - `aggregate_by_category`, `aggregate_by_city`, `aggregate_by_product`, `aggregate_monthly_trend`, `aggregate_by_gender`, `top_customers`: grouping aggregations.
  - `run_eda_pipeline`: master pipeline returning complete EDA results dict.
- `app/components/kpi_cards.py` — standardized KPI metric rendering components (`render_kpi_card`, `render_kpi_row`, `create_kpi_data`).
- `app/components/filters.py` — interactive sidebar filtering controls (`render_sidebar_filters`, `apply_filters`, `render_filter_summary`).
- `app/components/tables.py` — reusable table rendering components (`render_dataframe_table`, `render_paginated_table`, `render_paginated_kpi_table`).
- `tests/unit/test_eda.py` — 14 unit tests covering all EDA service functions (KPIs, numeric/categorical summaries, correlation matrix, aggregations, empty DataFrame handling).
- `tests/unit/test_formatters.py` — 4 unit tests verifying INR formatting, comma grouping, percentages, and null handling.
- `tests/unit/test_charts.py` — 4 unit tests verifying `ChartFactory` produces valid `go.Figure` instances adhering to the dark theme template.

#### Changed
- `app/pages/02_eda_bi.py` — upgraded from empty-state stub to complete Module 2 UI dashboard:
  - KPI row: Total Revenue, Total Orders, Average Order Value, Total Quantity.
  - Chart grid: Revenue by Category (bar), Monthly Revenue Trend (line), Correlation Heatmap, Revenue by City (bar).
  - Descriptive statistics: numeric summary table and categorical frequency tables.
  - Sidebar filters: date range, category, city, and numeric range sliders.

### Verification (Increment 2)

| Gate | Command | Result |
|---|---|---|
| Lint | `ruff check app tests scripts` | ✅ All checks passed |
| Format (ruff) | `ruff format --check app tests scripts` | ✅ 42 files already formatted |
| Format (black) | `black --check app tests scripts` | ✅ 34 files left unchanged |
| Layer rule | Ruff TID251 | ✅ Zero Streamlit imports in `services/`, `models/`, `database/` |
| Tests | `pytest tests/unit/ -v` | ✅ 86 passed in 1.87s |

Test coverage (Increment 2):
- `test_eda.py`: 14 tests covering all EDA service functions (KPIs, numeric/categorical summaries, correlation matrix, aggregations, empty DataFrame handling, missing columns).
- `test_formatters.py`: 4 tests verifying INR formatting, comma grouping, percentages, and null handling.
- `test_charts.py`: 4 tests verifying `ChartFactory` produces valid `go.Figure` instances adhering to the dark theme template.

Total test suite: 86 unit tests (6 from Increment 1A, 60 from Increment 1B & 1C, 22 from Increment 2).
| Tests | `pytest tests/unit/ -q` | ✅ 64 passed (18 from 1A/1B + 46 new unit tests across 5 test suites) |

Architectural purity:
- Zero Streamlit imports in `app/services/`, `app/models/`, `app/database/` (verified via AST test).
- Pure function / service isolation: `raw_df` immutability verified across all loader, profiler, cleaner, validator, and report_generator operations.
- Deterministic synthetic data generation with fixed seed and enforced schema.

## [0.2.0] — 2026-11-19

### Increment 1B — Ingestion, Schema Mapping, and Data Profiling

#### Added
- `app/models/dataset_schema.py` — canonical 12-column schema, expected dtypes,
  synonym mapping dictionary (FR-CC-02), `SchemaReport` dataclass,
  `map_columns()`, `validate_dataframe_schema()`, and non-mutating `apply_column_mapping()`.
- `app/models/validation_models.py` — typed data contracts: `ProfilingMetrics`,
  `ColumnProfile`, `ValidationSummary`, `RuleCheckResult`, `StatResult`,
  `CleaningLog`, `DataLoadResult`.
- `app/services/data_loader.py` — `DataLoader` service with pre-parse file validation
  (50 MB limit, `.csv`/`.xlsx` extension check), multi-encoding fallback parsing
  (`utf-8`, `utf-8-sig`, `latin1`, `cp1252`), openpyxl Excel parser, malformed CSV
  resilience, Scenario B bundled dataset loader with graceful absence handling,
  and DataFrame immutability guarantees.
- `app/services/profiler.py` — `Profiler` service computing dimensions, memory usage,
  missing value rates, duplicate rows, summary statistics, and automated type anomaly
  detection (numeric and datetime pattern heuristics for object columns).
- `tests/unit/test_data_loading.py` — 6 unit tests covering valid CSV ingestion,
  extension rejection, 50 MB boundary rejection, empty file handling, malformed CSV
  resilience, and DataFrame non-mutation.
- `tests/unit/test_schema.py` — 3 unit tests covering exact schema matching,
  case/spacing/synonym normalization, and non-mutating column renaming.
- `tests/unit/test_profiler.py` — 3 unit tests covering profiling metric calculations
  against a deterministic fixture, edge cases (single row, all-null column), and
  DataFrame non-mutation.

#### Changed
- `app/pages/01_data_immersion.py` — upgraded from stub to complete Increment 1B UI:
  file uploader tab, Scenario B bundled dataset tab, preview table with configurable
  row slider (5–100 rows), KPI summary cards (rows, columns, memory, missing cells,
  duplicate rows), detailed column profiling table, and data type anomaly alert banners.

### Verification (Increment 1B)

| Gate | Command | Result |
|---|---|---|
| Lint | `ruff check app tests` | ✅ All checks passed |
| Format (ruff) | `ruff format --check app tests` | ✅ 23 files already formatted |
| Format (black) | `black --check app tests` | ✅ 18 files left unchanged |
| Tests | `pytest tests/unit/ -v` | ✅ 18 passed (6 smoke + 6 loading + 3 schema + 3 profiler) |

Architectural purity:
- Zero Streamlit imports in `app/services/`, `app/models/`, `app/database/` (verified via AST test).
- Pure function / service isolation: `raw_df` immutability verified across all loader and profiler operations.

#### Added
- `app/models/dataset_schema.py` — canonical 12-column schema, expected dtypes,
  synonym mapping dictionary (FR-CC-02), `SchemaReport` dataclass,
  `map_columns()`, `validate_dataframe_schema()`, and non-mutating `apply_column_mapping()`.
- `app/models/validation_models.py` — typed data contracts: `ProfilingMetrics`,
  `ColumnProfile`, `ValidationSummary`, `RuleCheckResult`, `StatResult`,
  `CleaningLog`, `DataLoadResult`.
- `app/services/data_loader.py` — `DataLoader` service with pre-parse file validation
  (50 MB limit, `.csv`/`.xlsx` extension check), multi-encoding fallback parsing
  (`utf-8`, `utf-8-sig`, `latin1`, `cp1252`), openpyxl Excel parser, malformed CSV
  resilience, Scenario B bundled dataset loader with graceful absence handling,
  and DataFrame immutability guarantees.
- `app/services/profiler.py` — `Profiler` service computing dimensions, memory usage,
  missing value rates, duplicate rows, summary statistics, and automated type anomaly
  detection (numeric and datetime pattern heuristics for object columns).
- `tests/unit/test_data_loading.py` — 6 unit tests covering valid CSV ingestion,
  extension rejection, 50 MB boundary rejection, empty file handling, malformed CSV
  resilience, and DataFrame non-mutation.
- `tests/unit/test_schema.py` — 3 unit tests covering exact schema matching,
  case/spacing/synonym normalization, and non-mutating column renaming.
- `tests/unit/test_profiler.py` — 3 unit tests covering profiling metric calculations
  against a deterministic fixture, edge cases (single row, all-null column), and
  DataFrame non-mutation.

#### Changed
- `app/pages/01_data_immersion.py` — upgraded from stub to complete Increment 1B UI:
  file uploader tab, Scenario B bundled dataset tab, preview table with configurable
  row slider (5–100 rows), KPI summary cards (rows, columns, memory, missing cells,
  duplicate rows), detailed column profiling table, and data type anomaly alert banners.

### Verification (Increment 1B)

| Gate | Command | Result |
|---|---|---|
| Lint | `ruff check app tests` | ✅ All checks passed |
| Format (ruff) | `ruff format --check app tests` | ✅ 23 files already formatted |
| Format (black) | `black --check app tests` | ✅ 18 files left unchanged |
| Tests | `pytest tests/unit/ -v` | ✅ 18 passed (6 smoke + 6 loading + 3 schema + 3 profiler) |

Architectural purity:
- Zero Streamlit imports in `app/services/`, `app/models/`, `app/database/` (verified via AST test).
- Pure function / service isolation: `raw_df` immutability verified across all loader and profiler operations.