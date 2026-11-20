"""Unit tests for SQL query execution and security enforcement (Increment 3)."""

from __future__ import annotations

import sqlite3

import pandas as pd
import pytest
from app.database.authorizer import APPROVED_FUNCTIONS, attach_security_controls
from app.database.queries import (
    QueryResult,
    detect_multi_statement,
    execute_custom_query,
    execute_predefined_query,
    get_query_catalog,
    validate_single_select,
)

# ---------------------------------------------------------------------------
# Test Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def sample_df():
    """Sample DataFrame matching the canonical sales schema."""
    return pd.DataFrame(
        {
            "Order_ID": ["ORD001", "ORD002", "ORD003", "ORD004", "ORD005"],
            "Order_Date": [
                "2024-01-15",
                "2024-02-20",
                None,
                "2024-03-10",
                "2024-01-25",
            ],
            "Customer_ID": ["C001", "C002", "C003", "C001", "C004"],
            "Customer_Name": ["Alice", "Bob", "Charlie", "Alice", "Diana"],
            "Age": [30, 45, 25, 30, 50],
            "Gender": ["Female", "Male", "Male", "Female", "Female"],
            "City": ["Patna", "Delhi", "Mumbai", "Patna", "Chennai"],
            "Product": ["Laptop", "Phone", "Tablet", "Laptop", "Phone"],
            "Category": [
                "Electronics",
                "Electronics",
                "Electronics",
                "Electronics",
                "Electronics",
            ],
            "Quantity": [2, 1, 3, 1, 2],
            "Unit_Price": [50000.0, 30000.0, 15000.0, 50000.0, 30000.0],
            "Total_Sales": [100000.0, 30000.0, 45000.0, 50000.0, 60000.0],
        }
    )


@pytest.fixture
def secured_conn(sample_df):
    """Create an in-memory SQLite connection with security controls and sample data."""
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    # Ingest data BEFORE attaching security controls
    sample_df.to_sql("sales", conn, if_exists="replace", index=False)
    attach_security_controls(conn)
    yield conn
    conn.close()


@pytest.fixture
def empty_conn():
    """Create an empty secured connection for security tests."""
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    conn.execute(
        "CREATE TABLE sales (Order_ID TEXT, Order_Date TEXT, Customer_ID TEXT, "
        "Customer_Name TEXT, Age REAL, Gender TEXT, City TEXT, Product TEXT, "
        "Category TEXT, Quantity INTEGER, Unit_Price REAL, Total_Sales REAL)"
    )
    attach_security_controls(conn)
    yield conn
    conn.close()


# ---------------------------------------------------------------------------
# Predefined Query Tests
# ---------------------------------------------------------------------------


class TestPredefinedQueries:
    """Tests for the seven approved business queries."""

    def test_query_catalog_has_seven_queries(self):
        """Verify exactly seven predefined queries exist."""
        catalog = get_query_catalog()
        assert len(catalog) == 7

    def test_query_1_total_revenue(self, secured_conn):
        """Test Query 1: Total Revenue."""
        result = execute_predefined_query(secured_conn, "1_total_revenue")
        assert result.success
        assert result.data is not None
        assert len(result.data) == 1
        # 100000 + 30000 + 45000 + 50000 + 60000 = 285000
        assert result.data.iloc[0]["Total_Revenue"] == 285000.0

    def test_query_2_revenue_by_category(self, secured_conn):
        """Test Query 2: Revenue by Category."""
        result = execute_predefined_query(secured_conn, "2_revenue_by_category")
        assert result.success
        assert result.data is not None
        assert len(result.data) == 1  # All Electronics
        assert result.data.iloc[0]["Category"] == "Electronics"

    def test_query_3_revenue_by_product(self, secured_conn):
        """Test Query 3: Revenue by Product."""
        result = execute_predefined_query(secured_conn, "3_revenue_by_product")
        assert result.success
        assert result.data is not None
        # Laptop: 100000 + 50000 = 150000
        # Phone: 30000 + 60000 = 90000
        # Tablet: 45000
        assert len(result.data) == 3
        assert result.data.iloc[0]["Product"] == "Laptop"

    def test_query_4_revenue_by_city(self, secured_conn):
        """Test Query 4: Revenue by City."""
        result = execute_predefined_query(secured_conn, "4_revenue_by_city")
        assert result.success
        assert result.data is not None
        # Patna: 100000 + 50000 = 150000
        assert len(result.data) == 4
        assert result.data.iloc[0]["City"] == "Patna"

    def test_query_5_monthly_trend_excludes_null_dates(self, secured_conn):
        """Test Query 5: Monthly Revenue Trend excludes NULL Order_Date."""
        result = execute_predefined_query(secured_conn, "5_monthly_trend")
        assert result.success
        assert result.data is not None
        # Only 4 rows have non-null dates: 2024-01 (2 rows), 2024-02 (1), 2024-03 (1)
        assert len(result.data) == 3
        # Verify NULL dates are excluded (no NULL month group)
        assert "None" not in result.data["Month"].values

    def test_query_6_revenue_by_gender(self, secured_conn):
        """Test Query 6: Revenue Split by Gender."""
        result = execute_predefined_query(secured_conn, "6_revenue_by_gender")
        assert result.success
        assert result.data is not None
        assert len(result.data) == 2

    def test_query_7_top_customers(self, secured_conn):
        """Test Query 7: Top 10 Customers by Revenue."""
        result = execute_predefined_query(secured_conn, "7_top_customers")
        assert result.success
        assert result.data is not None
        # Alice: 100000 + 50000 = 150000
        assert len(result.data) <= 10
        assert result.data.iloc[0]["Customer_Name"] == "Alice"

    def test_invalid_query_id(self, secured_conn):
        """Test that invalid query ID returns error."""
        result = execute_predefined_query(secured_conn, "invalid_query")
        assert not result.success
        assert "Unknown query ID" in result.error_message


