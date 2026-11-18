# Technology Justification — Sales Analytics Workbench

**SDLC Phase:** 1 — Project Planning and Feasibility Study

---

## 1. Selection Criteria

| Criterion | Weight |
|---|---|
| Cross-platform (Windows/macOS/Linux) | Must |
| Open-source / zero licensing cost | Must |
| Active maintenance & community | High |
| Python 3.14 compatibility | Must |
| Low external dependencies | High |
| Demonstrates analytics engineering skills | High |

---

## 2. Language & Runtime

| Choice | Justification |
|---|---|
| **Python 3.14.7** | Already installed on the developer machine; all target libraries support it. If a future incompatibility arises, the virtual environment can be recreated with Python 3.12 (documented in Phase 6). |
| **Virtual environment (`.venv/`)** | Isolates project dependencies from global Python; required by SDLC policy. |

---

## 3. Core Libraries

| Library | Version | Role | Why this version |
|---|---|---|---|
| **Streamlit** | 1.49.1 | Web UI framework | Stable, production-ready; supports modern Plotly / pandas integration. |
| **pandas** | 2.3.3 | DataFrames, I/O, wrangling | Industry standard; handles CSV/XLSX/SQLite natively. |
| **NumPy** | 2.5.5 | Numeric arrays | pandas/SciPy transitive dependency; already compatible. |
| **Plotly** | 7.1.0 | Interactive charts | Interactive hover, zoom, download; dark theme support; web-native. |
| **Matplotlib** | 3.11.2 | Static charts / export | Used for any non-interactive figures or PNG export. |
| **SciPy** | 1.18.1 | Statistics | `scipy.stats.ttest_ind(equal_var=False)` implements Welch's t-test exactly as internship. |
| **openpyxl** | 3.1.5 | Excel I/O | Required by pandas for `.xlsx` read/write. |
| **SQLite** | stdlib | Embedded DB | Zero-config, file-based, part of Python standard library. |
| **pytest** | 9.2.0 | Test framework | Industry standard; fixtures, parametrization, coverage. |

---

## 4. Rejected / Deferred Alternatives

| Alternative | Reason for rejection |
|---|---|
| Dash (by Plotly) | Larger footprint, more boilerplate; Streamlit is faster for data-centric apps. |
| Flask / FastAPI + React | Over-engineered; requires separate frontend build; not needed for single-user demo. |
| Jupyter Notebook | Not a deployable application; poor for interactive stakeholder demo. |
| PostgreSQL / MySQL | External service dependency; violates "no external services" requirement. |
| Power BI Python SDK | Requires paid license / Azure; not available in university labs. |
| Tableau | Paid license; not available. |
| Python 3.12 venv (mandatory) | Unnecessary — 3.14.7 works; documented as fallback only. |

---

## 5. Development & Quality Tools

| Tool | Role |
|---|---|
| **Git / GitHub** | Version control; portfolio visibility. |
| **VS Code** | IDE with Python, Streamlit extensions. |
| **Markdown** | Documentation format (docs/, README). |
| **Conventional Commits** | Structured history; automated changelog potential. |
| **requirements.txt** | Reproducible dependency installation. |

---

## 6. Compatibility Note

All selected libraries are **MIT / BSD / Apache-2.0 licensed**, run on Windows 11,
and have wheel packages available on PyPI — no compilation step required.