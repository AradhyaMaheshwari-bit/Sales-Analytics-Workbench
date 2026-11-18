# Problem Statement & Objectives — Sales Analytics Workbench

**SDLC Phase:** 1 — Project Planning and Feasibility Study

---

## 1. Problem Statement

The 60-day internship produced **five independent artifacts** across five GitHub
repositories: a cleaned dataset, an Excel dashboard, a Power BI `.pbix`, a
statistical hypothesis test, and a 9-slide presentation. For the Phase-II
evaluation these artifacts have three limitations:

1. **Static** — a reviewer cannot change the input data and observe how
   statistics, queries and charts change.
2. **Fragmented** — the pipeline is split across files, folders and repos; the
   end-to-end flow is not visible in one place.
3. **Opaque** — results (e.g. t-statistic = 0.683, p-value = 0.495) are
   presented without the reviewer being able to recompute them.

## 2. Business Objectives

| ID | Objective |
|---|---|
| BO-1 | Provide a single runnable application that demonstrates the full analytics pipeline. |
| BO-2 | Allow reviewers to verify every analytical result by recomputing it live. |
| BO-3 | Support two modes: **Uploaded Dataset** (user-supplied data) and **Internship Dataset** (original 1,000-record dataset). |
| BO-4 | Reuse existing internship deliverables (methodology, queries, DAX, stats) with proper attribution. |
| BO-5 | Deliver a professional, university-demonstration-ready product with no external dependencies or paid licenses. |

## 3. Project Goals

| ID | Goal |
|---|---|
| GO-1 | Build a modular Streamlit application with five modules matching the five internship tasks. |
| GO-2 | Implement a reusable data-wrangling library (upload → profile → clean → export). |
| GO-3 | Implement EDA with descriptive stats, correlation, and Plotly visualizations. |
| GO-4 | Implement SQLite-backed SQL business queries. |
| GO-5 | Showcase the Power BI dashboard as an authentic deliverable (screenshots + DAX + slicers), without claiming Python charts are Power BI. |
| GO-6 | Implement Welch's t-test that recomputes on any uploaded dataset — never hardcoded. |
| GO-7 | Provide data storytelling and project-outcome summaries. |
| GO-8 | Provide a pytest test suite covering edge cases. |
| GO-9 | Provide complete deployment documentation. |

## 4. Success Criteria (SMART)

| ID | Criterion | Measure |
|---|---|---|
| SC-1 | App starts locally | `streamlit run app/main.py` succeeds in a clean venv. |
| SC-2 | Internship mode reproduces history | Historical stats match documented values within rounding. |
| SC-3 | Uploaded mode computes fresh results | t-test p-value differs from history when data differs. |
| SC-4 | Tests pass | `pytest` exits 0 with ≥ 90 % requirement coverage. |
| SC-5 | No critical defects | Zero open P0/P1 defects at deployment. |