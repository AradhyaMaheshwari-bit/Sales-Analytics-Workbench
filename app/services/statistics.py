"""Statistical validation service for the Sales Analytics Workbench.

Implements the approved two-tailed **Welch independent two-sample t-test**
(SDD-STAT §3.2), the Welch-Satterthwaite degrees of freedom, and the manually
computed 95% confidence interval for the difference in means (SDD-STAT §3.2).

Contract (SDD-STAT §4):
- Every statistic is computed freshly from the supplied ``active_df``.
- No historical benchmark value is ever returned by a computation path.

Guardrails (SDD-STAT §5):
- Single gender group, ``N < 5``, zero variance, non-finite sales values.
- Missing ``Gender`` rows are excluded and counted separately from
  missing/invalid ``Total_Sales`` rows.
- More than two gender categories require an explicit two-cohort selection.

Pure service: DataFrame in, result object out. No Streamlit imports.
"""

from __future__ import annotations

import math

import numpy as np
import pandas as pd
from scipy import stats

from app.models.validation_models import StatResult
from app.utils.logger import logger

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

GENDER_COLUMN = "Gender"
SALES_COLUMN = "Total_Sales"

#: Minimum valid observations required in each comparison group (SDD-STAT §5).
MIN_GROUP_SIZE = 5

#: Approved significance level (SDD-STAT §3.1).
DEFAULT_ALPHA = 0.05

# ---------------------------------------------------------------------------
# Cohort discovery and data preparation
# ---------------------------------------------------------------------------


def _gender_as_text(series: pd.Series) -> pd.Series:
    """Return the Gender column as string values with missing entries as NA."""
    return series.astype("string").str.strip()


def get_usable_gender_groups(df: pd.DataFrame | None) -> list[str]:
    """Return the sorted gender cohorts that have at least one observation.

    Missing, null and blank-string gender values are not cohorts and are
    never returned.

    Args:
        df: The active dataset.

    Returns:
        Sorted list of non-empty cohort labels, or ``[]`` when unavailable.
    """
    if df is None or len(df) == 0 or GENDER_COLUMN not in df.columns:
        return []

    text = _gender_as_text(df[GENDER_COLUMN])
    valid = text.dropna()
    valid = valid[valid.str.len() > 0]
    return sorted(str(value) for value in valid.unique())


def count_missing_gender_rows(df: pd.DataFrame | None) -> int:
    """Count rows whose gender value is missing, null or blank."""
    if df is None or len(df) == 0 or GENDER_COLUMN not in df.columns:
        return 0

    text = _gender_as_text(df[GENDER_COLUMN])
    return int((text.isna() | (text.str.len() == 0)).sum())


def _sales_as_numeric(series: pd.Series) -> pd.Series:
    """Coerce a sales column to float, turning unusable values into NaN."""
    return pd.to_numeric(series, errors="coerce").astype(float)


def compute_exclusion_counts(
    df: pd.DataFrame | None,
    group1: str,
    group2: str,
) -> tuple[int, int]:
    """Count excluded rows for the two selected cohorts as disjoint figures.

    The counts are computed over the rows that belong to ``group1`` or
    ``group2`` and are deliberately non-overlapping:

    1. Rows already dropped before cohort restriction because ``Gender`` is
       missing/blank (counted over the whole dataset).
    2. Rows that belong to the two selected cohorts but whose ``Total_Sales``
       is missing or non-finite.

    Rows belonging to other (unselected) cohorts are attributed to neither
    count, so the two figures never double-count the same row.

    Args:
        df: The active dataset.
        group1: First cohort label.
        group2: Second cohort label.

    Returns:
        A ``(missing_gender_rows, missing_sales_rows)`` tuple.
    """
    if df is None or len(df) == 0 or GENDER_COLUMN not in df.columns:
        return 0, 0

    missing_gender = count_missing_gender_rows(df)
    if SALES_COLUMN not in df.columns:
        return missing_gender, 0

    text = _gender_as_text(df[GENDER_COLUMN])
    in_cohorts = text.notna() & text.isin([group1, group2])
    sales = _sales_as_numeric(df[SALES_COLUMN])
    missing_sales = int((in_cohorts & ~np.isfinite(sales.to_numpy(dtype=float))).sum())
    return missing_gender, missing_sales


