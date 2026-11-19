"""Module 4 — Power BI Showcase (placeholder).

Empty-state stub for Increment 1A. Screenshots and DAX measure cards arrive
in Increment 4. The authentic deliverable disclaimer is shown when the page
renders.
"""

import streamlit as st

st.header("Module 4 — Power BI Showcase")
st.divider()

st.caption(
    "*This module showcases the Power BI dashboard produced as Task 4 of ApexPlanet "
    "Software Pvt. Ltd. internship. Power BI is a separate desktop application; "
    "screenshots are presented here for academic evaluation. Interactive filtering "
    "is not available in this view.*"
)

if st.session_state.get("active_df") is None:
    st.info(
        "No dataset loaded. Upload a CSV or XLSX file, or enable Demo Mode "
        "in Module 1 to activate the showcase."
    )
else:
    st.write("Real Module 4 UI arrives in Increment 4.")
