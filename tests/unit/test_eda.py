"""Unit tests for the EDA service layer (Increment 2)."""

import pandas as pd
import pytest
from app.services.eda import (
    aggregate_by_category,
    aggregate_by_city,
    aggregate_by_gender,
    aggregate_by_product,
    aggregate_monthly_trend,
    compute_categorical_summary,
    compute_correlation_matrix,
    compute_kpis,
    compute_numeric_summary,
    get_key_correlation_pairs,
    run_eda_pipeline,
    top_customers,
)


@pytest.fixture
def sample_df():
    """Sample DataFrame for testing."""
    return pd.DataFrame(
        {
            "Order_ID": ["A", "B", "C", "D", "E"],
            "Order_Date": [
                "2024-01-01",
                "2024-01-02",
                "2024-01-03",
                "2024-01-04",
                "2024-01-05",
            ],
            "Customer_ID": ["C1", "C2", "C3", "C4", "C5"],
            "Age": [30, 45, 25, 50, 35],
            "Gender": ["Male", "Female", "Male", "Female", "Male"],
            "City": ["Patna", "Delhi", "Mumbai", "Chennai", "Hyderabad"],
            "Product": ["A", "B", "A", "B", "C"],
            "Category": [
                "Electronics",
                "Furniture",
                "Electronics",
                "Furniture",
                "Electronics",
            ],
            "Quantity": [2, 1, 3, 2, 1],
            "Unit_Price": [100.0, 200.0, 150.0, 100.0, 250.0],
            "Total_Sales": [200.0, 200.0, 450.0, 200.0, 250.0],
        }
    )


def test_compute_kpis():
    """Test KPI calculation with sample data."""
    df = pd.DataFrame(
        {
            "Order_ID": ["A", "B", "C"],
            "Total_Sales": [200.0, 200.0, 450.0],
            "Quantity": [2, 1, 3],
        }
    )
    kpis = compute_kpis(df)
    assert kpis["total_revenue"] == 850.0
    assert kpis["total_orders"] == 3
    assert kpis["avg_order_value"] == pytest.approx(283.33, 0.01)
    assert kpis["total_quantity"] == 6


def test_compute_numeric_summary():
    """Test numeric summary computation."""
    df = pd.DataFrame(
        {
            "A": [1, 2, 3, 4, 5],
            "B": [10, 20, 30, 40, 50],
        }
    )
    numeric_summary = compute_numeric_summary(df)
    assert numeric_summary.shape == (9, 2)  # 9 statistics rows, 2 columns (A, B)
    assert numeric_summary.loc["count", "A"] == 5
    assert numeric_summary.loc["mean", "A"] == 3.0
    assert numeric_summary.loc["std", "A"] == pytest.approx(1.5811, abs=0.0001)


def test_compute_categorical_summary():
    """Test categorical summary computation."""
    df = pd.DataFrame(
        {
            "Category": ["A", "B", "A", "C", "B", "A"],
            "City": ["X", "Y", "X", "Y", "X", "Z"],
        }
    )
    summary = compute_categorical_summary(df)
    assert "Category" in summary
    assert "City" in summary
    assert len(summary["Category"]) == 3  # A, B, C
    assert len(summary["City"]) == 3  # X, Y, Z


def test_compute_correlation_matrix():
    """Test correlation matrix computation."""
    df = pd.DataFrame(
        {
            "X": [1, 2, 3, 4, 5],
            "Y": [2, 4, 6, 8, 10],
            "Z": [5, 4, 3, 2, 1],
        }
    )
    corr = compute_correlation_matrix(df, "pearson")
    assert corr.shape == (3, 3)
    assert corr.loc["X", "Y"] == 1.0  # perfect positive


def test_get_key_correlation_pairs():
    """Test correlation pair extraction."""
    df = pd.DataFrame(
        {
            "A": [1.0, 2.0, 3.0, 4.0],
            "B": [2.0, 4.0, 6.0, 8.0],  # perfect positive with A
            "C": [5.0, 4.0, 3.0, 2.0],  # perfect negative with A
        }
    )
    pos, neg = get_key_correlation_pairs(df, top_n=1)
    assert len(pos) == 1
    assert len(neg) == 1
    assert pos[0][0] == "A"
    assert pos[0][1] == "B"
    assert pos[0][2] == pytest.approx(1.0)
    assert neg[0][2] == pytest.approx(-1.0)


