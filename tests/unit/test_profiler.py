"""Unit tests for dataset profiler service (Increment 1B)."""

import numpy as np
import pandas as pd
import pytest
from app.services.profiler import Profiler, profile_dataframe


@pytest.fixture
def sample_sales_df() -> pd.DataFrame:
    """Fixed sample sales dataframe for deterministic assertion."""
    return pd.DataFrame(
        {
            "Order_ID": ["ORD1", "ORD2", "ORD3", "ORD3"],  # 1 duplicate row with below
            "Total_Sales": [100.0, 200.0, 300.0, 300.0],
            "Quantity": [1, 2, 3, 3],
            "Category": ["Electronics", "Fashion", "Home", "Home"],
            "Missing_Col": [1.0, np.nan, 3.0, 3.0],
        }
    )


def test_profiler_metrics_computation(sample_sales_df: pd.DataFrame) -> None:
    """Profiler correctly computes row/col counts, duplicates, missing cells, and stats."""
    profiler = Profiler()
    metrics = profiler.profile(sample_sales_df)

    assert metrics.row_count == 4
    assert metrics.column_count == 5
    assert metrics.duplicate_row_count == 1
    assert metrics.duplicate_percentage == 25.0
    assert metrics.missing_total == 1
    assert metrics.missing_percentage == (1 / 20) * 100.0

    # Numeric summary
    ts_profile = metrics.columns["Total_Sales"]
    assert ts_profile.non_null_count == 4
    assert ts_profile.null_count == 0
    assert ts_profile.min_val == 100.0
    assert ts_profile.max_val == 300.0
    assert ts_profile.mean == 225.0


def test_profiler_single_row_and_all_null() -> None:
    """Profiler handles single-row DataFrame and all-null column without exception."""
    df = pd.DataFrame(
        {
            "Single": [42.0],
            "AllNull": [np.nan],
        }
    )
    metrics = profile_dataframe(df)

    assert metrics.row_count == 1
    assert metrics.column_count == 2
    assert metrics.columns["AllNull"].null_count == 1
    assert metrics.columns["AllNull"].non_null_count == 0
    assert metrics.columns["AllNull"].mean is None
    assert metrics.columns["Single"].mean == 42.0


def test_profiler_does_not_mutate_input(sample_sales_df: pd.DataFrame) -> None:
    """Profiler never mutates the input DataFrame."""
    original_copy = sample_sales_df.copy(deep=True)
    _ = profile_dataframe(sample_sales_df)

    pd.testing.assert_frame_equal(sample_sales_df, original_copy)
