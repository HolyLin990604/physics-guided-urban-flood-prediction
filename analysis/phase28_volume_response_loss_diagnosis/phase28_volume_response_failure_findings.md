# Phase 28 Volume-Response Loss Failure Diagnosis

This diagnostic compares Phase 27 seed42 against the Phase 25 seed42 baseline using existing `evaluation_test/test_batch_*/forecast_maps.npz` files only. It is a volume-response proxy analysis based on depth rasters; it does not train, alter model architecture, alter losses, alter configs, or claim strict mass conservation, SWE, or PINN behavior.

## Direct Answers

1. Did Phase 27's volume-bias worsening come from false-wet expansion? **No**. Total Phase27 - Phase25 false-wet volume excess change was `-184.071` versus total delta volume bias `6974.12`.
2. Did it come from already-wet depth amplification? **No**. Already-wet Phase27 - Phase25 depth amplification summed to `1396.2`.
3. Did it come from a small number of timesteps or broad behavior? **Broad behavior with a concentrated high-worsening tail**; top 10% of paired records account for `0.591` of positive absolute-relative-bias worsening.
4. Did it occur mainly in shallow, moderate, or deep target-depth bins? The largest absolute target-depth-bin contribution was `dry_or_threshold` with `5362.82` Phase27 - Phase25 predicted-volume change.
5. Was underresponse-only volume loss mismatched because Phase 25 seed42 was already near-zero aggregate volume bias? **Yes**. Phase 25 aggregate relative volume bias was `0.00296825`.
6. Which loss redesign is best supported? **tolerance-band volume consistency**.

## Summary Totals

| Metric | Value |
|---|---:|
| paired step records | 456 |
| Phase 25 relative volume bias | 0.00296824696134 |
| Phase 27 relative volume bias | 0.0246616453135 |
| Delta volume bias | 6974.12327529 |
| Delta absolute relative volume bias | 0.0216933983522 |
| Mean paired delta absolute relative volume bias | 0.0170952581496 |
| False-wet volume excess delta | -184.07081075 |
| False-dry volume loss decrease | 809.610759601 |
| Already-wet amplification | 1396.20365276 |

## Target Depth Bins

| Target depth bin | Phase27 - Phase25 predicted volume | Share of total delta volume bias |
|---|---:|---:|
| `dry_or_threshold` | 5362.81712741 | 0.768959 |
| `shallow` | 486.677587979 | 0.0697833 |
| `moderate` | 907.330155142 | 0.1301 |
| `deep` | 217.298404768 | 0.0311578 |

## Conservative Interpretation

The supported redesign should be treated as a diagnostic recommendation, not as confirmation that Phase 27 achieved volume-response consistency. The largest target-depth-bin contribution is in dry-or-threshold cells, while thresholded false-wet volume excess decreased; this indicates that the worsening is not explained by simple false-wet expansion under the 0.05 m wet/dry threshold. Any future loss should avoid pushing near-balanced aggregate cases into over-response and should continue to report signed and absolute relative volume-bias proxy diagnostics.

## Outputs

- `volume_bias_decomposition_by_step.csv`
- `volume_bias_depth_bin_decomposition.csv`
- `volume_bias_timestep_ranking.csv`
- `volume_bias_decomposition_summary.csv`
- `phase28_volume_response_failure_summary.json`
- `phase28_volume_response_failure_findings.md`
