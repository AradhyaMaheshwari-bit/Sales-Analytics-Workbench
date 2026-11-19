# Phase 4 Implementation Plan (Revision 2)

**SDLC Phase:** 4 — Implementation
**Document ID:** IMP-PLAN-REV2
**Version:** 2.0
**Date:** 2026-11-19
**Supersedes:** IMP-PLAN-REV1
**Status:** PENDING APPROVAL — no implementation may begin until approved

---

## 0. Planning-Only Constraint

This revision creates no application code, configuration, requirements file, CHANGELOG
entry, test, or Git state. `Phase-I_Evaluation/` is not accessed.

---

## 1. Verified Environment Facts

| Fact | Verified Value | How Verified |
|---|---|---|
| Active interpreter | Python **3.14.6** (`.venv`) | `python --version` |
| Previous 3.14.6 / 3.14.7 discrepancy | Resolved: **3.14.6** | Direct interpreter query |
| Installed packages | streamlit 1.49.1, pandas 2.3.3, numpy 2.5.5, plotly 7.1.0, scipy 1.18.1, openpyxl 3.1.5, pytest 9.2.0 | `pip list` |
| Ruff / Black | **Installed in Increment 1A**: ruff 0.17.5, black 26.10.1 | `pip list`, `--version` |
| requirements.txt / pyproject.toml / CHANGELOG.md | **Do not exist** | Directory listing |
| Git | Repository exists, remote `origin` = `github.com/AradhyaMaheshwari-bit/Sales-Analytics-Workbench.git`, HEAD = `9b6fb5c` | `git log`, `git remote -v` |
| Existing dirs | `app/{components,database,models,pages,services,utils}`, `data/{raw,processed}`, `tests/`, `reports/exports/` | Directory listing (all empty) |
| `scripts/` | **Does not exist** | Directory listing |

---

## 2. Design-Authoritative File Map

Every planned path below is taken from `docs/03-design/module-design.md` §2 unless
explicitly marked as a deviation.

| Path | Source | Increment |
|---|---|---|
| `app/main.py` | SDD-MOD §2.1 | 1A |
| `app/pages/01_data_immersion.py` | SDD-MOD §2.1 | 1A (empty state) → 1B, 1C |
| `app/pages/02_eda_bi.py` | SDD-MOD §2.1 | 1A (empty state) → 2 |
| `app/pages/03_sql_analysis.py` | SDD-MOD §2.1 | 1A (empty state) → 3 |
| `app/pages/04_power_bi.py` | SDD-MOD §2.1 | 1A (empty state) → 4 |
| `app/pages/05_statistical_validation.py` | SDD-MOD §2.1 | 1A (empty state) → 5 |
| `app/components/kpi_cards.py`, `filters.py`, `tables.py` | SDD-MOD §2.2 | 2 / 4 |
| `app/services/data_loader.py` | SDD-MOD §2.3 | 1B |
| `app/services/profiler.py` | SDD-MOD §2.3 | 1B |
| `app/services/cleaner.py` | SDD-MOD §2.3 | 1C |
| `app/services/validator.py` | SDD-MOD §2.3 | 1C |
| `app/services/eda.py` | SDD-MOD §2.3 | 2 |
| `app/services/statistics.py` | SDD-MOD §2.3 | 5 |
| `app/services/report_generator.py` | SDD-MOD §2.3 | 1C / 2 |
| `app/database/db_manager.py` | SDD-MOD §2.4 | 1C |
| `app/database/authorizer.py` | SDD-MOD §2.4 | 3 |
| `app/database/queries.py` | SDD-MOD §2.4 | 3 |
| `app/models/dataset_schema.py` | SDD-MOD §2.5 | 1B |
| `app/models/validation_models.py` | SDD-MOD §2.5 | 1B / 5 |
| `app/utils/styling.py` | SDD-MOD §2.6 | 1A |
| `app/utils/charts.py` | SDD-MOD §2.6 | 2 |
| `app/utils/formatters.py` | SDD-MOD §2.6 | 1C / 2 |
| `app/utils/logger.py` | SDD-MOD §2.6 | 1A |
| `app/assets/power_bi/` (+ `dax_measures_reference.json`) | SDD-PBI §2.1 | 4 |
| `scripts/generate_demo_data.py` | SRS-DDS §2 (D-1) | 1C |
| `tests/unit/test_*.py` | SDD-MOD §3 (`tests/unit/`) | see §6 |
| `pyproject.toml`, `requirements.txt`, `CHANGELOG.md` | NFR-M-03, Phase 4 workflow | 1A |
| `docs/04-implementation/*` | Phase 4 documentation artefacts | each increment |

