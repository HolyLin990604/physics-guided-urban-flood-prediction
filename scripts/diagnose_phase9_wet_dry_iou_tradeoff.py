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


def load_json_if_available(path: Path) -> Any | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


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


def empty_counts(steps: int) -> list[dict[str, int]]:
    return [{"tp": 0, "fp": 0, "fn": 0, "tn": 0} for _ in range(steps)]


def add_counts(
    counts_by_step: list[dict[str, int]],
    *,
    prediction: np.ndarray,
    target: np.ndarray,
    wet_threshold: float,
) -> None:
    if prediction.shape != target.shape:
        raise ValueError(f"Prediction shape {prediction.shape} does not match target shape {target.shape}.")
    if prediction.ndim != 5:
        raise ValueError(f"Expected rank-5 arrays [B, T, C, H, W], got {prediction.shape}.")

    pred_wet = prediction > wet_threshold
    target_wet = target > wet_threshold
    steps = prediction.shape[1]
    for step in range(steps):
        pred_step = pred_wet[:, step]
        target_step = target_wet[:, step]
        counts_by_step[step]["tp"] += int(np.logical_and(pred_step, target_step).sum())
        counts_by_step[step]["fp"] += int(np.logical_and(pred_step, ~target_step).sum())
        counts_by_step[step]["fn"] += int(np.logical_and(~pred_step, target_step).sum())
        counts_by_step[step]["tn"] += int(np.logical_and(~pred_step, ~target_step).sum())


