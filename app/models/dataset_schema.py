"""Canonical dataset schema and validation rules for the Sales Analytics Workbench."""

from dataclasses import dataclass

# ──────────────────────────────────────────────────────────────────────────────
# Canonical 12-column sales schema (internship dataset)
# ──────────────────────────────────────────────────────────────────────────────

CANONICAL_COLUMNS = [
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

# Expected pandas dtypes for each canonical column
EXPECTED_DTYPES = {
    "Order_ID": "object",
    "Order_Date": "object",  # raw string; normalized to datetime later
    "Customer_ID": "object",
    "Customer_Name": "object",
    "Age": "float64",  # nullable numeric
    "Gender": "object",  # "Male" / "Female"
    "City": "object",
    "Product": "object",
    "Category": "object",
    "Quantity": "int64",
    "Unit_Price": "float64",
    "Total_Sales": "float64",
}

# Columns that must be present for minimal viable analysis
REQUIRED_FOR_ANALYSIS = ["Total_Sales", "Order_Date"]

# Synonym mapping for flexible column mapping (FR-CC-02)
# Keys are lowercased, whitespace-stripped user column names
SYNONYM_MAP: dict[str, str] = {
    # Order_ID variants
    "order_id": "Order_ID",
    "orderid": "Order_ID",
    "order number": "Order_ID",
    "ordernumber": "Order_ID",
    "order_no": "Order_ID",
    "orderno": "Order_ID",
    # Order_Date variants
    "order_date": "Order_Date",
    "orderdate": "Order_Date",
    "date": "Order_Date",
    "transaction_date": "Order_Date",
    "transactiondate": "Order_Date",
    "sale_date": "Order_Date",
    "saledate": "Order_Date",
    # Customer_ID variants
    "customer_id": "Customer_ID",
    "customerid": "Customer_ID",
    "cust_id": "Customer_ID",
    "custid": "Customer_ID",
    "client_id": "Customer_ID",
    "clientid": "Customer_ID",
    # Customer_Name variants
    "customer_name": "Customer_Name",
    "customername": "Customer_Name",
    "cust_name": "Customer_Name",
    "custname": "Customer_Name",
    "client_name": "Customer_Name",
    "clientname": "Customer_Name",
    "name": "Customer_Name",
    # Age variants
    "age": "Age",
    "customer_age": "Age",
    "customerage": "Age",
    # Gender variants
    "gender": "Gender",
    "sex": "Gender",
    # City variants
    "city": "City",
    "location": "City",
    "town": "City",
    # Product variants
    "product": "Product",
    "product_name": "Product",
    "productname": "Product",
    "item": "Product",
    "item_name": "Product",
    # Category variants
    "category": "Category",
    "product_category": "Category",
    "productcategory": "Category",
    "cat": "Category",
    # Quantity variants
    "quantity": "Quantity",
    "qty": "Quantity",
    "units": "Quantity",
    "quantity_sold": "Quantity",
    "quantitysold": "Quantity",
    # Unit_Price variants
    "unit_price": "Unit_Price",
    "unitprice": "Unit_Price",
    "price": "Unit_Price",
    "unit_price_inr": "Unit_Price",
    "unitpriceinr": "Unit_Price",
    # Total_Sales variants
    "total_sales": "Total_Sales",
    "totalsales": "Total_Sales",
    "revenue": "Total_Sales",
    "sales": "Total_Sales",
    "amount": "Total_Sales",
    "total_amount": "Total_Sales",
    "totalamount": "Total_Sales",
}


@dataclass(frozen=True)
class SchemaReport:
    """Result of schema validation against the canonical 12-column schema."""

    # Raw columns found in the uploaded file (preserving original case)
    raw_columns: list[str]
    # Canonical columns that were successfully mapped
    mapped_columns: dict[str, str]  # raw_col -> canonical_col
    # Raw columns that could not be mapped to any canonical column
    unmapped_columns: list[str]
    # Canonical columns that are missing from the upload
    missing_canonical: list[str]
    # Whether the dataset has at least one revenue column and one date/category column
    viable_for_analysis: bool


def normalize_column_name(name: str) -> str:
    """Normalize a column name for synonym lookup: strip, lowercase, replace separators."""
    return name.strip().lower().replace("-", "_").replace(" ", "_")


def map_columns(raw_columns: list[str]) -> SchemaReport:
    """Map raw uploaded columns to canonical schema using exact match + synonyms."""
    mapped: dict[str, str] = {}
    unmapped: list[str] = []
    canonical_found: set[str] = set()

    for raw in raw_columns:
        normalized = normalize_column_name(raw)
        # 1) Exact case-insensitive match to canonical
        canonical_match = None
        for canon in CANONICAL_COLUMNS:
            if normalize_column_name(canon) == normalized:
                canonical_match = canon
                break

        # 2) Synonym lookup
        if canonical_match is None:
            canonical_match = SYNONYM_MAP.get(normalized)

        if canonical_match is not None:
            mapped[raw] = canonical_match
            canonical_found.add(canonical_match)
        else:
            unmapped.append(raw)

    missing = [c for c in CANONICAL_COLUMNS if c not in canonical_found]
    # Minimal viable: at least Total_Sales (or synonym) AND one of Order_Date/Category/City/Product
    has_revenue = "Total_Sales" in canonical_found
    has_dimension = any(
        c in canonical_found for c in ("Order_Date", "Category", "City", "Product")
    )
    viable = has_revenue and has_dimension

    return SchemaReport(
        raw_columns=raw_columns,
        mapped_columns=mapped,
        unmapped_columns=unmapped,
        missing_canonical=missing,
        viable_for_analysis=viable,
    )


def validate_dataframe_schema(df) -> SchemaReport:
    """Validate a DataFrame against the canonical schema."""
    return map_columns(list(df.columns))


def apply_column_mapping(df, mapping: dict[str, str]):
    """Return a deep copy of df with mapped columns renamed to canonical."""
    return df.rename(columns=mapping).copy(deep=True)
