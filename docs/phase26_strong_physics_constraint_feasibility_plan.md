# Phase 26 Strong Physics Constraint Feasibility Audit and Conservation-Loss Design Plan

## 1. Background

The project has completed Phase 25, where `target_wet_recall_consistency` was introduced as a targeted physical-consistency refinement over the Phase 10 baseline.

Phase 25 showed consistent three-seed improvements over Phase 10 in standard prediction metrics and key physical-consistency indicators. In particular, it reduced false-dry behavior and wet-area contraction while improving RMSE, MAE, and wet/dry IoU.

However, Phase 25 should not be overstated as a complete strong-physics solution. It improves an important local physical failure mode, but it does not explicitly enforce water-volume conservation, continuity residuals, hydrodynamic flux consistency, or shallow-water-equation constraints.

Therefore, Phase 26 moves from targeted physical-consistency refinement toward a feasibility audit for stronger physics constraints.

## 2. Motivation

The long-term objective of this project is not only to minimize RMSE, MAE, or wet/dry IoU, but to build a trustworthy, interpretable, physically consistent, and operationally useful deep-learning surrogate for rapid urban flood warning.

Previous phases established the following chain:

- Phase 12 diagnosed reliability and applicability boundaries.
- Phase 13 visualized representative high-risk failure cases.
- Phase 14 analyzed confidence-margin and cross-seed disagreement proxies.
- Phase 15 transformed reliability diagnostics into risk screening and spatial risk mapping.
- Phase 16 generated warning rules and applicability-boundary guidance.
- Phase 23 demonstrated representative warning case studies.
- Phase 24 deepened physical-consistency diagnosis and showed that high-risk cases are physically less consistent.
- Phase 25 introduced a targeted wet-recall consistency loss and verified that physical failure modes can be partially corrected through loss design.

Phase 26 is designed to answer the next question:

**Can the current data and model outputs support stronger physics constraints, especially conservation-oriented constraints?**

## 3. Key Scientific Question

The core question of Phase 26 is:

**Given the currently available dataset and model outputs, what level of strong physics constraint can be credibly supported?**

More specifically, Phase 26 will determine whether the project can support:

1. A Level 4 conservation-constrained surrogate, where the model is encouraged to satisfy approximate water-volume or mass-response consistency; or
2. A Level 5 full SWE/PINN-style surrogate, where the model would explicitly satisfy shallow-water-equation residuals involving water depth, velocity, flux, terrain, boundary conditions, and source/sink terms.

The expected working hypothesis is:

- The current project may support a Level 4 conservation-constrained surrogate.
- The current project likely does not yet support a Level 5 full SWE/PINN surrogate because key physical variables and boundary data may be unavailable or incomplete.

## 4. Physics-Constraint Levels

### Level 1: Pure data-driven surrogate

The model is evaluated mainly with RMSE, MAE, IoU, and rollout stability.

### Level 2: Weak physics-guided surrogate

The model includes simple physics-inspired losses such as non-negativity, wet/dry consistency, rainfall-depth consistency, topography regularization, and continuity-inspired regularization.

These losses encourage plausible behavior but do not directly enforce conservation laws or PDE residuals.

### Level 3: Targeted physical-consistency refinement

Phase 25 belongs to this level.

The `target_wet_recall_consistency` loss targets a specific diagnosed failure mode: locations that should be wet in the target field but are predicted as dry.

This reduces false-dry behavior and wet-area contraction, but it does not explicitly enforce water-volume conservation.

### Level 4: Conservation-constrained surrogate

This level introduces conservation-oriented diagnostics and potentially conservation-aware loss design.

The central idea is that the predicted flood-depth field should have a physically reasonable volume response relative to rainfall input, target water-depth evolution, wet-area expansion or contraction, false-dry volume loss, and scenario-level intensity.

This is the most realistic next target for the current project.

### Level 5: Full SWE/PINN-style surrogate

This level would require explicit hydrodynamic residuals from the shallow water equations.

It would require additional information such as velocity fields or discharge/flux fields, shape-compatible DEM/static elevation, spatial resolution `dx` and `dy`, time step `dt`, boundary inflow/outflow conditions, pump and gate operation records, infiltration/drainage/source-sink terms, valid computational-domain masks, and boundary masks.

This level should not be claimed unless the required physical variables and metadata are available.

## 5. Phase 26 Objectives

Phase 26 has four main objectives.

### Objective 1: Audit available physics inputs

Check whether the current repository and dataset contain the physical inputs needed for stronger constraints, including:

- flood depth sequence `h(t)`;
- rainfall sequence;
- DEM or static elevation;
- impervious layer;
- manhole or drainage-related static layer;
- time interval `dt`;
- grid spacing `dx` and `dy`;
- scenario metadata;
- valid domain mask;
- boundary mask;
- Phase 10 and Phase 25 predicted flood-depth maps;
- target flood-depth maps.

Special attention should be given to whether DEM/static elevation is shape-compatible with the flood-depth arrays.

### Objective 2: Diagnose conservation residuals without training

Before designing a new loss, Phase 26 should first perform diagnostic-only conservation analysis.

The analysis should compare Phase 10 and Phase 25 outputs using aligned scenarios and quantify whether Phase 25 is more physically consistent in terms of volume response.

Possible diagnostics include:

- target total water volume;
- predicted total water volume;
- predicted-target volume bias;
- timestep-wise volume response;
- scenario-level cumulative volume response;
- false-dry volume loss;
- false-wet volume excess;
- wet-area contraction;
- peak-depth underprediction;
- relationship between rainfall intensity and predicted volume response.

