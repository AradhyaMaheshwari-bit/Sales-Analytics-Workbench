# Functional Requirements — Sales Analytics Workbench

**SDLC Phase:** 2 — Requirements Analysis
**Document ID:** SRS-FR
**Version:** 1.0

---

## 1. Overview

This document defines 22 functional requirements (20 core + 2 cross-cutting)
organized by application module. Each requirement has an ID, description,
acceptance criteria, and priority level.

Priority levels:
- **P0 (Critical):** Must deliver for evaluation; app non-functional without it.
- **P1 (High):** Expected by evaluator; strongly impacts demo quality.
- **P2 (Medium):** Enhances experience; acceptable to defer if schedule requires.

---

## 2. Module 1 — Data Immersion & Data Wrangling

### FR-01: Dataset Upload
| Field | Value |
|---|---|
| ID | FR-01 |
| Title | Dataset Upload |
| Description | The system shall allow users to upload a dataset file in CSV or XLSX format through a file uploader widget. |
| Acceptance Criteria | 1. File uploader accepts `.csv` and `.xlsx` only. 2. Unsupported formats show a clear error message. 3. Files > 50 MB are rejected with a size warning. 4. Successfully uploaded files are parsed into a pandas DataFrame without modifying the original file. |
| Priority | P0 |
| Module | Data Immersion & Data Wrangling |

### FR-02: CSV and Excel Support
| Field | Value |
|---|---|
| ID | FR-02 |
| Title | Multi-format File Parsing |
| Description | The system shall parse CSV files (comma-delimited, UTF-8) and XLSX files (first sheet by default) into a tabular DataFrame. |
| Acceptance Criteria | 1. CSV files are parsed with `pandas.read_csv()`. 2. XLSX files are parsed with `pandas.read_excel()` using openpyxl engine. 3. Encoding errors are caught and reported. 4. Empty files produce a clear "empty dataset" message, not a crash. |
| Priority | P0 |
| Module | Data Immersion & Data Wrangling |

### FR-03: Dataset Preview
| Field | Value |
|---|---|
| ID | FR-03 |
| Title | Dataset Preview |
| Description | The system shall display the first N rows of the uploaded dataset in a scrollable table. Users can adjust N (default: 10). |
| Acceptance Criteria | 1. Default preview shows 10 rows. 2. Adjustable via slider/number input (range 5–100). 3. Columns are not truncated. 4. Large values display correctly (e.g., ₹ values). |
| Priority | P0 |
| Module | Data Immersion & Data Wrangling |

### FR-04: Data Profiling
| Field | Value |
|---|---|
| ID | FR-04 |
| Title | Data Profiling Summary |
| Description | The system shall display dataset dimensions (rows × columns), column names, data types per column, memory usage, and basic shape information. |
| Acceptance Criteria | 1. Row count and column count displayed as KPI cards. 2. Column info table shows: name, dtype, non-null count, null count, null %. 3. Memory usage displayed in human-readable format (KB/MB). |
| Priority | P0 |
| Module | Data Immersion & Data Wrangling |

### FR-05: Missing Value Detection
| Field | Value |
|---|---|
| ID | FR-05 |
| Title | Missing Value Detection |
| Description | The system shall identify and display missing values per column, both as counts and percentages. |
| Acceptance Criteria | 1. Table showing column name, missing count, missing %. 2. Columns with zero missing values are included (showing 0). 3. Visual indicator (bar or highlight) for columns exceeding a threshold (e.g., > 5%). 4. Total missing values displayed as a summary metric. |
| Priority | P0 |
| Module | Data Immersion & Data Wrangling |

### FR-06: Duplicate Detection
| Field | Value |
|---|---|
| ID | FR-06 |
| Title | Duplicate Row Detection |
| Description | The system shall detect and report duplicate rows in the dataset. |
| Acceptance Criteria | 1. Total duplicate count displayed. 2. Option to view the duplicate rows. 3. Duplicates identified across all columns by default. 4. Zero duplicates produces a success message. |
| Priority | P0 |
| Module | Data Immersion & Data Wrangling |

