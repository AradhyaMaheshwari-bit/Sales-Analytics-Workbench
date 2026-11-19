"""Module 2 — Exploratory Data Analysis & BI (placeholder).

Empty-state stub for Increment 1A. Descriptive statistics, correlation
analysis and interactive Plotly charts arrive in Increment 2.
"""

import streamlit as st

st.header("Module 2 — EDA & BI")
st.divider()

if st.session_state.get("active_df") is None:
    st.info(
        "No dataset loaded. Upload a CSV or XLSX file, or enable Demo Mode in "
        "Module 1 to populate the analysis modules."
    )
else:
    st.write("Real Module 2 UI arrives in Increment 2.")
