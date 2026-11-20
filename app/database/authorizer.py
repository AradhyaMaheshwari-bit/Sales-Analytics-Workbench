"""SQLite engine-level security authorizer and progress handler (Increment 3).

Enforces the SELECT-only security policy (NFR-S-02, D-3) at the SQLite
engine level using ``sqlite3.Connection.set_authorizer`` and
``sqlite3.Connection.set_progress_handler()``.

Design (SDD-DB-SQL §4):
- Allows only read-only SELECT operations.
- Permits reads exclusively from `main.sales`.
- Denies access to SQLite system tables, temporary tables, and all unauthorized tables.
- Denies INSERT, UPDATE, DELETE, CREATE, DROP, ALTER, ATTACH, DETACH, PRAGMA, and other write/schema/database-management operations.
- Restricts SQL functions to an approved safe allowlist.
- Disables SQLite extension loading.
- Enforces execution limits using ``set_progress_handler()``:
  - Maximum wall-clock execution time: 2 seconds.
  - Maximum instruction budget: 1,000,000 SQLite VM opcodes.
  - Uses monotonic elapsed-time measurement and an independent opcode counter.
- Keeps the security policy maintainable and independently testable.
"""

from __future__ import annotations

import sqlite3
import time
from typing import Any

# Approved safe SQL functions for analytical queries
APPROVED_FUNCTIONS: set[str] = {
    "sum",
    "total",
    "avg",
    "count",
    "min",
    "max",
    "round",
    "strftime",
    "lower",
    "upper",
    "coalesce",
    "abs",
    "length",
    "substr",
    "trim",
    "cast",
    "ifnull",
}


def make_authorizer_callback():
    """Factory creating a strict SQLite authorizer callback.

    Returns:
        A callable matching the signature required by ``set_authorizer``.
    """

    def authorizer_callback(
        action: int,
        param1: Any,
        param2: Any,
        db_name: Any,
        trigger_name: Any,
    ) -> int:
        """SQLite engine authorizer callback."""
        # Allow top-level SELECT statements
        if action == sqlite3.SQLITE_SELECT:
            return sqlite3.SQLITE_OK

        # Allow reading from the canonical 'sales' table in 'main' (or default) database
        elif action == sqlite3.SQLITE_READ:
            table = str(param1 or "").lower()
            db = str(db_name or "").lower()
            if table == "sales" and (not db or db == "main"):
                return sqlite3.SQLITE_OK
            return sqlite3.SQLITE_DENY

        # Allow approved SQL functions
        elif action == sqlite3.SQLITE_FUNCTION:
            func = str(param2 or "").lower()
            if func in APPROVED_FUNCTIONS:
                return sqlite3.SQLITE_OK
            return sqlite3.SQLITE_DENY

        # Allow recursive CTE expansion (read-only; bounded by the progress handler)
        elif action == sqlite3.SQLITE_RECURSIVE:
            return sqlite3.SQLITE_OK

        # Deny all other actions (INSERT, UPDATE, DELETE, CREATE, DROP, ALTER,
        # ATTACH, DETACH, PRAGMA, transaction writes, temp-table creation, and any read of
        # internal tables like sqlite_master, sqlite_schema, sqlite_temp_master)
        return sqlite3.SQLITE_DENY

    return authorizer_callback


def attach_security_controls(
    conn: sqlite3.Connection,
    max_seconds: float = 2.0,
    max_opcodes: int = 1_000_000,
    opcode_chunk: int = 1000,
) -> None:
    """Attach the engine authorizer and progress handler timeout controls to *conn*.

    Args:
        conn: The SQLite connection instance.
        max_seconds: Maximum wall-clock execution time in seconds (default 2.0).
        max_opcodes: Maximum virtual machine opcode budget (default 1,000,000).
        opcode_chunk: Frequency of opcode progress handler invocations.
    """
    # 1. Set the strict engine authorizer
    conn.set_authorizer(make_authorizer_callback())

    # 2. Disable extension loading (NFR-S-02)
    conn.enable_load_extension(False)

    # 3. Set up progress handler for timeout and opcode budget enforcement
    start_time = time.monotonic()
    opcodes_executed = 0

    def progress_handler() -> int:
        """Progress handler invoked every N opcodes by SQLite."""
        nonlocal opcodes_executed
        opcodes_executed += opcode_chunk

        # Check opcode budget limit
        if opcodes_executed >= max_opcodes:
            return 1  # Non-zero return aborts query with OperationalError: interrupted

        # Check wall-clock time limit
        if (time.monotonic() - start_time) >= max_seconds:
            return 1  # Non-zero return aborts query with OperationalError: interrupted

        return 0

    conn.set_progress_handler(progress_handler, opcode_chunk)
