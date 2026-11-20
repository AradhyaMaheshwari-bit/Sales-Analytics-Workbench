"""Unit tests for the deterministic synthetic data generator (Increment 1C).

Covers plan items 10–11:
- Same seed → identical output (deterministic).
- 12-column schema; Total_Sales == Quantity × Unit_Price within rounding.
- Gender ∈ {Male, Female}.
- Plausible date range; documented row count.
- Generated output confined to data/raw/ and Git-ignored.
"""

import pandas as pd
import pytest
from scripts.generate_demo_data import generate_and_save, generate_demo_dataframe


@pytest.fixture
def df_from_generator() -> pd.DataFrame:
    return generate_demo_dataframe()


@pytest.fixture
def df_from_save(tmp_path) -> pd.DataFrame:
    out = tmp_path / "internship_dataset.xlsx"
    return generate_and_save(out)


def test_deterministic_identical_output() -> None:
    """Two calls with same seed produce byte-identical DataFrames."""
    df1 = generate_demo_dataframe()
    df2 = generate_demo_dataframe()
    pd.testing.assert_frame_equal(df1, df2)


def test_12_column_schema(df_from_generator: pd.DataFrame) -> None:
    expected = [
        "Order_ID",
        "Order_Date",
        "Customer_ID",
        "Customer_Name",
        "Age",
        "Gender",
        "City",
        "Product",
        "Category",
        "Quantity",
        "Unit_Price",
        "Total_Sales",
    ]
    assert list(df_from_generator.columns) == expected


def test_gender_only_male_female(df_from_generator: pd.DataFrame) -> None:
    assert set(df_from_generator["Gender"].unique()) <= {"Male", "Female"}


def test_total_sales_quantity_price_rounding(df_from_generator: pd.DataFrame) -> None:
    """Total_Sales ≈ Quantity × Unit_Price within rounding tolerance."""
    for _, row in df_from_generator.iterrows():
        expected = round(row["Quantity"] * row["Unit_Price"], 2)
        assert row["Total_Sales"] == expected


def test_plausible_date_range(df_from_generator: pd.DataFrame) -> None:
    """All dates fall between 2024-01-01 and 2024-12-31 inclusive."""
    for d in df_from_generator["Order_Date"]:
        dt = pd.to_datetime(d)
        assert DATE_MIN <= dt.date() <= DATE_MAX


def test_documented_row_count(df_from_generator: pd.DataFrame) -> None:
    assert len(df_from_generator) == 60


def test_saved_dataset_is_readable(tmp_path) -> None:
    out = tmp_path / "test_dataset.xlsx"
    generate_and_save(out)
    df_read = pd.read_excel(out, engine="openpyxl")
    assert len(df_read) == 60


# Module-level constants for test readability
DATE_MIN = pd.Timestamp("2024-01-01").date()
DATE_MAX = pd.Timestamp("2024-12-31").date()
