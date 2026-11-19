"""Unit tests for canonical schema mapping and validation (Increment 1B)."""

import pandas as pd
from app.models.dataset_schema import (
    CANONICAL_COLUMNS,
    apply_column_mapping,
    map_columns,
    validate_dataframe_schema,
)


def test_exact_schema_matching() -> None:
    """Exact canonical column names map 1:1 with zero unmapped columns."""
    df = pd.DataFrame(columns=CANONICAL_COLUMNS)
    report = validate_dataframe_schema(df)
    assert not report.missing_canonical
    assert not report.unmapped_columns
    assert report.viable_for_analysis


def test_synonym_and_case_mapping() -> None:
    """Column names with different casing, spacing, or synonyms map correctly."""
    raw_cols = [
        "order id",
        "TRANSACTION DATE",
        "cust_id",
        "Client Name",
        "Age",
        "SEX",
        "Location",
        "item",
        "category",
        "qty",
        "unitprice",
        "revenue",
        "unknown_custom_col",
    ]
    report = map_columns(raw_cols)

    assert report.mapped_columns["order id"] == "Order_ID"
    assert report.mapped_columns["TRANSACTION DATE"] == "Order_Date"
    assert report.mapped_columns["cust_id"] == "Customer_ID"
    assert report.mapped_columns["Client Name"] == "Customer_Name"
    assert report.mapped_columns["SEX"] == "Gender"
    assert report.mapped_columns["Location"] == "City"
    assert report.mapped_columns["item"] == "Product"
    assert report.mapped_columns["qty"] == "Quantity"
    assert report.mapped_columns["unitprice"] == "Unit_Price"
    assert report.mapped_columns["revenue"] == "Total_Sales"

    assert "unknown_custom_col" in report.unmapped_columns
    assert report.viable_for_analysis


def test_apply_column_mapping_non_mutating() -> None:
    """Applying column mapping produces a new renamed DataFrame without mutating original."""
    df = pd.DataFrame({"revenue": [100.0, 200.0], "date": ["2026-01-01", "2026-01-02"]})
    orig_cols = list(df.columns)
    mapping = {"revenue": "Total_Sales", "date": "Order_Date"}

    mapped_df = apply_column_mapping(df, mapping)
    assert list(df.columns) == orig_cols
    assert list(mapped_df.columns) == ["Total_Sales", "Order_Date"]
