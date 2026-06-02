# Phase 44: UrbanFlood24 Full Level 4+ Replanning

## Executive Summary

Phase 44 is a replanning phase only. No training is run, no seed runs are performed, no loss function is changed, no configuration is changed, and no model architecture is modified.

After Phase 43, the project is replanned under a stricter constraint: future work must use only the already downloaded UrbanFlood24 full dataset. No additional external files, author-provided metadata, hydrodynamic intermediate fields, or ICM/MIKE+ exports will be available or treated as a required path.

Under this constraint, short-term Level 5 / SWE / PINN claims are frozen. The available dataset supports high-resolution Level 4+ proxy modeling, reliability diagnostics, and warning framework extension. It does not support strict hydrodynamic closure, full mass conservation claims, or SWE residual losses.

Future training should begin only after full dataset indexing and dataloader smoke tests are complete.

## Background from Phase 41-43

Phases 41-43 evaluated whether the project could move beyond the earlier benchmark-scale warning framework into a stronger physically constrained modeling setup.

Phase 43 inspected the UrbanFlood24 full dataset at:

```text
E:\BaiduNetdiskDownload\urbanflood24\urbanflood24
```

The Phase 43 result was:

```text
selected_decision = full_dataset_readiness_uncertain_needs_metadata
level5_supported = false
level4_plus_supported = true
training_authorized = false
total_files = 354
total_dirs = 186
sampled_arrays_count = 54
```

The observed full dataset structure included train/test splits, flood/geodata groups, location1/location2/location3, and scenario directories containing `flood.npy` and `rainfall.npy`. The geodata directories contain `absolute_DEM.npy`, `impervious.npy`, and `manhole.npy`.

Observed array shapes were:

```text
flood.npy shape: (360, 1, 500, 500), float64
rainfall.npy shape: (180,) or (360,), float64
static arrays shape: (500, 500), float64
```

Phase 43 therefore found that the full dataset is real, large enough to support future high-resolution modeling experiments, and promising for Level 4+ proxy modeling. It did not establish sufficient evidence for Level 5 hydrodynamic closure.

## New Project Constraint

Future work must be based only on the available UrbanFlood24 full dataset already downloaded at the inspected path.

The following are not available as required project paths:

- No additional external hydrodynamic fields.
- No author-provided metadata.
- No required author clarification path.
- No ICM/MIKE+ export path.
- No additional simulator-derived conservation or flux fields.

This constraint changes the near-term research plan. The project should no longer wait for external metadata before making progress, but it must also avoid unsupported claims that require unavailable information.

## Why Level 5 Is Frozen

Level 5 is frozen because the available files do not expose enough hydrodynamic state and model metadata to support strict conservation, SWE residual training, or full hydrodynamic closure.

The available dataset includes flood depth-like dynamic arrays, rainfall forcing arrays, and static geodata arrays. It does not provide the complete set of fields normally needed to form defensible SWE residuals or conservation checks, such as velocity components, discharge or fluxes, boundary conditions, drainage exchange terms, roughness parameterization, solver metadata, and complete hydraulic connectivity information.

Therefore, the project should not implement SWE residual losses in the near term. It should not claim strict conservation, full mass conservation, or Level 5 physics support. Any physical language should remain limited to proxy diagnostics, terrain-aware checks, rainfall-response consistency, spatial reliability analysis, and warning applicability.

## What UrbanFlood24 Full Can Support

The UrbanFlood24 full dataset can support a stronger Level 4+ research direction:

- High-resolution flood proxy modeling using `flood.npy`, `rainfall.npy`, and static geodata.
- Train/test evaluation across available locations and scenarios.
- Downsampled modeling at practical resolutions such as 128x128 and potentially 256x256.
- Patch or tile-based modeling if full-frame training is too expensive.
- Multiscale modeling that combines global rainfall/static context with local high-resolution tiles.
- Reliability diagnostics based on prediction error, uncertainty proxies, failure cases, event intensity, terrain classes, imperviousness, and manhole proximity.
- Warning framework extension using predicted flood maps and reliability-aware screening.
- Dataset readiness analysis, indexing, and reproducible adapter construction.

