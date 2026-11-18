# Power BI Showcase Design — Sales Analytics Workbench

**SDLC Phase:** 3 — System Design (Checkpoint B)
**Document ID:** SDD-PBI
**Version:** 1.0

---

## 1. Overview

Module 4 (`app/pages/04_power_bi.py`) presents the Power BI Sales Performance Dashboard created as Task 4 of the ApexPlanet internship. Power BI is a separate desktop-produced deliverable; this module showcases it within the Streamlit workbench using static screenshot assets and structured documentation of the DAX measures, slicers, and visualizations.

---

## 2. Asset Strategy & Design Constraints

### 2.1 Asset Location
- **Canonical Asset Directory:** `app/assets/power_bi/`
- **Included Assets:**
  - `dashboard_full.png` — Full dashboard screenshot (high resolution, minimum 1920×1080).
  - `dashboard_filter_state.png` — Screenshot showing slicers active on a filtered view (e.g., "Electronics" category only).
  - `dax_measures_reference.json` — Machine-readable record of all DAX measures (name, formula, return type, business purpose).

### 2.2 Asset Git Policy
- Power BI `.pbix` file is excluded from Git via `.gitignore` (`*.pbix`).
- Dashboard screenshots (PNG) are **included** in Git as they are small static deliverable evidence (< 5MB each).
- `dax_measures_reference.json` is included as structured documentation.

### 2.3 Authentic Deliverable Disclaimer
The top banner of Module 4 must display a prominent, non-dismissible callout:

> *"This module showcases the Power BI dashboard produced as Task 4 of ApexPlanet Software Pvt. Ltd. internship. Power BI is a separate desktop application; screenshots are presented here for academic evaluation. Interactive filtering is not available in this view."*

---

## 3. Six DAX Measures

The following six DAX measures were created in the internship Power BI project. Each is documented here for implementation reference in `dax_measures_reference.json` and the interactive measure cards in Module 4.

| # | Measure Name | DAX Formula | Return Type | Business Purpose |
|---|---|---|---|---|
| 1 | **Total Revenue** | `Total Revenue = SUM(Sales[Total_Sales])` | Currency (₹) | Aggregate revenue across all transactions. |
| 2 | **Average Order Value** | `AOV = DIVIDE(SUM(Sales[Total_Sales]), COUNTROWS(Sales))` | Currency (₹) | Revenue per transaction; key retail performance KPI. |
| 3 | **Total Orders** | `Total Orders = COUNTROWS(Sales)` | Integer | Count of all transaction records. |
| 4 | **Total Quantity Sold** | `Total Quantity = SUM(Sales[Quantity])` | Integer | Units moved across all products. |
| 5 | **Revenue by Gender %** | `Gender % = DIVIDE(SUM(Sales[Total_Sales]), CALCULATE(SUM(Sales[Total_Sales]), ALL(Sales[Gender])), 0)` | Percentage | Gender's contribution as a share of total revenue. |
| 6 | **Top Category Revenue** | `Top Category = CALCULATE(SUM(Sales[Total_Sales]), TOPN(1, ALL(Sales[Category]), SUM(Sales[Total_Sales])))` | Currency (₹) | Revenue from the single highest-performing product category. |

---

## 4. Slicers & Interactive Filters (Dashboard Capability Documentation)

The Power BI dashboard was designed with four slicers enabling cross-visual filtering:

| # | Slicer Field | Slicer Type | Filters Applied To |
|---|---|---|---|
| 1 | `Category` | Multi-select dropdown | Revenue by product visual, monthly trend, top products table |
| 2 | `Gender` | Radio button tile | Gender revenue split donut chart, revenue scatter, KPI cards |
| 3 | `City` | Multi-select list | City revenue map, product table |
| 4 | `Order_Date` | Date range filter (between) | Monthly revenue trend line, all aggregates |

---

## 5. Six Dynamic Visualizations (Dashboard Capability Documentation)

| # | Visual Type | Data Bound | Business Insight |
|---|---|---|---|
| 1 | **KPI Cards (×4)** | Total Revenue, AOV, Total Orders, Total Quantity | High-level executive summary at a glance |
| 2 | **Clustered Bar Chart** | Revenue by Category | Compares category performance horizontally |
| 3 | **Line Chart** | Monthly Revenue Trend (Order_Date → Month) | Reveals seasonality and growth patterns |
| 4 | **Donut Chart** | Revenue Split by Gender | Male vs. Female revenue proportion (consistent with FR-19 analysis) |
| 5 | **Map Visual** | Revenue by City | Spatial distribution of customer spend |
| 6 | **Top 10 Products Table** | Product → Revenue (sorted descending) | Identifies highest-revenue individual products |

---

## 6. Module 4 UI Layout Specification

```
┌──────────────────────────────────────────────────────────────────────────────┐
│  MODULE 4: POWER BI SALES DASHBOARD SHOWCASE                                 │
│  [ Authentic Deliverable Disclaimer Banner — Non-dismissible ]               │
├──────────────────────────────────────────────────────────────────────────────┤
│  SECTION 1: Dashboard Screenshot Viewer                                      │
│  ┌────────────────────────────────────────────────────────────────────────┐  │
│  │  [ dashboard_full.png — Full-width high-res screenshot ]               │  │
│  │  Caption: "Task 4 Deliverable — Sales Performance Power BI Dashboard"  │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
│  [ Expander: View Filtered Dashboard State → dashboard_filter_state.png ]    │
├──────────────────────────────────────────────────────────────────────────────┤
│  SECTION 2: DAX Measure Interactive Cards (2×3 grid)                         │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐                             │
│  │ Total Rev  │  │    AOV     │  │Tot. Orders │                             │
│  │ DAX card   │  │ DAX card   │  │ DAX card   │                             │
│  └────────────┘  └────────────┘  └────────────┘                             │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐                             │
│  │ Tot. Qty   │  │ Gender %   │  │ Top Cat.   │                             │
│  │ DAX card   │  │ DAX card   │  │ DAX card   │                             │
│  └────────────┘  └────────────┘  └────────────┘                             │
│  Each card: Measure Name → Formula (code block) → Return Type → Purpose     │
├──────────────────────────────────────────────────────────────────────────────┤
│  SECTION 3: Slicers & Visuals Breakdown Table                                │
│  [ 4-row Slicer table | 6-row Visuals table ]                               │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 7. Requirement Traceability

| Requirement | Covered By |
|---|---|
| FR-18: Power BI DAX showcase | Sections 3, 5, 6 |
| NFR-M-01: Internship work authenticity | Section 2 (authentic deliverable disclaimer) |
| NFR-U-02: Dark executive theme | Dark navy card styling for DAX measure cards |
