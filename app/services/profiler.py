"""Dataset profiling service for the Sales Analytics Workbench.

Computes dimensional metrics, data types, missing value rates, duplicate rows,
summary statistics, and flags potential type anomalies.
"""

import pandas as pd

from app.models.validation_models import ColumnProfile, ProfilingMetrics
from app.utils.logger import logger


def _detect_type_anomaly(series: pd.Series) -> tuple[bool, str | None]:
    """Inspect an object series for potential numeric or datetime conversions."""
    non_null = series.dropna()
    if non_null.empty:
        return False, None

    # Check for numeric conversion (> 80% can be parsed as numeric)
    sample_size = min(len(non_null), 200)
    sample = non_null.iloc[:sample_size]

    numeric_converted = pd.to_numeric(sample, errors="coerce")
    numeric_ratio = numeric_converted.notna().mean()
    if numeric_ratio >= 0.8:
        return True, (
            f"{numeric_ratio * 100:.1f}% of sampled values are numeric. "
            "Consider converting to numeric."
        )

    # Check for date conversion (> 80% can be parsed as datetime)
    # Only test if string values look somewhat like dates (contains '-' or '/' or numbers)
    sample_str = sample.astype(str)
    has_date_symbols = sample_str.str.contains(r"[\/\-]", regex=True).mean()
    if has_date_symbols >= 0.5:
        try:
            date_converted = pd.to_datetime(sample, errors="coerce")
            date_ratio = date_converted.notna().mean()
            if date_ratio >= 0.8:
                return True, (
                    f"{date_ratio * 100:.1f}% of sampled values resemble dates. "
                    "Consider converting to datetime."
                )
        except Exception:
            pass

    return False, None


class Profiler:
    """Service to compute profiling metrics on a DataFrame."""

    def __init__(self) -> None:
        self.logger = logger

    def profile(self, df: pd.DataFrame) -> ProfilingMetrics:
        """Compute comprehensive profiling metrics for the provided DataFrame.

        Never mutates the input DataFrame.
        """
        if df is None:
            raise ValueError("DataFrame cannot be None")

        row_count = int(len(df))
        column_count = int(len(df.columns))
        memory_usage_bytes = (
            int(df.memory_usage(deep=True).sum()) if column_count > 0 else 0
        )

        if row_count == 0 or column_count == 0:
            return ProfilingMetrics(
                row_count=row_count,
                column_count=column_count,
                memory_usage_bytes=memory_usage_bytes,
                columns={},
                missing_total=0,
                missing_percentage=0.0,
                duplicate_row_count=0,
                duplicate_percentage=0.0,
            )

        missing_total = int(df.isna().sum().sum())
        missing_percentage = float((missing_total / (row_count * column_count)) * 100.0)

        duplicate_row_count = int(df.duplicated().sum())
        duplicate_percentage = float((duplicate_row_count / row_count) * 100.0)

        columns_profile: dict[str, ColumnProfile] = {}

        for col in df.columns:
            series = df[col]
            dtype_str = str(series.dtype)
            non_null_count = int(series.count())
            null_count = int(series.isna().sum())
            null_percentage = (
                float((null_count / row_count) * 100.0) if row_count > 0 else 0.0
            )

            unique_count = int(series.nunique(dropna=True))
            sample_values = [str(val) for val in series.dropna().iloc[:5].tolist()]

            mean: float | None = None
            std: float | None = None
            min_val: float | None = None
            max_val: float | None = None
            potential_issue = False
            issue_msg: str | None = None

            if pd.api.types.is_numeric_dtype(series):
                if non_null_count > 0:
                    mean_val = series.mean()
                    mean = float(mean_val) if pd.notna(mean_val) else None

                    std_val = series.std()
                    std = float(std_val) if pd.notna(std_val) else None

                    min_val_calc = series.min()
                    min_val = float(min_val_calc) if pd.notna(min_val_calc) else None

                    max_val_calc = series.max()
                    max_val = float(max_val_calc) if pd.notna(max_val_calc) else None
            else:
                # Detect anomalies on object or category series
                potential_issue, issue_msg = _detect_type_anomaly(series)

            columns_profile[str(col)] = ColumnProfile(
                name=str(col),
                dtype=dtype_str,
                non_null_count=non_null_count,
                null_count=null_count,
                null_percentage=null_percentage,
                mean=mean,
                std=std,
                min_val=min_val,
                max_val=max_val,
                unique_count=unique_count,
                sample_values=sample_values,
                potential_type_issue=potential_issue,
                potential_type_message=issue_msg,
            )

        return ProfilingMetrics(
            row_count=row_count,
            column_count=column_count,
            memory_usage_bytes=memory_usage_bytes,
            columns=columns_profile,
            missing_total=missing_total,
            missing_percentage=missing_percentage,
            duplicate_row_count=duplicate_row_count,
            duplicate_percentage=duplicate_percentage,
        )


def profile_dataframe(df: pd.DataFrame) -> ProfilingMetrics:
    """Convenience function to profile a DataFrame."""
    profiler = Profiler()
    return profiler.profile(df)
