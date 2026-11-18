# Security and Reliability Design — Sales Analytics Workbench

**SDLC Phase:** 3 — System Design (Checkpoint B)
**Document ID:** SDD-SEC
**Version:** 1.0

---

## 1. Overview

This document specifies the complete security architecture and reliability engineering design for the Sales Analytics Workbench, covering file upload validation, SQL engine security, data privacy, session isolation, error handling, and graceful degradation.

---

## 2. File Upload Security

### 2.1 Allowlisted File Types
- **Accepted Extensions:** `.csv`, `.xlsx` only.
- **Validation Mechanism:** File extension check **AND** MIME type sniffing via Python `imghdr`/`magic` library; both must agree.
- **Rejected Files:** All other extensions are rejected before reading. Error message: *"Unsupported file type. Please upload a .csv or .xlsx file."*

### 2.2 File Size Limit
- **Maximum File Size:** 50 MB per upload.
- **Enforcement:** Size check performed before `pd.read_csv()` / `pd.read_excel()` call.
- **Rationale:** Prevents memory exhaustion (`OutOfMemoryError`) from a maliciously or accidentally large file on the Streamlit server.

### 2.3 Malformed File Handling
- **CSV Parsing:** `pd.read_csv(errors='replace')` for encoding issues; truncated files raise `pd.errors.ParserError`, caught and reported to the user.
- **Excel Parsing:** `pd.read_excel()` wrapped in try/except `Exception`; password-protected files raise `openpyxl.utils.exceptions.InvalidFileException`, reported cleanly.
- **Malicious Content:** No macro execution (`.xlsx` macros are never executed by openpyxl); no formula evaluation.

---

## 3. SQL Security Architecture (Decision D-3)

Full specification is documented in [SDD-DB-SQL §4](database-and-sql-design.md). Summary of controls:

| Control | Mechanism | Enforcement Point |
|---|---|---|
| SELECT-only enforcement | `sqlite3.Connection.set_authorizer` callback | SQLite engine (kernel level) |
| Write operations blocked | SQLITE_DENY on INSERT/UPDATE/DELETE/CREATE/DROP/PRAGMA | Authorizer callback |
| Schema introspection blocked | Deny READ on `sqlite_master`, `sqlite_schema` | Authorizer callback |
| Multi-statement injection blocked | Single-statement pre-check before `cursor.execute()` | `queries.py` service |
| Computational timeout | `set_progress_handler` — 2s / 1,000,000 opcodes | SQLite engine (kernel level) |
| Result-row overflow | `cursor.fetchmany(500)` | `queries.py` service |

### 3.1 Security Boundary Guarantee
The SQL security boundary is the SQLite engine authorizer. Keyword allowlisting / regex-based query filtering is **not** the primary security boundary and is **not relied upon** for security enforcement. The authorizer fires at the engine level regardless of input format, encoding, or obfuscation.

### 3.2 SQL Injection Risk Profile
Because all user SQL input is executed against an **in-memory, single-table SQLite database** containing only the user's own uploaded or loaded dataset:
- There is no persistent database to corrupt.
- There are no system secrets accessible via SQL.
- Data exfiltration via SQL is bounded to the user's own active dataset.
- The authorizer and row limit prevent destructive or computationally abusive queries.

---

## 4. Data Privacy Design

### 4.1 No Data Persistence
- The in-memory SQLite database (`:memory:`) is destroyed when the Streamlit session ends or is reset. No user data is written to disk by the application.
- Uploaded files are processed in memory only; they are not saved to a server filesystem path.

### 4.2 No External Transmission
- The application transmits no user data to external APIs, analytics services, or third-party backends.
- All computation is local (Streamlit server / local machine).

### 4.3 Internship Dataset Privacy
- The unmodified internship dataset (`data/raw/`) is excluded from Git (`.gitignore: *.csv, *.xlsx`), ensuring customer-adjacent records from the ApexPlanet project are not committed to a public repository.
- The synthetic demonstration generator (Scenario A, `scripts/generate_demo_data.py`) produces statistically representative but entirely fictional data; it never reproduces actual customer identifiers.

