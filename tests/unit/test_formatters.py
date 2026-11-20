"""Unit tests for the formatting utilities (Increment 2)."""

from app.utils.formatters import (
    format_inr,
    format_kpi_value,
    format_number,
    format_percent,
)


def test_format_inr():
    """Test INR formatting with Indian numbering system."""
    assert format_inr(0) == "₹0.00"
    assert format_inr(1234.56) == "₹1,234.56"
    assert format_inr(123456.78) == "₹1,23,456.78"
    assert format_inr(12345678.9) == "₹1,23,45,678.90"
    assert format_inr(100000000) == "₹10,00,00,000.00"
    assert format_inr(-500.5) == "-₹500.50"
    assert format_inr(None) == "—"


def test_format_percent():
    """Test percentage formatting."""
    assert format_percent(0.1234) == "12.34%"
    assert format_percent(12.34) == "12.34%"
    assert format_percent(1.0) == "100.00%"
    assert format_percent(0) == "0.00%"
    assert format_percent(None) == "—"


def test_format_number():
    """Test number formatting with commas."""
    assert format_number(0) == "0"
    assert format_number(1234) == "1,234"
    assert format_number(123456) == "1,23,456"
    assert format_number(12345678) == "1,23,45,678"
    assert format_number(-500) == "-500"
    assert format_number(None) == "—"


def test_format_kpi_value():
    """Test KPI value semantic formatting."""
    assert format_kpi_value(1234.56, "currency") == "₹1,234.56"
    assert format_kpi_value(1234, "count") == "1,234"
    assert format_kpi_value(0.1234, "percentage") == "12.34%"
    assert format_kpi_value(None, "currency") == "—"
