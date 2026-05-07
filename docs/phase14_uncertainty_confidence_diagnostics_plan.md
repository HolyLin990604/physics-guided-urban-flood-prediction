# Phase 14 Uncertainty / Confidence Diagnostics Plan

## Objective

Phase 14 builds on the Phase 12 reliability/applicability diagnosis and the Phase 13 representative failure-case visual summary.

The purpose is not to retrain the model, change the architecture, tune Phase 10 parameters, or open a new sweep. The purpose is to diagnose whether the current Phase 10 recommended model provides observable signals that can indicate when its predictions may be less reliable.

The core question is:

Can the model or its outputs provide warning signs before or when it becomes unreliable?

This phase should move the project from knowing where failures occur toward diagnosing whether failure risk can be detected from output-space confidence proxies and cross-seed disagreement.

## Starting Point

The current recommended Phase 10 setting remains:

- `boundary_band_pixels = 1`
- `boundary_weight = 2.0`

This setting has already passed test-facing confirmation on:

- `seed123`
- `seed42`
- `seed202`

Phase 12 identified the main reliability limits:

- exact wet/dry boundary cells
- shallow threshold-adjacent cells
- moderate-to-deep depths
- high-intensity `location2` scenarios
- local peak-depth extremes

Phase 13 visually confirmed that the highest-ranked failures collapse into two high-intensity `location2` target scenarios repeated across seeds, with systematic underprediction, reduced predicted wet fraction, local peak-depth underprediction, and false-dry dominated wet/dry mismatch.

Phase 14 should use this evidence as the starting point.

## Scope

In scope:

- output-space confidence proxy diagnosis
- wet/dry threshold margin analysis
- cross-seed disagreement analysis
- relation between confidence proxies and actual error
- relation between confidence proxies and wet/dry mismatch
- relation between confidence proxies and Phase 12/13 caution zones
- diagnostic tables, JSON summaries, and figures

Out of scope:

- retraining
- changing U-Net + TCN architecture
- changing rainfall-conditioned temporal gate design
- changing Phase 10 loss implementation
- tuning `boundary_weight`
- tuning `boundary_band_pixels`
- adding a new uncertainty head
- opening a new model-family search
- claiming calibrated probabilistic uncertainty without calibration evidence

## Primary Inputs

Phase 14 should reuse existing saved outputs.

Phase 10 test-facing forecast maps:

- `runs/phase10_margin_aware_boundary_band_seed123_40e/evaluation_test/test_batch_*/forecast_maps.npz`
- `runs/phase10_margin_aware_boundary_band_seed42_40e/evaluation_test/test_batch_*/forecast_maps.npz`
- `runs/phase10_margin_aware_boundary_band_seed202_40e/evaluation_test/test_batch_*/forecast_maps.npz`

Phase 12 diagnostics:

- `analysis/phase12_reliability/summary.json`
- `analysis/phase12_reliability/timestep_metrics.csv`
- `analysis/phase12_reliability/depth_bin_metrics.csv`
- `analysis/phase12_reliability/boundary_distance_metrics.csv`
- `analysis/phase12_reliability/scenario_metrics.csv`
- `analysis/phase12_reliability/failure_cases.csv`

Phase 13 failure-case visual summaries:

- `analysis/phase13_failure_cases/selected_failure_cases.csv`
- `analysis/phase13_failure_cases/summary.json`
- `analysis/phase13_failure_cases/figures/`

## Diagnostic Direction 1: Wet/Dry Confidence Margin

The first deterministic confidence proxy should be based on distance from the wet/dry threshold.

For each predicted pixel:

- `confidence_margin = abs(prediction - wet_threshold)`

With the current wet threshold:

- `wet_threshold = 0.05`

Interpretation:

- low margin means the prediction is close to the wet/dry decision boundary
- high margin means the prediction is farther from the threshold
- low-margin predictions may be more prone to wet/dry classification errors

Diagnostic questions:

- Are wet/dry classification errors concentrated in low-margin pixels?
- Are false-dry errors associated with low prediction confidence margin?
- Do exact wet/dry boundary cells have lower confidence margin?
- Do high-intensity `location2` failure cases show lower margin in the missed wet areas?
- Does margin-based risk separate correct wet/dry classification from mismatch regions?

Expected outputs:

- confidence-margin bins
- per-bin wet/dry error rate
- per-bin false-dry rate
- per-bin false-wet rate
- per-bin RMSE / MAE
- summary figure showing error rate versus confidence margin

## Diagnostic Direction 2: Cross-Seed Disagreement

The second confidence proxy should use the existing multi-seed outputs as a lightweight ensemble-style diagnostic.

Available seeds:

- `seed123`
- `seed42`
- `seed202`

For matched scenarios, compare predictions across seeds.

Possible disagreement metrics:

- per-pixel standard deviation of predicted depth
- per-pixel range of predicted depth
- per-scenario mean disagreement
- wet/dry disagreement rate across seeds
- disagreement within boundary regions
- disagreement inside Phase 13 failure cases

Diagnostic questions:

- Do high-error scenarios show larger cross-seed disagreement?
- Is disagreement higher near wet/dry boundaries?
- Is disagreement higher in high-intensity `location2` cases?
- Does cross-seed disagreement align with absolute error or wet/dry mismatch?
- Do repeated Phase 13 failure scenarios show consistent underprediction despite different seeds?