### 2.1 Corrections against IMP-PLAN-REV1

- `app/services/dataset_schema.py` → **`app/models/dataset_schema.py`** (SDD-MOD §2.5).
- `app/database/sql_authorizer.py` → **`app/database/authorizer.py`**; `sql_security.py`
  folded into `authorizer.py` (progress handler) and `queries.py` (row cap), matching
  SDD-DB-SQL §4.1–§4.2.
- `app/services/queries.py` → **`app/database/queries.py`**.
- `app/utils/config.py` → **`app/utils/styling.py`**.
- `app/utils/session_state.py` → **removed**; session initialisation belongs in
  `app/main.py` (SDD-MOD §2.1).
- `app/pages/00_home.py` → **removed** (not in SDD-MOD; landing content lives in
  `app/main.py`).
- `app/assets/power_bi/dashboard_full.png` placeholder → **removed** (see §5).

---

## 3. Layering Rules (enforced in review)

- `app/services/**`, `app/models/**`, `app/database/**` must **not** import `streamlit`.
  Enforced by a Ruff rule (`flake8-tidy-imports` banned-api) plus a unit test that
  parses each service module's imports.
- Presentation layer (`app/pages/`, `app/components/`, `app/main.py`) holds no
  business logic and no raw SQL strings other than the approved catalogue.
- Services are pure: DataFrame in, result out, deep copies at every mutation point
  (TD-07).
- Utilities import nothing from `app.services` / `app.database`.

---

## 4. Dependency Specification

Deliberate pins to the **already-installed, verified** versions. No upgrade and no
environment change without separate authorisation.

```
# requirements.txt (deliberately maintained — not pip freeze)
streamlit==1.49.1
pandas==2.3.3
numpy==2.5.5
plotly==7.1.0
scipy==1.18.1
openpyxl==3.1.5

# requirements-dev.txt
pytest==9.2.0
ruff==0.17.5
black==26.10.1
```

Direct runtime dependencies only; transitive packages are not listed. Ruff 0.17.5 and
Black 26.10.1 were installed into the existing `.venv` during Increment 1A with no
other package upgraded.

---

## 5. Power BI Module (Increment 4)

- **No placeholder image is created or generated.** No fabricated screenshot, mock
  dashboard render, or stand-in graphic may be committed.
- Module 4 implements a **missing-asset state** (SDD-SEC §6.3): if
  `app/assets/power_bi/dashboard_full.png` is absent, the page renders an info banner
  ("Dashboard screenshots not found. Please add assets to app/assets/power_bi/.") and
  displays no image widget. The DAX measure cards, slicer table, and visual table
  render from `dax_measures_reference.json` regardless.
- Only the six DAX measures in SDD-PBI §3, four slicers in §4, and six visuals in §5
  are presented. No additional or invented measures, metrics, or screenshots.
- The non-dismissible authentic-deliverable disclaimer (SDD-PBI §2.3) is retained.
- Deployed asset arrives only when you supply the real screenshot.

---

## 6. Increments

### Increment 1A — Foundation and runnable shell

**Files:** `pyproject.toml`, `requirements.txt`, `requirements-dev.txt`, `CHANGELOG.md`,
`app/main.py`, `app/utils/styling.py`, `app/utils/logger.py`, `app/__init__.py`,
package `__init__.py` files for `pages/`, `utils/`, `services/`, `database/`,
`models/`, `components/`; five page stubs with dependency-aware empty states.

**Scope:** `st.navigation` registry, dark navy CSS injection, logger configuration,
`st.set_page_config`, sidebar identity block, empty-state rendering for all five
modules.

**Tests — `tests/unit/test_app_smoke.py` (genuine, not lint):**
1. `AppTest.from_file("app/main.py").run()` → `at.exception` is empty.
2. All five page scripts run headless without raising (`AppTest` per page file).
3. Page registry exposes exactly five entries in the approved order.
4. Empty state text present on each analysis page when `active_df` is absent.
5. Theme CSS string is injected into the main container.
6. No service/model/database module imports `streamlit` (AST scan test).

**Quality gate:** `ruff check app tests` and `ruff format --check app tests` exit 0;
`black --check app tests` exit 0.

**Exit criteria:** app launches under `streamlit run app/main.py`; five pages
navigable; smoke tests pass; no module crashes on the empty dataset.

---

