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
DEFAULT_OUTPUT_DIR = Path("analysis/phase27_conservative_volume_response_consistency")
THRESHOLD_M = 0.05
EPS = 1.0e-12

RUNS: dict[str, str] = {
    "phase25": "runs/phase25_target_wet_recall_seed42_40e",
    "phase27": "runs/phase27_volume_response_seed42_40e",
}

STANDARD_METRICS = (
    "rmse",
    "mae",
    "wet_dry_iou",
    "rollout_stability",
    "step_rmse_std",
)

PAIRED_DELTA_METRICS = (
    "relative_volume_bias",
    "absolute_relative_volume_bias",
    "false_dry_rate",
    "false_wet_rate",
    "false_dry_volume_loss",
    "false_wet_volume_excess",
    "wet_area_contraction",
    "peak_depth_underprediction",
    "rmse",
    "mae",
)

LOWER_IS_BETTER_STANDARD = {"rmse", "mae", "step_rmse_std"}
HIGHER_IS_BETTER_STANDARD = {"wet_dry_iou", "rollout_stability"}


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
            "Diagnostic-only comparison of Phase 27 conservative volume-response seed42 "
            "against the Phase 25 target-wet recall seed42 baseline. Reads existing "
            "evaluation_test/test_batch_*/forecast_maps.npz and metrics.json files only."
        )
    )
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
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


def metric_value(row: dict[str, Any], key: str) -> str:
    value = row.get(key)
    if value is None:
        return "n/a"
    return f"{float(value):.6g}"


def yes_no(value: bool) -> str:
    return "Yes" if value else "No"


def normalize_forecast_array(arr: np.ndarray, key: str, source: Path) -> np.ndarray:
    """Return an array shaped [B, T, C, H, W] for consistent iteration."""
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
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"Expected JSON object in {display_path(path)}")
    return {key: safe_float(data[key]) for key in STANDARD_METRICS if key in data}


def compute_step_metrics(
    prediction: np.ndarray,
    target: np.ndarray,
    threshold: float,
    eps: float,
) -> dict[str, float | int]:
    prediction = np.where(np.isfinite(prediction), prediction, 0.0)
    target = np.where(np.isfinite(target), target, 0.0)
    diff = prediction - target

    target_positive = np.maximum(target, 0.0)
    prediction_positive = np.maximum(prediction, 0.0)
    target_volume_proxy = safe_float(np.sum(target_positive))
    prediction_volume_proxy = safe_float(np.sum(prediction_positive))
    volume_bias = prediction_volume_proxy - target_volume_proxy
    relative_volume_bias = volume_bias / (target_volume_proxy + eps)

    target_wet_mask = target > threshold
    prediction_wet_mask = prediction > threshold
    target_wet_area = int(np.count_nonzero(target_wet_mask))
    prediction_wet_area = int(np.count_nonzero(prediction_wet_mask))
    total_area = int(target.size)
    target_dry_area = total_area - target_wet_area

    false_dry_mask = target_wet_mask & ~prediction_wet_mask
    false_wet_mask = ~target_wet_mask & prediction_wet_mask
    false_dry_count = int(np.count_nonzero(false_dry_mask))
    false_wet_count = int(np.count_nonzero(false_wet_mask))

    peak_depth_target = safe_float(np.max(target)) if target.size else 0.0
    peak_depth_prediction = safe_float(np.max(prediction)) if prediction.size else 0.0

    return {
        "target_volume_proxy": target_volume_proxy,
        "prediction_volume_proxy": prediction_volume_proxy,
        "volume_bias": volume_bias,
        "relative_volume_bias": relative_volume_bias,
        "absolute_relative_volume_bias": abs(relative_volume_bias),
        "target_wet_area": target_wet_area,
        "prediction_wet_area": prediction_wet_area,
        "target_dry_area": target_dry_area,
        "wet_area_bias": prediction_wet_area - target_wet_area,
        "wet_area_contraction": max(target_wet_area - prediction_wet_area, 0) / (target_wet_area + eps),
        "false_dry_count": false_dry_count,
        "false_wet_count": false_wet_count,
        "false_dry_rate": false_dry_count / (target_wet_area + eps),
        "false_wet_rate": false_wet_count / (target_dry_area + eps),
        "false_dry_volume_loss": safe_float(np.sum(target[false_dry_mask])),
        "false_wet_volume_excess": safe_float(np.sum(prediction[false_wet_mask])),
        "peak_depth_target": peak_depth_target,
        "peak_depth_prediction": peak_depth_prediction,
        "peak_depth_underprediction": max(peak_depth_target - peak_depth_prediction, 0.0),
        "rmse": safe_float(np.sqrt(np.mean(diff * diff))),
        "mae": safe_float(np.mean(np.abs(diff))),
    }


