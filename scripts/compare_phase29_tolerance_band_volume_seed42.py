from __future__ import annotations

import argparse
import csv
import json
import math
import zipfile
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np


REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = Path("analysis/phase29_tolerance_band_volume_consistency")
THRESHOLD_M = 0.05
EPS = 1.0e-12

RUNS: dict[str, str] = {
    "phase25": "runs/phase25_target_wet_recall_seed42_40e",
    "phase27": "runs/phase27_volume_response_seed42_40e",
    "phase29": "runs/phase29_tolerance_band_volume_seed42_40e",
}

STANDARD_METRICS = (
    "rmse",
    "mae",
    "wet_dry_iou",
    "rollout_stability",
    "step_rmse_std",
)

RUN_DELTA_METRICS = (
    "metrics_json_rmse",
    "metrics_json_mae",
    "metrics_json_wet_dry_iou",
    "metrics_json_rollout_stability",
    "metrics_json_step_rmse_std",
    "aggregate_relative_volume_bias",
    "aggregate_absolute_relative_volume_bias",
    "mean_step_relative_volume_bias",
    "mean_step_absolute_relative_volume_bias",
    "false_dry_rate",
    "false_dry_volume_loss",
    "false_wet_rate",
    "false_wet_volume_excess",
    "wet_area_contraction",
    "peak_depth_underprediction",
    "rmse_from_maps",
    "mae_from_maps",
)

DEPTH_BINS = (
    ("dry_or_threshold", -math.inf, THRESHOLD_M),
    ("shallow", THRESHOLD_M, 0.15),
    ("moderate", 0.15, 0.30),
    ("deep", 0.30, math.inf),
)

LOWER_IS_BETTER = {
    "metrics_json_rmse",
    "metrics_json_mae",
    "metrics_json_step_rmse_std",
    "aggregate_absolute_relative_volume_bias",
    "mean_step_absolute_relative_volume_bias",
    "false_dry_rate",
    "false_dry_volume_loss",
    "false_wet_rate",
    "false_wet_volume_excess",
    "wet_area_contraction",
    "peak_depth_underprediction",
    "rmse_from_maps",
    "mae_from_maps",
}
HIGHER_IS_BETTER = {"metrics_json_wet_dry_iou", "metrics_json_rollout_stability"}


def display_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT)).replace("\\", "/")
    except ValueError:
        return str(path)


def resolve_repo_path(path: Path) -> Path:
    return path if path.is_absolute() else REPO_ROOT / path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Diagnostic-only Phase 29 tolerance-band volume consistency comparison "
            "against Phase 25 and Phase 27 seed42 test outputs."
        )
    )
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    parser.add_argument("--threshold", type=float, default=THRESHOLD_M)
    parser.add_argument("--eps", type=float, default=EPS)
    return parser.parse_args()


def safe_float(value: Any) -> float:
    number = float(value)
    if math.isnan(number) or math.isinf(number):
        return 0.0
    return number


def json_ready(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): json_ready(item) for key, item in value.items()}
    if isinstance(value, list):
        return [json_ready(item) for item in value]
    if isinstance(value, tuple):
        return [json_ready(item) for item in value]
    if isinstance(value, np.generic):
        return value.item()
    return value


def metric_text(value: Any) -> str:
    if value is None or value == "":
        return "n/a"
    return f"{float(value):.6g}"


def yes_no(value: bool) -> str:
    return "Yes" if value else "No"


def normalize_forecast_array(arr: np.ndarray, key: str, source: Path) -> np.ndarray:
    arr = np.asarray(arr, dtype=np.float64)
    if arr.ndim == 5:
        return arr
    if arr.ndim == 4:
        return arr[:, :, np.newaxis, :, :]
    if arr.ndim == 3:
        return arr[np.newaxis, :, np.newaxis, :, :]
    if arr.ndim == 2:
        return arr[np.newaxis, np.newaxis, np.newaxis, :, :]
    raise ValueError(f"{key} in {display_path(source)} has unsupported shape {arr.shape}")


