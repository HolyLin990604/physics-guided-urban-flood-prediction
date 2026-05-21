# Phase 32 Domain-/Boundary-Aware Physical Consistency Findings

## 1. Executive Summary

Phase 32 formalizes a conservative Level 4+ domain-/boundary-aware physical consistency strategy using Phase 31 recovered masks and masked diagnostic support.

Phase 32 is design/diagnostic-only. It does not train a model, modify losses, modify training configs, or alter model architecture. It does not justify immediate seed42 training, seed123 or seed202 expansion, or tolerance/weight sweeps.

The current decision is:

`design_ready_no_training_yet`

Level 4+ proxy diagnostics are supported. Level 5 remains unsupported because the repository still lacks the hydrodynamic state, flux, boundary-condition, spacing, and time-step information required for stronger physics claims.

## 2. What Phase 32 Adds Beyond Phase 31

Phase 31 established that masked physical proxy diagnostics are feasible. Phase 32 translates that recovered capability into a formal design and guardrail framework.

The added Phase 32 contribution is not a new training method. It is a design framework that:

- assigns physical and diagnostic roles to recovered masks;
- identifies the Phase 29 trade-off that future work must avoid;
- defines region-aware guardrail groups;
- formalizes 20 guardrail metrics;
- formalizes 12 stop/go criteria;
- preserves the Level 4+ / Level 5 claim boundary;
- sets the current decision to `design_ready_no_training_yet`.

This means Phase 32 provides a structured basis for future diagnostic refinement or for a later narrow pilot review. It does not itself justify training.

## 3. Evidence Used From Phase 31

Phase 32 relies on the following Phase 31 inputs:

- `valid_domain = absolute_DEM < 99` is supported as the main valid-domain mask.
- `boundary_ring` and `interior` masks are supported.
- `high_impervious_valid` is supported.
- `manhole_nonzero_valid` is supported.
- Sample-to-location mapping was recovered from adjacent `evaluation_test/test_batch_*/summary.json` metadata using `metadata.location`.
- Masked diagnostics are supported for existing forecast-map outputs.

These inputs support Level 4+ static-map-aware, domain-aware, boundary-aware, and region-specific proxy diagnostics. They do not provide full hydrodynamic closure.

## 4. Region Roles

`valid_domain` is the main physical target domain. Future physical proxy diagnostics or candidate objectives should be restricted to this region unless a separate design decision documents otherwise.

`interior` is a stable core-domain diagnostic region. It helps separate broad valid-domain behavior from boundary-sensitive behavior.

`boundary_ring` is a boundary-sensitive wet/dry guardrail region. It is useful for monitoring false-dry and false-wet behavior near valid-domain edges, but it is not a substitute for boundary flux or boundary-condition data.

`high_impervious_valid` is a false-wet guardrail region. It should be used conservatively because imperviousness is a static runoff proxy, not a direct hydraulic state variable.

`manhole_nonzero_valid` is a false-dry diagnostic and guardrail region. It should be treated as a sparse drainage-indicator proxy, not as source/sink closure or a complete drainage-network representation.

`invalid_or_high` is diagnostic contrast only. It is not a physical target domain and should not receive future physical-consistency objectives.

## 5. Phase 29 Masked-Diagnostic Lesson

The Phase 29 masked diagnostic result is mixed and should not be treated as a Phase 29 success claim.

Phase 29 improved the valid-domain relative volume-bias proxy relative to Phase 27:

| Metric | Phase 27 | Phase 29 |
| --- | ---: | ---: |
| valid-domain relative volume-bias proxy | 0.0169359 | 0.0115344 |

However, Phase 29 worsened several valid-domain masked metrics:

| Metric | Phase 27 | Phase 29 |
| --- | ---: | ---: |
| valid-domain RMSE | 0.0460827 | 0.0480984 |
| valid-domain MAE | 0.0183693 | 0.0190492 |
| valid-domain false-dry rate | 0.0689175 | 0.0739891 |
| valid-domain false-wet rate | 0.0181923 | 0.0194308 |
| valid-domain false-dry volume-loss proxy | 3575.36 | 4027.38 |
| valid-domain false-wet volume-excess proxy | 5263.67 | 5690.27 |

Region-specific Phase 29 concerns are also important:

- `manhole_nonzero_valid` has the highest Phase 29 false-dry rate: `0.131298`.
- `high_impervious_valid` has the highest Phase 29 false-wet rate: `0.0239894`.

The lesson is conservative: future physical proxy design must not optimize a volume-bias proxy while allowing worse RMSE, MAE, false-dry behavior, false-wet behavior, or region-specific wet/dry failures.

## 6. Guardrail Metrics

Phase 32 formalizes 20 guardrail metrics before any future training pilot.

The guardrail groups are:

- `standard`
- `valid_domain`
- `boundary_ring`
- `high_impervious_valid`
- `manhole_nonzero_valid`
- `dry_threshold`
- `level_boundary`

The guardrail framework includes standard evaluation quality, valid-domain masked errors, boundary-ring wet/dry behavior, high-impervious false-wet behavior, manhole-region false-dry behavior, dry-threshold accumulation behavior, and claim-boundary checks.

These metrics are guardrails for future decision-making. They are not evidence that a new loss has been implemented or validated.

## 7. Stop/Go Criteria

Phase 32 formalizes 12 stop/go criteria.

The current stop/go position is conservative:

- Phase 32 remains design/diagnostic-only before training.
- A future objective has not yet been selected.
- Target region and mask definitions are partly established by design, but must be fixed before any pilot.
- Guardrail metric categories are defined, but acceptance and rejection thresholds are not yet fixed.
- Phase 27 and Phase 29 masked baselines are available, but full baseline acceptance/rejection criteria are not yet written.
- Claims remain Level 4+ proxy framed.
- No strict conservation, full mass conservation, SWE/PINN, or hydrodynamic-closure claim is supported.

Because the objective, thresholds, and full baseline acceptance/rejection criteria are not yet fixed, training is not justified.

## 8. Current Decision

Current decision:

`design_ready_no_training_yet`

This decision means Phase 32 has a documented design and guardrail framework, but the project should not proceed directly to training.

A future seed42 pilot would require all guardrails, target regions, baseline comparisons, and acceptance/rejection thresholds to be fixed before training begins.

## 9. What Is Allowed Next

Allowed next work is limited to conservative diagnostic or design refinement, such as:

- refining the Phase 32 guardrail definitions;
- documenting acceptance and rejection thresholds;
- fixing baseline comparison tables before any pilot;
- reviewing whether one diagnosed failure mode is sharp enough for a seed42-only pilot;
- extending masked diagnostics without changing training behavior;
- preparing a future pilot proposal that remains Level 4+ proxy framed.

A seed42 pilot may be considered only after all stop/go criteria are satisfied before training.

## 10. What Is Not Allowed

Phase 32 does not justify:

- immediate seed42 training;
- seed123 or seed202 training;
- tolerance sweeps;
- weight sweeps;
- direct continuation of the Phase 29 tolerance-band approach;
- modifying `utils/physics_losses.py`;
- adding or changing training configs;
- modifying model architecture;
- treating invalid/high DEM cells as a physical target domain;
- treating impervious or manhole maps as full hydraulic forcing, source/sink, or drainage-capacity fields;
- claiming Phase 29 success;
- claiming strict conservation;
- claiming full mass conservation;
- claiming SWE/PINN;
- claiming hydrodynamic closure.

## 11. Level Boundary

Supported Level 4+ scope:

- static-map-aware diagnostics;
- domain-aware diagnostics;
- boundary-aware diagnostics;
- masked physical proxy metrics;
- region-specific failure-mode analysis;
- guarded future proxy design.

Unsupported Level 5 scope:

- strict mass conservation;
- full mass conservation;
- SWE/PINN residuals;
- hydrodynamic closure;
- flux-based residuals;
- boundary-condition closure;
- claims requiring aligned velocity or flux fields, boundary inflow/outflow fields, source/sink fields, explicit `dx/dy`, explicit physical `dt`, or complete hydrodynamic state variables.

This boundary should remain explicit in future Phase 32 work.

## 12. Final Conclusion

Phase 32 successfully translates Phase 31 recovered masks and masked diagnostics into a conservative Level 4+ domain-/boundary-aware physical consistency design. However, it remains `design_ready_no_training_yet`.

The next step may be further diagnostic/design refinement or a carefully justified seed42 pilot only after all stop/go criteria are satisfied. Immediate training, seed expansion, and tolerance/weight sweeps are not justified by the current Phase 32 evidence.