### FR-07: Data Type Inspection
| Field | Value |
|---|---|
| ID | FR-07 |
| Title | Data Type Inspection and Anomaly Detection |
| Description | The system shall display the inferred data type for each column and flag potential type mismatches (e.g., a numeric column stored as object). |
| Acceptance Criteria | 1. Data types shown per column. 2. Columns where the dtype is `object` but > 80% of values are numeric are flagged as potential type issues. 3. Date-like strings in object columns are flagged for conversion. |
| Priority | P1 |
| Module | Data Immersion & Data Wrangling |

### FR-08: Data Cleaning
| Field | Value |
|---|---|
| ID | FR-08 |
| Title | Configurable Data Cleaning |
| Description | The system shall provide configurable cleaning operations: handle missing values (drop rows, fill with mean/median/mode/custom), remove duplicates, and correct data types. |
| Acceptance Criteria | 1. Missing value strategy selectable per column or globally. 2. Duplicate removal toggle. 3. Type conversion options (to numeric, to datetime, to category). 4. Original DataFrame is never mutated — cleaning produces a new copy. 5. Cleaning summary shows before/after row count, columns affected, actions taken. |
| Priority | P0 |
| Module | Data Immersion & Data Wrangling |

### FR-09: Data Validation
| Field | Value |
|---|---|
| ID | FR-09 |
| Title | Business Rule Validation |
| Description | The system shall validate business rules on the dataset: numeric fields contain valid numbers, Quantity > 0, Unit_Price > 0, Total_Sales ≈ Quantity × Unit_Price (within rounding tolerance). |
| Acceptance Criteria | 1. Validation rules are applied after cleaning. 2. Violations are reported per row with column and expected vs. actual values. 3. Validation is configurable (user can enable/disable rules). 4. A validation summary shows pass/fail counts. |
| Priority | P1 |
| Module | Data Immersion & Data Wrangling |

### FR-10: Cleaned Dataset Export
| Field | Value |
|---|---|
| ID | FR-10 |
| Title | Export Cleaned Dataset |
| Description | The system shall allow users to download the cleaned dataset as CSV or XLSX. |
| Acceptance Criteria | 1. Download button produces a valid file. 2. CSV export uses UTF-8 encoding. 3. XLSX export uses openpyxl engine. 4. Exported file contains only the cleaned data, not the original. 5. File name includes a timestamp or "cleaned" suffix. |
| Priority | P0 |
| Module | Data Immersion & Data Wrangling |

---

## 3. Module 2 — EDA & Business Intelligence

### FR-11: Exploratory Data Analysis
| Field | Value |
|---|---|
| ID | FR-11 |
| Title | Exploratory Data Analysis Dashboard |
| Description | The system shall perform and display EDA including distribution analysis, category-wise analysis, city-wise analysis, and time-based analysis using interactive Plotly charts. |
| Acceptance Criteria | 1. At least 5 distinct chart types displayed. 2. Charts are interactive (hover, zoom, download). 3. Charts adapt to dark theme. 4. Empty/single-value columns produce a message, not a crash. |
| Priority | P0 |
| Module | EDA & Business Intelligence |

### FR-12: Statistical Summaries
| Field | Value |
|---|---|
| ID | FR-12 |
| Title | Descriptive Statistics |
| Description | The system shall display descriptive statistics (count, mean, std, min, quartiles, max) for all numeric columns and frequency tables for categorical columns. |
| Acceptance Criteria | 1. Numeric summary matches `DataFrame.describe()` output. 2. Categorical summary shows unique count, top value, frequency. 3. Currency values are formatted with ₹ symbol and commas. |
| Priority | P0 |
| Module | EDA & Business Intelligence |

### FR-13: Correlation Analysis
| Field | Value |
|---|---|
| ID | FR-13 |
| Title | Correlation Matrix and Key Pairs |
| Description | The system shall compute and display a Pearson correlation matrix for numeric columns, highlighting the strongest positive and negative correlations. |
| Acceptance Criteria | 1. Heatmap visualization with color scale. 2. Top 3 positive and top 3 negative correlation pairs listed. 3. Correlation between Unit_Price and Total_Sales highlighted (historical r = 0.686). 4. Age vs Total_Sales shown (historical r = 0.001). |
| Priority | P1 |
| Module | EDA & Business Intelligence |

