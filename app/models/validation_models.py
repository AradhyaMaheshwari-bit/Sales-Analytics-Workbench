"""Typed data contracts for validation, profiling, and statistical results."""

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ProfilingMetrics:
    """Complete profiling metrics for a dataset."""

    row_count: int
    column_count: int
    memory_usage_bytes: int
    columns: dict[str, ColumnProfile]
    missing_total: int
    missing_percentage: float
    duplicate_row_count: int
    duplicate_percentage: float


@dataclass(frozen=True)
class ColumnProfile:
    """Profile for a single column."""

    name: str
    dtype: str
    non_null_count: int
    null_count: int
    null_percentage: float
    # Numeric stats (if applicable)
    mean: float | None = None
    std: float | None = None
    min_val: float | None = None
    max_val: float | None = None
    # Sample values for object columns
    unique_count: int | None = None
    sample_values: list[str] | None = None
    # Type anomaly flag
    potential_type_issue: bool = False
    potential_type_message: str | None = None


@dataclass(frozen=True)
class ValidationSummary:
    """Summary of business rule validation."""

    total_rows: int
    checks: dict[str, RuleCheckResult]
    overall_pass: bool


@dataclass(frozen=True)
class RuleCheckResult:
    """Result of a single business rule check."""

    rule_name: str
    passed: int
    failed: int
    failure_details: list[str] = field(default_factory=list)
    passed_percentage: float = 0.0


@dataclass(frozen=True)
class StatResult:
    """Welch's t-test result with 95% CI."""

    t_statistic: float
    p_value: float
    degrees_of_freedom: float
    ci_lower: float
    ci_upper: float
    mean_diff: float
    group1_name: str
    group2_name: str
    group1_count: int
    group2_count: int
    group1_mean: float
    group2_mean: float
    decision: str  # "Reject H0" or "Fail to Reject H0"
    alpha: float = 0.05


@dataclass(frozen=True)
class CleaningLog:
    """Log entry for a single cleaning operation."""

    step: int
    operation: str
    columns_affected: list[str]
    rows_before: int
    rows_after: int
    details: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class DataLoadResult:
    """Result of loading a file into a DataFrame."""

    dataframe: Any  # pd.DataFrame - using Any to avoid pandas import at module level
    schema_report: SchemaReport
    load_info: dict[str, Any]
    success: bool
    error_message: str | None = None


# Import SchemaReport here to avoid circular import
from app.models.dataset_schema import SchemaReport  # noqa: E402

# Re-export for convenience
__all__ = [
    "ProfilingMetrics",
    "ColumnProfile",
    "ValidationSummary",
    "RuleCheckResult",
    "StatResult",
    "CleaningLog",
    "DataLoadResult",
    "SchemaReport",
]
