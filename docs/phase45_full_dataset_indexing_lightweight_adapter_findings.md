# Phase 45 Full Dataset Indexing and Lightweight Adapter Findings

## 1. Executive Summary

Phase 45 was a no-training data engineering phase for the already downloaded UrbanFlood24 full dataset. Its purpose was to build reproducible indexes and adapter design notes that can support later dataloader smoke tests.

Phase 45 completed the intended indexing work. The dataset root exists, 168 scenarios were indexed, 6 static geodata rows were indexed, and no warnings were recorded. The selected decision is:

```text
indexing_ready_for_dataloader_smoke
```

This decision authorizes only Phase 46 dataloader smoke testing. It does not authorize training.

## 2. Inputs and Outputs

Primary input dataset root:

```text
E:/BaiduNetdiskDownload/urbanflood24/urbanflood24
```

Phase 45 created or uses the following repository artifacts:

- `docs/phase45_full_dataset_indexing_lightweight_adapter_plan.md`
- `scripts/build_phase45_full_dataset_index.py`
- `analysis/phase45_full_dataset_indexing/scenario_index.csv`
- `analysis/phase45_full_dataset_indexing/static_geodata_index.csv`
- `analysis/phase45_full_dataset_indexing/dataset_index_summary.json`
- `analysis/phase45_full_dataset_indexing/dataset_index_summary.md`
- `analysis/phase45_full_dataset_indexing/adapter_design_notes.md`

The index artifacts record metadata and paths only. Phase 45 did not copy dataset files into the repository and did not materialize full arrays in memory.

## 3. Indexed Dataset Coverage

The Phase 45 index confirms that the UrbanFlood24 full dataset has reproducible scenario and static geodata indexes for the current workstation.

Summary coverage:

- `dataset_root_exists = true`
- `scenario_count_total = 168`
- `train scenarios = 120`
- `test scenarios = 48`
- `static_index_rows = 6`
- `warning_count = 0`

Scenario coverage by split:

- `train = 120`
- `test = 48`

Static coverage:

- `complete_500x500 = 6`

## 4. Scenario Index Findings

The scenario index records one row per discovered flood scenario and includes flood, rainfall, static geodata paths, inspected shapes, dtypes, file sizes, scenario type, and notes.

Scenario type counts:

- `design = 108`
- `measured = 60`

Scenario count by split and location:

- `train/location1 = 40`
- `train/location2 = 40`
- `train/location3 = 40`
- `test/location1 = 16`
- `test/location2 = 16`
- `test/location3 = 16`

No missing flood files, rainfall files, or static geodata links were reported in the Phase 45 summary.

## 5. Static Geodata Index Findings

The static geodata index records one row per split and location. It includes paths and metadata for:

- `absolute_DEM.npy`
- `impervious.npy`
- `manhole.npy`

All 6 indexed static rows have `complete_500x500` coverage. This supports Phase 46 smoke testing against the indexed 500 by 500 dynamic flood arrays and static maps.

## 6. Important Shape and Sequence-Length Findings

Phase 45 found two flood sequence shapes:

- `(360, 1, 500, 500) = 153`
- `(480, 1, 500, 500) = 15`

Phase 45 also found two rainfall lengths:

- `180 = 108`
- `360 = 60`

All inspected arrays are recorded as:

- `float64 = 354`

These findings are important because Phase 46 cannot assume a single dynamic sequence length or a single rainfall length. Dataloader smoke tests must explicitly handle flood sequence length variability and rainfall length variability before any later training phase is considered.

## 7. Adapter Design Implications

The lightweight adapter should treat the Phase 45 CSV files as canonical metadata inputs. It should enumerate records, validate required columns, filter records, and lazily open arrays only when a smoke test asks for a sample.

The adapter path should support:

- filtering by `split`, `location`, `scenario_type`, and `rainfall_length`;
- validating flood, rainfall, and static paths before loading sample data;
- memory-mapped array access with controlled slicing;
- representative shape checks for Phase 46;
- candidate downsample or tiling feasibility checks without committing to training.

The adapter should not define normalization, loss behavior, architecture behavior, conservation residuals, or training policy.

## 8. What Phase 45 Enables

Phase 45 enables Phase 46 dataloader smoke tests against the full UrbanFlood24 dataset index.

Specifically, Phase 45 enables:

- reproducible scenario lookup without rescanning the dataset tree;
- reproducible static geodata lookup by split and location;
- split-aware and location-aware sample selection;
- conservative design versus measured scenario filtering;
- metadata-aware handling of flood shapes and rainfall lengths;
- smoke-test planning for lazy loading, downsampling, tiling, and collation.

## 9. What Phase 45 Does Not Authorize

Phase 45 does not authorize model training.

The following were not performed and remain unauthorized by Phase 45:

- training runs;
- seed runs;
- sweeps;
- loss modifications;
- config changes for model behavior;
- model architecture changes;
- SWE residual implementation;
- PINN implementation;
- Level 5 support claims;
- copying dataset files into the repository;
- full-array memory loading.

`training_authorized = false` remains the controlling guardrail.

## 10. Phase 46 Requirements

Phase 46 must remain a dataloader smoke-test phase.

Minimum Phase 46 requirements:

- consume `scenario_index.csv` and `static_geodata_index.csv` without rescanning the full dataset;
- verify required columns and path existence;
- lazily open representative flood, rainfall, and static arrays;
- handle flood shape variability between `(360, 1, 500, 500)` and `(480, 1, 500, 500)`;
- handle rainfall length variability between `180` and `360`;
- test small sample and batch construction for shape compatibility only;
- test candidate 128 by 128 and 256 by 256 downsample or tiling paths if needed;
- avoid training, sweeps, and seed experiments.

Phase 47 training remains blocked until Phase 46 dataloader smoke tests pass.

## 11. Guardrails

Phase 45 guardrails remain active:

- No training was run.
- No seed runs were performed.
- No sweeps were performed.
- No loss, config, or model architecture was modified.
- No SWE residual or PINN was implemented.
- No full arrays were loaded into memory.
- No dataset files were copied into the repository.
- `level4_plus_supported = true`
- `level5_supported = false`
- `training_authorized = false`

This remains a Level 4+ full-dataset route. Level 5 remains unsupported.

## 12. Final Conclusion

Phase 45 successfully produced a reproducible full-dataset scenario index and static geodata index for UrbanFlood24. The current evidence supports the conservative decision `indexing_ready_for_dataloader_smoke`.

The next authorized step is Phase 46 dataloader smoke testing. Training remains unauthorized, and Phase 47 remains blocked until those smoke tests pass.