def process_file(path: Path, phase: str, run_name: str, threshold: float, eps: float) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    with np.load(path, allow_pickle=False) as data:
        for key in ("prediction", "target", "error"):
            if key not in data:
                raise KeyError(f"{key} missing from {display_path(path)}")
        prediction = normalize_forecast_array(data["prediction"], "prediction", path)
        target = normalize_forecast_array(data["target"], "target", path)

    if prediction.shape != target.shape:
        raise ValueError(
            f"prediction shape {prediction.shape} does not match target shape {target.shape} in {display_path(path)}"
        )

    batch_name = path.parent.name
    batch_index_text = batch_name.replace("test_batch_", "")
    try:
        batch_index = int(batch_index_text)
    except ValueError:
        batch_index = -1

    for sample_index in range(prediction.shape[0]):
        for timestep in range(prediction.shape[1]):
            metrics = compute_step_metrics(prediction[sample_index, timestep], target[sample_index, timestep], threshold, eps)
            records.append(
                {
                    "phase": phase,
                    "seed": 42,
                    "run_name": run_name,
                    "run_dir": RUNS[phase],
                    "batch_file": display_path(path),
                    "batch_name": batch_name,
                    "batch_index": batch_index,
                    "sample_index": sample_index,
                    "timestep": timestep,
                    **metrics,
                }
            )
    return records