def list_forecast_files(run_dir: Path) -> list[Path]:
    eval_dir = run_dir / "evaluation_test"
    if not eval_dir.exists():
        return []
    return [
        batch_dir / "forecast_maps.npz"
        for batch_dir in sorted(eval_dir.glob("test_batch_*"), key=lambda item: item.name)
        if batch_dir.is_dir()
    ]


def read_metrics_json(run_dir: Path) -> dict[str, float]:
    path = run_dir / "evaluation_test" / "metrics.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Expected JSON object in {display_path(path)}")
    return {key: safe_float(data[key]) for key in STANDARD_METRICS if key in data}


def target_depth_bin_masks(target: np.ndarray, threshold: float) -> list[tuple[str, np.ndarray]]:
    bins = (
        ("dry_or_threshold", target <= threshold),
        ("shallow", (target > threshold) & (target <= 0.15)),
        ("moderate", (target > 0.15) & (target <= 0.30)),
        ("deep", target > 0.30),
    )
    return [(name, np.asarray(mask, dtype=bool)) for name, mask in bins]


def compute_step_metrics(prediction: np.ndarray, target: np.ndarray, threshold: float, eps: float) -> dict[str, Any]:
    prediction = np.where(np.isfinite(prediction), prediction, 0.0)
    target = np.where(np.isfinite(target), target, 0.0)
    diff = prediction - target
    prediction_positive = np.maximum(prediction, 0.0)
    target_positive = np.maximum(target, 0.0)

    target_volume = safe_float(target_positive.sum())
    prediction_volume = safe_float(prediction_positive.sum())
    volume_bias = prediction_volume - target_volume

    target_wet = target > threshold
    prediction_wet = prediction > threshold
    false_dry = target_wet & ~prediction_wet
    false_wet = ~target_wet & prediction_wet

    target_wet_area = int(target_wet.sum())
    prediction_wet_area = int(prediction_wet.sum())
    target_dry_area = int(target.size - target_wet_area)
    false_dry_count = int(false_dry.sum())
    false_wet_count = int(false_wet.sum())

    peak_target = safe_float(target.max()) if target.size else 0.0
    peak_prediction = safe_float(prediction.max()) if prediction.size else 0.0
    sum_sq_error = safe_float(np.square(diff, dtype=np.float64).sum())
    sum_abs_error = safe_float(np.abs(diff).sum())
    pixel_count = int(diff.size)

    return {
        "pixel_count": pixel_count,
        "sum_sq_error": sum_sq_error,
        "sum_abs_error": sum_abs_error,
        "target_volume_proxy": target_volume,
        "prediction_volume_proxy": prediction_volume,
        "volume_bias": volume_bias,
        "relative_volume_bias": volume_bias / (target_volume + eps),
        "absolute_relative_volume_bias": abs(volume_bias / (target_volume + eps)),
        "target_wet_area": target_wet_area,
        "prediction_wet_area": prediction_wet_area,
        "target_dry_area": target_dry_area,
        "false_dry_count": false_dry_count,
        "false_wet_count": false_wet_count,
        "false_dry_rate": false_dry_count / (target_wet_area + eps),
        "false_dry_volume_loss": safe_float(target_positive[false_dry].sum()),
        "false_wet_rate": false_wet_count / (target_dry_area + eps),
        "false_wet_volume_excess": safe_float(prediction_positive[false_wet].sum()),
        "wet_area_contraction": max(target_wet_area - prediction_wet_area, 0) / (target_wet_area + eps),
        "peak_depth_target": peak_target,
        "peak_depth_prediction": peak_prediction,
        "peak_depth_underprediction": max(peak_target - peak_prediction, 0.0),
        "rmse": math.sqrt(sum_sq_error / pixel_count) if pixel_count else 0.0,
        "mae": sum_abs_error / pixel_count if pixel_count else 0.0,
    }


