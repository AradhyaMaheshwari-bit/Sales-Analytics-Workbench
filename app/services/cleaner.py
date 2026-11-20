"""Non-mutating data cleaning service for the Sales Analytics Workbench.

Executes configurable data cleaning operations (missing-value strategies,
duplicate removal, type coercion, date normalisation) and returns a new
DataFrame together with CleaningLog entries for history/undo support.

NFR-R-02 / TD-07: the input DataFrame is never mutated — every operation
works on a deep copy.  The returned logs are intended to be pushed onto the
``cleaning_history`` stack (undo support); reset restores ``raw_df``.

Date normalisation follows the approved strategy (data-architecture §5):
valid dates become ``YYYY-MM-DD`` strings, unparseable values become
``None`` (NULL), and the affected row is *preserved* — never silently
dropped — with the count reported in the cleaning summary.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from app.models.validation_models import CleaningLog

# Default per-column dtype coercion applied by the cleaning pipeline
# (matches EXPECTED_DTYPES in app/models/dataset_schema.py).
DEFAULT_TYPE_MAP: dict[str, str] = {
    "Quantity": "int64",
    "Unit_Price": "float64",
    "Age": "float64",
    "Total_Sales": "float64",
}

MISSING_STRATEGIES = ("drop", "fill_mean", "fill_median", "fill_mode", "leave")


def handle_missing_values(
    df: pd.DataFrame,
    strategy: str = "drop",
    subset: list[str] | None = None,
) -> tuple[pd.DataFrame, CleaningLog]:
    """Apply a missing-value strategy and return a new DataFrame + log entry.

    Supported strategies:
    - ``"drop"``:       drop rows containing nulls (within *subset* columns,
                       or across all columns when *subset* is None).
    - ``"fill_mean"``:  fill numeric nulls with the column mean.
    - ``"fill_median"``: fill numeric nulls with the column median.
    - ``"fill_mode"``:  fill numeric nulls with the column mode (first mode).
    - ``"leave"``:      no change.

    The input DataFrame is never mutated.
    """
    if strategy not in MISSING_STRATEGIES:
        raise ValueError(
            f"Unknown missing-value strategy: {strategy!r}. "
            f"Expected one of {MISSING_STRATEGIES}."
        )

    rows_before = len(df)
    result_df = df.copy(deep=True)

    if strategy == "leave":
        return result_df, CleaningLog(
            step=1,
            operation="missing_value_strategy",
            columns_affected=[],
            rows_before=rows_before,
            rows_after=rows_before,
            details={"strategy": "leave", "removed_rows": 0},
        )

    if strategy == "drop":
        subset_cols = [c for c in (subset or []) if c in result_df.columns]
        if subset and subset_cols != list(subset):
            missing_cols = [c for c in subset if c not in result_df.columns]
            # Unknown subset columns are ignored rather than raising, so the
            # pipeline never crashes on a partially mapped upload.
            _ = missing_cols
        before = len(result_df)
        result_df = result_df.dropna(subset=subset_cols if subset_cols else None)
        after = len(result_df)
        return result_df, CleaningLog(
            step=1,
            operation="missing_value_drop",
            columns_affected=subset_cols if subset_cols else list(result_df.columns),
            rows_before=before,
            rows_after=after,
            details={"removed_rows": before - after, "strategy": "drop"},
        )

    # fill_mean / fill_median / fill_mode — numeric columns only
    numeric_cols = [
        c for c in result_df.columns if pd.api.types.is_numeric_dtype(result_df[c])
    ]
    filled: dict[str, int] = {}
    for col in numeric_cols:
        null_count = int(result_df[col].isna().sum())
        if null_count == 0:
            continue
        if strategy == "fill_mean":
            fill_value = result_df[col].mean()
        elif strategy == "fill_median":
            fill_value = result_df[col].median()
        else:  # fill_mode
            modes = result_df[col].mode()
            fill_value = modes.iloc[0] if not modes.empty else np.nan
        if pd.isna(fill_value):
            # Cannot fill an all-null column; leave it untouched.
            continue
        result_df[col] = result_df[col].fillna(float(fill_value))
        filled[col] = null_count

    return result_df, CleaningLog(
        step=1,
        operation="missing_value_fill",
        columns_affected=list(filled.keys()),
        rows_before=rows_before,
        rows_after=len(result_df),
        details={
            "strategy": strategy,
            "removed_rows": 0,
            "cells_filled": sum(filled.values()),
            "columns_filled": filled,
        },
    )


def remove_duplicates(
    df: pd.DataFrame,
    keep: str = "first",
) -> tuple[pd.DataFrame, CleaningLog]:
    """Remove duplicate rows and return a new DataFrame + log entry.

    The input DataFrame is never mutated.
    """
    rows_before = len(df)
    dup_mask = df.duplicated(keep=keep)
    removed = int(dup_mask.sum())
    result_df = df.loc[~dup_mask].copy(deep=True) if removed > 0 else df.copy(deep=True)

    return result_df, CleaningLog(
        step=2,
        operation="remove_duplicates",
        columns_affected=list(df.columns),
        rows_before=rows_before,
        rows_after=len(result_df),
        details={"removed_rows": removed, "keep": keep},
    )


def coerce_types(
    df: pd.DataFrame,
    type_map: dict[str, str] | None = None,
) -> tuple[pd.DataFrame, CleaningLog]:
    """Convert column dtypes per *type_map*; return a new DataFrame + log.

    If *type_map* is None, DEFAULT_TYPE_MAP is used.  Columns that fail
    coercion are left unchanged and recorded in the log details, so a bad
    upload never aborts the pipeline.
    """
    effective_map = dict(type_map) if type_map else dict(DEFAULT_TYPE_MAP)
    result_df = df.copy(deep=True)
    succeeded: list[str] = []
    failed: dict[str, str] = {}

    for col, target_dtype in effective_map.items():
        if col not in result_df.columns:
            continue
        try:
            result_df[col] = result_df[col].astype(target_dtype)
            succeeded.append(col)
        except (ValueError, TypeError) as exc:
            failed[col] = str(exc)

    return result_df, CleaningLog(
        step=3,
        operation="type_coercion",
        columns_affected=succeeded,
        rows_before=len(df),
        rows_after=len(result_df),
        details={
            "type_map": effective_map,
            "coerced_columns": succeeded,
            "failed_columns": failed,
        },
    )


def normalize_dates(
    df: pd.DataFrame,
    date_column: str = "Order_Date",
) -> tuple[pd.DataFrame, CleaningLog]:
    """Normalise a date column to ISO-8601 (``YYYY-MM-DD``) strings.

    - Valid dates   → ``"YYYY-MM-DD"`` string.
    - Unparseable   → ``None`` (NULL) — the row is **preserved**, never
      silently dropped, and the count is reported in the log details.

    The input DataFrame is never mutated.
    """
    rows_before = len(df)
    result_df = df.copy(deep=True)

    if date_column not in result_df.columns:
        return result_df, CleaningLog(
            step=4,
            operation="date_normalisation",
            columns_affected=[],
            rows_before=rows_before,
            rows_after=rows_before,
            details={
                "date_column": date_column,
                "valid_rows": 0,
                "unparseable_rows": 0,
                "error": f"Date column '{date_column}' not found in DataFrame",
            },
        )

    parsed = pd.to_datetime(result_df[date_column], errors="coerce")
    unparseable = int(parsed.isna().sum())
    valid = int(parsed.notna().sum())

    def _format(value: Any) -> str | None:
        if pd.isna(value):
            return None
        try:
            return pd.Timestamp(value).strftime("%Y-%m-%d")
        except ValueError, TypeError:
            return None

    result_df[date_column] = parsed.apply(_format)

    return result_df, CleaningLog(
        step=4,
        operation="date_normalisation",
        columns_affected=[date_column],
        rows_before=rows_before,
        rows_after=len(result_df),
        details={
            "date_column": date_column,
            "valid_rows": valid,
            "unparseable_rows": unparseable,
            "strategy": "coerce_to_iso_string",
        },
    )


def clean_dataframe(
    df: pd.DataFrame,
    missing_strategy: str = "drop",
    missing_subset: list[str] | None = None,
    remove_dup_keep: str = "first",
    type_coercion: bool = True,
    date_normalisation: bool = True,
) -> tuple[pd.DataFrame, list[CleaningLog]]:
    """Run the full cleaning pipeline; return ``(cleaned_df, logs)``.

    Pipeline order (data-architecture §3 CleaningPipeline):
    1. Missing-value handling → 2. Duplicate removal →
    3. Type coercion → 4. Date normalisation.

    Each step operates on a copy, so the input DataFrame is never mutated.
    The returned logs are appended to ``cleaning_history`` by the caller.
    """
    logs: list[CleaningLog] = []
    current = df.copy(deep=True)

    current, log_missing = handle_missing_values(
        current,
        strategy=missing_strategy,
        subset=missing_subset,
    )
    logs.append(log_missing)

    current, log_dupes = remove_duplicates(current, keep=remove_dup_keep)
    logs.append(log_dupes)

    if type_coercion:
        current, log_types = coerce_types(current)
        logs.append(log_types)

    if date_normalisation:
        current, log_dates = normalize_dates(current)
        logs.append(log_dates)

    return current, logs
