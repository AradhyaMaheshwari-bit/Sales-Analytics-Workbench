# Non-Functional Requirements — Sales Analytics Workbench

**SDLC Phase:** 2 — Requirements Analysis
**Document ID:** SRS-NFR
**Version:** 1.0

---

## 1. Overview

Non-functional requirements (NFRs) define quality attributes, constraints, and
system-wide properties beyond specific features. These requirements apply to
the entire application.

---

## 2. Usability (NFR-U)

### NFR-U-01: Intuitive Navigation
**Requirement:** The application shall provide clear sidebar navigation allowing
users to switch between the five modules with at most one click per module.

**Acceptance Criteria:**
- Sidebar menu lists all five modules.
- Current module is visually highlighted.
- Module names match internship task names.
- No broken links or dead-end pages.

### NFR-U-02: Consistent UI Theme
**Requirement:** The application shall apply a professional dark navy and blue
color scheme consistently across all pages, with readable typography and
adequate contrast.

**Acceptance Criteria:**
- Background: dark navy (#0E1117 or similar).
- Primary accent: blue (#1f77b4 or similar).
- Text: white or light gray with contrast ratio ≥ 4.5:1 (WCAG AA).
- Font: system sans-serif (Arial, Segoe UI, or Roboto fallback).
- All interactive elements (buttons, sliders) have hover states.

### NFR-U-03: User Feedback
**Requirement:** The system shall provide clear success, error, warning, and
info messages for all user actions (upload, clean, export, query).

**Acceptance Criteria:**
- Success: green toast/message (e.g., "Dataset cleaned successfully").
- Error: red message with actionable guidance (e.g., "Unsupported format. Upload CSV or XLSX").
- Warning: yellow/orange message for non-critical issues.
- Loading: spinner or progress indicator for operations > 1 second.

### NFR-U-04: Responsive Layout
**Requirement:** The UI shall render correctly at standard desktop resolutions
(1280×720 minimum, 1920×1080 typical).

**Acceptance Criteria:**
- No horizontal scrolling at 1280px width.
- Charts fit viewport or provide scrollable containers.
- Tables paginate or scroll vertically when exceeding viewport height.

---

## 3. Performance (NFR-P)

### NFR-P-01: Upload Performance
**Requirement:** File upload and parsing shall complete within 5 seconds for
datasets ≤ 10,000 rows, ≤ 50 columns.

**Acceptance Criteria:**
- Internship dataset (1,000 rows × 12 columns) loads in < 2 seconds.
- Large datasets (10,000 rows) load in < 5 seconds.
- Progress indicator shown during parsing.

### NFR-P-02: Chart Rendering
**Requirement:** Interactive Plotly charts shall render within 3 seconds for
datasets ≤ 10,000 rows.

**Acceptance Criteria:**
- Charts appear within 3 seconds of triggering.
- Loading spinner shown during render.
- Chart interactions (zoom, hover) respond within 100ms.

### NFR-P-03: Statistical Computation
**Requirement:** Welch's t-test shall compute within 2 seconds for datasets
≤ 10,000 rows per group.

**Acceptance Criteria:**
- Internship dataset (511 male, 489 female) completes in < 1 second.
- Larger groups (5,000 per group) complete in < 2 seconds.

---

## 4. Reliability (NFR-R)

### NFR-R-01: Error Handling
**Requirement:** The application shall handle invalid inputs gracefully without
crashing or exposing stack traces to the user.

**Acceptance Criteria:**
- Invalid file formats: user-friendly error message.
- Empty datasets: "No data to display" message, not a crash.
- Missing required columns: clear guidance on required mappings.
- SQL errors: error message with query syntax hint.
- Division by zero: handled with NaN or infinity checks.

### NFR-R-02: Data Integrity
**Requirement:** The application shall never mutate the original uploaded file
or the user's active DataFrame without explicit user action.

**Acceptance Criteria:**
- Cleaning operations produce a new DataFrame copy.
- Original uploaded file remains unmodified on disk.
- Undo/reset option returns to the original uploaded state.

### NFR-R-03: Deterministic Results
**Requirement:** Statistical and analytical results shall be deterministic — the
same dataset produces the same results across runs.

**Acceptance Criteria:**
- Welch's t-test on internship dataset always produces t = 0.683, p = 0.495.
- Correlation matrix is symmetric and stable.
- Sort order for SQL queries is consistent (ORDER BY applied).

---

## 5. Maintainability (NFR-M)

### NFR-M-01: Modular Code Structure
**Requirement:** The codebase shall follow a modular architecture with
separation of concerns: UI pages, business logic services, data models, and
utilities.

**Acceptance Criteria:**
- `app/pages/` contains Streamlit page scripts.
- `app/services/` contains business logic (cleaning, stats, SQL).
- `app/models/` contains data structures and schemas.
- `app/utils/` contains shared utilities (formatters, validators).
- No page file exceeds 500 lines.

### NFR-M-02: Code Documentation
**Requirement:** All public functions and classes shall have docstrings
explaining purpose, parameters, return values, and exceptions.

**Acceptance Criteria:**
- Every service function has a docstring (Google or NumPy style).
- Complex logic has inline comments.
- Magic numbers (e.g., 0.05 for alpha) are named constants with comments.

### NFR-M-03: PEP 8 Compliance
**Requirement:** Python code shall follow PEP 8 style guidelines (enforced via
linter if available).

**Acceptance Criteria:**
- Line length ≤ 88 characters (Black formatter default).
- 4-space indentation.
- Meaningful variable names (no single-letter except loop indices).
- Imports organized: standard library, third-party, local.

---

## 6. Security (NFR-S)

### NFR-S-01: No Hardcoded Secrets
**Requirement:** The application shall not contain hardcoded credentials,
API keys, or sensitive data in source files.

**Acceptance Criteria:**
- No `.env` files committed to Git.
- No hardcoded passwords, tokens, or connection strings.
- Secrets loaded from environment variables or external config.

### NFR-S-02: Input Validation
**Requirement:** All user inputs (uploaded files, custom SQL, numeric inputs)
shall be validated before processing.

**Acceptance Criteria:**
- File extensions validated against allow-list.
- Custom SQL executes under the approved SELECT-only security policy (D-3):
  - Exactly **one SQL statement** per request (multi-statement input rejected).
  - Only read-only `SELECT` queries permitted.
  - A **SQLite authorizer** (`sqlite3.Connection.set_authorizer`) denies write
    operations (`INSERT`, `UPDATE`, `DELETE`, `DROP`, `ALTER`, `CREATE`,
    `TRUNCATE`, `REPLACE`) and schema modifications at the engine level.
  - **Extension loading disabled** (`enable_load_extension` never called).
  - **Execution-time and result-row limits** applied to prevent resource
    exhaustion.
  - Invalid or prohibited queries return clear, actionable error messages.
- Keyword filtering alone is **not** treated as the security boundary — the
  authorizer is the primary control; keyword checks are at most an early
  convenience filter.
- Numeric inputs validated for range and type.

### NFR-S-03: Safe File Handling
**Requirement:** Uploaded files shall be processed in a safe temporary directory
with no arbitrary code execution.

**Acceptance Criteria:**
- Files are read, not executed.
- No `eval()`, `exec()`, or dynamic imports on user data.
- Malformed Excel files caught and reported, not allowed to crash.

---

## 7. Data Integrity (NFR-D)

### NFR-D-01: Reproducibility
**Requirement:** Given the same input dataset, the application shall produce
identical analytical results across sessions and environments.

**Acceptance Criteria:**
- Statistical tests use fixed seed where randomness is involved (none expected).
- Sorting is deterministic.
- Floating-point precision is consistent (rounding to 2 decimal places for display).

### NFR-D-02: Historical Result Validation
**Requirement:** When using the internship dataset, results shall match the
documented historical values within rounding tolerance (±0.01 for floats).

**Acceptance Criteria:**
- Male orders = 511, female orders = 489.
- Male avg sales = ₹141,807.34 ± ₹1.
- t-statistic = 0.683 ± 0.001.
- p-value = 0.495 ± 0.001.
- CI bounds match documented values.

---

## 8. Scalability (NFR-SC)

### NFR-SC-01: Dataset Size Limits
**Requirement:** The application shall handle datasets up to 50,000 rows × 100
columns without crashing (performance may degrade gracefully).

**Acceptance Criteria:**
- Datasets > 50,000 rows produce a warning but attempt to process.
- Out-of-memory errors are caught and reported.
- Large datasets trigger incremental/chunked processing where possible.

### NFR-SC-02: Concurrent Users
**Requirement:** The application is designed for single-user local execution.
Multi-user concurrency is out of scope.

**Acceptance Criteria:**
- One user session per `streamlit run` process.
- Session state isolates user data (Streamlit session state mechanism).

---

## 9. Compatibility (NFR-C)

### NFR-C-01: Python Version
**Requirement:** The application shall run on Python 3.12+ (tested on 3.14).

**Acceptance Criteria:**
- No deprecated Python features used.
- Dependencies compatible with Python 3.12+.
- Virtual environment setup documented.

### NFR-C-02: Operating System
**Requirement:** The application shall run on Windows 10/11. macOS and Linux
compatibility is a stretch goal but not guaranteed.

**Acceptance Criteria:**
- Path separators use `os.path.join()` or `pathlib.Path`.
- No Windows-specific shell commands in critical paths.
- Installation instructions include Windows-specific steps.

### NFR-C-03: Browser Compatibility
**Requirement:** The Streamlit UI shall render correctly in Chrome 90+, Edge 90+,
Firefox 90+.

**Acceptance Criteria:**
- UI tested in Chrome (primary).
- No browser-specific CSS or JavaScript required.
- Plotly charts render in all three browsers.

---

## 10. Deployment (NFR-DP)

### NFR-DP-01: Installation Simplicity
**Requirement:** The application shall install with at most three commands:
create venv, install requirements, run app.

**Acceptance Criteria:**
- `python -m venv .venv` (or `py -m venv .venv` on Windows).
- `.venv\Scripts\pip install -r requirements.txt`.
- `streamlit run app/main.py`.
- Total setup time < 5 minutes on a clean machine with Python pre-installed.

### NFR-DP-02: No External Services
**Requirement:** The application shall not depend on external APIs, cloud
services, or paid subscriptions.

**Acceptance Criteria:**
- No internet connection required at runtime.
- SQLite used instead of PostgreSQL/MySQL (in-memory database, per FR-15 — no external database server required).
- No API keys needed for demo.

### NFR-DP-03: Startup Time
**Requirement:** The application shall start and display the home page within
10 seconds of running `streamlit run app/main.py`.

**Acceptance Criteria:**
- Import time < 5 seconds.
- Home page renders within 5 seconds.
- Lazy loading for heavy modules where possible.