def process_file(
    path: Path,
    phase: str,
    run_name: str,
    threshold: float,
    eps: float,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    with np.load(path, allow_pickle=False) as data:
        if "prediction" not in data or "target" not in data:
            raise KeyError(f"prediction or target missing from {display_path(path)}")
        prediction = normalize_forecast_array(data["prediction"], "prediction", path)
        target = normalize_forecast_array(data["target"], "target", path)

    if prediction.shape != target.shape:
        raise ValueError(
            f"prediction shape {prediction.shape} does not match target shape {target.shape} in {display_path(path)}"
        )

    batch_name = path.parent.name
    try:
        batch_index = int(batch_name.replace("test_batch_", ""))
    except ValueError:
        batch_index = -1

    step_records: list[dict[str, Any]] = []
    bin_records: list[dict[str, Any]] = []
    for sample_index in range(prediction.shape[0]):
        for timestep in range(prediction.shape[1]):
            pred_step = prediction[sample_index, timestep]
            target_step = target[sample_index, timestep]
            metrics = compute_step_metrics(pred_step, target_step, threshold, eps)
            step_key = {
                "phase": phase,
                "seed": 42,
                "run_name": run_name,
                "run_dir": RUNS[phase],
                "batch_file": display_path(path),
                "batch_name": batch_name,
                "batch_index": batch_index,
                "sample_index": sample_index,
                "timestep": timestep,
            }
            step_records.append({**step_key, **metrics})

            pred_positive = np.maximum(np.where(np.isfinite(pred_step), pred_step, 0.0), 0.0)
            target_positive = np.maximum(np.where(np.isfinite(target_step), target_step, 0.0), 0.0)
            total_predicted_volume = safe_float(pred_positive.sum())
            total_target_volume = safe_float(target_positive.sum())
            for bin_name, mask in target_depth_bin_masks(target_step, threshold):
                bin_pred_volume = safe_float(pred_positive[mask].sum())
                bin_target_volume = safe_float(target_positive[mask].sum())
                bin_records.append(
                    {
                        **step_key,
                        "target_depth_bin": bin_name,
                        "cell_count": int(mask.sum()),
                        "predicted_volume_proxy": bin_pred_volume,
                        "target_volume_proxy": bin_target_volume,
                        "predicted_volume_contribution": bin_pred_volume / (total_predicted_volume + eps),
                        "target_volume_contribution": bin_target_volume / (total_target_volume + eps),
                    }
                )
    return step_records, bin_records


def aggregate_step_records(records: list[dict[str, Any]], group_fields: tuple[str, ...], eps: float) -> list[dict[str, Any]]:
    grouped: dict[tuple[Any, ...], list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        grouped[tuple(record[field] for field in group_fields)].append(record)

    rows: list[dict[str, Any]] = []
    for key, items in sorted(grouped.items(), key=lambda pair: tuple(str(value) for value in pair[0])):
        row = {field: value for field, value in zip(group_fields, key)}
        row["step_count"] = len(items)
        row["pixel_count"] = int(sum(item["pixel_count"] for item in items))
        row["sum_sq_error"] = safe_float(sum(item["sum_sq_error"] for item in items))
        row["sum_abs_error"] = safe_float(sum(item["sum_abs_error"] for item in items))
        row["sum_target_volume_proxy"] = safe_float(sum(item["target_volume_proxy"] for item in items))
        row["sum_prediction_volume_proxy"] = safe_float(sum(item["prediction_volume_proxy"] for item in items))
        row["volume_bias"] = row["sum_prediction_volume_proxy"] - row["sum_target_volume_proxy"]
        row["aggregate_relative_volume_bias"] = row["volume_bias"] / (row["sum_target_volume_proxy"] + eps)
        row["aggregate_absolute_relative_volume_bias"] = abs(row["aggregate_relative_volume_bias"])
        row["mean_step_relative_volume_bias"] = safe_float(np.mean([item["relative_volume_bias"] for item in items]))
        row["mean_step_absolute_relative_volume_bias"] = safe_float(
            np.mean([item["absolute_relative_volume_bias"] for item in items])
        )
        row["sum_target_wet_area"] = int(sum(item["target_wet_area"] for item in items))
        row["sum_prediction_wet_area"] = int(sum(item["prediction_wet_area"] for item in items))
        row["sum_target_dry_area"] = int(sum(item["target_dry_area"] for item in items))
        row["sum_false_dry_count"] = int(sum(item["false_dry_count"] for item in items))
        row["sum_false_wet_count"] = int(sum(item["false_wet_count"] for item in items))
        row["false_dry_rate"] = row["sum_false_dry_count"] / (row["sum_target_wet_area"] + eps)
        row["false_wet_rate"] = row["sum_false_wet_count"] / (row["sum_target_dry_area"] + eps)
        row["false_dry_volume_loss"] = safe_float(sum(item["false_dry_volume_loss"] for item in items))
        row["false_wet_volume_excess"] = safe_float(sum(item["false_wet_volume_excess"] for item in items))
        row["wet_area_contraction"] = max(row["sum_target_wet_area"] - row["sum_prediction_wet_area"], 0) / (
            row["sum_target_wet_area"] + eps
        )
        row["mean_step_wet_area_contraction"] = safe_float(np.mean([item["wet_area_contraction"] for item in items]))
        row["peak_depth_underprediction"] = safe_float(np.mean([item["peak_depth_underprediction"] for item in items]))
        row["rmse_from_maps"] = math.sqrt(row["sum_sq_error"] / row["pixel_count"]) if row["pixel_count"] else 0.0
        row["mae_from_maps"] = row["sum_abs_error"] / row["pixel_count"] if row["pixel_count"] else 0.0
        rows.append(row)
    return rows


def aggregate_depth_bins(records: list[dict[str, Any]], eps: float) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        grouped[(record["phase"], record["target_depth_bin"])].append(record)

    rows: list[dict[str, Any]] = []
    for phase in RUNS:
        phase_total_pred = safe_float(
            sum(record["predicted_volume_proxy"] for record in records if record["phase"] == phase)
        )
        phase_total_target = safe_float(sum(record["target_volume_proxy"] for record in records if record["phase"] == phase))
        for bin_name, _, _ in DEPTH_BINS:
            items = grouped.get((phase, bin_name), [])
            pred_volume = safe_float(sum(item["predicted_volume_proxy"] for item in items))
            target_volume = safe_float(sum(item["target_volume_proxy"] for item in items))
            rows.append(
                {
                    "phase": phase,
                    "seed": 42,
                    "target_depth_bin": bin_name,
                    "step_count": len(items),
                    "cell_count": int(sum(item["cell_count"] for item in items)),
                    "predicted_volume_proxy": pred_volume,
                    "target_volume_proxy": target_volume,
                    "predicted_volume_contribution": pred_volume / (phase_total_pred + eps),
                    "target_volume_contribution": target_volume / (phase_total_target + eps),
                    "mean_step_predicted_volume_contribution": safe_float(
                        np.mean([item["predicted_volume_contribution"] for item in items])
                    )
                    if items
                    else 0.0,
                }
            )
    return rows


def attach_standard_metrics(by_run: list[dict[str, Any]], standard_metrics: dict[str, dict[str, float]]) -> None:
    for row in by_run:
        metrics = standard_metrics.get(row["phase"], {})
        for metric in STANDARD_METRICS:
            row[f"metrics_json_{metric}"] = metrics.get(metric, "")


def make_delta_rows(
    by_run: list[dict[str, Any]],
    baseline_phase: str,
    comparison_phase: str = "phase29",
) -> list[dict[str, Any]]:
    lookup = {row["phase"]: row for row in by_run}
    if baseline_phase not in lookup or comparison_phase not in lookup:
        return []
    base = lookup[baseline_phase]
    comp = lookup[comparison_phase]
    rows: list[dict[str, Any]] = []
    for metric in RUN_DELTA_METRICS:
        base_value = base.get(metric)
        comp_value = comp.get(metric)
        if base_value == "" or comp_value == "" or base_value is None or comp_value is None:
            continue
        delta = float(comp_value) - float(base_value)
        improved = (metric in LOWER_IS_BETTER and delta < 0.0) or (metric in HIGHER_IS_BETTER and delta > 0.0)
        rows.append(
            {
                "comparison": f"{comparison_phase}_minus_{baseline_phase}",
                "metric": metric,
                baseline_phase: base_value,
                comparison_phase: comp_value,
                "delta": delta,
                "lower_is_better": metric in LOWER_IS_BETTER,
                "higher_is_better": metric in HIGHER_IS_BETTER,
                "improved": improved,
            }
        )
    return rows


def make_context_delta_rows(by_run: list[dict[str, Any]]) -> list[dict[str, Any]]:
    lookup = {row["phase"]: row for row in by_run}
    if "phase25" not in lookup or "phase27" not in lookup:
        return []
    rows: list[dict[str, Any]] = []
    for metric in RUN_DELTA_METRICS:
        p25 = lookup["phase25"].get(metric)
        p27 = lookup["phase27"].get(metric)
        if p25 == "" or p27 == "" or p25 is None or p27 is None:
            continue
        rows.append(
            {
                "comparison": "phase27_minus_phase25",
                "metric": metric,
                "phase25": p25,
                "phase27": p27,
                "delta": float(p27) - float(p25),
            }
        )
    return rows


def build_conclusion(
    by_run: list[dict[str, Any]],
    delta_vs_phase25: list[dict[str, Any]],
    delta_vs_phase27: list[dict[str, Any]],
    depth_bins: list[dict[str, Any]],
) -> dict[str, Any]:
    run = {row["phase"]: row for row in by_run}
    d25 = {row["metric"]: row["delta"] for row in delta_vs_phase25}
    d27 = {row["metric"]: row["delta"] for row in delta_vs_phase27}
    bins = {(row["phase"], row["target_depth_bin"]): row for row in depth_bins}

    aggregate_volume_response_improved_vs_phase27 = d27.get("aggregate_absolute_relative_volume_bias", 0.0) < 0.0
    mean_step_volume_response_improved_vs_phase27 = d27.get("mean_step_absolute_relative_volume_bias", 0.0) < 0.0
    dry_threshold_reduced_vs_phase27 = (
        bins.get(("phase29", "dry_or_threshold"), {}).get("predicted_volume_contribution", 0.0)
        < bins.get(("phase27", "dry_or_threshold"), {}).get("predicted_volume_contribution", 0.0)
    )
    phase25_bias = abs(float(run.get("phase25", {}).get("aggregate_relative_volume_bias", 0.0)))
    phase29_bias = abs(float(run.get("phase29", {}).get("aggregate_relative_volume_bias", 0.0)))
    near_phase25_bias = phase29_bias <= phase25_bias + 0.005
    false_dry_loss_worse = d25.get("false_dry_volume_loss", 0.0) > 0.0 or d27.get("false_dry_volume_loss", 0.0) > 0.0
    false_wet_worse = d25.get("false_wet_rate", 0.0) > 0.0 or d25.get("false_wet_volume_excess", 0.0) > 0.0
    standard_metric_losses_vs_phase27 = [
        metric
        for metric in (
            "metrics_json_rmse",
            "metrics_json_mae",
            "metrics_json_wet_dry_iou",
            "metrics_json_rollout_stability",
            "metrics_json_step_rmse_std",
        )
        if (metric in LOWER_IS_BETTER and d27.get(metric, 0.0) > 0.0)
        or (metric in HIGHER_IS_BETTER and d27.get(metric, 0.0) < 0.0)
    ]
    standard_preserved = len(standard_metric_losses_vs_phase27) <= 1

    primary_improves_clearly = (
        aggregate_volume_response_improved_vs_phase27
        and mean_step_volume_response_improved_vs_phase27
        and dry_threshold_reduced_vs_phase27
    )

    if primary_improves_clearly and standard_preserved and not false_dry_loss_worse:
        result_label = "successful_tolerance_band_redesign_seed42"
        recommendation = "proceed_to_seed123_seed202_confirmation"
    elif primary_improves_clearly:
        result_label = "mixed_result"
        recommendation = "remain_seed42_only_pending_revision"
    else:
        result_label = "negative_result"
        recommendation = "reject_or_revise_before_more_seeds"

    if not primary_improves_clearly:
        recommendation = "reject_or_revise_before_more_seeds"

    return {
        "question_answers": {
            "phase29_improved_aggregate_volume_response_relative_to_phase27": aggregate_volume_response_improved_vs_phase27,
            "phase29_reduced_dry_or_threshold_volume_accumulation_relative_to_phase27": dry_threshold_reduced_vs_phase27,
            "phase29_remained_close_to_phase25_near_zero_aggregate_volume_bias": near_phase25_bias,
            "phase29_worsened_false_dry_volume_loss_relative_to_phase25_or_phase27": false_dry_loss_worse,
            "phase29_increased_false_wet_rate_or_volume_excess": false_wet_worse,
            "phase29_preserved_standard_metrics_well_enough": standard_preserved,
        },
        "standard_metric_losses_vs_phase27": standard_metric_losses_vs_phase27,
        "primary_volume_response_objective_improved_clearly": primary_improves_clearly,
        "result_label": result_label,
        "recommendation": recommendation,
    }


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fieldnames: list[str] = []
    for row in rows:
        for key in row:
            if key not in fieldnames:
                fieldnames.append(key)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(json_ready(data), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_markdown(path: Path, summary: dict[str, Any]) -> None:
    by_run = {row["phase"]: row for row in summary["run_level_aggregates"]}
    depth = {(row["phase"], row["target_depth_bin"]): row for row in summary["depth_bin_decomposition"]}
    d25 = {row["metric"]: row for row in summary["phase29_minus_phase25_deltas"]}
    d27 = {row["metric"]: row for row in summary["phase29_minus_phase27_deltas"]}
    qa = summary["conclusion"]["question_answers"]

    lines = [
        "# Phase 29 Seed42 Tolerance-Band Volume Consistency Diagnostic",
        "",
        "This diagnostic compares Phase 29 against Phase 25 and Phase 27 using existing test `forecast_maps.npz` and `metrics.json` artifacts only. Volume quantities are depth-raster volume proxies, not strict conservation, full mass conservation, SWE residuals, or PINN evidence.",
        "",
        "## Direct Answers",
        "",
        f"1. Did Phase 29 improve aggregate volume response relative to Phase 27? **{yes_no(qa['phase29_improved_aggregate_volume_response_relative_to_phase27'])}**. Delta aggregate absolute relative volume bias: `{metric_text(d27.get('aggregate_absolute_relative_volume_bias', {}).get('delta'))}`; lower is better.",
        f"2. Did Phase 29 reduce dry_or_threshold volume accumulation relative to Phase 27? **{yes_no(qa['phase29_reduced_dry_or_threshold_volume_accumulation_relative_to_phase27'])}**. Phase 27 contribution: `{metric_text(depth[('phase27', 'dry_or_threshold')]['predicted_volume_contribution'])}`; Phase 29 contribution: `{metric_text(depth[('phase29', 'dry_or_threshold')]['predicted_volume_contribution'])}`.",
        f"3. Did Phase 29 remain close to Phase 25's near-zero aggregate volume bias? **{yes_no(qa['phase29_remained_close_to_phase25_near_zero_aggregate_volume_bias'])}**. Phase 25 aggregate bias: `{metric_text(by_run['phase25']['aggregate_relative_volume_bias'])}`; Phase 29 aggregate bias: `{metric_text(by_run['phase29']['aggregate_relative_volume_bias'])}`.",
        f"4. Did Phase 29 worsen false-dry volume loss relative to Phase 25 or Phase 27? **{yes_no(qa['phase29_worsened_false_dry_volume_loss_relative_to_phase25_or_phase27'])}**. Delta vs Phase 25: `{metric_text(d25.get('false_dry_volume_loss', {}).get('delta'))}`; delta vs Phase 27: `{metric_text(d27.get('false_dry_volume_loss', {}).get('delta'))}`.",
        f"5. Did Phase 29 increase false-wet rate or false-wet volume excess? **{yes_no(qa['phase29_increased_false_wet_rate_or_volume_excess'])}**. False-wet-rate delta vs Phase 27: `{metric_text(d27.get('false_wet_rate', {}).get('delta'))}`; false-wet-volume delta vs Phase 27: `{metric_text(d27.get('false_wet_volume_excess', {}).get('delta'))}`.",
        f"6. Did Phase 29 preserve standard metrics well enough? **{yes_no(qa['phase29_preserved_standard_metrics_well_enough'])}**. Standard metric losses vs Phase 27: `{', '.join(summary['conclusion']['standard_metric_losses_vs_phase27']) or 'none'}`.",
        f"7. Overall result: **{summary['conclusion']['result_label']}**. Recommendation: **{summary['conclusion']['recommendation']}**.",
        "",
        "## Conservative Interpretation",
        "",
    ]

    if summary["conclusion"]["primary_volume_response_objective_improved_clearly"]:
        lines.append(
            "Phase 29 improves the primary volume-response objective on seed42 under these proxy diagnostics, subject to the listed false-dry, false-wet, and standard-metric trade-offs."
        )
    else:
        lines.append(
            "Phase 29 does not clearly improve the primary volume-response objective on seed42. Under the requested conservative rule, this should not proceed to seed123/seed202 confirmation without revision."
        )

    lines.extend(
        [
            "",
            "## Standard Metrics",
            "",
            "| Metric | Phase 25 | Phase 27 | Phase 29 | Phase29 - Phase25 | Phase29 - Phase27 |",
            "|---|---:|---:|---:|---:|---:|",
        ]
    )
    for metric in STANDARD_METRICS:
        key = f"metrics_json_{metric}"
        lines.append(
            f"| `{metric}` | {metric_text(by_run['phase25'].get(key))} | {metric_text(by_run['phase27'].get(key))} | "
            f"{metric_text(by_run['phase29'].get(key))} | {metric_text(d25.get(key, {}).get('delta'))} | "
            f"{metric_text(d27.get(key, {}).get('delta'))} |"
        )

    lines.extend(
        [
            "",
            "## Run-Level Volume Proxies",
            "",
            "| Phase | Aggregate rel. volume bias | Aggregate abs. rel. volume bias | Mean-step abs. rel. volume bias | False-dry loss | False-wet excess | False-dry rate | False-wet rate | Wet-area contraction | RMSE from maps | MAE from maps |",
            "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for phase in ("phase25", "phase27", "phase29"):
        row = by_run[phase]
        lines.append(
            f"| `{phase}` | {metric_text(row['aggregate_relative_volume_bias'])} | "
            f"{metric_text(row['aggregate_absolute_relative_volume_bias'])} | "
            f"{metric_text(row['mean_step_absolute_relative_volume_bias'])} | "
            f"{metric_text(row['false_dry_volume_loss'])} | {metric_text(row['false_wet_volume_excess'])} | "
            f"{metric_text(row['false_dry_rate'])} | {metric_text(row['false_wet_rate'])} | "
            f"{metric_text(row['wet_area_contraction'])} | {metric_text(row['rmse_from_maps'])} | "
            f"{metric_text(row['mae_from_maps'])} |"
        )

    lines.extend(
        [
            "",
            "## Target-Depth-Bin Predicted Volume Contribution",
            "",
            "| Phase | dry_or_threshold | shallow | moderate | deep |",
            "|---|---:|---:|---:|---:|",
        ]
    )
    for phase in ("phase25", "phase27", "phase29"):
        lines.append(
            f"| `{phase}` | {metric_text(depth[(phase, 'dry_or_threshold')]['predicted_volume_contribution'])} | "
            f"{metric_text(depth[(phase, 'shallow')]['predicted_volume_contribution'])} | "
            f"{metric_text(depth[(phase, 'moderate')]['predicted_volume_contribution'])} | "
            f"{metric_text(depth[(phase, 'deep')]['predicted_volume_contribution'])} |"
        )

    lines.extend(
        [
            "",
            "## Output Files",
            "",
            "- `phase29_seed42_by_step.csv`",
            "- `phase29_seed42_by_run.csv`",
            "- `phase29_seed42_delta_vs_phase25.csv`",
            "- `phase29_seed42_delta_vs_phase27.csv`",
            "- `phase29_seed42_depth_bin_decomposition.csv`",
            "- `phase29_seed42_summary.json`",
            "- `phase29_seed42_summary.md`",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    output_dir = resolve_repo_path(args.output_dir)

    step_records: list[dict[str, Any]] = []
    depth_bin_step_records: list[dict[str, Any]] = []
    standard_metrics: dict[str, dict[str, float]] = {}
    missing_or_errors: list[dict[str, str]] = []
    processed_files = 0

    for phase, run_rel in RUNS.items():
        run_dir = REPO_ROOT / run_rel
        if not run_dir.exists():
            missing_or_errors.append({"phase": phase, "path": run_rel, "reason": "run directory missing"})
            continue
        try:
            standard_metrics[phase] = read_metrics_json(run_dir)
        except (OSError, KeyError, ValueError, json.JSONDecodeError) as exc:
            missing_or_errors.append(
                {"phase": phase, "path": display_path(run_dir / "evaluation_test" / "metrics.json"), "reason": str(exc)}
            )
        for forecast_file in list_forecast_files(run_dir):
            try:
                new_steps, new_bins = process_file(forecast_file, phase, run_dir.name, args.threshold, args.eps)
                step_records.extend(new_steps)
                depth_bin_step_records.extend(new_bins)
                processed_files += 1
            except (OSError, KeyError, ValueError, zipfile.BadZipFile) as exc:
                missing_or_errors.append(
                    {"phase": phase, "path": display_path(forecast_file), "reason": f"read error: {exc}"}
                )

    by_run = aggregate_step_records(step_records, ("phase", "seed", "run_name", "run_dir"), args.eps)
    attach_standard_metrics(by_run, standard_metrics)
    depth_bins = aggregate_depth_bins(depth_bin_step_records, args.eps)
    delta_vs_phase25 = make_delta_rows(by_run, "phase25")
    delta_vs_phase27 = make_delta_rows(by_run, "phase27")
    context_delta = make_context_delta_rows(by_run)
    conclusion = build_conclusion(by_run, delta_vs_phase25, delta_vs_phase27, depth_bins)

    outputs = {
        "by_step": output_dir / "phase29_seed42_by_step.csv",
        "by_run": output_dir / "phase29_seed42_by_run.csv",
        "delta_vs_phase25": output_dir / "phase29_seed42_delta_vs_phase25.csv",
        "delta_vs_phase27": output_dir / "phase29_seed42_delta_vs_phase27.csv",
        "depth_bins": output_dir / "phase29_seed42_depth_bin_decomposition.csv",
        "summary_json": output_dir / "phase29_seed42_summary.json",
        "summary_md": output_dir / "phase29_seed42_summary.md",
    }

    write_csv(outputs["by_step"], step_records)
    write_csv(outputs["by_run"], by_run)
    write_csv(outputs["delta_vs_phase25"], delta_vs_phase25 + context_delta)
    write_csv(outputs["delta_vs_phase27"], delta_vs_phase27)
    write_csv(outputs["depth_bins"], depth_bins)

    summary = {
        "scope": {
            "diagnostic_only": True,
            "threshold_m": args.threshold,
            "eps": args.eps,
            "runs": RUNS,
            "output_dir": display_path(output_dir),
            "note": "Reads only existing evaluation_test/test_batch_*/forecast_maps.npz and metrics.json files.",
        },
        "processed_map_files": processed_files,
        "step_record_count": len(step_records),
        "missing_or_error_files": missing_or_errors,
        "standard_metrics": standard_metrics,
        "run_level_aggregates": by_run,
        "phase29_minus_phase25_deltas": delta_vs_phase25,
        "phase29_minus_phase27_deltas": delta_vs_phase27,
        "phase27_minus_phase25_context_deltas": context_delta,
        "depth_bin_decomposition": depth_bins,
        "conclusion": conclusion,
    }
    write_json(outputs["summary_json"], summary)
    write_markdown(outputs["summary_md"], summary)

    print("Phase 29 seed42 tolerance-band volume consistency diagnostic complete.")
    print(f"  processed map files: {processed_files}")
    print(f"  step records: {len(step_records)}")
    if missing_or_errors:
        print(f"  missing/error files: {len(missing_or_errors)}")
    print(f"  recommendation: {conclusion['recommendation']}")
    for path in outputs.values():
        print(f"  wrote: {display_path(path)}")


if __name__ == "__main__":
    main()
