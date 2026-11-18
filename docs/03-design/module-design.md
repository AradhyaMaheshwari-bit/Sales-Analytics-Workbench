# Module Design — Sales Analytics Workbench

**SDLC Phase:** 3 — System Design (Checkpoint B)
**Document ID:** SDD-MOD
**Version:** 1.0

---

## 1. Overview

This document defines the complete module structure, file paths, responsibilities, inputs, outputs, dependencies, and requirements traceability for every module in the application.

---

## 2. Module Inventory & Specifications

### 2.1 Presentation Layer (`app/`)

| File Path | Responsibility | Inputs | Outputs | Dependencies | Req IDs |
|---|---|---|---|---|---|
| `app/main.py` | Application entry point; initializes session state, injects global dark theme CSS, configures `st.navigation`. | User browser session | Streamlit page rendering | `streamlit`, `app/utils/styling.py` | FR-CC-01, NFR-U-01, NFR-U-02 |
| `app/pages/01_data_immersion.py` | Module 1 UI: Dataset upload/mode toggle, preview, profiling, missing values, duplicates, cleaning controls, validation, export. | `st.session_state` | Rendered UI, interactive widgets | `streamlit`, `pandas`, `data_loader`, `profiler`, `cleaner`, `validator` | FR-01 to FR-10, FR-CC-01, FR-CC-02 |
| `app/pages/02_eda_bi.py` | Module 2 UI: Exploratory Data Analysis, descriptive stats, correlation matrix, distribution and category charts. | `st.session_state` | Rendered EDA dashboard | `streamlit`, `pandas`, `eda`, `charts`, `formatters` | FR-11 to FR-14 |
| `app/pages/03_sql_analysis.py` | Module 3 UI: Pre-built 7 SQL queries dropdown, custom SELECT SQL console, paginated result tables. | `st.session_state` | Rendered SQL workbench | `streamlit`, `pandas`, `db_manager`, `queries` | FR-15, FR-16 |
| `app/pages/04_power_bi.py` | Module 4 UI: Power BI showcase, authentic screenshots, 6 DAX measures breakdown, 4 slicers, 6 visuals. | Local image assets | Rendered BI showcase | `streamlit`, `app/components/` | FR-18 |
| `app/pages/05_statistical_validation.py` | Module 5 UI: Welch's t-test live computation, t-stat, p-value, 95% CI, interpretation, storytelling summary, GitHub links. | `st.session_state` | Rendered statistical & story page | `streamlit`, `pandas`, `statistics`, `charts` | FR-19, FR-20 |

### 2.2 Reusable UI Components (`app/components/`)

| File Path | Responsibility | Inputs | Outputs | Dependencies | Req IDs |
|---|---|---|---|---|---|
| `app/components/kpi_cards.py` | Renders standardized executive KPI metric cards with delta indicators and custom styling. | Title, value, delta (opt), icon | Streamlit HTML/Metric widget | `streamlit` | NFR-U-02, FR-18 |
| `app/components/filters.py` | Renders multi-select filters, sliders, and sidebar controls. | Column series, filter options | Filtered DataFrame subset | `streamlit`, `pandas` | FR-18, FR-CC-02 |
| `app/components/tables.py` | Renders styled, formatted data tables with currency/percentage formatting and pagination. | DataFrame, formatting rules | Streamlit dataframe widget | `streamlit`, `pandas`, `formatters` | NFR-U-02, FR-03 |

### 2.3 Service & Domain Logic Layer (`app/services/`)

