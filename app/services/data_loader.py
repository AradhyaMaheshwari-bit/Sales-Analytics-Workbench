"""Data ingestion and validation service for the Sales Analytics Workbench.

Handles CSV and XLSX parsing, file validation, pre-parse size checks, and loading
Scenario B bundled data. Never mutates input data and returns deep copies.
"""

import io
from pathlib import Path
from typing import Literal

import pandas as pd

from app.models.dataset_schema import (
    validate_dataframe_schema,
)
from app.models.validation_models import DataLoadResult
from app.utils.logger import logger

MAX_FILE_SIZE_BYTES = 50 * 1024 * 1024  # 50 MB
ALLOWED_EXTENSIONS = {".csv", ".xlsx"}

#: Reserved path for the authentic internship dataset (historical benchmark only).
ORIGINAL_DATASET_PATH = "data/raw/internship_dataset.xlsx"

#: Default path for the synthetic demo dataset (Scenario A demo mode).
SYNTHETIC_DEMO_DATASET_PATH = "data/raw/synthetic_demo_dataset.xlsx"


class DataLoader:
    """Service for validating, loading, and parsing dataset files."""

    def __init__(self) -> None:
        self.logger = logger

    def validate_file_metadata(
        self, file_name: str, file_size: int
    ) -> tuple[bool, str | None]:
        """Validate file extension and size before reading or parsing."""
        suffix = Path(file_name).suffix.lower()
        if suffix not in ALLOWED_EXTENSIONS:
            return (
                False,
                f"Unsupported file format: '{suffix}'. Only .csv and .xlsx files are supported.",
            )

        if file_size > MAX_FILE_SIZE_BYTES:
            return False, "File size exceeds 50 MB limit."

        if file_size == 0:
            return False, "Dataset is empty."

        return True, None

    def load_file(
        self,
        file_buffer: bytes | io.BytesIO,
        file_name: str,
        file_type: Literal["csv", "xlsx"] | str | None = None,
    ) -> DataLoadResult:
        """Parse a CSV or XLSX file buffer into a DataFrame with schema validation.

        Args:
            file_buffer: Raw bytes or BytesIO buffer.
            file_name: Original file name.
            file_type: Optional explicit type ('csv' or 'xlsx'). If omitted, inferred from file_name.

        Returns:
            DataLoadResult with parsed DataFrame, SchemaReport, and status.
        """
        # Determine file type
        if file_type is None:
            suffix = Path(file_name).suffix.lower().lstrip(".")
            file_type = suffix

        file_type_normalized = file_type.lower()
        if file_type_normalized not in ("csv", "xlsx"):
            return DataLoadResult(
                dataframe=None,
                schema_report=None,
                load_info={"file_name": file_name, "file_type": file_type},
                success=False,
                error_message=f"Unsupported file format: '{file_type}'. Only .csv and .xlsx files are supported.",
            )

        # Get raw bytes for size check and stream parsing
        if isinstance(file_buffer, io.BytesIO):
            raw_bytes = file_buffer.getvalue()
        elif isinstance(file_buffer, bytes):
            raw_bytes = file_buffer
        else:
            try:
                raw_bytes = file_buffer.read()
            except Exception as e:
                return DataLoadResult(
                    dataframe=None,
                    schema_report=None,
                    load_info={"file_name": file_name},
                    success=False,
                    error_message=f"Could not read file buffer: {e}",
                )

        # Pre-parse validation
        is_valid, validation_err = self.validate_file_metadata(
            file_name, len(raw_bytes)
        )
        if not is_valid:
            return DataLoadResult(
                dataframe=None,
                schema_report=None,
                load_info={"file_name": file_name, "file_size": len(raw_bytes)},
                success=False,
                error_message=validation_err,
            )

        df: pd.DataFrame | None = None

        try:
            if file_type_normalized == "csv":
                # Handle possible encodings gracefully
                parsed = False
                last_err: Exception | None = None
                for enc in ("utf-8", "utf-8-sig", "latin1", "cp1252"):
                    try:
                        df = pd.read_csv(
                            io.BytesIO(raw_bytes),
                            encoding=enc,
                            engine="python",
                        )
                        parsed = True
                        break
                    except (
                        UnicodeDecodeError,
                        pd.errors.EmptyDataError,
                        pd.errors.ParserError,
                    ) as exc:
                        last_err = exc
                        if isinstance(exc, pd.errors.EmptyDataError):
                            # Immediate empty file detection
                            return DataLoadResult(
                                dataframe=None,
                                schema_report=None,
                                load_info={"file_name": file_name, "file_type": "csv"},
                                success=False,
                                error_message="Dataset is empty.",
                            )
                        continue

                if not parsed:
                    err_msg = (
                        f"CSV parsing error: {last_err}"
                        if last_err
                        else "Unable to parse CSV file."
                    )
                    return DataLoadResult(
                        dataframe=None,
                        schema_report=None,
                        load_info={"file_name": file_name, "file_type": "csv"},
                        success=False,
                        error_message=err_msg,
                    )

            elif file_type_normalized == "xlsx":
                try:
                    df = pd.read_excel(io.BytesIO(raw_bytes), engine="openpyxl")
                except Exception as exc:
                    return DataLoadResult(
                        dataframe=None,
                        schema_report=None,
                        load_info={"file_name": file_name, "file_type": "xlsx"},
                        success=False,
                        error_message=f"Excel parsing error: {exc}",
                    )

        except Exception as e:
            self.logger.error(f"Unexpected parsing failure for {file_name}: {e}")
            return DataLoadResult(
                dataframe=None,
                schema_report=None,
                load_info={"file_name": file_name, "file_type": file_type_normalized},
                success=False,
                error_message=f"Parsing error: {e}",
            )

        if df is None or df.empty or len(df.columns) == 0:
            return DataLoadResult(
                dataframe=None,
                schema_report=None,
                load_info={"file_name": file_name, "file_type": file_type_normalized},
                success=False,
                error_message="Dataset is empty.",
            )

        # Deep copy to ensure isolation
        df_copy = df.copy(deep=True)

        schema_report = validate_dataframe_schema(df_copy)

        return DataLoadResult(
            dataframe=df_copy,
            schema_report=schema_report,
            load_info={
                "file_name": file_name,
                "file_type": file_type_normalized,
                "file_size": len(raw_bytes),
                "row_count": len(df_copy),
                "column_count": len(df_copy.columns),
            },
            success=True,
            error_message=None,
        )

    def load_bundled_dataset(
        self, relative_path: str = SYNTHETIC_DEMO_DATASET_PATH
    ) -> DataLoadResult:
        """Load the synthetic demo dataset from data/raw/synthetic_demo_dataset.xlsx.

        Returns a failure DataLoadResult with clear setup guidance if absent.

        Note:
            The default bundled path points to the synthetic demo dataset. The
            authentic internship dataset (historical benchmark) is loaded
            exclusively through the benchmark test path
            ``data/raw/internship_dataset.xlsx``.
        """
        path = Path(relative_path)
        if not path.is_file():
            return DataLoadResult(
                dataframe=None,
                schema_report=None,
                load_info={"file_name": str(path)},
                success=False,
                error_message=(
                    f"Synthetic demo dataset not found at '{relative_path}'. "
                    "Please generate it via scripts/generate_demo_data.py or upload "
                    "a file via the Upload tab."
                ),
            )

        try:
            with open(path, "rb") as f:
                content = f.read()
            return self.load_file(content, file_name=path.name, file_type="xlsx")
        except Exception as exc:
            return DataLoadResult(
                dataframe=None,
                schema_report=None,
                load_info={"file_name": str(path)},
                success=False,
                error_message=f"Failed to read bundled dataset: {exc}",
            )


def load_file_buffer(
    file_buffer: bytes | io.BytesIO,
    file_name: str,
    file_type: Literal["csv", "xlsx"] | str | None = None,
) -> DataLoadResult:
    """Convenience function to parse and validate a file buffer."""
    loader = DataLoader()
    return loader.load_file(file_buffer, file_name, file_type)
