"""Module 2 — EDA & BI Dashboard.

Displays exploratory data analysis including KPI cards, interactive Plotly charts,
descriptive statistics, correlation matrix, and filtering controls.

All logic is in services/eda.py and components; this page handles UI composition.
"""

import pandas as pd
import streamlit as st

from app.components.filters import apply_filters, render_sidebar_filters
from app.components.kpi_cards import create_kpi_data, render_kpi_row
from app.services.eda import (
    aggregate_monthly_trend,
    compute_correlation_matrix,
    compute_kpis,
    run_eda_pipeline,
)
from app.utils.charts import ChartFactory

# Initialize ChartFactory
chart_factory = ChartFactory()


def _check_data_loaded() -> bool:
    """Check if a valid dataset is loaded for analysis."""
    if (
        st.session_state.get("active_df") is None
        or len(st.session_state.get("active_df", pd.DataFrame())) == 0
    ):
        st.info("No dataset loaded. Upload a file or enable Demo Mode in Module 1.")
        return False
    return True


def _check_analysis_ready() -> bool:
    """Check if dataset has required columns for analysis."""
    df = st.session_state.get("active_df", pd.DataFrame())
    required = ["Total_Sales", "Order_Date"]  # Minimum required for meaningful analysis
    missing = [col for col in required if col not in df.columns]
    if missing:
        st.warning(f"Missing required columns for analysis: {missing}")
        return False
    return True


def _missing_columns(df: pd.DataFrame, *columns: str) -> list[str]:
    """Return the subset of *columns* absent from *df* (FR-11 AC-4: never crash)."""
    return [col for col in columns if col not in df.columns]


def _render_kpi_section() -> None:
    """Render KPI cards in a row at the top of the dashboard."""
    if not _check_data_loaded():
        return

    df = st.session_state["active_df"]
    kpis = create_kpi_data(
        total_revenue=df["Total_Sales"].sum(),
        total_orders=(
            len(df["Order_ID"].unique()) if "Order_ID" in df.columns else len(df)
        ),
        avg_order_value=compute_kpis(df)["avg_order_value"],
        total_quantity=df["Quantity"].sum() if "Quantity" in df.columns else 0,
    )
    render_kpi_row(kpis, columns=4)


def _render_chart_grid() -> None:
    """Render the main chart grid with 4 Plotly charts."""
    if not _check_data_loaded() or not _check_analysis_ready():
        return

    df = st.session_state["active_df"]
    st.subheader("Interactive Charts")

    # 1. Revenue by Category (Bar)
    if missing := _missing_columns(df, "Category"):
        st.info(f"Cannot render 'Revenue by Category' — missing columns: {missing}")
    else:
        fig1 = chart_factory.bar_chart(
            df,
            x="Category",
            y="Total_Sales",
            title="Revenue by Category",
            yaxis_title="Revenue (₹)",
            y_is_currency=True,
        )
        st.plotly_chart(fig1, use_container_width=True)

    # 2. Monthly Revenue Trend (Line)
    monthly_trend = aggregate_monthly_trend(df)
    if monthly_trend.empty:
        st.info("Monthly Revenue Trend unavailable — no parseable Order_Date values.")
    else:
        fig2 = chart_factory.line_chart(
            monthly_trend,
            x="Month",
            y="Total_Sales",
            title="Monthly Revenue Trend",
            yaxis_title="Revenue (₹)",
            y_is_currency=True,
        )
        st.plotly_chart(fig2, use_container_width=True)

    # 3. Revenue by City (Horizontal Bar)
    if missing := _missing_columns(df, "City"):
        st.info(f"Cannot render 'Revenue by City' — missing columns: {missing}")
    else:
        fig3 = chart_factory.bar_chart(
            df,
            x="City",
            y="Total_Sales",
            title="Revenue by City",
            xaxis_title="City",
            yaxis_title="Revenue (₹)",
            y_is_currency=True,
            orientation="h",
        )
        st.plotly_chart(fig3, use_container_width=True)

    # 4. Correlation Matrix (Heatmap)
    corr_matrix = compute_correlation_matrix(df)
    if corr_matrix.empty:
        st.info("Correlation matrix requires at least two numeric columns.")
    else:
        fig4 = chart_factory.correlation_heatmap(
            corr_matrix,
            title="Correlation Matrix",
        )
        st.plotly_chart(fig4, use_container_width=True)


def _render_filtering_section() -> None:
    """Render filtering controls and apply them to the dataset."""
    st.subheader("Filter Controls")

    filters = render_sidebar_filters(st.session_state.get("active_df", pd.DataFrame()))

    if filters:
        st.subheader("Filtered View")
        filtered_df = apply_filters(st.session_state["active_df"], filters)
        # Update session state to use filtered data
        st.session_state["active_df"] = filtered_df
        # Re-render the chart grid with filtered data
        _render_chart_grid()
    else:
        st.subheader("All Data")
        # Ensure active_df is the unfiltered dataset
        st.session_state["active_df"] = st.session_state.get(
            "active_df", pd.DataFrame()
        )


def _render_statistics_section() -> None:
    """Render descriptive statistics and frequency tables."""
    if not _check_data_loaded() or not _check_analysis_ready():
        return

    df = st.session_state["active_df"]
    stats = run_eda_pipeline(df)

    st.subheader("Descriptive Statistics")
    numeric_summary = stats["numeric_summary"]
    if not numeric_summary.empty:
        st.dataframe(numeric_summary, use_container_width=True)

    categorical_summary = stats["categorical_summary"]
    for col, freq_df in categorical_summary.items():
        if not freq_df.empty:
            st.subheader(f"Column: {col}")
            st.dataframe(freq_df, use_container_width=True)


def _render_top_insights() -> None:
    """Show key insights including correlation pairs and top customers."""
    if not _check_data_loaded() or not _check_analysis_ready():
        return

    stats = run_eda_pipeline(st.session_state["active_df"])
    top_positive = stats["top_positive_corr"]
    top_negative = stats["top_negative_corr"]

    if top_positive:
        st.subheader("Strong Positive Correlations")
        for col1, col2, corr in top_positive:
            st.metric(f"{col1} ↔ {col2}", f"{corr:.3f}", delta=f"{corr:.3f}")

    if top_negative:
        st.subheader("Strong Negative Correlations")
        for col1, col2, corr in top_negative:
            st.metric(f"{col1} ↔ {col2}", f"{corr:.3f}", delta=f"{corr:.3f}")


def main() -> None:
    """Main application entry point for Module 2."""
    st.set_page_config(
        page_title="EDA & BI Dashboard",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Page header
    st.title("Module 2 — EDA & Business Intelligence")
    st.divider()

    # KPI Row
    _render_kpi_section()

    # Main Content
    col1, col2 = st.columns([2, 1])
    with col1:
        _render_chart_grid()
        _render_statistics_section()
        _render_top_insights()
    with col2:
        _render_filtering_section()


if __name__ == "__main__":
    main()
