# Demonstration Data Strategy — Sales Analytics Workbench

**SDLC Phase:** 2 — Requirements Analysis
**Document ID:** SRS-DDS
**Version:** 1.1 (D-1 approved)

---

## 1. Purpose

The original internship dataset (`Phase-I_Evaluation/Dataset.xlsx`) must never be
committed to Git, never modified, and never exposed beyond the local machine.
This document defines two separate data scenarios so that (A) anyone cloning the
repository can demonstrate the application independently, and (B) the original
internship analysis remains private.

---

## 2. Scenario A — Repository Demonstration (Synthetic Data)

**Decision D-1 (approved):** A synthetic data generator script will be included
at `scripts/generate_demo_data.py` (created during Phase 4 — **not in this
phase**).

**Generator requirements (documented now, implemented later):**
- Produces a dataset matching the original 12-column schema exactly:
  `Order_ID, Order_Date, Customer_ID, Customer_Name, Age, Gender, City, Product, Category, Quantity, Unit_Price, Total_Sales`.
- Generates **realistic but entirely synthetic records** — no copying, embedding,
  reproduction, or exposure of actual customer records or confidential values
  from the original internship dataset.
- Supports a **fixed random seed** (CLI argument) for reproducibility.
- Generated files are written to `data/raw/` and remain excluded from Git
  unless a future explicit decision changes that policy.
- README (Phase 6) documents how to run the generator.

**Business-rule preservation:** the generator must respect the analytical
invariants the application relies on (numeric `Total_Sales` ≈ `Quantity ×
Unit_Price` within rounding tolerance; Gender values limited to
`Male`/`Female`; plausible date range) so that all five modules work on
synthetic data exactly as they do on real data.

---

## 3. Scenario B — Private Internship Analysis (Original Data)

- The original internship dataset remains **private**.
- The user **manually copies** `Phase-I_Evaluation/Dataset.xlsx` to
  `data/raw/internship_dataset.xlsx` (one-time, documented in the Phase 6
  README).
- `data/raw/` is excluded from Git via `.gitignore` — the private copy is never
  committed.
- Runtime loading reads **only** from `data/raw/` — the application never reads
  from `Phase-I_Evaluation/` at runtime, and `Phase-I_Evaluation/` is never
  accessed or modified during development.
- **Graceful absence:** the application must remain fully usable with an
  uploaded dataset even when the private internship dataset is absent. Internship
  Dataset Mode shows a "dataset not found — run setup step X" message instead of
  crashing.

---

## 4. Deployment Considerations

| Scenario | Data Supplied By |
|---|---|
| Cloned repository (no private data) | Scenario A — synthetic generator |
| University lab demo (local, private data available) | Scenario B — manual copy; or Scenario A |
| Reviewer brings own data | Standard upload pipeline (FR-01..FR-10) |
| Git repository (public) | Nothing committed — `data/raw/` excluded; README explains both scenarios |
| Future cloud deployment | Scenario A only — no private data shipped |

---

## 5. Git Exclusion Rules (both scenarios)

- `data/raw/` and all generated/private data files are excluded from Git
  (`.gitignore`).
- No dataset of any kind is committed without a separate explicit approval
  (per the dataset version-control policy in `InitialPrompt.md`).
- The synthetic generator **script** (source code) is committable; its
  **output** is not.
