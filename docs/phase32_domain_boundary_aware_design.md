# Phase 32 Domain-/Boundary-Aware Physical Consistency Design

## 1. Executive Summary

Phase 32 formalizes a conservative Level 4+ domain-/boundary-aware physical consistency design based on Phase 31 recovered static masks and masked depth-raster diagnostics.

This is not a Level 5 physics model. It does not claim strict conservation, full mass conservation, SWE/PINN residuals, or full hydrodynamic closure. The supported scope is structured physical proxy diagnosis and future guardrail design over valid-domain, boundary-ring, high-impervious, and manhole-nonzero regions.

The design conclusion is conservative: Phase 32A should remain design/diagnostic-first. No immediate loss implementation, architecture modification, configuration change, seed expansion, or sweep is justified by the current evidence.

## 2. Design Inputs from Phase 31

Phase 31 recovered enough physical context to support Level 4+ masked proxy diagnostics:

- `valid_domain = absolute_DEM < 99` is supported as a candidate valid-domain mask.
- `invalid_or_high = absolute_DEM >= 99` is supported as a diagnostic contrast region.
- `boundary_ring` and `interior` masks are supported and shape-compatible with 128 x 128 flood maps.
- `high_impervious_valid` is supported as a valid-domain static runoff-proxy region.
- `manhole_nonzero_valid` is supported as a valid-domain sparse drainage-indicator proxy region.
- Train/test masks are consistent for the inspected locations.
- Sample-to-location mapping was recovered from adjacent `evaluation_test/test_batch_*/summary.json` files using `metadata.location`.
- Masked diagnostics are fully supported for existing forecast-map outputs.

These inputs support domain-aware and boundary-aware diagnostics. They do not provide velocity, flux, boundary inflow/outflow, source/sink terms, explicit `dx/dy`, explicit physical `dt`, or complete hydrodynamic state variables.

## 3. Failure Modes to Target

Phase 31 masked diagnostics show that Phase 29 should not be treated as a broad physical-consistency success.

Phase 29 improved the valid-domain masked relative volume-bias proxy versus Phase 27:

| Metric | Phase 27 | Phase 29 |
| --- | ---: | ---: |
| valid-domain relative volume-bias proxy | 0.0169359 | 0.0115344 |

However, Phase 29 worsened the main valid-domain masked error and wet/dry proxy metrics:

| Metric | Phase 27 | Phase 29 | Interpretation |
| --- | ---: | ---: | --- |
| valid-domain RMSE | 0.0460827 | 0.0480984 | worsened |
| valid-domain MAE | 0.0183693 | 0.0190492 | worsened |
| valid-domain false-dry rate | 0.0689175 | 0.0739891 | worsened |
| valid-domain false-wet rate | 0.0181923 | 0.0194308 | worsened |
| valid-domain false-dry volume-loss proxy | 3575.36 | 4027.38 | worsened |
| valid-domain false-wet volume-excess proxy | 5263.67 | 5690.27 | worsened |

Region-specific concerns are also clear:

- `manhole_nonzero_valid` has the highest Phase 29 false-dry rate: `0.131298`.
- `high_impervious_valid` has the highest Phase 29 false-wet rate: `0.0239894`.
- Boundary-ring false-dry worsened from Phase 27 to Phase 29.

The design target is therefore not a generic volume-bias improvement. The target is a guarded Level 4+ proxy strategy that avoids trading lower volume-bias proxy for worse masked RMSE, MAE, false-dry behavior, false-wet behavior, and region-specific wet/dry failures.

## 4. Region Roles

### `valid_domain`

Main physical target domain for Level 4+ proxy diagnostics. Future physical-consistency metrics should be restricted to this region unless a stronger reason is documented.

### `interior`

Stable core-domain diagnostic region. It is useful for separating broad model behavior from boundary-sensitive behavior.

### `boundary_ring`

Boundary-sensitive wet/dry guardrail region. It should be used to monitor false-dry and false-wet behavior near valid-domain edges, while recognizing that true boundary fluxes are unavailable.

### `high_impervious_valid`

False-wet guardrail region inside the valid domain. Imperviousness is a static runoff proxy, not a hydraulic state variable, so this region should be used conservatively for diagnostic and guardrail purposes.

### `manhole_nonzero_valid`

False-dry diagnostic and guardrail region inside the valid domain. The manhole map is a sparse indicator, not a complete drainage/source-sink field, so this region should not be treated as hydrodynamic closure.

### `invalid_or_high`

Diagnostic contrast only. This region should not be treated as a physical target domain and should not receive future physical-consistency objectives.

## 5. Candidate Objective Families

These are design-level concepts only. They are not implementation instructions and do not justify modifying losses yet.

### A. Valid-Domain Masked Consistency

Restrict physical proxy evaluation to `valid_domain = absolute_DEM < 99`. This avoids treating high/invalid DEM cells as a physical target domain.

Possible proxy focus:

- valid-domain RMSE and MAE;
- valid-domain false-dry and false-wet rates;
- valid-domain relative volume-bias proxy.

Main risk: by itself, this can repeat the Phase 29 pattern of improving volume-bias proxy while worsening other masked errors.

### B. Boundary-Ring Wet/Dry Guardrail

Use `boundary_ring` to monitor wet/dry behavior near valid-domain edges.

Possible proxy focus:

- boundary-ring false-dry rate;
- boundary-ring false-wet rate;
- boundary-ring peak-depth underprediction;
- boundary-ring volume-bias proxy.

Main risk: boundary cells are physically ambiguous without measured boundary fluxes or boundary-condition fields.

### C. High-Impervious False-Wet Guardrail

Use `high_impervious_valid` to detect or guard against spurious wet expansion in high-impervious valid-domain cells.

Possible proxy focus:

- high-impervious false-wet rate;
- high-impervious false-wet volume-excess proxy;
- high-impervious RMSE and MAE.

Main risk: imperviousness is a static descriptor and should not be interpreted as a full runoff, drainage, or hydraulic forcing term.

### D. Manhole-Region False-Dry Monitor

Use `manhole_nonzero_valid` to monitor underprediction in sparse drainage-indicator regions.

Possible proxy focus:

- manhole-nonzero false-dry rate;
- manhole-nonzero false-dry volume-loss proxy;
- manhole-nonzero peak-depth underprediction.

Main risk: manhole indicators do not provide drainage capacity, flow direction, source/sink magnitude, or operational state.

### E. Dry-Threshold Accumulation Guard

Monitor dry or near-threshold cells so future proxy objectives do not create low-depth accumulation or false-wet expansion.

Possible proxy focus:

- dry-or-threshold predicted-volume contribution;
- false-wet expansion near the dry threshold;
- low-depth accumulation proxy.

Main risk: threshold behavior is sensitive to metric definitions and can create new trade-offs if tuned without standard-metric guardrails.

## 6. Recommended Design Choice

The recommended Phase 32A choice is:

**Design/diagnostic-first; no immediate loss implementation.**

Phase 32 should not continue directly from Phase 29, modify `utils/physics_losses.py`, add a training config, run seed123/seed202, or perform tolerance/weight sweeps.

If a future pilot is considered, it should be a narrow guarded Level 4+ proxy design with:

- valid-domain restriction;
- boundary-ring false-dry monitoring;
- high-impervious false-wet monitoring;
- manhole-nonzero false-dry monitoring;
- dry-threshold accumulation monitoring;
- explicit standard-metric guardrails.

Any future pilot should be seed42-only unless a separate stop/go review justifies expansion. The pilot objective must target one diagnosed failure mode and must be evaluated against fixed baselines before training begins.

## 7. Guardrail Metrics

Guardrails must be defined before any future training pilot.

### Standard Guardrails

- Overall RMSE must not worsen beyond a predeclared tolerance.
- Overall MAE must not worsen beyond a predeclared tolerance.
- Wet/dry IoU must not decline beyond a predeclared tolerance.
- Rollout stability must not degrade.
- Existing standard evaluation tables must remain comparable to Phase 25, Phase 27, and Phase 29 baselines.

### Valid-Domain Guardrails

- valid-domain RMSE;
- valid-domain MAE;
- valid-domain false-dry rate;
- valid-domain false-wet rate;
- valid-domain relative volume-bias proxy;
- valid-domain false-dry volume-loss proxy;
- valid-domain false-wet volume-excess proxy.

### Boundary-Ring Guardrails

- boundary-ring false-dry rate;
- boundary-ring false-wet rate;
- boundary-ring peak-depth underprediction;
- boundary-ring absolute relative volume-bias proxy.

### High-Impervious Guardrails

- high-impervious false-wet rate;
- high-impervious false-wet volume-excess proxy;
- high-impervious RMSE;
- high-impervious MAE.

### Manhole-Region Guardrails

- manhole-nonzero false-dry rate;
- manhole-nonzero false-dry volume-loss proxy;
- manhole-nonzero peak-depth underprediction;
- manhole-nonzero RMSE and MAE.

### Dry-Threshold Guardrails

- dry-or-threshold predicted-volume contribution;
- false-wet expansion near the dry threshold;
- low-depth accumulation proxy;
- dry-threshold contribution as a share of total predicted valid-domain proxy volume.

## 8. Stop/Go Criteria for Any Future Pilot

A future seed42 pilot is allowed only if all of the following are true before training:

1. The objective targets one diagnosed failure mode.
2. The target region and mask are fixed before training.
3. All standard, valid-domain, boundary-ring, high-impervious, manhole, and dry-threshold guardrails are defined.
4. The design explicitly avoids repeating the Phase 27 underresponse-only failure.
5. The design explicitly avoids repeating the Phase 29 tolerance-band trade-off.
6. Baseline comparisons are fixed before training.
7. Acceptance and rejection criteria are written before training.
8. No claim goes beyond Level 4+ proxy framing.

If any criterion is unmet, the project should remain diagnostic-only.

## 9. What Not To Do

Phase 32 should not:

- continue Phase 29 directly;
- run seed123 or seed202;
- tune tolerance or weight values;
- introduce unguarded volume-loss objectives;
- treat invalid/high DEM cells as a physical target domain;
- treat impervious or manhole maps as full hydraulic forcing or source/sink fields;
- modify model architecture;
- modify losses;
- modify training configs;
- perform sweeps;
- claim strict conservation, full mass conservation, SWE/PINN, Level 5 physics, or full hydrodynamic closure.

## 10. Final Design Decision

Decision = `design_ready_no_training_yet`

Next step = optional diagnostic script to formalize guardrail metrics, or Phase 32 findings if no more scripts are needed.
