# Phase 47 Controlled Full Dataset Downsample Baseline Plan

## Executive Summary

Phase 47 is a planning and authorization-boundary phase for the first controlled full UrbanFlood24 dataset downsample baseline training. It does not run training, does not start seed42, does not create training outputs, and does not authorize open-ended experimentation.

The expected conservative decision is:

```text
phase47_128_downsample_training_plan_ready
```

This decision authorizes only the next implementation step for one controlled 128x128 full-dataset downsample baseline, using the existing Level 4+ model family as much as possible. It does not authorize 256x256 training, tile or multiscale training, full 500x500 training, SWE residuals, PINN components, Level 5 claims, seed sweeps, seed123/seed202 expansion, proxy-loss redesign, or uncontrolled hyperparameter search.

Recommended future training route:

```text
resolution = 128x128 downsample
dataset = UrbanFlood24 full indexed scenarios from Phase 45
split = existing train/test split from scenario_index.csv
seed = seed42 only
pilot_epochs = 5-10
training_claim_level = Level 4+
training_authorized_now = false
implementation_authorized_next = bounded 128x128 baseline only
```

## Background from Phase 44-46

Phase 44 replanned the project around the already downloaded UrbanFlood24 full dataset only. It froze short-term Level 5, SWE, and PINN claims because the available dataset files do not expose the full hydrodynamic state, boundary metadata, solver controls, or conservation diagnostics required for strict shallow-water residuals, full mass conservation claims, or hydrodynamic closure.

Phase 45 completed full dataset indexing and lightweight adapter preparation. Its result was:

```text
scenario_count_total = 168
train scenarios = 120
test scenarios = 48
static_index_rows = 6
selected_decision = indexing_ready_for_dataloader_smoke
training_authorized = false
```

Phase 46 completed no-training dataloader smoke, downsample, and tiling feasibility checks. Its result was:

```text
scenario_index_loaded = true
static_index_loaded = true
representative_samples_count = 11
downsample_128_passed = true
downsample_256_passed = true
tile_checks_passed = true
batch_smoke_passed = true
memory_safe = true
selected_decision = dataloader_smoke_ready_for_downsample_baseline
training_authorized = false
level4_plus_supported = true
level5_supported = false
```

Together, Phases 44-46 support planning a first full-dataset downsample training baseline. They do not support immediate uncontrolled training or revived Level 5/SWE/PINN claims.

## Why Phase 47 Can Be Planned Now

Phase 47 can be planned because the project now has enough non-training evidence to define a narrow training boundary:

- The full UrbanFlood24 scenario index exists and records the train/test split.
- Static feature indexing exists for the relevant geodata arrays.
- Representative flood and rainfall arrays can be opened.
- 128x128 and 256x256 downsample checks passed in Phase 46.
- Batch smoke checks passed without observed memory risk.
- The project has a reviewed decision that Level 4+ is currently supportable and Level 5 is not.

The planning phase is necessary because passing dataloader smoke checks is not the same as authorizing training. Phase 47 defines the exact implementation and training boundary before any training command is run.

## Training Scope and Authorization Boundary

Phase 47 authorizes planning for exactly one future controlled baseline:

```text
allowed_training_family = full UrbanFlood24 downsample baseline
allowed_resolution = 128x128
allowed_seed = seed42 only
allowed_epoch_range = 5-10 pilot epochs initially
allowed_claim_level = Level 4+
allowed_dataset = Phase 45 indexed UrbanFlood24 full dataset
```

The first training should use the existing Level 4+ model family as much as possible. If adapter compatibility requires small plumbing changes, those changes must be documented as adapter plumbing rather than model redesign.

Not authorized:

- SWE residuals.
- PINN components.
- Level 5 claims.
- New proxy-loss redesign.
- Seed sweeps.
- seed123 or seed202 expansion.
- 256x256 baseline training.
- Tile or multiscale training.
- Full 500x500 training.
- Uncontrolled hyperparameter search.
- Rewriting the model architecture unless unavoidable for adapter compatibility.
- Writing transformed training datasets to disk.
- Copying the approximately 100GB dataset into the repository.

This document does not authorize running training in the planning commit. It authorizes only a bounded implementation step that can later run the reviewed 128x128 pilot.

## Recommended First Baseline: 128x128 Downsample

The recommended first baseline is a 128x128 downsample model because it is the lowest-risk full-dataset training route that is already supported by Phase 46 feasibility checks.

Reasons to start at 128x128:

- It minimizes memory pressure relative to 256x256 and 500x500.
- It keeps data movement smaller while exercising all indexed train/test scenarios.
- It allows the project to validate rainfall alignment, static feature integration, target construction, batching, loss computation, and evaluation before scaling resolution.
- It preserves a conservative Level 4+ framing instead of reintroducing unsupported Level 5/SWE/PINN claims.

The 256x256, tile, multiscale, and full 500x500 routes remain deferred until the 128x128 baseline demonstrates viable training behavior and the artifacts are reviewed.

## Dataset and Index Inputs

The future implementation should consume the Phase 45 index artifacts rather than rediscovering the dataset ad hoc. The expected inputs are:

```text
analysis/phase45_full_dataset_indexing/scenario_index.csv
analysis/phase45_full_dataset_indexing/static_index.csv
```

The scenario split must come from `scenario_index.csv`:

```text
train scenarios = 120
test scenarios = 48
```

The implementation should lazily read:

```text
flood.npy
rainfall.npy
absolute_DEM.npy
impervious.npy
manhole.npy
```

It must not write transformed training datasets to disk. Downsampling should happen in the dataloader or in-memory preprocessing path for each batch/sample.

## Sampling Strategy

The first baseline should use a simple fixed-window supervised sampling strategy.

Recommended dynamic design:

```text
input = short fixed flood history window sampled from flood.npy
target = future flood-depth/downsampled flood window
```

The implementation should select history and forecast window lengths conservatively, using existing model expectations where possible. The sampling policy should:

- Respect each scenario's available flood sequence length.
- Avoid indexing beyond the scenario sequence.
- Use train scenarios only for optimization.
- Use test scenarios only for held-out evaluation.
- Keep per-scenario sampling bounded so measured and design scenarios do not create uncontrolled batch counts.
- Record sampled window parameters in the config and findings.

If the existing model family already assumes a specific sequence length, the adapter should conform to that expectation unless doing so is impossible.

## Rainfall Alignment Strategy

Rainfall alignment must be conservative because Phase 45 observed rainfall length variants of 180 and 360. The future implementation should support both lengths without assuming a single universal temporal grid.

Recommended approach:

- Load `rainfall.npy` for each scenario lazily.
- Align rainfall to the selected flood input/target window by using a documented temporal summarization method.
- Use rainfall features that are compatible with both length 180 and length 360 arrays.
- Prefer simple summaries such as recent-window rainfall, cumulative rainfall over the model input period, and forecast-window rainfall summaries if target-period rainfall is explicitly allowed by the baseline definition.
- Record the rainfall alignment rule in the config.

The implementation must avoid hidden leakage. If rainfall from the prediction horizon is used, it must be treated as known forcing and documented as such. If the intended baseline is purely autoregressive, future rainfall should be excluded and the config must say so.

## Static Feature Strategy

The first baseline should use the following static inputs:

```text
absolute_DEM.npy
impervious.npy
manhole.npy
```

Each static feature should be downsampled to 128x128 and combined with dynamic inputs in the same input convention used by the existing Level 4+ model family.

Static feature handling should:

- Preserve channel identity.
- Avoid writing downsampled static tensors into the repository.
- Use deterministic downsampling.
- Record the downsampling method.
- Validate static tensor shape before training.

No additional static feature engineering is authorized in Phase 47 beyond adapter-compatible preprocessing.

## Model / Loss / Config Scope

The first baseline should use the existing Level 4+ model family as much as possible.

Allowed:

- Adapter plumbing needed to connect Phase 45/46 indexed data to the existing training path.
- A 128x128 configuration for the controlled pilot.
- Existing supervised flood-depth prediction losses.
- Minimal shape/channel compatibility changes if documented.

Not allowed:

- SWE residual loss.
- PINN loss.
- Strict conservation loss.
- New proxy-loss redesign.
- Architecture redesign.
- New model family selection.
- Uncontrolled hyperparameter search.

Future expected implementation files, not created by this Phase 47 planning step:

```text
scripts/train_phase47_full_downsample_baseline.py
configs/train_phase47_full_downsample128_seed42_10e.json
```

If existing `train_model.py` can be extended safely through a config-driven path, that is acceptable and may be preferable. Any such extension must remain bounded to adapter compatibility and the controlled 128x128 baseline.

## Training Resource and Memory Constraints

The pilot should be deliberately conservative.

Initial constraints:

```text
resolution = 128x128
batch_size = selected only after implementation smoke run
epochs = 5-10 pilot epochs
seed = seed42 only
dataset_loading = lazy
transformed_dataset_write = false
```

The implementation smoke run should select a batch size based on observed memory behavior. The initial training command should not assume that Phase 46 batch smoke results automatically validate long training memory behavior.

