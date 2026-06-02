# Phase 45 Lightweight Adapter Design Notes

These notes define the intended Phase 46 data access contract. Phase 45 produced indexes only and did not train models.

## Inputs

- `scenario_index.csv` is the canonical scenario table. Phase 46 should read it once, validate required columns, and use each row as a lazy record pointing to flood, rainfall, and static geodata paths.
- `static_geodata_index.csv` is the canonical static coverage table. Phase 46 should join it by `split` and `location` or use the static path columns already copied into each scenario row.
- Paths are stored as `absolute_forward_slash` for reproducibility on this workstation. A future adapter should allow a configurable dataset root so indexes can be relocated without rescanning.

## Lazy Loading Contract

- Do not load full arrays during adapter initialization.
- Open `flood.npy`, `rainfall.npy`, `absolute_DEM.npy`, `impervious.npy`, and `manhole.npy` only when a caller requests a sample or metadata check.
- Use `numpy.load(path, mmap_mode="r")` for heavy arrays and slice only the timesteps or spatial windows needed for a smoke test.
- Do not compute statistics, normalization constants, histograms, conservation residuals, or derived physics fields in the adapter.

## Filtering Contract

- Support filtering by `split`, `location`, `scenario_type`, and `rainfall_length` before any array is opened.
- Preserve both `design` and `measured` scenario types; treat `unknown` rows as opt-in records for diagnostics.
- Require valid flood/rainfall/static paths before a Phase 46 smoke-test sample is materialized.

## Future Downsample And Tiling Checks

- Phase 46 may test read-time downsample candidates at `128x128` and `256x256` for shape feasibility only.
- Tile or multiscale sampling can be explored by slicing mmap arrays into spatial windows, but Phase 46 should first verify boundary handling, static map alignment, rainfall length variability, and batch collation.
- Any downsample, tile, or multiscale path should remain a smoke-test data access check until a later phase explicitly authorizes training.

## Guardrails

- Phase 45 performed no training.
- Phase 45 did not run `seed42`, `seed123`, `seed202`, or sweeps.
- Phase 45 did not modify loss functions, configs, model architecture, SWE residuals, or PINN components.
- Phase 45 makes no Level 5, SWE, PINN, strict conservation, or hydrodynamic closure claim.
- `level5_supported` remains `false` and `training_authorized` remains `false`.