def test_run_eda_pipeline():
    """Test the complete EDA pipeline."""
    df = pd.DataFrame(
        {
            "Order_ID": ["A", "B", "C"],
            "Total_Sales": [200.0, 200.0, 450.0],
            "Order_Date": ["2024-01-01", "2024-01-02", "2024-01-03"],
        }
    )
    result = run_eda_pipeline(df)

    # Check KPIs
    assert "kpis" in result
    assert result["kpis"]["total_revenue"] == 850.0

    # Check numeric summary
    assert "numeric_summary" in result
    assert result["numeric_summary"].shape[0] == 9  # 9 statistics rows
    assert "Total_Sales" in result["numeric_summary"].columns

    # Check categorical summary
    assert "categorical_summary" in result

    # Check correlation matrix
    assert "correlation_matrix" in result
    assert isinstance(result["correlation_matrix"], pd.DataFrame)

    # Check top correlations
    assert "top_positive_corr" in result
    assert "top_negative_corr" in result

    # Check grouped aggregations
    assert "by_category" in result
    assert "by_city" in result
    assert "by_product" in result


def test_eda_pipeline_empty_dataframe():
    """Test EDA pipeline with empty DataFrame."""
    df = pd.DataFrame()
    result = run_eda_pipeline(df)
    assert "kpis" in result
    assert result["kpis"]["total_revenue"] == 0.0
    assert result["kpis"]["total_orders"] == 0
    assert result["kpis"]["avg_order_value"] == 0.0
    assert result["kpis"]["total_quantity"] == 0
    assert result["numeric_summary"].empty


def test_eda_pipeline_missing_required_columns():
    """Test EDA pipeline with custom columns."""
    df = pd.DataFrame({"A": [1, 2], "B": [3, 4]})
    result = run_eda_pipeline(df)
    assert "numeric_summary" in result
    assert result["numeric_summary"].shape[1] == 2  # Computes summary for A and B


# Test aggregate functions
def test_aggregate_by_category():
    df = pd.DataFrame(
        {
            "Category": ["Electronics", "Furniture", "Electronics", "Furniture"],
            "Total_Sales": [200, 100, 300, 150],
        }
    )
    result = aggregate_by_category(df, "Category", "Total_Sales")
    assert len(result) == 2
    assert result.iloc[0]["Category"] == "Electronics"
    assert result.iloc[0]["Total_Sales"] == 500
    assert result.iloc[1]["Category"] == "Furniture"
    assert result.iloc[1]["Total_Sales"] == 250


def test_aggregate_by_city():
    df = pd.DataFrame(
        {
            "City": ["Patna", "Delhi", "Patna", "Mumbai"],
            "Total_Sales": [100, 150, 300, 100],
        }
    )
    result = aggregate_by_city(df, "City", "Total_Sales")
    assert len(result) == 3
    assert result.iloc[0]["City"] == "Patna"
    assert result.iloc[0]["Total_Sales"] == 400


def test_aggregate_by_product():
    df = pd.DataFrame(
        {
            "Product": ["A", "B", "A", "B", "C"],
            "Total_Sales": [200, 150, 300, 100, 250],
        }
    )
    result = aggregate_by_product(df, "Product", "Total_Sales", top_n=2)
    assert len(result) == 2
    assert result.iloc[0]["Product"] == "A"
    assert result.iloc[0]["Total_Sales"] == 500


def test_aggregate_monthly_trend():
    df = pd.DataFrame(
        {
            "Order_Date": ["2024-01-01", "2024-01-15", "2024-02-01", "2024-02-15"],
            "Total_Sales": [100, 150, 200, 250],
        }
    )
    result = aggregate_monthly_trend(df, "Order_Date", "Total_Sales")
    assert len(result) == 2
    assert result.iloc[0]["Month"] == "2024-01"
    assert result.iloc[0]["Total_Sales"] == 250
    assert result.iloc[1]["Month"] == "2024-02"
    assert result.iloc[1]["Total_Sales"] == 450


def test_aggregate_by_gender():
    df = pd.DataFrame(
        {
            "Gender": ["Male", "Female", "Male", "Female"],
            "Total_Sales": [200, 150, 200, 150],
        }
    )
    result = aggregate_by_gender(df, "Gender", "Total_Sales")
    assert len(result) == 2
    assert result.iloc[0]["Gender"] == "Male"
    assert result.iloc[0]["Total_Sales"] == 400


def test_top_customers():
    df = pd.DataFrame(
        {
            "Customer_Name": ["Alice", "Bob", "Bob", "Charlie", "Alice"],
            "Total_Sales": [100, 150, 150, 200, 100],
        }
    )
    result = top_customers(df, "Customer_Name", "Total_Sales", top_n=2)
    assert len(result) == 2
    assert result.iloc[0]["Customer_Name"] == "Bob"
    assert result.iloc[0]["Total_Sales"] == 300
    assert result.iloc[1]["Customer_Name"] == "Alice"
    assert result.iloc[1]["Total_Sales"] == 200
