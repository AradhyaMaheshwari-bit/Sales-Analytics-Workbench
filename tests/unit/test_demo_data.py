"""Unit tests for the deterministic synthetic data generator (Increment 1C).

Covers plan items 10–11:
- Same seed → identical output (deterministic).
- 12-column schema; Total_Sales == Quantity × Unit_Price within rounding.
- Gender ∈ {Male, Female}.
- Plausible date range; documented row count.
- Generated output confined to data/raw/ and Git-ignored.

Path collision correction tests:
- Generator defaults to data/raw/synthetic_demo_dataset.xlsx.
- Synthetic generation never overwrites the reserved original internship
  dataset path (data/raw/internship_dataset.xlsx).
- Demo Mode loader reads from the synthetic demo path.
"""

from __future__ import annotations

import inspect
from pathlib import Path

import pandas as pd
import pytest
from app.services.data_loader import DataLoader
from scripts.generate_demo_data import (
    ORIGINAL_DATASET_PATH,
    SYNTHETIC_DEMO_DATASET_PATH,
    generate_and_save,
    generate_demo_dataframe,
)

DATE_MIN = pd.Timestamp("2024-01-01").date()
DATE_MAX = pd.Timestamp("2024-12-31").date()


@pytest.fixture
def df_from_generator() -> pd.DataFrame:
    return generate_demo_dataframe()


@pytest.fixture
def df_from_save(tmp_path) -> pd.DataFrame:
    out = tmp_path / "internship_dataset.xlsx"
    return generate_and_save(out)


def test_deterministic_identical_output() -> None:
    """Two calls with same seed produce byte-identical DataFrames."""
    df1 = generate_demo_dataframe()
    df2 = generate_demo_dataframe()
    pd.testing.assert_frame_equal(df1, df2)


def test_12_column_schema(df_from_generator: pd.DataFrame) -> None:
    expected = [
        "Order_ID",
        "Order_Date",
        "Customer_ID",
        "Customer_Name",
        "Age",
        "Gender",
        "City",
        "Product",
        "Category",
        "Quantity",
        "Unit_Price",
        "Total_Sales",
    ]
    assert list(df_from_generator.columns) == expected


def test_gender_only_male_female(df_from_generator: pd.DataFrame) -> None:
    assert set(df_from_generator["Gender"].unique()) <= {"Male", "Female"}


def test_total_sales_quantity_price_rounding(df_from_generator: pd.DataFrame) -> None:
    """Total_Sales ≈ Quantity × Unit_Price within rounding tolerance."""
    for _, row in df_from_generator.iterrows():
        expected = round(row["Quantity"] * row["Unit_Price"], 2)
        assert row["Total_Sales"] == expected


def test_plausible_date_range(df_from_generator: pd.DataFrame) -> None:
    """All dates fall between 2024-01-01 and 2024-12-31 inclusive."""
    for d in df_from_generator["Order_Date"]:
        dt = pd.to_datetime(d)
        assert DATE_MIN <= dt.date() <= DATE_MAX


def test_documented_row_count(df_from_generator: pd.DataFrame) -> None:
    assert len(df_from_generator) == 60


def test_saved_dataset_is_readable(tmp_path) -> None:
    out = tmp_path / "test_dataset.xlsx"
    generate_and_save(out)
    df_read = pd.read_excel(out, engine="openpyxl")
    assert len(df_read) == 60


# ---------------------------------------------------------------------------
# Path-collision regression tests
# ---------------------------------------------------------------------------


def test_default_generator_destination_is_synthetic_demo_path() -> None:
    """The default generator destination is data/raw/synthetic_demo_dataset.xlsx."""
    default = inspect.signature(generate_and_save).parameters["output_path"].default
    assert str(default) == str(SYNTHETIC_DEMO_DATASET_PATH)
    assert default == "data/raw/synthetic_demo_dataset.xlsx"


def test_generator_creates_parent_directory(tmp_path) -> None:
    """Generator creates the required parent directory safely under an isolated path."""
    target = tmp_path / "subdir" / "synthetic_demo_dataset.xlsx"
    generate_and_save(target)
    assert target.is_file()
    df_read = pd.read_excel(target, engine="openpyxl")
    assert len(df_read) == 60


def test_generator_rejects_reserved_original_dataset_path() -> None:
    """Generating synthetic data to the reserved original dataset path is rejected."""
    with pytest.raises(ValueError, match="Refusing to write synthetic data"):
        generate_and_save(ORIGINAL_DATASET_PATH)


def test_generator_rejects_equivalent_resolved_paths() -> None:
    """Equivalent spellings of the reserved path are also rejected."""
    equivalent_paths = [
        "./data/raw/internship_dataset.xlsx",
        "data/raw/../raw/internship_dataset.xlsx",
        str(Path(ORIGINAL_DATASET_PATH).resolve()),
    ]
    for candidate in equivalent_paths:
        with pytest.raises(ValueError, match="Refusing to write synthetic data"):
            generate_and_save(candidate)


