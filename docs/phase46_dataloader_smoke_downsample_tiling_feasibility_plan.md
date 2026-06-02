# Phase 46 Dataloader Smoke, Downsample, and Tiling Feasibility Plan

## Executive Summary

Phase 46 is a no-training dataloader smoke test and downsample/tiling feasibility phase for the UrbanFlood24 full dataset. It consumes the Phase 45 index artifacts, verifies that representative dynamic rainfall/flood arrays and static geodata arrays can be opened lazily, and checks whether small controlled samples can be downsampled, tiled, and batched for shape verification only.

Phase 46 does not authorize model training by itself. It prepares the project for Phase 47 full dataset downsample baseline training only if the smoke tests pass, memory remains controlled, and the results are reviewed.

Planned script:

```text
scripts/smoke_phase46_full_dataloader.py
```

Optional lightweight dataset module:

```text
data/urbanflood24_full_dataset.py
```

Expected output directory:

```text
analysis/phase46_dataloader_smoke_downsample_tiling/
```

Expected conservative decision:

```text
dataloader_smoke_ready_for_downsample_baseline
```

This decision is valid only if lazy reads, downsample tests, tile tests, and very small batch shape checks pass without memory issues.

## Background from Phase 44-45

Phase 44 replanned the project around the already downloaded UrbanFlood24 full dataset. It froze short-term Level 5, SWE, and PINN claims because the available files do not expose the hydrodynamic state and metadata required for strict shallow-water residuals, conservation claims, or full hydrodynamic closure.

Phase 45 completed no-training full dataset indexing and lightweight adapter preparation. Its selected decision was:

```text
selected_decision = indexing_ready_for_dataloader_smoke
training_authorized = false
level4_plus_supported = true
level5_supported = false
```

Phase 45 indexed:

```text
scenario_count_total = 168
train scenarios = 120
test scenarios = 48
static_index_rows = 6
warning_count = 0
```

Important indexed evidence from Phase 45:

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

static coverage:
complete_500x500 = 6

