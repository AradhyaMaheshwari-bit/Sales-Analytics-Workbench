"""Tests for SQL statement validation (Increment 3)."""

from app.database.queries import (
    detect_multi_statement,
    validate_single_select,
)


class TestDetectMultiStatement:
    """Tests for the multi-statement detection function."""

    # Basic cases
    def test_empty_string(self):
        assert not detect_multi_statement("")

    def test_whitespace_only(self):
        assert not detect_multi_statement("   \n\t  ")

    def test_single_statement_no_semicolon(self):
        assert not detect_multi_statement("SELECT 1")

    def test_single_statement_with_semicolon(self):
        assert not detect_multi_statement("SELECT 1;")

    def test_single_statement_with_whitespace_and_semicolon(self):
        assert not detect_multi_statement("   SELECT 1;   ")

    def test_two_statements_separated_by_semicolon(self):
        assert detect_multi_statement("SELECT 1; DELETE 2")

    # String literal cases
    def test_semicolon_in_single_quoted_string(self):
        assert not detect_multi_statement("SELECT 'A;B'")

    def test_semicolon_in_double_quoted_identifier(self):
        assert not detect_multi_statement('SELECT "Column;Name" FROM sales')

    def test_semicolon_in_double_quoted_string(self):
        # SQLite also allows double-quoted strings in some contexts
        assert not detect_multi_statement('SELECT "A;B"')

    # Doubled quotes (SQL standard escaping)
    def test_doubled_single_quote(self):
        assert not detect_multi_statement("SELECT 'O''Reilly'")

    def test_doubled_double_quote(self):
        assert not detect_multi_statement('SELECT "Table""Name" FROM sales')

    def test_doubled_quotes_with_semicolon(self):
        assert not detect_multi_statement("SELECT 'O''Reilly;Smith'")

    # Comments
    def test_leading_line_comment(self):
        assert not detect_multi_statement("-- comment\nSELECT 1;")

    def test_leading_block_comment(self):
        assert not detect_multi_statement("/* comment */ SELECT 1;")

    def test_trailing_line_comment(self):
        assert not detect_multi_statement("SELECT 1; -- DELETE 2")

    def test_trailing_block_comment(self):
        assert not detect_multi_statement("SELECT 1; /* DELETE 2 */")

    def test_comments_between_statements(self):
        # This should be detected as multiple statements
        assert detect_multi_statement("SELECT 1; -- comment\nSELECT 2")

    def test_block_comment_between_statements(self):
        assert detect_multi_statement("SELECT 1; /* comment */ SELECT 2")

    # Multiple statements
    def test_multiple_statements(self):
        assert detect_multi_statement("SELECT 1; SELECT 2")

    def test_multiple_semicolons(self):
        assert detect_multi_statement("SELECT 1;; DELETE 2")
        assert detect_multi_statement("SELECT 1; ; DELETE 2")

    def test_append_after_valid_select(self):
        assert detect_multi_statement("SELECT * FROM sales; DROP TABLE sales")

    # Comment-only input
    def test_comment_only_input(self):
        assert not detect_multi_statement("-- just a comment")
        assert not detect_multi_statement("/* just a comment */")

    # CTEs (single statement with semicolon)
    def test_cte_single_statement(self):
        assert not detect_multi_statement("WITH cte AS (SELECT 1) SELECT * FROM cte;")

    def test_cte_without_semicolon(self):
        assert not detect_multi_statement("WITH cte AS (SELECT 1) SELECT * FROM cte")


