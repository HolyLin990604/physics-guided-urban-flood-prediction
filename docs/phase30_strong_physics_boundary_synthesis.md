# Phase 30 Strong Physics Boundary Synthesis

## 1. Executive Summary

Phases 24 through 29 move the project from reliability-aware flood-depth prediction toward a more physically interpretable and conservation-proxy-evaluated surrogate. The strongest defensible current position is that the project has advanced to a reliability-aware, physical-consistency-diagnosed, conservation-proxy-evaluated flood surrogate.

This is a meaningful improvement over an unconstrained black-box predictor because the project now diagnoses physically interpretable failure modes, links those failures to reliability categories, evaluates aggregate and timestep-wise volume-response proxies, and communicates applicability boundaries.

However, the current repository evidence does not support claims of strict mass conservation, full hydrodynamic closure, shallow-water-equation residual consistency, PINN behavior, or Level 5 strong physics. The available outputs primarily consist of predicted and target flood-depth rasters, with limited or missing information about velocity, flux, boundary conditions, source/sink terms, explicit grid spacing, explicit timestep duration, and compatible topography.

Therefore, the current strong-physics level should be stated conservatively as:

**Level 4 conservation-proxy / physical-consistency-guided surrogate.**

## 2. Evidence Chain from Phase 24 to Phase 29

Phase 24 established that high-risk cases are not only statistically worse, but also physically less consistent. The diagnosed failure modes included stronger false-dry behavior, wet-area contraction, peak-depth underprediction, wet-connectivity loss, and increasingly negative volume-response bias. These physical diagnostics were strongly linked to the reliability and warning-risk scores, with reported correlations of `0.913` for false-dry rate, `0.862` for wet-area contraction, `0.856` for peak-depth underprediction, and `0.539` for connectivity loss indicator. Phase 24 therefore justified physical-consistency diagnostics beyond RMSE, MAE, and wet/dry IoU.

Phase 25 converted part of the Phase 24 diagnosis into a targeted depth-field-compatible refinement: `target_wet_recall_consistency`. Across `seed123`, `seed42`, and `seed202`, this refinement improved standard metrics and reduced the intended physical failure modes. Mean standard metric deltas versus Phase 10 were `RMSE = -0.007057`, `MAE = -0.001519`, `wet/dry IoU = +0.076670`, `rollout stability = +0.001035`, and `step RMSE std = -0.001071`. Mean aligned physical deltas included `false_dry_rate = -0.111321`, `wet_area_contraction = -0.079104`, `relative_volume_bias = +0.105093`, and `peak_depth_underprediction = -0.014962`. Phase 25 is therefore a strong three-seed positive targeted refinement, but it is not a complete physical-consistency or hydrodynamic solution.

Phase 26 audited the feasibility of stronger physics claims. It found that Level 4 conservation-oriented diagnostics are partially supported because paired prediction and target depth maps are available for volume-response proxy analysis. It also found that Level 4 conservation-aware loss design remains uncertain, and Level 5 full SWE/PINN residual constraints are not supported. Phase 26 is the key boundary-setting phase: it supports conservation-proxy diagnostics, not strict conservation enforcement.

Phase 27 tested a seed42 underresponse-only `volume_response_consistency` loss. It improved all listed standard seed42 test metrics and several under-response proxies, including false-dry volume loss, wet-area contraction, peak-depth underprediction, false-wet rate, and false-wet volume excess. However, it failed the primary volume-response objective: aggregate absolute relative volume bias worsened by `+0.0216934`, mean-step absolute relative volume bias worsened by `+0.0170953`, and aggregate relative volume bias moved from Phase 25 near-zero behavior toward over-response. Phase 27 should therefore remain a mixed seed42 pilot.

Phase 28 diagnosed why Phase 27 failed its primary volume-response objective. The worsening was not mainly caused by threshold-level false-wet expansion and was not primarily caused by already-wet amplification. The dominant source was `dry_or_threshold` low-depth or near-threshold accumulation, which contributed `+5362.82`, about `76.9%` of the total delta volume bias. This explains how Phase 27 could improve wet/dry thresholded indicators while still worsening aggregate volume-response proxies.

Phase 29 tested a tolerance-band volume consistency redesign on seed42. It partially repaired the Phase 27 volume-response problem: aggregate absolute relative volume bias improved from `0.0246616` to `0.019464`, mean-step absolute relative volume bias improved from `0.257274` to `0.230447`, and `dry_or_threshold` contribution decreased from `0.137662` to `0.131428`. However, the trade-off was not acceptable. Relative to Phase 27, all listed standard metrics worsened, false-dry volume loss worsened, false-wet volume excess worsened, and peak-depth underprediction worsened. Phase 29 should therefore remain a mixed seed42-only tolerance-band pilot, not a confirmed improvement.

## 3. Current Strong-Physics Level

The current strong-physics level is:

**Level 4 conservation-proxy / physical-consistency-guided surrogate.**

The model and surrounding analysis currently support:

- physical consistency diagnostics;
- failure-mode interpretation;
- reliability screening;
- warning-rule guidance;
- conservation-proxy evaluation;
- applicability-boundary communication.

The project does not currently support:

- strict mass conservation;
- full SWE residuals;
- PINN claims;
- hydrodynamic flux consistency;
- boundary-condition closure;
- universal physical reliability.

