# User Stories and Use Cases — Sales Analytics Workbench

**SDLC Phase:** 2 — Requirements Analysis
**Document ID:** SRS-US
**Version:** 1.0

---

## 1. User Stories

### US-01: Dataset Upload & Immersion
**As a** technical reviewer evaluating the Phase-II internship project,
**I want to** upload my own sales dataset (CSV or XLSX) or use the pre-loaded internship dataset,
**So that** I can verify the application's ability to handle raw data dynamically.

- **Acceptance Criteria:**
  - File uploader accepts `.csv` and `.xlsx`.
  - Toggle available to switch to "Internship Dataset Mode" instantly.
  - Dimensions, column dtypes, and preview displayed immediately upon upload.

### US-02: Data Cleaning & Wrangling
**As a** data analyst / student developer,
**I want to** inspect missing values, duplicates, and data types, and apply cleaning rules,
**So that** I can transform raw, messy data into an analysis-ready dataset and export it.

- **Acceptance Criteria:**
  - Missing value summary table displayed with counts and percentages.
  - Duplicate row detection with view option.
  - Configurable cleaning options (fill missing, drop duplicates, fix dtypes).
  - Cleaned dataset downloadable as CSV/XLSX.

### US-03: Exploratory Data Analysis & Business Intelligence
**As a** business stakeholder,
**I want to** view descriptive statistics, correlation matrices, and interactive charts,
**So that** I can understand sales distributions, category performance, geographic revenue, and temporal trends.

- **Acceptance Criteria:**
  - Numeric summary statistics table.
  - Correlation matrix heatmap with top pairs highlighted.
  - Interactive Plotly charts (revenue by category, monthly trend, city breakdown, gender distribution).

### US-04: SQL Business Query Execution
**As a** database analyst,
**I want to** execute pre-built SQL business queries against an embedded SQLite database created from the dataset,
**So that** I can verify relational data processing capabilities.

- **Acceptance Criteria:**
  - Seven pre-built SQL queries available in a dropdown.
  - Query description and results table displayed.
  - Custom SQL query editor for advanced exploration, restricted to read-only `SELECT` execution under the approved security policy (single statement per request; SQLite authorizer denies writes and schema changes; extension loading disabled; time/row limits enforced).

### US-05: Power BI Dashboard Showcase
**As a** project evaluator,
**I want to** view the authentic Power BI dashboard deliverables (screenshots, DAX measures, slicers, visuals),
**So that** I can verify the industry-standard BI work completed during the internship.

- **Acceptance Criteria:**
  - Power BI screenshots displayed.
  - All 6 DAX measures explained with formulas.
  - 4 slicers and 6 visualizations documented.
  - Clear attribution that Power BI is an authentic standalone deliverable.

### US-06: Statistical Hypothesis Testing
**As a** statistician / reviewer,
**I want to** run Welch's independent two-sample t-test comparing male and female average sales,
**So that** I can verify formal hypothesis testing, p-values, t-statistics, and 95% confidence intervals on the data.

- **Acceptance Criteria:**
  - Null and alternative hypotheses stated.
  - T-statistic, p-value, mean difference, and 95% CI displayed.
  - Decision (Fail to Reject H₀) and plain-language interpretation displayed.
  - Recomputes live on uploaded datasets; reproduces historical values (t=0.683, p=0.495) on internship dataset.

### US-07: Data Storytelling & Outcomes
**As a** university evaluator,
**I want to** review key business insights, project outcomes, and GitHub portfolio links,
**So That** I have a complete summary of the 60-day internship achievements.

- **Acceptance Criteria:**
  - Summary of all 5 internship tasks.
  - Key business findings highlighted.
  - GitHub portfolio repository links provided.
  - Final project conclusion.

---

## 2. Use Cases

### UC-01: End-to-End Analytics Workflow (Main Flow)

| Field | Value |
|---|---|
| **Use Case ID** | UC-01 |
| **Title** | End-to-End Analytics Execution |
| **Primary Actor** | University Evaluator / Student |
| **Preconditions** | Application running (`streamlit run app/main.py`). |
| **Trigger** | User opens application in browser. |
| **Postconditions** | User has explored data, cleaned it, viewed EDA, run SQL queries, checked BI showcase, and reviewed statistical validation. |

**Normal Flow:**
1. User launches application; home page displays project overview and module navigation.
2. User selects **Module 1 (Data Immersion & Wrangling)**.
3. User selects "Internship Dataset" (or uploads a custom dataset).
4. System displays dataset profile (dimensions, columns, missing values, duplicates).
5. User clicks "Run Cleaning Pipeline"; system cleans data and displays summary; user downloads cleaned dataset.
6. User navigates to **Module 2 (EDA & Business Intelligence)**.
7. System displays descriptive statistics, correlation matrix, and Plotly charts.
8. User selects and runs pre-built SQL queries from the dropdown against the SQLite database.
9. User navigates to **Module 3 (Dashboard & Power BI Showcase)**.
10. System displays Power BI screenshots, DAX measures, and slicer documentation.
11. User navigates to **Module 4 (Statistical Validation)**.
12. System performs Welch's t-test and displays t-statistic, p-value, 95% CI, and interpretation.
13. User navigates to **Module 5 (Data Storytelling & Outcomes)**.
14. System displays key insights, task summary, and GitHub links.
15. Use case ends successfully.

**Alternative Flows:**
- *A1 (Invalid File Upload):* User uploads an unsupported file format (e.g., `.pdf` or `.txt`). System displays error message prompting for CSV or XLSX and halts processing.
- *A2 (Missing Columns in Custom Upload):* User uploads a CSV lacking expected sales columns. System prompts user with column mapping interface (FR-CC-02).
- *A3 (SQL Query Error):* User enters invalid custom SQL. SQLite raises an exception; system catches it, displays error message, and prevents crash.