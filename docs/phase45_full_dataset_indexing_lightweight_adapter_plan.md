# Phase 45 Full Dataset Indexing and Lightweight Adapter Plan

## Executive Summary

Phase 45 is a no-training data engineering phase for the already downloaded UrbanFlood24 full dataset. Its purpose is to create a reproducible full-dataset index and a lightweight adapter design that can support later dataloader smoke tests without copying the dataset into the repository or loading full arrays into memory.

Phase 45 must not train models, run seed experiments, run sweeps, modify loss functions, modify configuration, modify model architecture, implement SWE residuals, implement PINN components, or claim Level 5 support.

Planned script:

```text
scripts/build_phase45_full_dataset_index.py
```

Optional adapter draft:

```text
data/urbanflood24_full_adapter.py
```

Expected output directory:

```text
analysis/phase45_full_dataset_indexing/
```

Expected conservative decision:

```text
indexing_ready_for_dataloader_smoke
```

## Background from Phase 43-44

Phase 43 inspected the UrbanFlood24 full dataset at:

```text
E:\BaiduNetdiskDownload\urbanflood24\urbanflood24
```

The observed dataset root contains:

- `train`
- `test`

Each split contains:

- `flood`
- `geodata`

Both `flood` and `geodata` contain:

- `location1`
- `location2`
- `location3`

Observed scenario directories contain:

- `flood.npy`
- `rainfall.npy`

Observed geodata files contain:

- `absolute_DEM.npy`
- `impervious.npy`
- `manhole.npy`

Phase 43 recorded:

```text
total_files = 354
total_dirs = 186
sampled_arrays_count = 54
level5_supported = false
level4_plus_supported = true
```

Observed array shapes and dtypes were:

```text
flood.npy shape: (360, 1, 500, 500), float64
rainfall.npy shape: (180,) or (360,), float64
static arrays shape: (500, 500), float64
```

Phase 44 replanned the project around the already downloaded UrbanFlood24 full dataset only. Short-term Level 5 / SWE / PINN claims are frozen. Future work is redirected to high-resolution Level 4+ proxy modeling, reliability diagnostics, and warning framework extension.

## Purpose of Full Dataset Indexing

Full dataset indexing creates a stable, machine-readable bridge between raw UrbanFlood24 files and later dataloader experiments. The index should describe what exists, where it exists, and which shape/dtype assumptions are supported by lightweight metadata inspection.

The Phase 45 index is not a training dataset export. It should not transform, downsample, normalize, cache, duplicate, or package flood arrays. It should record paths and metadata so Phase 46 can run focused dataloader smoke tests against known scenario and geodata records.

The index should support later questions such as:

- Which split, location, and scenario does a sample belong to?
- Does each scenario have both `flood.npy` and `rainfall.npy`?
- Does each scenario have matching static geodata paths for its split and location?
- What are the observed flood and rainfall shapes, dtypes, and rainfall lengths?
- Are any scenarios incomplete or irregular?
- Can a future dataloader construct samples without scanning the dataset tree every run?

## Dataset Path and Safety Rules

UrbanFlood24 full dataset path:

```text
E:\BaiduNetdiskDownload\urbanflood24\urbanflood24
```

The future indexing script should treat this path as an external read-only dataset root.

Safety rules:

- Do not copy the 100GB dataset into the repository.
- Do not write files inside the UrbanFlood24 dataset directory.
- Do not load full arrays into memory.
- Use `numpy.load(..., mmap_mode='r')` for shape and dtype checks only.
- Do not materialize flood, rainfall, or static array values in output artifacts.
- Write only CSV, JSON, and Markdown index artifacts under `analysis/phase45_full_dataset_indexing/`.
- Treat all outputs as indexing and adapter preparation, not training data generation.

## Planned Index Files

Phase 45 should produce:

- `analysis/phase45_full_dataset_indexing/scenario_index.csv`
- `analysis/phase45_full_dataset_indexing/static_geodata_index.csv`
- `analysis/phase45_full_dataset_indexing/dataset_index_summary.json`
- `analysis/phase45_full_dataset_indexing/dataset_index_summary.md`
- `analysis/phase45_full_dataset_indexing/adapter_design_notes.md`

The CSV files should be the canonical machine-readable outputs for Phase 46. The JSON summary should preserve counts, warnings, decisions, and guardrail status. The Markdown summary should provide a compact human-readable evidence report. The adapter notes should define the intended lightweight adapter contract without requiring model or training changes.

## Scenario Index Design

`scenario_index.csv` should contain one row per scenario directory under:

```text
<dataset_root>/<split>/flood/<location>/<scenario>/
```

Required columns:

- `split`
- `location`
- `scenario`
- `scenario_type`
- `flood_path`
- `rainfall_path`
- `flood_shape`
- `flood_dtype`
- `rainfall_shape`
- `rainfall_dtype`
- `rainfall_length`
- `static_dem_path`
- `static_impervious_path`
- `static_manhole_path`
- `flood_file_size_bytes`
- `rainfall_file_size_bytes`
- `notes`

`scenario_type` should be conservative and filename-derived only. A proposed rule is:

- `design` for return-period/probability/duration-style scenario names such as `r100y_p0.1_d3h`.
- `measured` for event/intensity-style names such as `G1135_intensity_117`.
- If a name does not match either pattern, keep the row and record a warning in `notes`.