This distinction should remain explicit in README, manuscript, and future project-status language. The project can be described as physics-guided and physically diagnosed, but not as fully physics-constrained.

## 4. Why Level 5 SWE/PINN Is Not Supported

Level 5 SWE/PINN-style claims require hydrodynamic state and forcing information that is missing, unclear, or not demonstrated as shape-compatible in the current repository evidence.

The missing or unclear requirements include:

- velocity or flux fields;
- boundary inflow and outflow;
- pump and gate operation time series;
- explicit `dx` and `dy`;
- explicit `dt` if timestep duration is not fully traceable;
- source/sink, drainage, and infiltration terms;
- shape-compatible DEM or static elevation;
- boundary and valid-domain masks;
- complete hydrodynamic state variables.

Without these inputs, the project cannot compute a complete continuity residual, cannot close boundary fluxes, cannot evaluate full shallow-water momentum consistency, and cannot justify a PINN or full SWE residual claim. Depth-raster volume sums are useful diagnostic proxies, but they are not equivalent to physically dimensioned water balance or strict mass conservation.

## 5. Lessons from Phase 27 and Phase 29

Phase 27 and Phase 29 show that simple volume-response losses are risky.

Phase 27 improved standard metrics and several under-response-related proxies, but worsened aggregate and timestep-wise volume bias. This means standard predictive improvement and local under-response improvement do not guarantee better volume-response behavior.

Phase 28 showed that the Phase 27 failure was dominated by `dry_or_threshold` low-depth or near-threshold accumulation. This is an important diagnostic because such accumulation can remain weakly visible to thresholded wet/dry metrics while still increasing the volume proxy.

Phase 29 partially repaired the Phase 27 aggregate volume bias and reduced the diagnosed `dry_or_threshold` contribution, but worsened standard metrics, false-dry indicators, false-wet indicators, and peak-depth proxies. This means the tested tolerance-band configuration is directionally informative but not acceptable for confirmation.

Therefore, volume-response loss development should pause unless a new plan justifies a revised objective, sharper diagnostics, and explicit guardrails. The current Phase 27 and Phase 29 evidence does not justify seed expansion, tolerance sweeps, weight sweeps, or success claims.

## 6. Boundary Statement

The project can claim:

- physics-guided surrogate modeling;
- reliability-aware warning support;
- physical-consistency diagnosis;
- conservation-proxy evaluation;
- identified applicability boundaries.

The project cannot claim:

- strict mass conservation;
- full hydrodynamic physical consistency;
- SWE/PINN constraints;
- guaranteed physically consistent prediction;
- full operational replacement of hydrodynamic simulation.

The safest wording is that the model is a rapid flood-depth prediction surrogate with reliability-aware warning support, physical-consistency diagnostics, and conservation-proxy evaluation. It should not be presented as a hydrodynamically closed or strictly conservative simulator.

## 7. Recommended Current Position

The current best defensible position is:

**Use the project as a rapid flood-depth prediction and reliability-aware warning-support surrogate with explicit physical-consistency diagnostics and applicability boundaries.**

This position reflects the strongest evidence from the repository. It recognizes the progress from raw prediction toward reliability screening, warning-rule guidance, and physical failure-mode interpretation, while avoiding unsupported claims about full physical closure.

## 8. Next-Step Decision

The recommended next-step decision is:

- do not continue Phase 27 or Phase 29 seed expansion;
- do not run `seed123` or `seed202` for the current Phase 27 or Phase 29 designs;
- do not perform tolerance or weight sweeps;
- do not immediately design another loss unless a new plan justifies the objective, diagnostics, and guardrails;
- prefer manuscript, README, and research-narrative consolidation next.

This decision follows directly from the Phase 27 and Phase 29 trade-offs. More training would not be justified unless the loss design is reframed around the documented failure mechanisms and the required evaluation criteria are specified in advance.

## 9. Future Data Requirements

Moving beyond Level 4 proxy diagnostics toward stronger physics would require additional aligned data and metadata, including:

- water depth plus velocity and/or flux fields;
- boundary inflow and outflow conditions;
- pump and gate operation time series;
- explicit `dx`, `dy`, and `dt`;
- source/sink terms such as drainage, infiltration, rainfall-runoff generation, and other forcing terms;
- shape-compatible DEM or static elevation;
- valid-domain masks and boundary masks;
- hydrodynamic solver metadata and scenario-level forcing metadata.

These requirements should be treated as prerequisites for any future claim of strict conservation, SWE residual consistency, PINN-style physics enforcement, or full hydrodynamic closure.

## 10. Final Conclusion

Phases 24 through 29 moved the project from physical-consistency diagnosis to strong-physics feasibility boundary identification. The current system is not full-physics-constrained, not strictly mass-conservative, not SWE/PINN-based, and not hydrodynamically closed.

At the same time, it is significantly more credible than a black-box surrogate because it diagnoses physical failure modes, links those modes to reliability risk, evaluates conservation proxies, screens warning reliability, and communicates applicability boundaries.

The correct Phase 30 conclusion is therefore conservative but positive: the project has reached a Level 4 conservation-proxy / physical-consistency-guided surrogate position, and its next strongest contribution is likely narrative consolidation rather than immediate additional volume-response training.
