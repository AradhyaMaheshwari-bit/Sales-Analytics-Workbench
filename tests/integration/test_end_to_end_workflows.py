"""End-to-end integration and QA tests for the Sales Analytics Workbench.

Covers cross-layer continuity, data ingestion, cleaning pipelines, SQLite database
lifecycle and security authorizer, predefined and custom SQL execution, EDA and KPI
aggregations, statistical hypothesis testing, and headless AppTest page smoke flows.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest
from app.database.db_manager import DatabaseManager, get_db_manager
from app.database.queries import (
    APPROVED_QUERIES,
    execute_custom_query,
    execute_predefined_query,
)
from app.services.cleaner import clean_dataframe
from app.services.data_loader import DataLoader
from app.services.eda import compute_kpis, run_eda_pipeline
from app.services.statistics import prepare_comparison_frame, run_gender_comparison
from scipy import stats
from scripts.generate_demo_data import generate_and_save

try:
    from streamlit.testing.v1 import AppTest
except ImportError:
    AppTest = None


@pytest.fixture
def sample_demo_file(tmp_path) -> Path:
    """Generate a deterministic synthetic demo file in an isolated temp directory."""
    target = tmp_path / "synthetic_demo_dataset.xlsx"
    generate_and_save(target)
    return target


def test_load_file_bytes_supported(sample_demo_file: Path) -> None:
    """I-1: DataLoader.load_file accepts raw bytes and returns valid DataLoadResult."""
    raw_bytes = sample_demo_file.read_bytes()
    loader = DataLoader()
    result = loader.load_file(
        raw_bytes, file_name="synthetic_demo_dataset.xlsx", file_type="xlsx"
    )
    assert result.success
    assert result.dataframe is not None
    assert len(result.dataframe) == 60
    assert result.schema_report is not None


def test_cleaning_log_counts_and_invalid_date_behavior(sample_demo_file: Path) -> None:
    """I-2: Cleaning pipeline logs record correct row counts and preserve invalid dates as NULL."""
    df = pd.read_excel(sample_demo_file, engine="openpyxl")
    df.loc[0, "Order_Date"] = "not-a-date"
    df.loc[1, "Quantity"] = None

    cleaned_df, logs = clean_dataframe(
        df,
        missing_strategy="drop",
        remove_dup_keep="first",
        type_coercion=True,
        date_normalisation=True,
    )
    assert len(logs) == 4

    missing_log = logs[0]
    assert missing_log.operation == "missing_value_drop"
    assert missing_log.details.get("removed_rows") == 1
    assert missing_log.rows_after == len(df) - 1

    date_log = next(entry for entry in logs if entry.operation == "date_normalisation")
    assert date_log.details.get("unparseable_rows") == 1
    assert date_log.details.get("valid_rows") == len(df) - 2
    assert date_log.rows_before == date_log.rows_after == len(df) - 1

    # Unparseable date row was preserved and coerced to None
    assert cleaned_df.loc[0, "Order_Date"] is None
    assert len(cleaned_df) == len(df) - 1


def test_sqlite_receives_exact_cleaned_dataset(sample_demo_file: Path) -> None:
    """I-3: SQLite sales table matches cleaned DataFrame row count, columns, and total sales."""
    df = pd.read_excel(sample_demo_file, engine="openpyxl")
    cleaned_df, _ = clean_dataframe(df)
    mgr = DatabaseManager()
    conn = mgr.rebuild(cleaned_df)
    try:
        assert mgr.count_rows() == len(cleaned_df)
        assert mgr.get_table_columns() == list(cleaned_df.columns)
        cursor = conn.execute("SELECT SUM(Total_Sales) FROM sales")
        sql_sum = float(cursor.fetchone()[0])
        expected_sum = float(cleaned_df["Total_Sales"].sum())
        assert abs(sql_sum - expected_sum) < 1e-9
    finally:
        mgr.close()


def test_kpi_revenue_matches_sql_total_revenue(sample_demo_file: Path) -> None:
    """I-4: compute_kpis total revenue agrees with SQL total revenue query within 1e-9."""
    df = pd.read_excel(sample_demo_file, engine="openpyxl")
    cleaned_df, _ = clean_dataframe(df)
    kpis = compute_kpis(cleaned_df)
    mgr = DatabaseManager()
    conn = mgr.rebuild(cleaned_df)
    try:
        res = execute_predefined_query(conn, "1_total_revenue")
        assert res.success
        sql_revenue = float(res.data.iloc[0]["Total_Revenue"])
        assert abs(kpis["total_revenue"] - sql_revenue) < 1e-9
    finally:
        mgr.close()


def test_all_seven_predefined_queries_return_nonempty(sample_demo_file: Path) -> None:
    """I-5: All seven predefined SQL business queries succeed and return non-empty data."""
    df = pd.read_excel(sample_demo_file, engine="openpyxl")
    cleaned_df, _ = clean_dataframe(df)
    mgr = DatabaseManager()
    conn = mgr.rebuild(cleaned_df)
    try:
        for qid in APPROVED_QUERIES:
            res = execute_predefined_query(conn, qid)
            assert res.success, f"Query {qid} failed: {res.error_message}"
            assert res.data is not None
            assert res.row_count > 0
    finally:
        mgr.close()


def test_custom_sql_security_enforcement(sample_demo_file: Path) -> None:
    """I-6: Custom SQL enforces SELECT-only security policy, rejecting writes."""
    df = pd.read_excel(sample_demo_file, engine="openpyxl")
    cleaned_df, _ = clean_dataframe(df)
    mgr = DatabaseManager()
    conn = mgr.rebuild(cleaned_df)
    try:
        res_valid = execute_custom_query(conn, "SELECT COUNT(*) FROM sales")
        assert res_valid.success

        res_invalid = execute_custom_query(conn, "DELETE FROM sales")
        assert not res_invalid.success
        assert "Security Violation" in res_invalid.error_message
        assert mgr.count_rows() == len(cleaned_df)
    finally:
        mgr.close()


def test_prepare_comparison_frame_return_type_and_exclusion(
    sample_demo_file: Path,
) -> None:
    """I-7: prepare_comparison_frame isolates valid cohorts and excludes non-finite sales."""
    df = pd.read_excel(sample_demo_file, engine="openpyxl")
    groups = df["Gender"].dropna().unique().tolist()
    if len(groups) >= 2:
        g1, g2 = groups[0], groups[1]
        frame = prepare_comparison_frame(df, g1, g2)
        assert list(frame.columns) == ["Gender", "Total_Sales"]
        assert frame["Gender"].dtype == object or pd.api.types.is_string_dtype(
            frame["Gender"]
        )
        assert frame["Total_Sales"].notna().all()


def test_database_manager_connection_lifecycle(sample_demo_file: Path) -> None:
    """I-8a: DatabaseManager rebuild and close lifecycle manages connections correctly."""
    df = pd.read_excel(sample_demo_file, engine="openpyxl")
    mgr = DatabaseManager()
    mgr.rebuild(df)
    assert mgr.connection is not None
    mgr.close()
    assert mgr.connection is None

    mgr.rebuild(df)
    assert mgr.connection is not None
    mgr.close()


def test_get_db_manager_singleton_connection_ownership() -> None:
    """I-8b: get_db_manager returns singleton instance; connection is managed explicitly."""
    mgr1 = get_db_manager()
    mgr2 = get_db_manager()
    assert mgr1 is mgr2


def test_continuity_across_layers(sample_demo_file: Path) -> None:
    """I-9: End-to-end continuity verified via row counts, schemas, EDA vs SQL aggregates, and stats."""
    df = pd.read_excel(sample_demo_file, engine="openpyxl")
    cleaned_df, logs = clean_dataframe(df)

    row_delta = logs[0].rows_before - logs[0].rows_after
    assert len(cleaned_df) == len(df) - row_delta

    mgr = DatabaseManager()
    conn = mgr.rebuild(cleaned_df)
    try:
        assert mgr.count_rows() == len(cleaned_df)

        eda_stats = run_eda_pipeline(cleaned_df)
        kpi_rev = eda_stats["kpis"]["total_revenue"]
        sql_rev_res = execute_predefined_query(conn, "1_total_revenue")
        sql_rev = float(sql_rev_res.data.iloc[0]["Total_Revenue"])
        assert abs(kpi_rev - sql_rev) < 1e-9

        eda_cat = (
            eda_stats["by_category"].sort_values("Category").reset_index(drop=True)
        )
        sql_cat_res = execute_custom_query(
            conn,
            "SELECT Category, SUM(Total_Sales) AS Revenue FROM sales GROUP BY Category ORDER BY Category",
        )
        sql_cat = sql_cat_res.data.sort_values("Category").reset_index(drop=True)
        assert abs(eda_cat["Total_Sales"].sum() - sql_cat["Revenue"].sum()) < 1e-9

        groups = cleaned_df["Gender"].dropna().unique().tolist()
        if len(groups) >= 2:
            stat_res = run_gender_comparison(cleaned_df, groups[0], groups[1])
            s1 = cleaned_df.loc[
                cleaned_df["Gender"] == groups[0], "Total_Sales"
            ].dropna()
            s2 = cleaned_df.loc[
                cleaned_df["Gender"] == groups[1], "Total_Sales"
            ].dropna()
            scipy_t, scipy_p = stats.ttest_ind(s1, s2, equal_var=False)
            assert abs(stat_res.t_statistic - scipy_t) < 1e-6
            assert abs(stat_res.p_value - scipy_p) < 1e-6
    finally:
        mgr.close()


@pytest.mark.skipif(AppTest is None, reason="Streamlit AppTest not available")
def test_analysis_pages_render_with_injected_session_state(
    sample_demo_file: Path,
) -> None:
    """A-1: Headless AppTest smoke verification for pages 02, 03, and 05 with injected state."""
    df = pd.read_excel(sample_demo_file, engine="openpyxl")
    cleaned_df, _ = clean_dataframe(df)
    mgr = DatabaseManager()
    conn = mgr.rebuild(cleaned_df)

    app_root = Path(__file__).resolve().parents[2] / "app"

    page2 = AppTest.from_file(str(app_root / "pages/02_eda_bi.py"))
    page2.session_state["active_df"] = cleaned_df
    page2.run(timeout=10)
    assert not page2.exception

    page3 = AppTest.from_file(str(app_root / "pages/03_sql_analysis.py"))
    page3.session_state["active_df"] = cleaned_df
    page3.session_state["db_conn"] = conn
    page3.run(timeout=10)
    assert not page3.exception

    page5 = AppTest.from_file(str(app_root / "pages/05_statistical_validation.py"))
    page5.session_state["active_df"] = cleaned_df
    page5.run(timeout=10)
    assert not page5.exception

    mgr.close()


@pytest.mark.skipif(AppTest is None, reason="Streamlit AppTest not available")
def test_sql_page_requires_database_connection(sample_demo_file: Path) -> None:
    """A-2: SQL analysis page displays warning when db connection is unavailable."""
    df = pd.read_excel(sample_demo_file, engine="openpyxl")
    cleaned_df, _ = clean_dataframe(df)

    app_root = Path(__file__).resolve().parents[2] / "app"
    page3 = AppTest.from_file(str(app_root / "pages/03_sql_analysis.py"))
    page3.session_state["active_df"] = cleaned_df
    page3.session_state["db_conn"] = None
    page3.run(timeout=10)
    assert not page3.exception
    assert any("Database connection not available" in w.value for w in page3.warning)


@pytest.mark.skipif(AppTest is None, reason="Streamlit AppTest not available")
def test_statistics_page_shows_empty_state() -> None:
    """A-3: Statistical validation page displays empty-state message when active_df is None."""
    app_root = Path(__file__).resolve().parents[2] / "app"
    page5 = AppTest.from_file(str(app_root / "pages/05_statistical_validation.py"))
    page5.session_state["active_df"] = None
    page5.run(timeout=10)
    assert not page5.exception
    assert any("No dataset loaded" in i.value for i in page5.info)


@pytest.mark.skipif(AppTest is None, reason="Streamlit AppTest not available")
def test_eda_page_renders_monthly_trend_with_canonical_dataset(
    sample_demo_file: Path,
) -> None:
    """A-4: Module 2 renders the monthly trend chart from the canonical dataset schema.

    Regression for the crash where ``line_chart`` received the raw dataset and
    was asked for a ``Month`` column that only exists on the aggregated frame.
    """
    df = pd.read_excel(sample_demo_file, engine="openpyxl")
    cleaned_df, _ = clean_dataframe(df)
    assert "Month" not in cleaned_df.columns

    app_root = Path(__file__).resolve().parents[2] / "app"
    page2 = AppTest.from_file(str(app_root / "pages/02_eda_bi.py"))
    page2.session_state["active_df"] = cleaned_df
    page2.run(timeout=10)
    assert not page2.exception
    # The monthly-trend chart (and the rest of the grid) rendered without the
    # missing-column fallback, proving a Month/Total_Sales frame was supplied.
    assert not any("Monthly Revenue Trend unavailable" in i.value for i in page2.info)


@pytest.mark.skipif(AppTest is None, reason="Streamlit AppTest not available")
def test_eda_page_degrades_gracefully_without_optional_columns() -> None:
    """A-5: Module 2 shows messages instead of crashing when optional columns are absent (FR-11 AC-4)."""
    partial_df = pd.DataFrame(
        {"Order_Date": ["2024-01-01", "2024-02-01"], "Total_Sales": [100.0, 200.0]}
    )

    app_root = Path(__file__).resolve().parents[2] / "app"
    page2 = AppTest.from_file(str(app_root / "pages/02_eda_bi.py"))
    page2.session_state["active_df"] = partial_df
    page2.run(timeout=10)

    assert not page2.exception
    infos = [i.value for i in page2.info]
    assert any("Revenue by Category" in msg for msg in infos)
    assert any("Revenue by City" in msg for msg in infos)
