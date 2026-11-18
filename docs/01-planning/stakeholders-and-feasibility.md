# Stakeholders & Feasibility — Sales Analytics Workbench

**SDLC Phase:** 1 — Project Planning and Feasibility Study

---

## 1. Stakeholder Identification

| ID | Stakeholder | Role | Interest / Influence |
|---|---|---|---|
| ST-1 | Aradhya Maheshwari | Developer, BCA student | Owns the product; runs the demo. |
| ST-2 | TMU Phase-II evaluator | Academic reviewer | Judges the application against evaluation criteria. |
| ST-3 | ApexPlanet internship mentor | Industry supervisor | Validates technical authenticity of the work. |
| ST-4 | Future students | End users | Reuse the Workbench for their own demonstrations. |
| ST-5 | University lab staff | IT support | Must run the app with minimal setup. |

## 2. Feasibility Assessment

### 2.1 Technical Feasibility — **FEASIBLE**

| Aspect | Finding |
|---|---|
| Language / framework | Python 3.14.7 is installed; Streamlit 1.49.1 is available and installs cleanly. |
| Data libraries | pandas, NumPy, SciPy, openpyxl, matplotlib, Plotly all install and import without issues. |
| Database | SQLite is part of the Python standard library — zero external dependencies. |
| File formats | CSV and XLSX reading/writing supported via pandas + openpyxl. |
| Statistics | `scipy.stats.ttest_ind(equal_var=False)` implements Welch's t-test exactly as documented in the internship synopsis. |
| Risk | None identified. All required packages are stable, cross-platform, and free. |

**Decision:** The proposed stack is technically sound. A project virtual
environment (`.venv/`) isolates dependencies from the global interpreter.

### 2.2 Operational Feasibility — **FEASIBLE**

| Aspect | Finding |
|---|---|
| Environment setup | One command: `python -m venv .venv && .venv\Scripts\pip install -r requirements.txt`. |
| Startup | One command: `streamlit run app/main.py`. |
| Hardware | Any modern Windows PC; no GPU required. |
| Skills required | Python, pandas, Streamlit — all already in use during the internship. |
| Maintenance | Modular codebase; dependencies pinned in `requirements.txt`. |

### 2.3 Economic Feasibility — **FEASIBLE**

| Aspect | Finding |
|---|---|
| Licensing | All selected packages are open-source / MIT-licensed (Streamlit, pandas, NumPy, SciPy, Plotly, matplotlib, openpyxl, pytest). |
| Cloud costs | None — the app runs locally. |
| Hardware costs | None — reuses existing lab hardware. |
| Time investment | ~10–12 working days, phased across SDLC milestones. |

### 2.4 Schedule Feasibility — **FEASIBLE (with buffer)**

See `timeline-and-risks.md`. Total estimated effort is contained within the
planned SDLC schedule, with a one-week buffer for testing and fixes.

## 3. Key Assumptions

| ID | Assumption |
|---|---|
| A-1 | The reviewer has Python 3.8+ and can create a virtual environment. |
| A-2 | Uploaded datasets are CSV or XLSX with at least one numeric column. |
| A-3 | The original internship dataset remains available in `Phase-I_Evaluation/Dataset.xlsx`. |
| A-4 | The reviewer has (or can install) the listed Python packages. |
| A-5 | No internet access is required at demonstration time. |