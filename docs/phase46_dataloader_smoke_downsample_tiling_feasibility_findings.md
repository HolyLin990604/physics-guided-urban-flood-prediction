# Phase 46 Dataloader Smoke, Downsample, and Tiling Feasibility Findings

## Executive Summary

Phase 46 completed a no-training dataloader smoke test for the UrbanFlood24 full-dataset route. The phase validated that the Phase 45 scenario and static geodata indexes can be loaded, that representative flood, rainfall, and static arrays can be accessed through bounded lazy reads, and that small controlled downsample, tile, and batch shape checks are feasible.

The selected decision is:

```text
selected_decision = dataloader_smoke_ready_for_downsample_baseline
```

This finding supports planning a controlled Phase 47 full dataset downsample baseline, likely beginning with a 128x128 route. It does not by itself authorize uncontrolled training or any Level 5 claim.

## Inputs and Outputs

Phase 46 consumed the Phase 45 index artifacts:

```text
analysis/phase45_full_dataset_indexing/scenario_index.csv
analysis/phase45_full_dataset_indexing/static_geodata_index.csv
```

The Phase 46 smoke script was:

```text
scripts/smoke_phase46_full_dataloader.py
```

The Phase 46 evidence files are:

```text
analysis/phase46_dataloader_smoke_downsample_tiling/dataloader_smoke_summary.json
analysis/phase46_dataloader_smoke_downsample_tiling/dataloader_smoke_summary.md
analysis/phase46_dataloader_smoke_downsample_tiling/sample_shape_checks.csv
analysis/phase46_dataloader_smoke_downsample_tiling/downsample_feasibility_checks.csv
analysis/phase46_dataloader_smoke_downsample_tiling/tile_feasibility_checks.csv
analysis/phase46_dataloader_smoke_downsample_tiling/batch_smoke_checks.csv
analysis/phase46_dataloader_smoke_downsample_tiling/memory_safety_notes.md
```

No transformed training datasets were written to disk.

## Index Validation

The scenario index loaded successfully:

```text
scenario_index_loaded = true
scenario_count_total = 168
train scenarios = 120
test scenarios = 48
```

The static geodata index loaded successfully:

```text
static_index_loaded = true
static_index_rows = 6
static coverage = complete_500x500
```

The Phase 46 result preserved the expected Phase 45 dataset structure:

```text
scenario type counts:
design = 108
measured = 60

rainfall length counts:
180 = 108
360 = 60

flood shape counts:
(360, 1, 500, 500) = 153
(480, 1, 500, 500) = 15
```

No index-level warning was recorded.

## Representative Sample Coverage

Phase 46 selected 11 representative samples:

```text
representative_samples_count = 11
```

The representative set covered:

- train and test splits.
- location1, location2, and location3.
- design and measured scenarios.
- flood sequence length 360 and 480.
- rainfall length 180 and 360.
- static geodata with 500x500 coverage.

The sample shape checks passed:

```text
sample_shape_checks_passed = true
```

This coverage is sufficient for a dataloader smoke test. It is not a complete training-data audit and should not be treated as model-performance evidence.

## Lazy / mmap Read Checks

The smoke checks used lazy memory-mapped array access:

```text
numpy.load(..., mmap_mode="r")
```

This was applied to flood, rainfall, and static `.npy` access. Flood reads were bounded to a smoke window of 2 temporal frames per representative sample:

```text
smoke_window = 2
```

No full flood sequences were materialized in memory. The lazy-read result supports practical dataloader planning, but future training still needs explicit fixed-window sampling and rainfall-alignment rules.

## Downsample Feasibility Findings

The 128x128 downsample feasibility checks passed:

```text
downsample_128_passed = true
```

The 256x256 downsample feasibility checks also passed:

```text
downsample_256_passed = true
```

The checks downsampled bounded flood windows from `(2, 1, 500, 500)` to `(2, 1, 128, 128)` and `(2, 1, 256, 256)`. Static stacks were checked from `(3, 500, 500)` to `(3, 128, 128)` and `(3, 256, 256)`.

The recorded method was `torch.nn.functional.interpolate_bilinear`, with small in-memory slices only. This is a shape, access, and memory feasibility result. It is not a quality comparison between 128x128 and 256x256, and it does not select a final training resolution by itself.

## Tile / Patch Feasibility Findings

Tile and patch checks passed:

```text
tile_checks_passed = true
```

The smoke test extracted deterministic 256x256 patches from representative 500x500 flood windows and matching static stacks. Checked origins included:

```text
(0, 0)
(122, 122)
(244, 244)
```

The recorded tile shapes were:

```text
flood_tile_shape = (2, 1, 256, 256)
static_tile_shape = (3, 256, 256)
```

This supports tile or patch extraction as a future modeling option. It does not require Phase 47 to use tiling, and it does not authorize writing tile datasets to disk.

## Batch Smoke Findings

The batch smoke check passed:

```text
batch_smoke_passed = true
```

The checked batch used:

```text
batch_size = 2
smoke_window = 2
downsample_size = 128
```

The recorded batch shapes were:

```text
flood_window_batch_shape = (2, 2, 1, 128, 128)
static_stack_batch_shape = (2, 3, 128, 128)
rainfall_summary_batch_shape = (2, 3)
```

This confirms that a tiny shape-only batch can be assembled. No model forward pass, optimizer step, loss computation, seed run, or training command was executed.

## Memory Safety Findings

Memory safety passed:

```text
memory_safe = true
```

The evidence supporting this conclusion is conservative:

- Large `.npy` files were opened with memory mapping.
- Flood reads were bounded to the first 2 temporal frames per representative sample.
- Full flood sequences were not materialized.
- Downsample checks used bounded slices only.
- Tile checks stayed in memory and wrote only compact metadata.
- No transformed training datasets were written to disk.
- No files were written inside the UrbanFlood24 dataset directory.

This result indicates that the smoke workflow stayed within the intended memory boundary. It does not prove that every future training configuration is memory safe.

## What Phase 46 Enables

Phase 46 makes it reasonable to plan Phase 47 full dataset downsample baseline training under controlled conditions.

The strongest supported next step is a separate Phase 47 plan that starts with a 128x128 downsample baseline before any training command. A 256x256 route appears feasible from this smoke evidence, but 128x128 remains the more conservative first baseline.

Phase 46 also supports keeping a Level 4+ full-dataset route open:

```text
level4_plus_supported = true
```

## What Phase 46 Does Not Authorize

Phase 46 does not authorize training:

```text
training_authorized = false
```

Phase 46 did not perform:

- model training.
- seed runs.
- sweeps.
- model forward passes.
- optimizer steps.
- loss computation.
- loss function changes.
- config changes.
- model architecture changes.
- SWE residual implementation.
- PINN implementation.
- Level 5 validation.
- full-array materialization.
- transformed training dataset writing.

Successful smoke tests are prerequisites for controlled Phase 47 planning. They are not model-performance evidence and are not automatic permission to run uncontrolled training.

## Phase 47 Readiness Boundary

Phase 46 establishes a readiness boundary for planning, not execution. The evidence supports preparing a Phase 47 downsample baseline plan that specifies:

- the selected first resolution, likely 128x128.
- fixed-window flood sampling rules.
- rainfall alignment or summarization rules for lengths 180 and 360.
- static feature handling.
- batch size and memory limits.
- train/test split handling.
- explicit training authorization criteria.
- output and logging boundaries.

Level 5 remains unsupported:

```text
level5_supported = false
```

The current route remains a Level 4+ full-dataset proxy modeling route, not a strict hydrodynamic closure or SWE/PINN route.

## Guardrails

The following guardrails remain active:

- `training_authorized = false`.
- `level4_plus_supported = true` only for the Level 4+ full-dataset route.
- `level5_supported = false`.
- Do not run training without a reviewed Phase 47 plan.
- Do not run seed42, seed123, seed202, or any other seed experiment as part of Phase 46.
- Do not run sweeps.
- Do not modify losses, configs, or model architecture under Phase 46.
- Do not implement SWE residuals or PINN components under Phase 46.
- Do not claim Level 5 support.
- Do not materialize full flood arrays in memory.
- Do not write transformed training datasets to disk.
- Do not write derived data into the UrbanFlood24 dataset directory.

These guardrails should carry into Phase 47 until a controlled baseline plan explicitly replaces them.

## Final Conclusion

Phase 46 successfully completed no-training dataloader smoke testing and downsample/tiling feasibility checks. The scenario and static indexes loaded, 11 representative samples covered the required split/location/type/shape/rainfall diversity, bounded lazy reads worked, 128x128 and 256x256 downsample checks passed, tile checks passed, a tiny 128x128 batch smoke check passed, and memory safety remained controlled.

The conservative conclusion is:

```text
selected_decision = dataloader_smoke_ready_for_downsample_baseline
training_authorized = false
level4_plus_supported = true
level5_supported = false
```

Phase 46 makes Phase 47 downsample baseline planning reasonable, especially for a 128x128 first baseline. It does not run or automatically authorize training, seed experiments, sweeps, SWE residuals, PINN components, architecture changes, or Level 5 claims.