### Objective 3: Determine feasible strong-physics level

Based on the audit and conservation diagnostics, Phase 26 should determine whether the current project supports:

- Level 4 conservation-constrained surrogate design;
- only diagnostic-level conservation analysis for now;
- or whether Level 5 full SWE/PINN constraints are currently unsupported.

### Objective 4: Prepare conservation-loss design if justified

If the diagnostic evidence supports it, Phase 26 should propose a future conservation-aware loss for Phase 27.

The loss should not be implemented blindly in Phase 26. It should be designed only after confirming that the required data are available and that conservation residual analysis provides useful evidence.

## 6. Planned Scripts

### 6.1 scripts/audit_phase26_physics_inputs.py

Purpose:

Audit the repository and dataset for physics-relevant inputs.

Expected checks:

- available static layers;
- shapes of static layers;
- shape compatibility between DEM/static layers and flood-depth arrays;
- rainfall array format;
- flood-depth sequence shape;
- scenario metadata availability;
- availability of Phase 10 and Phase 25 map outputs;
- availability of target arrays;
- possible `dt`, `dx`, and `dy` metadata;
- possible valid-domain or boundary masks.

Expected outputs:

- `analysis/phase26_strong_physics_constraint_feasibility/physics_input_audit.json`
- `analysis/phase26_strong_physics_constraint_feasibility/physics_input_audit.md`

### 6.2 scripts/analyze_phase26_conservation_residual.py

Purpose:

Compute diagnostic-only conservation and volume-response residuals for Phase 10 and Phase 25.

Expected diagnostics:

- target volume;
- predicted volume;
- volume bias;
- relative volume bias;
- false-dry volume loss;
- false-wet volume excess;
- wet-area contraction;
- peak-depth underprediction;
- rainfall-volume response proxy;
- Phase 25 minus Phase 10 differences.

Expected outputs:

- `analysis/phase26_strong_physics_constraint_feasibility/conservation_residual_summary.csv`
- `analysis/phase26_strong_physics_constraint_feasibility/conservation_residual_by_scenario.csv`
- `analysis/phase26_strong_physics_constraint_feasibility/conservation_residual_by_seed.csv`
- `analysis/phase26_strong_physics_constraint_feasibility/summary.json`

### 6.3 scripts/summarize_phase26_physics_feasibility.py

Purpose:

Summarize whether current project data support stronger physics constraints.

Expected outputs:

- `analysis/phase26_strong_physics_constraint_feasibility/physics_feasibility_summary.md`
- `docs/phase26_strong_physics_constraint_feasibility_findings.md`

## 7. Expected Output Directory

All Phase 26 analysis outputs should be saved under:

`analysis/phase26_strong_physics_constraint_feasibility/`

Expected files may include:

- `physics_input_audit.json`
- `physics_input_audit.md`
- `conservation_residual_summary.csv`
- `conservation_residual_by_scenario.csv`
- `conservation_residual_by_seed.csv`
- `summary.json`
- `physics_feasibility_summary.md`
- `figures/`

## 8. Important Constraints

Phase 26 must follow these constraints:

1. Do not return to Phase 10 boundary-weight tuning.
2. Do not perform a Phase 25 weight sweep.
3. Do not add uncontrolled loss terms.
4. Do not begin new training before the physics-input audit and conservation diagnostics are complete.
5. Do not claim full SWE/PINN capability without velocity, flux, boundary, and source-sink data.
6. Do not optimize only for RMSE/MAE.
7. Do not treat connectivity as only an image-segmentation problem; interpret it as part of physical flood propagation reliability.
8. Do not overstate Phase 25 as a complete strong-physics solution.

## 9. Expected Phase 26 Conclusion Types

### Conclusion A: Level 4 is feasible

If current data support robust conservation-residual diagnostics, then the project can proceed to a Phase 27 conservation-aware training stage.

### Conclusion B: Level 4 is partially feasible

If some but not all conservation-related information is available, then Phase 27 should use a conservative volume-response consistency loss rather than a full mass-conservation residual.

### Conclusion C: Level 5 is not currently feasible

If velocity fields, fluxes, boundary conditions, pump/gate operations, and source-sink terms are unavailable, then full SWE/PINN-style constraints should not be claimed.

This is the expected outcome unless additional hydrodynamic variables are found.

## 10. Relationship to Phase 25

Phase 25 was a necessary bridge toward strong physics constraints.

It demonstrated that a diagnosed physical failure mode can be translated into a targeted loss and improved consistently across three seeds.

Phase 26 builds directly on that result by asking whether the next level of physics can be enforced through conservation-oriented diagnostics and, later, conservation-aware loss design.

The logic is:

- Phase 24 diagnosed physical inconsistency.
- Phase 25 corrected one important failure mode.
- Phase 26 audits whether stronger conservation constraints are feasible.
- Phase 27 may implement conservation-aware refinement if Phase 26 supports it.

## 11. Working Hypothesis

The working hypothesis for Phase 26 is:

The current dataset likely supports Level 4 conservation-oriented diagnostics and possibly a conservative volume-response consistency loss, but it likely does not support full Level 5 SWE/PINN residual constraints without additional velocity, flux, boundary, source-sink, and shape-compatible terrain information.

## 12. Immediate Next Step

The immediate next step after this plan is to implement `scripts/audit_phase26_physics_inputs.py` and use it to determine what physics-relevant inputs are actually available in the repository and dataset.