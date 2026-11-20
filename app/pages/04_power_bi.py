"""Module 4 — Power BI Showcase (Increment 4).

Presents the Power BI Sales Performance Dashboard created as Task 4 of the
ApexPlanet internship. Includes authentic deliverable disclaimer, missing-asset
screenshot fallback handling, interactive DAX measure reference cards, and
comprehensive slicer and visualization capability documentation.

Design (SDD-PBI §1-6, SRS-SQL §2, FR-18):
- Non-dismissible authentic deliverable disclaimer banner.
- Dynamic screenshot viewer checking for `app/assets/power_bi/dashboard_full.png`.
- 2x3 grid of DAX measure cards parsed from `dax_measures_reference.json`.
- Slicers and visualizations reference tables.
"""

from __future__ import annotations

import json
from pathlib import Path

import streamlit as st

# Page configuration
st.set_page_config(page_title="Power BI Showcase", page_icon="📊")

st.header("Module 4 — Power BI Showcase")
st.divider()

# 1. Non-dismissible authentic deliverable disclaimer (SDD-PBI §2.3)
st.warning(
    "**Authentic Deliverable Notice:** This module showcases the Power BI dashboard "
    "produced as Task 4 of ApexPlanet Software Pvt. Ltd. internship. Power BI is a "
    "separate desktop application; screenshots are presented here for academic "
    "evaluation. Interactive filtering is not available in this view."
)

st.divider()

# Load DAX reference JSON
json_path = Path("app/assets/power_bi/dax_measures_reference.json")
reference_data: dict = {}
if json_path.exists():
    try:
        with open(json_path, encoding="utf-8") as f:
            reference_data = json.load(f)
    except Exception as e:
        st.error(f"Failed to load DAX measures reference JSON: {e}")

# 2. Section 1: Dashboard Screenshot Viewer
st.subheader("1. Dashboard Screenshot Viewer")
screenshot_path = Path("app/assets/power_bi/dashboard_full.png")
filter_screenshot_path = Path("app/assets/power_bi/dashboard_filter_state.png")

if screenshot_path.exists():
    st.image(
        str(screenshot_path),
        caption="Task 4 Deliverable — Sales Performance Power BI Dashboard",
        use_container_width=True,
    )
    if filter_screenshot_path.exists():
        with st.expander("View Filtered Dashboard State (Category: Electronics)"):
            st.image(
                str(filter_screenshot_path),
                caption="Filtered Dashboard View",
                use_container_width=True,
            )
else:
    st.info(
        "Dashboard screenshots not found. Please add assets to app/assets/power_bi/."
    )

st.divider()

# 3. Section 2: DAX Measure Interactive Cards (2x3 Grid)
st.subheader("2. DAX Measure Reference Cards")
st.markdown(
    "The Power BI model incorporates the following six core DAX measures created "
    "during the internship task:"
)

dax_measures = reference_data.get("dax_measures", [])
if dax_measures:
    # Render in a 2x3 grid (3 columns per row)
    for i in range(0, len(dax_measures), 3):
        cols = st.columns(3)
        for j in range(3):
            if i + j < len(dax_measures):
                measure = dax_measures[i + j]
                with cols[j]:
                    st.markdown(f"### {measure.get('measure_name', '')}")
                    st.code(measure.get("dax_formula", ""), language="dax")
                    st.markdown(f"**Return Type:** `{measure.get('return_type', '')}`")
                    st.markdown(f"**Purpose:** {measure.get('purpose', '')}")
                    st.markdown("---")

st.divider()

# 4. Section 3: Slicers & Visualizations Breakdown Table
st.subheader("3. Dashboard Capability Documentation")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### Slicers & Interactive Filters")
    slicers = reference_data.get("slicers", [])
    if slicers:
        slicer_rows = [
            {
                "Slicer Field": s.get("slicer_field"),
                "Type": s.get("slicer_type"),
                "Filters Applied To": s.get("filters_applied_to"),
            }
            for s in slicers
        ]
        st.dataframe(slicer_rows, use_container_width=True, hide_index=True)

with col2:
    st.markdown("### Dynamic Visualizations")
    visuals = reference_data.get("visualizations", [])
    if visuals:
        visual_rows = [
            {
                "#": v.get("visual_number"),
                "Visual Type": v.get("visual_type"),
                "Data Bound": v.get("data_bound"),
                "Business Insight": v.get("business_insight"),
            }
            for v in visuals
        ]
        st.dataframe(visual_rows, use_container_width=True, hide_index=True)

st.markdown("---")
st.caption(
    "**Deliverable Note:** The `.pbix` Power BI source file is excluded from Git version control "
    "via `.gitignore` due to binary file sizing constraints but is fully verified and available in the "
    "local internship deliverable archive."
)
