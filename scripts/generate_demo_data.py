"""Generate the deterministic synthetic internship dataset (FR-CC-01, D-1).

Writes the synthetic sales dataset to ``data/raw/internship_dataset.xlsx``
(scenario A demo mode / scenario B bundled dataset).

Design constraints (approved specs, do NOT deviate):
- Deterministic output: same fixed seed → identical dataset on every run.
- 12-column canonical schema (``CANONICAL_COLUMNS``).
- ``Total_Sales == Quantity × Unit_Price`` within rounding tolerance.
- ``Gender`` ∈ {Male, Female}.
- Plausible date range (2024-01-01 … 2024-12-31).
- No real internship customer records are used.
- Generated output confined to ``data/raw/`` and Git-ignored.

This module is a standalone script (not part of the service layer) and must
not be imported by services/models/database.
"""

from __future__ import annotations

import random
from datetime import date, datetime
from pathlib import Path

import pandas as pd

# Fixed seed → fully deterministic output
_GENERATE_SEED = 42

# Documented synthetic row count
DEMO_ROW_COUNT = 60

# Plausible date range for synthetic orders (inclusive)
DATE_MIN = date(2024, 1, 1)
DATE_MAX = date(2024, 12, 31)

# Products by category with plausible INR unit prices
_PRODUCT_CATALOG: dict[str, list[dict[str, object]]] = {
    "Electronics": [
        {"product": "Wireless Headphones", "unit_price": 1500.0},
        {"product": "Smartwatch", "unit_price": 3000.0},
        {"product": "Laptop Stand", "unit_price": 2500.0},
        {"product": "Bluetooth Speaker", "unit_price": 1800.0},
    ],
    "Fashion": [
        {"product": "Cotton T-Shirt", "unit_price": 600.0},
        {"product": "Denim Jeans", "unit_price": 1800.0},
        {"product": "Running Sneakers", "unit_price": 3500.0},
        {"product": "Wool Jacket", "unit_price": 2500.0},
    ],
    "Home": [
        {"product": "Stainless Kettle", "unit_price": 700.0},
        {"product": "Desk Fan", "unit_price": 900.0},
        {"product": "LED Lamp", "unit_price": 1500.0},
        {"product": "Cotton Bed Sheet", "unit_price": 2200.0},
    ],
}


def _generate_rows() -> list[dict[str, object]]:
    rng = random.Random(_GENERATE_SEED)
    customers = [
        ("CUST-001", "Aarav Sharma"),
        ("CUST-002", "Diya Verma"),
        ("CUST-003", "Kabir Singh"),
        ("CUST-004", "Meera Iyer"),
        ("CUST-005", "Reyansh Nair"),
        ("CUST-006", "Ananya Deshmukh"),
    ]

    rows: list[dict[str, object]] = []
    order_counter = 1
    for _ in range(DEMO_ROW_COUNT):
        category = rng.choice(list(_PRODUCT_CATALOG.keys()))
        product_def = rng.choice(_PRODUCT_CATALOG[category])
        product = str(product_def["product"])
        unit_price = float(product_def["unit_price"])
        quantity = int(rng.randint(1, 5))
        total_sales = round(quantity * unit_price, 2)

        cust_id, cust_name = rng.choice(customers)
        rows.append(
            {
                "Order_ID": f"ORD-{order_counter:03d}",
                "Order_Date": datetime.fromordinal(
                    rng.randint(DATE_MIN.toordinal(), DATE_MAX.toordinal())
                ).strftime("%Y-%m-%d"),
                "Customer_ID": cust_id,
                "Customer_Name": cust_name,
                "Age": float(rng.randint(19, 55)),
                "Gender": rng.choice(["Male", "Female"]),
                "City": rng.choice(
                    ["Patna", "Delhi", "Mumbai", "Bangalore", "Pune", "Kolkata"]
                ),
                "Product": product,
                "Category": category,
                "Quantity": quantity,
                "Unit_Price": unit_price,
                "Total_Sales": total_sales,
            }
        )
        order_counter += 1

    return rows


def generate_demo_dataframe() -> pd.DataFrame:
    """Generate the synthetic demo DataFrame deterministically."""
    rows = _generate_rows()
    df = pd.DataFrame(rows)
    return df[
        [
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
    ]


def generate_and_save(
    output_path: str | Path = "data/raw/internship_dataset.xlsx",
) -> pd.DataFrame:
    """Generate the deterministic dataset and save it to *output_path*.

    Returns the generated DataFrame (for verification / tests).
    """
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    df = generate_demo_dataframe()
    df.to_excel(output, index=False, engine="openpyxl")
    return df


if __name__ == "__main__":
    generated = generate_and_save()
    print(
        f"Generated synthetic demo dataset with {len(generated)} rows "
        f"at {Path('data/raw/internship_dataset.xlsx')}"
    )
