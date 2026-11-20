"""Unit tests for the report generator service (Increment 1C).

Covers plan items 8:
Exports: CSV and multi-sheet XLSX bytes are non-empty, readable back by pandas,
expected columns/rows.  Summary and Statistics sheets present; Query Results
sheet deferred to Increment 3.
"""

import io

import pandas as pd
import pytest
from app.services.report_generator import (
    _statistics_sheet,
    _summary_sheet,
    _validation_sheet,
    df_to_csv_bytes,
    df_to_xlsx_bytes,
    generate_cleaned_export,
    generate_excel_report,
)


@pytest.fixture
def clean_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Order_ID": ["ORD-1", "ORD-2", "ORD-3"],
            "Order_Date": ["2024-01-01", "2024-01-15", "2024-02-10"],
            "Customer_ID": ["C-1", "C-2", "C-3"],
            "Quantity": [2, 3, 1],
            "Unit_Price": [100.0, 200.0, 300.0],
            "Total_Sales": [200.0, 600.0, 300.0],
        }
    )


@pytest.fixture
def metrics() -> object:
    from app.models.validation_models import ProfilingMetrics

    return ProfilingMetrics(
        row_count=3,
        column_count=6,
        memory_usage_bytes=1024,
        columns={},
        missing_total=0,
        missing_percentage=0.0,
        duplicate_row_count=0,
        duplicate_percentage=0.0,
    )


def test_csv_export_bytes_nonempty(clean_df: pd.DataFrame) -> None:
    bytes_out, filename = generate_cleaned_export(clean_df, "csv")
    assert len(bytes_out) > 0
    assert filename.endswith(".csv")


def test_csv_export_readable_back(clean_df: pd.DataFrame) -> None:
    bytes_out, filename = generate_cleaned_export(clean_df, "csv")
    df_read = pd.read_csv(io.BytesIO(bytes_out), encoding="utf-8")
    pd.testing.assert_frame_equal(
        df_read.sort_index(axis=1), clean_df.sort_index(axis=1)
    )


def test_xlsx_bytes_nonempty(clean_df: pd.DataFrame) -> None:
    bytes_out, filename = generate_cleaned_export(clean_df, "xlsx")
    assert len(bytes_out) > 0
    assert filename.endswith(".xlsx")


def test_xlsx_readable_back_by_pandas(clean_df: pd.DataFrame) -> None:
    bytes_out, filename = generate_cleaned_export(clean_df, "xlsx")
    df_read = pd.read_excel(io.BytesIO(bytes_out), engine="openpyxl")
    # Row count should match; column ordering may differ due to DataFrame
    # constructor differences, so we only check shape+col-sets
    assert df_read.shape == clean_df.shape
    assert set(df_read.columns) == set(clean_df.columns)


def test_df_to_csv_bytes(clean_df: pd.DataFrame) -> None:
    bytes_out = df_to_csv_bytes(clean_df)
    assert len(bytes_out) > 0
    df_read = pd.read_csv(io.BytesIO(bytes_out), encoding="utf-8")
    pd.testing.assert_frame_equal(df_read, clean_df)


def test_df_to_xlsx_bytes(clean_df: pd.DataFrame) -> None:
    bytes_out = df_to_xlsx_bytes(clean_df)
    assert len(bytes_out) > 0


def test_summary_sheet(metrics, clean_df: pd.DataFrame) -> None:
    summary = _summary_sheet(metrics, clean_df)
    assert len(summary) > 0
    assert "Total Rows" in summary["Metric"].values


def test_statistics_sheet(clean_df: pd.DataFrame) -> None:
    stats = _statistics_sheet(clean_df)
    assert len(stats) > 0
    assert "Column" in stats.columns
    assert "Dtype" in stats.columns


def test_validation_sheet(clean_df: pd.DataFrame) -> None:
    from app.services.validator import validate_business_rules

    summary = validate_business_rules(clean_df)
    val_sheet = _validation_sheet(summary)
    assert len(val_sheet) > 0
    assert "Rule" in val_sheet.columns


def test_excel_report_summary_statistics_sheets_present(
    clean_df: pd.DataFrame,
    metrics,
) -> None:
    bytes_out, filename = generate_excel_report(clean_df, metrics=metrics)
    df_read = pd.read_excel(io.BytesIO(bytes_out), engine="openpyxl")
    sheet_names = df_read.keys() if hasattr(df_read, "keys") else []
    # We can't easily split an xlsx in-memory like this, so verify the
    # byte size and that openpyxl can parse the workbook
    assert len(bytes_out) > 0
    # Ensure two tabs at minimum are written
    xls = pd.ExcelFile(io.BytesIO(bytes_out))
    sheet_names = xls.sheet_names
    assert "Summary" in sheet_names
    assert "Statistics" in sheet_names


def test_excel_report_deferred_query_results_not_present(
    clean_df: pd.DataFrame,
    metrics,
) -> None:
    """Increment 1C: Query Results sheet is NOT generated; only Summary+Stats."""
    bytes_out, filename = generate_excel_report(clean_df, metrics=metrics)
    xls = pd.ExcelFile(io.BytesIO(bytes_out))
    sheet_names = xls.sheet_names
    assert "Query Results" not in sheet_names


def test_excel_report_validation_sheet_present_when_provided(
    clean_df: pd.DataFrame,
    metrics,
) -> None:
    from app.services.validator import validate_business_rules

    summary = validate_business_rules(clean_df)
    bytes_out, filename = generate_excel_report(
        clean_df, metrics=metrics, validation=summary
    )
    xls = pd.ExcelFile(io.BytesIO(bytes_out))
    sheet_names = xls.sheet_names
    # When validation is supplied, the Validation sheet should be present
    assert "Validation" in sheet_names