### Increment 1B — Ingestion, schema, profiling

**Files:** `app/services/data_loader.py`, `app/models/dataset_schema.py`,
`app/services/profiler.py`, `app/models/validation_models.py` (ProfilingMetrics,
SchemaReport), `app/pages/01_data_immersion.py` (upload/preview/profile UI only).

**Tests — `tests/unit/test_data_loading.py`, `test_schema.py`, `test_profiler.py`:**
1. CSV and XLSX parse into a DataFrame with the canonical 12 columns.
2. `.txt`, `.json`, `.xls` rejected with the approved message; no read attempted.
3. File > 50 MB rejected by size check **before** parsing (synthetic in-memory buffer).
4. Empty file → "empty dataset" message, no exception.
5. Malformed/truncated CSV → caught `ParserError`, reported.
6. Encoding fault → parsed or reported, never an uncaught exception.
7. Column mapping: exact-name match, case/whitespace variants, synonym mapping, and
   unmappable-columns report (FR-CC-02).
8. Profiler: row/column counts, dtype per column, missing counts and percentages,
   duplicate-row count, numeric summary — asserted against a fixed fixture.
9. Profiler on a single-row DataFrame and on an all-null column → no exception.
10. `raw_df` is not mutated by any loader or profiler call (identity + content check).

**Exit criteria:** upload → preview → profile works end-to-end; tests pass; no
Streamlit import in `services/` or `models/`.

---

### Increment 1C — Cleaning, database foundation, Module 1 completion

**Files:** `app/services/cleaner.py`, `app/services/validator.py`,
`app/services/report_generator.py`, `app/database/db_manager.py`,
`scripts/generate_demo_data.py`, `app/pages/01_data_immersion.py` (full).

**Tests — `tests/unit/test_cleaning.py`, `test_validator.py`, `test_db_manager.py`,
`test_report_generator.py`, `test_demo_data.py`:**
1. Missing-value strategies: drop rows, fill mean/median/mode, leave untouched; each
   returns a new DataFrame and leaves `raw_df` byte-identical.
2. Duplicate removal reports the exact removed-row count.
3. **Date normalisation:** valid dates → `YYYY-MM-DD` strings; unparseable → `NULL`;
   the count of unparseable rows is reported in the cleaning summary (SRS-SQL Query 5
   requirement); rows are **not** silently dropped.
4. Undo: pops the history stack and restores the previous `active_df` exactly.
5. Reset: restores an exact copy of `raw_df`.
6. Data replacement: new upload tears down prior state and DB connection.
7. Validator: `Quantity <= 0`, `Unit_Price <= 0`, `Total_Sales ≈ Quantity × Unit_Price`
   mismatch detection, with pass/fail counts.
8. Exports: CSV and multi-sheet XLSX bytes are non-empty, readable back by pandas, and
   contain the expected columns/rows.
9. `db_manager`: DataFrame registers into table `sales` with all 12 columns; rebuild
   closes the previous connection; NULL dates survive ingestion.
10. `scripts/generate_demo_data.py`: same seed → identical output; 12-column schema;
    `Total_Sales == Quantity × Unit_Price` within rounding; Gender ∈ {Male, Female};
    plausible date range; documented row count.
11. Generated output is confined to `data/raw/` and is Git-ignored (policy test).

**Exit criteria:** Module 1 complete (upload, profile, clean, validate, export, undo,
reset); tests pass; synthetic dataset generated and verified.

---

### Increment 2 — EDA and BI

**Files:** `app/services/eda.py`, `app/utils/charts.py`, `app/utils/formatters.py`,
`app/components/{kpi_cards,filters,tables}.py`, `app/pages/02_eda_bi.py`.

**Tests — `tests/unit/test_eda.py`, `test_charts.py`, `test_formatters.py`:**
numeric summary against a fixed fixture; Pearson correlation for known pairs; frequency
tables; grouping aggregations; empty/one-row frames; ChartFactory returns a
`plotly.graph_objects.Figure` with the `workbench_dark` template applied; INR formatting
(`₹1,41,807.34`), percentage and comma formatting edge cases.

**Exit criteria:** dashboard renders all six visual classes; figures honour the theme.

---

### Increment 3 — SQL analysis and engine security

**Files:** `app/database/authorizer.py`, `app/database/queries.py`,
`app/pages/03_sql_analysis.py`.

