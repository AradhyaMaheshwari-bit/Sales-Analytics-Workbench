"""Unit tests for Power BI showcase and DAX reference data (Increment 4)."""

from __future__ import annotations

import json
import logging
from pathlib import Path

import pytest

try:
    from streamlit.testing.v1 import AppTest
except ImportError:
    AppTest = None

PROJECT_ROOT = Path(__file__).resolve().parents[2]
APP_ROOT = PROJECT_ROOT / "app"
PAGE_SCRIPT = APP_ROOT / "pages" / "04_power_bi.py"


def test_dax_reference_json_exists_and_parses():
    """Verify dax_measures_reference.json exists and is valid JSON."""
    json_path = Path("app/assets/power_bi/dax_measures_reference.json")
    assert json_path.exists(), "dax_measures_reference.json must exist"

    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)

    assert isinstance(data, dict)
    assert "dax_measures" in data
    assert "slicers" in data
    assert "visualizations" in data


def test_dax_measures_count_and_contents():
    """Verify exactly six approved DAX measures are present with correct formulas."""
    json_path = Path("app/assets/power_bi/dax_measures_reference.json")
    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)

    measures = data["dax_measures"]
    assert len(measures) == 6, f"Expected 6 DAX measures, got {len(measures)}"

    expected_names = {
        "Total Revenue",
        "Average Order Value",
        "Total Orders",
        "Total Quantity Sold",
        "Revenue by Gender %",
        "Top Category Revenue",
    }
    found_names = {m["measure_name"] for m in measures}
    assert found_names == expected_names

    # Verify specific formula for Total Revenue
    total_rev = next(m for m in measures if m["measure_name"] == "Total Revenue")
    assert "SUM(Sales[Total_Sales])" in total_rev["dax_formula"]
    assert total_rev["return_type"] == "Currency (₹)"


def test_slicers_count_and_contents():
    """Verify exactly four approved slicers are present."""
    json_path = Path("app/assets/power_bi/dax_measures_reference.json")
    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)

    slicers = data["slicers"]
    assert len(slicers) == 4, f"Expected 4 slicers, got {len(slicers)}"

    expected_fields = {"Category", "Gender", "City", "Order_Date / Month"}
    found_fields = {s["slicer_field"] for s in slicers}
    assert found_fields == expected_fields


def test_visualizations_count_and_contents():
    """Verify exactly six approved visualizations are present."""
    json_path = Path("app/assets/power_bi/dax_measures_reference.json")
    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)

    visuals = data["visualizations"]
    assert len(visuals) == 6, f"Expected 6 visualizations, got {len(visuals)}"

    # Check first visual is KPI Cards
    assert "KPI Cards" in visuals[0]["visual_type"]


@pytest.mark.skipif(AppTest is None, reason="streamlit.testing not available")
def test_power_bi_page_renders_disclaimer_and_missing_asset_message():
    """Verify the Power BI page displays disclaimer and missing-asset message."""
    logging.getLogger("streamlit").setLevel(logging.ERROR)
    page = AppTest.from_file(str(PAGE_SCRIPT))
    page.run(timeout=10)
    assert not page.exception, f"Page raised exception: {page.exception}"

    # Check disclaimer callout exists
    assert page.warning, "Expected warning element for authentic deliverable disclaimer"
    disclaimer_found = any(
        "Authentic Deliverable Notice" in w.value or "ApexPlanet" in w.value
        for w in page.warning
    )
    assert disclaimer_found, "Authentic deliverable disclaimer not found"

    # Check missing screenshot info banner
    assert page.info, "Expected info element for missing screenshots"
    missing_msg = any(
        "Dashboard screenshots not found. Please add assets to app/assets/power_bi/."
        in i.value
        for i in page.info
    )
    assert missing_msg, "Missing screenshot informational message not found"


@pytest.mark.skipif(AppTest is None, reason="streamlit.testing not available")
def test_power_bi_page_renders_dax_and_tables_without_images():
    """Verify DAX measures and capability tables render even when images are absent."""
    logging.getLogger("streamlit").setLevel(logging.ERROR)
    page = AppTest.from_file(str(PAGE_SCRIPT))
    page.run(timeout=10)
    assert not page.exception

    # Confirm no st.image was rendered when screenshot is missing
    assert not page.get("imgs"), "No image should be rendered when screenshot is absent"

    # Confirm subheaders exist for sections
    subheaders = [s.value for s in page.subheader]
    assert any("DAX Measure Reference Cards" in s for s in subheaders)
    assert any("Dashboard Capability Documentation" in s for s in subheaders)