class TestValidateSingleSelect:
    """Tests for the single-SELECT validation function."""

    def test_valid_select(self):
        is_valid, msg = validate_single_select("SELECT * FROM sales;")
        assert is_valid
        assert msg == ""

    def test_valid_select_no_semicolon(self):
        is_valid, msg = validate_single_select("SELECT * FROM sales")
        assert is_valid
        assert msg == ""

    def test_valid_cte(self):
        is_valid, msg = validate_single_select(
            "WITH cte AS (SELECT 1) SELECT * FROM cte;"
        )
        assert is_valid
        assert msg == ""

    def test_empty_query_rejected(self):
        is_valid, msg = validate_single_select("")
        assert not is_valid
        assert "empty" in msg.lower()

    def test_whitespace_only_rejected(self):
        is_valid, msg = validate_single_select("   ")
        assert not is_valid
        assert "empty" in msg.lower()

    def test_comment_only_rejected(self):
        is_valid, msg = validate_single_select("-- comment")
        assert not is_valid
        assert "empty" in msg.lower()

    def test_non_select_rejected(self):
        is_valid, msg = validate_single_select("INSERT INTO sales VALUES (1);")
        assert not is_valid
        assert "Only SELECT" in msg

    def test_update_rejected(self):
        is_valid, msg = validate_single_select("UPDATE sales SET x = 1;")
        assert not is_valid

    def test_delete_rejected(self):
        is_valid, msg = validate_single_select("DELETE FROM sales;")
        assert not is_valid

    def test_create_rejected(self):
        is_valid, msg = validate_single_select("CREATE TABLE x (y INT);")
        assert not is_valid

    def test_multiple_statements_rejected(self):
        is_valid, msg = validate_single_select("SELECT 1; SELECT 2;")
        assert not is_valid
        assert "Multiple" in msg

    def test_append_statement_after_select_rejected(self):
        is_valid, msg = validate_single_select("SELECT 1; DROP TABLE sales;")
        assert not is_valid
        assert "Multiple" in msg

    def test_select_with_trailing_comment_valid(self):
        is_valid, msg = validate_single_select("SELECT 1; -- comment")
        assert is_valid

    def test_select_with_trailing_block_comment_valid(self):
        is_valid, msg = validate_single_select("SELECT 1; /* comment */")
        assert is_valid

    def test_semicolon_in_string_literal_valid(self):
        is_valid, msg = validate_single_select("SELECT 'A;B' FROM sales;")
        assert is_valid

    def test_semicolon_in_quoted_identifier_valid(self):
        is_valid, msg = validate_single_select('SELECT "Col;Name" FROM sales;')
        assert is_valid

    def test_comment_marker_in_string_literal_not_stripped(self):
        is_valid, msg = validate_single_select("SELECT '-- not a comment' FROM sales;")
        assert is_valid

    def test_block_comment_marker_in_string_literal_not_stripped(self):
        is_valid, msg = validate_single_select(
            "SELECT '/* not a comment */' FROM sales;"
        )
        assert is_valid

    def test_comment_marker_in_identifier_not_stripped(self):
        is_valid, msg = validate_single_select('SELECT "col--name" FROM sales;')
        assert is_valid

    def test_backslash_in_string_literal_not_escape(self):
        # Backslash is not an escape in standard SQLite; semicolon after it in string is protected
        is_valid, msg = validate_single_select(r"SELECT 'C:\path;dir' FROM sales;")
        assert is_valid

    def test_cte_with_insert_rejected(self):
        is_valid, msg = validate_single_select(
            "WITH cte AS (SELECT 1) INSERT INTO sales VALUES (1);"
        )
        assert not is_valid
        assert "Security Violation" in msg

    def test_cte_with_delete_rejected(self):
        is_valid, msg = validate_single_select(
            "WITH cte AS (SELECT 1) DELETE FROM sales;"
        )
        assert not is_valid
        assert "Security Violation" in msg

    def test_cte_with_update_rejected(self):
        is_valid, msg = validate_single_select(
            "WITH cte AS (SELECT 1) UPDATE sales SET Total_Sales = 0;"
        )
        assert not is_valid
        assert "Security Violation" in msg

    def test_non_select_error_message_is_security_violation(self):
        is_valid, msg = validate_single_select("INSERT INTO sales VALUES (1);")
        assert not is_valid
        assert "Security Violation" in msg
