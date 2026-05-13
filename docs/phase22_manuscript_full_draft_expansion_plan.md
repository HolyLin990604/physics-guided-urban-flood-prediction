# Phase 22 Manuscript Full Draft Expansion Plan

## 1. Objective

Phase 22 aims to expand the Phase 20 manuscript draft skeleton into a fuller academic manuscript draft by using the Phase 21 claim-evidence and figure/table alignment document.

This is a manuscript full-draft expansion phase, not a new experiment phase. The work should convert the existing manuscript skeleton, evidence map, reliability-aware warning framework, and preserved quantitative findings into a more complete academic draft with fuller prose, clearer section transitions, and evidence-traceable results interpretation.

## 2. Non-Goals

Phase 22 must not include:

- no retraining;
- no architecture modification;
- no Phase 10 loss modification;
- no `boundary_weight` tuning;
- no `boundary_band_pixels` tuning;
- no new sweep;
- no new result generation;
- no invented references;
- no unsupported claims.

## 3. Main Deliverable

The main Phase 22 manuscript output should be:

- `docs/manuscript_full_draft_reliability_aware_urban_flood_warning.md`

This file should expand the Phase 20 skeleton into a fuller academic manuscript draft while preserving evidence traceability to Phase 21 and earlier findings documents.

## 4. Expansion Strategy

The Phase 22 draft should expand the following manuscript sections beyond skeleton form:

- Abstract;
- Introduction;
- Study Area and Dataset;
- Hydrodynamic Simulation and Surrogate Model;
- Physics-Guided Prediction Framework;
- Reliability-Aware Warning Layer;
- Results;
- Discussion;
- Conclusions.

Expansion should prioritize academic continuity, explicit links between methods and results, and cautious interpretation of the reliability-aware warning framework. The draft should use the Phase 20 manuscript skeleton as the starting structure and the Phase 21 evidence alignment document as the control document for claim support.

## 5. Evidence Alignment Requirement

Every major result claim in the Phase 22 manuscript draft should be traceable to:

- `docs/manuscript_evidence_figure_table_alignment.md`

Claims should remain connected to existing supporting documents, figures, tables, CSV files, JSON summaries, or prior phase findings. Claims that are not supported by the Phase 21 alignment document should be removed, softened, or left as explicitly marked evidence gaps rather than presented as established findings.

## 6. Figure and Table Placeholder Policy

Figure and table placeholders should be retained where final journal-ready figures or tables have not yet been selected.

Placeholders should identify the intended manuscript role and, where known, the candidate evidence source from the Phase 21 figure and table inventory. Phase 22 should not invent new figures, tables, values, captions, or visual evidence beyond the existing project outputs and documented placeholders.

## 7. Preserved Quantitative Facts

The Phase 22 manuscript draft must preserve the following established quantitative facts:

- current Phase 10 setting: `boundary_band_pixels = 1`, `boundary_weight = 2.0`;
- Phase 15: 57 Phase 10 map files loaded;
- Phase 15: 114 scenario-level risk records;
- Phase 15: 16384 pixel-level risk records;
- Phase 15: 76 reliable, 25 caution, 13 high-risk;
- Phase 15: Phase 13-like `location2+r300y` cases 24/24 flagged as caution/high-risk;
- Phase 16: scenario warnings reliable=76, caution=25, high-risk=13;
- Phase 16: pixel warnings reliable=5714, caution=8805, high-risk=1865;
- Phase 16: high-risk warning cases=13, matching Phase 15 high-risk cases.

These values should not be recalculated, altered, rounded differently, or extended into new claims during Phase 22.

## 8. Writing Constraints

The Phase 22 manuscript draft should:

- write in academic English;
- use placeholders for literature citations;
- do not invent new citations;
- do not claim calibrated probabilistic uncertainty;
- do not claim universal generalization;
- do not claim the surrogate replaces hydrodynamic modeling in high-stakes decisions;
- preserve deterministic warning-label wording.

Warning labels such as reliable, caution, and high-risk should be described as deterministic interpretation labels derived from the documented warning framework, not as calibrated probabilities, Bayesian uncertainty estimates, confidence intervals, or guaranteed error bounds.

## 9. Completion Criteria

Phase 22 is complete when:

- the plan document is committed;
- the full manuscript draft file is created;
- major sections are expanded beyond skeleton form;
- preserved quantitative facts remain accurate;
- evidence alignment is respected;
- `README.md`, `docs/project_status.md`, and `docs/experiment_index.md` are updated if useful;
- the branch is merged into `main`.
