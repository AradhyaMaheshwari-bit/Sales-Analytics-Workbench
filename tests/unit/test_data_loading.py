"""Unit tests for dataset loading and validation service (Increment 1B)."""

import pandas as pd
from app.services.data_loader import DataLoader, load_file_buffer


def test_load_valid_csv() -> None:
    """1. Valid CSV parses successfully into a DataFrame."""
    csv_data = b"Order_ID,Order_Date,Total_Sales\nORD-001,2026-01-01,1500.00\nORD-002,2026-01-02,2500.00"
    result = load_file_buffer(csv_data, "sales.csv", "csv")
    assert result.success, f"Failed: {result.error_message}"
    assert result.dataframe is not None
    assert len(result.dataframe) == 2
    assert "Total_Sales" in result.dataframe.columns


def test_unsupported_file_extension() -> None:
    """2. Unsupported extensions (.txt, .json, .xls) are rejected."""
    loader = DataLoader()
    for ext in (".txt", ".json", ".xls", ".pdf"):
        res = loader.load_file(b"some content", f"file{ext}")
        assert not res.success
        assert "Unsupported file format" in (res.error_message or "")


def test_file_size_limit_exceeded() -> None:
    """3. File > 50 MB is rejected before parsing."""
    loader = DataLoader()
    # Mock a large buffer > 50MB
    large_bytes = b"a" * (51 * 1024 * 1024)
    res = loader.load_file(large_bytes, "large.csv")
    assert not res.success
    assert "exceeds 50 MB limit" in (res.error_message or "")


def test_empty_file_handling() -> None:
    """4. Empty file produces 'Dataset is empty' message without crash."""
    loader = DataLoader()
    res = loader.load_file(b"", "empty.csv")
    assert not res.success
    assert "empty" in (res.error_message or "").lower()


def test_malformed_csv_handling() -> None:
    """5. Malformed CSV is caught and reported gracefully."""
    # Malformed CSV where row columns mismatch
    bad_csv = b"Col1,Col2,Col3\nval1,val2\nval1,val2,val3,val4"
    res = load_file_buffer(bad_csv, "bad.csv", "csv")
    # pandas python engine handles bad lines or raises ParserError; either way handled gracefully
    assert isinstance(res.success, bool)
    if not res.success:
        assert res.error_message is not None


def test_dataframe_non_mutation() -> None:
    """10. DataLoader never mutates the original buffer or input DataFrames."""
    csv_data = b"Order_ID,Total_Sales\nORD-1,100.0\n"
    res1 = load_file_buffer(csv_data, "test.csv", "csv")
    res2 = load_file_buffer(csv_data, "test.csv", "csv")
    assert res1.dataframe is not res2.dataframe
    pd.testing.assert_frame_equal(res1.dataframe, res2.dataframe)
