"""Business-rule validation service for the Sales Analytics Workbench.

Applies the FR-09 validation rules to a *cleaned* DataFrame and returns a
typed ``ValidationSummary`` with per-rule pass/fail counts and per-row
failure details (row index, column, expected vs. actual value).

Rules are individually configurable (enable/disable) per FR-09 AC-3, and
the summary reports pass/fail counts per FR-09 AC-4.  The service is pure:
it never mutates the input DataFrame and has no Streamlit dependency.
"""

from __future__ import annotations

from typing import Any

import pandas as pd

from app.models.validation_models import RuleCheckResult, ValidationSummary

# Tolerance for the Total_Sales ≈ Quantity × Unit_Price rule.
# "within rounding tolerance" per FR-09 — two decimal places of INR.
DEFAULT_TOLERANCE = 0.01

RULE_IDS = ("quantity_positive", "unit_price_positive", "total_sales_match")


def _fmt(value: Any) -> str:
    """Render a value for failure-detail strings without leaking NaN noise."""
    if pd.isna(value):
        return "NULL"
    if isinstance(value, float):
        return f"{value:.2f}"
    return str(value)


def check_quantity_positive(df: pd.DataFrame) -> RuleCheckResult:
    """FR-09 rule: Quantity must be > 0 for every row."""
    if "Quantity" not in df.columns:
        return RuleCheckResult(
            rule_name="quantity_positive",
            passed=0,
            failed=0,
            failure_details=["Rule not applicable: 'Quantity' column missing"],
            passed_percentage=0.0,
        )

    failures: list[str] = []
    for idx, value in df["Quantity"].items():
        if pd.isna(value) or not (value > 0):
            failures.append(f"row {idx}: Quantity={_fmt(value)}; expected > 0")

    passed_count = len(df) - len(failures)
    total = len(df)
    return RuleCheckResult(
        rule_name="quantity_positive",
        passed=passed_count,
        failed=len(failures),
        failure_details=failures,
        passed_percentage=(passed_count / total * 100.0) if total else 100.0,
    )


def check_unit_price_positive(df: pd.DataFrame) -> RuleCheckResult:
    """FR-09 rule: Unit_Price must be > 0 for every row."""
    if "Unit_Price" not in df.columns:
        return RuleCheckResult(
            rule_name="unit_price_positive",
            passed=0,
            failed=0,
            failure_details=["Rule not applicable: 'Unit_Price' column missing"],
            passed_percentage=0.0,
        )

    failures: list[str] = []
    for idx, value in df["Unit_Price"].items():
        if pd.isna(value) or not (value > 0):
            failures.append(f"row {idx}: Unit_Price={_fmt(value)}; expected > 0")

    passed_count = len(df) - len(failures)
    total = len(df)
    return RuleCheckResult(
        rule_name="unit_price_positive",
        passed=passed_count,
        failed=len(failures),
        failure_details=failures,
        passed_percentage=(passed_count / total * 100.0) if total else 100.0,
    )


def check_total_sales_match(
    df: pd.DataFrame,
    tolerance: float = DEFAULT_TOLERANCE,
) -> RuleCheckResult:
    """FR-09 rule: Total_Sales ≈ Quantity × Unit_Price within *tolerance*."""
    required = ("Total_Sales", "Quantity", "Unit_Price")
    missing = [c for c in required if c not in df.columns]
    if missing:
        return RuleCheckResult(
            rule_name="total_sales_match",
            passed=0,
            failed=0,
            failure_details=[f"Rule not applicable: missing column(s) {missing}"],
            passed_percentage=0.0,
        )

    failures: list[str] = []
    for idx, row in df.iterrows():
        quantity = row["Quantity"]
        unit_price = row["Unit_Price"]
        total_sales = row["Total_Sales"]

        if pd.isna(quantity) or pd.isna(unit_price) or pd.isna(total_sales):
            failures.append(
                f"row {idx}: Total_Sales={_fmt(total_sales)}, "
                f"Quantity={_fmt(quantity)}, Unit_Price={_fmt(unit_price)}; "
                "expected Quantity × Unit_Price (NULL operand)"
            )
            continue

        expected = float(quantity) * float(unit_price)
        if abs(float(total_sales) - expected) > tolerance:
            failures.append(
                f"row {idx}: Total_Sales={_fmt(total_sales)}, "
                f"expected {expected:.2f} (Quantity {_fmt(quantity)} × "
                f"Unit_Price {_fmt(unit_price)}); diff "
                f"{abs(float(total_sales) - expected):.2f} > tolerance {tolerance:.2f}"
            )

    passed_count = len(df) - len(failures)
    total = len(df)
    return RuleCheckResult(
        rule_name="total_sales_match",
        passed=passed_count,
        failed=len(failures),
        failure_details=failures,
        passed_percentage=(passed_count / total * 100.0) if total else 100.0,
    )


class Validator:
    """Apply configurable FR-09 business rules to a cleaned DataFrame."""

    def __init__(self, tolerance: float = DEFAULT_TOLERANCE) -> None:
        self.tolerance = tolerance
        self._checks = {
            "quantity_positive": check_quantity_positive,
            "unit_price_positive": check_unit_price_positive,
            "total_sales_match": lambda df: check_total_sales_match(
                df, tolerance=self.tolerance
            ),
        }

    def validate(
        self,
        df: pd.DataFrame,
        enabled_rules: list[str] | None = None,
    ) -> ValidationSummary:
        """Run the selected rules and return a typed ValidationSummary.

        Args:
            df: The cleaned DataFrame (validation runs *after* cleaning).
            enabled_rules: Rule IDs to run.  None runs all rules.

        Returns:
            ValidationSummary with per-rule RuleCheckResult entries and an
            ``overall_pass`` flag that is True only when every enabled rule
            passed for every row.
        """
        rules = list(enabled_rules) if enabled_rules is not None else list(RULE_IDS)

        checks: dict[str, RuleCheckResult] = {}
        for rule_id in rules:
            check_fn = self._checks.get(rule_id)
            if check_fn is None:
                raise ValueError(
                    f"Unknown validation rule: {rule_id!r}. Expected one of {RULE_IDS}."
                )
            checks[rule_id] = check_fn(df)

        overall_pass = all(result.failed == 0 for result in checks.values())

        return ValidationSummary(
            total_rows=len(df),
            checks=checks,
            overall_pass=overall_pass,
        )


def validate_business_rules(
    df: pd.DataFrame,
    enabled_rules: list[str] | None = None,
    tolerance: float = DEFAULT_TOLERANCE,
) -> ValidationSummary:
    """Convenience wrapper: validate *df* with default configuration."""
    validator = Validator(tolerance=tolerance)
    return validator.validate(df, enabled_rules=enabled_rules)