### FR-14: Interactive Visualizations
| Field | Value |
|---|---|
| ID | FR-14 |
| Title | Interactive Plotly Charts |
| Description | The system shall render all analytical charts using Plotly with interactivity (hover tooltips, zoom, pan, download as PNG). |
| Acceptance Criteria | 1. All charts use Plotly (`plotly.express` or `plotly.graph_objects`). 2. Dark navy theme applied consistently. 3. Hover shows exact values. 4. PNG download available. |
| Priority | P0 |
| Module | EDA & Business Intelligence |

### FR-15: SQLite Database Operations
| Field | Value |
|---|---|
| ID | FR-15 |
| Title | SQLite Database Creation |
| Description | The system shall create an in-memory SQLite database from the active (cleaned) dataset, allowing SQL queries to be executed against it. |
| Acceptance Criteria | 1. DataFrame is loaded into SQLite table named `sales`. 2. Schema matches DataFrame columns and types. 3. Row count in SQLite matches DataFrame row count. 4. Database is created fresh for each session/upload. 5. Custom queries against this database execute under the SELECT-only policy defined in NFR-S-02 (single statement, read-only authorizer, no extension loading, time/row limits). |
| Priority | P0 |
| Module | EDA & Business Intelligence |

### FR-16: SQL Business Queries
| Field | Value |
|---|---|
| ID | FR-16 |
| Title | Pre-built SQL Business Queries |
| Description | The system shall provide seven pre-built SQL queries answering key business questions (adapted from internship Task-1/Task-2 repository queries). |
| Acceptance Criteria | 1. Seven queries are available from a dropdown. 2. Each query has a title and business question description. 3. Query results displayed in a formatted table. 4. Users can also type and execute custom SQL queries. 5. Invalid SQL produces an error message, not a crash. 6. Custom SQL executes under the approved SELECT-only security policy (D-3): exactly one statement per request, read-only `SELECT` queries only, enforced via a SQLite authorizer that denies write operations and schema modifications, extension loading disabled, execution-time and result-row limits applied. Keyword filtering alone is not the security boundary. |
| Priority | P0 |
| Module | EDA & Business Intelligence |
| Notes | Queries preserved from https://github.com/AradhyaMaheshwari-bit/Sales-Performance-Dashboard-Data-Analytics-Project (file `SQL_Analysis.py`). Query 5 required a schema adaptation (extracting month from `Order_Date` via SQLite `STRFTIME()`); the other six are verbatim. See `docs/02-requirements/sql-query-reference.md` for the full query list. |

### FR-17: Excel Report Generation
| Field | Value |
|---|---|
| ID | FR-17 |
| Title | Excel Report Export |
| Description | The system shall generate a downloadable Excel report containing summary statistics, KPIs, and key data tables. |
| Acceptance Criteria | 1. Report includes sheets: Summary, Statistics, Query Results. 2. KPI values are formatted. 3. Download button produces a valid `.xlsx` file. 4. File opens correctly in Excel / LibreOffice Calc. |
| Priority | P1 |
| Module | EDA & Business Intelligence |

---

## 4. Module 3 — Dashboard & Power BI Showcase

### FR-18: Power BI Project Showcase
| Field | Value |
|---|---|
| ID | FR-18 |
| Title | Power BI Dashboard Showcase |
| Description | The system shall showcase the Power BI dashboard as an authentic deliverable: display dashboard screenshots, explain each of the six DAX measures, describe the four slicers, and document the six visualizations. |
| Acceptance Criteria | 1. Dashboard screenshot(s) displayed. 2. Each DAX measure listed with formula and purpose. 3. Four slicers described (City, Category, Gender, Month). 4. Six visualizations listed with chart type and purpose. 5. Clear labeling: "This is a screenshot of the actual Power BI dashboard" — no claim that Python charts are Power BI. 6. Link to `.pbix` file or note about availability. |
| Priority | P0 |
| Module | Dashboard & Power BI Showcase |

---

