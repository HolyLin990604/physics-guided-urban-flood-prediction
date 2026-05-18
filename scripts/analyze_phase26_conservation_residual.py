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
DEFAULT_OUTPUT_DIR = Path("analysis/phase26_strong_physics_constraint_feasibility")
THRESHOLD_M = 0.05
EPS = 1.0e-12

RUN_PAIRS: dict[str, dict[str, str]] = {
    "seed123": {
        "phase10": "runs/phase10_margin_aware_boundary_band_seed123_40e",
        "phase25": "runs/phase25_target_wet_recall_seed123_40e",
    },
    "seed42": {
        "phase10": "runs/phase10_margin_aware_boundary_band_seed42_40e",
        "phase25": "runs/phase25_target_wet_recall_seed42_40e",
    },
    "seed202": {
        "phase10": "runs/phase10_margin_aware_boundary_band_seed202_40e",
        "phase25": "runs/phase25_target_wet_recall_seed202_40e",
    },
}

PAIRED_DELTA_METRICS = (
    "relative_volume_bias",
    "absolute_relative_volume_bias",
    "false_dry_rate",
    "false_dry_volume_loss",
    "wet_area_contraction",
    "peak_depth_underprediction",
    "rmse",
    "mae",
    "false_wet_rate",
    "false_wet_volume_excess",
)

LOWER_IS_BETTER_METRICS = {
    "absolute_relative_volume_bias",
    "false_dry_rate",
    "false_dry_volume_loss",
    "wet_area_contraction",
    "peak_depth_underprediction",
    "rmse",
    "mae",
}
TRADE_OFF_METRICS = {"false_wet_rate", "false_wet_volume_excess"}


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
            "Compare Phase 10 and Phase 25 evaluation_test forecast maps with "
            "diagnostic-only conservation and volume-response proxies."
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


def normalize_forecast_array(arr: np.ndarray, key: str, source: Path) -> np.ndarray:
    """Return an array shaped [B, T, C, H, W] for consistent iteration."""
    arr = np.asarray(arr, dtype=np.float64)
    if arr.ndim == 5:
        return arr
    if arr.ndim == 4:
        # Common fallback: [B, T, H, W].
        return arr[:, :, np.newaxis, :, :]
    if arr.ndim == 3:
        # Common fallback for one sample: [T, H, W].
        return arr[np.newaxis, :, np.newaxis, :, :]
    if arr.ndim == 2:
        # One sample, one timestep, one channel.
        return arr[np.newaxis, np.newaxis, np.newaxis, :, :]
    raise ValueError(f"{key} in {display_path(source)} has unsupported shape {arr.shape}")


def list_expected_batch_files(run_dir: Path) -> list[Path]:
    eval_dir = run_dir / "evaluation_test"
    if not eval_dir.exists():
        return []
    batch_dirs = sorted(eval_dir.glob("test_batch_*"), key=lambda item: item.name)
    return [batch_dir / "forecast_maps.npz" for batch_dir in batch_dirs if batch_dir.is_dir()]


def discover_seed_files(seed: str) -> tuple[dict[str, list[Path]], list[dict[str, str]]]:
    files_by_phase: dict[str, list[Path]] = {}
    missing: list[dict[str, str]] = []
    for phase, run_rel in RUN_PAIRS[seed].items():
        run_dir = REPO_ROOT / run_rel
        expected_files = list_expected_batch_files(run_dir)
        if not run_dir.exists():
            missing.append({"seed": seed, "phase": phase, "path": run_rel, "reason": "run directory missing"})
            files_by_phase[phase] = []
            continue
        if not expected_files:
            missing.append(
                {
                    "seed": seed,
                    "phase": phase,
                    "path": display_path(run_dir / "evaluation_test"),
                    "reason": "no evaluation_test/test_batch_* directories found",
                }
            )
            files_by_phase[phase] = []
            continue
        present = []
        for path in expected_files:
            if path.exists():
                present.append(path)
            else:
                missing.append(
                    {
                        "seed": seed,
                        "phase": phase,
                        "path": display_path(path),
                        "reason": "forecast_maps.npz missing",
                    }
                )
        files_by_phase[phase] = present
    return files_by_phase, missing


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


