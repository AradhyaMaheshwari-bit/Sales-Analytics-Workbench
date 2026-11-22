"""Application entry point for the Sales Analytics Workbench.

Initializes Streamlit page configuration, the dark navy theme, shared
``st.session_state`` state, and the five-page navigation shell.
"""

import streamlit as st

from app.utils.logger import logger
from app.utils.styling import THEME_CSS

PAGES = [
    st.Page(
        "pages/01_data_immersion.py",
        title="Data Immersion & Wrangling",
        icon=":material/data_exploration:",
    ),
    st.Page(
        "pages/02_eda_bi.py",
        title="EDA & BI",
        icon=":material/bar_chart:",
    ),
    st.Page(
        "pages/03_sql_analysis.py",
        title="SQL Analysis",
        icon=":material/code:",
    ),
    st.Page(
        "pages/04_power_bi.py",
        title="Power BI Showcase",
        icon=":material/dashboard:",
    ),
    st.Page(
        "pages/05_statistical_validation.py",
        title="Statistical Validation",
        icon=":material/query_stats:",
    ),
]


def _initialize_session_state() -> None:
    """Seed shared session state once per session."""
    defaults = {
        "raw_df": None,
        "active_df": None,
        "cleaning_history": [],
        "db_conn": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def _inject_theme() -> None:
    """Inject the dark navy executive CSS theme."""
    st.markdown(THEME_CSS, unsafe_allow_html=True)


def _render_sidebar_identity() -> None:
    """Render the sidebar identity block."""
    st.sidebar.title("Sales Analytics Workbench")
    st.sidebar.caption("Aradhya Maheshwari — BCA Internship")
    st.sidebar.divider()


def _render_landing() -> None:
    """Render the landing page content."""
    st.title("Sales Analytics Workbench")
    st.subheader(
        "Unified internship demonstration — SDLC Phase 4, Increment 6 (Integration & Final QA)"
    )

    st.markdown("""
        This workbench demonstrates five analytical modules built during the ApexPlanet
        internship. Use the sidebar navigation to proceed.

        **Modules**
        1. **Data Immersion & Wrangling** — upload, preview, profile, clean, validate, export.
        2. **EDA & BI** — descriptive statistics, correlations, interactive charts.
        3. **SQL Analysis** — pre-built business queries against an in-memory SQLite database.
        4. **Power BI Showcase** — dashboard screenshots and DAX measure documentation.
        5. **Statistical Validation** — Welch's t-test with 95% confidence interval.

        **Current state:** No dataset is loaded. Upload a file or enable Demo Mode in Module 1
        before running analysis modules.
        """)

    st.info(
        "Select a module from the sidebar to begin. Modules render an empty state until a "
        "dataset is active."
    )

    logger.info("Application launched — Increment 6")


def main() -> None:
    """Boot the application."""
    st.set_page_config(
        page_title="Sales Analytics Workbench",
        page_icon=":material/analytics:",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    _initialize_session_state()
    _inject_theme()
    _render_sidebar_identity()

    pg = st.navigation(PAGES)

    # Landing content renders on every page transition as a header; navigation
    # below renders the selected module page.
    _render_landing()

    pg.run()


if __name__ == "__main__":
    main()
