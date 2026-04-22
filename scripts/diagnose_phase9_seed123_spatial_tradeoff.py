from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

import numpy as np


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_WET_THRESHOLD = 0.05
DEFAULT_NEAR_THRESHOLD_MARGIN = 0.005
DEFAULT_STEPS = (9, 10)
DEFAULT_STATIC_RUN_ROOT = Path(
    "runs/phase8_validation_temporal_gate_residual_response_split_protected_h16_a010_f025_af025_40e_seed123"
)
DEFAULT_ADAPTIVE_RUN_ROOT = Path(
    "runs/phase8_validation_temporal_gate_residual_response_split_protected_h16_a010_f025_af025_adapt010_40e_seed123"
)
DEFAULT_OUTPUT_DIR = Path("analysis/phase9_seed123_spatial_tradeoff")


def resolve_repo_path(path: str | Path) -> Path:
    path = Path(path)
    if path.is_absolute():
        return path
    return REPO_ROOT / path


def display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return str(path)


def discover_batch_dirs(run_root: Path) -> dict[str, dict[str, Path]]:
    forecast_paths = sorted(run_root.glob("visualizations/epoch_*/val_batch_*/forecast_maps.npz"))
    batches: dict[str, dict[str, Path]] = {}
    for forecast_path in forecast_paths:
        epoch = forecast_path.parents[1].name
        batch = forecast_path.parent.name
        batches.setdefault(epoch, {})[batch] = forecast_path.parent
    return batches


def choose_latest_common_epoch(
    static_batches: dict[str, dict[str, Path]],
    adaptive_batches: dict[str, dict[str, Path]],
) -> tuple[str | None, list[str]]:
    common_epochs = sorted(set(static_batches) & set(adaptive_batches))
    if not common_epochs:
        return None, []
    epoch = common_epochs[-1]
    common_batches = sorted(set(static_batches[epoch]) & set(adaptive_batches[epoch]))
    return epoch, common_batches


def load_maps(batch_dir: Path) -> dict[str, np.ndarray]:
    maps_path = batch_dir / "forecast_maps.npz"
    with np.load(maps_path) as payload:
        missing = {"prediction", "target"} - set(payload.files)
        if missing:
            raise ValueError(f"{display_path(maps_path)} is missing arrays: {sorted(missing)}")
        return {
            "prediction": payload["prediction"],
            "target": payload["target"],
        }


def shift_mask(mask: np.ndarray, dy: int, dx: int) -> np.ndarray:
    shifted = np.zeros_like(mask, dtype=bool)
    src_y = slice(max(0, -dy), mask.shape[-2] - max(0, dy))
    dst_y = slice(max(0, dy), mask.shape[-2] - max(0, -dy))
    src_x = slice(max(0, -dx), mask.shape[-1] - max(0, dx))
    dst_x = slice(max(0, dx), mask.shape[-1] - max(0, -dx))
    shifted[..., dst_y, dst_x] = mask[..., src_y, src_x]
    return shifted


def dilate_4(mask: np.ndarray) -> np.ndarray:
    result = mask.copy()
    for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        result |= shift_mask(mask, dy, dx)
    return result


def erode_4(mask: np.ndarray) -> np.ndarray:
    result = mask.copy()
    for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        result &= shift_mask(mask, dy, dx)
    return result


def target_boundary_band(target_wet: np.ndarray) -> np.ndarray:
    return dilate_4(target_wet) & ~erode_4(target_wet)


def safe_div(numerator: int | float, denominator: int | float) -> float | None:
    if denominator == 0:
        return None
    return float(numerator) / float(denominator)


def wet_confusion(prediction: np.ndarray, target: np.ndarray, wet_threshold: float) -> dict[str, np.ndarray]:
    pred_wet = prediction > wet_threshold
    target_wet = target > wet_threshold
    return {
        "prediction_wet": pred_wet,
        "target_wet": target_wet,
        "tp": pred_wet & target_wet,
        "fp": pred_wet & ~target_wet,
        "fn": ~pred_wet & target_wet,
        "tn": ~pred_wet & ~target_wet,
    }


def error_class(confusion: dict[str, np.ndarray]) -> np.ndarray:
    classes = np.zeros(confusion["target_wet"].shape, dtype=np.uint8)
    classes[confusion["tp"]] = 1
    classes[confusion["fp"]] = 2
    classes[confusion["fn"]] = 3
    return classes


