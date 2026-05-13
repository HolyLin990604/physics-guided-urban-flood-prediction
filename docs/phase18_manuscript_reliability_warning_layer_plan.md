# Phase 18 Manuscript Reliability-Aware Warning Layer Plan

## 1. Objective

Phase 18 aims to translate the completed reliability-aware warning framework into manuscript-oriented writing materials.

This phase should convert the Phase 12-17 evidence into clear paper text, tables, section outlines, contribution language, limitations, and result-discussion notes for a manuscript section focused on reliability-aware use of the urban flood surrogate model.

Phase 18 is a writing and synthesis phase. It should not reopen experiments or model development.

## 2. Current basis

Phases 12 through 17 have already built a complete reliability-aware flood-warning framework around the fixed Phase 10 recommended model.

The current project narrative is:

- rapid flood-depth prediction;
- reliability diagnosis;
- failure-mode interpretation;
- confidence proxy diagnostics;
- spatial risk mapping;
- warning-rule guidance.

The Phase 10 recommended model remains fixed, with:

- `boundary_band_pixels = 1`;
- `boundary_weight = 2.0`.

Phase 18 should use the completed Phase 12-17 outputs as the evidence base for manuscript preparation.

## 3. Non-goals

Phase 18 must not include:

- no retraining;
- no architecture modification;
- no Phase 10 loss modification;
- no `boundary_weight` tuning;
- no `boundary_band_pixels` tuning;
- no new sweep;
- no new uncertainty claim;
- no new result generation unless later explicitly needed.

Phase 18 should prepare manuscript-ready content from existing results.

## 4. Main manuscript target

The main target manuscript section should be:

**Reliability-Aware Warning Layer for Urban Flood Surrogate Prediction**

This section should explain how the rapid flood-depth surrogate is paired with deterministic reliability screening, spatial risk mapping, and warning-rule interpretation.

## 5. Planned deliverables

Phase 18 should create manuscript-oriented documents such as:

- `docs/manuscript_reliability_aware_warning_layer.md`;
- optional `docs/manuscript_phase12_16_results_discussion_notes.md`;
- optional `docs/manuscript_reliability_framework_contribution_summary.md`.

The required first output is the Phase 18 plan document:

- `docs/phase18_manuscript_reliability_warning_layer_plan.md`.

Additional manuscript documents should be created only as writing materials. They should not modify experiment outputs or analysis results.

## 6. Content structure for the manuscript section

The manuscript section should include:

- motivation for reliability-aware analysis;
- reliability diagnosis;
- failure-mode interpretation;
- confidence proxy diagnostics;
- risk screening and spatial risk mapping;
- warning-rule and applicability-boundary guidance;
- limitations and non-claims;
- contribution statement.

The writing should connect these components into a coherent reliability-aware warning layer rather than presenting them as disconnected experiment phases.

## 7. How Phase 12-17 map to manuscript sections

The Phase 12-17 materials should map to paper writing as follows:

- Phase 12 -> reliability/applicability diagnosis result;
- Phase 13 -> failure-case explanation result;
- Phase 14 -> confidence proxy analysis;
- Phase 15 -> reliability screening/risk mapping method and result;
- Phase 16 -> warning-rule and applicability-boundary layer;
- Phase 17 -> integrated framework narrative.

Phase 18 should preserve this logic chain while rewriting it in manuscript language.

## 8. Key quantitative facts to preserve

The manuscript materials should preserve the following quantitative facts:

- Phase 15 loaded 57 Phase 10 map files.
- Phase 15 produced 114 scenario-level risk records.
- Phase 15 produced 16,384 pixel-level risk records.
- Phase 15 classified scenario-level labels as 76 reliable, 25 caution, and 13 high-risk.
- Phase 15 flagged Phase 13-like `location2` + `r300y` cases as caution/high-risk in 24 of 24 cases.
- Phase 16 scenario warnings were reliable = 76, caution = 25, and high-risk = 13.
- Phase 16 pixel warnings were reliable = 5,714, caution = 8,805, and high-risk = 1,865.
- Phase 16 identified 13 high-risk warning cases, matching the Phase 15 high-risk cases.

These values should be carried into manuscript text, tables, or result summaries without reinterpretation as new experiments.

## 9. Writing constraints

The manuscript writing must follow these constraints:

- do not claim calibrated probabilistic uncertainty;
- do not claim universal generalization;
- do not claim the surrogate replaces hydrodynamic modeling;
- describe confidence margin as a wet/dry classification risk proxy;
- describe warning labels as deterministic operational interpretation labels;
- preserve applicability-boundary wording.

The manuscript should emphasize that the framework supports reliability-aware interpretation of rapid surrogate predictions, not probabilistic uncertainty quantification or full replacement of physics-based flood modeling.

## 10. Completion criteria

Phase 18 is complete when:

- the plan document is committed;
- at least one manuscript-ready reliability-aware warning layer document is created;
- the manuscript document clearly explains method, results, discussion, limitations, and contribution;
- `README`, `project_status`, and `experiment_index` are updated only if useful;
- the branch is merged into `main`.

Completion should be judged by whether Phase 18 produces manuscript-ready writing materials that accurately synthesize the Phase 12-17 reliability-aware warning framework without introducing new experimental claims.
