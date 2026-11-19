"""Module 1 — Data Immersion & Data Wrangling (placeholder).

Empty-state stub for Increment 1A. Upload, preview, profiling, cleaning,
validation and export UI is implemented in Increments 1B and 1C.
"""

import streamlit as st

st.header("Module 1 — Data Immersion & Data Wrangling")
st.divider()

if st.session_state.get("active_df") is None:
    st.info(
        "No dataset loaded. Upload a CSV or XLSX file, or run the demo-data "
        "generator to populate a synthetic dataset."
    )
else:
    st.write("Real Module 1 UI arrives in Increments 1B and 1C.")