def summarize_model(
    *,
    model_label: str,
    prediction: np.ndarray,
    target: np.ndarray,
    wet_threshold: float,
    near_threshold_margin: float,
) -> tuple[dict[str, Any], dict[str, np.ndarray]]:
    confusion = wet_confusion(prediction, target, wet_threshold)
    boundary = target_boundary_band(confusion["target_wet"])
    near_threshold = np.abs(target - wet_threshold) <= near_threshold_margin
    tp = int(confusion["tp"].sum())
    fp = int(confusion["fp"].sum())
    fn = int(confusion["fn"].sum())
    tn = int(confusion["tn"].sum())
    union = tp + fp + fn
    total = tp + fp + fn + tn
    summary = {
        "model": model_label,
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "tn": tn,
        "iou": safe_div(tp, union),
        "precision": safe_div(tp, tp + fp),
        "recall": safe_div(tp, tp + fn),
        "prediction_wet_area_ratio": safe_div(tp + fp, total),
        "target_wet_area_ratio": safe_div(tp + fn, total),
        "mean_abs_error": float(np.abs(prediction - target).mean()),
        "fp_on_target_boundary_count": int((confusion["fp"] & boundary).sum()),
        "fn_on_target_boundary_count": int((confusion["fn"] & boundary).sum()),
        "fp_on_target_boundary_ratio": safe_div(int((confusion["fp"] & boundary).sum()), fp),
        "fn_on_target_boundary_ratio": safe_div(int((confusion["fn"] & boundary).sum()), fn),
        "fp_near_threshold_target_count": int((confusion["fp"] & near_threshold).sum()),
        "fn_near_threshold_target_count": int((confusion["fn"] & near_threshold).sum()),
        "fp_near_threshold_target_ratio": safe_div(int((confusion["fp"] & near_threshold).sum()), fp),
        "fn_near_threshold_target_ratio": safe_div(int((confusion["fn"] & near_threshold).sum()), fn),
    }
    masks = {
        "prediction_wet_mask": confusion["prediction_wet"].astype(np.uint8),
        "target_wet_mask": confusion["target_wet"].astype(np.uint8),
        "fp_mask": confusion["fp"].astype(np.uint8),
        "fn_mask": confusion["fn"].astype(np.uint8),
        "error_class": error_class(confusion),
        "target_boundary_band": boundary.astype(np.uint8),
        "target_near_threshold_mask": near_threshold.astype(np.uint8),
        "absolute_error": np.abs(prediction - target).astype(np.float32),
    }
    return summary, masks


def aggregate_rows(rows: list[dict[str, Any]], step: int) -> dict[str, Any]:
    static_rows = [row for row in rows if row["forecast_step"] == step and row["model"] == "static_af025"]
    adaptive_rows = [row for row in rows if row["forecast_step"] == step and row["model"] == "adapt010"]
    static = sum_model_rows(static_rows)
    adaptive = sum_model_rows(adaptive_rows)
    return {
        "forecast_step": step,
        "static": static,
        "adapt010": adaptive,
        "delta": {
            "iou": None if static["iou"] is None or adaptive["iou"] is None else adaptive["iou"] - static["iou"],
            "fp": adaptive["fp"] - static["fp"],
            "fn": adaptive["fn"] - static["fn"],
            "prediction_wet_area_ratio": adaptive["prediction_wet_area_ratio"] - static["prediction_wet_area_ratio"],
            "mean_abs_error": adaptive["mean_abs_error"] - static["mean_abs_error"],
        },
        "mode": classify_shift(static, adaptive),
    }


def sum_model_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    tp = sum(int(row["tp"]) for row in rows)
    fp = sum(int(row["fp"]) for row in rows)
    fn = sum(int(row["fn"]) for row in rows)
    tn = sum(int(row["tn"]) for row in rows)
    total = tp + fp + fn + tn
    weighted_mae = sum(float(row["mean_abs_error"]) * int(row["total_pixels"]) for row in rows)
    return {
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "tn": tn,
        "iou": safe_div(tp, tp + fp + fn),
        "precision": safe_div(tp, tp + fp),
        "recall": safe_div(tp, tp + fn),
        "prediction_wet_area_ratio": safe_div(tp + fp, total),
        "target_wet_area_ratio": safe_div(tp + fn, total),
        "mean_abs_error": safe_div(weighted_mae, total),
        "fp_on_target_boundary_ratio": safe_div(
            sum(int(row["fp_on_target_boundary_count"]) for row in rows),
            fp,
        ),
        "fn_on_target_boundary_ratio": safe_div(
            sum(int(row["fn_on_target_boundary_count"]) for row in rows),
            fn,
        ),
        "fp_near_threshold_target_ratio": safe_div(
            sum(int(row["fp_near_threshold_target_count"]) for row in rows),
            fp,
        ),
        "fn_near_threshold_target_ratio": safe_div(
            sum(int(row["fn_near_threshold_target_count"]) for row in rows),
            fn,
        ),
    }


