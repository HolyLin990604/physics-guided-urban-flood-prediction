# Phase 41 SWE Data Readiness Audit Plan

## 1. Executive Summary

Phase 41 is a no-training SWE Data Readiness Audit after Phase 40 selected:

`selected_decision = pause_loss_redesign_move_to_swe_data_readiness`

Phase 41 audits whether the repository and available datasets contain the data required for future Level 5 / SWE-oriented physical constraints. It does not implement SWE residual constraints, does not implement PINN behavior, does not train models, and does not authorize training.

Phase 41 should produce a documented inventory of SWE-oriented data availability, alignment, and missing inputs. The audit should determine whether future SWE residual prototype work is data-supported, partially supported, unsupported, or uncertain because required data may exist only outside the current repository export.

Planned audit script:

`scripts/audit_phase41_swe_data_readiness.py`

Expected output directory:

`analysis/phase41_swe_data_readiness_audit/`

## 2. Background from Phase 38-40

Phase 38 ran the authorized seed42 pilot using `manhole_nonzero_false_dry_guardrail`. That pilot was rejected under the predeclared guardrail framework.

Phase 39 diagnosed the rejected pilot and found a Phase29-like trade-off pattern. The pilot improved a narrow manhole-related false-dry proxy while failing broader valid-domain, regional guardrail, and standard metric checks.

Phase 40 completed a failed-pilot design review and selected:

`selected_decision = pause_loss_redesign_move_to_swe_data_readiness`

Phase 40 also recorded:

`training_authorized = false`

`next_recommended_phase = phase41_swe_data_readiness_audit`

The Phase 40 decision does not claim pilot success, strict conservation, full mass conservation, SWE/PINN behavior, hydrodynamic closure, or Level 5 support. It only recommends a no-training audit of whether the project has the data needed for future SWE-oriented physical constraints.

## 3. Purpose of SWE Data Readiness Audit

The purpose of Phase 41 is to determine whether current repository files, dataset exports, configuration metadata, preprocessing artifacts, and analysis outputs contain the data required to support future Level 5 / SWE-oriented residual constraints.

Phase 41 should answer:

1. Are required SWE-oriented fields present in the repository or datasets?
2. Are those fields spatially and temporally aligned with the model inputs and targets?
3. Are key numerical metadata fields such as `dx`, `dy`, and `dt` explicitly available?
4. Are boundary conditions and source/sink terms available with enough specificity for residual-style constraints?
5. Are hydrodynamic state variables available beyond water-depth targets or proxy masks?
6. Can existing data support only Level 4+ proxy diagnostics, or can it support future Level 5 residual prototypes?
7. Which missing inputs block SWE/PINN or hydrodynamic closure claims?

This phase is an audit and classification phase only.

## 4. Required SWE-Oriented Data Categories

Phase 41 should audit the following required data categories:

- `velocity_or_flux_fields`
- `dx_dy_grid_spacing`
- `dt_time_step`
- `boundary_conditions`
- `source_sink_terms`
- `pump_gate_operations`
- `hydrodynamic_state_variables`
- `rainfall_source_alignment`
- `DEM/static_elevation_alignment`
- `valid_domain_and_boundary_masks`

For each category, the audit should record:

- whether the category is present, missing, partial, or uncertain;
- candidate file paths or repository references;
- field names, array names, column names, or config keys;
- spatial resolution, if discoverable;
- temporal resolution, if discoverable;
- alignment with model inputs, targets, masks, and scenarios;
- whether the field is directly usable for future SWE residual work;
- whether the field only supports proxy diagnostics;
- notes explaining limitations or assumptions.

## 5. Repository and Dataset Search Targets

Phase 41 should search existing repository content only. It may inspect files and metadata, but it must not regenerate data through training or model evaluation.

Primary search targets:

- `datasets/`
- `configs/`
- `scripts/`
- `analysis/`
- `README.md`
- `docs/`
- `utils/`
- `trainers/`
- `models/`

The search should include file names, directory names, config keys, dataset field names, CSV headers, JSON keys, NumPy archive keys where safely inspectable, and existing documentation text.

Suggested search terms include:

- velocity, flux, discharge, flow, flowrate, qx, qy, u, v
- dx, dy, grid, spacing, resolution, cellsize
- dt, timestep, time_step, interval, cadence
- boundary, upstream, downstream, inlet, outlet
- source, sink, inflow, outflow, rainfall, runoff
- pump, gate, valve, control, operation
- depth, stage, water_level, hydraulic_head, state
- DEM, elevation, static, slope
- mask, valid, domain, boundary_ring

The audit should distinguish explicit physical data from names that only appear in comments, plans, or aspirational documentation.

## 6. Readiness Levels

Phase 41 should classify each required data category and the overall project using conservative readiness levels.

Category-level readiness:

- `present_aligned`: data are explicitly present and aligned to model spatial and temporal dimensions.
- `present_unverified_alignment`: data are present, but alignment is not fully proven.
- `partial`: partial or proxy fields exist, but they are incomplete for SWE residual use.
- `missing`: no usable evidence of the category was found.
- `uncertain_external_export_needed`: repository evidence suggests the data may exist externally, but it is not available in the current repository/dataset export.

Overall readiness decision candidates:

- `swe_data_ready_for_residual_prototype`
- `partial_readiness_needs_data_recovery`
- `not_ready_for_swe_constraints`
- `readiness_uncertain_requires_external_data_export`

