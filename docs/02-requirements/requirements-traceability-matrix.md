# Requirements Traceability Matrix (RTM) — Sales Analytics Workbench

**SDLC Phase:** 2 — Requirements Analysis
**Document ID:** SRS-RTM
**Version:** 1.1

---

## 1. Overview

The Requirements Traceability Matrix maps functional requirements (FRs) to
user stories (US), design components, and test cases (TC) to ensure complete
coverage and prevent orphaned features.

> **Important:** All file paths listed in the "Design Component" column are
> **provisional** and represent the proposed architecture. They will be
> validated and finalized during Phase 3 (System Design). No code is created
> during Phase 2. If the architecture changes during Phase 3, this RTM will be
> updated accordingly.

---

## 2. Traceability Matrix Table

| Req ID | Requirement Title | User Story | Module | Design Component | Test Case ID | Priority |
|---|---|---|---|---|---|---|
| FR-01 | Dataset Upload | US-01 | Module 1 | `app/services/data_loader.py` | TC-01-01 | P0 |
| FR-02 | Multi-format Parsing | US-01 | Module 1 | `app/services/data_loader.py` | TC-01-02 | P0 |
| FR-03 | Dataset Preview | US-01 | Module 1 | `app/pages/01_data_immersion.py` | TC-01-03 | P0 |
| FR-04 | Data Profiling | US-01 | Module 1 | `app/services/profiler.py` | TC-01-04 | P0 |
| FR-05 | Missing Value Detection | US-02 | Module 1 | `app/services/profiler.py` | TC-01-05 | P0 |
| FR-06 | Duplicate Detection | US-02 | Module 1 | `app/services/profiler.py` | TC-01-06 | P0 |
| FR-07 | Data Type Inspection | US-02 | Module 1 | `app/services/profiler.py` | TC-01-07 | P1 |
| FR-08 | Configurable Cleaning | US-02 | Module 1 | `app/services/cleaner.py` | TC-01-08 | P0 |
| FR-09 | Business Rule Validation | US-02 | Module 1 | `app/services/validator.py` | TC-01-09 | P1 |
| FR-10 | Cleaned Dataset Export | US-02 | Module 1 | `app/pages/01_data_immersion.py` | TC-01-10 | P0 |
| FR-11 | Exploratory Data Analysis | US-03 | Module 2 | `app/pages/02_eda_bi.py` | TC-02-01 | P0 |
| FR-12 | Descriptive Statistics | US-03 | Module 2 | `app/services/eda.py` | TC-02-02 | P0 |
| FR-13 | Correlation Analysis | US-03 | Module 2 | `app/services/eda.py` | TC-02-03 | P1 |
| FR-14 | Interactive Plotly Charts | US-03 | Module 2 | `app/components/charts.py` | TC-02-04 | P0 |
| FR-15 | SQLite Database Creation | US-04 | Module 2 | `app/database/db_manager.py` | TC-02-05 | P0 |
| FR-16 | SQL Business Queries | US-04 | Module 2 | `app/database/queries.py` | TC-02-06 | P0 |
| FR-17 | Excel Report Generation | US-03 | Module 2 | `app/services/report_generator.py` | TC-02-07 | P1 |
| FR-18 | Power BI Showcase | US-05 | Module 3 | `app/pages/03_power_bi.py` | TC-03-01 | P0 |
| FR-19 | Statistical Hypothesis Test | US-06 | Module 4 | `app/services/statistics.py` | TC-04-01 | P0 |
| FR-20 | Data Storytelling & Summary | US-07 | Module 5 | `app/pages/05_outcomes.py` | TC-05-01 | P1 |
| FR-CC-01 | Internship Dataset Mode | US-01 | Cross-cutting | `app/services/data_loader.py` | TC-CC-01 | P0 |
| FR-CC-02 | Flexible Column Mapping | US-01 | Cross-cutting | `app/services/data_loader.py` | TC-CC-02 | P1 |

---

## 3. Coverage Summary

- **Total Functional Requirements:** 22 (20 core + 2 cross-cutting)
- **Covered by User Stories:** 22 / 22 (100%)
- **Covered by Design Components:** 22 / 22 (100%)
- **Covered by Planned Test Cases:** 22 / 22 (100%)
- **Orphaned Requirements:** 0
- **Unmapped Test Cases:** 0