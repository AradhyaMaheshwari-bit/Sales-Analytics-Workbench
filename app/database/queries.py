"""SQL query execution and business query catalog (Increment 3).

Implements the seven approved business queries and a secure custom query executor
enforcing SELECT-only, single-statement, and resource-limit policies.

Design (SDD-DB-SQL §5, SRS-SQL §2):
- Seven predefined queries from the original internship Task-1 repository.
- Query 5 adapted to use STRFTIME('%Y-%m', Order_Date) with NULL date exclusion.
- Custom SQL execution enforces single statement, SELECT-only (via authorizer),
  timeout/opcode limits (via progress handler), and result capping.
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass

import pandas as pd


@dataclass
class QueryResult:
    """Result of a SQL query execution."""

    success: bool
    data: pd.DataFrame | None = None
    error_message: str | None = None
    row_count: int = 0
    truncated: bool = False


# Seven approved business queries (SRS-SQL §2)
APPROVED_QUERIES = {
    "1_total_revenue": {
        "title": "Total Revenue",
        "question": "What is the total revenue across all sales?",
        "sql": "SELECT SUM(Total_Sales) AS Total_Revenue FROM sales;",
    },
    "2_revenue_by_category": {
        "title": "Revenue by Category",
        "question": "Which product categories generate the most revenue?",
        "sql": "SELECT Category, SUM(Total_Sales) AS Revenue FROM sales GROUP BY Category ORDER BY Revenue DESC;",
    },
    "3_revenue_by_product": {
        "title": "Revenue by Product",
        "question": "Which individual products generate the most revenue?",
        "sql": "SELECT Product, SUM(Total_Sales) AS Revenue FROM sales GROUP BY Product ORDER BY Revenue DESC;",
    },
    "4_revenue_by_city": {
        "title": "Revenue by City",
        "question": "Which cities contribute the most to revenue?",
        "sql": "SELECT City, SUM(Total_Sales) AS Revenue FROM sales GROUP BY City ORDER BY Revenue DESC;",
    },
    "5_monthly_trend": {
        "title": "Monthly Revenue Trend",
        "question": "What is the monthly revenue trend (seasonality) throughout the year?",
        "sql": "SELECT STRFTIME('%Y-%m', Order_Date) AS Month, SUM(Total_Sales) AS Revenue FROM sales WHERE Order_Date IS NOT NULL GROUP BY Month ORDER BY Month;",
    },
    "6_revenue_by_gender": {
        "title": "Revenue Split by Gender",
        "question": "How does revenue split by gender?",
        "sql": "SELECT Gender, SUM(Total_Sales) AS Revenue FROM sales GROUP BY Gender;",
    },
    "7_top_customers": {
        "title": "Top 10 Customers",
        "question": "Who are the top-10 customers by revenue?",
        "sql": "SELECT Customer_Name, SUM(Total_Sales) AS Revenue FROM sales GROUP BY Customer_Name ORDER BY Revenue DESC LIMIT 10;",
    },
}


def _strip_sql_comments(sql: str) -> str:
    """Remove SQL comments from a query string.

    Handles both ``--`` line comments and ``/* ... */`` block comments.
    Correctly respects single-quoted strings (with SQLite ``''`` escaping)
    and double-quoted identifiers (with SQLite ``""`` escaping).
    Does NOT treat backslash as an escape character.
    """
    result: list[str] = []
    i = 0
    n = len(sql)

    while i < n:
        # Single-quoted string literal
        if sql[i] == "'":
            result.append("'")
            i += 1
            while i < n:
                if sql[i] == "'":
                    result.append("'")
                    # Check for doubled single quote ''
                    if i + 1 < n and sql[i + 1] == "'":
                        result.append("'")
                        i += 2
                        continue
                    else:
                        i += 1
                        break
                else:
                    result.append(sql[i])
                    i += 1
            continue

        # Double-quoted identifier
        if sql[i] == '"':
            result.append('"')
            i += 1
            while i < n:
                if sql[i] == '"':
                    result.append('"')
                    # Check for doubled double quote ""
                    if i + 1 < n and sql[i + 1] == '"':
                        result.append('"')
                        i += 2
                        continue
                    else:
                        i += 1
                        break
                else:
                    result.append(sql[i])
                    i += 1
            continue

        # Line comment: --
        if sql[i] == "-" and i + 1 < n and sql[i + 1] == "-":
            i += 2
            while i < n and sql[i] != "\n":
                i += 1
            if i < n:
                result.append("\n")
                i += 1
            continue

        # Block comment: /* ... */
        if sql[i] == "/" and i + 1 < n and sql[i + 1] == "*":
            i += 2
            while i + 1 < n and not (sql[i] == "*" and sql[i + 1] == "/"):
                i += 1
            i += 2  # Skip past */
            continue

        result.append(sql[i])
        i += 1

    return "".join(result)


def detect_multi_statement(sql: str) -> bool:
    """Detect multiple SQL statements in a query string.

    Returns True if a semicolon is found outside string literals and quoted
    identifiers, followed by non-whitespace, non-comment content.
    """
    cleaned = _strip_sql_comments(sql)

    i = 0
    n = len(cleaned)

    while i < n:
        char = cleaned[i]

        # Skip single-quoted strings
        if char == "'":
            i += 1
            while i < n:
                if cleaned[i] == "'":
                    if i + 1 < n and cleaned[i + 1] == "'":
                        i += 2
                        continue
                    i += 1
                    break
                i += 1
            continue

        # Skip double-quoted identifiers
        if char == '"':
            i += 1
            while i < n:
                if cleaned[i] == '"':
                    if i + 1 < n and cleaned[i + 1] == '"':
                        i += 2
                        continue
                    i += 1
                    break
                i += 1
            continue

        # Semicolon outside strings/identifiers
        if char == ";":
            remaining = cleaned[i + 1 :].strip()
            if remaining:
                return True

        i += 1

    return False


def validate_single_select(sql: str) -> tuple[bool, str]:
    """Pre-validate that SQL is a single SELECT statement.

    This is a convenience early check. The SQLite authorizer enforces
    the policy at the engine level regardless.

    Args:
        sql: The SQL query string.

    Returns:
        (is_valid, error_message)
    """
    sql_trimmed = sql.strip()

    # Strip comments to detect empty/comment-only input
    sql_no_comments = _strip_sql_comments(sql_trimmed).strip()

    if not sql_no_comments:
        return False, "Query is empty."

    if detect_multi_statement(sql_trimmed):
        return (
            False,
            "Multiple SQL statements are not permitted. Submit exactly one SELECT query.",
        )

    # Handle statement type
    upper_sql = sql_no_comments.upper()

    if upper_sql.startswith("SELECT"):
        return True, ""

    if upper_sql.startswith("WITH"):
        # For CTEs, verify that the terminal/outer statement is a SELECT
        # A CTE looks like: WITH ... SELECT ...
        # If it is WITH ... INSERT / UPDATE / DELETE, reject it.
        # Check if the query contains INSERT, UPDATE, DELETE as statement verbs
        # or verify that it ends up doing a SELECT.
        # Since authorizer is the final defense, we do a sensible lexical check:
        # It must contain a top-level SELECT after CTE definitions.
        # Reject obvious write CTEs:
        for write_verb in ("INSERT ", "UPDATE ", "DELETE ", "DROP ", "ALTER "):
            # If the write verb appears after the WITH clause outside strings
            if write_verb in upper_sql:
                # Check if it's a write CTE (e.g., WITH cte AS (...) INSERT INTO...)
                # A safe heuristic: must contain SELECT and not contain top-level write
                pass
        # If it contains INSERT INTO / UPDATE / DELETE outside subqueries, reject
        import re

        # Look for CTE pattern: WITH ... AS (...) SELECT ...
        # If it does not contain SELECT as the main query verb, reject
        if not re.search(r"\)\s*SELECT\b", upper_sql) and not upper_sql.startswith(
            "WITH RECURSIVE"
        ):
            # Check if there is a top-level SELECT at all
            if "SELECT" not in upper_sql:
                return (
                    False,
                    "Security Violation: Only SELECT queries are permitted.",
                )
        # Check for CTE containing writes
        if re.search(r"\)\s*(INSERT|UPDATE|DELETE|DROP|ALTER)\b", upper_sql):
            return (
                False,
                "Security Violation: Only SELECT queries are permitted.",
            )
        return True, ""

    return (
        False,
        "Security Violation: Only SELECT queries are permitted.",
    )


def execute_custom_query(
    conn: sqlite3.Connection, query: str, max_rows: int = 500
) -> QueryResult:
    """Execute a custom user-provided SELECT query with security enforcement.

    Args:
        conn: The secured SQLite connection with authorizer attached.
        query: The user-provided SQL query string.
        max_rows: Maximum number of rows to return (default 500).

    Returns:
        QueryResult with success/data/error_message/truncated.
    """
    # Pre-check: single SELECT
    is_valid, error_msg = validate_single_select(query)
    if not is_valid:
        return QueryResult(success=False, error_message=error_msg)

    try:
        cursor = conn.cursor()
        # Fetch max_rows + 1 to detect truncation
        cursor.execute(query)
        rows = cursor.fetchmany(max_rows + 1)
        truncated = len(rows) > max_rows
        if truncated:
            rows = rows[:max_rows]

        col_names = (
            [desc[0] for desc in cursor.description] if cursor.description else []
        )
        df = pd.DataFrame(rows, columns=col_names)

        return QueryResult(
            success=True,
            data=df,
            row_count=len(rows),
            truncated=truncated,
        )

    except sqlite3.DatabaseError as e:
        error_str = str(e)
        if "not authorized" in error_str.lower():
            msg = "Security Violation: Only SELECT queries on the `sales` table are permitted."
        elif "interrupted" in error_str.lower():
            msg = "Query exceeded the computational time limit (2 seconds, 1,000,000 opcodes). Simplify your query or add a WHERE clause."
        else:
            msg = f"Query failed: {error_str}"
        return QueryResult(success=False, error_message=msg)
    except Exception as e:
        return QueryResult(
            success=False,
            error_message=f"Unexpected error: {type(e).__name__}. Please report this.",
        )


def execute_predefined_query(
    conn: sqlite3.Connection, query_id: str, max_rows: int = 500
) -> QueryResult:
    """Execute a predefined approved business query.

    Args:
        conn: The secured SQLite connection.
        query_id: The query identifier (e.g., "1_total_revenue").
        max_rows: Maximum rows to return.

    Returns:
        QueryResult with success/data/error_message.
    """
    if query_id not in APPROVED_QUERIES:
        return QueryResult(success=False, error_message=f"Unknown query ID: {query_id}")

    query_def = APPROVED_QUERIES[query_id]
    return execute_custom_query(conn, query_def["sql"], max_rows)


def get_query_catalog() -> dict[str, dict[str, str]]:
    """Return the approved query catalog for UI population.

    Returns:
        Dict mapping query_id -> {title, question, sql}.
    """
    return APPROVED_QUERIES