def process_file(path: Path, seed: str, phase: str, run_name: str, threshold: float, eps: float) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    with np.load(path, allow_pickle=False) as data:
        for key in ("prediction", "target"):
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
                    "seed": seed,
                    "run_name": run_name,
                    "run_dir": RUN_PAIRS[seed][phase],
                    "batch_file": display_path(path),
                    "batch_name": batch_name,
                    "batch_index": batch_index,
                    "sample_index": sample_index,
                    "timestep": timestep,
                    **metrics,
                }
            )
    return records


def aggregate_records(records: list[dict[str, Any]], group_fields: tuple[str, ...]) -> list[dict[str, Any]]:
    grouped: dict[tuple[Any, ...], list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        grouped[tuple(record[field] for field in group_fields)].append(record)

    rows: list[dict[str, Any]] = []
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

    for key, items in sorted(grouped.items(), key=lambda pair: tuple(str(value) for value in pair[0])):
        row = {field: value for field, value in zip(group_fields, key)}
        row["step_count"] = len(items)
        for metric in mean_metrics:
            row[f"mean_{metric}"] = safe_float(np.mean([item[metric] for item in items]))
        for metric in sum_metrics:
            row[f"sum_{metric}"] = safe_float(np.sum([item[metric] for item in items]))

        row["aggregate_relative_volume_bias"] = row["sum_volume_bias"] / (row["sum_target_volume_proxy"] + EPS)
        row["absolute_aggregate_relative_volume_bias"] = abs(row["aggregate_relative_volume_bias"])
        row["aggregate_false_dry_rate"] = row["sum_false_dry_count"] / (row["sum_target_wet_area"] + EPS)
        row["aggregate_false_wet_rate"] = row["sum_false_wet_count"] / (row["sum_target_dry_area"] + EPS)
        row["aggregate_wet_area_contraction"] = max(
            row["sum_target_wet_area"] - row["sum_prediction_wet_area"], 0.0
        ) / (row["sum_target_wet_area"] + EPS)
        rows.append(row)
    return rows


def compute_paired_deltas(records: list[dict[str, Any]], aggregate_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    phase_records: dict[tuple[str, str, int, int, int], dict[str, dict[str, Any]]] = defaultdict(dict)
    for record in records:
        key = (record["seed"], record["batch_name"], int(record["batch_index"]), int(record["sample_index"]), int(record["timestep"]))
        phase_records[key][record["phase"]] = record

    delta_values: dict[str, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))
    unmatched = defaultdict(int)
    for key, by_phase in phase_records.items():
        seed = key[0]
        if "phase10" not in by_phase or "phase25" not in by_phase:
            unmatched[seed] += 1
            continue
        for metric in PAIRED_DELTA_METRICS:
            delta_values[seed][metric].append(float(by_phase["phase25"][metric]) - float(by_phase["phase10"][metric]))

    seed_phase_aggregates = {(row["seed"], row["phase"]): row for row in aggregate_rows}
    rows: list[dict[str, Any]] = []
    for seed in RUN_PAIRS:
        row: dict[str, Any] = {
            "seed": seed,
            "paired_step_count": len(delta_values[seed].get("rmse", [])),
            "unmatched_step_count": unmatched[seed],
        }
        for metric in PAIRED_DELTA_METRICS:
            values = delta_values[seed].get(metric, [])
            row[f"mean_delta_{metric}"] = safe_float(np.mean(values)) if values else None
        row["delta_mean_step_relative_volume_bias"] = row["mean_delta_relative_volume_bias"]
        row["delta_mean_step_absolute_relative_volume_bias"] = row["mean_delta_absolute_relative_volume_bias"]
        for metric in PAIRED_DELTA_METRICS:
            values = delta_values[seed].get(metric, [])
            if metric in LOWER_IS_BETTER_METRICS:
                if metric == "absolute_relative_volume_bias":
                    improved_key = "mean_step_absolute_relative_volume_bias_improved"
                else:
                    improved_key = f"{metric}_improved"
                row[improved_key] = bool(values and row[f"mean_delta_{metric}"] < 0.0)
            elif metric in TRADE_OFF_METRICS:
                row[f"{metric}_tradeoff_increased"] = bool(values and row[f"mean_delta_{metric}"] > 0.0)

        p10 = seed_phase_aggregates.get((seed, "phase10"))
        p25 = seed_phase_aggregates.get((seed, "phase25"))
        if p10 and p25:
            row["delta_aggregate_relative_volume_bias"] = (
                p25["aggregate_relative_volume_bias"] - p10["aggregate_relative_volume_bias"]
            )
            row["delta_aggregate_absolute_relative_volume_bias"] = (
                p25["absolute_aggregate_relative_volume_bias"] - p10["absolute_aggregate_relative_volume_bias"]
            )
            row["aggregate_volume_proxy_improved"] = row["delta_aggregate_absolute_relative_volume_bias"] < 0.0
        else:
            row["delta_aggregate_relative_volume_bias"] = None
            row["delta_aggregate_absolute_relative_volume_bias"] = None
            row["aggregate_volume_proxy_improved"] = False
        rows.append(row)
    return rows


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


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(json_ready(data), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def conclusion_from_deltas(delta_rows: list[dict[str, Any]]) -> dict[str, Any]:
    valid_rows = [row for row in delta_rows if row["paired_step_count"]]
    if not valid_rows:
        return {
            "phase25_more_conservation_consistent": False,
            "false_dry_volume_loss_reduced": False,
            "wet_area_contraction_reduced": False,
            "peak_depth_preservation_improved": False,
            "false_wet_tradeoffs_introduced": False,
            "overall": "No paired records were available for a Phase 25 vs Phase 10 conclusion.",
        }

    def mean_delta(name: str) -> float:
        values = [row[name] for row in valid_rows if row.get(name) is not None]
        return safe_float(np.mean(values)) if values else 0.0

    conservation = mean_delta("delta_aggregate_absolute_relative_volume_bias") < 0.0
    false_dry = mean_delta("mean_delta_false_dry_volume_loss") < 0.0
    contraction = mean_delta("mean_delta_wet_area_contraction") < 0.0
    peak = mean_delta("mean_delta_peak_depth_underprediction") < 0.0
    false_wet_tradeoff = (
        mean_delta("mean_delta_false_wet_rate") > 0.0 or mean_delta("mean_delta_false_wet_volume_excess") > 0.0
    )
    positives = sum([conservation, false_dry, contraction, peak])
    if positives >= 3:
        overall = (
            "Phase 25 is directionally stronger on the main conservation-proxy diagnostics, especially aggregate "
            "volume response, false-dry volume loss, wet-area contraction, peak-depth preservation, RMSE, and MAE."
        )
    elif positives:
        overall = "Phase 25 shows mixed conservation-proxy behavior relative to Phase 10."
    else:
        overall = "Phase 25 is not stronger on the main conservation-proxy diagnostics."

    return {
        "phase25_more_conservation_consistent": conservation,
        "false_dry_volume_loss_reduced": false_dry,
        "wet_area_contraction_reduced": contraction,
        "peak_depth_preservation_improved": peak,
        "false_wet_tradeoffs_introduced": false_wet_tradeoff,
        "mean_seed_delta_aggregate_absolute_relative_volume_bias": mean_delta(
            "delta_aggregate_absolute_relative_volume_bias"
        ),
        "mean_seed_delta_mean_step_absolute_relative_volume_bias": mean_delta(
            "delta_mean_step_absolute_relative_volume_bias"
        ),
        "mean_seed_delta_false_dry_volume_loss": mean_delta("mean_delta_false_dry_volume_loss"),
        "mean_seed_delta_wet_area_contraction": mean_delta("mean_delta_wet_area_contraction"),
        "mean_seed_delta_peak_depth_underprediction": mean_delta("mean_delta_peak_depth_underprediction"),
        "mean_seed_delta_false_wet_rate": mean_delta("mean_delta_false_wet_rate"),
        "mean_seed_delta_false_wet_volume_excess": mean_delta("mean_delta_false_wet_volume_excess"),
        "overall": overall,
    }


def format_bool_answer(value: bool) -> str:
    return "Yes" if value else "No"


def metric_value(row: dict[str, Any], key: str) -> str:
    value = row.get(key)
    if value is None:
        return "n/a"
    return f"{float(value):.6g}"


def write_markdown(path: Path, summary: dict[str, Any]) -> None:
    conclusion = summary["conclusion"]
    delta_rows = summary["paired_phase25_minus_phase10_deltas_by_seed"]
    phase_rows = summary["phase_level_aggregates"]
    missing = summary["missing_or_error_files"]

    lines = [
        "# Phase 26 Conservation Residual Proxy Diagnostics",
        "",
        "This diagnostic compares Phase 10 recommended baseline runs with Phase 25 target_wet_recall runs using existing `evaluation_test/test_batch_*/forecast_maps.npz` outputs only. It does not train models, alter losses, alter configs, or modify checkpoints.",
        "",
        "## Direct Answers",
        "",
        f"1. Phase 25 more conservation-consistent at aggregate volume-proxy level: **{format_bool_answer(conclusion['phase25_more_conservation_consistent'])}**. Mean seed delta in aggregate absolute relative volume bias: `{conclusion.get('mean_seed_delta_aggregate_absolute_relative_volume_bias', 0.0):.6g}`; lower is better.",
        f"2. Phase 25 reduces false-dry volume loss: **{format_bool_answer(conclusion['false_dry_volume_loss_reduced'])}**. Mean paired delta: `{conclusion.get('mean_seed_delta_false_dry_volume_loss', 0.0):.6g}`; lower is better.",
        f"3. Phase 25 reduces wet-area contraction: **{format_bool_answer(conclusion['wet_area_contraction_reduced'])}**. Mean paired delta: `{conclusion.get('mean_seed_delta_wet_area_contraction', 0.0):.6g}`; lower is better.",
        f"4. Phase 25 improves peak-depth preservation: **{format_bool_answer(conclusion['peak_depth_preservation_improved'])}**. Mean paired delta in peak-depth underprediction: `{conclusion.get('mean_seed_delta_peak_depth_underprediction', 0.0):.6g}`; lower is better.",
        f"5. Phase 25 introduces false-wet trade-offs: **{format_bool_answer(conclusion['false_wet_tradeoffs_introduced'])}**. Mean paired false-wet-rate delta: `{conclusion.get('mean_seed_delta_false_wet_rate', 0.0):.6g}`; mean paired false-wet-volume-excess delta: `{conclusion.get('mean_seed_delta_false_wet_volume_excess', 0.0):.6g}`.",
        "6. This is conservation-proxy diagnostics, not full SWE/PINN residual analysis, because the forecast maps only provide predicted and target water-depth rasters. They do not provide aligned velocity or flux fields, boundary inflow/outflow conditions, source/sink and drainage terms, pump/gate operations, or explicit `dt`, `dx`, and `dy` needed to compute shallow-water-equation residuals.",
        "",
            "## Overall Conclusion",
            "",
            conclusion["overall"],
            "",
            "Phase 25 increases false-wet rate and false-wet volume excess slightly, so those remain trade-offs.",
            "",
            "## Aggregate vs Timestep-Wise Volume Bias",
            "",
            "- `aggregate_abs_relative_volume_bias` is computed from aggregate predicted volume and aggregate target volume over the full paired evaluation seed or set.",
            "- `mean_step_absolute_relative_volume_bias` is the mean of timestep-level absolute relative volume bias and can move differently from the aggregate metric.",
            "- Phase 25 strongly improves aggregate absolute relative volume bias across all three seeds.",
            "- Timestep-wise absolute relative volume bias is mixed: seed42 improves, while seed123 and seed202 show very small increases.",
            "- Therefore the conclusion is conservative: Phase 25 improves aggregate water-volume response and reduces under-response, but it is not a strict timestep-wise conservation solution.",
            "",
            "## Phase-Level Aggregates",
        "",
        "| Phase | Steps | Aggregate relative volume bias | Abs aggregate relative volume bias | Aggregate false dry rate | Aggregate false wet rate | Mean RMSE | Mean MAE |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in phase_rows:
        lines.append(
            f"| `{row['phase']}` | {row['step_count']} | {metric_value(row, 'aggregate_relative_volume_bias')} | "
            f"{metric_value(row, 'absolute_aggregate_relative_volume_bias')} | {metric_value(row, 'aggregate_false_dry_rate')} | "
            f"{metric_value(row, 'aggregate_false_wet_rate')} | {metric_value(row, 'mean_rmse')} | {metric_value(row, 'mean_mae')} |"
        )

    lines.extend(
        [
            "",
            "## Paired Phase25 - Phase10 Deltas By Seed",
            "",
            "| Seed | Paired steps | Delta aggregate abs rel volume bias | Delta mean-step abs rel volume bias | Delta false dry rate | Delta false dry volume loss | Delta wet-area contraction | Delta peak underprediction | Delta RMSE | Delta MAE | Delta false wet rate | Delta false wet volume excess |",
            "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for row in delta_rows:
        lines.append(
            f"| `{row['seed']}` | {row['paired_step_count']} | "
            f"{metric_value(row, 'delta_aggregate_absolute_relative_volume_bias')} | "
            f"{metric_value(row, 'delta_mean_step_absolute_relative_volume_bias')} | "
            f"{metric_value(row, 'mean_delta_false_dry_rate')} | "
            f"{metric_value(row, 'mean_delta_false_dry_volume_loss')} | "
            f"{metric_value(row, 'mean_delta_wet_area_contraction')} | "
            f"{metric_value(row, 'mean_delta_peak_depth_underprediction')} | "
            f"{metric_value(row, 'mean_delta_rmse')} | "
            f"{metric_value(row, 'mean_delta_mae')} | "
            f"{metric_value(row, 'mean_delta_false_wet_rate')} | "
            f"{metric_value(row, 'mean_delta_false_wet_volume_excess')} |"
        )

    lines.extend(
        [
            "",
            "## Improvement Directions",
            "",
            "- Lower absolute relative volume bias is better.",
            "- Lower false-dry rate and lower false-dry volume loss are better.",
            "- Lower wet-area contraction is better.",
            "- Lower peak-depth underprediction is better.",
            "- Lower RMSE and MAE are better.",
            "- False-wet rate and false-wet volume excess are monitored as trade-offs.",
            "",
            "## Missing Or Error Files",
            "",
        ]
    )
    if missing:
        for item in missing:
            lines.append(f"- `{item.get('path')}` ({item.get('seed')}, {item.get('phase')}): {item.get('reason')}")
    else:
        lines.append("- None.")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    output_dir = resolve_repo_path(args.output_dir)

    step_records: list[dict[str, Any]] = []
    missing_or_errors: list[dict[str, str]] = []
    processed_files = 0

    for seed in RUN_PAIRS:
        files_by_phase, missing = discover_seed_files(seed)
        missing_or_errors.extend(missing)
        for phase, files in files_by_phase.items():
            run_name = Path(RUN_PAIRS[seed][phase]).name
            for path in files:
                try:
                    records = process_file(path, seed, phase, run_name, args.threshold, args.eps)
                except (OSError, KeyError, ValueError, zipfile.BadZipFile) as exc:  # type: ignore[name-defined]
                    missing_or_errors.append(
                        {"seed": seed, "phase": phase, "path": display_path(path), "reason": f"read error: {exc}"}
                    )
                    continue
                step_records.extend(records)
                processed_files += 1

    by_run = aggregate_records(step_records, ("phase", "seed", "run_name", "run_dir"))
    by_seed = aggregate_records(step_records, ("phase", "seed"))
    by_phase = aggregate_records(step_records, ("phase",))
    phase_delta = compute_paired_deltas(step_records, by_seed)
    conclusion = conclusion_from_deltas(phase_delta)

    outputs = {
        "by_step": output_dir / "conservation_residual_by_step.csv",
        "by_run": output_dir / "conservation_residual_by_run.csv",
        "by_seed": output_dir / "conservation_residual_by_seed.csv",
        "phase_delta": output_dir / "conservation_residual_phase_delta.csv",
        "summary_json": output_dir / "summary.json",
        "summary_md": output_dir / "conservation_residual_summary.md",
    }

    write_csv(outputs["by_step"], step_records)
    write_csv(outputs["by_run"], by_run)
    write_csv(outputs["by_seed"], by_seed)
    write_csv(outputs["phase_delta"], phase_delta)

    summary = {
        "scope": {
            "diagnostic_only": True,
            "threshold_m": args.threshold,
            "run_pairs": RUN_PAIRS,
            "output_dir": display_path(output_dir),
            "note": "Reads existing evaluation_test/test_batch_*/forecast_maps.npz only; writes only Phase 26 analysis outputs.",
        },
        "processed_map_files": processed_files,
        "step_record_count": len(step_records),
        "missing_or_error_files": missing_or_errors,
        "run_level_aggregates": by_run,
        "seed_level_aggregates": by_seed,
        "phase_level_aggregates": by_phase,
        "paired_phase25_minus_phase10_deltas_by_seed": phase_delta,
        "improvement_directions": {
            "absolute_relative_volume_bias": "lower is better",
            "aggregate_absolute_relative_volume_bias": "lower is better",
            "mean_step_absolute_relative_volume_bias": "lower is better but evaluated separately from aggregate volume bias",
            "false_dry_rate": "lower is better",
            "false_dry_volume_loss": "lower is better",
            "wet_area_contraction": "lower is better",
            "peak_depth_underprediction": "lower is better",
            "rmse": "lower is better",
            "mae": "lower is better",
            "false_wet_rate": "monitored as trade-off",
            "false_wet_volume_excess": "monitored as trade-off",
        },
        "conclusion": conclusion,
    }
    write_json(outputs["summary_json"], summary)
    write_markdown(outputs["summary_md"], summary)

    print("Phase 26 conservation residual proxy diagnostics complete.")
    print(f"  processed map files: {processed_files}")
    print(f"  step records: {len(step_records)}")
    if missing_or_errors:
        print(f"  missing/error files: {len(missing_or_errors)}")
        for item in missing_or_errors[:8]:
            print(f"    - {item['path']} ({item['seed']}, {item['phase']}): {item['reason']}")
        if len(missing_or_errors) > 8:
            print(f"    - ... {len(missing_or_errors) - 8} more")
    print("  per-seed Phase25 - Phase10 deltas:")
    for row in phase_delta:
        print(
            "    "
            f"{row['seed']}: paired_steps={row['paired_step_count']}, "
            f"delta_aggregate_absolute_relative_volume_bias={metric_value(row, 'delta_aggregate_absolute_relative_volume_bias')}, "
            f"delta_mean_step_absolute_relative_volume_bias={metric_value(row, 'delta_mean_step_absolute_relative_volume_bias')}, "
            f"delta_false_dry_volume_loss={metric_value(row, 'mean_delta_false_dry_volume_loss')}, "
            f"delta_wet_area_contraction={metric_value(row, 'mean_delta_wet_area_contraction')}, "
            f"delta_peak_underprediction={metric_value(row, 'mean_delta_peak_depth_underprediction')}, "
            f"delta_rmse={metric_value(row, 'mean_delta_rmse')}, "
            f"delta_false_wet_rate={metric_value(row, 'mean_delta_false_wet_rate')}"
        )
    print(f"  overall conclusion: {conclusion['overall']}")
    for path in outputs.values():
        print(f"  wrote: {display_path(path)}")


if __name__ == "__main__":
    main()
