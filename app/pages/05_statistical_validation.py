"""Module 5 — Statistical Validation (placeholder).

Empty-state stub for Increment 1A. Welch's t-test and 95% CI arrive in
Increment 5. Edge guards and the historical benchmark assertion are
configured to be active only on the unmodified internship dataset.
"""

import streamlit as st

st.header("Module 5 — Statistical Validation")
st.divider()

if st.session_state.get("active_df") is None:
    st.info(
        "No dataset loaded. Upload a CSV or XLSX file, or enable Demo Mode "
        "in Module 1 to activate the statistical analysis."
    )
else:
    st.write("Real Module 5 UI arrives in Increment 5.")
