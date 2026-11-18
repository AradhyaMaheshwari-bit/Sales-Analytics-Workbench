# Project Scope — Sales Analytics Workbench

**SDLC Phase:** 1 — Project Planning and Feasibility Study

---

## 1. In-Scope Features

### Module 1 — Data Immersion & Data Wrangling
- Upload CSV and XLSX datasets (with file validation).
- Display dataset dimensions, preview, column info, dtypes.
- Missing-value detection and duplicate detection.
- Configurable cleaning: drop/fill missing values, drop duplicates, data-type
  coercion, business-rule validation.
- Feature engineering: date-derived columns (year, month, quarter, day-of-week),
  revenue verification (`Quantity × Unit_Price` vs `Total_Sales`).
- Cleaning summary report; export cleaned dataset (CSV / XLSX).

### Module 2 — EDA & Business Intelligence
- Descriptive statistics (numerical + categorical).
- Correlation matrix and key-pair correlations.
- Distribution, category-wise, city-wise, and time-based analyses.
- Interactive Plotly visualizations.
- SQLite database creation and seven prepared business SQL queries.

### Module 3 — Dashboard & Power BI Showcase
- Project KPI cards.
- Explanation of the six DAX measures.
- Display of Power BI dashboard screenshots.
- Explanation of the four slicers and six visualizations.
- Attribution to the original Power BI deliverable.

### Module 4 — Statistical Validation
- Null / alternative hypothesis formulation.
- Welch's independent two-sample t-test (recomputed on active dataset).
- t-statistic, p-value, 95% confidence interval, significance level, decision,
  and plain-language interpretation.

### Module 5 — Data Storytelling & Project Outcomes
- Key business insights, project outcomes, five-task summary.
- GitHub portfolio links, reports and deliverables access, final summary.

### Cross-cutting
- Dark navy / blue professional UI (sidebar navigation, cards, tables, loading
  indicators, success/error messages, empty states, responsive layout).
- Two operating modes: Uploaded Dataset and Internship Dataset.
- Column detection and configurable mapping for non-identical schemas.

## 2. Out-of-Scope Features

| Item | Reason |
|---|---|
| Embedding or executing a `.pbix` file | Power BI Desktop is required; not available cross-platform. Shown as an authentic deliverable only. |
| Power BI Online / Power Platform integration | Requires paid/enterprise Microsoft licensing. |
| Real-time data pipelines / streaming | Outside the internship scope (batch analytics only). |
| Multi-user authentication / hosting | Single-user local demonstration. |
| Modifying the five original GitHub repositories | Explicitly prohibited. |
| Modifying `Phase-I_Evaluation/` | Explicitly prohibited (read-only submission). |
| Large-scale cloud deployment | Local university demonstration only. |
| ML / predictive modelling | Not part of the internship deliverables. |

## 3. Functional Boundary Summary

```
INGEST  : CSV / XLSX upload  ──►  Internship dataset fallback
PROCESS : profile → clean → validate → feature-engineer
ANALYZE : EDA → SQL queries → correlations → visualizations
VALIDATE: Welch's t-test + confidence interval
PRESENT : KPIs → Power BI showcase → storytelling → outcomes
EXPORT  : cleaned CSV / XLSX, SQLite DB, Excel report
```

## 4. Non-Functional Scope

Usability, performance, reliability, maintainability, security, data integrity,
scalability and compatibility are documented in
`docs/02-requirements/non-functional-requirements.md`.