**Seven queries (SRS-SQL §2), all in the catalogue, business logic preserved:**
1. Total revenue — `SELECT SUM(Total_Sales) AS Total_Revenue FROM sales;`
2. Revenue by Category — `GROUP BY Category ORDER BY Revenue DESC`
3. Revenue by Product — `GROUP BY Product ORDER BY Revenue DESC`
4. Revenue by City — `GROUP BY City ORDER BY Revenue DESC`
5. Monthly trend — `SELECT STRFTIME('%Y-%m', Order_Date) AS Month, SUM(Total_Sales) AS Revenue FROM sales WHERE Order_Date IS NOT NULL GROUP BY Month ORDER BY Month;` with `Order_Date` normalised to `YYYY-MM-DD` or `NULL`. The `WHERE Order_Date IS NOT NULL` predicate is mandatory so the monthly aggregation never produces a NULL month group. Rows with invalid dates **remain in the cleaned dataset**; their count is reported by the cleaning summary (they are excluded from this grouping only).
6. Revenue by Gender — `GROUP BY Gender`
7. Top-10 Customers — `GROUP BY Customer_Name ORDER BY Revenue DESC LIMIT 10`

Each query is shown with its business question (FR-16 traceability).

**Security implementation (NFR-S-02, D-3):**
- `set_authorizer` allowlist: `SQLITE_SELECT`; `SQLITE_READ` only when the table is
  `sales` in schema `main`; `SQLITE_FUNCTION` only for the approved function set
  (`SUM`, `AVG`, `COUNT`, `MIN`, `MAX`, `ROUND`, `STRFTIME`, `LOWER`, `UPPER`,
  `COALESCE`, plus `TOTAL` if required by aggregation tests).
- Deny: `INSERT`, `UPDATE`, `DELETE`, `CREATE_*`, `DROP_*`, `ALTER_TABLE`, `ATTACH`,
  `DETACH`, `PRAGMA`, `TRANSACTION`-level writes, temp-table creation, and any read of
  `sqlite_master` / `sqlite_schema` / `sqlite_temp_master`.
- Authorizer attached **after** `to_sql` ingestion (SDD-DB-SQL §2.2), re-attached on
  every rebuild, and detached only inside the ingestion path.
- `set_progress_handler` with a monotonic-clock deadline of 2.0 s **and** an instruction
  budget of 1,000,000 opcodes; either trip aborts with a reported error.
- Result cap `cursor.fetchmany(500)` with the "first 500 rows" warning.
- Keyword filtering is explicitly **not** a security boundary and is not implemented as
  one.

**Tests — `tests/unit/test_authorizer.py`, `test_queries.py`:**
1. All seven queries return the expected shapes/values on a fixed fixture.
2. Prohibited statements denied: `INSERT`, `UPDATE`, `DELETE`, `DROP TABLE`,
   `CREATE TABLE`, `ALTER TABLE`, `ATTACH`, `DETACH`, `PRAGMA`, `VACUUM`, `REINDEX`.
3. Obfuscated attempts denied at engine level: leading comments, mixed case,
   semicolon chaining, `WITH ... DELETE`, subquery writes.
4. Direct execution attempt bypassing the query service (`conn.execute("DELETE …")`)
   still denied — proves the boundary is not the wrapper.
5. Unauthorised read denied: a second table registered before the authorizer is
   attached, then read → denied.
6. System-table access denied: `SELECT name FROM sqlite_master`.
7. Unapproved SQL function denied (e.g. `load_extension`, `printf` outside allowlist).
8. Timeout: a deliberately expensive self-join/cartesian query aborts within the
   deadline and raises the reported error.
9. Instruction-count limit trips independently of wall clock.
10. Result cap: a query matching > 500 rows returns exactly 500 plus the warning flag.
11. Session isolation: two connections do not see each other's `sales` table.
12. Streamlit rerun simulation: authorizer attached after a rebuild survives a second
    simulated rerun (re-create connection path) and still denies writes.
13. Ingestion path still succeeds while the authorizer is attached post-load.

**Exit criteria:** seven queries correct; every denial, timeout, and row-cap test
green; no keyword-filter dependency in the code path.

---

### Increment 4 — Power BI showcase

**Files:** `app/assets/power_bi/dax_measures_reference.json`, `app/pages/04_power_bi.py`
(no image assets created).

**Tests:** JSON validates against the six approved measures with formulas and return
types; page renders the missing-asset banner when the PNG is absent; disclaimer present;
no reference to any non-approved measure.

**Exit criteria:** module renders correctly in the missing-asset state and will display
the screenshot unchanged once you supply it.

---

### Increment 5 — Statistical validation