def finalize_counts(model_label: str, counts_by_step: list[dict[str, int]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for step_idx, counts in enumerate(counts_by_step):
        tp = counts["tp"]
        fp = counts["fp"]
        fn = counts["fn"]
        tn = counts["tn"]
        union = tp + fp + fn
        pred_wet = tp + fp
        target_wet = tp + fn
        total = tp + fp + fn + tn
        rows.append(
            {
                "model": model_label,
                "forecast_step": step_idx,
                "tp": tp,
                "fp": fp,
                "fn": fn,
                "tn": tn,
                "iou": safe_div(tp, union),
                "precision": safe_div(tp, pred_wet),
                "recall": safe_div(tp, target_wet),
                "target_wet_area_ratio": safe_div(target_wet, total),
                "prediction_wet_area_ratio": safe_div(pred_wet, total),
            }
        )
    return rows


def safe_div(numerator: int | float, denominator: int | float) -> float | None:
    if denominator == 0:
        return None
    return float(numerator) / float(denominator)


def summarize_margin(values: np.ndarray, wet_threshold: float, margin: float) -> dict[str, Any]:
    near = np.abs(values - wet_threshold) <= margin
    total = int(values.size)
    count = int(near.sum())
    return {
        "total_pixels": total,
        "near_threshold_count": count,
        "near_threshold_ratio": safe_div(count, total),
        "threshold": wet_threshold,
        "margin": margin,
        "min": float(values.min()),
        "max": float(values.max()),
        "mean": float(values.mean()),
    }


def format_value(value: Any) -> str:
    if value is None:
        return "NA"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def build_step_deltas(static_rows: list[dict[str, Any]], adaptive_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    static_by_step = {int(row["forecast_step"]): row for row in static_rows}
    adaptive_by_step = {int(row["forecast_step"]): row for row in adaptive_rows}
    deltas: list[dict[str, Any]] = []
    for step in sorted(set(static_by_step) & set(adaptive_by_step)):
        static_row = static_by_step[step]
        adaptive_row = adaptive_by_step[step]
        deltas.append(
            {
                "forecast_step": step,
                "static_iou": static_row["iou"],
                "adapt010_iou": adaptive_row["iou"],
                "iou_delta": None
                if static_row["iou"] is None or adaptive_row["iou"] is None
                else adaptive_row["iou"] - static_row["iou"],
                "fp_delta": int(adaptive_row["fp"]) - int(static_row["fp"]),
                "fn_delta": int(adaptive_row["fn"]) - int(static_row["fn"]),
                "static_prediction_wet_area_ratio": static_row["prediction_wet_area_ratio"],
                "adapt010_prediction_wet_area_ratio": adaptive_row["prediction_wet_area_ratio"],
            }
        )
    return deltas


def summarize_tradeoff(
    static_rows: list[dict[str, Any]],
    adaptive_rows: list[dict[str, Any]],
    margin_summary: dict[str, Any],
) -> dict[str, Any]:
    step_deltas = build_step_deltas(static_rows, adaptive_rows)
    static_iou = np.mean([row["iou"] for row in static_rows if row["iou"] is not None])
    adaptive_iou = np.mean([row["iou"] for row in adaptive_rows if row["iou"] is not None])
    static_fp = sum(int(row["fp"]) for row in static_rows)
    adaptive_fp = sum(int(row["fp"]) for row in adaptive_rows)
    static_fn = sum(int(row["fn"]) for row in static_rows)
    adaptive_fn = sum(int(row["fn"]) for row in adaptive_rows)
    static_near = margin_summary["static_af025_prediction"]["near_threshold_ratio"]
    adaptive_near = margin_summary["adapt010_prediction"]["near_threshold_ratio"]

    valid_iou_deltas = [row for row in step_deltas if row["iou_delta"] is not None]
    highlights = {
        "largest_iou_drop": min(valid_iou_deltas, key=lambda row: row["iou_delta"]) if valid_iou_deltas else None,
        "largest_fn_increase": max(step_deltas, key=lambda row: row["fn_delta"]) if step_deltas else None,
        "largest_fp_increase": max(step_deltas, key=lambda row: row["fp_delta"]) if step_deltas else None,
    }
    fp_increase_steps = sum(1 for row in step_deltas if row["fp_delta"] > 0)
    fn_increase_steps = sum(1 for row in step_deltas if row["fn_delta"] > 0)

    summary = {
        "mean_static_iou": float(static_iou),
        "mean_adapt010_iou": float(adaptive_iou),
        "mean_iou_delta": float(adaptive_iou - static_iou),
        "total_static_fp": static_fp,
        "total_adapt010_fp": adaptive_fp,
        "total_fp_delta": adaptive_fp - static_fp,
        "total_static_fn": static_fn,
        "total_adapt010_fn": adaptive_fn,
        "total_fn_delta": adaptive_fn - static_fn,
        "static_prediction_near_threshold_ratio": static_near,
        "adapt010_prediction_near_threshold_ratio": adaptive_near,
        "near_threshold_ratio_delta": None if static_near is None or adaptive_near is None else adaptive_near - static_near,
        "fp_increase_steps": fp_increase_steps,
        "fn_increase_steps": fn_increase_steps,
        "step_count": len(step_deltas),
        "step_deltas": step_deltas,
        "highlights": highlights,
    }
    summary["interpretation"] = interpret_tradeoff(summary)
    return summary


def interpret_tradeoff(summary: dict[str, Any]) -> str:
    if summary["mean_iou_delta"] >= 0:
        return "No mean IoU give-back is visible in the compared paired artifact subset."

    fp_delta = summary["total_fp_delta"]
    fn_delta = summary["total_fn_delta"]
    fp_steps = summary["fp_increase_steps"]
    fn_steps = summary["fn_increase_steps"]
    near_delta = summary["near_threshold_ratio_delta"] or 0.0
    has_mixed_steps = fp_steps > 0 and fn_steps > 0

    if fn_delta > fp_delta > 0 and has_mixed_steps:
        mode = "mixed error mode, FN-leaning overall, with step-specific FP increases also present"
    elif fp_delta > fn_delta > 0 and has_mixed_steps:
        mode = "mixed error mode, FP-leaning overall, with step-specific FN increases also present"
    elif fn_delta > 0 and fp_delta <= 0:
        mode = "FN-leaning overall"
    elif fp_delta > 0 and fn_delta <= 0:
        mode = "FP-leaning overall"
    else:
        mode = "mixed error mode without a single dominant FP/FN direction"

    if near_delta > 0:
        return f"The IoU give-back is {mode}; adapt010 also has a higher near-threshold prediction ratio."
    return f"The IoU give-back is {mode}; near-threshold prediction ratio does not increase."


def write_confusion_csv(rows: list[dict[str, Any]], output_path: Path) -> None:
    fields = [
        "model",
        "forecast_step",
        "tp",
        "fp",
        "fn",
        "tn",
        "iou",
        "precision",
        "recall",
        "target_wet_area_ratio",
        "prediction_wet_area_ratio",
    ]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: format_value(row.get(field)) for field in fields})


def write_markdown(
    *,
    output_path: Path,
    seed_label: str,
    static_run_root: Path,
    adaptive_run_root: Path,
    selected_epoch: str | None,
    selected_batches: list[str],
    used_artifacts: list[dict[str, str]],
    missing_notes: list[str],
    tradeoff_summary: dict[str, Any] | None,
    wet_threshold: float,
    near_threshold_margin: float,
    static_rows: list[dict[str, Any]],
    adaptive_rows: list[dict[str, Any]],
) -> None:
    lines = [
        f"# Phase 9 Wet/Dry IoU Trade-Off Diagnosis: {seed_label}",
        "",
        f"- wet threshold: `{wet_threshold}`",
        f"- near-threshold margin: `+/- {near_threshold_margin}`",
        f"- static run root: `{display_path(static_run_root)}`",
        f"- adapt010 run root: `{display_path(adaptive_run_root)}`",
        f"- selected artifact epoch: `{selected_epoch or 'NONE'}`",
        f"- selected batches: `{', '.join(selected_batches) if selected_batches else 'NONE'}`",
        "",
        "## Artifact Availability",
        "",
    ]
    if used_artifacts:
        for artifact in used_artifacts:
            lines.append(
                f"- {artifact['batch']}: static `{artifact['static_forecast_maps']}`, adapt010 `{artifact['adapt010_forecast_maps']}`"
            )
    else:
        lines.append("- No paired forecast artifacts were available.")

    lines.extend(["", "## Missing Or Limited Comparisons", ""])
    if missing_notes:
        lines.extend(f"- {note}" for note in missing_notes)
    else:
        lines.append("- No missing paired batch artifacts in the selected epoch.")

    lines.extend(
        [
            "",
            "## First-Pass Interpretation",
            "",
            f"- {tradeoff_summary['interpretation'] if tradeoff_summary else 'No paired arrays were available for wet/dry IoU diagnosis.'}",
            "- This is a paired artifact diagnosis only; it does not replace the full validation metrics.",
            "- Step-level conclusions are based only on the currently available paired artifact subset.",
            "",
            "## Aggregate Deltas",
            "",
            "| metric | delta |",
            "|---|---:|",
            f"| mean IoU delta | {format_value(tradeoff_summary['mean_iou_delta'] if tradeoff_summary else None)} |",
            f"| total FP delta | {format_value(tradeoff_summary['total_fp_delta'] if tradeoff_summary else None)} |",
            f"| total FN delta | {format_value(tradeoff_summary['total_fn_delta'] if tradeoff_summary else None)} |",
            f"| near-threshold prediction ratio delta | {format_value(tradeoff_summary['near_threshold_ratio_delta'] if tradeoff_summary else None)} |",
            "",
            "## Mean Per-Step IoU In Compared Artifacts",
            "",
            "| model | mean IoU | total FP | total FN |",
            "|---|---:|---:|---:|",
        ]
    )
    for label, rows in (("static_af025", static_rows), ("adapt010", adaptive_rows)):
        mean_iou = np.mean([row["iou"] for row in rows if row["iou"] is not None]) if rows else None
        total_fp = sum(int(row["fp"]) for row in rows)
        total_fn = sum(int(row["fn"]) for row in rows)
        lines.append(f"| {label} | {format_value(mean_iou)} | {total_fp} | {total_fn} |")

    lines.extend(["", "## Step-Level Highlights", ""])
    if tradeoff_summary:
        lines.extend(
            [
                "| highlight | step | static IoU | adapt010 IoU | IoU delta | FP delta | FN delta | static pred wet ratio | adapt010 pred wet ratio |",
                "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
            ]
        )
        for label, row in (
            ("largest IoU drop", tradeoff_summary["highlights"]["largest_iou_drop"]),
            ("largest FN increase", tradeoff_summary["highlights"]["largest_fn_increase"]),
            ("largest FP increase", tradeoff_summary["highlights"]["largest_fp_increase"]),
        ):
            if row is None:
                continue
            lines.append(
                "| {label} | {step} | {static_iou} | {adapt_iou} | {iou_delta} | {fp_delta} | {fn_delta} | {static_wet} | {adapt_wet} |".format(
                    label=label,
                    step=row["forecast_step"],
                    static_iou=format_value(row["static_iou"]),
                    adapt_iou=format_value(row["adapt010_iou"]),
                    iou_delta=format_value(row["iou_delta"]),
                    fp_delta=format_value(row["fp_delta"]),
                    fn_delta=format_value(row["fn_delta"]),
                    static_wet=format_value(row["static_prediction_wet_area_ratio"]),
                    adapt_wet=format_value(row["adapt010_prediction_wet_area_ratio"]),
                )
            )
    else:
        lines.append("- No step-level highlights available.")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Diagnose Phase 9 wet/dry IoU trade-off from existing artifacts.")
    parser.add_argument("--static-run-root", type=Path, required=True, help="Static af025 run root.")
    parser.add_argument("--adapt010-run-root", type=Path, required=True, help="adapt010 run root.")
    parser.add_argument("--seed-label", required=True, help="Seed label for output summaries.")
    parser.add_argument("--output-dir", type=Path, required=True, help="Output directory under analysis/.")
    parser.add_argument(
        "--wet-threshold",
        type=float,
        default=DEFAULT_WET_THRESHOLD,
        help="Wet/dry threshold. Defaults to the repository convention used by metrics configs.",
    )
    parser.add_argument(
        "--near-threshold-margin",
        type=float,
        default=DEFAULT_NEAR_THRESHOLD_MARGIN,
        help="Absolute margin around wet threshold used for near-threshold counts.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
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

    missing_notes: list[str] = []
    used_artifacts: list[dict[str, str]] = []
    if selected_epoch is None:
        missing_notes.append("No common visualization epoch with forecast_maps.npz was found.")
        selected_batches = []
    elif not selected_batches:
        missing_notes.append(f"No common val_batch directories found under selected epoch {selected_epoch}.")

    static_counts: list[dict[str, int]] | None = None
    adaptive_counts: list[dict[str, int]] | None = None
    target_values: list[np.ndarray] = []
    static_prediction_values: list[np.ndarray] = []
    adaptive_prediction_values: list[np.ndarray] = []

    for batch in selected_batches:
        static_dir = static_batches[selected_epoch][batch]
        adaptive_dir = adaptive_batches[selected_epoch][batch]
        static_maps = load_maps(static_dir)
        adaptive_maps = load_maps(adaptive_dir)
        if static_maps["prediction"].shape != adaptive_maps["prediction"].shape:
            missing_notes.append(f"Shape mismatch for {batch}; skipped.")
            continue
        if static_maps["target"].shape != adaptive_maps["target"].shape:
            missing_notes.append(f"Target shape mismatch for {batch}; skipped.")
            continue
        if not np.allclose(static_maps["target"], adaptive_maps["target"]):
            missing_notes.append(f"Targets differ numerically for {batch}; using each model's own target.")

        steps = static_maps["prediction"].shape[1]
        if static_counts is None:
            static_counts = empty_counts(steps)
            adaptive_counts = empty_counts(steps)

        add_counts(
            static_counts,
            prediction=static_maps["prediction"],
            target=static_maps["target"],
            wet_threshold=args.wet_threshold,
        )
        add_counts(
            adaptive_counts,
            prediction=adaptive_maps["prediction"],
            target=adaptive_maps["target"],
            wet_threshold=args.wet_threshold,
        )
        target_values.append(static_maps["target"].reshape(-1))
        static_prediction_values.append(static_maps["prediction"].reshape(-1))
        adaptive_prediction_values.append(adaptive_maps["prediction"].reshape(-1))
        used_artifacts.append(
            {
                "batch": batch,
                "static_forecast_maps": display_path(static_dir / "forecast_maps.npz"),
                "adapt010_forecast_maps": display_path(adaptive_dir / "forecast_maps.npz"),
                "static_summary": display_path(static_dir / "summary.json") if (static_dir / "summary.json").exists() else "MISSING",
                "adapt010_summary": display_path(adaptive_dir / "summary.json") if (adaptive_dir / "summary.json").exists() else "MISSING",
                "static_depth_timeseries": display_path(static_dir / "depth_timeseries.json")
                if (static_dir / "depth_timeseries.json").exists()
                else "MISSING",
                "adapt010_depth_timeseries": display_path(adaptive_dir / "depth_timeseries.json")
                if (adaptive_dir / "depth_timeseries.json").exists()
                else "MISSING",
            }
        )

    if static_counts is None or adaptive_counts is None:
        static_rows: list[dict[str, Any]] = []
        adaptive_rows: list[dict[str, Any]] = []
        tradeoff_summary = None
        margin_summary = {
            "seed_label": args.seed_label,
            "wet_threshold": args.wet_threshold,
            "near_threshold_margin": args.near_threshold_margin,
            "status": "no_paired_arrays_available",
        }
    else:
        static_rows = finalize_counts("static_af025", static_counts)
        adaptive_rows = finalize_counts("adapt010", adaptive_counts)
        margin_summary = {
            "seed_label": args.seed_label,
            "wet_threshold": args.wet_threshold,
            "near_threshold_margin": args.near_threshold_margin,
            "selected_epoch": selected_epoch,
            "selected_batches": selected_batches,
            "used_artifacts": used_artifacts,
            "target": summarize_margin(np.concatenate(target_values), args.wet_threshold, args.near_threshold_margin),
            "static_af025_prediction": summarize_margin(
                np.concatenate(static_prediction_values), args.wet_threshold, args.near_threshold_margin
            ),
            "adapt010_prediction": summarize_margin(
                np.concatenate(adaptive_prediction_values), args.wet_threshold, args.near_threshold_margin
            ),
        }
        tradeoff_summary = summarize_tradeoff(static_rows, adaptive_rows, margin_summary)

    output_dir.mkdir(parents=True, exist_ok=True)
    write_confusion_csv(static_rows + adaptive_rows, output_dir / "wet_dry_confusion_by_step.csv")
    (output_dir / "wet_dry_threshold_margin.json").write_text(
        json.dumps(margin_summary, indent=2),
        encoding="utf-8",
    )
    (output_dir / "wet_dry_step_highlights.json").write_text(
        json.dumps(
            {
                "seed_label": args.seed_label,
                "selected_epoch": selected_epoch,
                "selected_batches": selected_batches,
                "tradeoff_summary": tradeoff_summary,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    write_markdown(
        output_path=output_dir / "wet_dry_iou_tradeoff_summary.md",
        seed_label=args.seed_label,
        static_run_root=static_run_root,
        adaptive_run_root=adaptive_run_root,
        selected_epoch=selected_epoch,
        selected_batches=selected_batches,
        used_artifacts=used_artifacts,
        missing_notes=missing_notes,
        tradeoff_summary=tradeoff_summary,
        wet_threshold=args.wet_threshold,
        near_threshold_margin=args.near_threshold_margin,
        static_rows=static_rows,
        adaptive_rows=adaptive_rows,
    )

    print(f"Wrote CSV: {display_path(output_dir / 'wet_dry_confusion_by_step.csv')}")
    print(f"Wrote JSON: {display_path(output_dir / 'wet_dry_threshold_margin.json')}")
    print(f"Wrote JSON: {display_path(output_dir / 'wet_dry_step_highlights.json')}")
    print(f"Wrote Markdown: {display_path(output_dir / 'wet_dry_iou_tradeoff_summary.md')}")
    if used_artifacts:
        print("Used forecast artifacts:")
        for artifact in used_artifacts:
            print(f"- {artifact['batch']}: {artifact['static_forecast_maps']} | {artifact['adapt010_forecast_maps']}")


if __name__ == "__main__":
    main()
