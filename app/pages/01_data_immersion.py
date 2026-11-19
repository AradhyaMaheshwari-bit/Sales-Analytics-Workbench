"""Module 1 — Data Immersion & Data Wrangling (Increment 1B).

Provides file upload, pre-parse validation, multi-format parsing, schema mapping,
dataset preview, and comprehensive data profiling.
"""

import pandas as pd
import streamlit as st

from app.models.dataset_schema import apply_column_mapping
from app.services.data_loader import DataLoader
from app.services.profiler import profile_dataframe

st.header("Module 1 — Data Immersion & Data Wrangling")
st.divider()

loader = DataLoader()

# Session state initialization check
if "raw_df" not in st.session_state:
    st.session_state["raw_df"] = None
if "active_df" not in st.session_state:
    st.session_state["active_df"] = None
if "schema_report" not in st.session_state:
    st.session_state["schema_report"] = None
if "load_info" not in st.session_state:
    st.session_state["load_info"] = {}


# --- Sidebar / Top Controls for Ingestion ---
tab_upload, tab_bundled = st.tabs(
    ["📁 File Upload", "🏛️ Internship Dataset (Scenario B)"]
)

with tab_upload:
    uploaded_file = st.file_uploader(
        "Upload Sales Dataset (CSV or XLSX)",
        type=["csv", "xlsx"],
        help="Upload CSV or Excel files up to 50 MB matching or mapping to the 12-column sales schema.",
    )

    if uploaded_file is not None:
        file_bytes = uploaded_file.getvalue()
        file_name = uploaded_file.name
        load_result = loader.load_file(file_bytes, file_name)

        if load_result.success:
            st.session_state["raw_df"] = load_result.dataframe.copy(deep=True)
            # Apply automatic column mapping if columns match synonyms
            if load_result.schema_report and load_result.schema_report.mapped_columns:
                mapped_df = apply_column_mapping(
                    load_result.dataframe, load_result.schema_report.mapped_columns
                )
                st.session_state["active_df"] = mapped_df
            else:
                st.session_state["active_df"] = load_result.dataframe.copy(deep=True)

            st.session_state["schema_report"] = load_result.schema_report
            st.session_state["load_info"] = load_result.load_info
            st.success(
                f"Successfully loaded '{file_name}' ({load_result.load_info.get('row_count', 0):,} rows, {load_result.load_info.get('column_count', 0)} columns)."
            )
        else:
            st.error(load_result.error_message or "Failed to load dataset.")

with tab_bundled:
    st.markdown("""
    Load the private internship dataset from `data/raw/internship_dataset.xlsx` (Scenario B).
    If the file is not present locally, place it in `data/raw/` or use file upload.
    """)
    if st.button("Load Bundled Internship Dataset"):
        bundled_result = loader.load_bundled_dataset()
        if bundled_result.success:
            st.session_state["raw_df"] = bundled_result.dataframe.copy(deep=True)
            if (
                bundled_result.schema_report
                and bundled_result.schema_report.mapped_columns
            ):
                mapped_df = apply_column_mapping(
                    bundled_result.dataframe,
                    bundled_result.schema_report.mapped_columns,
                )
                st.session_state["active_df"] = mapped_df
            else:
                st.session_state["active_df"] = bundled_result.dataframe.copy(deep=True)

            st.session_state["schema_report"] = bundled_result.schema_report
            st.session_state["load_info"] = bundled_result.load_info
            st.success("Successfully loaded bundled internship dataset.")
        else:
            st.warning(bundled_result.error_message)


st.divider()

# --- Main View: Empty State vs Loaded Dataset ---
active_df: pd.DataFrame | None = st.session_state.get("active_df")
schema_report = st.session_state.get("schema_report")
load_info = st.session_state.get("load_info", {})

if active_df is None or active_df.empty:
    st.info(
        "No dataset loaded. Upload a CSV or XLSX file above, or load the bundled "
        "internship dataset to begin data immersion and profiling."
    )
else:
    # --- Schema Report & Validation Banner ---
    if schema_report and schema_report.missing_canonical:
        st.warning(
            f"⚠️ Schema Notice: The dataset is missing canonical columns: {schema_report.missing_canonical}. "
            "Some downstream analytics or queries may be limited."
        )

    # --- Dataset Preview Section ---
    st.subheader("1. Dataset Preview")
    col_slider, col_info = st.columns([2, 2])
    with col_slider:
        preview_rows = st.slider(
            "Preview rows", min_value=5, max_value=100, value=10, step=5
        )
    with col_info:
        st.metric("Source File", load_info.get("file_name", "Unknown"))
        st.metric("Total Rows", f"{len(active_df):,}")
        st.metric("Total Columns", f"{len(active_df.columns)}")

    st.dataframe(active_df.head(preview_rows), use_container_width=True)

    st.divider()

    # --- Data Profiling Section ---
    st.subheader("2. Comprehensive Data Profiling")
    metrics = profile_dataframe(active_df)

    # KPI Metrics Row
    kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
    with kpi1:
        st.metric("Rows", f"{metrics.row_count:,}")
    with kpi2:
        st.metric("Columns", f"{metrics.column_count}")
    with kpi3:
        mem_kb = metrics.memory_usage_bytes / 1024
        mem_str = f"{mem_kb / 1024:.2f} MB" if mem_kb >= 1024 else f"{mem_kb:.1f} KB"
        st.metric("Memory", mem_str)
    with kpi4:
        st.metric(
            "Missing Cells",
            f"{metrics.missing_total:,}",
            f"{metrics.missing_percentage:.2f}%",
            delta_color="inverse",
        )
    with kpi5:
        st.metric(
            "Duplicate Rows",
            f"{metrics.duplicate_row_count:,}",
            f"{metrics.duplicate_percentage:.2f}%",
            delta_color="inverse",
        )

    # Column Profile Table
    st.markdown("#### Column Profiling & Statistics")
    profile_rows = []
    for _col_name, cprof in metrics.columns.items():
        profile_rows.append(
            {
                "Column": cprof.name,
                "Type": cprof.dtype,
                "Non-Null": f"{cprof.non_null_count:,}",
                "Null Count": f"{cprof.null_count:,} ({cprof.null_percentage:.1f}%)",
                "Unique": f"{cprof.unique_count:,}"
                if cprof.unique_count is not None
                else "—",
                "Mean": f"{cprof.mean:,.2f}" if cprof.mean is not None else "—",
                "Min": f"{cprof.min_val:,.2f}" if cprof.min_val is not None else "—",
                "Max": f"{cprof.max_val:,.2f}" if cprof.max_val is not None else "—",
                "Anomaly": cprof.potential_type_message or "None",
            }
        )

    profile_df = pd.DataFrame(profile_rows)
    st.dataframe(profile_df, use_container_width=True)

    # Type anomaly alerts if any
    anomalies = [c for c in metrics.columns.values if c.potential_type_issue]
    if anomalies:
        st.warning("⚠️ **Potential Data Type Anomalies Detected:**")
        for anom in anomalies:
            st.markdown(f"- **{anom.name}**: {anom.potential_type_message}")
