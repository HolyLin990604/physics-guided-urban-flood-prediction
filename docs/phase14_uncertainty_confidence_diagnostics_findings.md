# Phase 14 Uncertainty / Confidence Diagnostics Findings

## Purpose

Phase 14 builds on the Phase 12 reliability/applicability diagnosis and the Phase 13 representative failure-case visual summary.

The purpose is not to retrain the model, change the architecture, modify the Phase 10 loss, tune `boundary_weight`, tune `boundary_band_pixels`, or open a new sweep. The purpose is to diagnose whether the current Phase 10 recommended model provides output-space signals that can help identify when predictions may be less reliable.

The diagnostic object remains the Phase 10 recommended setting:

- `boundary_band_pixels = 1`
- `boundary_weight = 2.0`

The Phase 14 analysis is explicitly proxy-based. It uses deterministic confidence, risk, and disagreement proxies. It should not be interpreted as calibrated probabilistic uncertainty.

## Inputs

Phase 14 uses saved Phase 10 test-facing forecast maps from:

- `runs/phase10_margin_aware_boundary_band_seed123_40e/evaluation_test/test_batch_*/forecast_maps.npz`
- `runs/phase10_margin_aware_boundary_band_seed42_40e/evaluation_test/test_batch_*/forecast_maps.npz`
- `runs/phase10_margin_aware_boundary_band_seed202_40e/evaluation_test/test_batch_*/forecast_maps.npz`

It also uses Phase 12 and Phase 13 diagnostic context:

- `analysis/phase12_reliability/failure_cases.csv`
- `analysis/phase12_reliability/scenario_metrics.csv`
- `analysis/phase13_failure_cases/summary.json`

No model predictions were recomputed by retraining. No model code was modified.

## Outputs

Phase 14 generated:

- `scripts/analyze_phase14_confidence.py`
- `analysis/phase14_confidence/summary.json`
- `analysis/phase14_confidence/confidence_margin_metrics.csv`
- `analysis/phase14_confidence/seed_disagreement_metrics.csv`
- `analysis/phase14_confidence/risk_proxy_metrics.csv`
- `analysis/phase14_confidence/scenario_confidence_metrics.csv`
- `analysis/phase14_confidence/figures/confidence_margin_vs_wet_dry_error.png`
- `analysis/phase14_confidence/figures/seed_disagreement_vs_rmse.png`

The full default run produced:

- 114 scenario confidence rows
- 38 matched cross-seed disagreement rows

## Diagnostic 1: Confidence-Margin Proxy

The first proxy is the wet/dry confidence margin:

`confidence_margin = abs(prediction - wet_threshold)`

The wet/dry threshold is:

`wet_threshold = 0.05`

This proxy measures how far each predicted depth is from the wet/dry decision threshold. A low confidence margin means that the prediction lies close to the classification boundary.

## Main Finding 1: Low Confidence Margin Indicates Wet/Dry Classification Risk

The confidence-margin diagnostics show a clear relationship between low confidence margin and wet/dry classification error.

In the aggregate results:

| Confidence-margin bin | Wet/dry class error rate | False-dry rate |
|---|---:|---:|
| `[0,0.005)` | 0.4549 | 0.4930 |
| `[0.005,0.01)` | 0.3637 | 0.4772 |
| `[0.01,0.02)` | 0.2323 | 0.4537 |
| `[0.02,0.05)` | 0.0290 | 0.3996 |
| `[0.05,0.1)` | 0.0045 | 0.0631 |

This shows that pixels close to the wet/dry threshold are much more likely to be misclassified.

The result supports the use of confidence margin as a wet/dry classification risk proxy.

## Main Finding 2: Confidence Margin Is Not A Direct Depth-Error Uncertainty Measure

Confidence margin is useful for wet/dry classification risk, but it should not be interpreted as a general water-depth error uncertainty measure.

The high-margin bin `[0.2,5)` has very low wet/dry class error, but RMSE and MAE can still be high because many cells in this bin are clearly wet and may still have substantial depth-magnitude error.

This distinction is important:

- confidence margin is useful for threshold-based wet/dry decision risk
- confidence margin is not sufficient to explain all continuous water-depth errors
- high confidence in wet/dry state does not guarantee accurate depth magnitude

This is consistent with the Phase 12 and Phase 13 findings that local peak-depth underprediction remains an important reliability limit.

## Diagnostic 2: Risk-Proxy Relationship

The risk-proxy metrics further support the distinction between classification risk and depth-magnitude risk.

False-dry cells show much lower confidence margins than correct-wet cells. In the aggregate results:

| Wet/dry outcome | Mean confidence margin | Interpretation |
|---|---:|---|
| false dry | 0.0234 | close to threshold, high wet/dry risk |
| correct wet | 0.2943 | clearly wet, low wet/dry classification risk |

This supports the interpretation that false-dry errors are associated with lower confidence-margin behavior.

However, correct-wet cells can still have nontrivial RMSE and MAE. Therefore, margin-based diagnostics should be used for wet/dry reliability screening, not as a complete replacement for depth-error evaluation.

