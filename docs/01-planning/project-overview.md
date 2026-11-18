# Project Overview — Sales Analytics Workbench

**SDLC Phase:** 1 — Project Planning and Feasibility Study
**Author:** Aradhya Maheshwari (BCA – Data Analytics & AI, 5th Semester)
**Institution:** Teerthanker Mahaveer University (TMU)
**Internship Provider:** ApexPlanet Software Pvt. Ltd.
**Duration:** 60 Days (5 internship modules)

---

## 1. Project Title

**Sales Analytics Workbench**

## 2. Project Type

End-to-End Data Analytics Application (unified Python + Streamlit web application).

## 3. Purpose

The application consolidates and demonstrates the complete analytical work
completed during the 60-day Data Analytics Internship at ApexPlanet Software
Pvt. Ltd. It serves as the **working project demonstration** for the university's
**Phase-II internship evaluation**.

Rather than re-presenting static reports, the Workbench lets a reviewer
**interactively run the entire analytics pipeline** on a dataset: upload a file
(or use the original internship dataset), profile it, clean it, run EDA, execute
SQL business queries, view the Power BI dashboard, run a Welch's t-test, and
read the final data-storytelling narrative — all inside one professional
dark-navy interface.

## 4. Background / Problem Statement

During the internship, five separate tasks were completed across five different
GitHub repositories, each producing its own deliverables (Excel dashboard, Power
BI `.pbix`, statistical report, 9-slide presentation, SQLite queries). For the
Phase-II evaluation, the reviewer needs a **single, integrated, runnable
application** that:

1. Demonstrates the **complete SDLC** of a real analytics product.
2. Lets the reviewer **verify results live** instead of trusting static numbers.
3. Reuses existing internship work where technically appropriate (datasets,
   DAX measures, SQL queries, statistical methodology), with proper attribution.
4. Runs reliably in a standard university lab environment (Windows, Python 3.14,
   no external services, no paid licenses).

The problem: the existing deliverables are **static artifacts** — a reviewer
cannot change the dataset, cannot re-run the statistics, and cannot inspect the
pipeline step by step. The Sales Analytics Workbench solves this by turning the
internship outputs into an **interactive, reproducible application**.

## 5. Existing Work to Reuse (Reference Repositories)

| Task | Repository | Deliverable reused |
|---|---|---|
| 1 — Data Immersion & Wrangling | `Data-Immersion-Wrangling` | Cleaning methodology, feature-engineering rules |
| 2 — EDA & BI | `Sales-Performance-Dashboard-Data-Analytics-Project` | 7 SQL business queries, Excel dashboard logic |
| 3 — Power BI Dashboard | `PowerBI-Sales-Analytics-Dashboard` | 6 DAX measures, 4 slicers, 6 visuals |
| 4 — Statistical Validation | `Sales-Analytics-Statistical-Validation` | Welch's t-test implementation, CI methodology |
| 5 — Capstone | `AradhyaMaheshwari-Data-Analytics-Portfolio` | Portfolio structure, README attribution model |

These repositories are treated as **read-only references**. They are not
modified, cloned into the working tree, or pushed to. Only documented
methodology and query logic are ported into the new application, with
attribution preserved.

## 6. Target User

- **Primary:** TMU Phase-II internship evaluator (technical reviewer).
- **Secondary:** Future students preparing their own internship demonstrations.

## 7. Definition of Success

- Application starts with `streamlit run app/main.py` in a clean environment.
- All five internship modules are accessible from a single sidebar.
- Statistical results are **recomputed live** on uploaded data — never hardcoded.
- Internship-mode reproduces the documented historical results.
- Test suite passes; no critical defects at deployment.