def prepare_comparison_frame(
    df: pd.DataFrame,
    group1: str,
    group2: str,
) -> pd.DataFrame:
    """Build the analysable two-cohort frame for a Welch comparison.

    Applies, in order:
    1. Removal of rows with missing/blank ``Gender``.
    2. Restriction to the two requested cohorts.
    3. Removal of rows whose ``Total_Sales`` is missing or non-finite.

    Args:
        df: The active dataset.
        group1: First cohort label.
        group2: Second cohort label.

    Returns:
        DataFrame with columns ``["Gender", "Total_Sales"]`` containing only
        usable observations for the two cohorts.
    """
    frame = pd.DataFrame(
        {
            "Gender": _gender_as_text(df[GENDER_COLUMN]),
            "Total_Sales": _sales_as_numeric(df[SALES_COLUMN]),
        }
    )

    # Missing-gender rows take no part in the comparison.
    frame = frame[frame["Gender"].notna()]

    # Restrict to the two selected cohorts.
    frame = frame[frame["Gender"].isin([group1, group2])].copy()
    frame["Gender"] = frame["Gender"].astype(str)

    # Non-finite / missing sales values are excluded by pairwise omission.
    numeric = frame["Total_Sales"].to_numpy(dtype=float)
    finite = np.isfinite(numeric)
    return frame.loc[finite].reset_index(drop=True)


# ---------------------------------------------------------------------------
# Core Welch calculation
# ---------------------------------------------------------------------------


def welch_ttest(
    sample1: pd.Series | list[float] | np.ndarray,
    sample2: pd.Series | list[float] | np.ndarray,
    group1_name: str,
    group2_name: str,
    alpha: float = DEFAULT_ALPHA,
) -> StatResult:
    """Run the approved two-tailed Welch independent two-sample t-test.

    Computes the Welch t-statistic, the Welch-Satterthwaite degrees of freedom,
    the two-tailed p-value, and the manually derived 95% confidence interval
    for the difference in means (SDD-STAT §3.2).

    Args:
        sample1: Observations for the first cohort.
        sample2: Observations for the second cohort.
        group1_name: Label of the first cohort.
        group2_name: Label of the second cohort.
        alpha: Significance level (default 0.05).

    Returns:
        A populated :class:`StatResult`.

    Raises:
        ValueError: When a guard condition prevents a valid test.
    """
    values1 = np.asarray(pd.Series(sample1), dtype=float)
    values2 = np.asarray(pd.Series(sample2), dtype=float)

    n1, n2 = values1.size, values2.size
    if n1 < MIN_GROUP_SIZE or n2 < MIN_GROUP_SIZE:
        raise ValueError("Sample size too small for reliable t-test (N < 5).")

    mean1, mean2 = float(values1.mean()), float(values2.mean())

    # Unbiased (ddof=1) sample variances, consistent with SDD-STAT §3.2.
    var1, var2 = float(values1.var(ddof=1)), float(values2.var(ddof=1))
    if var1 == 0.0 or var2 == 0.0:
        raise ValueError("Cannot compute t-statistic: zero variance in group.")

    term1 = var1 / n1
    term2 = var2 / n2
    standard_error_sq = term1 + term2
    standard_error = math.sqrt(standard_error_sq)
    if standard_error == 0.0 or not math.isfinite(standard_error):
        raise ValueError("Cannot compute t-statistic: zero variance in group.")

    t_statistic = (mean1 - mean2) / standard_error

    # Welch-Satterthwaite degrees of freedom.
    denominator = (term1**2) / (n1 - 1) + (term2**2) / (n2 - 1)
    if denominator == 0.0 or not math.isfinite(denominator):
        raise ValueError("Cannot compute t-statistic: zero variance in group.")
    degrees_of_freedom = (standard_error_sq**2) / denominator

    # Two-tailed p-value from the t distribution.
    p_value = float(2.0 * stats.t.sf(abs(t_statistic), degrees_of_freedom))

    # Manually computed 95% confidence interval for the mean difference.
    mean_diff = mean1 - mean2
    critical_value = float(stats.t.ppf(1.0 - alpha / 2.0, degrees_of_freedom))
    margin_of_error = critical_value * standard_error

    decision = "Reject H0" if p_value < alpha else "Fail to Reject H0"

    logger.info(
        "Welch t-test executed: n1=%s n2=%s t=%.4f df=%.4f p=%.4f decision=%s",
        n1,
        n2,
        t_statistic,
        degrees_of_freedom,
        p_value,
        decision,
    )

    return StatResult(
        t_statistic=float(t_statistic),
        p_value=float(p_value),
        degrees_of_freedom=float(degrees_of_freedom),
        ci_lower=float(mean_diff - margin_of_error),
        ci_upper=float(mean_diff + margin_of_error),
        mean_diff=float(mean_diff),
        group1_name=str(group1_name),
        group2_name=str(group2_name),
        group1_count=int(n1),
        group2_count=int(n2),
        group1_mean=mean1,
        group2_mean=mean2,
        decision=decision,
        alpha=float(alpha),
    )


# ---------------------------------------------------------------------------
# Guarded end-to-end analysis
# ---------------------------------------------------------------------------


