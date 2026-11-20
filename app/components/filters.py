"""Filter components for the Sales Analytics Workbench.

Provides reusable filter controls for the EDA dashboard and other modules.
"""

from __future__ import annotations

from typing import Any

import pandas as pd
import streamlit as st


def render_sidebar_filters(df: pd.DataFrame) -> dict[str, Any]:
    """Render sidebar filter controls and return the applied filters.

    Args:
        df: The active DataFrame to filter.

    Returns:
        Dict of filter column -> selected values (list for multi-select,
        tuple for range slider, None if no filter applied).
    """
    if df is None or len(df) == 0:
        st.sidebar.info("No dataset loaded")
        return {}

    st.sidebar.subheader("Filters")
    st.sidebar.caption("Apply filters to update charts and KPIs")

    filters = {}

    # Categorical filters (multi-select)
    categorical_cols = df.select_dtypes(include=["object", "category"]).columns
    for col in categorical_cols:
        unique_vals = sorted(df[col].dropna().unique().tolist())
        if len(unique_vals) > 1 and len(unique_vals) <= 50:
            selected = st.sidebar.multiselect(
                f"{col}",
                options=unique_vals,
                default=unique_vals,
                key=f"filter_{col}",
            )
            if len(selected) < len(unique_vals):
                filters[col] = selected

    # Numeric filters (range slider)
    numeric_cols = df.select_dtypes(
        include=["int64", "float64", "int32", "float32"]
    ).columns
    for col in numeric_cols:
        if col in ("Order_ID", "Customer_ID"):
            continue  # Skip ID columns

        min_val = float(df[col].min())
        max_val = float(df[col].max())
        if min_val == max_val:
            continue

        selected_range = st.sidebar.slider(
            f"{col}",
            min_value=min_val,
            max_value=max_val,
            value=(min_val, max_val),
            key=f"filter_{col}_range",
        )
        if selected_range != (min_val, max_val):
            filters[col] = selected_range

    # Date filter (if Order_Date present)
    if "Order_Date" in df.columns:
        date_series = pd.to_datetime(df["Order_Date"], errors="coerce")
        valid_dates = date_series.dropna()
        if not valid_dates.empty:
            min_date = valid_dates.min().date()
            max_date = valid_dates.max().date()
            if min_date != max_date:
                selected_dates = st.sidebar.date_input(
                    "Order Date Range",
                    value=(min_date, max_date),
                    min_value=min_date,
                    max_value=max_date,
                    key="filter_order_date_range",
                )
                if len(selected_dates) == 2:
                    if selected_dates != (min_date, max_date):
                        filters["Order_Date"] = selected_dates

    # Clear filters button
    if filters and st.sidebar.button("Clear All Filters", key="clear_filters_btn"):
        # Streamlit will rerun with default values
        st.rerun()

    return filters


def apply_filters(df: pd.DataFrame, filters: dict[str, Any]) -> pd.DataFrame:
    """Apply filters to a DataFrame and return a filtered copy.

    Args:
        df: The DataFrame to filter.
        filters: Dict from render_sidebar_filters.

    Returns:
        Filtered DataFrame copy.
    """
    if df is None or len(df) == 0 or not filters:
        return df.copy() if df is not None else pd.DataFrame()

    result = df.copy()

    for col, selected in filters.items():
        if col == "Order_Date" and isinstance(selected, tuple) and len(selected) == 2:
            # Date range filter
            start_date = pd.Timestamp(selected[0])
            end_date = pd.Timestamp(selected[1]) + pd.Timedelta(days=1)
            date_series = pd.to_datetime(result[col], errors="coerce")
            mask = (date_series >= start_date) & (date_series < end_date)
            result = result[mask]
        elif isinstance(selected, list):
            # Categorical multi-select
            result = result[result[col].isin(selected)]
        elif isinstance(selected, tuple) and len(selected) == 2:
            # Numeric range slider
            min_val, max_val = selected
            result = result[(result[col] >= min_val) & (result[col] <= max_val)]

    return result


def render_filter_summary(filters: dict[str, Any]) -> None:
    """Render a summary of active filters in the main area.

    Args:
        filters: Dict from render_sidebar_filters.
    """
    if not filters:
        return

    st.caption("Active filters:")
    cols = st.columns(min(len(filters), 4))
    for i, (col, selected) in enumerate(filters.items()):
        with cols[i % 4]:
            if isinstance(selected, list):
                st.write(f"**{col}:** {len(selected)} selected")
            elif isinstance(selected, tuple):
                st.write(f"**{col}:** {selected[0]:.2f} – {selected[1]:.2f}")
            else:
                st.write(f"**{col}:** {selected}")
