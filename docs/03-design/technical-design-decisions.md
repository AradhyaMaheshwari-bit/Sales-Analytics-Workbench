# Technical Design Decisions — Sales Analytics Workbench

**SDLC Phase:** 3 — System Design (Checkpoint B)
**Document ID:** SDD-TDD
**Version:** 1.0

---

## 1. Overview

This document records the key technical design decisions made during Phase 3 System Design, along with the alternatives considered, the rationale for each choice, and the trade-offs accepted.

---

## 2. Technology Stack Decisions

### TD-01: Streamlit as Application Framework

| Aspect | Detail |
|---|---|
| **Decision** | Use Streamlit ≥ 1.36 as the sole web application framework. |
| **Alternatives Considered** | Flask + Jinja2 templates, Dash (Plotly), Django, Jupyter Notebooks |
| **Rationale** | Streamlit provides rapid development of data-native applications with native DataFrame rendering, built-in widgets, session state management, and file uploader — all essential for the workbench's five analytical modules. It eliminates the need for separate frontend code (HTML/CSS/JS), which is outside the BCA Data Analytics & AI curriculum focus. |
| **Trade-offs** | Limited control over DOM/CSS compared to React-based frameworks; the reactive re-run model requires careful session state management; no built-in user authentication system. |
| **References** | FR-CC-01, NFR-U-01, technology-justification.md |

### TD-02: `st.navigation` API for Multipage Architecture

| Aspect | Detail |
|---|---|
| **Decision** | Use `st.navigation()` declared in `app/main.py` for centralized page routing (Streamlit ≥ 1.36). |
| **Alternatives Considered** | Legacy `pages/` folder auto-discovery (`st.Page` scanning), custom sidebar radio button routing |
| **Rationale** | `st.navigation` provides programmatic control over page ordering, display names, and icons. Unlike auto-discovery, it allows a single entry point (`main.py`) to initialize global session state, inject CSS, and configure shared sidebar components before any page script executes. |
| **Trade-offs** | Requires Streamlit ≥ 1.36; older deployments would need the legacy approach. |
| **References** | SDD-ARCH §2, module-design.md §2.1 |

### TD-03: In-Memory SQLite (`:memory:`) as Query Engine

| Aspect | Detail |
|---|---|
| **Decision** | Use `sqlite3.connect(':memory:', check_same_thread=False)` for all SQL analysis. |
| **Alternatives Considered** | File-based SQLite (`.db`), DuckDB, PostgreSQL (external), `pandasql` |
| **Rationale** | In-memory SQLite requires zero infrastructure setup, provides ISO SQL compliance suitable for educational demonstration, and is automatically destroyed at session end (NFR-DP-01). `check_same_thread=False` is technically mandatory due to Streamlit's worker thread pool model (SDD-DB-SQL §2.1). DuckDB was rejected for being outside the original internship technology stack specification. PostgreSQL was rejected as over-engineering for a single-user analytics tool. |
| **Trade-offs** | No cross-session data persistence (acceptable: each session starts fresh); limited to datasets that fit in server RAM; no concurrent write support (unnecessary for SELECT-only design). |
| **References** | FR-15, NFR-DP-02, D-3, SDD-DB-SQL §2 |

### TD-04: `check_same_thread=False` Threading Decision

| Aspect | Detail |
|---|---|
| **Decision** | Pass `check_same_thread=False` to every `sqlite3.connect` call. |
| **Alternatives Considered** | Create per-thread SQLite connections, use SQLAlchemy connection pool |
| **Rationale** | Streamlit dispatches consecutive script reruns to different threads from its worker pool. A single session's `st.session_state['db_conn']` must be accessible across these reruns. Since operations are inherently serialized per session (Streamlit runs scripts sequentially), there is no actual concurrent write risk. Without this flag, `sqlite3.ProgrammingError: SQLite objects created in a thread can only be used in that same thread` occurs. |
| **Trade-offs** | Disables SQLite's built-in thread safety check; mitigated by Streamlit's sequential execution model per session. |
| **References** | SDD-DB-SQL §2.1 |

---

## 3. Security Architecture Decisions

### TD-05: Engine-Level Authorizer as Security Boundary (D-3)

