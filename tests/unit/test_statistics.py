"""Unit tests for the statistical validation module and Welch's t-test (Increment 5)."""

from __future__ import annotations

import pandas as pd
import pytest
from app.models.validation_models import StatResult
from app.services.statistics import (
    count_missing_gender_rows,
    get_usable_gender_groups,
    run_gender_comparison,
    welch_ttest,
)


def test_welch_ttest_calculation():
    """Verify Welch t-statistic, df, and manually computed 95% CI."""
    sample1 = [100.0, 110.0, 105.0, 108.0, 102.0, 107.0]
    sample2 = [90.0, 92.0, 88.0, 95.0, 91.0, 89.0]
    result = welch_ttest(sample1, sample2, "GroupA", "GroupB", alpha=0.05)

    assert isinstance(result, StatResult)
    assert result.group1_name == "GroupA"
    assert result.group2_name == "GroupB"
    assert result.group1_count == 6
    assert result.group2_count == 6
    assert result.t_statistic > 0
    assert result.p_value < 0.05
    assert result.decision == "Reject H0"
    assert result.ci_lower < result.mean_diff < result.ci_upper


def test_decision_rule_fail_to_reject():
    """Verify decision rule when p-value >= alpha (fail to reject H0)."""
    sample1 = [100.0, 101.0, 99.0, 100.5, 99.5, 100.0]
    sample2 = [100.1, 100.9, 99.2, 100.3, 99.7, 100.1]
    result = welch_ttest(sample1, sample2, "GroupA", "GroupB", alpha=0.05)

    assert result.p_value >= 0.05
    assert result.decision == "Fail to Reject H0"


def test_guard_missing_required_columns():
    """Verify error when required columns are missing."""
    df = pd.DataFrame({"Other": [1, 2, 3]})
    with pytest.raises(ValueError, match="Missing required column"):
        run_gender_comparison(df, "Male", "Female")


def test_guard_single_available_group():
    """Verify error when only one gender category exists."""
    df = pd.DataFrame(
        {
            "Gender": ["Male", "Male", "Male", "Male", "Male", "Male"],
            "Total_Sales": [100.0, 110.0, 105.0, 108.0, 102.0, 107.0],
        }
    )
    with pytest.raises(ValueError, match="requires two independent groups"):
        run_gender_comparison(df, "Male", "Female")


def test_guard_small_sample_size():
    """Verify error when N < 5 in either group."""
    df = pd.DataFrame(
        {
            "Gender": ["Male", "Male", "Female", "Female", "Female"],
            "Total_Sales": [100.0, 110.0, 90.0, 92.0, 88.0],
        }
    )
    with pytest.raises(ValueError, match="Sample size too small"):
        run_gender_comparison(df, "Male", "Female")


def test_guard_zero_variance():
    """Verify error when sample variance is zero in a group."""
    df = pd.DataFrame(
        {
            "Gender": ["Male"] * 5 + ["Female"] * 5,
            "Total_Sales": [
                100.0,
                100.0,
                100.0,
                100.0,
                100.0,
                90.0,
                92.0,
                88.0,
                95.0,
                91.0,
            ],
        }
    )
    with pytest.raises(ValueError, match="zero variance"):
        run_gender_comparison(df, "Male", "Female")


def test_missing_sales_pairwise_omission():
    """Verify missing/non-finite sales values are excluded pairwise."""
    df2 = pd.DataFrame(
        {
            "Gender": ["Male"] * 8 + ["Female"] * 6,
            "Total_Sales": [100.0, 110.0, 105.0, 108.0, 103.0, 104.0, 106.0, None]
            + [90.0, 92.0, 88.0, 95.0, 91.0, 89.0],
        }
    )
    result = run_gender_comparison(df2, "Male", "Female")
    assert result.group1_count == 7
    assert result.group2_count == 6


def test_missing_gender_exclusion_and_count():
    """Verify missing gender rows are excluded and counted separately."""
    df = pd.DataFrame(
        {
            "Gender": ["Male"] * 5 + ["Female"] * 5 + [None, "", "   "],
            "Total_Sales": [100.0] * 13,
        }
    )
    assert count_missing_gender_rows(df) == 3
    groups = get_usable_gender_groups(df)
    assert groups == ["Female", "Male"]


def test_more_than_two_gender_categories_requires_selection():
    """Verify ValueError is raised when > 2 categories exist and none selected."""
    df = pd.DataFrame(
        {
            "Gender": ["Male"] * 5 + ["Female"] * 5 + ["Other"] * 5,
            "Total_Sales": [100.0, 102.0, 104.0, 106.0, 108.0]
            + [90.0, 92.0, 94.0, 96.0, 98.0]
            + [80.0, 82.0, 84.0, 86.0, 88.0],
        }
    )
    with pytest.raises(ValueError, match="More than two gender cohorts are present"):
        run_gender_comparison(df, None, None)

    # When two cohorts are explicitly selected from the three available:
    result = run_gender_comparison(df, "Male", "Female")
    assert result.group1_name == "Male"
    assert result.group2_name == "Female"


def test_source_inspection_no_hardcoded_constants():
    """Ensure normal computation paths do not return hardcoded historical benchmark constants."""
    df_low = pd.DataFrame(
        {
            "Gender": ["Male"] * 5 + ["Female"] * 5,
            "Total_Sales": [10.0, 11.0, 12.0, 9.0, 10.0]
            + [20.0, 21.0, 22.0, 19.0, 20.0],
        }
    )
    res_low = run_gender_comparison(df_low, "Male", "Female")
    assert round(res_low.group1_mean, 1) == 10.4
    assert round(res_low.group2_mean, 1) == 20.4

    df_high = pd.DataFrame(
        {
            "Gender": ["Male"] * 5 + ["Female"] * 5,
            "Total_Sales": [1000.0, 1100.0, 1200.0, 900.0, 1000.0]
            + [2000.0, 2100.0, 2200.0, 1900.0, 2000.0],
        }
    )
    res_high = run_gender_comparison(df_high, "Male", "Female")
    assert round(res_high.group1_mean, 1) == 1040.0
    assert round(res_high.group2_mean, 1) == 2040.0


def test_historical_benchmark_gated():
    """Historical benchmark test: runs only if data/raw/internship_dataset.xlsx exists."""
    from pathlib import Path

    import openpyxl  # noqa: F401

    benchmark_path = Path("data/raw/internship_dataset.xlsx")
    if not benchmark_path.is_file():
        pytest.skip(
            "Historical benchmark dataset not present at data/raw/internship_dataset.xlsx"
        )

    df = pd.read_excel(benchmark_path)
    assert len(df) == 1000
    result = run_gender_comparison(df, "Male", "Female")
    assert 0.678 <= result.t_statistic <= 0.688
    assert 0.490 <= result.p_value <= 0.500
    assert result.decision == "Fail to Reject H0"