def run_gender_comparison(
    df: pd.DataFrame | None,
    group1: str | None = None,
    group2: str | None = None,
    alpha: float = DEFAULT_ALPHA,
) -> StatResult:
    """Run the guarded Welch comparison on the active dataset.

    Validations performed:
    - Required columns ``Gender`` and ``Total_Sales`` must be present.
    - Missing ``Gender`` values are excluded and reported separately (by the
      caller) via ``count_missing_gender_rows``.
    - Missing / non-finite ``Total_Sales`` values are excluded pairwise.

    Behaviour when more than two cohorts are available:
    - No selection supplied -> ``ValueError`` prompting for cohort selection.

    Args:
        df: The active dataset.
        group1: Explicitly selected first cohort, if any.
        group2: Explicitly selected second cohort, if any.
        alpha: Significance level (default 0.05).

    Returns:
        A populated :class:`StatResult`.

    Raises:
        ValueError: With a clear, actionable message when the test cannot be run.
    """
    if df is None or len(df) == 0:
        raise ValueError("No usable observations: the active dataset is empty.")

    missing_columns = [
        col for col in (GENDER_COLUMN, SALES_COLUMN) if col not in df.columns
    ]
    if missing_columns:
        raise ValueError(
            "Statistical test aborted. Missing required column(s): "
            + ", ".join(f"'{col}'" for col in missing_columns)
            + "."
        )

    available_groups = get_usable_gender_groups(df)
    if len(available_groups) < 2:
        raise ValueError(
            f"Statistical t-test requires two independent groups. Found: {len(available_groups)} group."
        )

    if group1 is None and group2 is None:
        raise ValueError(
            "More than two gender cohorts are present. Select the two cohorts "
            "to compare."
        )

    if group1 is None or group2 is None or group1 == group2:
        raise ValueError("Select both comparison cohorts before running the test.")

    unavailable = [g for g in (group1, group2) if g not in available_groups]
    if unavailable:
        raise ValueError(
            "Invalid cohort selection: "
            + ", ".join(f"'{g}'" for g in unavailable)
            + " is not an available comparison cohort."
        )

    frame = prepare_comparison_frame(df, group1, group2)
    eligible_rows = int(len(frame))

    if eligible_rows == 0:
        raise ValueError(
            "No usable observations: the selected cohorts contain no valid "
            "'Total_Sales' values."
        )

    values1 = frame.loc[frame["Gender"] == group1, SALES_COLUMN]
    values2 = frame.loc[frame["Gender"] == group2, SALES_COLUMN]

    short_groups = [
        f"{name} (N={len(values)})"
        for name, values in ((group1, values1), (group2, values2))
        if len(values) < MIN_GROUP_SIZE
    ]
    if short_groups:
        raise ValueError(
            f"Sample size too small for reliable t-test (N < 5). Insufficient observations in: {', '.join(short_groups)}."
        )

    return welch_ttest(values1, values2, group1, group2, alpha=alpha)


# ---------------------------------------------------------------------------
# Plain-language interpretation
# ---------------------------------------------------------------------------


def build_interpretation(result: StatResult) -> str:
    """Build a business-language interpretation of a computed StatResult.

    The wording is derived entirely from the computed values; it never quotes
    historical benchmark figures. Failing to reject H0 is never described as
    proof that the means are equal (SDD-STAT §3.3).

    Args:
        result: The computed Welch test result.

    Returns:
        A plain-language interpretation paragraph.
    """
    g1, g2 = result.group1_name, result.group2_name
    alpha_pct = int(round(result.alpha * 100))
    direction = "higher" if result.mean_diff > 0 else "lower"
    ci_spans_zero = result.ci_lower < 0 < result.ci_upper

    if result.p_value < result.alpha:
        paragraph = (
            f"At the {alpha_pct}% significance level the null hypothesis is "
            f"rejected (p = {result.p_value:.4f} < {result.alpha}). The mean "
            f"Total Sales for {g1} is {direction} than for {g2} by a margin that "
            f"is unlikely to have arisen from sampling variation alone. The 95% "
            f"confidence interval does not include zero."
        )
    else:
        paragraph = (
            f"At the {alpha_pct}% significance level the null hypothesis is not "
            f"rejected (p = {result.p_value:.4f} ≥ {result.alpha}). The "
            f"observed difference of about {result.mean_diff:,.2f} between {g1} "
            f"and {g2} is consistent with sampling variation. Failing to reject "
            f"H0 does not prove that the two population means are equal — it "
            f"means the data provide insufficient evidence of a difference."
        )

    if ci_spans_zero:
        paragraph += (
            " The 95% confidence interval spans zero, so a zero difference in "
            "mean sales remains plausible at this confidence level."
        )

    paragraph += (
        " Statistical significance is not the same as business significance: "
        "the result alone does not establish causation or justify a revenue claim."
    )
    return paragraph