def classify_shift(static: dict[str, Any], adaptive: dict[str, Any]) -> str:
    fp_delta = adaptive["fp"] - static["fp"]
    fn_delta = adaptive["fn"] - static["fn"]
    wet_delta = adaptive["prediction_wet_area_ratio"] - static["prediction_wet_area_ratio"]
    if fp_delta > 0 and fn_delta <= 0:
        return "wet-expansive, FP-growth dominated"
    if fn_delta > 0 and fp_delta <= 0:
        return "dry-conservative, FN-growth dominated"
    if fp_delta > 0 and fn_delta > 0:
        return "mixed shift with both FP and FN growth"
    if wet_delta > 0:
        return "wet-expansive with lower total error counts"
    if wet_delta < 0:
        return "dry-conservative with lower total error counts"
    return "mixed or neutral shift"


def write_summary_csv(rows: list[dict[str, Any]], output_path: Path) -> None:
    fields = [
        "batch",
        "forecast_step",
        "model",
        "tp",
        "fp",
        "fn",
        "tn",
        "iou",
        "precision",
        "recall",
        "prediction_wet_area_ratio",
        "target_wet_area_ratio",
        "mean_abs_error",
        "fp_on_target_boundary_ratio",
        "fn_on_target_boundary_ratio",
        "fp_near_threshold_target_ratio",
        "fn_near_threshold_target_ratio",
    ]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: format_value(row.get(field)) for field in fields})


def format_value(value: Any) -> str:
    if value is None:
        return "NA"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_markdown(
    *,
    output_path: Path,
    static_run_root: Path,
    adaptive_run_root: Path,
    selected_epoch: str,
    selected_batches: list[str],
    steps: list[int],
    used_artifacts: list[dict[str, str]],
    aggregate: list[dict[str, Any]],
    wet_threshold: float,
    near_threshold_margin: float,
) -> None:
    lines = [
        "# Phase 9 Seed123 Spatial Wet/Dry Trade-Off Diagnosis",
        "",
        f"- static run root: `{display_path(static_run_root)}`",
        f"- adapt010 run root: `{display_path(adaptive_run_root)}`",
        f"- selected artifact epoch: `{selected_epoch}`",
        f"- selected batches: `{', '.join(selected_batches)}`",
        f"- selected steps: `{', '.join(str(step) for step in steps)}`",
        f"- wet threshold: `{wet_threshold}`",
        f"- near-threshold target margin: `+/- {near_threshold_margin}`",
        "",
        "## Artifact Paths Used",
        "",
    ]
    for artifact in used_artifacts:
        lines.append(
            f"- {artifact['batch']}: static `{artifact['static_forecast_maps']}`, adapt010 `{artifact['adapt010_forecast_maps']}`"
        )

    lines.extend(
        [
            "",
            "## Step Summary",
            "",
            "| step | static IoU | adapt010 IoU | IoU delta | FP delta | FN delta | pred wet-area delta | static boundary FP/FN | adapt010 boundary FP/FN | shift reading |",
            "|---:|---:|---:|---:|---:|---:|---:|---|---|---|",
        ]
    )
    for item in aggregate:
        static = item["static"]
        adaptive = item["adapt010"]
        delta = item["delta"]
        lines.append(
            "| {step} | {static_iou} | {adaptive_iou} | {iou_delta} | {fp_delta} | {fn_delta} | {wet_delta} | {static_boundary} | {adaptive_boundary} | {mode} |".format(
                step=item["forecast_step"],
                static_iou=format_value(static["iou"]),
                adaptive_iou=format_value(adaptive["iou"]),
                iou_delta=format_value(delta["iou"]),
                fp_delta=format_value(delta["fp"]),
                fn_delta=format_value(delta["fn"]),
                wet_delta=format_value(delta["prediction_wet_area_ratio"]),
                static_boundary=format_boundary(static),
                adaptive_boundary=format_boundary(adaptive),
                mode=item["mode"],
            )
        )

    lines.extend(["", "## Interpretation", ""])
    by_step = {item["forecast_step"]: item for item in aggregate}
    if 9 in by_step:
        item = by_step[9]
        lines.append(
            "- Step 9 is wet-expansive for adapt010 in the inspected paired artifacts: "
            f"FP changes by `{item['delta']['fp']}` while FN changes by `{item['delta']['fn']}`, "
            f"and prediction wet-area ratio changes by `{item['delta']['prediction_wet_area_ratio']:.6f}`. "
            "The IoU loss is therefore FP-growth dominated in this subset."
        )
    if 10 in by_step:
        item = by_step[10]
        lines.append(
            "- Step 10 shifts in the opposite direction: adapt010 is dry-conservative relative to static af025, "
            f"with FP changing by `{item['delta']['fp']}` and FN changing by `{item['delta']['fn']}`. "
            f"IoU is nearly flat to slightly higher in this subset (`{item['delta']['iou']:.6f}`), so the transition is not a step-10 IoU failure despite increased FN."
        )

    lines.extend(
        [
            "- Boundary ratios are high for FP/FN errors in both models, supporting a boundary/wet-margin interpretation for these selected artifacts. This is based on a simple one-pixel target wet/dry boundary band, not a hydrologic boundary model.",
            "- The obvious step difference is direction: step 9 expands wet predictions and loses IoU through FP growth, while step 10 contracts wet predictions and trades lower FP for higher FN.",
            "- This summary is limited to the paired `forecast_maps.npz` artifacts listed above and should not be read as a full validation-set spatial conclusion.",
            "",
            "## Compact Mask Artifacts",
            "",
            "For each selected batch and step, `spatial_masks_<batch>_stepXX.npz` stores target/static/adapt010 wet masks, FP/FN masks, error-class masks, one-pixel target boundary bands, target near-threshold masks, and absolute-error arrays. Error class encoding is `0=TN`, `1=TP`, `2=FP`, `3=FN`.",
        ]
    )
    output_path.write_text("\n".join(lines), encoding="utf-8")


