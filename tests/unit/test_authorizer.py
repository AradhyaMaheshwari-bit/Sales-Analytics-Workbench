"""Unit tests for the SQLite authorizer and progress handler (Increment 3)."""

from __future__ import annotations

import sqlite3

import pandas as pd
import pytest
from app.database.authorizer import (
    APPROVED_FUNCTIONS,
    attach_security_controls,
    make_authorizer_callback,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def sample_df():
    """Sample DataFrame matching the canonical sales schema."""
    return pd.DataFrame(
        {
            "Order_ID": ["ORD001", "ORD002"],
            "Order_Date": ["2024-01-15", "2024-02-20"],
            "Customer_ID": ["C001", "C002"],
            "Customer_Name": ["Alice", "Bob"],
            "Age": [30, 45],
            "Gender": ["Female", "Male"],
            "City": ["Patna", "Delhi"],
            "Product": ["Laptop", "Phone"],
            "Category": ["Electronics", "Electronics"],
            "Quantity": [2, 1],
            "Unit_Price": [50000.0, 30000.0],
            "Total_Sales": [100000.0, 30000.0],
        }
    )


@pytest.fixture
def raw_conn():
    """Unauthorized in-memory connection with a populated ``sales`` table."""
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    conn.execute("CREATE TABLE sales (Order_ID TEXT, Total_Sales REAL)")
    conn.execute("INSERT INTO sales VALUES ('ORD001', 100.0)")
    yield conn
    conn.close()


@pytest.fixture
def secured_conn(raw_conn):
    """Connection with security controls attached after ingestion."""
    attach_security_controls(raw_conn)
    yield raw_conn


@pytest.fixture
def raw_conn_factory():
    """Factory for multiple pre-populated in-memory connections."""

    def _make() -> sqlite3.Connection:
        conn = sqlite3.connect(":memory:", check_same_thread=False)
        conn.execute("CREATE TABLE sales (Order_ID TEXT, Total_Sales REAL)")
        conn.execute("INSERT INTO sales VALUES ('ORD001', 100.0)")
        return conn

    return _make


# ---------------------------------------------------------------------------
# Authorizer callback logic
# ---------------------------------------------------------------------------


class TestAuthorizerCallback:
    """Direct behaviour tests for the engine authorizer callback."""

    def test_allows_select(self, secured_conn):
        """SELECT is permitted."""
        assert secured_conn.execute("SELECT 1").fetchone() == (1,)

    def test_allows_read_from_sales(self, secured_conn):
        """Reading the canonical sales table is permitted."""
        rows = secured_conn.execute("SELECT Order_ID FROM sales").fetchall()
        assert rows == [("ORD001",)]

    def test_denies_insert(self, secured_conn):
        """INSERT is rejected at the engine level."""
        with pytest.raises(sqlite3.DatabaseError) as exc:
            secured_conn.execute("INSERT INTO sales VALUES ('X', 1.0)")
        assert "not authorized" in str(exc.value).lower()

    def test_denies_update(self, secured_conn):
        """UPDATE is rejected at the engine level."""
        with pytest.raises(sqlite3.DatabaseError) as exc:
            secured_conn.execute("UPDATE sales SET Total_Sales = 0")
        assert "not authorized" in str(exc.value).lower()

    def test_denies_delete(self, secured_conn):
        """DELETE is rejected at the engine level."""
        with pytest.raises(sqlite3.DatabaseError) as exc:
            secured_conn.execute("DELETE FROM sales")
        assert "not authorized" in str(exc.value).lower()

    def test_denies_create_table(self, secured_conn):
        """CREATE TABLE is rejected at the engine level."""
        with pytest.raises(sqlite3.DatabaseError):
            secured_conn.execute("CREATE TABLE rogue (x INTEGER)")

    def test_denies_drop_table(self, secured_conn):
        """DROP TABLE is rejected at the engine level."""
        with pytest.raises(sqlite3.DatabaseError):
            secured_conn.execute("DROP TABLE sales")

    def test_denies_attach(self, secured_conn):
        """ATTACH DATABASE is rejected at the engine level."""
        with pytest.raises(sqlite3.DatabaseError):
            secured_conn.execute("ATTACH DATABASE ':memory:' AS rogue")

    def test_denies_pragma(self, secured_conn):
        """PRAGMA is rejected at the engine level."""
        with pytest.raises(sqlite3.DatabaseError):
            secured_conn.execute("PRAGMA table_info(sales)")

    def test_denies_sqlite_master(self, secured_conn):
        """Reading sqlite_master is rejected at the engine level."""
        with pytest.raises(sqlite3.DatabaseError):
            secured_conn.execute("SELECT name FROM sqlite_master")

    def test_denies_unauthorized_table(self):
        """A SELECT against a non-sales table is rejected."""
        conn = sqlite3.connect(":memory:", check_same_thread=False)
        conn.execute("CREATE TABLE rogue (x INTEGER)")
        attach_security_controls(conn)
        try:
            with pytest.raises(sqlite3.DatabaseError) as exc:
                conn.execute("SELECT * FROM rogue")
            error_msg = str(exc.value).lower()
            assert "not authorized" in error_msg or "access to" in error_msg
        finally:
            conn.close()

    def test_callback_returns_deny_for_unknown_action(self):
        """Any action other than SELECT/READ/FUNCTION is denied."""
        callback = make_authorizer_callback()
        assert (
            callback(sqlite3.SQLITE_INSERT, "sales", None, "main", None)
            == sqlite3.SQLITE_DENY
        )
        assert (
            callback(sqlite3.SQLITE_DELETE, "sales", None, "main", None)
            == sqlite3.SQLITE_DENY
        )

    def test_callback_denies_other_database(self):
        """Reads from a non-main database are denied."""
        callback = make_authorizer_callback()
        assert (
            callback(sqlite3.SQLITE_READ, "sales", None, "other", None)
            == sqlite3.SQLITE_DENY
        )


# ---------------------------------------------------------------------------
# Approved function allowlist
# ---------------------------------------------------------------------------


class TestApprovedFunctions:
    """The function allowlist gates execution."""

    def test_allowlist_contents(self):
        """The allowlist contains the aggregate functions the queries need."""
        for fn in ("sum", "count", "avg", "min", "max", "strftime"):
            assert fn in APPROVED_FUNCTIONS

    def test_approved_functions_execute(self, secured_conn):
        """Allowlisted functions run without an authorization error."""
        assert secured_conn.execute(
            "SELECT SUM(Total_Sales) FROM sales"
        ).fetchone() == (100.0,)
        assert secured_conn.execute("SELECT COUNT(*) FROM sales").fetchone() == (1,)

    def test_unapproved_function_denied(self, secured_conn):
        """Functions outside the allowlist are rejected."""
        with pytest.raises(sqlite3.DatabaseError):
            secured_conn.execute("SELECT RANDOM() FROM sales")

    def test_load_extension_denied(self, secured_conn):
        """load_extension() is not on the allowlist and is rejected."""
        with pytest.raises(sqlite3.DatabaseError):
            secured_conn.execute("SELECT load_extension('evil') FROM sales")


# ---------------------------------------------------------------------------
# Progress handler
# ---------------------------------------------------------------------------


class TestProgressHandler:
    """The progress handler aborts runaway statements."""

    def test_wall_clock_limit_interrupts_query(self, raw_conn):
        """A near-zero wall-clock budget aborts a normal query."""
        # opcode_chunk=1 forces the handler to fire on the first opcode;
        # the tiny 1-row dataset otherwise completes before any check.
        attach_security_controls(
            raw_conn, max_seconds=0.0, max_opcodes=10**12, opcode_chunk=1
        )
        with pytest.raises(sqlite3.OperationalError) as exc:
            raw_conn.execute("SELECT COUNT(*) FROM sales")
        assert "interrupt" in str(exc.value).lower()

    def test_opcode_limit_interrupts_query(self, raw_conn):
        """An opcode budget of zero (first handler call) aborts the query."""
        attach_security_controls(
            raw_conn, max_seconds=3600.0, max_opcodes=0, opcode_chunk=1
        )
        with pytest.raises(sqlite3.OperationalError) as exc:
            raw_conn.execute("SELECT COUNT(*) FROM sales")
        assert "interrupt" in str(exc.value).lower()

    def test_generous_budget_allows_normal_query(self, secured_conn):
        """Normal queries complete under the default limits."""
        assert secured_conn.execute("SELECT COUNT(*) FROM sales").fetchone() == (1,)

    def test_limits_are_independent(self, raw_conn_factory):
        """A generous wall clock does not rescue an exhausted opcode budget."""
        conn = raw_conn_factory()
        attach_security_controls(
            conn, max_seconds=3600.0, max_opcodes=0, opcode_chunk=1
        )
        try:
            with pytest.raises(sqlite3.OperationalError):
                conn.execute("SELECT COUNT(*) FROM sales")
        finally:
            conn.close()

        conn = raw_conn_factory()
        attach_security_controls(
            conn, max_seconds=0.0, max_opcodes=10**12, opcode_chunk=1
        )
        try:
            with pytest.raises(sqlite3.OperationalError):
                conn.execute("SELECT COUNT(*) FROM sales")
        finally:
            conn.close()

    def test_timeout_does_not_apply_without_execution(self):
        """A zero budget still permits trivial statements issued through the same API."""
        conn = sqlite3.connect(":memory:", check_same_thread=False)
        attach_security_controls(conn, max_seconds=5.0, max_opcodes=10**12)
        try:
            assert conn.execute("SELECT 1").fetchone() == (1,)
        finally:
            conn.close()


# ---------------------------------------------------------------------------
# Per-statement budget reset (timeout raised from 2s to 5s)
# ---------------------------------------------------------------------------


class TestPerStatementBudgetReset:
    """Budgets reset per statement so consecutive queries inherit no stale state."""

    # Authorized (reads only ``sales``) but CPU-heavy: a 7-way self cross-join.
    _HEAVY_SQL = (
        "SELECT COUNT(*) FROM sales a, sales b, sales c, sales d, "
        "sales e, sales f, sales g"
    )

    @staticmethod
    def _make_conn(rows: int = 8) -> sqlite3.Connection:
        conn = sqlite3.connect(":memory:", check_same_thread=False)
        conn.execute("CREATE TABLE sales (x INTEGER)")
        conn.executemany("INSERT INTO sales VALUES (?)", [(i,) for i in range(rows)])
        return conn

    def test_default_wall_clock_is_five_seconds(self):
        """The default wall-clock budget is 5 seconds (raised from 2)."""
        import inspect

        sig = inspect.signature(attach_security_controls)
        assert sig.parameters["max_seconds"].default == 5.0

    def test_default_opcode_limit_is_one_million(self):
        """The opcode limit remains exactly 1,000,000."""
        import inspect

        sig = inspect.signature(attach_security_controls)
        assert sig.parameters["max_opcodes"].default == 1_000_000

    def test_opcode_budget_resets_between_consecutive_queries(self):
        """After an opcode-limited query is aborted, a later query gets a fresh budget.

        With the old cumulative counter the aborted query exhausted the budget,
        so the follow-up light query would also be interrupted. A successful
        follow-up proves the per-statement reset.
        """
        conn = self._make_conn()
        # One heavy query costs well over 1,000,000 opcodes, so this budget
        # aborts it while leaving plenty of headroom for the light follow-up.
        attach_security_controls(conn, max_seconds=3600.0, max_opcodes=1_000_000)
        try:
            with pytest.raises(sqlite3.OperationalError):
                conn.execute(self._HEAVY_SQL).fetchone()
            # Fresh per-statement budget: the light query must succeed.
            assert conn.execute("SELECT COUNT(*) FROM sales").fetchone() == (8,)
        finally:
            conn.close()

    def test_wall_clock_budget_resets_between_consecutive_queries(self):
        """Idle time before a query does not count against its wall-clock budget."""
        import time

        conn = self._make_conn()
        attach_security_controls(conn, max_seconds=0.5, max_opcodes=10**12)
        try:
            # Would be interrupted if the window started at attach time.
            time.sleep(0.6)
            assert conn.execute("SELECT COUNT(*) FROM sales").fetchone() == (8,)
        finally:
            conn.close()

    def test_wall_clock_limit_interrupts_genuine_runaway(self):
        """A long-running authorized query is aborted by the wall-clock limit.

        A 16-row, 7-way self cross-join (16^7 ~ 2.7e8 rows) reliably runs far
        longer than the 0.3 s budget on any reasonable machine.
        """
        conn = self._make_conn(rows=16)
        attach_security_controls(conn, max_seconds=0.3, max_opcodes=10**12)
        try:
            with pytest.raises(sqlite3.OperationalError) as exc:
                conn.execute(self._HEAVY_SQL).fetchone()
            assert "interrupt" in str(exc.value).lower()
        finally:
            conn.close()

    def test_opcode_limit_interrupts_genuine_runaway(self):
        """A runaway authorized query is aborted by the opcode budget."""
        conn = self._make_conn()
        attach_security_controls(conn, max_seconds=3600.0, max_opcodes=100_000)
        try:
            with pytest.raises(sqlite3.OperationalError) as exc:
                conn.execute(self._HEAVY_SQL).fetchone()
            assert "interrupt" in str(exc.value).lower()
        finally:
            conn.close()


# ---------------------------------------------------------------------------
# Integration with database manager lifecycle
# ---------------------------------------------------------------------------


class TestDatabaseManagerIntegration:
    """Security survives the rebuild path used by the application."""

    def test_rebuild_attaches_security(self, sample_df):
        """A rebuilt connection denies writes but allows reads."""
        from app.database.db_manager import DatabaseManager

        manager = DatabaseManager()
        conn = manager.rebuild(sample_df)

        try:
            assert conn.execute("SELECT COUNT(*) FROM sales").fetchone()[0] == len(
                sample_df
            )
            with pytest.raises(sqlite3.DatabaseError):
                conn.execute("DELETE FROM sales")
        finally:
            manager.close()

    def test_usage_metrics_available_after_rebuild(self, sample_df):
        """Read paths used by other modules still work post-lockdown."""
        from app.database.db_manager import DatabaseManager

        manager = DatabaseManager()
        manager.rebuild(sample_df)
        try:
            assert manager.count_rows() == len(sample_df)
            assert manager.get_table_columns()[:2] == ["Order_ID", "Order_Date"]
        finally:
            manager.close()
