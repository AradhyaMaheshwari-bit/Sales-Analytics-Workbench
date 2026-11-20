"""Tables component for the Sales Analytics Workbench.

Provides reusable, styled data tables with pagination, formatting,
and responsive layout for displaying analysis results.
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

from app.utils.formatters import format_inr


def render_dataframe_table(
    df: pd.DataFrame,
    title: str | None = None,
    page_size: int = 10,
    show_index: bool = False,
    format_column: dict[str, str] | None = None,
) -> None:
    """Render a styled Streamlit dataframe with optional title and formatting.

    Args:
        df: DataFrame to display.
        title: Optional title for the table.
        page_size: Number of rows per page (default 10).
        show_index: Whether to show DataFrame index (default False).
        format_column: Dict mapping column names to formatting strings (e.g., "₹#,##0.00").
    """
    if df.empty:
        st.info("No data to display.")
        return

    if title:
        st.subheader(title)

    # Apply column formatting if specified
    if format_column:
        formatted_df = df.copy()
        for col, fmt in format_column.items():
            if col in formatted_df.columns:
                if fmt == "₹":
                    # Format as Indian Rupee with commas and 2 decimals
                    formatted_df[col] = formatted_df[col].apply(
                        lambda x: format_inr(x) if pd.notna(x) else "—"
                    )
                elif fmt == "percent":
                    formatted_df[col] = formatted_df[col].apply(
                        lambda x: f"{x:.2%}" if pd.notna(x) else "—"
                    )
                elif fmt == "comma":
                    formatted_df[col] = formatted_df[col].apply(
                        lambda x: f"{x:,}" if pd.notna(x) else "—"
                    )
                elif fmt == "int":
                    formatted_df[col] = formatted_df[col].apply(
                        lambda x: str(int(x)) if pd.notna(x) else "—"
                    )
                elif fmt == "currency":
                    formatted_df[col] = formatted_df[col].apply(
                        lambda x: format_inr(x) if pd.notna(x) else "—"
                    )
                # Add more formatters as needed

    # Render the table
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=not show_index,
        column_config={
            col: st.column_config.TextColumn(
                col,
                help=fmt,
                format=fmt,
                width=None,
            )
            for col, fmt in (format_column or {}).items()
        },
    )


def render_paginated_table(
    df: pd.DataFrame,
    title: str | None = None,
    page_size: int = 10,
    show_index: bool = False,
    format_column: dict[str, str] | None = None,
) -> None:
    """Render a paginated table with navigation controls."""
    if df.empty:
        st.info("No data to display.")
        return

    if title:
        st.subheader(title)

    # Calculate pagination
    total_rows = len(df)
    num_pages = (total_rows + page_size - 1) // page_size

    # Pagination controls
    page_num = st.session_state.get("eda_page_num", 0)
    st.write(f"Page {page_num + 1} of {num_pages}")

    # Pagination controls
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if page_num > 0:
            if st.button("← Previous", key=f"prev_page_{page_num}"):
                st.session_state["eda_page_num"] = page_num - 1
                st.experimental_rerun()
        else:
            st.disabled("← Previous")
    with col2:
        st.selectbox(
            "Go to page",
            options=list(range(num_pages)),
            format_func=lambda x: f"{x + 1}",
            key=f"page_selector_{page_num}",
        )
        if st.button("Go", key=f"go_page_{page_num}"):
            st.session_state["eda_page_num"] = st.session_state[
                f"page_selector_{page_num}"
            ]
            st.experimental_rerun()
    with col3:
        if page_num < num_pages - 1:
            if st.button("Next →", key=f"next_page_{page_num}"):
                st.session_state["eda_page_num"] = page_num + 1
                st.experimental_rerun()
        else:
            st.disabled("Next →")

    # Slice the data
    start_idx = page_num * page_size
    end_idx = start_idx + page_size
    page_df = df.iloc[start_idx:end_idx]

    # Apply formatting if specified
    if format_column:
        page_df = page_df.copy()
        for col, fmt in format_column.items():
            if col in page_df.columns:
                if fmt == "₹":
                    page_df[col] = page_df[col].apply(
                        lambda x: format_inr(x) if pd.notna(x) else "—"
                    )
                elif fmt == "currency":
                    page_df[col] = page_df[col].apply(
                        lambda x: format_inr(x) if pd.notna(x) else "—"
                    )
                elif fmt == "comma":
                    page_df[col] = page_df[col].apply(
                        lambda x: f"{x:,}" if pd.notna(x) else "—"
                    )
                elif fmt == "percent":
                    page_df[col] = page_df[col].apply(
                        lambda x: f"{x:.2%}" if pd.notna(x) else "—"
                    )
                elif fmt == "int":
                    page_df[col] = page_df[col].apply(
                        lambda x: str(int(x)) if pd.notna(x) else "—"
                    )

    st.dataframe(
        page_df,
        use_container_width=True,
        hide_index=not show_index,
        column_config={
            col: st.column_config.TextColumn(
                col,
                help=fmt,
                format=fmt,
                width=None,
            )
            for col, fmt in (format_column or {}).items()
        },
    )


def render_paginated_kpi_table(
    kpis: list[dict],
    title: str | None = None,
    page_size: int = 4,
) -> None:
    """Render KPIs in a paginated table format."""
    if not kpis:
        return

    cols = st.columns(4)
    for i, kpi in enumerate(kpis):
        with cols[i % 4]:
            st.metric(
                label=kpi["title"],
                value=kpi["value"],
                delta=kpi.get("delta", ""),
                delta_color=kpi.get("delta_color", "normal"),
            )