| File Path | Responsibility | Inputs | Outputs | Dependencies | Req IDs |
|---|---|---|---|---|---|
| `app/services/data_loader.py` | Parses CSV/XLSX, validates file size/extension, loads bundled internship dataset (Scenario B). | File buffer or path | Parsed `pd.DataFrame` | `pandas`, `openpyxl` | FR-01, FR-02, FR-CC-01 |
| `app/services/profiler.py` | Computes dimensions, dtypes, missing value counts/percentages, duplicate rows, column stats. | `pd.DataFrame` | Dict of profiling metrics | `pandas` | FR-04, FR-05, FR-06, FR-07 |
| `app/services/cleaner.py` | Executes non-mutating data cleaning (imputation, dropping duplicates, type coercion). Returns new copy + history log. | `pd.DataFrame`, cleaning config | Tuple (`pd.DataFrame`, `dict` log) | `pandas`, `numpy` | FR-08, NFR-R-02 |
| `app/services/validator.py` | Validates business rules (Quantity > 0, Unit_Price > 0, Total_Sales match). | `pd.DataFrame` | Validation summary (`dict` pass/fail) | `pandas` | FR-09 |
| `app/services/eda.py` | Computes descriptive statistics, frequency tables, correlation matrices, and grouping aggregations. | `pd.DataFrame` | Aggregated DataFrames / stats dict | `pandas`, `numpy` | FR-11, FR-12, FR-13 |
| `app/services/statistics.py` | Executes Welch's t-test (`equal_var=False`), Welch-Satterthwaite df, critical t, 95% CI bounds, decision. | Two `pd.Series` (Male/Female sales) | Typed `StatResult` dataclass | `scipy.stats`, `numpy` | FR-19 |
| `app/services/report_generator.py`| Generates multi-sheet Excel reports (`openpyxl`) and downloadable CSV files. | `pd.DataFrame`, analysis dict | Byte stream / buffer | `pandas`, `openpyxl` | FR-10, FR-17 |

### 2.4 Database & SQL Layer (`app/database/`)

| File Path | Responsibility | Inputs | Outputs | Dependencies | Req IDs |
|---|---|---|---|---|---|
| `app/database/db_manager.py` | Manages in-memory SQLite connection lifecycle, dataframe registration into table `sales`. | `pd.DataFrame`, session state | `sqlite3.Connection` handle | `sqlite3`, `pandas` | FR-15, NFR-DP-02 |
| `app/database/authorizer.py` | Implements SQLite connection `set_authorizer` callback enforcing SELECT-only access and table locking. | SQLite auth action codes | `sqlite3.SQLITE_OK` or `SQLITE_DENY` | `sqlite3` | NFR-S-02, FR-16 |
| `app/database/queries.py` | Catalog of 7 approved reference SQL queries and parameterized custom query executor with row/time limits. | `sqlite3.Connection`, query string | `pd.DataFrame` or error message | `sqlite3`, `pandas` | FR-16, SRS-SQL |

### 2.5 Models & Contracts (`app/models/`)

| File Path | Responsibility | Inputs | Outputs | Dependencies | Req IDs |
|---|---|---|---|---|---|
| `app/models/dataset_schema.py` | Defines canonical column names, expected dtypes, and validation rules. | Raw column names | Schema validation report | `pandas` | FR-CC-02 |
| `app/models/validation_models.py` | Dataclasses for StatResult, CleaningLog, ValidationSummary, and ProfilingMetrics. | Raw computation output | Typed data objects | Python `dataclasses` | FR-08, FR-19 |

### 2.6 Cross-Cutting Utilities (`app/utils/`)

| File Path | Responsibility | Inputs | Outputs | Dependencies | Req IDs |
|---|---|---|---|---|---|
| `app/utils/styling.py` | Injects custom CSS for dark navy executive theme, card styling, and typography. | None | Streamlit HTML injection | `streamlit` | NFR-U-02 |
| `app/utils/charts.py` | Centralized Plotly chart factory (`ChartFactory`) applying dark theme, INR tooltips, and responsive sizing. | Data, chart type, config | `plotly.graph_objects.Figure` | `plotly` | FR-14, NFR-U-02 |
| `app/utils/formatters.py` | Formats numeric values into INR currency (`₹1,41,807.34`), percentages, and commas. | Numeric value | Formatted string | Python `locale` / format strings | NFR-U-02, FR-12 |
| `app/utils/logger.py` | Configures structured logging without exposing sensitive data. | Log message, level | Log output | Python `logging` | NFR-M-02 |

---

## 3. Inter-Module Dependencies & Coupling

- **Zero Circular Dependencies:** Presentation depends on Services and Database; Services depend only on pandas/numpy/scipy; Database depends only on SQLite; Utilities are dependency-free.
- **Service Isolation:** All services are pure functions receiving DataFrames and returning results, allowing them to be tested independently in `tests/unit/`.
