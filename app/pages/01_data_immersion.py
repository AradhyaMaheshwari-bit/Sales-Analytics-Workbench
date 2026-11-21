"""Module 1 — Data Immersion & Data Wrangling (Increment 1C).

Provides source selection (upload / bundled scenario B), dataset preview,
comprehensive data profiling, configurable cleaning pipeline, business-rule
validation, undo/reset/replacement state handling, and cleaned-data export.

Design: ui-ux-design.md §5.1 (tabs), data-architecture.md §2-§5, module-design.md §2.3.
"""

import pandas as pd
import streamlit as st

from app.database.db_manager import DatabaseManager
from app.models.dataset_schema import apply_column_mapping
from app.services.cleaner import clean_dataframe
from app.services.data_loader import DataLoader
from app.services.profiler import profile_dataframe
from app.services.report_generator import (
    df_to_xlsx_bytes,
    generate_cleaned_export,
    generate_excel_report,
    generate_timestamped_filename,
)
from app.services.validator import validate_business_rules

st.header("Module 1 — Data Immersion & Data Wrangling")
st.divider()

loader = DataLoader()
db_manager = DatabaseManager()

# Session state initialisation (mirrors design §2.1)
for key, default in (
    ("raw_df", None),
    ("active_df", None),
    ("cleaning_history", []),
    ("column_mapping", {}),
    ("db_conn", None),
    ("load_info", {}),
    ("schema_report", None),
):
    if key not in st.session_state:
        st.session_state[key] = default


def _rebuild_db(df: pd.DataFrame) -> None:
    """Rebuild the per-session in-memory SQLite sales table from *df*."""
    st.session_state["db_conn"] = db_manager.rebuild(df)


def _handle_upload_source() -> None:
    """Render source selection (upload vs. bundled Scenario B)."""
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
            if load_result.schema_report and load_result.schema_report.mapped_columns:
                st.session_state["column_mapping"] = dict(
                    load_result.schema_report.mapped_columns
                )
                st.session_state["active_df"] = apply_column_mapping(
                    load_result.dataframe, load_result.schema_report.mapped_columns
                )
            else:
                st.session_state["active_df"] = load_result.dataframe.copy(deep=True)
            st.session_state["schema_report"] = load_result.schema_report
            st.session_state["load_info"] = load_result.load_info
            st.success(
                f"Successfully loaded '{file_name}' "
                f"({load_result.load_info.get('row_count', 0):,} rows, "
                f"{load_result.load_info.get('column_count', 0)} columns)."
            )
        else:
            st.error(load_result.error_message or "Failed to load dataset.")
        return

    st.markdown(
        """
    Load the synthetic demo dataset from `data/raw/synthetic_demo_dataset.xlsx`.
    If the file is not present locally, generate it via `scripts/generate_demo_data.py` or use file upload.
    """
    )
    if st.button("Load Synthetic Demo Dataset"):
        bundled_result = loader.load_bundled_dataset()
        if bundled_result.success:
            st.session_state["raw_df"] = bundled_result.dataframe.copy(deep=True)
            if (
                bundled_result.schema_report
                and bundled_result.schema_report.mapped_columns
            ):
                st.session_state["column_mapping"] = dict(
                    bundled_result.schema_report.mapped_columns
                )
                st.session_state["active_df"] = apply_column_mapping(
                    bundled_result.dataframe,
                    bundled_result.schema_report.mapped_columns,
                )
            else:
                st.session_state["active_df"] = bundled_result.dataframe.copy(deep=True)
            st.session_state["schema_report"] = bundled_result.schema_report
            st.session_state["load_info"] = bundled_result.load_info
            st.success("Successfully loaded synthetic demo dataset.")
        else:
            st.warning(bundled_result.error_message)


def _render_preview() -> None:
    """Tab 1 content: source selection + dataset preview + column mapping."""
    st.subheader("1. Dataset Preview")

    _handle_upload_source()

    active_df: pd.DataFrame | None = st.session_state.get("active_df")

    if active_df is None or active_df.empty:
        st.info(
            "No dataset loaded. Upload a CSV or XLSX file above, or load the synthetic "
            "demo dataset to begin data immersion and profiling."
        )
        return

    schema_report = st.session_state.get("schema_report")
    if schema_report is not None and schema_report.missing_canonical:
        st.warning(
            f"⚠️ Schema Notice: The dataset is missing canonical columns: "
            f"{schema_report.missing_canonical}. Some downstream analytics or queries may be limited."
        )

    col_slider, col_info = st.columns([2, 2])
    with col_slider:
        preview_rows = st.slider(
            "Preview rows", min_value=5, max_value=100, value=10, step=5
        )
    with col_info:
        st.metric(
            "Source File",
            st.session_state.get("load_info", {}).get("file_name", "Unknown"),
        )
        st.metric("Total Rows", f"{len(active_df):,}")
        st.metric("Total Columns", f"{len(active_df.columns)}")

    st.dataframe(active_df.head(preview_rows), use_container_width=True)

    st.divider()
    st.caption(
        "Full schema columns (canonical order): " + ", ".join(list(active_df.columns))
    )


def _render_profiling() -> None:
    """Tab 2 content: comprehensive data profiling."""
    active_df: pd.DataFrame | None = st.session_state.get("active_df")
    if active_df is None or active_df.empty:
        return

    st.subheader("2. Comprehensive Data Profiling")
    metrics = profile_dataframe(active_df)

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

    anomalies = [c for c in metrics.columns.values() if c.potential_type_issue]
    if anomalies:
        st.warning("⚠️ **Potential Data Type Anomalies Detected:**")
        for anom in anomalies:
            st.markdown(f"- **{anom.name}**: {anom.potential_type_message}")