Memory observations to record:

- Peak GPU memory if CUDA is used.
- Peak process memory if available.
- Batch size.
- Sample tensor shapes.
- Runtime per epoch or per fixed number of iterations.
- Any dataloader worker or pin-memory setting.

If memory behavior is unstable or cannot be measured adequately, the training plan should be blocked or reduced before training begins.

## Evaluation Metrics

The first baseline should report supervised prediction quality and basic operational stability, not hydrodynamic closure.

Required metrics:

```text
RMSE
MAE
wet/dry IoU
step RMSE std
basic runtime observations
basic memory observations
```

If rollout evaluation is applicable to the existing model family, also report:

```text
rollout stability
```

Metrics should be computed on the held-out test scenarios from the Phase 45 split. Training metrics may be logged for monitoring, but test metrics must remain clearly separated from optimization.

The findings must avoid claiming strict conservation, full mass conservation, SWE consistency, or Level 5 hydrodynamic support.

## Output Directory and Artifact Plan

The controlled future run directory should use a name similar to:

```text
runs/phase47_full_downsample128_baseline_seed42_10e
```

Future analysis outputs should go under:

```text
analysis/phase47_controlled_downsample_baseline/
```

Future findings document:

```text
docs/phase47_controlled_full_dataset_downsample_baseline_findings.md
```

Future expected artifacts may include:

- Training config snapshot.
- Model checkpoint or best checkpoint.
- Metrics CSV or JSON.
- Evaluation summary.
- Runtime and memory notes.
- A concise findings document.

These artifacts should not be created in this planning step.

## Failure / Stop Conditions

The future implementation or training should stop before or during pilot execution if any of the following occur:

- `scenario_index.csv` cannot be loaded.
- `static_index.csv` cannot be loaded.
- The train/test split differs unexpectedly from 120 train and 48 test scenarios.
- Required files are missing for sampled scenarios.
- Flood or rainfall arrays have unsupported shapes.
- Rainfall alignment cannot be defined without leakage or undocumented assumptions.
- Static feature downsampling produces inconsistent shapes.
- Batch construction fails.
- Memory use is unsafe or grows unexpectedly.
- Loss becomes non-finite.
- Evaluation metrics cannot be computed.
- The implementation requires model redesign rather than adapter plumbing.
- The run would require 256x256, tile, multiscale, full 500x500, SWE/PINN, or seed expansion to proceed.

Possible blocked decisions:

```text
phase47_training_plan_blocked_needs_adapter_revision
phase47_training_plan_blocked_by_memory_risk
phase47_training_plan_deferred
```

## Guardrails

Phase 47 guardrails:

- Planning only.
- Do not train in this planning commit.
- Do not run seed42 yet.
- Do not run seed123 or seed202.
- Do not run sweeps.
- Do not implement SWE residuals.
- Do not implement PINN.
- Do not claim strict conservation.
- Do not claim full mass conservation.
- Do not claim hydrodynamic closure.
- Do not claim Level 5 support.
- Do not write transformed training datasets to disk.
- Do not copy the approximately 100GB dataset into the repository.
- Do not bypass Phase 47 authorization boundaries.
- Do not start 256x256, tile, multiscale, or full 500x500 training.
- Do not rewrite the model architecture unless unavoidable for adapter compatibility, and document any unavoidable change as adapter plumbing.

Decision candidates:

```text
phase47_128_downsample_training_plan_ready
phase47_training_plan_blocked_needs_adapter_revision
phase47_training_plan_blocked_by_memory_risk
phase47_training_plan_deferred
```

Expected conservative decision:

```text
phase47_128_downsample_training_plan_ready
```

## Success Criteria

Phase 47 planning is successful if it establishes a clear, reviewable boundary for the next implementation step:

- Only one controlled 128x128 full-dataset baseline is authorized for implementation.
- The implementation route uses Phase 45 indexes and Phase 46 smoke evidence.
- The model remains within the existing Level 4+ family as much as possible.
- The pilot is limited to one seed, likely seed42.
- The first pilot is limited to 5-10 epochs.
- No SWE/PINN/Level 5 claims are introduced.
- No 256x256, tile, multiscale, full 500x500, or seed expansion work is authorized.
- Expected future files and artifact directories are named but not created.
- Stop conditions are defined before training.

## Final Conclusion

Phase 47 authorizes only a controlled 128x128 full-dataset downsample baseline implementation in the next step, not immediate uncontrolled training. Training remains bounded to this reviewed plan and remains Level 4+.

The selected conservative decision is:

```text
phase47_128_downsample_training_plan_ready
```

