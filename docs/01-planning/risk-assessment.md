# Risk Assessment — Sales Analytics Workbench

**SDLC Phase:** 1 — Project Planning and Feasibility Study

---

## 1. Risk Register

| ID | Risk | Category | Likelihood | Impact | Mitigation |
|---|---|---|---|---|---|
| R-1 | Python 3.14 incompatibility with a required library | Technical | Low | High | Verified: streamlit, pandas, plotly, scipy install cleanly on 3.14.7. Created `.venv`. |
| R-2 | Missing openpyxl / python-docx / python-pptx in clean environment | Technical | Low | Medium | Requirements file will pin all runtime + doc dependencies. |
| R-3 | Upload of unsupported file type crashes app | Functional | Medium | Medium | File-type allow-list validation before parsing. |
| R-4 | Empty dataset leads to empty statistics / chart errors | Functional | Medium | Medium | Guarded empty-state handling with clear user messages. |
| R-5 | Statistical test invalid for single-group / tiny datasets | Functional | Medium | Medium | Small-dataset guard; statistical tests only run when group sizes are sufficient. |
| R-6 | User cleans data silently, destroying original data | Data integrity | Low | High | Never mutate original uploaded frame; cleaned copy is produced only on explicit action. |
| R-7 | Historical results accidentally hardcoded as new results | Correctness | Medium | High | Internship mode reuses *documented* constants; uploaded mode always recomputes live. |
| R-8 | Dependency version drift between developer and evaluator | Technical | Low | Medium | Pin versions in `requirements.txt`; document environment setup. |
| R-9 | Power BI deliverable misrepresented as Python output | Communication | Low | High | Clear labeling: Power BI is an authentic deliverable shown via screenshots + DAX; Python charts are separate. |
| R-10 | Scope creep (adding features beyond internship) | Process | High | Low | Strict out-of-scope list enforced during implementation. |

## 2. Risk Handling Strategy

- All risks are registered in this document.
- **High** risks (R-6, R-7, R-9) must be resolved before Phase 4 (Implementation).
- Medium risks: mitigated via test coverage (Phase 5).
- Residual risk acceptance: local single-user demo assumes trusted data source.

## 3. Risk Review Triggers

Reassess the register at the end of each SDLC phase before proceeding.

## 4. Contingency

If dependency installation fails on a participant machine, fallback: use the
recommended Python 3.12 virtual environment documented in Phase 6.
