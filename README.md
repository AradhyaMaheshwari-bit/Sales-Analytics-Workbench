# Sales Analytics Workbench

A comprehensive five-module business intelligence and data analytics desktop application built with Streamlit, pandas, Plotly, SQLite, and SciPy for the TMU BCA Internship Evaluation.

---

## 1. Application Overview & Modules

The workbench implements an end-to-end analytical workflow across five core modules:

1. **Module 1 — Data Immersion & Wrangling** (`app/pages/01_data_immersion.py`):
   - Multi-format dataset ingestion (CSV, XLSX) with encoding fallbacks and size boundaries.
   - Dataset preview with configurable row slider.
   - Automated profiling (shape, memory, null rates, duplicate rows, data type anomaly detection).
   - Non-mutating data cleaning pipeline (missing value strategies, duplicate removal, type coercion, date normalization).
   - Business rule validation and cleaned dataset export (CSV, XLSX).

2. **Module 2 — Exploratory Data Analysis & BI Dashboard** (`app/pages/02_eda_bi.py`):
   - Dynamic executive KPI cards (Total Revenue, Total Orders, Average Order Value, Total Quantity).
   - Interactive Plotly visualizations (Revenue by Category, Monthly Trend, Revenue by City, Correlation Heatmap).
   - Descriptive statistics and categorical frequency distribution tables.
   - Multi-dimensional sidebar filters.

3. **Module 3 — SQL Analysis & Engine Security** (`app/pages/03_sql_analysis.py`):
   - In-memory SQLite database lifecycle with runtime data ingestion.
   - Predefined business queries catalog addressing key analytical questions.
   - Custom SQL query editor with engine-level authorizer enforcing SELECT-only policy, single-statement restriction, and resource limits.

4. **Module 4 — Power BI Showcase** (`app/pages/04_power_bi.py`):
   - Authentic project deliverable showcase.
   - Interactive reference cards for all six DAX business measures.
   - Documentation of interactive slicers and dynamic visualizations.
   - Disclaimer banner and graceful fallback when offline dashboard assets are absent.

5. **Module 5 — Statistical Validation** (`app/pages/05_statistical_validation.py`):
   - Welch's independent two-sample t-test comparing sales across demographic cohorts.
   - Computed t-statistic, two-tailed p-value, Welch-Satterthwaite degrees of freedom, and manual 95% confidence intervals.
   - Robust guardrails for small sample sizes, missing data, and zero variance.
   - Plain-language business interpretation with sampling variation caveats.

*(Note: FR-20 Data Storytelling & Project Summary is formally deferred from this evaluation increment).*

---

## 2. Prerequisites & Environment

The workbench is locally verified on **Python 3.14.6** on Windows 11 / x86_64. No minimum Python version is formally guaranteed beyond compatibility with the pinned dependency stack:

- **Runtime Dependencies** (`requirements.txt`):
  - `streamlit==1.49.1`
  - `pandas==2.3.3`
  - `numpy==2.5.5`
  - `plotly==7.1.0`
  - `scipy==1.18.1`
  - `openpyxl==3.1.5`

- **Development & QA Tooling** (`requirements-dev.txt`):
  - `pytest==9.2.0`
  - `ruff==0.17.5`
  - `black==26.10.1`

---

## 3. Setup Instructions

Clone the repository and set up a virtual environment:

### Windows (PowerShell)
```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### macOS / Linux (POSIX Bash)
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

---

## 4. Synthetic Demo Data Generation

The application includes a deterministic synthetic dataset generator for offline evaluation and testing without authentic student or customer records:

```powershell
python scripts/generate_demo_data.py
```

- Generates 60 deterministic records adhering to the canonical 12-column schema at `data/raw/synthetic_demo_dataset.xlsx`.
- Enforces strict fail-closed path guards that refuse writes targeting or resolving to the reserved authentic dataset path (`data/raw/internship_dataset.xlsx`).
- All files in `data/raw/` are excluded from version control via `.gitignore`.

---

## 5. Running the Application

Launch the Streamlit web interface:

```powershell
streamlit run app/main.py
```

Once running, navigate to **Module 1 (Data Immersion & Wrangling)** and click **"Load Synthetic Demo Dataset"** or upload your own CSV/XLSX file.

---

## 6. Running Tests

The test suite requires setting `PYTHONPATH` to the repository root because `pyproject.toml` does not contain a pytest `pythonpath` configuration:

### Windows (PowerShell)
```powershell
$env:PYTHONPATH="."
pytest tests -q
```

### macOS / Linux (POSIX Bash)
```bash
PYTHONPATH=. pytest tests -q
```

---

## 7. Quality Gates

Run code formatting and linting checks across all codebase directories:

```powershell
ruff check app tests scripts
ruff format --check app tests scripts
black --check app tests scripts
```

All quality gates must exit with code 0.

---

## 8. Project Structure

```
Phase-II_Development/
├── app/
│   ├── main.py                     # Entry point & navigation registry
│   ├── pages/                      # Streamlit UI page modules (01 to 05)
│   ├── services/                   # Pure business logic (data loader, profiler, cleaner, eda, statistics)
│   ├── database/                   # SQLite lifecycle, authorizer, and query catalogue
│   ├── models/                     # Typed data schemas and validation models
│   ├── components/                 # Reusable UI widgets and KPI cards
│   ├── utils/                      # Plotly charts factory, formatting, styling, logging
│   └── assets/                     # Power BI metadata references and assets
├── scripts/
│   └── generate_demo_data.py       # Deterministic synthetic data generator
├── tests/
│   ├── unit/                       # Unit tests for services, models, and presentation
│   └── integration/                # End-to-end integration and cross-layer workflow tests
├── docs/                           # Architecture, SDLC requirements, design, and implementation specs
├── pyproject.toml                  # Ruff and Black tool configuration
├── requirements.txt                # Pinned runtime dependencies
├── requirements-dev.txt            # Pinned testing and linting tools
└── CHANGELOG.md                    # Keep a Changelog version history
```

---

## 9. Privacy & Dataset Separation

The authentic TMU BCA internship dataset is strictly protected:
- The path `data/raw/internship_dataset.xlsx` is reserved exclusively for the authentic local dataset.
- Synthetic generation outputs are confined to `data/raw/synthetic_demo_dataset.xlsx`.
- Both raw data files are Git-ignored (`*.xlsx`, `*.csv`) to prevent sensitive or authentic records from entering version control.
- `scripts/generate_demo_data.py` employs a fail-closed guard preventing accidental overwrites of the authentic dataset.

---

## 10. Power BI Deliverables Note

Module 4 (`app/pages/04_power_bi.py`) showcases the Power BI analytical deliverable. The complete reference specifications for DAX formulas, slicers, and dynamic charts are defined in `app/assets/power_bi/dax_measures_reference.json`. If local dashboard screenshots (`dashboard_full.png`) are not available, the application displays an authentic deliverable banner with fallback documentation.