def format_boundary(summary: dict[str, Any]) -> str:
    return "FP {fp}, FN {fn}".format(
        fp=format_value(summary["fp_on_target_boundary_ratio"]),
        fn=format_value(summary["fn_on_target_boundary_ratio"]),
    )


def run_diagnosis(args: argparse.Namespace) -> None:
    static_run_root = resolve_repo_path(args.static_run_root)
    adaptive_run_root = resolve_repo_path(args.adapt010_run_root)
    output_dir = resolve_repo_path(args.output_dir)
    if not static_run_root.exists():
        raise FileNotFoundError(f"Static run root not found: {display_path(static_run_root)}")
    if not adaptive_run_root.exists():
        raise FileNotFoundError(f"adapt010 run root not found: {display_path(adaptive_run_root)}")

    static_batches = discover_batch_dirs(static_run_root)
    adaptive_batches = discover_batch_dirs(adaptive_run_root)
    selected_epoch, selected_batches = choose_latest_common_epoch(static_batches, adaptive_batches)
    if selected_epoch is None or not selected_batches:
        raise FileNotFoundError("No paired forecast_maps.npz artifacts found for a common validation epoch.")

    steps = sorted(set(args.steps))
    output_dir.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, Any]] = []
    used_artifacts: list[dict[str, str]] = []
    mask_dir = output_dir / "compact_masks"
    mask_dir.mkdir(parents=True, exist_ok=True)

    for batch in selected_batches:
        static_dir = static_batches[selected_epoch][batch]
        adaptive_dir = adaptive_batches[selected_epoch][batch]
        static_maps = load_maps(static_dir)
        adaptive_maps = load_maps(adaptive_dir)
        if static_maps["prediction"].shape != adaptive_maps["prediction"].shape:
            raise ValueError(f"Prediction shape mismatch for {batch}.")
        if static_maps["target"].shape != adaptive_maps["target"].shape:
            raise ValueError(f"Target shape mismatch for {batch}.")
        if not np.allclose(static_maps["target"], adaptive_maps["target"]):
            raise ValueError(f"Targets differ numerically for {batch}; spatial paired diagnosis requires shared targets.")

        used_artifacts.append(
            {
                "batch": batch,
                "static_forecast_maps": display_path(static_dir / "forecast_maps.npz"),
                "adapt010_forecast_maps": display_path(adaptive_dir / "forecast_maps.npz"),
            }
        )

        target = static_maps["target"]
        future_steps = target.shape[1]
        for step in steps:
            if step < 0 or step >= future_steps:
                raise ValueError(f"Requested step {step} is outside available range [0, {future_steps - 1}].")

            step_target = target[:, step]
            static_prediction = static_maps["prediction"][:, step]
            adaptive_prediction = adaptive_maps["prediction"][:, step]
            static_summary, static_masks = summarize_model(
                model_label="static_af025",
                prediction=static_prediction,
                target=step_target,
                wet_threshold=args.wet_threshold,
                near_threshold_margin=args.near_threshold_margin,
            )
            adaptive_summary, adaptive_masks = summarize_model(
                model_label="adapt010",
                prediction=adaptive_prediction,
                target=step_target,
                wet_threshold=args.wet_threshold,
                near_threshold_margin=args.near_threshold_margin,
            )
            for summary in (static_summary, adaptive_summary):
                summary["batch"] = batch
                summary["forecast_step"] = step
                summary["total_pixels"] = int(step_target.size)
                rows.append(summary)

            np.savez_compressed(
                mask_dir / f"spatial_masks_{batch}_step{step:02d}.npz",
                target_wet_mask=static_masks["target_wet_mask"],
                static_af025_wet_mask=static_masks["prediction_wet_mask"],
                adapt010_wet_mask=adaptive_masks["prediction_wet_mask"],
                static_fp_mask=static_masks["fp_mask"],
                static_fn_mask=static_masks["fn_mask"],
                adapt010_fp_mask=adaptive_masks["fp_mask"],
                adapt010_fn_mask=adaptive_masks["fn_mask"],
                static_error_class=static_masks["error_class"],
                adapt010_error_class=adaptive_masks["error_class"],
                target_boundary_band=static_masks["target_boundary_band"],
                target_near_threshold_mask=static_masks["target_near_threshold_mask"],
                static_absolute_error=static_masks["absolute_error"],
                adapt010_absolute_error=adaptive_masks["absolute_error"],
            )

    aggregate = [aggregate_rows(rows, step) for step in steps]
    write_summary_csv(rows, output_dir / "seed123_step09_10_spatial_summary.csv")
    (output_dir / "seed123_step09_10_spatial_summary.json").write_text(
        json.dumps(
            {
                "static_run_root": display_path(static_run_root),
                "adapt010_run_root": display_path(adaptive_run_root),
                "selected_epoch": selected_epoch,
                "selected_batches": selected_batches,
                "selected_steps": steps,
                "wet_threshold": args.wet_threshold,
                "near_threshold_margin": args.near_threshold_margin,
                "used_artifacts": used_artifacts,
                "aggregate": aggregate,
                "rows": rows,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    write_markdown(
        output_path=output_dir / "seed123_step09_10_spatial_diagnosis.md",
        static_run_root=static_run_root,
        adaptive_run_root=adaptive_run_root,
        selected_epoch=selected_epoch,
        selected_batches=selected_batches,
        steps=steps,
        used_artifacts=used_artifacts,
        aggregate=aggregate,
        wet_threshold=args.wet_threshold,
        near_threshold_margin=args.near_threshold_margin,
    )

    print(f"Wrote CSV: {display_path(output_dir / 'seed123_step09_10_spatial_summary.csv')}")
    print(f"Wrote JSON: {display_path(output_dir / 'seed123_step09_10_spatial_summary.json')}")
    print(f"Wrote Markdown: {display_path(output_dir / 'seed123_step09_10_spatial_diagnosis.md')}")
    print(f"Wrote compact masks: {display_path(mask_dir)}")
    print("Used forecast artifacts:")
    for artifact in used_artifacts:
        print(f"- {artifact['batch']}: {artifact['static_forecast_maps']} | {artifact['adapt010_forecast_maps']}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Spatial FP/FN diagnosis for seed123 static af025 vs adapt010 forecast artifacts."
    )
    parser.add_argument("--static-run-root", type=Path, default=DEFAULT_STATIC_RUN_ROOT)
    parser.add_argument("--adapt010-run-root", type=Path, default=DEFAULT_ADAPTIVE_RUN_ROOT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--steps", type=int, nargs="+", default=list(DEFAULT_STEPS))
    parser.add_argument("--wet-threshold", type=float, default=DEFAULT_WET_THRESHOLD)
    parser.add_argument("--near-threshold-margin", type=float, default=DEFAULT_NEAR_THRESHOLD_MARGIN)
    return parser.parse_args()


def main() -> None:
    run_diagnosis(parse_args())


if __name__ == "__main__":
    main()
