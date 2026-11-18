# Timeline and Milestones — Sales Analytics Workbench

**SDLC Phase:** 1 — Project Planning and Feasibility Study

---

## 1. High-Level Schedule (Estimated)

| Phase | Title | Duration | Key Deliverables |
|---|---|---|---|
| 1 | Project Planning and Feasibility Study | 2 days (complete now) | All `docs/01-planning/` documents, `.gitignore`, project overview, feasibility. |
| 2 | Requirements Analysis | 3 days | SRS, user stories, use cases, acceptance criteria, RTM. |
| 3 | System Design | 3 days | Architecture diagrams, data flow, UI wireframes, module breakdown, SDD. |
| 4 | Implementation | 5 days | Modular code across 5 modules, streaming pipeline, UI pages, DB, statistical tests. |
| 5 | Testing & QA | 3 days | pytest unit + integration + data validation + regression tests; report. |
| 6 | Deployment | 2 days | `requirements.txt`, `.gitignore`, `README.md`, env setup, startup instructions, sample data guide, troubleshooting. |
| 7 | Maintenance & Final Documentation | 2 days | Maintenance plan, known limitations, future enhancements, final project report, SDLC completion summary. |
| **Total** | **18 calendar days** | **~3 weeks** |

> *Note: These are business days, not calendar days. With 5-day work weeks, Phase 1 alone takes roughly half a working week. The full project fits within 3.5 working weeks.*

## 2. Milestone-Gate Review Points

After each phase, the following must be verified before proceeding:

| Milestone | Required sign-off |
|---|---|
| Planning (Phase 1) | All `docs/01-planning/` documents complete, `.gitignore` present, feasibility approved. |
| Requirements (Phase 2) | SRS and RTM approved by reviewer; user stories cover all 20 functional requirements. |
| Design (Phase 3) | SDD approved; architecture reviewed; module boundaries confirmed. |
| Implementation (Phase 4) | All milestones complete; tests written alongside code; reviewer approves feature demo. |
| Testing (Phase 5) | Test suite passes (≥ 90% coverage); critical defects resolved; reviewer approves quality gate. |
| Deployment (Phase 6) | App starts with `streamlit run app/main.py`; docs verified; reviewer approves release readiness. |
| Maintenance (Phase 7) | Final report signed off; future-enhancement backlog created. |

## 3. Buffer Allocation

- 1 working day buffer after Phase 5 (testing) for unexpected defects.
- 1 working day buffer after Phase 6 (deployment) for documentation polish.
- Total schedule has a 2-day (~10%) contingency.

## 4. Milestone-Gate Checklist — Phase 1 Completion

- [x] All 7 documents in `docs/01-planning/` exist and have meaningful content.
- [x] `.gitignore` created at repository root.
- [x] No Phase-I_Evaluation files modified.
- [x] Python venv created at `.venv/`.
- [x] Dependencies installed and verified.
- [ ] Phase 1 report presented to reviewer for explicit approval.