"""Module 3 — SQL Analysis (placeholder).

Empty-state stub for Increment 1A. Pre-built SQL queries against the
in-memory SQLite database arrive in Increment 3.
"""

import streamlit as st

st.header("Module 3 — SQL Analysis")
st.divider()

if st.session_state.get("active_df") is None:
    st.info(
        "No dataset loaded. Upload a CSV or XLSX file, or enable Demo Mode "
        "in Module 1 to activate the SQL workbench."
    )
else:
    st.write("Real Module 3 UI arrives in Increment 3.")