# ---------------------------------------------------------------------------
# Security Tests
# ---------------------------------------------------------------------------


class TestSecurityEnforcement:
    """Tests for SQL security controls."""

    def test_insert_denied(self, empty_conn):
        """INSERT is denied by authorizer."""
        result = execute_custom_query(
            empty_conn,
            "INSERT INTO sales (Order_ID) VALUES ('X');",
        )
        assert not result.success
        assert (
            "Security Violation" in result.error_message
            or "not authorized" in result.error_message.lower()
        )

    def test_update_denied(self, empty_conn):
        """UPDATE is denied by authorizer."""
        result = execute_custom_query(
            empty_conn,
            "UPDATE sales SET Total_Sales = 0;",
        )
        assert not result.success

    def test_delete_denied(self, empty_conn):
        """DELETE is denied by authorizer."""
        result = execute_custom_query(empty_conn, "DELETE FROM sales;")
        assert not result.success

    def test_create_table_denied(self, empty_conn):
        """CREATE TABLE is denied by authorizer."""
        result = execute_custom_query(
            empty_conn,
            "CREATE TABLE malicious (x INT);",
        )
        assert not result.success

    def test_drop_table_denied(self, empty_conn):
        """DROP TABLE is denied by authorizer."""
        result = execute_custom_query(empty_conn, "DROP TABLE sales;")
        assert not result.success

    def test_alter_table_denied(self, empty_conn):
        """ALTER TABLE is denied by authorizer."""
        result = execute_custom_query(
            empty_conn,
            "ALTER TABLE sales ADD COLUMN malicious TEXT;",
        )
        assert not result.success

    def test_attach_denied(self, empty_conn):
        """ATTACH DATABASE is denied by authorizer."""
        result = execute_custom_query(
            empty_conn,
            "ATTACH DATABASE ':memory:' AS malicious;",
        )
        assert not result.success

    def test_detach_denied(self, empty_conn):
        """DETACH DATABASE is denied by authorizer."""
        result = execute_custom_query(empty_conn, "DETACH DATABASE main;")
        assert not result.success

    def test_pragma_denied(self, empty_conn):
        """PRAGMA is denied by authorizer."""
        result = execute_custom_query(empty_conn, "PRAGMA table_info(sales);")
        assert not result.success

    def test_sqlite_master_denied(self, empty_conn):
        """Reading sqlite_master is denied by authorizer."""
        result = execute_custom_query(
            empty_conn,
            "SELECT name FROM sqlite_master;",
        )
        assert not result.success

    def test_unauthorized_function_denied(self, empty_conn):
        """Unauthorized SQL functions are denied."""
        result = execute_custom_query(
            empty_conn,
            "SELECT load_extension('malicious') FROM sales;",
        )
        assert not result.success

    def test_select_on_unauthorized_table_denied(self, empty_conn):
        """SELECT on non-sales table is denied."""
        # Create a second table before authorizer
        conn = sqlite3.connect(":memory:", check_same_thread=False)
        conn.execute("CREATE TABLE other_table (x INT)")
        conn.execute("INSERT INTO other_table VALUES (1)")
        attach_security_controls(conn)

        result = execute_custom_query(conn, "SELECT * FROM other_table;")
        assert not result.success
        conn.close()

    def test_comment_before_insert_denied(self, empty_conn):
        """Comments cannot bypass security."""
        result = execute_custom_query(
            empty_conn,
            "/* comment */ INSERT INTO sales VALUES ('X', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL);",
        )
        assert not result.success

    def test_cte_with_insert_denied(self, empty_conn):
        """CTE wrapping INSERT is still denied."""
        result = execute_custom_query(
            empty_conn,
            "WITH cte AS (SELECT 1) INSERT INTO sales SELECT * FROM cte;",
        )
        assert not result.success

    def test_subquery_write_denied(self, empty_conn):
        """Subquery with write intent is denied."""
        result = execute_custom_query(
            empty_conn,
            "SELECT (DELETE FROM sales);",
        )
        assert not result.success