## Diagnostic 3: Boundary And Depth Risk

The risk-proxy metrics also align with the earlier Phase 12 reliability diagnosis.

Boundary-distance results show that exact boundary cells remain much riskier than far-field cells:

| Boundary-distance band | RMSE | MAE | Wet/dry class error rate |
|---|---:|---:|---:|
| boundary_0px | 0.0890 | 0.0434 | 0.1329 |
| near_boundary_1_3px | 0.0628 | 0.0217 | 0.0083 |
| far_field_gt3px | 0.0159 | 0.0088 | 0.0015 |

This confirms the Phase 12 conclusion that exact wet/dry boundary cells remain a major reliability bottleneck.

Depth-bin results also remain consistent with Phase 12:

- shallow cells show high wet/dry class error
- moderate and deep target-depth cells show larger continuous depth errors
- deep cells are not mainly a wet/dry classification problem, but a depth-magnitude underprediction problem

This supports a two-part interpretation:

- threshold-adjacent shallow cells are difficult for wet/dry classification
- moderate-to-deep cells are difficult for depth magnitude accuracy

## Diagnostic 4: Cross-Seed Disagreement Proxy

The second proxy is cross-seed disagreement.

The script compares matched scenarios across:

- `seed123`
- `seed42`
- `seed202`

It computes scenario-level prediction disagreement across seeds and relates this disagreement to scenario-level error.

The global correlation between mean prediction standard deviation across seeds and mean seed RMSE is approximately:

`0.151`

This indicates only weak global correlation.

## Main Finding 3: Cross-Seed Disagreement Is An Auxiliary Proxy, Not A Strong Standalone Error Predictor

Cross-seed disagreement should not be treated as a strong standalone scenario-error predictor.

The `seed_disagreement_vs_rmse` figure shows a scattered relationship rather than a strong linear trend. The low correlation suggests that multi-seed disagreement can provide useful auxiliary information, but it does not by itself reliably rank all high-error scenarios.

This is an important negative/limited result.

It means that repeated model seeds can help indicate some instability, but high scenario error can also occur when different seeds fail in a similar way. This is especially relevant to Phase 13, where the highest-ranked failures repeated across seeds and showed similar underprediction patterns.

## Relationship To Phase 13

Phase 13 found that the highest-ranked failures collapse into two high-intensity `location2` scenarios repeated across seeds:

- `location2 / r300y_p0.6_d3h / start_idx = 0`, worst step 1
- `location2 / r300y_p0.8_d3h / start_idx = 0`, worst step 4

Phase 14 adds an important interpretation.

The Phase 13 failure cases are not simply explained by low confidence margin everywhere. Their scenario-level mean confidence margin is moderate, and their low-margin fraction is not extreme.

This means that the Phase 13 failures are better interpreted as structured underprediction and wet-area contraction in specific high-intensity `location2` scenarios, rather than as purely threshold-ambiguous predictions.

Therefore:

- confidence margin helps identify wet/dry threshold risk
- Phase 13 failures also involve systematic depth and extent underprediction
- cross-seed disagreement is limited because multiple seeds can fail similarly

## Practical Interpretation

Phase 14 provides useful operational reliability-screening signals, but the findings must be interpreted carefully.

The practical interpretation is:

1. Low confidence margin can flag pixels where wet/dry classification is risky.
2. False-dry errors are associated with lower confidence margins.
3. Boundary cells remain the main classification-risk zone.
4. Moderate-to-deep depths still require depth-error diagnostics because margin alone does not capture peak-depth underprediction.
5. Cross-seed disagreement is useful as an auxiliary signal, but weak as a standalone scenario-risk predictor.
6. Phase 13 high-intensity `location2` failures show that multiple seeds can fail in a similar way, so low disagreement does not guarantee reliability.

## What Phase 14 Does Not Claim

Phase 14 does not claim calibrated probabilistic uncertainty.

The outputs should not be interpreted as:

- predictive probability
- Bayesian posterior uncertainty
- calibrated confidence interval
- guaranteed error bound

The correct interpretation is:

- confidence-margin proxy for wet/dry threshold risk
- disagreement proxy for seed-wise prediction variability
- risk-proxy diagnostics for reliability screening

## Decision

The Phase 14 first-pass confidence diagnostics are useful and should be retained.

The strongest supported conclusion is:

Confidence margin is a useful proxy for wet/dry classification risk.

The main limitation is:

Cross-seed disagreement has weak global correlation with scenario RMSE and should be treated as auxiliary evidence rather than a strong standalone predictor.

No retraining, architecture change, Phase 10 loss change, or boundary-weight sweep is justified by this Phase 14 first pass.

## Next Step

After this findings document is reviewed and committed, the next step is a light documentation sync:

- update `docs/project_status.md`
- update `docs/experiment_index.md`
- optionally update `README.md` with a concise Phase 14 note

A future follow-up may consider more explicit uncertainty methods only if the proxy-based diagnostics indicate a clear need. Possible directions include:

- confidence maps for Phase 13 failure cases
- scenario-level reliability screening rules
- calibrated uncertainty only if calibration data and evaluation design are added
