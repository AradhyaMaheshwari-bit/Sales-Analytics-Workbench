"""Export service: cleaned-dataset CSV/XLSX and multi-sheet Excel reports.

Implements FR-10 (Cleaned Dataset Export) and FR-17 (Excel Report
Generation) with the Increment 1C scope agreed with the project owner:

- Cleaned-dataset CSV (UTF-8) and XLSX (openpyxl) exports, with a
  ``cleaned`` suffix / timestamp in the filename (FR-10 AC-5).
- Multi-sheet XLSX *report*: **Summary** and **Statistics** sheets.
  The **Query Results** sheet of FR-17 is deferred to Increment 3, when the
  seven SQL queries exist — see the module docstring in
  ``docs/04-implementation/phase-4-implementation-plan.md`` and the
  CHANGELOG entry for this increment.

The service is pure: it accepts a DataFrame (plus optional profiling /
validation data) and returns bytes — no Streamlit, no disk writes, no
mutated inputs.
"""

from __future__ import annotations

import io
from datetime import datetime

import pandas as pd

from app.models.validation_models import (
    ProfilingMetrics,
    ValidationSummary,
)


def generate_timestamped_filename(
    base_name: str,
    extension: str,
    cleaned: bool = True,
) -> str:
    """Build a filename with a ``cleaned`` suffix and a timestamp.

    Example: ``"internship_dataset_cleaned_20261119_143015.csv"``
    (FR-10 AC-5: file name includes a timestamp or 'cleaned' suffix).
    """
    safe_base = base_name.replace(" ", "_")
    safe_base = safe_base.rsplit(".", 1)[0] if "." in safe_base else safe_base
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    cleaned_tag = "_cleaned" if cleaned else ""
    return f"{safe_base}{cleaned_tag}_{ts}.{extension.lower()}"


def df_to_csv_bytes(df: pd.DataFrame) -> bytes:
    """Serialise a DataFrame to CSV bytes with UTF-8 encoding (FR-10 AC-2)."""
    csv_str = df.to_csv(index=False, encoding="utf-8")
    return csv_str.encode("utf-8")


def df_to_xlsx_bytes(df: pd.DataFrame) -> bytes:
    """Serialise a DataFrame to XLSX bytes via openpyxl (FR-10 AC-3)."""
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="Cleaned_Data", index=False)
    return buffer.getvalue()


def generate_cleaned_export(
    df: pd.DataFrame,
    file_format: str,
) -> tuple[bytes, str]:
    """Export cleaned data as CSV or XLSX.

    Returns ``(bytes, suggested_filename)``.  Raises ValueError for
    unsupported formats.
    """
    if file_format == "csv":
        return df_to_csv_bytes(df), generate_timestamped_filename(
            "sales_dataset", "csv"
        )
    if file_format in ("xlsx", "xlsm"):
        return df_to_xlsx_bytes(df), generate_timestamped_filename(
            "sales_dataset", "xlsx"
        )
    raise ValueError(
        f"Unsupported export format: {file_format!r}. Use 'csv' or 'xlsx'."
    )


# ---------------------------------------------------------------------------
# FR-17 Excel report (Summary + Statistics sheets; Query Results → Increment 3)
# ---------------------------------------------------------------------------


def _summary_sheet(metrics: ProfilingMetrics | None, df: pd.DataFrame) -> pd.DataFrame:
    """Build the *Summary* sheet: dataset-level overview metrics."""
    rows = [
        ("Total Rows", str(len(df))),
        ("Total Columns", str(len(df.columns))),
        ("Missing Cells", str(int(df.isna().sum().sum()))),
        ("Duplicate Rows", str(int(df.duplicated().sum()))),
    ]
    if metrics is not None:
        rows.append(("Memory Usage (bytes)", str(metrics.memory_usage_bytes)))
        rows.append(("Missing Percentage", f"{metrics.missing_percentage:.2f}%"))
        rows.append(("Duplicate Percentage", f"{metrics.duplicate_percentage:.2f}%"))
    rows.append(("Sheet Note", "Query Results sheet deferred to Increment 3"))
    return pd.DataFrame(rows, columns=["Metric", "Value"])


def _statistics_sheet(df: pd.DataFrame) -> pd.DataFrame:
    """Build the *Statistics* sheet: per-column descriptive statistics."""
    rows: list[dict[str, object]] = []
    for col in df.columns:
        series = df[col]
        row: dict[str, object] = {
            "Column": str(col),
            "Dtype": str(series.dtype),
            "Non-Null": int(series.count()),
            "Null": int(series.isna().sum()),
            "Unique": int(series.nunique(dropna=True)),
        }
        if pd.api.types.is_numeric_dtype(series):
            row["Mean"] = round(float(series.mean()), 4) if series.count() else None
            row["Std"] = round(float(series.std()), 4) if series.count() > 1 else None
            row["Min"] = round(float(series.min()), 4) if series.count() else None
            row["Max"] = round(float(series.max()), 4) if series.count() else None
        rows.append(row)
    return pd.DataFrame(rows)


def generate_excel_report(
    df: pd.DataFrame,
    metrics: ProfilingMetrics | None = None,
    validation: ValidationSummary | None = None,
) -> tuple[bytes, str]:
    """Generate the multi-sheet FR-17 Excel report.

    Sheets (Increment 1C scope):
    1. **Summary** — dataset overview + metric rows.
    2. **Statistics** — per-column descriptive statistics.
    3. **Validation** — business-rule pass/fail counts (present only when
       *validation* is supplied).

    The FR-17 **Query Results** sheet is deferred to Increment 3.

    Returns ``(bytes, suggested_filename)``.
    """
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        _summary_sheet(metrics, df).to_excel(writer, sheet_name="Summary", index=False)
        _statistics_sheet(df).to_excel(writer, sheet_name="Statistics", index=False)
        if validation is not None:
            _validation_sheet(validation).to_excel(
                writer, sheet_name="Validation", index=False
            )

    filename = generate_timestamped_filename("sales_report", "xlsx", cleaned=False)
    return buffer.getvalue(), filename


def _validation_sheet(validation: ValidationSummary) -> pd.DataFrame:
    """Flatten a ValidationSummary into a table for the Validation sheet."""
    rows: list[dict[str, object]] = []
    for rule_name, result in validation.checks.items():
        rows.append(
            {
                "Rule": rule_name,
                "Passed": result.passed,
                "Failed": result.failed,
                "Passed (%)": round(result.passed_percentage, 2),
                "Overall Pass": validation.overall_pass,
            }
        )
    rows.append(
        {
            "Rule": "TOTAL",
            "Passed": validation.total_rows,
            "Failed": 0,
            "Passed (%)": "",
            "Overall Pass": validation.overall_pass,
        }
    )
    return pd.DataFrame(rows)
