# Phase 21 Manuscript Evidence and Figure Alignment Plan

## 1. Objective

Phase 21 aims to align the Phase 20 manuscript draft skeleton with existing evidence, figures, tables, JSON/CSV outputs, and findings documents before full manuscript expansion.

This phase should verify that manuscript claims, figure candidates, table candidates, and quantitative statements are traceable to existing project evidence. It should prepare the manuscript for evidence-supported writing, not create new experiments or results.

## 2. Non-Goals

Phase 21 must not include:

- no retraining;
- no architecture modification;
- no Phase 10 loss modification;
- no `boundary_weight` tuning;
- no `boundary_band_pixels` tuning;
- no new sweep;
- no new result generation;
- no new uncertainty claim;
- no invented figures or unsupported claims.

## 3. Main Deliverable

The main Phase 21 evidence-alignment file should be:

- `docs/manuscript_evidence_figure_table_alignment.md`

This document should serve as the manuscript evidence map for expanding the Phase 20 draft into a complete, supportable paper.

## 4. Evidence Alignment Scope

The alignment document should map each major manuscript claim to existing evidence using the following fields:

- manuscript claim;
- supporting phase;
- supporting file or figure;
- key quantitative value;
- manuscript placement;
- recommendation for main text or supplementary material.

Primary evidence sources include:

- `docs/phase12_reliability_applicability_findings.md`
- `docs/phase13_failure_case_visual_summary_findings.md`
- `docs/phase14_uncertainty_confidence_diagnostics_findings.md`
- `docs/phase15_reliability_screening_risk_mapping_findings.md`
- `docs/phase16_reliability_warning_applicability_findings.md`
- `analysis/phase12_reliability/`
- `analysis/phase13_failure_cases/`
- `analysis/phase14_confidence/`
- `analysis/phase15_reliability_screening/`
- `analysis/phase16_warning_rules/`

The alignment should connect these sources to the current manuscript files:

- `docs/manuscript_draft_reliability_aware_urban_flood_warning.md`
- `docs/manuscript_structure_and_submission_consolidation.md`
- `docs/manuscript_reliability_aware_warning_layer.md`

## 5. Figure and Table Planning Scope

Figure and table candidates should be organized into the following groups:

- study area and dataset;
- model architecture and workflow;
- base prediction performance;
- reliability diagnosis;
- failure-case interpretation;
- confidence proxy diagnostics;
- risk screening and spatial risk mapping;
- warning-rule and applicability-boundary guidance;
- summary contribution tables.

For each candidate, the alignment document should identify the evidence source, intended manuscript section, likely role in the argument, and whether it belongs in the main text or supplementary material.

## 6. Key Claims to Align

Phase 21 should align evidence for the following manuscript claims:

- the surrogate provides rapid flood-depth prediction;
- reliability is non-uniform across depth, boundary, timestep, and scenario conditions;
- severe failures are systematic rather than random;
- confidence margin is useful as a wet/dry classification risk proxy;
- deterministic risk screening identifies reliable, caution, and high-risk cases;
- Phase 13-like `location2+r300y` cases were 24/24 flagged as caution/high-risk;
- warning rules convert deterministic risk labels into operational guidance.

Claims that cannot be supported by existing files should be listed as unresolved evidence gaps or removed from the manuscript expansion plan.

## 7. Preserved Quantitative Facts

The alignment document must preserve the following established facts:

- current Phase 10 setting: `boundary_band_pixels = 1`, `boundary_weight = 2.0`;
- Phase 15: 57 Phase 10 map files loaded;
- Phase 15: 114 scenario-level risk records;
- Phase 15: 16384 pixel-level risk records;
- Phase 15: 76 reliable, 25 caution, 13 high-risk;
- Phase 15: Phase 13-like `location2+r300y` cases 24/24 flagged as caution/high-risk;
- Phase 16: scenario warnings reliable=76, caution=25, high-risk=13;
- Phase 16: pixel warnings reliable=5714, caution=8805, high-risk=1865;
- Phase 16: high-risk warning cases=13, matching Phase 15 high-risk cases.

## 8. Expected Output Structure

The final alignment document should include:

- manuscript claim-to-evidence table;
- figure inventory;
- table inventory;
- main-text versus supplementary recommendation;
- unresolved evidence gaps;
- immediate next writing tasks.

## 9. Completion Criteria

Phase 21 is complete when:

- this plan is committed;
- `docs/manuscript_evidence_figure_table_alignment.md` is created;
- all major manuscript claims are mapped to existing evidence;
- recommended main-text and supplementary figures are identified;
- unresolved gaps are listed;
- `README.md`, `docs/project_status.md`, and `docs/experiment_index.md` are updated only if useful;
- the branch is merged into `main`.
