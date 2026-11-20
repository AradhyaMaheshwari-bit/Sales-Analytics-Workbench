"""In-memory SQLite lifecycle manager for the Sales Analytics Workbench.

FR-15: create an in-memory SQLite database and register the active
DataFrame into the lowercase ``sales`` table.  NFR-DP-02: no external
services — the database is per-session in-memory only.

Design (SDD-DB-SQL §2.2, data-architecture §3): whenever ``active_df``
changes (upload, clean, undo, reset) the previous connection is closed and
a fresh one built from the new DataFrame.  The authorizer and progress
handler (Increment 3) are attached after ingestion completes.

The module is Streamlit-free: callers pass in a connection handle or let
the manager create one, and nothing here reads ``st.session_state``.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

import pandas as pd

from app.database.authorizer import attach_security_controls

# Canonical SQLite schema (SDD-DB-SQL §3).  No PK / NOT NULL constraints —
# uploaded datasets are imperfect before cleaning; business rules live in
# validator.py instead.
SALES_SCHEMA_SQL = """
CREATE TABLE sales (
    Order_ID        TEXT,
    Order_Date      TEXT,
    Customer_ID     TEXT,
    Customer_Name   TEXT,
    Age             REAL,
    Gender          TEXT,
    City            TEXT,
    Product         TEXT,
    Category        TEXT,
    Quantity        INTEGER,
    Unit_Price      REAL,
    Total_Sales     REAL
)
"""


class DatabaseManager:
    """Manage an in-memory SQLite connection and the ``sales`` table."""

    def __init__(self) -> None:
        self._conn: sqlite3.Connection | None = None

    # -- connection lifecycle ------------------------------------------------

    @property
    def connection(self) -> sqlite3.Connection | None:
        return self._conn

    def create_connection(self, secured: bool = True) -> sqlite3.Connection:
        """Open a fresh in-memory connection.

        ``check_same_thread=False`` is mandatory (SDD-DB-SQL §2.1): Streamlit
        may execute a session's script runs on different worker threads.

        Args:
            secured: If True, attach security authorizer and progress handler.
        """
        self._conn = sqlite3.connect(":memory:", check_same_thread=False)
        if secured:
            attach_security_controls(self._conn)
        return self._conn

    def close(self) -> None:
        """Close the current connection if one is open."""
        if self._conn is not None:
            try:
                self._conn.close()
            except sqlite3.Error:
                pass
            self._conn = None

    def rebuild(self, df: pd.DataFrame) -> sqlite3.Connection:
        """Rebuild the database from *df* (SDD-DB-SQL §2.2).

        1. Close the existing connection (if any).
        2. Open a fresh in-memory connection (unsecured for ingestion).
        3. Ingest *df* into table ``sales`` via ``to_sql(if_exists='replace')``.
        4. Attach security authorizer and progress handler after ingestion.
        """
        self.close()
        # Create unsecured connection for ingestion
        conn = self.create_connection(secured=False)
        self._ingest(conn, df)
        # Attach security controls after data is loaded
        attach_security_controls(conn)
        return conn

    # -- ingestion ------------------------------------------------------------

    def _ingest(self, conn: sqlite3.Connection, df: pd.DataFrame) -> None:
        """Register the DataFrame into table ``sales`` with all 12 columns.

        NULL dates survive ingestion: they are written as NULL and the column
        remains TEXT so ``STRFTIME`` in Query 5 never crashes.
        """
        df_to_write = df.copy(deep=True)

        # Normalise column dtypes toward the canonical schema before write.
        # Unmapped columns are preserved as-is (SQLite accepts anything).
        if "Quantity" in df_to_write.columns:
            df_to_write["Quantity"] = (
                pd.to_numeric(df_to_write["Quantity"], errors="coerce")
                .fillna(0)
                .astype("int64")
            )
        for col in ("Unit_Price", "Total_Sales", "Age"):
            if col in df_to_write.columns:
                df_to_write[col] = pd.to_numeric(
                    df_to_write[col], errors="coerce"
                ).astype("float64")

        df_to_write.to_sql("sales", conn, if_exists="replace", index=False)
        conn.commit()

    # -- queries --------------------------------------------------------------

    def get_table_columns(self) -> list[str]:
        """Return the column names of the ``sales`` table."""
        if self._conn is None:
            return []
        cursor = self._conn.execute("SELECT * FROM sales LIMIT 0")
        return [desc[0] for desc in cursor.description] if cursor.description else []

    def count_rows(self) -> int:
        """Return the row count of the ``sales`` table (0 if not built)."""
        if self._conn is None:
            return 0
        cursor = self._conn.execute("SELECT COUNT(*) FROM sales")
        row = cursor.fetchone()
        return int(row[0]) if row else 0

    def query(self, sql: str) -> list[tuple[Any, ...]]:
        """Execute a read-only SQL query and return all rows.

        Increment 1C scope: simple passthrough for module wiring and tests.
        The authorizer / progress handler / row cap are Increment 3.
        """
        if self._conn is None:
            raise RuntimeError("Database not initialised; call rebuild() first.")
        cursor = self._conn.execute(sql)
        return cursor.fetchall()


# ---------------------------------------------------------------------------
# Module-level convenience (per-session instance wiring in the UI)
# ---------------------------------------------------------------------------

_db_manager_instance: DatabaseManager | None = None


def get_db_manager() -> DatabaseManager:
    """Return a module-level singleton DatabaseManager."""
    global _db_manager_instance
    if _db_manager_instance is None:
        _db_manager_instance = DatabaseManager()
    return _db_manager_instance


def rebuild_sales_table(df: pd.DataFrame) -> sqlite3.Connection:
    """Convenience: rebuild the singleton's ``sales`` table from *df*."""
    return get_db_manager().rebuild(df)


def build_demo_dataset_path() -> Path:
    """Return the canonical path for the bundled internship dataset."""
    return Path("data/raw/internship_dataset.xlsx")