def test_generator_rejects_path_resolution_failure(monkeypatch, tmp_path) -> None:
    """Path resolution failure raises ValueError and prevents any file write."""
    original_resolve = Path.resolve

    def mock_resolve(self, strict=False):
        if str(self).endswith("synthetic_demo_dataset.xlsx") or str(self).endswith(
            "some_path.xlsx"
        ):
            raise OSError("Simulated path resolution error")
        return original_resolve(self, strict=strict)

    monkeypatch.setattr(Path, "resolve", mock_resolve)
    target = tmp_path / "some_path.xlsx"

    with pytest.raises(ValueError, match="path resolution failed"):
        generate_and_save(target)

    assert not target.exists()


def test_generator_never_overwrites_original_dataset_sentinel(tmp_path) -> None:
    """Synthetic generation does not modify a sentinel original dataset file."""
    sentinel = tmp_path / "internship_dataset.xlsx"
    # Create sentinel mimicking the original internship dataset
    sentinel_df = pd.DataFrame({"Order_ID": ["ORD-000"], "Total_Sales": [999999.0]})
    sentinel_df.to_excel(sentinel, index=False, engine="openpyxl")
    sentinel_mtime = sentinel.stat().st_mtime

    # Attempt synthetic generation targeting a sibling path (not the sentinel)
    synthetic_target = tmp_path / "synthetic_demo_dataset.xlsx"
    generate_and_save(synthetic_target)

    assert sentinel.is_file()
    sentinel_after = pd.read_excel(sentinel, engine="openpyxl")
    assert len(sentinel_after) == 1
    assert sentinel_after["Total_Sales"].iloc[0] == 999999.0
    assert sentinel.stat().st_mtime == sentinel_mtime


def test_default_generation_writes_to_synthetic_path_only(
    tmp_path, monkeypatch
) -> None:
    """Default generation writes only to the synthetic path, never the original path.

    The CWD is redirected into an isolated temporary directory so that the
    generator's relative default path resolves inside tmp_path and the real
    repository dataset can never be touched by this test.
    """
    raw_dir = tmp_path / "data" / "raw"
    raw_dir.mkdir(parents=True)
    original_dataset_path = raw_dir / "internship_dataset.xlsx"
    sentinel_df = pd.DataFrame({"Order_ID": ["ORD-000"], "Total_Sales": [999999.0]})
    sentinel_df.to_excel(original_dataset_path, index=False, engine="openpyxl")
    sentinel_bytes = original_dataset_path.read_bytes()
    sentinel_mtime = original_dataset_path.stat().st_mtime

    monkeypatch.chdir(tmp_path)

    # Default generation (no explicit output path)
    generate_and_save()

    synthetic_target = raw_dir / "synthetic_demo_dataset.xlsx"
    assert synthetic_target.is_file(), "Synthetic demo dataset was not created"

    # The reserved original dataset is untouched (bytes and mtime)
    assert original_dataset_path.is_file(), "Original dataset sentinel was removed"
    assert original_dataset_path.read_bytes() == sentinel_bytes
    assert original_dataset_path.stat().st_mtime == sentinel_mtime

    # Nothing else was written alongside the reserved original dataset
    assert sorted(p.name for p in raw_dir.iterdir()) == [
        "internship_dataset.xlsx",
        "synthetic_demo_dataset.xlsx",
    ]


# ---------------------------------------------------------------------------
# Demo Mode loader tests
# ---------------------------------------------------------------------------


def test_demo_loader_reads_synthetic_demo_path(tmp_path) -> None:
    """load_bundled_dataset reads from the synthetic demo path by default."""
    synthetic_target = tmp_path / "synthetic_demo_dataset.xlsx"
    demo_df = pd.DataFrame(
        {
            "Order_ID": ["ORD-001", "ORD-002"],
            "Total_Sales": [100.0, 200.0],
        }
    )
    demo_df.to_excel(synthetic_target, index=False, engine="openpyxl")

    loader = DataLoader()
    result = loader.load_bundled_dataset(str(synthetic_target))
    assert result.success
    assert result.dataframe is not None
    assert len(result.dataframe) == 2


def test_demo_loader_default_path_is_synthetic_demo_path() -> None:
    """The bundled loader default points at the synthetic demo dataset."""
    default = (
        inspect.signature(DataLoader.load_bundled_dataset)
        .parameters["relative_path"]
        .default
    )
    assert default == "data/raw/synthetic_demo_dataset.xlsx"


def test_demo_loader_missing_demo_file_returns_failure_not_fallback(tmp_path) -> None:
    """Missing demo file produces a failure DataLoadResult, not a silent fallback."""
    missing_path = str(tmp_path / "synthetic_demo_dataset.xlsx")
    loader = DataLoader()
    result = loader.load_bundled_dataset(missing_path)
    assert not result.success
    assert "Synthetic demo dataset not found" in (result.error_message or "")
    assert result.dataframe is None