---

## 5. Session Isolation & State Safety

### 5.1 Per-Session Database
Each browser session has its own `st.session_state` dictionary and its own `sqlite3.Connection(":memory:")`. Streamlit's architecture ensures session state is never shared across concurrent users.

### 5.2 Defensive Copying Contract
All DataFrame mutations flow through `df.copy(deep=True)` before modification. `st.session_state['raw_df']` is permanently read-only; no code path writes to it after initial population. This is specified in [SDD-DATA §2](data-architecture.md).

---

## 6. Error Handling & Reliability Design

### 6.1 Error Handling Philosophy
Every external I/O operation and user-triggered computation is wrapped in structured `try/except` blocks. Exceptions are never silently swallowed; they are captured, logged at the appropriate severity level, and surfaced to the user as an actionable error callout.

### 6.2 Error Classification & User Messaging

| Error Class | Examples | User-Facing Message | Severity |
|---|---|---|---|
| **File I/O** | Unsupported format, corrupted file | "Unable to parse file. Please verify it is a valid CSV or XLSX." | `warning` |
| **SQL Security Denial** | Authorizer blocks INSERT/DROP | "Security Violation: Only SELECT queries on the `sales` table are permitted." | `error` |
| **SQL Timeout** | Complex query exceeds 2s / 1M opcodes | "Query exceeded the computational time limit. Simplify your query or add a WHERE clause." | `error` |
| **Statistical Invalid Input** | $N < 5$ per group, zero variance | "Statistical test aborted. See warning details." | `warning` |
| **Empty Dataset** | No rows after filtering | "No data matches the current filters. Adjust your selection." | `info` |
| **Date Parse Failure** | Unparseable `Order_Date` values | "X rows contained unparseable dates and have been stored as NULL." | `warning` |
| **Unexpected Exception** | Unhandled runtime error | "An unexpected error occurred. Please report this to the developer." | `error` |

### 6.3 Graceful Degradation Rules
- If `active_df` is not yet populated (no dataset loaded), all analysis pages display the **empty state**: *"No dataset loaded. Upload a file or enable Demo Mode."* — no module crashes or raises an uncaught exception.
- If the SQLite connection is not available (`db_conn` missing from session state), SQL page renders a non-fatal warning rather than throwing `AttributeError`.
- If Power BI screenshot assets are missing from `app/assets/power_bi/`, Module 4 renders an info banner: *"Dashboard screenshots not found. Please add assets to app/assets/power_bi/."*

---

## 7. Structured Logging Design

### 7.1 Logger Configuration (`app/utils/logger.py`)
- **Library:** Python standard `logging` module.
- **Log Levels:** `DEBUG` (development), `INFO` (successful operations), `WARNING` (data quality issues), `ERROR` (caught exceptions), `CRITICAL` (unrecoverable failures).
- **Format:** `[YYYY-MM-DD HH:MM:SS] [LEVEL] [module_name]: message`
- **No Sensitive Data:** Column values, user file names, and actual data row contents are never included in log output to prevent accidental exposure.

### 7.2 Logged Events
- Dataset load (source: upload / internship / synthetic), row count, column count.
- Cleaning operations applied (type, columns affected, rows changed).
- SQL query execution (query hash, execution time ms, row count returned).
- Security authorizer denials (action code, table name).
- Statistical test execution (group sizes, t-statistic, p-value, decision).
- All caught exceptions with traceback (except in production where tracebacks are suppressed from UI).

---

## 8. Requirement Traceability

| Requirement | Covered By |
|---|---|
| NFR-S-01: Input validation | §2 (File Upload Security) |
| NFR-S-02: SQL security | §3 (SQL Security Architecture) |
| NFR-R-01: Error handling | §6 (Error Handling & Reliability Design) |
| NFR-R-02: Data integrity | §5.2 (Defensive Copying Contract) |
| NFR-DP-01: No data persistence | §4.1 |
| NFR-DP-02: In-memory SQLite | §5.1 |
| NFR-M-02: Logging | §7 (Structured Logging Design) |
