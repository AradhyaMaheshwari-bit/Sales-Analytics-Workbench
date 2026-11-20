"""Formatting utilities for the Sales Analytics Workbench.

Provides Indian Rupee (INR) currency formatting, percentage formatting,
and comma-separated number formatting for consistent display across
all modules.
"""

from __future__ import annotations


def format_inr(value: float | int | None) -> str:
    """Format a numeric value as Indian Rupee currency string.

    Uses Indian numbering system: lakhs and crores with commas.
    Examples:
        1234.56    -> ₹1,234.56
        123456.78  -> ₹1,23,456.78
        12345678.9 -> ₹1,23,45,678.90
        100000000  -> ₹10,00,00,000.00

    Args:
        value: Numeric value to format. None returns "—".

    Returns:
        Formatted INR string with ₹ symbol and comma groupings.
    """
    if value is None:
        return "—"

    num = float(value)
    if num == 0:
        return "₹0.00"
    if num < 0:
        return f"-{format_inr(-num)}"

    int_part = int(num)
    dec_part = round((num - int_part) * 100)

    s = str(int_part)
    rev = s[::-1]
    groups = [rev[:3]]
    i = 3
    while i < len(rev):
        groups.append(rev[i : i + 2])
        i += 2
    indian_format = ",".join(groups)[::-1]
    return f"₹{indian_format}.{dec_part:02d}"


def format_percent(value: float | int | None, decimals: int = 2) -> str:
    """Format a numeric value as a percentage string.

    Args:
        value: Value between 0 and 100 (or 0 and 1) to format as percentage.
        decimals: Number of decimal places (default 2).

    Returns:
        Formatted percentage string, e.g., "12.34%".
    """
    if value is None:
        return "—"

    num = float(value)

    if abs(num) <= 1:
        num = num * 100

    return f"{num:.{decimals}f}%"


def format_number(value: float | int | None, decimals: int = 0) -> str:
    """Format a numeric value with comma separators (Indian numbering system).

    Args:
        value: Numeric value to format.
        decimals: Number of decimal places (default 0).

    Returns:
        Formatted number string with comma groupings, e.g., "1,23,456".
    """
    if value is None:
        return "—"

    num = float(value)
    if num == 0:
        return "0"
    if num < 0:
        return f"-{format_number(-num, decimals)}"

    if decimals > 0:
        factor = 10**decimals
        rounded = round(num * factor) / factor
        int_part = int(rounded)
        dec_str = f"{rounded:.{decimals}f}".split(".")[1]
    else:
        int_part = int(round(num))
        dec_str = ""

    s = str(int_part)
    rev = s[::-1]
    groups = [rev[:3]]
    i = 3
    while i < len(rev):
        groups.append(rev[i : i + 2])
        i += 2
    indian_format = ",".join(groups)[::-1]
    if decimals > 0:
        return f"{indian_format}.{dec_str}"
    return indian_format


def format_kpi_value(value: float | int | None, value_type: str = "currency") -> str:
    """Format a KPI value based on its semantic type.

    Args:
        value: The numeric value to format.
        value_type: One of "currency", "count", "ratio", "percentage".

    Returns:
        Appropriately formatted string for KPI card display.
    """
    if value is None:
        return "—"

    if value_type == "currency":
        return format_inr(value)
    elif value_type == "count":
        return format_number(value, decimals=0)
    elif value_type == "ratio":
        return format_number(value, decimals=2)
    elif value_type == "percentage":
        return format_percent(value)
    else:
        return str(value)