def _render_cleaning() -> None:
    """Tab 3 content: configurable cleaning pipeline + history/undo/reset."""
    active_df: pd.DataFrame | None = st.session_state.get("active_df")
    if active_df is None or active_df.empty:
        return

    st.subheader("3. Cleaning Pipeline")

    col_strat, col_dupes, col_dates = st.columns(3)
    with col_strat:
        missing_strategy = st.selectbox(
            "Missing Value Strategy",
            options=["drop", "fill_mean", "fill_median", "fill_mode", "leave"],
            index=0,
            help="FR-08: configurable missing-value handling.",
        )
    with col_dupes:
        _ = st.toggle(
            "Remove Duplicates", value=False, help="FR-08: duplicate removal toggle."
        )
    with col_dates:
        normalise_dates_flag = st.toggle(
            "Normalise Order_Date to YYYY-MM-DD", value=True
        )

    st.session_state["missing_subset"] = st.multiselect(
        "Columns to apply missing-value strategy to (empty = all)",
        options=[
            c for c in active_df.columns if pd.api.types.is_numeric_dtype(active_df[c])
        ],
        default=[],
    )
    missing_subset = st.session_state["missing_subset"]

    if st.button("Execute Cleaning", type="primary"):
        cleaned_df, logs = clean_dataframe(
            active_df,
            missing_strategy=missing_strategy,
            missing_subset=missing_subset if missing_strategy == "drop" else None,
            remove_dup_keep="first",
            type_coercion=True,
            date_normalisation=normalise_dates_flag,
        )
        st.session_state["cleaning_history"].append(
            {
                "previous_df": active_df.copy(deep=True),
                "logs": logs,
            }
        )
        st.session_state["active_df"] = cleaned_df
        _rebuild_db(cleaned_df)
        st.success(
            f"Dataset cleaned: {len(cleaned_df):,} rows (was {len(active_df):,}). "
            f"Operations applied: {[log.operation for log in logs]}."
        )

    cleaning_history = st.session_state.get("cleaning_history", [])
    st.markdown("#### Cleaning Summary & History")
    if not cleaning_history:
        st.caption("No cleaning operations have been executed yet.")
    else:
        for entry in reversed(cleaning_history):
            for log in entry.get("logs", []):
                st.markdown(
                    f"- Step {log.step}: {log.operation} — columns: {log.columns_affected}, "
                    f"rows {log.rows_before} → {log.rows_after}"
                )
                if log.operation == "date_normalisation":
                    st.markdown(
                        f"  - Valid rows: {log.details.get('valid_rows', 0)}; "
                        f"Unparseable rows: {log.details.get('unparseable_rows', 0)}"
                    )

    undo_col, reset_col = st.columns(2)
    with undo_col:
        if st.button("Undo Last Cleaning Step"):
            if cleaning_history:
                entry = cleaning_history.pop()
                restored = entry.get("previous_df")
                if restored is not None:
                    st.session_state["active_df"] = restored.copy(deep=True)
                    _rebuild_db(st.session_state["active_df"])
    with reset_col:
        if st.button("Reset to Raw Data"):
            st.session_state["cleaning_history"] = []
            st.session_state["active_df"] = st.session_state["raw_df"].copy(deep=True)
            _rebuild_db(st.session_state["active_df"])


def _render_validation_and_export() -> None:
    """Tab 4 content: business-rule validation + cleaned data export."""
    active_df: pd.DataFrame | None = st.session_state.get("active_df")
    if active_df is None or active_df.empty:
        return

    st.subheader("4. Business Rule Validation & Export")

    validation_summary = validate_business_rules(active_df)
    st.markdown("#### Validation Summary")
    for rule_name, result in validation_summary.checks.items():
        col_r, col_f = st.columns(2)
        with col_r:
            st.metric(f"Rule: {rule_name} — Passed", f"{result.passed}")
        with col_f:
            st.metric(f"Rule: {rule_name} — Failed", f"{result.failed}")

    st.markdown("#### Validation Failure Details")
    if not validation_summary.overall_pass:
        for rule_name, result in validation_summary.checks.items():
            if result.failed > 0:
                st.markdown(f"**{rule_name} failures:**")
                for detail in result.failure_details:
                    st.markdown(f"- {detail}")

    st.markdown("#### Cleaned Dataset Export")
    export_col, report_col = st.columns(2)
    with export_col:
        if st.button("Generate Cleaned Export"):
            bytes_out, filename = generate_cleaned_export(active_df, "csv")
            st.download_button(
                label="Download Cleaned CSV",
                data=bytes_out,
                file_name=filename,
                mime="text/csv",
            )
            xlsx_bytes = df_to_xlsx_bytes(active_df)
            xlsx_name = generate_timestamped_filename("sales_dataset", "xlsx")
            st.download_button(
                label="Download Cleaned XLSX",
                data=xlsx_bytes,
                file_name=xlsx_name,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
    with report_col:
        if st.button("Generate Excel Report"):
            report_bytes, report_name = generate_excel_report(
                active_df,
                metrics=profile_dataframe(active_df),
                validation=validation_summary,
            )
            st.download_button(
                label="Download Excel Report (.xlsx)",
                data=report_bytes,
                file_name=report_name,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )


tab_preview, tab_profiling, tab_cleaning, tab_validation = st.tabs(
    [
        "📊 Data Preview",
        "🔍 Data Profiling",
        "🧹 Cleaning Pipeline",
        "✅ Validation & Export",
    ]
)

with tab_preview:
    _render_preview()

with tab_profiling:
    _render_profiling()

with tab_cleaning:
    _render_cleaning()

with tab_validation:
    _render_validation_and_export()
