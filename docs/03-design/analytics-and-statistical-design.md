# Analytics and Statistical Design — Sales Analytics Workbench

**SDLC Phase:** 3 — System Design (Checkpoint B)
**Document ID:** SDD-STAT
**Version:** 1.0

---

## 1. Overview

This document specifies the analytical methodologies, aggregations, statistical algorithms, hypothesis testing formulations, and degrees-of-freedom calculations implemented in the Service Layer (`app/services/eda.py` and `app/services/statistics.py`).

---

## 2. Descriptive & Exploratory Analytics

### 2.1 Numerical Summaries
For numerical fields (`Age`, `Quantity`, `Unit_Price`, `Total_Sales`):
- **Metrics:** Count, Mean, Standard Deviation (sample, ddof=1), Min, 25th percentile ($Q_1$), Median ($Q_2$), 75th percentile ($Q_3$), Max, Interquartile Range ($IQR = Q_3 - Q_1$).
- **Currency Handling:** `Unit_Price` and `Total_Sales` are formatted with Indian Rupee symbol (`₹`) and comma groupings.

### 2.2 Correlation Analysis
- **Formula:** Pearson product-moment correlation coefficient $r_{xy}$:
  $$r_{xy} = \frac{\sum (x_i - \bar{x})(y_i - \bar{y})}{\sqrt{\sum (x_i - \bar{x})^2 \sum (y_i - \bar{y})^2}}$$
- **Key Pairs Tracked:**
  - `Unit_Price` vs. `Total_Sales` (Historical benchmark: $r = 0.686$, strong positive).
  - `Age` vs. `Total_Sales` (Historical benchmark: $r = 0.001$, negligible).
  - `Quantity` vs. `Total_Sales` (Historical benchmark: moderate positive).

---

## 3. Statistical Hypothesis Testing Design

### 3.1 Business Question & Hypotheses
- **Business Question:** *"Does average sales per order differ significantly between male and female customers?"*
- **Null Hypothesis ($H_0$):** $\mu_{\text{male}} = \mu_{\text{female}}$ (There is no significant difference in average sales between male and female customers).
- **Alternative Hypothesis ($H_1$):** $\mu_{\text{male}} \neq \mu_{\text{female}}$ (There is a significant difference in average sales between male and female customers).
- **Test Type:** Two-tailed, independent two-sample test.
- **Significance Level:** $\alpha = 0.05$ (5% threshold).

### 3.2 Test Selection: Welch's Independent Two-Sample T-Test
Welch's t-test is used instead of Student's t-test because it does **not** assume equal population variances ($\sigma_1^2 \neq \sigma_2^2$), which is standard in real-world retail transaction data.

#### T-Statistic Formula:
$$t = \frac{\bar{X}_1 - \bar{X}_2}{\sqrt{\frac{s_1^2}{N_1} + \frac{s_2^2}{N_2}}}$$

Where:
- $\bar{X}_1, \bar{X}_2$ = sample means of Male and Female sales.
- $s_1^2, s_2^2$ = sample variances (unbiased, ddof=1).
- $N_1, N_2$ = sample sizes of Male and Female orders.

#### Welch-Satterthwaite Degrees of Freedom ($\nu$):
$$\nu \approx \frac{\left(\frac{s_1^2}{N_1} + \frac{s_2^2}{N_2}\right)^2}{\frac{\left(\frac{s_1^2}{N_1}\right)^2}{N_1 - 1} + \frac{\left(\frac{s_2^2}{N_2}\right)^2}{N_2 - 1}}$$

#### 95% Confidence Interval for Difference of Means:
$$\text{Standard Error } (SE) = \sqrt{\frac{s_1^2}{N_1} + \frac{s_2^2}{N_2}}$$
$$\text{Critical Value } (t_{\text{crit}}) = t_{1 - \alpha/2, \, \nu} = t_{0.975, \, \nu}$$
$$\text{Margin of Error } (ME) = t_{\text{crit}} \times SE$$
$$\text{CI}_{95\%} = (\bar{X}_1 - \bar{X}_2) \pm ME$$

### 3.3 Decision Rule
- If $p < \alpha$ (0.05): **Reject $H_0$** (Statistically significant difference).
- If $p \ge \alpha$ (0.05): **Fail to Reject $H_0$** (No statistically significant difference).
- If the 95% Confidence Interval spans zero (lower bound $< 0 <$ upper bound), zero difference remains plausible.

---

## 4. Historical Benchmark vs. Live Calculation Contract

To guarantee absolute scientific integrity:
1. **Live Calculation:** The statistical service `app/services/statistics.py` **always computes fresh statistics** from `active_df`. It never returns hardcoded outputs.
2. **Historical Validation Check:**
   When the unmodified internship dataset is loaded ($N=1,000$), the computed results must reproduce the historical values:
   - Male Orders: 511 | Female Orders: 489
   - Male Mean: ₹141,807.34 | Female Mean: ₹136,883.21
   - Mean Difference: ₹4,924.13
   - T-statistic: 0.683 ($\pm 0.005$)
   - P-value: 0.495 ($\pm 0.005$)
   - 95% CI: −₹9,231.58 to ₹19,079.85
   - Decision: Fail to Reject $H_0$
3. **Uploaded Dataset Behavior:** If a user uploads custom data or cleans the dataset, the test calculates genuine values which may legitimately result in "Reject $H_0$".

---

## 5. Edge Case & Guardrail Specifications

| Scenario | Detection Rule | Safe Handling Behavior |
|---|---|---|
| **Single Gender Group** | Unique values in Gender column $< 2$ | Test aborted; warning card displayed: *"Statistical t-test requires two independent groups. Found: 1 group."* |
| **Insufficient Sample Size** | Either group count $N < 5$ | Test aborted; warning card displayed: *"Sample size too small for reliable t-test ($N < 5$)."* |
| **Zero Variance** | Sample variance $s^2 = 0$ in either group | Test aborted; message: *"Cannot compute t-statistic: zero variance in group."* |
| **Missing Values in Sales** | NaN or Null in `Total_Sales` | Handled via pairwise omission (`dropna()`) with count of excluded rows reported. |
| **Non-binary Gender Values** | More than 2 gender categories present | UI prompts user to select the two primary comparison cohorts (e.g., Male vs. Female). |
