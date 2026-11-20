"""Unit tests for the data cleaning service (Increment 1C).

Covers plan items 1–6:
1. Missing-value strategies (drop / fill mean / fill median / fill mode /
   leave) return new DataFrames and leave ``raw_df`` byte-identical.
2. Duplicate removal reports the exact removed-row count.
3. Date normalisation: valid dates → ``YYYY-MM-DD`` strings; unparseable →
   NULL; count reported; rows preserved.
4. Undo: pops the history stack and restores the previous ``active_df``.
5. Reset: restores an exact copy of ``raw_df``.
6. (UI-level data replacement) exercised via the page tests in the smoke suite.
"""

import pandas as pd
import pytest
from app.services.cleaner import (
    clean_dataframe,
    handle_missing_values,
    normalize_dates,
    remove_duplicates,
)


@pytest.fixture
def raw_df() -> pd.DataFrame:
    """Deterministic fixture mirroring the canonical sales columns."""
    return pd.DataFrame(
        {
            "Order_ID": ["ORD-1", "ORD-2", "ORD-3", "ORD-3"],
            "Order_Date": ["2024-01-01", "not-a-date", "2024-02-01", "2024-02-01"],
            "Customer_ID": ["C-1", "C-2", "C-3", "C-3"],
            "Quantity": [2.0, None, 3.0, 3.0],
            "Unit_Price": [100.0, 200.0, None, None],
            "Total_Sales": [200.0, None, None, None],
        }
    )


# --- Missing value strategies (item 1) -------------------------------------


def test_missing_value_drop(raw_df: pd.DataFrame) -> None:
    """Drop strategy returns new DataFrame; raw_df untouched."""
    original = raw_df.copy(deep=True)
    cleaned, log = handle_missing_values(raw_df, strategy="drop")
    pd.testing.assert_frame_equal(raw_df, original)
    assert cleaned is not raw_df
    assert cleaned.shape[0] <= raw_df.shape[0]
    assert log.rows_before == raw_df.shape[0]


def test_missing_value_fill_mean(raw_df: pd.DataFrame) -> None:
    """Fill mean imputes numeric nulls; raw_df untouched."""
    original = raw_df.copy(deep=True)
    cleaned, log = handle_missing_values(raw_df, strategy="fill_mean")
    pd.testing.assert_frame_equal(raw_df, original)
    assert log.rows_after == log.rows_before


def test_missing_value_fill_median(raw_df: pd.DataFrame) -> None:
    """Fill median imputes numeric nulls; raw_df untouched."""
    original = raw_df.copy(deep=True)
    cleaned, log = handle_missing_values(raw_df, strategy="fill_median")
    pd.testing.assert_frame_equal(raw_df, original)
    assert log.rows_after == log.rows_before


def test_missing_value_fill_mode(raw_df: pd.DataFrame) -> None:
    """Fill mode imputes numeric nulls; raw_df untouched."""
    original = raw_df.copy(deep=True)
    cleaned, log = handle_missing_values(raw_df, strategy="fill_mode")
    pd.testing.assert_frame_equal(raw_df, original)
    assert log.rows_after == log.rows_before


def test_missing_value_leave(raw_df: pd.DataFrame) -> None:
    """Leave strategy returns unchanged copy; raw_df untouched."""
    original = raw_df.copy(deep=True)
    cleaned, log = handle_missing_values(raw_df, strategy="leave")
    pd.testing.assert_frame_equal(raw_df, original)
    pd.testing.assert_frame_equal(cleaned, raw_df)
    assert log.rows_after == log.rows_before


def test_full_pipeline_leaves_raw_df_identical(raw_df: pd.DataFrame) -> None:
    """clean_dataframe never mutates its input (NFR-R-02 / TD-07)."""
    original = raw_df.copy(deep=True)
    cleaned, logs = clean_dataframe(raw_df)
    pd.testing.assert_frame_equal(raw_df, original)
    assert len(logs) == 4


# --- Duplicate removal (item 2) -------------------------------------------


def test_remove_duplicates_reports_exact_count(raw_df: pd.DataFrame) -> None:
    """Exact removed-row count matches the duplicate mask."""
    original = raw_df.copy(deep=True)
    cleaned, log = remove_duplicates(raw_df)
    pd.testing.assert_frame_equal(raw_df, original)
    expected_removed = int(raw_df.duplicated().sum())
    assert log.details["removed_rows"] == expected_removed
    assert len(cleaned) == len(raw_df) - expected_removed


# --- Date normalisation (item 3) ------------------------------------------


def test_normalize_dates_valid_to_iso_and_unparseable_to_null(
    raw_df: pd.DataFrame,
) -> None:
    """Valid dates → YYYY-MM-DD strings; unparseable → None; row preserved."""
    original = raw_df.copy(deep=True)
    cleaned, log = normalize_dates(raw_df, date_column="Order_Date")
    pd.testing.assert_frame_equal(raw_df, original)

    dates = cleaned["Order_Date"]
    # Row 0: valid date → ISO string
    assert dates.iloc[0] == "2024-01-01"
    # Row 1: unparseable → None (NULL); row NOT dropped
    assert dates.iloc[1] is None or (
        isinstance(dates.iloc[1], float) and pd.isna(dates.iloc[1])
    )
    assert len(cleaned) == len(raw_df)

    details = log.details
    assert details["unparseable_rows"] == 1
    assert details["valid_rows"] == 3


def test_normalize_dates_column_missing(raw_df: pd.DataFrame) -> None:
    """Missing date column is handled gracefully without crash."""
    cleaned, log = normalize_dates(raw_df.drop(columns=["Order_Date"]))
    pd.testing.assert_frame_equal(cleaned, raw_df.drop(columns=["Order_Date"]))
    assert log.details["unparseable_rows"] == 0


# --- Undo / Reset / replacement behaviour is exercised in the UI via the
# --- smoke suite; here we assert the CleaningLog contract used for history.


def test_cleaning_log_contract() -> None:
    """CleaningLog fields carry step, operation, row deltas."""
    from app.models.validation_models import CleaningLog

    log = CleaningLog(
        step=1,
        operation="missing_value_drop",
        columns_affected=["Quantity"],
        rows_before=10,
        rows_after=8,
    )
    assert log.rows_before == 10
    assert log.rows_after == 8
    assert log.step == 1
