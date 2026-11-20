"""Exploratory Data Analysis service for the Sales Analytics Workbench.

Provides pure functions for descriptive statistics, correlation analysis,
frequency tables, and grouping aggregations. All functions accept a
DataFrame and return new DataFrames or dicts — no mutation, no Streamlit.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Numerical Summaries
# ---------------------------------------------------------------------------


def compute_numeric_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Compute descriptive statistics for all numeric columns.

    Returns a DataFrame with rows: count, mean, std, min, 25%, 50%, 75%, max, IQR.
    Matches pandas.DataFrame.describe() output plus IQR.

    Args:
        df: Input DataFrame.

    Returns:
        DataFrame with statistics as rows and numeric columns as columns.
    """
    # Select only numeric columns
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    if len(numeric_cols) == 0:
        return pd.DataFrame()

    # Use pandas describe with percentiles
    stats = df[numeric_cols].describe(percentiles=[0.25, 0.5, 0.75])

    # Add IQR row
    iqr = stats.loc["75%"] - stats.loc["25%"]
    iqr.name = "IQR"
    stats = pd.concat([stats, pd.DataFrame([iqr], index=["IQR"])])

    # Round for display
    return stats.round(4)


def compute_categorical_summary(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Compute frequency tables for all categorical/object columns.

    Args:
        df: Input DataFrame.

    Returns:
        Dict mapping column name -> frequency DataFrame with columns
        [value, count, percentage].
    """
    categorical_cols = df.select_dtypes(include=["object", "category"]).columns
    result = {}

    for col in categorical_cols:
        vc = df[col].value_counts(dropna=False)
        pct = df[col].value_counts(normalize=True, dropna=False) * 100
        freq_df = pd.DataFrame(
            {
                "value": vc.index.astype(str),
                "count": vc.values,
                "percentage": pct.values.round(2),
            }
        )
        result[col] = freq_df

    return result


def compute_correlation_matrix(
    df: pd.DataFrame,
    method: str = "pearson",
) -> pd.DataFrame:
    """Compute correlation matrix for numeric columns.

    Args:
        df: Input DataFrame.
        method: Correlation method ('pearson', 'spearman', 'kendall').

    Returns:
        Square correlation matrix DataFrame.
    """
    numeric_df = df.select_dtypes(include=[np.number])
    if numeric_df.shape[1] < 2:
        return pd.DataFrame()

    corr = numeric_df.corr(method=method)
    return corr.round(4)


def get_key_correlation_pairs(
    df: pd.DataFrame,
    top_n: int = 3,
    method: str = "pearson",
) -> tuple[list[tuple[str, str, float]], list[tuple[str, str, float]]]:
    """Get top positive and negative correlation pairs.

    Args:
        df: Input DataFrame.
        top_n: Number of pairs to return.
        method: Correlation method.

    Returns:
        Tuple of (top_positive_pairs, top_negative_pairs), each a list of
        (col1, col2, correlation) sorted by absolute correlation descending.
    """
    corr = compute_correlation_matrix(df, method)
    if corr.empty:
        return [], []

    # Get upper triangle (excluding diagonal)
    mask = np.triu(np.ones(corr.shape), k=1).astype(bool)
    pairs = corr.where(mask).stack().reset_index()
    pairs.columns = ["col1", "col2", "correlation"]

    # Sort by correlation value
    pairs = pairs.sort_values("correlation", ascending=False)

    # Top positive
    pos = pairs.nlargest(top_n, "correlation")
    # Top negative
    neg = pairs.nsmallest(top_n, "correlation")

    return (
        [(row.col1, row.col2, row.correlation) for _, row in pos.iterrows()],
        [(row.col1, row.col2, row.correlation) for _, row in neg.iterrows()],
    )


# ---------------------------------------------------------------------------
# Grouping Aggregations
# ---------------------------------------------------------------------------


def aggregate_by_category(
    df: pd.DataFrame,
    category_col: str = "Category",
    value_col: str = "Total_Sales",
) -> pd.DataFrame:
    """Aggregate revenue by category, sorted descending.

    Args:
        df: Input DataFrame.
        category_col: Column to group by.
        value_col: Numeric column to sum.

    Returns:
        DataFrame with columns [category_col, value_col] sorted by value_col desc.
    """
    if category_col not in df.columns or value_col not in df.columns:
        return pd.DataFrame(columns=[category_col, value_col])

    result = (
        df.groupby(category_col, as_index=False)[value_col]
        .sum()
        .sort_values(value_col, ascending=False)
    )
    return result


def aggregate_by_city(
    df: pd.DataFrame,
    city_col: str = "City",
    value_col: str = "Total_Sales",
) -> pd.DataFrame:
    """Aggregate revenue by city, sorted descending.

    Args:
        df: Input DataFrame.
        city_col: Column to group by.
        value_col: Numeric column to sum.

    Returns:
        DataFrame with columns [city_col, value_col] sorted by value_col desc.
    """
    if city_col not in df.columns or value_col not in df.columns:
        return pd.DataFrame(columns=[city_col, value_col])

    result = (
        df.groupby(city_col, as_index=False)[value_col]
        .sum()
        .sort_values(value_col, ascending=False)
    )
    return result


def aggregate_by_product(
    df: pd.DataFrame,
    product_col: str = "Product",
    value_col: str = "Total_Sales",
    top_n: int | None = None,
) -> pd.DataFrame:
    """Aggregate revenue by product, sorted descending.

    Args:
        df: Input DataFrame.
        product_col: Column to group by.
        value_col: Numeric column to sum.
        top_n: Optional limit to top N products.

    Returns:
        DataFrame with columns [product_col, value_col] sorted by value_col desc.
    """
    if product_col not in df.columns or value_col not in df.columns:
        return pd.DataFrame(columns=[product_col, value_col])

    result = (
        df.groupby(product_col, as_index=False)[value_col]
        .sum()
        .sort_values(value_col, ascending=False)
    )
    if top_n:
        result = result.head(top_n)
    return result


def aggregate_monthly_trend(
    df: pd.DataFrame,
    date_col: str = "Order_Date",
    value_col: str = "Total_Sales",
) -> pd.DataFrame:
    """Aggregate revenue by month from Order_Date.

    Expects date_col to be in ISO format (YYYY-MM-DD) or parseable.

    Args:
        df: Input DataFrame.
        date_col: Date column name.
        value_col: Numeric column to sum.

    Returns:
        DataFrame with columns [Month, value_col] sorted by Month asc.
    """
    if date_col not in df.columns or value_col not in df.columns:
        return pd.DataFrame(columns=["Month", value_col])

    # Work on a copy to avoid mutating
    df_copy = df[[date_col, value_col]].copy()

    # Parse dates, coerce invalid to NaT
    df_copy[date_col] = pd.to_datetime(df_copy[date_col], errors="coerce")

    # Drop rows where date is NaT (NULL dates)
    df_copy = df_copy.dropna(subset=[date_col])

    if df_copy.empty:
        return pd.DataFrame(columns=["Month", value_col])

    # Extract year-month
    df_copy["Month"] = df_copy[date_col].dt.strftime("%Y-%m")

    # Aggregate
    result = (
        df_copy.groupby("Month", as_index=False)[value_col].sum().sort_values("Month")
    )
    return result


def aggregate_by_gender(
    df: pd.DataFrame,
    gender_col: str = "Gender",
    value_col: str = "Total_Sales",
) -> pd.DataFrame:
    """Aggregate revenue by gender.

    Args:
        df: Input DataFrame.
        gender_col: Column to group by.
        value_col: Numeric column to sum.

    Returns:
        DataFrame with columns [gender_col, value_col].
    """
    if gender_col not in df.columns or value_col not in df.columns:
        return pd.DataFrame(columns=[gender_col, value_col])

    result = (
        df.groupby(gender_col, as_index=False)[value_col]
        .sum()
        .sort_values(value_col, ascending=False)
    )
    return result


def top_customers(
    df: pd.DataFrame,
    customer_col: str = "Customer_Name",
    value_col: str = "Total_Sales",
    top_n: int = 10,
) -> pd.DataFrame:
    """Get top N customers by revenue.

    Args:
        df: Input DataFrame.
        customer_col: Customer identifier column.
        value_col: Numeric column to sum.
        top_n: Number of top customers to return.

    Returns:
        DataFrame with columns [customer_col, value_col] sorted desc, limited to top_n.
    """
    if customer_col not in df.columns or value_col not in df.columns:
        return pd.DataFrame(columns=[customer_col, value_col])

    result = (
        df.groupby(customer_col, as_index=False)[value_col]
        .sum()
        .sort_values(value_col, ascending=False)
        .head(top_n)
    )
    return result


# ---------------------------------------------------------------------------
# KPI Calculations
# ---------------------------------------------------------------------------


def compute_kpis(df: pd.DataFrame) -> dict[str, float | int]:
    """Compute executive KPI values from the active DataFrame.

    Returns:
        Dict with keys:
        - total_revenue: sum of Total_Sales
        - total_orders: count of unique Order_ID
        - avg_order_value: total_revenue / total_orders
        - total_quantity: sum of Quantity
    """
    if df is None or len(df) == 0:
        return {
            "total_revenue": 0.0,
            "total_orders": 0,
            "avg_order_value": 0.0,
            "total_quantity": 0,
        }

    total_revenue = (
        float(df["Total_Sales"].sum()) if "Total_Sales" in df.columns else 0.0
    )
    total_orders = (
        int(df["Order_ID"].nunique()) if "Order_ID" in df.columns else len(df)
    )
    total_quantity = int(df["Quantity"].sum()) if "Quantity" in df.columns else 0
    avg_order_value = total_revenue / total_orders if total_orders > 0 else 0.0

    return {
        "total_revenue": total_revenue,
        "total_orders": total_orders,
        "avg_order_value": avg_order_value,
        "total_quantity": total_quantity,
    }


# ---------------------------------------------------------------------------
# Complete EDA Profile
# ---------------------------------------------------------------------------


def run_eda_pipeline(df: pd.DataFrame) -> dict[str, Any]:
    """Run the complete EDA pipeline and return all results.

    Args:
        df: The active (cleaned) DataFrame.

    Returns:
        Dict containing all EDA results keyed by analysis type.
    """
    if df is None or len(df) == 0:
        return {
            "kpis": compute_kpis(df),
            "numeric_summary": pd.DataFrame(),
            "categorical_summary": {},
            "correlation_matrix": pd.DataFrame(),
            "top_positive_corr": [],
            "top_negative_corr": [],
            "by_category": pd.DataFrame(),
            "by_city": pd.DataFrame(),
            "by_product": pd.DataFrame(),
            "monthly_trend": pd.DataFrame(),
            "by_gender": pd.DataFrame(),
            "top_customers": pd.DataFrame(),
        }

    return {
        "kpis": compute_kpis(df),
        "numeric_summary": compute_numeric_summary(df),
        "categorical_summary": compute_categorical_summary(df),
        "correlation_matrix": compute_correlation_matrix(df),
        "top_positive_corr": get_key_correlation_pairs(df)[0],
        "top_negative_corr": get_key_correlation_pairs(df)[1],
        "by_category": aggregate_by_category(df),
        "by_city": aggregate_by_city(df),
        "by_product": aggregate_by_product(df),
        "monthly_trend": aggregate_monthly_trend(df),
        "by_gender": aggregate_by_gender(df),
        "top_customers": top_customers(df),
    }