dtype:
float64 = 354
```

This evidence supports a controlled dataloader smoke phase, but not training, SWE residual implementation, PINN implementation, or Level 5 claims.

## Purpose of Dataloader Smoke Testing

The purpose of Phase 46 is to prove that the indexed UrbanFlood24 full dataset can be accessed through a practical dataloader path before any training is attempted.

The smoke test should answer:

- Can the Phase 45 scenario and static geodata indexes be loaded and validated?
- Can representative `flood.npy`, `rainfall.npy`, and static arrays be opened lazily?
- Can the dataloader handle flood sequence lengths of 360 and 480?
- Can the dataloader handle rainfall lengths of 180 and 360?
- Can representative arrays be downsampled to 128x128 without materializing the full dataset?
- Is 256x256 downsampling feasible under controlled memory use?
- Can simple tile or patch extraction work from 500x500 arrays?
- Can a very small smoke batch be assembled for shape verification only?
- Does memory remain controlled throughout?

This phase should convert Phase 45 indexing readiness into dataloader readiness. It should not create training datasets or perform model optimization.

## Input Index Files

Phase 46 must consume the Phase 45 canonical index files:

```text
analysis/phase45_full_dataset_indexing/scenario_index.csv
analysis/phase45_full_dataset_indexing/static_geodata_index.csv
```

The smoke script should validate the presence and required columns of both files before any array access.

Required scenario index behavior:

- Load all 168 scenario rows.
- Preserve `split`, `location`, `scenario`, `scenario_type`, path, shape, dtype, and rainfall-length metadata.
- Confirm train/test counts remain 120 and 48.
- Confirm flood shapes include both `(360, 1, 500, 500)` and `(480, 1, 500, 500)`.
- Confirm rainfall lengths include both 180 and 360.
- Fail or warn explicitly if required columns are missing, paths are invalid, shapes are malformed, or counts no longer match Phase 45 evidence.

Required static geodata index behavior:

- Load all 6 static geodata rows.
- Confirm coverage status remains `complete_500x500`.
- Confirm static shapes remain `(500, 500)`.
- Confirm required static files exist for each split/location pair.

## Smoke Test Scope

Phase 46 should use a small representative subset selected from the Phase 45 indexes. The subset should include:

- At least one train scenario.
- At least one test scenario.
- At least one design scenario.
- At least one measured scenario.
- At least one scenario with rainfall length 180.
- At least one scenario with rainfall length 360.
- At least one scenario with flood sequence length 360.
- At least one scenario with flood sequence length 480, if available.
- Static geodata from multiple locations where practical.

The script should avoid broad scans that open every large array. Index-level validation may inspect all rows, but array-level smoke checks should remain representative and bounded.

## Downsample Feasibility Tests

Phase 46 should test downsampling as a feasibility check only. It should not write transformed arrays to disk.

Required 128x128 checks:

- Open representative flood arrays with `numpy.load(..., mmap_mode='r')`.
- Slice only a small number of timesteps for smoke verification.
- Downsample representative flood frames from 500x500 to 128x128.
- Downsample static geodata arrays from 500x500 to 128x128.
- Record input and output shapes.
- Record method used, such as area resize, interpolation, pooling, or a simple implementation available in the environment.
- Confirm memory remains controlled.

Required 256x256 checks:

- Attempt 256x256 downsampling only if memory remains safe after 128x128 checks.
- Use the same representative bounded-slice approach.
- Record whether 256x256 is feasible, feasible with warnings, or skipped for memory safety.
- Do not treat 256x256 success as required for Phase 47 if the conservative 128x128 path is ready.

The expected downsample result is not a quality assessment. It is a shape, access, and memory feasibility check.

## Tiling / Patch Feasibility Tests

Phase 46 should test simple tile or patch extraction from representative 500x500 arrays.

Candidate tile settings:

- 128x128 tiles.
- 256x256 tiles.
- Optional overlap only if implemented simply and safely.

Required tile checks:

- Extract a small number of spatial patches from representative flood slices.
- Extract matching static geodata patches.
- Confirm tile shape consistency across flood and static arrays.
- Confirm behavior near boundaries, such as crop, pad, or skip.
- Record tile origin coordinates and output shapes.
- Avoid enumerating or writing all possible tiles.

Tile feasibility should be evaluated as a future modeling option, not as an immediate training commitment.

## Batch Assembly Smoke Test

Phase 46 should assemble a very small smoke batch for shape verification only.

The batch test should:

- Use no model.
- Use no optimizer.
- Use no loss function.
- Avoid random seed experiment framing.
- Select a tiny fixed number of representative samples.
- Include rainfall, static geodata, and flood target slices in a consistent sample structure.
- Handle variable rainfall lengths 180 and 360 through a documented smoke-time strategy.
- Handle variable flood sequence lengths 360 and 480 through a documented smoke-time strategy.
- Verify resulting tensor or array shapes.
- Record batch dimensions, channel counts, sequence handling, and any padding/truncation/slicing rules.

Acceptable smoke-time strategies include bounded timestep slicing, padding to a local batch maximum, truncating to a fixed smoke horizon, or returning variable-length metadata rather than stacking variable-length sequences directly. The selected strategy should be reported clearly and should not be treated as final training design.

## Memory and Safety Rules

Phase 46 must obey the following safety rules:

- Do not train models.
- Do not run `seed42`, `seed123`, or `seed202`.
- Do not run sweeps.
- Do not modify loss functions.
- Do not modify configuration.
- Do not modify model architecture.
- Do not implement SWE residuals.
- Do not implement PINN components.
- Do not claim Level 5 support.
- Do not copy the 100GB dataset into the repository.
- Do not materialize full arrays into memory.
- Do not write transformed training datasets to disk.
- Do not write files inside the UrbanFlood24 dataset directory.
- Use lazy or memory-mapped reads for large `.npy` arrays.
- Use bounded slices for representative smoke checks.
- Write only compact JSON, Markdown, and CSV evidence files under the Phase 46 analysis directory.

The script should record memory safety notes even when checks pass. If memory measurements are available, they should be reported. If direct memory measurement is not available, the script should report bounded-read assumptions and maximum slice sizes used.

## Planned Smoke Test Script

Primary script:

```text
scripts/smoke_phase46_full_dataloader.py
```

The planned script should:

- Read `scenario_index.csv`.
- Read `static_geodata_index.csv`.
- Validate required columns, row counts, shape metadata, dtype metadata, path existence, and static coverage.
- Select representative scenarios covering split, scenario type, rainfall length, and flood sequence length diversity.
- Lazily open representative flood, rainfall, and static arrays.
- Run bounded shape checks.
- Run 128x128 downsample checks.
- Run 256x256 downsample checks only if memory is safe.
- Run simple tile/patch checks.
- Assemble a tiny smoke batch for shape verification.
- Write all expected Phase 46 outputs.
- Emit a conservative selected decision.

Optional dataset module:

```text
data/urbanflood24_full_dataset.py
```

The optional module should stay lightweight. It may provide index loading, record validation, lazy array opening, sample construction, downsample helpers, tile helpers, and shape-only batch collation. It must not include model, training, loss, SWE, or PINN logic.

## Expected Outputs

Phase 46 should write outputs under:

```text
analysis/phase46_dataloader_smoke_downsample_tiling/
```

Required outputs:

```text
dataloader_smoke_summary.json
dataloader_smoke_summary.md
sample_shape_checks.csv
downsample_feasibility_checks.csv
tile_feasibility_checks.csv
batch_smoke_checks.csv
memory_safety_notes.md
```

`dataloader_smoke_summary.json` should include:

- Input index paths.
- Scenario and static row counts.
- Validation status.
- Representative sample selection criteria.
- Observed flood shapes.
- Observed rainfall lengths.
- Static coverage status.
- Downsample check status.
- Tile check status.
- Batch smoke check status.
- Memory safety status.
- Guardrail status.
- Warning count.
- Selected decision.
- Training authorization status.
- Level 4+ and Level 5 support flags.

`dataloader_smoke_summary.md` should provide a concise human-readable evidence summary.

The CSV outputs should preserve machine-readable checks without storing large array values.

## Decision Criteria

Decision candidates:

```text
dataloader_smoke_ready_for_downsample_baseline
dataloader_smoke_passed_with_warnings
dataloader_smoke_blocked_by_shape_or_memory_issue
dataloader_smoke_blocked_by_index_issue
```

Use `dataloader_smoke_ready_for_downsample_baseline` only if:

- Both Phase 45 index files load successfully.
- Required columns and row counts validate.
- Static geodata coverage validates.
- Representative flood, rainfall, and static arrays open lazily.
- Flood sequence lengths 360 and 480 are handled or explicitly covered by representative checks.
- Rainfall lengths 180 and 360 are handled.
- 128x128 downsampling passes.
- 256x256 downsampling is either safely feasible or explicitly skipped without blocking the conservative 128x128 route.
- Simple tile/patch extraction passes.
- A tiny smoke batch can be assembled for shape verification.
- No memory safety issue occurs.
- No training, seed run, sweep, loss/config/model change, SWE residual, PINN component, or Level 5 claim is introduced.

Use `dataloader_smoke_passed_with_warnings` if the main dataloader path works but there are non-blocking warnings that should be reviewed before Phase 47.

Use `dataloader_smoke_blocked_by_shape_or_memory_issue` if shape variability, downsampling, tiling, batching, or memory behavior blocks a safe dataloader path.

Use `dataloader_smoke_blocked_by_index_issue` if Phase 45 index files are missing, invalid, inconsistent, or insufficient for representative dataloader checks.

## Guardrails

Phase 46 guardrails are:

- `training_authorized = false` during Phase 46 execution.
- `level4_plus_supported = true` remains supported only as a proxy modeling direction.
- `level5_supported = false` remains unchanged.
- No SWE residuals are implemented.
- No PINN components are implemented.
- No model architecture is changed.
- No losses or training configs are changed.
- No seed runs are performed.
- No sweeps are performed.
- No full dataset arrays are materialized in memory.
- No transformed training datasets are written to disk.

Any Phase 46 report should explicitly state that successful dataloader smoke tests are prerequisites for Phase 47, not proof of model performance.

## Success Criteria

Phase 46 succeeds if it produces the required output files and records:

- Valid loaded Phase 45 scenario index.
- Valid loaded Phase 45 static geodata index.
- Representative lazy array access for flood, rainfall, and static geodata.
- Successful handling of variable flood sequence lengths 360 and 480.
- Successful handling of variable rainfall lengths 180 and 360.
- Successful 128x128 downsample feasibility.
- Safe 256x256 downsample feasibility result or justified memory-safe skip.
- Successful simple tile/patch extraction.
- Successful tiny batch assembly for shape verification only.
- Controlled memory behavior.
- Zero guardrail violations.
- Conservative selected decision suitable for review.

The preferred selected decision is:

```text
dataloader_smoke_ready_for_downsample_baseline
```

This decision should be selected only when the smoke evidence supports moving to a reviewed Phase 47 downsample baseline plan.

## Final Conclusion

Phase 46 is a no-training dataloader smoke test phase. It prepares the project for Phase 47 full dataset downsample baseline training only if data loading, downsampling, tiling, and small-batch shape checks pass. It does not authorize training by itself unless the smoke tests succeed and are reviewed.
