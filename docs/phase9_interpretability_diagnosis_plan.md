# Phase 9 Interpretability Diagnosis Plan

## Objective

Phase 9 should explain the confirmed Phase 8 Batch 2 trade-off for `adapt010`; it should not search for a new model.

Batch 2 established that `adapt010` remains the active adaptive candidate because it gives consistent RMSE, MAE, and loss gains across the required full `40e` comparisons against static Phase 3.3 `af025`. Wet/dry IoU remains mixed because `seed123` gives back IoU, and no favorable-case guardrail failure was found. The next useful work is therefore diagnostic: inspect the adaptive mechanism, isolate the wet/dry IoU trade-off, and make the `af025` versus `adapt010` comparison reproducible from existing artifacts.

## Utility 1: Adaptive Mechanism Inspection / Logging

Purpose:

- Expose how the `adapt010` adaptive scalar behaves on existing validation/test batches.
- Check whether the bounded adaptive multiplier stays near identity, saturates, or varies by forecast step, rainfall input, or sample.
- Provide mechanism-level context for the RMSE/MAE gains without changing architecture or training behavior.

Most likely extension points:

- `models/unet_tcn.py`, or the archived/adaptive model module if the adaptive response-split implementation is restored separately.
- `scripts/evaluate_model.py` for an evaluation-time flag that enables inspection.
- `trainers/test.py` for collecting optional per-batch diagnostic tensors during inference.
- `utils/visualization.py` for writing compact JSON/NPZ artifacts alongside existing evaluation outputs.

Inputs:

- Existing `adapt010` run directories under `runs/`, especially full `40e` seed runs.
- Existing `checkpoints/best.pt` for the selected `adapt010` run.
- The matching training config embedded in the checkpoint or supplied through the config path used by `scripts/evaluate_model.py`.
- Validation/test batches loaded through `UrbanFlood24LiteProcessDataset` with the same split and `wet_threshold` conventions already used by evaluation.

Outputs/artifacts:

- `adaptive_alpha_summary.json` with per-run scalar summaries: count, min, max, mean, std, percentiles, and saturation counts at configured bounds.
- Optional `adaptive_alpha_by_step.csv` with forecast-step aggregates if the adaptive scalar is step-dependent.
- Optional compact plots under the evaluation artifact directory, limited to scalar histograms or step curves.
- A small metadata block recording run name, checkpoint path, split, seed, and adaptive range.

Explicitly not done yet:

- Do not add new adaptive parameters.
- Do not change `adaptive_alpha_range`.
- Do not train or fine-tune models.
- Do not add gradient-based attribution or saliency methods.
- Do not interpret scalar variation as causal evidence unless paired with controlled outputs already available.

## Utility 2: Wet-Dry IoU Trade-Off Diagnosis

Purpose:

- Explain why `adapt010` improves RMSE/MAE/loss while wet/dry IoU is mixed, with `seed123` as the priority case.
- Separate threshold-crossing errors from depth-magnitude errors.
- Identify whether IoU loss comes from false wet pixels, false dry pixels, boundary shifts, or near-threshold predictions.

Most likely extension points:

- `utils/metrics.py` to add reusable wet/dry confusion diagnostics without changing the existing `compute_forecast_metrics` output contract.
- `trainers/test.py` to optionally save per-batch wet/dry diagnostic summaries.
- `scripts/evaluate_model.py` for a post-hoc diagnostic mode over existing checkpoints.
- `utils/visualization.py`, `compare_maps.py`, and `compare_timeseries.py` as references for artifact layout and simple paired visual outputs.

Inputs:

- Paired `af025` and `adapt010` evaluation artifacts for the same seed, split, batch index, and forecast step where available.
- Existing `forecast_maps.npz` files containing `prediction`, `target`, and `error`.
- Existing `summary.json` and `depth_timeseries.json` metadata where present.
- The configured `metrics.wet_threshold`, currently used by `compute_forecast_metrics`.
- Full `40e` comparison seeds: `seed202`, `seed123`, and `seed42`, with `seed123` analyzed first.

Outputs/artifacts:

