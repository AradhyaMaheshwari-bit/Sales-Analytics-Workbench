"""Unit tests for the business-rule validator (Increment 1C).

Covers plan item 7:
Validator: ``Quantity <= 0``, ``Unit_Price <= 0``,
``Total_Sales ≈ Quantity × Unit_Price`` mismatch detection, with
pass/fail counts.
"""

import pandas as pd
import pytest
from app.services.validator import (
    check_quantity_positive,
    check_total_sales_match,
    check_unit_price_positive,
    validate_business_rules,
)


@pytest.fixture
def valid_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Quantity": [2, 3, 5],
            "Unit_Price": [100.0, 200.0, 10.0],
            "Total_Sales": [200.0, 600.0, 50.0],
        }
    )


@pytest.fixture
def invalid_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Quantity": [0, -1, 5],
            "Unit_Price": [100.0, 0.0, 10.0],
            "Total_Sales": [200.0, 600.0, 999.0],
        }
    )


def test_quantity_positive_rule(valid_df: pd.DataFrame) -> None:
    result = check_quantity_positive(valid_df)
    assert result.passed == 3
    assert result.failed == 0


def test_quantity_positive_rule_detects_violations(invalid_df: pd.DataFrame) -> None:
    result = check_quantity_positive(invalid_df)
    assert result.passed == 1
    assert result.failed == 2
    assert result.passed_percentage == pytest.approx(33.33, abs=0.01)
    assert any("row 0" in d and "Quantity=0" in d for d in result.failure_details)


def test_unit_price_positive_rule(valid_df: pd.DataFrame) -> None:
    result = check_unit_price_positive(valid_df)
    assert result.passed == 3
    assert result.failed == 0


def test_unit_price_positive_rule_detects_violations(invalid_df: pd.DataFrame) -> None:
    result = check_unit_price_positive(invalid_df)
    assert result.passed == 2
    assert result.failed == 1


def test_total_sales_match_rule(valid_df: pd.DataFrame) -> None:
    result = check_total_sales_match(valid_df)
    assert result.passed == 3
    assert result.failed == 0


def test_total_sales_match_rule_detects_mismatch(invalid_df: pd.DataFrame) -> None:
    result = check_total_sales_match(invalid_df)
    assert (
        result.failed == 3
    )  # rows 0, 1, 2 all have mismatched Total_Sales vs Quantity*Unit_Price


def test_validate_business_rules_overall_pass(valid_df: pd.DataFrame) -> None:
    summary = validate_business_rules(valid_df)
    assert summary.overall_pass is True
    assert summary.total_rows == 3
    assert all(r.failed == 0 for r in summary.checks.values())


def test_validate_business_rules_overall_fail(invalid_df: pd.DataFrame) -> None:
    summary = validate_business_rules(invalid_df)
    assert summary.overall_pass is False
    assert any(r.failed > 0 for r in summary.checks.values())


def test_missing_columns_handled_gracefully() -> None:
    df = pd.DataFrame({"Quantity": [1, 2]})
    result = check_total_sales_match(df)
    assert result.passed == 0
    assert result.failed == 0
    assert "missing column" in result.failure_details[0].lower()


def test_null_values_handled_gracefully() -> None:
    df = pd.DataFrame(
        {
            "Quantity": [1, None],
            "Unit_Price": [100.0, 200.0],
            "Total_Sales": [100.0, 400.0],
        }
    )
    result = check_total_sales_match(df)
    assert result.failed == 1  # row 1 has NULL quantity
