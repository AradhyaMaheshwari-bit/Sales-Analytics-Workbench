"""KPI Card components for the Sales Analytics Workbench.

Provides standardized executive metric cards with consistent styling
matching the dark navy executive theme.
"""

from __future__ import annotations

import streamlit as st


def render_kpi_card(
    title: str,
    value: str,
    delta: str | None = None,
    delta_color: str = "normal",
    icon: str | None = None,
    help_text: str | None = None,
) -> None:
    """Render a single KPI metric card using Streamlit's metric widget.

    Args:
        title: The metric label/title.
        value: The formatted metric value (e.g., "₹1,41,807.34").
        delta: Optional delta indicator (e.g., "+12.5%" or "-₹5,000").
        delta_color: "normal" (green for positive), "inverse" (red for positive), "off" (no color).
        icon: Optional emoji/icon string.
        help_text: Optional tooltip text on hover.
    """
    st.metric(
        label=title,
        value=value,
        delta=delta,
        delta_color=delta_color,
        help=help_text,
    )


def render_kpi_row(
    kpis: list[dict],
    columns: int = 4,
) -> None:
    """Render a row of KPI cards in a responsive grid.

    Args:
        kpis: List of dicts with keys: title, value, delta (optional), delta_color (optional), icon (optional), help (optional).
        columns: Number of columns in the grid (default 4).
    """
    cols = st.columns(columns)
    for i, kpi in enumerate(kpis):
        with cols[i % columns]:
            render_kpi_card(
                title=kpi.get("title", ""),
                value=kpi.get("value", "—"),
                delta=kpi.get("delta"),
                delta_color=kpi.get("delta_color", "normal"),
                icon=kpi.get("icon"),
                help_text=kpi.get("help"),
            )


def create_kpi_data(
    total_revenue: float,
    total_orders: int,
    avg_order_value: float,
    total_quantity: int,
) -> list[dict]:
    """Create standardized KPI data from computed values.

    Args:
        total_revenue: Sum of Total_Sales.
        total_orders: Count of unique orders.
        avg_order_value: Average revenue per order.
        total_quantity: Sum of Quantity.

    Returns:
        List of KPI dicts ready for render_kpi_row.
    """
    from app.utils.formatters import format_inr, format_number

    return [
        {
            "title": "Total Revenue",
            "value": format_inr(total_revenue),
            "help": "Sum of all Total_Sales in the active dataset",
        },
        {
            "title": "Total Orders",
            "value": format_number(total_orders),
            "help": "Count of unique Order_ID values",
        },
        {
            "title": "Avg Order Value",
            "value": format_inr(avg_order_value),
            "help": "Total Revenue / Total Orders",
        },
        {
            "title": "Total Quantity",
            "value": format_number(total_quantity),
            "help": "Sum of all Quantity values",
        },
    ]