def aggregate_records(records: list[dict[str, Any]], group_fields: tuple[str, ...], eps: float) -> list[dict[str, Any]]:
    grouped: dict[tuple[Any, ...], list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        grouped[tuple(record[field] for field in group_fields)].append(record)

    mean_metrics = (
        "target_volume_proxy",
        "prediction_volume_proxy",
        "volume_bias",
        "relative_volume_bias",
        "absolute_relative_volume_bias",
        "target_wet_area",
        "prediction_wet_area",
        "target_dry_area",
        "wet_area_bias",
        "wet_area_contraction",
        "false_dry_rate",
        "false_wet_rate",
        "false_dry_volume_loss",
        "false_wet_volume_excess",
        "peak_depth_target",
        "peak_depth_prediction",
        "peak_depth_underprediction",
        "rmse",
        "mae",
    )
    sum_metrics = (
        "target_volume_proxy",
        "prediction_volume_proxy",
        "volume_bias",
        "target_wet_area",
        "prediction_wet_area",
        "target_dry_area",
        "false_dry_count",
        "false_wet_count",
        "false_dry_volume_loss",
        "false_wet_volume_excess",
    )

    rows: list[dict[str, Any]] = []
    for key, items in sorted(grouped.items(), key=lambda pair: tuple(str(value) for value in pair[0])):
        row = {field: value for field, value in zip(group_fields, key)}
        row["step_count"] = len(items)
        for metric in mean_metrics:
            row[f"mean_{metric}"] = safe_float(np.mean([item[metric] for item in items]))
        for metric in sum_metrics:
            row[f"sum_{metric}"] = safe_float(np.sum([item[metric] for item in items]))

        row["aggregate_relative_volume_bias"] = row["sum_volume_bias"] / (row["sum_target_volume_proxy"] + eps)
        row["aggregate_absolute_relative_volume_bias"] = abs(row["aggregate_relative_volume_bias"])
        row["mean_step_relative_volume_bias"] = row["mean_relative_volume_bias"]
        row["mean_step_absolute_relative_volume_bias"] = row["mean_absolute_relative_volume_bias"]
        row["aggregate_false_dry_rate"] = row["sum_false_dry_count"] / (row["sum_target_wet_area"] + eps)
        row["aggregate_false_wet_rate"] = row["sum_false_wet_count"] / (row["sum_target_dry_area"] + eps)
        row["aggregate_wet_area_contraction"] = max(
            row["sum_target_wet_area"] - row["sum_prediction_wet_area"], 0.0
        ) / (row["sum_target_wet_area"] + eps)
        rows.append(row)
    return rows


def compute_paired_delta_rows(records: list[dict[str, Any]], by_run: list[dict[str, Any]]) -> list[dict[str, Any]]:
    phase_records: dict[tuple[str, int, int, int], dict[str, dict[str, Any]]] = defaultdict(dict)
    for record in records:
        key = (
            str(record["batch_name"]),
            int(record["batch_index"]),
            int(record["sample_index"]),
            int(record["timestep"]),
        )
        phase_records[key][record["phase"]] = record

    delta_rows: list[dict[str, Any]] = []
    for key, by_phase in sorted(phase_records.items()):
        if "phase25" not in by_phase or "phase27" not in by_phase:
            continue
        batch_name, batch_index, sample_index, timestep = key
        row: dict[str, Any] = {
            "seed": 42,
            "batch_name": batch_name,
            "batch_index": batch_index,
            "sample_index": sample_index,
            "timestep": timestep,
        }
        for metric in PAIRED_DELTA_METRICS:
            row[f"phase25_{metric}"] = by_phase["phase25"][metric]
            row[f"phase27_{metric}"] = by_phase["phase27"][metric]
            row[f"delta_{metric}"] = float(by_phase["phase27"][metric]) - float(by_phase["phase25"][metric])
        delta_rows.append(row)

    run_lookup = {row["phase"]: row for row in by_run}
    if "phase25" in run_lookup and "phase27" in run_lookup:
        p25 = run_lookup["phase25"]
        p27 = run_lookup["phase27"]
        aggregate_row = {
            "seed": 42,
            "batch_name": "__aggregate__",
            "batch_index": -1,
            "sample_index": -1,
            "timestep": -1,
            "phase25_aggregate_relative_volume_bias": p25["aggregate_relative_volume_bias"],
            "phase27_aggregate_relative_volume_bias": p27["aggregate_relative_volume_bias"],
            "delta_aggregate_relative_volume_bias": (
                p27["aggregate_relative_volume_bias"] - p25["aggregate_relative_volume_bias"]
            ),
            "phase25_aggregate_absolute_relative_volume_bias": p25["aggregate_absolute_relative_volume_bias"],
            "phase27_aggregate_absolute_relative_volume_bias": p27["aggregate_absolute_relative_volume_bias"],
            "delta_aggregate_absolute_relative_volume_bias": (
                p27["aggregate_absolute_relative_volume_bias"] - p25["aggregate_absolute_relative_volume_bias"]
            ),
            "phase25_mean_step_relative_volume_bias": p25["mean_step_relative_volume_bias"],
            "phase27_mean_step_relative_volume_bias": p27["mean_step_relative_volume_bias"],
            "delta_mean_step_relative_volume_bias": (
                p27["mean_step_relative_volume_bias"] - p25["mean_step_relative_volume_bias"]
            ),
            "phase25_mean_step_absolute_relative_volume_bias": p25["mean_step_absolute_relative_volume_bias"],
            "phase27_mean_step_absolute_relative_volume_bias": p27["mean_step_absolute_relative_volume_bias"],
            "delta_mean_step_absolute_relative_volume_bias": (
                p27["mean_step_absolute_relative_volume_bias"] - p25["mean_step_absolute_relative_volume_bias"]
            ),
        }
        delta_rows.append(aggregate_row)
    return delta_rows


def summarize_deltas(delta_rows: list[dict[str, Any]], by_run: list[dict[str, Any]]) -> dict[str, Any]:
    paired = [row for row in delta_rows if row.get("batch_name") != "__aggregate__"]
    summary: dict[str, Any] = {"paired_step_count": len(paired)}
    for metric in PAIRED_DELTA_METRICS:
        values = [row[f"delta_{metric}"] for row in paired]
        summary[f"mean_delta_{metric}"] = safe_float(np.mean(values)) if values else None

    run_lookup = {row["phase"]: row for row in by_run}
    if "phase25" in run_lookup and "phase27" in run_lookup:
        p25 = run_lookup["phase25"]
        p27 = run_lookup["phase27"]
        for metric in (
            "aggregate_relative_volume_bias",
            "aggregate_absolute_relative_volume_bias",
            "mean_step_relative_volume_bias",
            "mean_step_absolute_relative_volume_bias",
            "aggregate_false_dry_rate",
            "aggregate_false_wet_rate",
            "aggregate_wet_area_contraction",
        ):
            summary[f"phase25_{metric}"] = p25[metric]
            summary[f"phase27_{metric}"] = p27[metric]
            summary[f"delta_{metric}"] = p27[metric] - p25[metric]
    return summary


def standard_metric_deltas(phase_metrics: dict[str, dict[str, float]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for metric in STANDARD_METRICS:
        phase25 = phase_metrics.get("phase25", {}).get(metric)
        phase27 = phase_metrics.get("phase27", {}).get(metric)
        if phase25 is None or phase27 is None:
            continue
        delta = phase27 - phase25
        improved = (delta < 0.0 and metric in LOWER_IS_BETTER_STANDARD) or (
            delta > 0.0 and metric in HIGHER_IS_BETTER_STANDARD
        )
        rows.append(
            {
                "metric": metric,
                "phase25": phase25,
                "phase27": phase27,
                "delta_phase27_minus_phase25": delta,
                "improved": improved,
            }
        )
    return rows


def build_conclusion(delta_summary: dict[str, Any], standard_deltas: list[dict[str, Any]]) -> dict[str, Any]:
    standard_improved = all(row["improved"] for row in standard_deltas) if standard_deltas else False
    aggregate_volume_improved = delta_summary.get("delta_aggregate_absolute_relative_volume_bias", 0.0) < 0.0
    timestep_volume_improved = delta_summary.get("delta_mean_step_absolute_relative_volume_bias", 0.0) < 0.0
    false_dry_loss_reduced = delta_summary.get("mean_delta_false_dry_volume_loss", 0.0) < 0.0
    wet_area_contraction_reduced = delta_summary.get("mean_delta_wet_area_contraction", 0.0) < 0.0
    peak_preservation_improved = delta_summary.get("mean_delta_peak_depth_underprediction", 0.0) < 0.0
    false_wet_increased = (
        delta_summary.get("mean_delta_false_wet_rate", 0.0) > 0.0
        or delta_summary.get("mean_delta_false_wet_volume_excess", 0.0) > 0.0
    )
    core_volume_improved = aggregate_volume_improved and timestep_volume_improved
    support_metrics_improved = sum(
        [
            false_dry_loss_reduced,
            wet_area_contraction_reduced,
            peak_preservation_improved,
        ]
    )
    false_wet_driven_over_expansion = false_wet_increased and not (
        core_volume_improved and false_dry_loss_reduced and peak_preservation_improved
    )

    if standard_improved and core_volume_improved and support_metrics_improved >= 2 and not false_wet_driven_over_expansion:
        recommendation = "proceed_to_seed123_seed202_confirmation"
    elif standard_improved or support_metrics_improved >= 2:
        recommendation = "remain_seed42_positive_only"
    else:
        recommendation = "reject"

    if recommendation == "proceed_to_seed123_seed202_confirmation":
        overall = (
            "Phase 27 is seed42-positive on standard metrics and the main volume-response proxies. "
            "The false-wet increase should be treated as a trade-off and checked on seed123/seed202."
        )
    elif recommendation == "remain_seed42_positive_only":
        overall = (
            "Phase 27 is mixed on seed42: standard metrics and several under-response proxies improve, "
            "but aggregate and timestep-wise absolute relative volume bias do not. It should remain "
            "seed42-positive only rather than being treated as confirmed volume-response progress."
        )
    else:
        overall = "Phase 27 does not show enough seed42 evidence for this diagnostic and should be rejected."

    return {
        "standard_metrics_improved": standard_improved,
        "aggregate_volume_response_improved": aggregate_volume_improved,
        "timestep_absolute_relative_volume_bias_improved": timestep_volume_improved,
        "false_dry_volume_loss_reduced": false_dry_loss_reduced,
        "wet_area_contraction_reduced": wet_area_contraction_reduced,
        "peak_depth_preservation_improved": peak_preservation_improved,
        "false_wet_tradeoff_increased": false_wet_increased,
        "false_wet_driven_over_expansion": false_wet_driven_over_expansion,
        "recommendation": recommendation,
        "overall": overall,
    }


def volume_response_label(conclusion: dict[str, Any]) -> str:
    if conclusion["false_wet_driven_over_expansion"]:
        return "False-wet-driven over-expansion risk"
    if (
        conclusion["aggregate_volume_response_improved"]
        and conclusion["timestep_absolute_relative_volume_bias_improved"]
    ):
        return "Genuine seed42 volume-response improvement with any false-wet change treated as a trade-off"
    return "Mixed seed42 result; not a confirmed conservative volume-response improvement"


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
        for row in rows:
            writer.writerow(row)


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(json_ready(data), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_markdown(path: Path, summary: dict[str, Any]) -> None:
    conclusion = summary["conclusion"]
    delta_summary = summary["paired_phase27_minus_phase25_delta_summary"]
    by_run = {row["phase"]: row for row in summary["run_level_aggregates"]}
    standard_deltas = summary["standard_metric_deltas"]

    lines = [
        "# Phase 27 Seed42 Conservative Volume-Response Diagnostic",
        "",
        "This diagnostic compares Phase 27 against the Phase 25 seed42 baseline using existing `evaluation_test/test_batch_*/forecast_maps.npz` and `metrics.json` outputs only. It does not train, alter architecture, alter losses, alter configs, or claim full mass conservation.",
        "",
        "## Direct Answers",
        "",
        f"1. Does Phase 27 improve standard metrics over Phase 25 seed42? **{yes_no(conclusion['standard_metrics_improved'])}**. All listed standard metrics move in the preferred direction.",
        f"2. Does Phase 27 improve aggregate volume response? **{yes_no(conclusion['aggregate_volume_response_improved'])}**. Delta aggregate absolute relative volume bias: `{delta_summary.get('delta_aggregate_absolute_relative_volume_bias', 0.0):.6g}`; lower is better.",
        f"3. Does Phase 27 improve or worsen timestep-wise absolute relative volume bias? **{'Improve' if conclusion['timestep_absolute_relative_volume_bias_improved'] else 'Worsen'}**. Delta mean-step absolute relative volume bias: `{delta_summary.get('delta_mean_step_absolute_relative_volume_bias', 0.0):.6g}`; lower is better.",
        f"4. Does Phase 27 reduce false-dry volume loss? **{yes_no(conclusion['false_dry_volume_loss_reduced'])}**. Mean paired delta: `{delta_summary.get('mean_delta_false_dry_volume_loss', 0.0):.6g}`; lower is better.",
        f"5. Does Phase 27 reduce wet-area contraction? **{yes_no(conclusion['wet_area_contraction_reduced'])}**. Mean paired delta: `{delta_summary.get('mean_delta_wet_area_contraction', 0.0):.6g}`; lower is better.",
        f"6. Does Phase 27 improve peak-depth preservation? **{yes_no(conclusion['peak_depth_preservation_improved'])}**. Mean paired delta in peak-depth underprediction: `{delta_summary.get('mean_delta_peak_depth_underprediction', 0.0):.6g}`; lower is better.",
        f"7. Does Phase 27 increase false-wet rate or false-wet volume excess? **{yes_no(conclusion['false_wet_tradeoff_increased'])}**. False-wet-rate delta: `{delta_summary.get('mean_delta_false_wet_rate', 0.0):.6g}`; false-wet-volume-excess delta: `{delta_summary.get('mean_delta_false_wet_volume_excess', 0.0):.6g}`.",
        f"8. Is the result a genuine conservative volume-response improvement or a false-wet-driven over-expansion? **{volume_response_label(conclusion)}**.",
        f"9. Should Phase 27 proceed? **{conclusion['recommendation']}**.",
        "",
        "## Conservative Conclusion",
        "",
        conclusion["overall"],
        "",
        "This is a volume-response proxy diagnostic from depth rasters. It is not a full mass-conservation, SWE, or PINN residual analysis, and it does not establish strict timestep-wise conservation.",
        "",
        "## Standard Metrics",
        "",
        "| Metric | Phase 25 | Phase 27 | Delta Phase27 - Phase25 | Improved |",
        "|---|---:|---:|---:|---|",
    ]
    for row in standard_deltas:
        lines.append(
            f"| `{row['metric']}` | {row['phase25']:.12g} | {row['phase27']:.12g} | "
            f"{row['delta_phase27_minus_phase25']:.12g} | {yes_no(row['improved'])} |"
        )

    lines.extend(
        [
            "",
            "## Run-Level Volume Metrics",
            "",
            "| Phase | Steps | Aggregate relative volume bias | Aggregate absolute relative volume bias | Mean-step relative volume bias | Mean-step absolute relative volume bias | Aggregate wet-area contraction | Aggregate false dry rate | Aggregate false wet rate | Mean false-dry volume loss | Mean false-wet volume excess | Mean peak underprediction |",
            "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for phase in ("phase25", "phase27"):
        row = by_run[phase]
        lines.append(
            f"| `{phase}` | {row['step_count']} | {metric_value(row, 'aggregate_relative_volume_bias')} | "
            f"{metric_value(row, 'aggregate_absolute_relative_volume_bias')} | "
            f"{metric_value(row, 'mean_step_relative_volume_bias')} | "
            f"{metric_value(row, 'mean_step_absolute_relative_volume_bias')} | "
            f"{metric_value(row, 'aggregate_wet_area_contraction')} | "
            f"{metric_value(row, 'aggregate_false_dry_rate')} | "
            f"{metric_value(row, 'aggregate_false_wet_rate')} | "
            f"{metric_value(row, 'mean_false_dry_volume_loss')} | "
            f"{metric_value(row, 'mean_false_wet_volume_excess')} | "
            f"{metric_value(row, 'mean_peak_depth_underprediction')} |"
        )

    lines.extend(
        [
            "",
            "## Paired Phase27 - Phase25 Delta Summary",
            "",
            "| Metric | Mean paired delta | Direction |",
            "|---|---:|---|",
            f"| `absolute_relative_volume_bias` | {metric_value(delta_summary, 'mean_delta_absolute_relative_volume_bias')} | lower is better |",
            f"| `false_dry_volume_loss` | {metric_value(delta_summary, 'mean_delta_false_dry_volume_loss')} | lower is better |",
            f"| `wet_area_contraction` | {metric_value(delta_summary, 'mean_delta_wet_area_contraction')} | lower is better |",
            f"| `peak_depth_underprediction` | {metric_value(delta_summary, 'mean_delta_peak_depth_underprediction')} | lower is better |",
            f"| `rmse` | {metric_value(delta_summary, 'mean_delta_rmse')} | lower is better |",
            f"| `mae` | {metric_value(delta_summary, 'mean_delta_mae')} | lower is better |",
            f"| `false_wet_rate` | {metric_value(delta_summary, 'mean_delta_false_wet_rate')} | trade-off monitor |",
            f"| `false_wet_volume_excess` | {metric_value(delta_summary, 'mean_delta_false_wet_volume_excess')} | trade-off monitor |",
            "",
            "## Outputs",
            "",
            "- `phase27_seed42_by_step.csv`",
            "- `phase27_seed42_by_run.csv`",
            "- `phase27_seed42_delta.csv`",
            "- `phase27_seed42_summary.json`",
            "- `phase27_seed42_summary.md`",
        ]
    )

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    output_dir = resolve_repo_path(args.output_dir)

    step_records: list[dict[str, Any]] = []
    missing_or_errors: list[dict[str, str]] = []
    standard_metrics: dict[str, dict[str, float]] = {}
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

        forecast_files = list_forecast_files(run_dir)
        if not forecast_files:
            missing_or_errors.append(
                {"phase": phase, "path": display_path(run_dir / "evaluation_test"), "reason": "no test_batch files found"}
            )
            continue
        for forecast_file in forecast_files:
            if not forecast_file.exists():
                missing_or_errors.append(
                    {"phase": phase, "path": display_path(forecast_file), "reason": "forecast_maps.npz missing"}
                )
                continue
            try:
                step_records.extend(process_file(forecast_file, phase, run_dir.name, args.threshold, args.eps))
                processed_files += 1
            except (OSError, KeyError, ValueError, zipfile.BadZipFile) as exc:
                missing_or_errors.append(
                    {"phase": phase, "path": display_path(forecast_file), "reason": f"read error: {exc}"}
                )

    by_run = aggregate_records(step_records, ("phase", "seed", "run_name", "run_dir"), args.eps)
    delta_rows = compute_paired_delta_rows(step_records, by_run)
    delta_summary = summarize_deltas(delta_rows, by_run)
    standard_deltas = standard_metric_deltas(standard_metrics)
    conclusion = build_conclusion(delta_summary, standard_deltas)

    outputs = {
        "by_step": output_dir / "phase27_seed42_by_step.csv",
        "by_run": output_dir / "phase27_seed42_by_run.csv",
        "delta": output_dir / "phase27_seed42_delta.csv",
        "summary_json": output_dir / "phase27_seed42_summary.json",
        "summary_md": output_dir / "phase27_seed42_summary.md",
    }
    write_csv(outputs["by_step"], step_records)
    write_csv(outputs["by_run"], by_run)
    write_csv(outputs["delta"], delta_rows)

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
        "standard_metric_deltas": standard_deltas,
        "run_level_aggregates": by_run,
        "paired_phase27_minus_phase25_delta_summary": delta_summary,
        "conclusion": conclusion,
    }
    write_json(outputs["summary_json"], summary)
    write_markdown(outputs["summary_md"], summary)

    print("Phase 27 seed42 volume-response diagnostic complete.")
    print(f"  processed map files: {processed_files}")
    print(f"  step records: {len(step_records)}")
    print(f"  paired steps: {delta_summary.get('paired_step_count', 0)}")
    if missing_or_errors:
        print(f"  missing/error files: {len(missing_or_errors)}")
        for item in missing_or_errors[:8]:
            print(f"    - {item['path']} ({item['phase']}): {item['reason']}")
        if len(missing_or_errors) > 8:
            print(f"    - ... {len(missing_or_errors) - 8} more")
    print("  key Phase27 - Phase25 deltas:")
    print(f"    standard rmse: {next((metric_value(row, 'delta_phase27_minus_phase25') for row in standard_deltas if row['metric'] == 'rmse'), 'n/a')}")
    print(
        "    aggregate_absolute_relative_volume_bias: "
        f"{metric_value(delta_summary, 'delta_aggregate_absolute_relative_volume_bias')}"
    )
    print(
        "    mean_step_absolute_relative_volume_bias: "
        f"{metric_value(delta_summary, 'delta_mean_step_absolute_relative_volume_bias')}"
    )
    print(f"    false_dry_volume_loss: {metric_value(delta_summary, 'mean_delta_false_dry_volume_loss')}")
    print(f"    wet_area_contraction: {metric_value(delta_summary, 'mean_delta_wet_area_contraction')}")
    print(f"    peak_depth_underprediction: {metric_value(delta_summary, 'mean_delta_peak_depth_underprediction')}")
    print(f"    false_wet_rate: {metric_value(delta_summary, 'mean_delta_false_wet_rate')}")
    print(f"    false_wet_volume_excess: {metric_value(delta_summary, 'mean_delta_false_wet_volume_excess')}")
    print(f"  recommendation: {conclusion['recommendation']}")
    for path in outputs.values():
        print(f"  wrote: {display_path(path)}")


if __name__ == "__main__":
    main()