**Files:** `app/services/statistics.py`, `app/pages/05_statistical_validation.py`,
`app/models/validation_models.py` (StatResult).

**Tests — `tests/unit/test_statistics.py`:**
1. Welch t-statistic, Welch–Satterthwaite df, and manually computed 95 % CI match
   `scipy.stats.ttest_ind(equal_var=False)` and a hand-derived reference on a fixture.
2. Decision rule at α = 0.05 (both reject and fail-to-reject fixtures).
3. Guards: single group, N < 5, zero variance, NaN sales (pairwise drop with reported
   count), > 2 gender categories.
4. No hardcoded historical constant is returned on any path (source inspection test).
5. **Historical benchmark test is marked and skipped unless the original internship
   dataset is present at `data/raw/internship_dataset.xlsx`**; it asserts
   t = 0.683 ± 0.005, p = 0.495 ± 0.005, means ₹141,807.34 / ₹136,883.21, CI
   −₹9,231.58 to ₹19,079.85, decision "fail to reject". It never runs against
   synthetic or uploaded data.

**Exit criteria:** live computation correct, guards correct, benchmark test gated as
described.

---

## 7. Historical Benchmark Contract

- Applies **only** to the unmodified internship dataset (N = 1,000).
- Never asserted against synthetic, cleaned, or user-uploaded data.
- The Welch test, Welch–Satterthwaite degrees of freedom, and the manually computed
  95 % confidence interval are preserved exactly as designed (SDD-STAT §3.2, §4).

---

## 8. Synthetic Generator Contract (D-1)

Deterministic (`--seed`, default 42), 12-column schema, synthetic-only records, no
reproduction of real customers or confidential values, business invariants preserved,
output written to `data/raw/` and Git-ignored. README (Phase 6) will document usage.
Synthetic data is labelled in the UI as demonstration data, distinct from the private
internship dataset.

---

## 9. Ten-Step Git Checkpoint Procedure

Executed **after every logical increment** and never automated:

1. Run the relevant tests and quality checks.
2. Inspect `git status`.
3. Inspect the complete diff.
4. Verify `.gitignore` exclusions (no data, no `.venv`, no secrets, no `Phase-I_Evaluation/`).
5. Update `CHANGELOG.md` where appropriate.
6. Present the exact staged-file list and the proposed commit message.
7. **Stop for explicit commit authorisation.**
8. Commit and verify the commit hash.
9. **Stop for separate push authorisation.**
10. Push and verify the remote branch hash.

Commit authorship remains `Aradhya Maheshwari <maheshwariaradhya065@gmail.com>`; Claude
is never author or committer.

---

## 10. Quality Gates (NFR-M-03)

| Gate | Command | Applied to |
|---|---|---|
| Lint | `ruff check app tests scripts` | every increment |
| Format check | `ruff format --check app tests scripts` | every increment |
| Format check (secondary) | `black --check app tests scripts` | every increment |
| Layer rule | `ruff check app/services app/models app/database` with banned `streamlit` | every increment |
| Tests | `pytest tests -q` | every increment |

`pyproject.toml` carries `[tool.ruff]` (target `py314`, line-length 88, rules
E/F/W/I/B/UP/TID with `banned-api` for `streamlit` in the non-presentation packages)
and `[tool.black]` (line-length 88, target `py314`).

---

## 11. Remaining Decisions and Blockers

| ID | Item | Impact | Needed from you |
|---|---|---|---|
| B-1 | ~~Ruff and Black are not installed~~ **Resolved in Increment 1A** | NFR-M-03 enforceable | ruff 0.17.5, black 26.10.1 pinned in `requirements-dev.txt` |
| B-2 | `.gitignore` ignores `*.png`, contradicting SDD-PBI §2.2 (screenshots committed, < 5 MB each) | Real dashboard screenshot would be silently excluded | Approve a narrow negation `!app/assets/power_bi/*.png` |
| B-3 | Power BI screenshot and `.pbix` not yet available | Module 4 shows missing-asset state | Supply `dashboard_full.png` (and optional filtered-state shot) |
| B-4 | No landing page exists in SDD-MOD | Rev1's `00_home.py` would be an undocumented file | Confirm landing content lives in `app/main.py` (default assumption) |
| B-5 | `requirements-dev.txt` is not named by any design document | Minor packaging convention | Confirm splitting dev tooling from runtime pins |

---

## 12. Status

**PENDING APPROVAL.** No Increment 1A file is created until you approve this plan and
separately authorise implementation.