| Aspect | Detail |
|---|---|
| **Decision** | Use `sqlite3.Connection.set_authorizer` as the primary SQL security boundary. |
| **Alternatives Considered** | Regex keyword filtering, SQL parser-based allowlisting (e.g., `sqlparse`), separate read-only SQLite connection |
| **Rationale** | Engine-level authorizers intercept every SQL operation at the SQLite virtual machine layer, regardless of query syntax, encoding, aliasing, or obfuscation. Keyword filtering is inherently bypassable (Unicode homoglyphs, comments, hex encoding). Parser-based validation adds a dependency and may not cover all edge cases. The authorizer is the only mechanism that guarantees enforcement at execution time. |
| **Trade-offs** | Authorizer callback is invoked on every SQL operation (minor performance overhead); requires careful specification of allowed action codes. |
| **References** | NFR-S-02, D-3, SDD-DB-SQL §4, SDD-SEC §3 |

### TD-06: Progress Handler for Computational Timeout

| Aspect | Detail |
|---|---|
| **Decision** | Use `sqlite3.Connection.set_progress_handler` with 2-second wall-clock timeout and 1,000,000 opcode limit. |
| **Alternatives Considered** | Python `signal.alarm()` (Unix only), `threading.Timer` with connection close, no timeout |
| **Rationale** | `set_progress_handler` operates at the SQLite VM level, providing deterministic interruption of long-running queries regardless of operating system. `signal.alarm()` is unavailable on Windows. Thread-based timer interrupting from outside risks connection corruption. The progress handler cleanly aborts the current operation and raises `sqlite3.OperationalError`, which is catchable and user-reportable. |
| **Trade-offs** | Progress handler is polled every N opcodes (not exact wall-clock precision); acceptable granularity for a 2-second limit. |
| **References** | NFR-S-02, SDD-DB-SQL §4.2 |

---

## 4. Data Architecture Decisions

### TD-07: Pandas Defensive Copy Contract

| Aspect | Detail |
|---|---|
| **Decision** | All DataFrame mutations use `df.copy(deep=True)` before modifying data. `raw_df` is permanently read-only. |
| **Alternatives Considered** | Copy-on-write (pandas 2.0 experimental flag), immutable wrapper class, no explicit copying |
| **Rationale** | Deep copying is the most explicit and debuggable approach. Copy-on-write is experimental and may introduce subtle reference-sharing bugs. An immutable wrapper adds unnecessary class abstraction for a project of this scale. Deep copy guarantees that no reference aliasing ever occurs between `raw_df` and `active_df`. |
| **Trade-offs** | Memory cost of duplicating DataFrames (acceptable for datasets under 50MB); explicit `.copy()` calls at every mutation point rely on developer discipline (enforced by code review during Phase 5). |
| **References** | NFR-R-02, SDD-DATA §2, SDD-DATA §4 |

### TD-08: Date Normalization as ISO-8601 Strings in SQLite

| Aspect | Detail |
|---|---|
| **Decision** | Store valid dates as ISO-8601 strings (`YYYY-MM-DD`) and invalid dates as `NULL` in the SQLite `sales` table. |
| **Alternatives Considered** | Store as epoch integers, keep as original strings, store as SQLite `REAL` Julian day numbers |
| **Rationale** | ISO-8601 strings are human-readable in query results, compatible with `STRFTIME('%Y-%m', Order_Date)` for Query 5, and unambiguous across locales. `NULL` for invalid dates preserves the row (no silent deletion) while clearly indicating unparseable values. |
| **Trade-offs** | String comparison is slower than integer comparison for range queries; acceptable for datasets under 50K rows. |
| **References** | SDD-DATA §5, SDD-DB-SQL §5 (Query 5) |

### TD-09: Synthetic Data Generator Strategy (D-1)

| Aspect | Detail |
|---|---|
| **Decision** | Implement `scripts/generate_demo_data.py` as a reproducible synthetic data generator (Scenario A). |
| **Alternatives Considered** | Bundling actual internship dataset, using Faker library, hardcoded sample rows |
| **Rationale** | The internship dataset is excluded from Git to protect data privacy (NFR-DP-01). A generator script using `random.seed(42)` and `numpy.random` with a fixed seed produces statistically representative data (matching schema, distributions, and edge cases) without reproducing actual customer records. The Faker library was rejected as an unnecessary dependency. |
| **Trade-offs** | Synthetic distributions may not perfectly match real data; acceptable because the generator is for demonstration, not production analysis. Historical benchmarks apply only to the unmodified internship dataset. |
| **References** | D-1, FR-CC-01, demonstration-data-strategy.md |