Path columns should store absolute paths or consistently resolved dataset-root-relative paths. The choice should be explicit in `dataset_index_summary.json` and `adapter_design_notes.md`. For early reproducibility on the current workstation, absolute paths are acceptable, but the adapter should allow a configurable dataset root so the index can be relocated later.

## Static Geodata Index Design

`static_geodata_index.csv` should contain one row per split and location under:

```text
<dataset_root>/<split>/geodata/<location>/
```

Required columns:

- `split`
- `location`
- `absolute_dem_path`
- `impervious_path`
- `manhole_path`
- `dem_shape`
- `impervious_shape`
- `manhole_shape`
- `dem_dtype`
- `impervious_dtype`
- `manhole_dtype`
- `dem_file_size_bytes`
- `impervious_file_size_bytes`
- `manhole_file_size_bytes`
- `static_coverage_status`

`static_coverage_status` should summarize whether all expected static files exist and whether their inspected shapes are compatible with the observed flood spatial shape. Candidate values:

- `complete_500x500`
- `complete_with_warnings`
- `incomplete_missing_files`
- `incomplete_shape_mismatch`
- `inspection_error`

The script should preserve incomplete rows rather than silently dropping them, because missing static coverage is important for later dataloader behavior.

## Lightweight Adapter Design

The optional adapter draft should be a thin data access layer over the Phase 45 indexes. It should not implement model-specific logic or training behavior.

The adapter should be designed to:

- read `scenario_index.csv` and `static_geodata_index.csv`;
- validate required columns;
- filter by split, location, scenario type, or rainfall length;
- expose scenario records with paths to flood, rainfall, and static geodata files;
- lazily open arrays only when a caller explicitly requests sample data;
- use memory mapping or controlled slicing for heavy arrays;
- provide enough metadata for Phase 46 dataloader smoke tests;
- avoid assumptions about normalization, downsampling, tiling, batching, or loss functions.

The adapter should not:

- train a model;
- import or modify model architecture;
- import or modify loss code;
- create tensors unless Phase 46 explicitly requires a smoke-test loader path;
- cache full arrays in memory;
- write transformed training samples to disk.

The initial adapter contract can be limited to record enumeration and safe lazy access. Phase 46 can extend it only after smoke-test requirements are finalized.

## Shape / dtype Inspection Rules

The future script should inspect `.npy` metadata with:

```python
numpy.load(path, mmap_mode="r")
```

Inspection should record:

- array shape;
- dtype;
- file size in bytes;
- any exception raised during metadata inspection.

Inspection should not compute array statistics such as min, max, mean, percentiles, nonzero counts, or histograms in Phase 45. Those require reading array values and belong in later diagnostic phases only if explicitly planned.

Shape and dtype values should be serialized consistently:

- shapes as stable strings such as `(360, 1, 500, 500)` or JSON arrays in the summary;
- dtypes as strings such as `float64`;
- rainfall length as the first dimension for one-dimensional rainfall arrays, or `unknown` with a warning if shape is unexpected.

## Future Dataloader Requirements

Phase 46 dataloader smoke tests should be able to consume the Phase 45 outputs without rescanning the full dataset. The dataloader should be able to:

- select train or test scenario records;
- verify that flood, rainfall, and static paths exist before loading;
- open representative samples lazily;
- confirm expected dynamic/static spatial compatibility;
- handle rainfall length variability between 180 and 360;
- test candidate downsample paths such as 128x128 and 256x256;
- test whether patch or tile sampling is feasible without committing to a training run;
- produce small batches for shape verification only.

Phase 46 should remain a smoke-test phase until data access, transformations, and batching are confirmed. Training should wait for Phase 47.

## Guardrails

Phase 45 guardrails:

- No model training.
- No `seed42`, `seed123`, or `seed202` runs.
- No sweeps.
- No loss changes.
- No config changes for model behavior.
- No model architecture changes.
- No SWE residual implementation.
- No PINN implementation.
- No Level 5 support claim.
- No strict conservation claim.
- No full mass conservation claim.
- No hydrodynamic closure claim.
- No copying the full dataset into the repository.
- No full-array memory loads.
- No output outside `analysis/phase45_full_dataset_indexing/` except the planned script, optional adapter draft, and this planning document.

Decision candidates:

- `indexing_ready_for_dataloader_smoke`
- `indexing_incomplete_dataset_path_issue`
- `indexing_complete_with_warnings`

Expected conservative decision:

```text
indexing_ready_for_dataloader_smoke
```

## Success Criteria

Phase 45 is successful if:

- `scripts/build_phase45_full_dataset_index.py` is planned to index the full dataset without training or full-array loading;
- `scenario_index.csv` records all discovered scenario records with flood/rainfall paths, shapes, dtypes, rainfall length, static geodata paths, file sizes, scenario type, and notes;
- `static_geodata_index.csv` records expected geodata coverage for each split and location;
- `dataset_index_summary.json` records dataset root, output paths, counts, warning counts, guardrail status, and selected decision;
- `dataset_index_summary.md` summarizes the evidence in human-readable form;
- `adapter_design_notes.md` defines a lightweight adapter contract for Phase 46;
- missing files, shape irregularities, dtype irregularities, or scenario-name uncertainty are recorded as warnings rather than hidden;
- the final decision remains conservative and does not imply training authorization beyond future smoke tests.

## Final Conclusion

Phase 45 prepares a reproducible full-dataset index and lightweight adapter design for later dataloader smoke testing. It does not train, does not modify the model, and does not claim Level 5 support.