This is a meaningful extension over earlier phases because the full dataset has larger spatial coverage and richer scenario structure than small demonstration data.

## What UrbanFlood24 Full Cannot Support

The available dataset alone cannot support the following claims or methods:

- SWE residual loss implementation.
- PINN claims based on explicit shallow-water equation residuals.
- Strict conservation claims.
- Full mass conservation claims.
- Hydrodynamic closure claims.
- Verified Level 5 support.
- Calibration or validation against unavailable simulator internals.
- Claims requiring external author metadata or ICM/MIKE+ exports.

The project can still discuss physical plausibility, terrain-aware behavior, rainfall-response consistency, and reliability limits, but those should be framed as Level 4+ proxy diagnostics rather than Level 5 physics.

## Replanned Research Direction

The replanned direction is:

```text
High-resolution Level 4+ proxy modeling and reliability-aware warning extension
using only the available UrbanFlood24 full dataset.
```

The research should emphasize what can be measured and verified from the available arrays:

- Does the model learn spatial flood response from rainfall and static geodata?
- How does performance change by location, scenario, rainfall length, and flood intensity?
- Where does the model fail spatially?
- Are errors concentrated near terrain transitions, highly impervious zones, or manhole-related regions?
- Can reliability diagnostics identify low-confidence or high-risk warning outputs?
- Can the warning framework be extended from earlier phases to full-resolution or downsampled full-dataset predictions?

This keeps the project ambitious while avoiding unsupported Level 5 claims.

## Full Dataset Modeling Options

### Downsample 500x500 to 128x128

Downsampling to 128x128 is the most conservative first training option. It reduces memory pressure, allows faster iteration, and makes baseline training more feasible. It is appropriate for the first full-dataset baseline after indexing and dataloader smoke tests.

The main limitation is spatial detail loss. Small flood features, narrow flow paths, and localized infrastructure effects may be smoothed. This option is best for establishing an initial full-dataset learning pipeline and reliability diagnostic workflow, not for final high-resolution claims.

### Downsample 500x500 to 256x256

Downsampling to 256x256 preserves more spatial structure while still reducing the cost relative to full 500x500 training. It is a plausible second-stage refinement after a 128x128 baseline works.

The limitation is higher memory and compute demand. It should not be the first required path unless the Phase 46 dataloader feasibility test shows that it is reliable on the available hardware.

### Patch/Tile-Based Training

Patch or tile-based training can preserve local 500x500 detail while keeping memory manageable. Tiles may be extracted from full frames with static geodata channels and rainfall conditioning.

The main risk is loss of global context. Flood response can depend on upstream or broader topographic structure, and naive tiles may produce boundary artifacts. If this option is used, it should include careful tile indexing, overlap handling, and diagnostics for edge effects.

### Multiscale Training

Multiscale training can combine downsampled global context with higher-resolution local patches. This is a strong long-term Level 4+ direction because it can balance global rainfall/topographic context with local spatial detail.

The limitation is implementation complexity. It should follow a working downsample baseline rather than precede it.

### Full 500x500 Training as Later Feasibility Option

Full 500x500 training should remain a later feasibility option only. It may be useful if hardware, batching, and model memory requirements are manageable.

This should not be the default short-term plan. The project should first prove that indexing, dataloading, downsample baselines, and diagnostics work reliably.

## Recommended Technical Route

The recommended route is staged and conservative:

1. Build a full dataset index and lightweight adapter.
2. Run dataloader smoke tests before any training.
3. Start with a downsampled 128x128 full-dataset baseline.
4. Add reliability and physical proxy diagnostics.
5. Extend the warning framework using measured reliability behavior.
6. Consider 256x256, tile, or multiscale refinement only after the baseline path is stable.

This route avoids premature architecture or loss changes. It also prevents training from starting before the dataset structure is reproducibly indexed and verified.

## Phase 45-50 Roadmap

### Phase 45: Full Dataset Indexing and Lightweight Adapter

Create a reproducible index of the available UrbanFlood24 full dataset. The index should record split, group, location, scenario, file paths, array shapes, dtypes, rainfall length, and static geodata availability.