---

## 5. Statistical Design Decisions

### TD-10: Welch's T-Test Over Student's T-Test

| Aspect | Detail |
|---|---|
| **Decision** | Use Welch's independent two-sample t-test (`scipy.stats.ttest_ind(equal_var=False)`) with manual Welch-Satterthwaite degrees of freedom and 95% CI. |
| **Alternatives Considered** | Student's t-test (`equal_var=True`), Mann-Whitney U test, bootstrap confidence interval |
| **Rationale** | Welch's t-test does not assume equal population variances, making it the statistically safer default for real-world transactional data. Student's t-test would require verifying homogeneity of variances (Levene's test), adding complexity without benefit. Mann-Whitney tests ranks rather than means, which does not directly answer the business question about average sales. |
| **Trade-offs** | Slightly lower statistical power than Student's t-test when variances are truly equal; acceptable given the robustness gain. |
| **References** | FR-19, SDD-STAT §3.2 |

### TD-11: No Hardcoded Historical Values in Computation Path

| Aspect | Detail |
|---|---|
| **Decision** | Historical internship results (t=0.683, p=0.495, etc.) are treated as validation references for the unmodified internship dataset only. They are never hardcoded into the statistical computation functions. |
| **Alternatives Considered** | Storing expected results as constants and returning them when the internship dataset is detected |
| **Rationale** | Hardcoding results would violate scientific integrity and make the tool unable to produce genuine analysis on uploaded datasets. Live computation ensures the workbench is a genuine analytical tool, not a static report. Validation against historical benchmarks is a separate assertion in testing (Phase 5), not a runtime behavior. |
| **Trade-offs** | A rounding or floating-point deviation from historical values is theoretically possible on different hardware; tolerance bands ($\pm 0.005$) are specified in SDD-STAT §4. |
| **References** | FR-19, SDD-STAT §4 |

---

## 6. UI/UX Design Decisions

### TD-12: Dark Navy Executive Theme Over Default Streamlit Theme

| Aspect | Detail |
|---|---|
| **Decision** | Apply a custom dark navy color system (`--bg-main: #0B132B`) via injected CSS, overriding Streamlit's default light theme. |
| **Alternatives Considered** | Streamlit default light theme, Streamlit built-in dark mode toggle, Material Design theme |
| **Rationale** | The dark navy executive palette differentiates the project as a professional analytics product rather than a default student assignment. It provides WCAG AA contrast ratios for readability, reduces eye strain during extended analysis sessions, and creates visual consistency with the Plotly dark chart template. |
| **Trade-offs** | Custom CSS injection may break on Streamlit version upgrades; mitigated by testing against the pinned Streamlit version before deployment. |
| **References** | NFR-U-02, SDD-UI-UX §2 |

### TD-13: Centralized Plotly ChartFactory

| Aspect | Detail |
|---|---|
| **Decision** | All Plotly charts are created through a centralized `ChartFactory` class in `app/utils/charts.py` with a registered `workbench_dark` template. |
| **Alternatives Considered** | Per-page inline Plotly figure creation, Altair charts, Matplotlib static charts |
| **Rationale** | A centralized factory ensures visual consistency (colors, fonts, grid lines, margins, tooltips with INR formatting) across all 5 modules. Plotly was chosen for interactive charts (hover, zoom, pan) over Matplotlib (static images) and Altair (limited customization of dark themes). |
| **Trade-offs** | Plotly bundles are larger than Matplotlib; acceptable in a Streamlit server-rendered context. |
| **References** | FR-14, NFR-U-02, SDD-UI-UX §2 |

---

## 7. Decision Index

| ID | Decision | Section |
|---|---|---|
| TD-01 | Streamlit as framework | §2 |
| TD-02 | `st.navigation` for routing | §2 |
| TD-03 | In-memory SQLite | §2 |
| TD-04 | `check_same_thread=False` | §2 |
| TD-05 | Engine-level authorizer | §3 |
| TD-06 | Progress handler timeout | §3 |
| TD-07 | Defensive copy contract | §4 |
| TD-08 | ISO-8601 date normalization | §4 |
| TD-09 | Synthetic data generator | §4 |
| TD-10 | Welch's t-test selection | §5 |
| TD-11 | No hardcoded historical values | §5 |
| TD-12 | Dark navy executive theme | §6 |
| TD-13 | Centralized Plotly ChartFactory | §6 |