## 5. Module 4 — Statistical Validation

### FR-19: Statistical Hypothesis Testing
| Field | Value |
|---|---|
| ID | FR-19 |
| Title | Welch's Independent Two-Sample T-Test |
| Description | The system shall formulate null/alternative hypotheses, perform Welch's t-test on the active dataset (grouping by Gender on Total_Sales), compute t-statistic, p-value, 95% confidence interval, and provide a plain-language interpretation. |
| Acceptance Criteria | 1. H₀ and H₁ clearly stated. 2. Test runs on the *active* (uploaded or internship) dataset — never hardcoded. 3. t-statistic, p-value, CI bounds displayed. 4. Significance level (α = 0.05) shown. 5. Decision ("Reject H₀" or "Fail to Reject H₀") derived from p-value comparison. 6. Interpretation paragraph explains the result in business terms. 7. When using the **unmodified** internship dataset (1,000 rows, Gender column with Male/Female values), results reproduce the historical values (t = 0.683, p = 0.495, CI: −₹9,231.58 to ₹19,079.85) within rounding tolerance. 8. Any uploaded or cleaned dataset produces freshly computed results that may legitimately differ from the historical values. |
| Priority | P0 |
| Module | Statistical Validation |

---

## 6. Module 5 — Data Storytelling & Project Outcomes

### FR-20: Final Project Insights and Reports
| Field | Value |
|---|---|
| ID | FR-20 |
| Title | Data Storytelling & Project Summary |
| Description | The system shall present key business insights, project outcomes for each of the five internship tasks, GitHub portfolio links, and a final project summary. |
| Acceptance Criteria | 1. Key insights displayed (Electronics revenue, Patna geographic lead, correlation findings). 2. Five-task summary with deliverables per task. 3. GitHub repository links (5 repos + master portfolio). 4. Final summary with total deliverables count. 5. Historical results clearly labeled as "Internship Results" vs. dynamically computed results. |
| Priority | P1 |
| Module | Data Storytelling & Project Outcomes |

---

## 7. Cross-Cutting Functional Requirements

### FR-CC-01: Internship Dataset Mode
| Field | Value |
|---|---|
| ID | FR-CC-01 |
| Title | Internship Dataset Mode |
| Description | The system shall provide a mode where a demonstration dataset (1,000 records, 12 columns matching the internship schema) is loaded automatically for demonstration purposes, without requiring the evaluator to upload a file. Data is supplied per the approved two-scenario strategy in `demonstration-data-strategy.md`: Scenario A (synthetic generator output, approved under D-1) or Scenario B (user's private local copy of the internship dataset). |
| Acceptance Criteria | 1. Sidebar toggle or option to switch between "Upload" and "Internship Dataset" modes. 2. Scenario B: a **read-only copy** of the dataset is placed in `data/raw/internship_dataset.xlsx` by a manual, one-time setup step — excluded from Git via `.gitignore`. 3. The application loads only from `data/raw/` at runtime, never reading from `Phase-I_Evaluation/` directly. 4. The original file in `Phase-I_Evaluation/` remains completely unmodified. 5. The private copy is for local demonstration only and never exposed via any public deployment. 6. Scenario A: when the private copy is absent, the application remains fully usable with a synthetic dataset produced by `scripts/generate_demo_data.py` (created in Phase 4), whose output is likewise excluded from Git. 7. When the internship dataset is absent entirely, Internship Dataset Mode shows a clear "dataset not found" setup message instead of crashing. |
| Priority | P0 |

### FR-CC-02: Column Detection and Mapping
| Field | Value |
|---|---|
| ID | FR-CC-02 |
| Title | Flexible Column Mapping |
| Description | The system shall detect columns in uploaded datasets and allow users to map them to expected analysis columns (e.g., which column is "Total Sales", which is "Gender") when column names differ from the internship schema. |
| Acceptance Criteria | 1. Auto-detection when column names match expected schema. 2. Manual mapping UI when names differ. 3. Unmapped optional columns are skipped gracefully. 4. Required columns (at minimum one numeric column) must be mapped or analysis is blocked with a clear message. |
| Priority | P1 |