# ---------------------------------------------------------------------------
# Multi-Statement Detection Tests
# ---------------------------------------------------------------------------


class TestMultiStatementDetection:
    """Tests for multiple SQL statement detection."""

    def test_single_statement_valid(self):
        """Single statement returns False."""
        assert not detect_multi_statement("SELECT 1;")
        assert not detect_multi_statement("SELECT * FROM sales")

    def test_multiple_statements_detected(self):
        """Multiple statements return True."""
        assert detect_multi_statement("SELECT 1; SELECT 2;")
        assert detect_multi_statement("SELECT 1;\nDELETE FROM sales;")

    def test_semicolon_in_string_not_detected(self):
        """Semicolon inside string literal does not trigger detection."""
        assert not detect_multi_statement("SELECT 'hello;world';")
        assert not detect_multi_statement('SELECT "a;b";')

    def test_empty_query(self):
        """Empty query returns False."""
        assert not detect_multi_statement("")

    def test_whitespace_only(self):
        """Whitespace-only query returns False."""
        assert not detect_multi_statement("   \n\t  ")


class TestValidateSingleSelect:
    """Tests for SELECT validation."""

    def test_valid_select(self):
        """Valid SELECT passes."""
        is_valid, msg = validate_single_select("SELECT * FROM sales;")
        assert is_valid
        assert msg == ""

    def test_non_select_rejected(self):
        """Non-SELECT statement is rejected."""
        is_valid, msg = validate_single_select("INSERT INTO sales VALUES (1);")
        assert not is_valid
        assert "Only SELECT" in msg

    def test_empty_query_rejected(self):
        """Empty query is rejected."""
        is_valid, msg = validate_single_select("")
        assert not is_valid
        assert "empty" in msg.lower()

    def test_multiple_statements_rejected(self):
        """Multiple statements are rejected."""
        is_valid, msg = validate_single_select("SELECT 1; SELECT 2;")
        assert not is_valid
        assert "Multiple" in msg


# ---------------------------------------------------------------------------
# Execution Limit Tests
# ---------------------------------------------------------------------------


class TestExecutionLimits:
    """Tests for timeout and row cap enforcement."""

    def test_result_row_cap(self, secured_conn):
        """Results are capped at max_rows."""
        # Create a connection with many rows
        conn = sqlite3.connect(":memory:", check_same_thread=False)
        df = pd.DataFrame(
            {
                "Order_ID": [f"ORD{i:04d}" for i in range(600)],
                "Total_Sales": [100.0] * 600,
            }
        )
        df.to_sql("sales", conn, if_exists="replace", index=False)
        attach_security_controls(conn)

        result = execute_custom_query(conn, "SELECT * FROM sales;", max_rows=500)
        assert result.success
        assert result.truncated
        assert len(result.data) == 500
        conn.close()

    def test_result_truncation_flag(self, secured_conn):
        """Truncation flag is set correctly."""
        conn = sqlite3.connect(":memory:", check_same_thread=False)
        df = pd.DataFrame(
            {
                "Order_ID": [f"ORD{i:04d}" for i in range(600)],
                "Total_Sales": [100.0] * 600,
            }
        )
        df.to_sql("sales", conn, if_exists="replace", index=False)
        attach_security_controls(conn)

        result = execute_custom_query(conn, "SELECT * FROM sales;", max_rows=500)
        assert result.truncated
        conn.close()

    def test_small_result_not_truncated(self, secured_conn):
        """Small results are not truncated."""
        result = execute_custom_query(secured_conn, "SELECT * FROM sales LIMIT 3;")
        assert result.success
        assert not result.truncated
        assert len(result.data) == 3


# ---------------------------------------------------------------------------
# Query Result Tests
# ---------------------------------------------------------------------------


class TestQueryResult:
    """Tests for QueryResult dataclass."""

    def test_success_result(self):
        """Successful result has correct fields."""
        df = pd.DataFrame({"x": [1, 2, 3]})
        result = QueryResult(success=True, data=df, row_count=3, truncated=False)
        assert result.success
        assert result.row_count == 3

    def test_error_result(self):
        """Error result has error_message."""
        result = QueryResult(success=False, error_message="Query failed")
        assert not result.success
        assert result.error_message == "Query failed"


# ---------------------------------------------------------------------------
# Authorizer Function Allowlist Tests
# ---------------------------------------------------------------------------


class TestApprovedFunctions:
    """Tests for approved SQL functions."""

    def test_approved_functions_exist(self):
        """Approved functions set is populated."""
        assert "sum" in APPROVED_FUNCTIONS
        assert "count" in APPROVED_FUNCTIONS
        assert "strftime" in APPROVED_FUNCTIONS

    def test_unapproved_function_denied(self, empty_conn):
        """Unapproved functions are denied."""
        # Using a function not in the allowlist
        result = execute_custom_query(
            empty_conn,
            "SELECT RANDOM() FROM sales;",
        )
        assert not result.success
