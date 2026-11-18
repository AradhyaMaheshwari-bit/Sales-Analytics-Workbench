# Design Traceability Matrix — Sales Analytics Workbench

**SDLC Phase:** 3 — System Design (Checkpoint B)
**Document ID:** SDD-DTM
**Version:** 1.0

---

## 1. Overview

This matrix traces every Phase 2 requirement (22 Functional + 26 Non-Functional) to its corresponding Phase 3 design document(s). It ensures complete coverage and identifies any unaddressed requirements.

---

## 2. Functional Requirements Traceability

| Req ID | Requirement Title | Design Document(s) | Design Section(s) | Status |
|---|---|---|---|---|
| FR-01 | Dataset Upload | SDD-MOD, SDD-SEC | module-design §2.3 (`data_loader.py`), security-and-reliability-design §2 | ✅ Covered |
| FR-02 | Multi-format File Parsing | SDD-MOD, SDD-SEC | module-design §2.3 (`data_loader.py`), security-and-reliability-design §2.3 | ✅ Covered |
| FR-03 | Dataset Preview | SDD-MOD, SDD-UI-UX | module-design §2.1 (`01_data_immersion.py`), ui-ux-design §5.1 | ✅ Covered |
| FR-04 | Data Profiling Summary | SDD-MOD, SDD-UI-UX | module-design §2.3 (`profiler.py`), ui-ux-design §5.1 Tab 2 | ✅ Covered |
| FR-05 | Missing Value Detection | SDD-MOD | module-design §2.3 (`profiler.py`) | ✅ Covered |
| FR-06 | Duplicate Row Detection | SDD-MOD | module-design §2.3 (`profiler.py`) | ✅ Covered |
| FR-07 | Data Type Inspection | SDD-MOD | module-design §2.3 (`profiler.py`) | ✅ Covered |
| FR-08 | Configurable Data Cleaning | SDD-MOD, SDD-DATA | module-design §2.3 (`cleaner.py`), data-architecture §3 (CleaningPipeline state) | ✅ Covered |
| FR-09 | Business Rule Validation | SDD-MOD | module-design §2.3 (`validator.py`) | ✅ Covered |
| FR-10 | Cleaned Dataset Export | SDD-MOD, SDD-UI-UX | module-design §2.3 (`report_generator.py`), ui-ux-design §5.1 Tab 4 | ✅ Covered |
| FR-11 | EDA Dashboard | SDD-MOD, SDD-UI-UX, SDD-STAT | module-design §2.3 (`eda.py`), ui-ux-design §5.2, analytics-and-statistical-design §2 | ✅ Covered |
| FR-12 | Descriptive Statistics | SDD-MOD, SDD-STAT | module-design §2.3 (`eda.py`), analytics-and-statistical-design §2.1 | ✅ Covered |
| FR-13 | Correlation Analysis | SDD-STAT | analytics-and-statistical-design §2.2 | ✅ Covered |
| FR-14 | Interactive Plotly Charts | SDD-MOD, SDD-TDD | module-design §2.6 (`charts.py`), technical-design-decisions TD-13 | ✅ Covered |
| FR-15 | SQLite Database Creation | SDD-DB-SQL, SDD-MOD | database-and-sql-design §2, §3, module-design §2.4 (`db_manager.py`) | ✅ Covered |
| FR-16 | Pre-built SQL Business Queries | SDD-DB-SQL, SDD-MOD, SDD-SEC | database-and-sql-design §4, §5, module-design §2.4 (`queries.py`), security-and-reliability-design §3 | ✅ Covered |
| FR-17 | Excel Report Export | SDD-MOD | module-design §2.3 (`report_generator.py`) | ✅ Covered |
| FR-18 | Power BI Dashboard Showcase | SDD-PBI, SDD-MOD | power-bi-showcase-design §3–§6, module-design §2.1 (`04_power_bi.py`) | ✅ Covered |
| FR-19 | Welch's T-Test | SDD-STAT, SDD-MOD | analytics-and-statistical-design §3, §4, §5, module-design §2.3 (`statistics.py`) | ✅ Covered |
| FR-20 | Data Storytelling & Summary | SDD-MOD, SDD-UI-UX | module-design §2.1 (`05_statistical_validation.py`), ui-ux-design §5.5 | ✅ Covered |
| FR-CC-01 | Internship Dataset Mode | SDD-MOD, SDD-TDD, SDD-DATA | module-design §2.3 (`data_loader.py`), technical-design-decisions TD-09, data-architecture §3 | ✅ Covered |
| FR-CC-02 | Flexible Column Mapping | SDD-DATA, SDD-MOD | data-architecture §6, module-design §2.5 (`dataset_schema.py`) | ✅ Covered |

**Coverage: 22/22 Functional Requirements — 100%**

---

## 3. Non-Functional Requirements Traceability