Phase 45 should focus on data discovery and adapter design only. It should not run training.

### Phase 46: Dataloader Smoke Test and Downsample/Tiling Feasibility

Implement and test a lightweight dataloader path using the Phase 45 index. Verify that representative samples can be loaded, normalized or transformed consistently, and batched without shape ambiguity.

Evaluate feasibility for:

- 128x128 downsampling.
- 256x256 downsampling.
- Patch or tile extraction.
- Basic multiscale sample construction.

Phase 46 should use smoke tests only. It should not run full training or seed experiments.

### Phase 47: Full Dataset Downsample Baseline Training

Begin training only after Phase 45 indexing and Phase 46 dataloader smoke tests are complete.

The first recommended baseline is 128x128 downsampled prediction using rainfall and static geodata conditioning. The goal is to establish a working full-dataset modeling baseline, not to claim Level 5 physics.

No SWE residual or PINN loss should be introduced.

### Phase 48: Full Dataset Reliability and Physical Proxy Diagnostics

Add reliability diagnostics and physical proxy checks based only on available arrays.

Candidate analyses include:

- Error by flood intensity.
- Error by location and scenario.
- Error near terrain gradients.
- Error by imperviousness.
- Error near manhole indicator regions.
- Rainfall-response consistency.
- Spatial failure case mapping.
- Warning threshold sensitivity.

These diagnostics should be described as proxy and reliability analyses, not as strict conservation validation.

### Phase 49: Full Dataset Warning Framework Extension

Extend the earlier reliability-aware warning framework to the full UrbanFlood24 dataset setting.

This phase should connect predicted flood maps, reliability diagnostics, and warning thresholds. It may evaluate how warnings behave under different rainfall scenarios, spatial zones, and reliability filters.

The warning framework should be presented as decision support under model uncertainty, not as a fully closed hydrodynamic simulator.

### Phase 50: Optional 256x256 / Tile / Multiscale Refinement

Use Phase 50 for refinement only after the 128x128 baseline and diagnostics are stable.

Possible paths include:

- 256x256 downsample refinement.
- Patch or tile-based high-resolution refinement.
- Multiscale context-plus-tile modeling.
- Limited full 500x500 feasibility tests if hardware permits.

This phase remains Level 4+. It should not introduce unsupported Level 5 or SWE/PINN claims.

## Guardrails

- Phase 44 is a replanning phase only.
- No training is run in Phase 44.
- No seed runs are performed in Phase 44.
- No loss, config, or model architecture is modified in Phase 44.
- No SWE residual is implemented.
- No PINN method is implemented.
- No Level 5 support is claimed.
- Future work must use only the already downloaded UrbanFlood24 full dataset.
- Do not require author clarification as a project path.
- Do not require ICM/MIKE+ exports as a project path.
- Do not claim strict conservation.
- Do not claim full mass conservation.
- Do not claim hydrodynamic closure.
- Future training should begin only after indexing and dataloader smoke tests are complete.

## Success Criteria

Phase 44 is successful if it produces a conservative, usable replan that:

- Freezes near-term Level 5 / SWE / PINN claims.
- Defines the available UrbanFlood24 full dataset as the sole required data source.
- Identifies Level 4+ proxy modeling as the supported research direction.
- Explains why SWE residual losses and strict conservation claims are not supported.
- Establishes a staged Phase 45-50 roadmap.
- Separates dataset indexing and dataloader smoke testing from any future training.
- Provides modeling options without overcommitting to unsupported resolutions or methods.
- Preserves a credible path toward high-resolution reliability-aware warning research.

## Final Conclusion

Phase 44 replans the project around the evidence available after Phase 43 and the new constraint that no further external files or simulator exports will be obtained.

The full UrbanFlood24 dataset supports a strong Level 4+ path: high-resolution proxy flood modeling, reliability diagnostics, and warning framework extension. It does not support Level 5 hydrodynamic closure, SWE residual losses, strict conservation claims, or full mass conservation claims.

The next step should be Phase 45 full dataset indexing and lightweight adapter construction, followed by Phase 46 dataloader smoke tests. Training should begin only after those steps confirm that the available dataset can be loaded and transformed reproducibly.
