# Phase 20 Manuscript Draft Assembly Plan

## 1. Objective

Phase 20 aims to assemble a first full manuscript draft skeleton from the Phase 18 manuscript-oriented reliability-aware warning layer notes and the Phase 19 manuscript structure and submission consolidation.

This phase is a manuscript draft assembly phase. It should convert the existing project narrative, reliability-aware warning framework, preserved quantitative findings, and section-level outline into an initial paper draft structure. It should not reopen model development or generate new experimental evidence.

## 2. Non-Goals

Phase 20 must not include:

- no retraining;
- no architecture modification;
- no Phase 10 loss modification;
- no `boundary_weight` tuning;
- no `boundary_band_pixels` tuning;
- no new sweep;
- no new result generation;
- no new uncertainty claim.

## 3. Planned Main Deliverable

The main Phase 20 draft file should be:

- `docs/manuscript_draft_reliability_aware_urban_flood_warning.md`

This file should serve as the first manuscript draft skeleton, with major sections populated by draft academic text or structured placeholders where final wording, figures, tables, or submission formatting remain pending.

## 4. Draft Structure

The manuscript draft should use the following structure:

- Title
- Abstract
- Keywords
- 1. Introduction
- 2. Study Area and Dataset
- 3. Hydrodynamic Simulation and Surrogate Model
- 4. Physics-Guided Prediction Framework
- 5. Reliability-Aware Warning Layer
- 6. Results
- 7. Discussion
- 8. Conclusions
- Figure and Table Placeholders

## 5. Writing Source Documents

The draft should be assembled from existing manuscript and framework materials, especially:

- `docs/manuscript_reliability_aware_warning_layer.md`
- `docs/manuscript_structure_and_submission_consolidation.md`
- `docs/phase17_reliability_warning_framework_synthesis.md`
- Phase 12-16 findings documents

## 6. Required Preserved Facts

The manuscript draft must preserve the following established facts:

- current Phase 10 setting: `boundary_band_pixels = 1`, `boundary_weight = 2.0`;
- Phase 15: 57 Phase 10 map files loaded;
- Phase 15: 114 scenario-level risk records;
- Phase 15: 16384 pixel-level risk records;
- Phase 15: 76 reliable, 25 caution, 13 high-risk;
- Phase 15: Phase 13-like `location2+r300y` cases 24/24 flagged as caution/high-risk;
- Phase 16: scenario warnings reliable=76, caution=25, high-risk=13;
- Phase 16: pixel warnings reliable=5714, caution=8805, high-risk=1865;
- Phase 16: high-risk warning cases=13, matching Phase 15 high-risk cases.

## 7. Drafting Principles

The manuscript draft should:

- write in academic English;
- keep claims precise;
- avoid overclaiming calibrated uncertainty;
- avoid claiming universal generalization;
- avoid claiming that the surrogate replaces hydrodynamic modeling;
- use figure and table placeholders instead of inventing new results.

## 8. Completion Criteria

Phase 20 is complete when:

- this plan is committed;
- the first manuscript draft skeleton is created;
- major manuscript sections are populated with draft text or structured placeholders;
- figure and table placeholders are included;
- `README.md`, `docs/project_status.md`, and `docs/experiment_index.md` are updated only if useful;
- the branch is merged into `main`.
