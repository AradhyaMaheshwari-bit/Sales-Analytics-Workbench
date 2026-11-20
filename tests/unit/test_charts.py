"""Unit tests for the centralized Plotly chart factory (Increment 2)."""

import pandas as pd
import plotly.graph_objects as go
import pytest
from app.utils.charts import ChartFactory


@pytest.fixture
def factory():
    return ChartFactory()


@pytest.fixture
def sample_df():
    return pd.DataFrame(
        {
            "Category": ["Electronics", "Furniture", "Clothing"],
            "Revenue": [1000.0, 500.0, 750.0],
            "Month": ["2024-01", "2024-02", "2024-03"],
            "City": ["Patna", "Delhi", "Mumbai"],
        }
    )


def test_bar_chart_returns_figure(factory, sample_df):
    """Test bar chart creation returns a valid Plotly Figure."""
    fig = factory.bar_chart(
        sample_df,
        x="Category",
        y="Revenue",
        title="Revenue by Category",
    )
    assert isinstance(fig, go.Figure)
    assert fig.layout.title.text == "Revenue by Category"
    assert fig.layout.template.layout.paper_bgcolor == "#0B132B"


def test_line_chart_returns_figure(factory, sample_df):
    """Test line chart creation returns a valid Plotly Figure."""
    fig = factory.line_chart(
        sample_df,
        x="Month",
        y="Revenue",
        title="Monthly Revenue Trend",
    )
    assert isinstance(fig, go.Figure)
    assert fig.layout.title.text == "Monthly Revenue Trend"


def test_correlation_heatmap_returns_figure(factory):
    """Test correlation heatmap creation."""
    corr_df = pd.DataFrame(
        {
            "A": [1.0, 0.5],
            "B": [0.5, 1.0],
        },
        index=["A", "B"],
    )
    fig = factory.correlation_heatmap(corr_df, title="Correlation Matrix")
    assert isinstance(fig, go.Figure)
    assert fig.layout.title.text == "Correlation Matrix"


def test_pie_chart_returns_figure(factory, sample_df):
    """Test pie chart creation."""
    fig = factory.pie_chart(
        sample_df,
        values="Revenue",
        names="Category",
        title="Revenue Share",
    )
    assert isinstance(fig, go.Figure)
    assert fig.layout.title.text == "Revenue Share"