The default posture should be conservative. If required fields are not explicitly present and aligned, Phase 41 should not infer readiness from model performance, proxy metrics, or documentation intent.

## 7. Planned Audit Script

Phase 41 should implement:

`scripts/audit_phase41_swe_data_readiness.py`

The script should be audit-only. It must not train, evaluate checkpoints, modify losses, modify configs, modify model architecture, run seeds, launch sweeps, implement SWE residuals, or implement PINN methods.

The script should:

- define the required SWE-oriented data categories;
- search repository files and dataset metadata for candidate fields;
- inventory discovered files and field names;
- inspect lightweight structured metadata where feasible;
- summarize repository search evidence by category;
- classify each category using the readiness levels;
- identify missing critical inputs;
- produce a readiness matrix and final summary;
- fail closed or mark readiness uncertain when evidence is missing, ambiguous, or contradictory.

The script should avoid heavy data processing. Large binary or array files may be inspected only for metadata, shape, and available keys when that can be done safely without training or model execution.

## 8. Expected Outputs

Phase 41 should write outputs to:

`analysis/phase41_swe_data_readiness_audit/`

Required output files:

- `swe_required_data_inventory.csv`
- `repository_search_summary.csv`
- `dataset_field_inventory.csv`
- `swe_readiness_matrix.csv`
- `missing_swe_inputs.csv`
- `phase41_swe_data_readiness_summary.json`
- `phase41_swe_data_readiness_summary.md`

Suggested fields for `swe_required_data_inventory.csv`:

- `category`
- `required_for_swe_residual`
- `why_required`
- `minimum_evidence_needed`
- `present_status`
- `alignment_status`
- `candidate_paths`
- `notes`

Suggested fields for `repository_search_summary.csv`:

- `category`
- `search_term`
- `matches_found`
- `candidate_paths`
- `evidence_type`
- `usable_for_readiness`
- `notes`

Suggested fields for `dataset_field_inventory.csv`:

- `path`
- `file_type`
- `field_or_key`
- `shape_or_columns`
- `category_mapping`
- `spatial_alignment_evidence`
- `temporal_alignment_evidence`
- `notes`

Suggested fields for `swe_readiness_matrix.csv`:

- `category`
- `readiness_level`
- `critical_for_level5`
- `present_evidence`
- `missing_or_uncertain_evidence`
- `supports_level4_proxy_only`
- `supports_level5_swe_residual`
- `interpretation`

Suggested fields for `missing_swe_inputs.csv`:

- `category`
- `missing_input`
- `blocking_level`
- `needed_for`
- `recommended_recovery_action`
- `notes`

## 9. Interpretation Rules

Phase 41 should interpret findings conservatively.

If `velocity_or_flux_fields`, `dx_dy_grid_spacing`, `dt_time_step`, `boundary_conditions`, and `source_sink_terms` are missing, Phase 41 must conclude that Level 5 SWE residual constraints are not currently supported.

If only water depth, rainfall, DEM/static maps, and masks are available, Phase 41 may conclude that the project supports Level 4+ proxy diagnostics, but not full SWE/PINN closure.

If required data categories are present but not aligned to the model grid, time step, target horizon, valid domain, or boundary masks, Phase 41 should classify readiness as partial or uncertain, not ready.

If documentation mentions SWE, conservation, hydrodynamics, or Level 5 concepts but the required data categories are absent, documentation alone must not be treated as evidence of readiness.

If repository evidence suggests that missing hydrodynamic data may exist externally, Phase 41 should use:

`readiness_uncertain_requires_external_data_export`

If the audit finds explicit, aligned velocity or flux fields, grid spacing, time step, boundary conditions, source/sink terms, hydrodynamic state variables, rainfall alignment, elevation alignment, and valid-domain/boundary masks, Phase 41 may classify the project as:

`swe_data_ready_for_residual_prototype`

That classification would still not authorize implementation or training.

## 10. Guardrails

Phase 41 must follow these guardrails:

- no training
- no seed runs
- no sweeps
- no loss edits
- no config edits
- no model architecture edits
- no SWE residual implementation
- no PINN implementation
- no strict conservation claim
- no full mass conservation claim
- no hydrodynamic closure claim
- no Level 5 support claim unless required data categories are explicitly present and aligned

Phase 41 must not reinterpret the rejected Phase 38 pilot as successful. It must preserve Phase 40's decision that training remains unauthorized.

## 11. Success Criteria

Phase 41 succeeds if it produces a clear, reproducible, no-training audit of SWE data readiness.

Minimum success criteria:

- all required SWE-oriented data categories are listed and evaluated;
- repository and dataset search targets are documented;
- candidate fields and paths are inventoried;
- missing or uncertain required inputs are explicitly recorded;
- readiness levels are assigned conservatively;
- the final readiness decision is one of the approved decision candidates;
- the summary states whether current data support Level 5 SWE residual constraints, only Level 4+ proxy diagnostics, or neither;
- all guardrails are preserved.

Phase 41 does not require finding SWE-ready data. A valid outcome may be `not_ready_for_swe_constraints` if critical inputs are missing.

## 12. Final Conclusion

Phase 41 audits whether the project has the data required for future SWE-oriented Level 5 constraints. It does not implement those constraints and does not authorize training.

The audit should provide the evidence needed to decide whether future SWE residual prototype planning is possible, whether data recovery is needed first, or whether the current repository supports only Level 4+ proxy diagnostics rather than full SWE/PINN closure.