- `wet_dry_confusion_by_step.csv` with TP, FP, FN, TN, IoU, precision, recall, and wet-area ratio per forecast step.
- `wet_dry_threshold_margin.json` summarizing how many pixels fall near the wet threshold for prediction and target.
- Paired diagnostic maps for selected batches/steps: target wet mask, `af025` wet mask, `adapt010` wet mask, FP/FN overlays, and absolute-error maps.
- A short per-seed Markdown or JSON summary that states whether IoU changes are dominated by FP, FN, boundary, or near-threshold behavior.

Explicitly not done yet:

- Do not change the wet threshold to improve results.
- Do not introduce alternate IoU metrics as replacement headline metrics.
- Do not rerun training.
- Do not select new seeds.
- Do not promote or reject `adapt010` based only on one visual batch.

## Utility 3: Unified Static `af025` vs `adapt010` Comparison Reporting

Purpose:

- Produce one reproducible static-control comparison report from existing run artifacts.
- Keep RMSE/MAE/loss interpretation separate from wet/dry IoU and rollout-stability interpretation.
- Avoid manually reconstructing Phase 8 comparison tables from scattered `history.json`, `metrics.json`, and visualization outputs.

Most likely extension points:

- A new small reporting script under `scripts/` in a later implementation stage, using the same JSON-reading style as `scripts/evaluate_model.py` and `scripts/train_model.py`.
- `utils/metrics.py` only if shared delta/format helpers are needed.
- Existing comparison scripts `compare_maps.py` and `compare_timeseries.py` as references, not as the main reporting interface.
- Existing docs tables in `docs/phase7_adapt010_results.md`, `docs/phase8_batch1_results.md`, and Phase 8 Batch 2 notes as validation targets for the generated report.

Inputs:

- Existing run roots for static Phase 3.3 `af025` and `adapt010`.
- `history.json` for final validation metrics from training runs.
- `evaluation_<split>/metrics.json` where available for checkpoint evaluation metrics.
- Optional paired visualization artifacts under `visualizations/` or `evaluation_<split>/`.
- A simple manifest mapping each seed to the static run root and adaptive run root.

Outputs/artifacts:

- `phase9_af025_vs_adapt010_summary.md` generated under an analysis output directory, not committed as a replacement for existing docs unless explicitly requested later.
- `phase9_af025_vs_adapt010_summary.csv` with raw metric values and deltas.
- Per-seed status fields: RMSE/MAE/loss direction, wet/dry IoU direction, rollout-stability direction, and guardrail note.
- Links or paths to paired diagnostic artifacts when they exist.

Explicitly not done yet:

- Do not update `README.md`, `docs/project_status.md`, or prior phase docs.
- Do not create new configs.
- Do not add a ranking score that collapses all metrics into one number.
- Do not include `adapt025` except as closed historical context.
- Do not start a broader sweep or architecture comparison.

## Recommended Implementation Order

1. Build the unified `af025` versus `adapt010` reporting utility first, because it defines the run manifest and confirms that all required existing artifacts are readable.
2. Add wet/dry IoU diagnostics next, starting with `seed123`, because this is the unresolved mixed signal from Batch 2.
3. Add adaptive scalar inspection last, after the artifact layout is fixed, so mechanism logs can be joined with the same seed/run manifest.

## Smallest Useful First Deliverable

The smallest useful deliverable is a read-only manifest-driven report for the three full `40e` comparisons:

- `seed202`: static `af025` versus `adapt010`
- `seed123`: static `af025` versus `adapt010`
- `seed42`: static `af025` versus `adapt010`

It should read existing `history.json` or `metrics.json` files and emit one CSV plus one Markdown table with metric values and deltas. No model loading is required for this first deliverable.

## Success Criteria

Phase 9 succeeds when:

- Existing `af025` versus `adapt010` evidence can be regenerated from repository artifacts without manual table assembly.
- The `seed123` wet/dry IoU give-back is localized to concrete FP/FN, boundary, or near-threshold behavior.
- Adaptive scalar logs show whether `adapt010` is using its adaptive range conservatively or saturating.
- Diagnostic outputs preserve the Batch 2 conclusion: `adapt010` remains active, gains are strongest on RMSE/MAE/loss, wet/dry IoU is mixed, and no broader sweep is justified.
- No code path changes model behavior unless an explicit later implementation task requests it.