| Req ID | Requirement Title | Design Document(s) | Design Section(s) | Status |
|---|---|---|---|---|
| NFR-U-01 | Intuitive Navigation | SDD-UI-UX, SDD-ARCH | ui-ux-design §4, system-architecture §2 | ✅ Covered |
| NFR-U-02 | Consistent UI Theme | SDD-UI-UX, SDD-TDD | ui-ux-design §2, §3, technical-design-decisions TD-12, TD-13 | ✅ Covered |
| NFR-U-03 | User Feedback | SDD-UI-UX, SDD-SEC | ui-ux-design §6, security-and-reliability-design §6.2 | ✅ Covered |
| NFR-U-04 | Responsive Layout | SDD-UI-UX | ui-ux-design §5 (layout specs with viewport awareness) | ✅ Covered |
| NFR-P-01 | Upload Performance | SDD-SEC | security-and-reliability-design §2.2 (50MB limit design) | ✅ Covered |
| NFR-P-02 | Chart Rendering | SDD-TDD | technical-design-decisions TD-13 (centralized Plotly factory) | ✅ Covered |
| NFR-P-03 | Statistical Computation | SDD-STAT | analytics-and-statistical-design §3.2 (Welch's computation design) | ✅ Covered |
| NFR-R-01 | Error Handling | SDD-SEC | security-and-reliability-design §6 | ✅ Covered |
| NFR-R-02 | Data Integrity | SDD-DATA, SDD-TDD | data-architecture §2, §4, technical-design-decisions TD-07 | ✅ Covered |
| NFR-R-03 | Deterministic Results | SDD-STAT | analytics-and-statistical-design §4.2 (tolerance bands) | ✅ Covered |
| NFR-M-01 | Modular Code Structure | SDD-MOD, SDD-ARCH | module-design §2, system-architecture §2 | ✅ Covered |
| NFR-M-02 | Code Documentation | SDD-SEC | security-and-reliability-design §7 (logging + docstring policy) | ✅ Covered |
| NFR-M-03 | PEP 8 Compliance | — | Implementation-phase enforcement (linter config in Phase 4) | 🟡 Phase 4 |
| NFR-S-01 | No Hardcoded Secrets | SDD-SEC | security-and-reliability-design §4.3 (`.gitignore` policy) | ✅ Covered |
| NFR-S-02 | Input Validation / SQL Security | SDD-DB-SQL, SDD-SEC, SDD-TDD | database-and-sql-design §4, security-and-reliability-design §3, technical-design-decisions TD-05, TD-06 | ✅ Covered |
| NFR-S-03 | Safe File Handling | SDD-SEC | security-and-reliability-design §2.3 | ✅ Covered |
| NFR-D-01 | Reproducibility | SDD-STAT, SDD-TDD | analytics-and-statistical-design §4, technical-design-decisions TD-11 | ✅ Covered |
| NFR-D-02 | Historical Result Validation | SDD-STAT | analytics-and-statistical-design §4.2 (benchmark values + tolerance) | ✅ Covered |
| NFR-SC-01 | Dataset Size Limits | SDD-SEC | security-and-reliability-design §2.2 (50MB), §6.3 (graceful degradation) | ✅ Covered |
| NFR-SC-02 | Concurrent Users | SDD-DB-SQL, SDD-TDD | database-and-sql-design §2.1, technical-design-decisions TD-04 | ✅ Covered |
| NFR-C-01 | Python Version | SDD-TDD | technical-design-decisions §2 (stack decisions) | ✅ Covered |
| NFR-C-02 | Operating System | SDD-TDD | technical-design-decisions §2 (Windows primary) | ✅ Covered |
| NFR-C-03 | Browser Compatibility | SDD-UI-UX | ui-ux-design §5 (Streamlit renders in Chrome/Edge/Firefox) | ✅ Covered |
| NFR-DP-01 | Installation Simplicity | SDD-SEC | security-and-reliability-design §4.1 (no disk persistence) | ✅ Covered |
| NFR-DP-02 | No External Services | SDD-TDD, SDD-DB-SQL | technical-design-decisions TD-03, database-and-sql-design §2 | ✅ Covered |
| NFR-DP-03 | Startup Time | SDD-MOD | module-design §2.1 (`main.py` entry point, lazy import design) | ✅ Covered |

**Coverage: 25/26 Non-Functional Requirements designed — 96%**
**1 NFR deferred to Phase 4:** NFR-M-03 (PEP 8 Compliance) — enforced at implementation time via linter configuration, not a design-phase artifact.

---

## 4. Design Decision Traceability

| Decision ID | Decision Title | Originating Requirement(s) | Design Document |
|---|---|---|---|
| D-1 | Synthetic data generator strategy | FR-CC-01 | SDD-TDD (TD-09) |
| D-2 | Lowercase `sales` table name | FR-15, FR-16 | SDD-DB-SQL §5 |
| D-3 | SELECT-only SQL security | NFR-S-02, FR-15, FR-16 | SDD-DB-SQL §4, SDD-SEC §3, SDD-TDD (TD-05, TD-06) |

---

## 5. Design Document Cross-Reference Index

| Document ID | Document Title | File Path |
|---|---|---|
| SDD-ARCH | System Architecture | `docs/03-design/system-architecture.md` |
| SDD-MOD | Module Design | `docs/03-design/module-design.md` |
| SDD-DATA | Data Architecture & Data Flow | `docs/03-design/data-architecture.md` |
| SDD-DB-SQL | Database and SQL Architecture | `docs/03-design/database-and-sql-design.md` |
| SDD-UI-UX | UI/UX & Interaction Design | `docs/03-design/ui-ux-design.md` |
| SDD-STAT | Analytics and Statistical Design | `docs/03-design/analytics-and-statistical-design.md` |
| SDD-PBI | Power BI Showcase Design | `docs/03-design/power-bi-showcase-design.md` |
| SDD-SEC | Security and Reliability Design | `docs/03-design/security-and-reliability-design.md` |
| SDD-TDD | Technical Design Decisions | `docs/03-design/technical-design-decisions.md` |
| SDD-DTM | Design Traceability Matrix | `docs/03-design/design-traceability-matrix.md` |

---

## 6. Summary

| Category | Total | Covered in Design | Deferred to Implementation | Uncovered |
|---|---|---|---|---|
| Functional Requirements | 22 | 22 (100%) | 0 | 0 |
| Non-Functional Requirements | 26 | 25 (96%) | 1 (NFR-M-03) | 0 |
| Approved Decisions (D-1, D-2, D-3) | 3 | 3 (100%) | 0 | 0 |
| **Total** | **51** | **50 (98%)** | **1 (2%)** | **0** |