Expected outputs:

- seed-disagreement metrics by scenario
- seed-disagreement metrics by boundary-distance band
- seed-disagreement metrics by depth bin
- scatter figure: disagreement versus RMSE
- scatter figure: disagreement versus wet/dry class error

## Diagnostic Direction 3: Risk Proxy Relationship

The third direction should connect confidence proxies with actual reliability risk.

Risk labels may include:

- high absolute error
- false dry
- false wet
- wet/dry mismatch
- deep underprediction
- high-risk Phase 13 scenarios

Candidate explanatory variables:

- prediction confidence margin
- boundary-distance band
- target depth bin
- predicted depth bin
- cross-seed disagreement
- scenario-level target wet fraction
- scenario-level target maximum depth

Diagnostic questions:

- Which confidence proxy best separates reliable from unreliable pixels?
- Are false-dry regions more associated with low margin or high disagreement?
- Are deep-underprediction regions detectable from prediction magnitude or disagreement?
- Are boundary regions consistently low-confidence or high-disagreement?
- Can high-risk `location2` scenarios be identified by scenario-level proxy metrics?

Expected outputs:

- risk_proxy_metrics.csv
- scenario_risk_proxy_metrics.csv
- figures relating proxy values to actual errors
- summary.json identifying the most informative proxy signals

## Suggested First Script

Create:

- `scripts/analyze_phase14_confidence.py`

The script should run from the repository root.

Suggested CLI options:

- `--output-dir`
- `--wet-threshold`
- `--margin-bins`
- `--include-seed-disagreement`
- `--dpi`

Expected output directory:

- `analysis/phase14_confidence/`

Expected files:

- `analysis/phase14_confidence/summary.json`
- `analysis/phase14_confidence/confidence_margin_metrics.csv`
- `analysis/phase14_confidence/seed_disagreement_metrics.csv`
- `analysis/phase14_confidence/risk_proxy_metrics.csv`
- `analysis/phase14_confidence/scenario_confidence_metrics.csv`
- `analysis/phase14_confidence/figures/`

## Suggested Figures

Recommended first-pass figures:

- confidence margin versus wet/dry class error
- confidence margin versus false-dry rate
- confidence margin by boundary-distance band
- cross-seed disagreement versus scenario RMSE
- cross-seed disagreement versus wet/dry class error
- Phase 13 failure-case confidence maps if straightforward

Optional figures:

- spatial confidence-margin map for representative failure cases
- spatial cross-seed disagreement map for matched `location2` scenarios
- joint risk plot combining confidence margin and boundary distance

## Implementation Rules For Codex

Codex should follow these rules:

1. Do not modify model architecture.
2. Do not modify training code.
3. Do not modify Phase 10 loss implementation.
4. Do not retrain.
5. Do not tune `boundary_weight`.
6. Do not tune `boundary_band_pixels`.
7. Do not recompute model predictions unless strictly necessary.
8. Prefer saved Phase 10 `forecast_maps.npz` outputs.
9. Use Phase 12 and Phase 13 outputs as diagnostic context.
10. Do not claim calibrated uncertainty unless calibration is explicitly measured.
11. Use terms such as confidence proxy, risk proxy, or disagreement proxy unless true probabilistic uncertainty is justified.
12. Save all new outputs under `analysis/phase14_confidence/`.
13. Keep the first implementation simple, reproducible, and diagnostic.

## Expected Deliverables

Minimum deliverables:

- `docs/phase14_uncertainty_confidence_diagnostics_plan.md`
- `scripts/analyze_phase14_confidence.py`
- `analysis/phase14_confidence/summary.json`
- `analysis/phase14_confidence/confidence_margin_metrics.csv`
- `analysis/phase14_confidence/seed_disagreement_metrics.csv`
- `analysis/phase14_confidence/risk_proxy_metrics.csv`
- `analysis/phase14_confidence/scenario_confidence_metrics.csv`

Optional deliverables:

- diagnostic figures under `analysis/phase14_confidence/figures/`
- `docs/phase14_uncertainty_confidence_diagnostics_findings.md`
- README update after Phase 14 findings are stable

## Success Criteria

Phase 14 should be considered successful if it can answer:

- whether low wet/dry confidence margin is associated with higher classification error
- whether false-dry errors are detectable from confidence-margin behavior
- whether cross-seed disagreement is higher in difficult scenarios
- whether boundary regions show lower confidence or higher disagreement
- whether high-intensity `location2` failure cases have identifiable confidence or disagreement signatures
- whether any output-space proxy can help identify model risk without retraining

## Expected Interpretation

A successful Phase 14 first pass should not claim that the model has fully calibrated uncertainty.

The expected interpretation should be cautious:

- confidence margin is an output-space proxy, not a calibrated probability
- cross-seed disagreement is a lightweight ensemble-style proxy, not a full Bayesian uncertainty estimate
- useful proxies can still support operational reliability screening
- failure-risk signals should be reported as diagnostic indicators rather than guaranteed predictors

## Next Step

After this plan is committed, Codex can be used to implement `scripts/analyze_phase14_confidence.py`.

The first coding pass should generate confidence-margin, cross-seed disagreement, and risk-proxy diagnostics only. It should not modify the model, retrain, or reopen Phase 10 tuning.
