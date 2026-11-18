# SQL Business Query Reference — Sales Analytics Workbench

**SDLC Phase:** 2 — Requirements Analysis
**Document ID:** SRS-SQL
**Version:** 1.3 (SELECT-only policy and date-handling refinement applied)

---

## 1. Overview

The seven business-analysis SQL queries that were used in the original internship
Task-1 (Sales-Performance-Dashboard-Data-Analytics-Project) have been preserved
and are documented here. They are executed against the embedded SQLite database
(`sales` table, lowercase) created from the user-uploaded or internship dataset.

---

## 2. Seven Pre-Built SQL Business Queries

### Query 1: Total Revenue
- **Business Question:** *What is the total revenue across all sales?*
- **SQL Query:**
  ```sql
  SELECT SUM(Total_Sales) AS Total_Revenue FROM sales;
  ```

### Query 2: Revenue by Product Category
- **Business Question:** *Which product categories generate the most revenue?*
- **SQL Query:**
  ```sql
  SELECT Category, SUM(Total_Sales) AS Revenue
  FROM sales
  GROUP BY Category
  ORDER BY Revenue DESC;
  ```

### Query 3: Revenue by Individual Product
- **Business Question:** *Which individual products generate the most revenue?*
- **SQL Query:**
  ```sql
  SELECT Product, SUM(Total_Sales) AS Revenue
  FROM sales
  GROUP BY Product
  ORDER BY Revenue DESC;
  ```

### Query 4: Revenue by City
- **Business Question:** *Which cities contribute the most to revenue?*
- **SQL Query:**
  ```sql
  SELECT City, SUM(Total_Sales) AS Revenue
  FROM sales
  GROUP BY City
  ORDER BY Revenue DESC;
  ```

### Query 5: Monthly Revenue Trend
- **Business Question:** *What is the monthly revenue trend (seasonality) throughout the year?*
- **SQL Query:**
  ```sql
  SELECT STRFTIME('%Y-%m', Order_Date) AS Month, SUM(Total_Sales) AS Revenue
  FROM sales
  GROUP BY Month
  ORDER BY Month;
  ```
- **Adaptation Note:** The original repository query referenced a `Month` column which does not exist in the dataset schema. The dataset contains `Order_Date` (string/object type). This query uses SQLite's `STRFTIME()` function to extract year-month from `Order_Date`. The business question is preserved exactly. (SQLite allows `GROUP BY Month` on the SELECT alias; grouping on the alias or the full `STRFTIME` expression is equivalent here.)
- **Date-handling implementation requirements (to be satisfied in Phase 4):**
  - `Order_Date` must be **normalized or validated into a SQLite-compatible date representation** (`YYYY-MM-DD`) before this query executes.
  - The implementation must handle **invalid or unparseable date values safely** — rows with unparseable dates must not crash the query.
  - Invalid dates must **not be silently discarded without documentation**: the cleaning module's summary must report how many rows had unparseable dates and what was done with them (excluded from this query's grouping, flagged in the cleaning summary).
  - Query 6 and the statistical validation module are unaffected (they do not reference `Order_Date`).

### Query 6: Revenue Split by Gender
- **Business Question:** *How does revenue split by gender?*
- **SQL Query:**
  ```sql
  SELECT Gender, SUM(Total_Sales) AS Revenue
  FROM sales
  GROUP BY Gender;
  ```

### Query 7: Top-10 Customers by Revenue
- **Business Question:** *Who are the top-10 customers by revenue?*
- **SQL Query:**
  ```sql
  SELECT Customer_Name, SUM(Total_Sales) AS Revenue
  FROM sales
  GROUP BY Customer_Name
  ORDER BY Revenue DESC
  LIMIT 10;
  ```

---

## 3. Implementation Notes

- **Table name:** The SQLite table created from the cleaned dataset will be named
  `sales` (lowercase, conventional for SQLite). All column names are exactly as
  they appear in the internship dataset (`Order_ID`, `Order_Date`, `Customer_ID`,
  `Customer_Name`, `Age`, `Gender`, `City`, `Product`, `Category`, `Quantity`,
  `Unit_Price`, `Total_Sales`).
- **Query 5 adaptation:** The original query referenced a `Month` column which does
  not exist in the schema. Query 5 has been adapted to extract year-month from
  `Order_Date` using SQLite's `STRFTIME()` function while preserving the original
  business question.
- The queries are exposed in **Module 2** via a dropdown selector. Selecting a
  query automatically executes it and displays the result set in a paginated
  table.
- The **business question** for each query is presented alongside the query
  in the UI, ensuring traceability to the original internship deliverables.
- **Queries 1-4, 6, and 7** are preserved verbatim from the original Task-1 repository
  (source: https://github.com/AradhyaMaheshwari-bit/Sales-Performance-Dashboard-Data-Analytics-Project,
  file `SQL_Analysis.py`).
- **Query 5** required schema adaptation as documented above.

---

## 4. Alignment with Requirements

- **FR-16** (SQL Business Queries) references this document; each of the seven
  queries is listed with its exact text and associated business question.
- The **Requirements Traceability Matrix** links FR-16 to this `SRS-SQL`
  document (see `requirements-traceability-matrix.md`).
- The **User Story US-04** (SQL Business Query Execution) explicitly mentions
  "seven pre-built queries" — the list above fulfills that story.
