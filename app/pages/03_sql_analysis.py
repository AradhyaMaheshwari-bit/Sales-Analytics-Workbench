"""Module 3 — SQL Analysis (Increment 3).

Implements the SQL Analysis interface with:
- Seven predefined business queries from the original internship Task-1.
- Custom SELECT query editor with security enforcement.
- Paginated result tables with execution feedback.

Design (SDD-MOD §2.1, SRS-SQL §2):
- Query selector dropdown with business question descriptions.
- Secure execution via authorizer and progress handler.
- User-friendly error messages for rejected or failed queries.
"""

from __future__ import annotations

import streamlit as st

from app.database.queries import (
    execute_custom_query,
    execute_predefined_query,
    get_query_catalog,
)

# Page configuration
st.set_page_config(page_title="SQL Analysis", page_icon="🔍")

st.header("Module 3 — SQL Analysis")
st.markdown("""
Execute predefined business queries or write custom SELECT queries against
the loaded dataset. All queries run under a strict security policy: only
read-only SELECT statements on the `sales` table are permitted.
""")
st.divider()

# Check if dataset is loaded
if st.session_state.get("active_df") is None:
    st.info(
        "No dataset loaded. Upload a CSV or XLSX file, or enable Demo Mode "
        "in Module 1 to activate the SQL workbench."
    )
    st.stop()

# Check if database connection is available
db_conn = st.session_state.get("db_conn")
if db_conn is None:
    st.warning(
        "Database connection not available. Please reload the dataset in Module 1."
    )
    st.stop()

# Query mode selector
query_mode = st.radio(
    "Query Mode",
    options=["Predefined Queries", "Custom SQL"],
    horizontal=True,
    help="Choose between predefined business queries or write your own SELECT query.",
)

st.divider()

if query_mode == "Predefined Queries":
    # Predefined queries section
    catalog = get_query_catalog()

    query_options = {f"{v['title']} — {v['question']}": k for k, v in catalog.items()}

    selected_display = st.selectbox(
        "Select a Business Query",
        options=list(query_options.keys()),
        help="Choose from seven predefined analytical queries.",
    )

    selected_id = query_options[selected_display]
    query_def = catalog[selected_id]

    # Display query details
    st.subheader(query_def["title"])
    st.markdown(f"**Business Question:** {query_def['question']}")

    with st.expander("View SQL Query", expanded=False):
        st.code(query_def["sql"], language="sql")

    # Execute button
    if st.button("▶ Execute Query", type="primary"):
        with st.spinner("Executing query..."):
            result = execute_predefined_query(db_conn, selected_id)

        if result.success:
            st.success(f"Query returned {result.row_count} row(s).")
            if result.truncated:
                st.warning(
                    "Results capped at 500 rows. Refine your query with WHERE or LIMIT."
                )
            st.dataframe(result.data, use_container_width=True, hide_index=True)
        else:
            st.error(result.error_message)

else:
    # Custom SQL section
    st.subheader("Custom SELECT Query")
    st.markdown("""
        Write a SELECT query against the `sales` table. The following columns
        are available:

        - `Order_ID`, `Order_Date`, `Customer_ID`, `Customer_Name`, `Age`, `Gender`
        - `City`, `Product`, `Category`, `Quantity`, `Unit_Price`, `Total_Sales`

        **Security Policy:**
        - Only SELECT queries are permitted.
        - Only the `sales` table is accessible.
        - Maximum execution time: 2 seconds.
        - Maximum rows returned: 500.
        """)

    # SQL editor
    custom_sql = st.text_area(
        "SQL Query",
        value="SELECT * FROM sales LIMIT 10;",
        height=150,
        help="Enter a single SELECT statement.",
    )

    # Execute button
    if st.button("▶ Execute Query", type="primary"):
        if not custom_sql.strip():
            st.warning("Please enter a SQL query.")
        else:
            with st.spinner("Executing query..."):
                result = execute_custom_query(db_conn, custom_sql)

            if result.success:
                st.success(f"Query returned {result.row_count} row(s).")
                if result.truncated:
                    st.warning(
                        "Results capped at 500 rows. Refine your query with WHERE or LIMIT."
                    )
                st.dataframe(result.data, use_container_width=True, hide_index=True)
            else:
                st.error(result.error_message)

# Sidebar information
with st.sidebar:
    st.markdown("---")
    st.markdown("### SQL Analysis Info")
    st.markdown("""
        **Predefined Queries:** 7 business queries from the original internship
        Task-1 repository.

        **Security:** All queries are executed under SQLite engine-level
        authorization that enforces SELECT-only access to the `sales` table.
        """)
