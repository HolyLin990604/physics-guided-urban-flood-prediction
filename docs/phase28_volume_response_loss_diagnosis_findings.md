# Phase 28 Volume-Response Loss Diagnosis Findings

## 1. Purpose

Phase 28 diagnosed why the Phase 27 seed42 conservative volume-response pilot improved standard metrics and several under-response proxies but worsened aggregate and timestep-wise absolute relative volume bias.

This phase used committed diagnostic outputs from:

- `analysis/phase28_volume_response_loss_diagnosis/phase28_volume_response_failure_findings.md`
- `analysis/phase28_volume_response_loss_diagnosis/volume_bias_decomposition_summary.csv`
- `analysis/phase28_volume_response_loss_diagnosis/volume_bias_depth_bin_decomposition.csv`
- `analysis/phase28_volume_response_loss_diagnosis/volume_bias_timestep_ranking.csv`

Phase 28 was diagnostic only. It did not train a model, modify architecture, change losses, run additional seeds, or perform a Phase 27 weight sweep.

## 2. Main Diagnosis

The Phase 27 aggregate volume-response worsening did not come from threshold-level false-wet expansion and did not primarily come from already-wet amplification.

Key aggregate evidence:

- Delta volume bias total = `+6974.12`
- Phase 25 relative volume bias = `+0.00296825`
- Phase 27 relative volume bias = `+0.0246616`
- Delta absolute relative volume bias = `+0.0216934`
- Mean paired delta absolute relative volume bias = `+0.0170953`
- False-wet volume excess delta = `-184.071`
- Already-wet amplification = `+1396.20`

The false-wet volume excess delta was negative, so threshold-level false-wet expansion does not explain the worsening. Already-wet amplification was positive, but it was much smaller than the total `+6974.12` increase in volume bias, so it is not sufficient as the main explanation.

The dominant target-depth-bin contribution was `dry_or_threshold`:

| Target depth bin | Phase27 - Phase25 predicted-volume contribution | Share of total delta volume bias |
|---|---:|---:|
| `dry_or_threshold` | `+5362.82` | `0.768959` |
| `shallow` | `+486.678` | `0.0697833` |
| `moderate` | `+907.330` | `0.130100` |
| `deep` | `+217.298` | `0.0311578` |

The `dry_or_threshold` bin accounted for about `76.9%` of the total delta volume bias.

## 3. Interpretation

The most likely explanation is that Phase 27 added sub-threshold or near-threshold water-depth mass in target-dry or threshold-adjacent cells.

These values may not cross the `0.05 m` wet/dry threshold. As a result, they do not necessarily worsen false-wet rate or wet/dry IoU, but they still accumulate in the volume proxy. This explains why Phase 27 could improve thresholded and local under-response indicators while worsening aggregate volume bias.

This interpretation is a volume-proxy diagnosis from forecast depth rasters. It should not be treated as evidence of strict mass conservation, hydrodynamic consistency, or full SWE/PINN behavior.

## 4. Why Phase 27 Was Mixed

Phase 27 was standard-metric positive and improved several local under-response indicators, including false-dry volume loss, wet-area contraction, peak-depth preservation, and false-wet volume excess.

However, the primary volume-response objective failed because aggregate and timestep-wise absolute relative volume bias worsened. The run-level aggregate relative volume bias shifted from near-balanced in Phase 25 to a larger positive bias in Phase 27:

- Phase 25 = `+0.00296825`
- Phase 27 = `+0.0246616`

Therefore, Phase 27 remains a mixed seed42 pilot: standard-metric positive, but volume-response objective not confirmed.

## 5. Underresponse-Only Loss Mismatch

The Phase 25 seed42 baseline was already near aggregate volume balance, with relative volume bias `+0.00296825`.

Applying an underresponse-only volume loss to a near-balanced case can push the model toward over-response. The Phase 28 evidence is consistent with that risk: Phase 27 reduced some under-response proxies, but the aggregate signed relative volume bias moved farther positive.

This does not prove that underresponse-only volume losses are always unsuitable. It does indicate that the Phase 27 formulation was poorly matched to this near-balanced seed42 case and should not be directly expanded.

## 6. Recommended Redesign

The best-supported redesign direction is tolerance-band volume consistency.

Future loss design should:

- avoid penalizing near-zero volume bias;
- avoid pushing near-balanced cases into over-response;
- penalize only when signed relative volume bias exceeds a tolerance band;
- continue monitoring both signed and absolute volume bias;
- separately monitor `dry_or_threshold`-bin contributions;
- preserve Phase 25 and Phase 27 gains in false-dry volume loss, wet-area contraction, peak-depth preservation, and standard metrics.

A tolerance-band design would be more consistent with the Phase 28 diagnosis than simply increasing the Phase 27 underresponse-only loss weight. It should first be specified in a plan and then evaluated as a new training phase only after the diagnostic criteria and guardrails are clear.

## 7. Guardrails

Phase 28 does not justify claims of:

- strict mass conservation;
- full SWE/PINN behavior;
- full hydrodynamic consistency;
- strict timestep-wise conservation;
- confirmed Phase 27 success;
- seed123 or seed202 confirmation readiness.

The Phase 28 analysis is based on diagnostic volume proxies from prediction and target depth rasters. It should remain framed as a conservative diagnosis of the Phase 27 seed42 failure mode.

## 8. Decision

Phase 28 supports stopping direct expansion of the Phase 27 underresponse-only `volume_response_consistency` design.

Do not run seed123 or seed202 confirmation from the current Phase 27 formulation. Do not perform a Phase 27 weight sweep. Future work should redesign the loss before any new training.

The recommended decision is:

`stop_direct_phase27_expansion_redesign_loss_first`

## 9. Possible Next Phase

A possible next phase is:

`Phase 29 -- Tolerance-Band Volume Consistency Redesign`

Phase 29 should start with a plan, not training. That plan should define the tolerance-band objective, signed and absolute volume-bias diagnostics, `dry_or_threshold` monitoring, and preservation guardrails for the standard metrics and local under-response gains observed in Phase 25 and Phase 27.
