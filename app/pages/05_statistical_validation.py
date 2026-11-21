"""Module 5 — Statistical Validation (Increment 5).

Presents the approved Welch independent two-sample t-test interface:

- Hypothesis formulation (H0 / H1, two-tailed, α = 0.05).
- Computed Welch results: t-statistic, p-value, mean difference, 95% CI.
- Group summaries (sample sizes, means) and the actual decision.
- Plotly distribution overlay for the selected cohorts.
- Business interpretation derived from the computed result.

Design (SDD-STAT §3–§5, SDD-MOD §2.1, FR-19):
- Empty state: exactly the approved message when no dataset is active.
- Guard failures surface approved user-safe messages as warnings.
- Historical benchmark values live only in the gated test — never here.
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

from app.services.statistics import (
    DEFAULT_ALPHA,
    build_interpretation,
    compute_exclusion_counts,
    get_usable_gender_groups,
    run_gender_comparison,
)
from app.utils.charts import ChartFactory
from app.utils.formatters import format_inr, format_percent

chart_factory = ChartFactory()

EMPTY_STATE_MESSAGE = "No dataset loaded. Upload a file or enable Demo Mode."

HYPOTHESIS_MARKDOWN = """
**Null Hypothesis (H₀):** The mean `Total_Sales` for the first cohort is equal to
the mean `Total_Sales` for the second cohort.

**Alternative Hypothesis (H₁):** The mean `Total_Sales` for the first cohort is not
equal to the mean `Total_Sales` for the second cohort.

- Test type: two-tailed independent t-test (Welch, unequal variances).
- Significance level: α = 0.05.
"""


def _check_data_loaded() -> bool:
    """Check if a valid dataset is loaded for analysis."""
    if (
        st.session_state.get("active_df") is None
        or len(st.session_state.get("active_df", pd.DataFrame())) == 0
    ):
        st.info(EMPTY_STATE_MESSAGE)
        return False
    return True


def _available_cohorts() -> list[str]:
    """Return sorted gender cohorts present in the active dataset."""
    df = st.session_state.get("active_df", pd.DataFrame())
    return get_usable_gender_groups(df)


def _render_hypothesis() -> None:
    """Render the hypothesis formulation card."""
    st.subheader("Hypothesis")
    st.markdown(HYPOTHESIS_MARKDOWN)


def _render_result_metrics(result) -> None:
    """Render the computed Welch result metrics and group summaries."""
    group1_mean = format_inr(result.group1_mean)
    group2_mean = format_inr(result.group2_mean)

    stat_cols = st.columns(4)
    with stat_cols[0]:
        st.metric(label=f"{result.group1_name} Mean Sales", value=group1_mean)
    with stat_cols[1]:
        st.metric(label=f"{result.group2_name} Mean Sales", value=group2_mean)
    with stat_cols[2]:
        st.metric(label="Mean Difference", value=format_inr(result.mean_diff))
    with stat_cols[3]:
        st.metric(label="P-Value", value=format_percent(result.p_value))

    meta_cols = st.columns(4)
    with meta_cols[0]:
        st.metric(label="Welch T-Statistic", value=f"{result.t_statistic:.4f}")
    with meta_cols[1]:
        st.metric(label="Degrees of Freedom", value=f"{result.degrees_of_freedom:.4f}")
    with meta_cols[2]:
        st.metric(
            label="95% Confidence Interval",
            value=f"{result.ci_lower:.2f} – {result.ci_upper:.2f}",
        )
    with meta_cols[3]:
        st.metric(
            label="Significant?",
            value="Yes" if result.decision == "Reject H0" else "No",
        )

    st.markdown(f"""
**Decision:** {result.decision}

**95% Confidence Interval:** {format_inr(result.ci_lower)} to {format_inr(result.ci_upper)}

**Group Means:** {result.group1_name} = {group1_mean} (N = {result.group1_count});
{result.group2_name} = {group2_mean} (N = {result.group2_count}).

**Mean Difference:** {format_inr(result.mean_diff)}
""")


def _render_distribution_chart(result) -> None:
    """Render the Plotly distribution overlay for the selected cohorts."""
    df = st.session_state.get("active_df", pd.DataFrame())
    gender_text = df["Gender"].astype("string").str.strip()
    frame = pd.DataFrame(
        {
            "Gender": gender_text.where(gender_text.notna(), None),
            "Total_Sales": pd.to_numeric(df["Total_Sales"], errors="coerce"),
        }
    )
    frame = frame.dropna(subset=["Gender", "Total_Sales"])
    frame = frame[frame["Gender"].isin([result.group1_name, result.group2_name])].copy()
    frame["Gender"] = frame["Gender"].astype(str)

    # Rows excluded from the comparison, kept separate (no double-counting).
    missing_gender, missing_sales = compute_exclusion_counts(
        st.session_state.get("active_df", pd.DataFrame()),
        result.group1_name,
        result.group2_name,
    )
    excluded_md = (
        f"**Excluded rows:** {missing_gender} missing/blank Gender; "
        f"{missing_sales} missing/non-finite Total_Sales within the two "
        "selected cohorts (counts are disjoint and not double-counted)."
    )

    fig = chart_factory.distribution_overlay(
        frame,
        x="Total_Sales",
        color="Gender",
        title="Sales Distribution by Gender",
        yaxis_title="Total Sales (₹)",
        y_is_currency=True,
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown(excluded_md)


def render_page() -> None:
    """Render the complete Module 5 statistical validation page."""
    st.header("Module 5 — Statistical Validation")
    st.markdown("""
        Runs a Welch independent two-sample t-test comparing mean sales between
        two gender cohorts using the active dataset. All results are computed
        live; historical internship values are never used as defaults.
        """)
    st.divider()

    if not _check_data_loaded():
        return

    df = st.session_state.get("active_df", pd.DataFrame())

    _render_hypothesis()

    # Cohort selection for datasets with more than two categories.
    available = _available_cohorts()
    group1: str | None = None
    group2: str | None = None

    if len(available) > 2:
        group1 = st.selectbox(
            "Cohort 1 (e.g., Male)", options=available, key="statistical_cohort_1"
        )
        group2 = st.selectbox(
            "Cohort 2 (e.g., Female)",
            options=[g for g in available if g != group1],
            key="statistical_cohort_2",
        )
    elif len(available) == 2:
        group1, group2 = available

    if len(available) < 2:
        st.warning(
            "Statistical t-test requires two independent groups. Found: "
            + str(len(available))
            + " group."
        )
        return

    run_test = st.button("▶ Run Statistical Test", type="primary")

    if run_test:
        try:
            result = run_gender_comparison(
                df, group1=group1, group2=group2, alpha=DEFAULT_ALPHA
            )
        except ValueError as exc:
            st.warning(f"Statistical test aborted. {exc}")
            return

        _render_result_metrics(result)

        st.divider()
        st.subheader("Interpretation")
        st.markdown(build_interpretation(result))

        st.divider()
        st.subheader("Sales Distribution")
        _render_distribution_chart(result)

    else:
        st.info("Configure cohorts and run the statistical test to see results.")


def main() -> None:
    """Entry point for Module 5."""
    render_page()


if __name__ == "__main__":
    main()
