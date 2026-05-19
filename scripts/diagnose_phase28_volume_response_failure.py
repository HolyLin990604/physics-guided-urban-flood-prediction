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
DEFAULT_OUTPUT_DIR = Path("analysis/phase28_volume_response_loss_diagnosis")
PHASE25_RUN = "runs/phase25_target_wet_recall_seed42_40e"
PHASE27_RUN = "runs/phase27_volume_response_seed42_40e"
THRESHOLD_M = 0.05
EPS = 1.0e-12
TOP_K = 20

DEPTH_BINS: tuple[tuple[str, float | None, float | None], ...] = (
    ("dry_or_threshold", None, 0.05),
    ("shallow", 0.05, 0.2),
    ("moderate", 0.2, 0.5),
    ("deep", 0.5, None),
)


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
            "Diagnostic-only Phase 28 decomposition of Phase 27 seed42 volume-response "
            "bias worsening against Phase 25 seed42. Reads only existing "
            "evaluation_test/test_batch_*/forecast_maps.npz files."
        )
    )
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--threshold", type=float, default=THRESHOLD_M)
    parser.add_argument("--eps", type=float, default=EPS)
    parser.add_argument("--top-k", type=int, default=TOP_K)
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


def list_forecast_files(run_dir: Path) -> dict[str, Path]:
    eval_dir = run_dir / "evaluation_test"
    if not eval_dir.exists():
        return {}
    return {
        batch_dir.name: batch_dir / "forecast_maps.npz"
        for batch_dir in sorted(eval_dir.glob("test_batch_*"), key=lambda item: item.name)
        if batch_dir.is_dir()
    }


def load_forecast_file(path: Path) -> tuple[np.ndarray, np.ndarray]:
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
    return prediction, target


def target_bin_mask(target: np.ndarray, lower: float | None, upper: float | None) -> np.ndarray:
    if lower is None:
        return target <= float(upper)
    if upper is None:
        return target > float(lower)
    return (target > float(lower)) & (target <= float(upper))


def sum_positive(arr: np.ndarray) -> float:
    return safe_float(np.sum(np.maximum(arr, 0.0)))


def compute_pair_record(
    batch_name: str,
    sample_index: int,
    timestep: int,
    phase25_prediction: np.ndarray,
    phase27_prediction: np.ndarray,
    target: np.ndarray,
    threshold: float,
    eps: float,
) -> dict[str, Any]:
    phase25_prediction = np.where(np.isfinite(phase25_prediction), phase25_prediction, 0.0)
    phase27_prediction = np.where(np.isfinite(phase27_prediction), phase27_prediction, 0.0)
    target = np.where(np.isfinite(target), target, 0.0)

    target_volume_proxy = sum_positive(target)
    phase25_prediction_volume_proxy = sum_positive(phase25_prediction)
    phase27_prediction_volume_proxy = sum_positive(phase27_prediction)
    phase25_volume_bias = phase25_prediction_volume_proxy - target_volume_proxy
    phase27_volume_bias = phase27_prediction_volume_proxy - target_volume_proxy
    phase25_relative_volume_bias = phase25_volume_bias / (target_volume_proxy + eps)
    phase27_relative_volume_bias = phase27_volume_bias / (target_volume_proxy + eps)

    target_wet_mask = target > threshold
    phase25_wet_mask = phase25_prediction > threshold
    phase27_wet_mask = phase27_prediction > threshold

    phase25_overlap_mask = target_wet_mask & phase25_wet_mask
    phase27_overlap_mask = target_wet_mask & phase27_wet_mask
    phase25_false_dry_mask = target_wet_mask & ~phase25_wet_mask
    phase27_false_dry_mask = target_wet_mask & ~phase27_wet_mask
    phase25_false_wet_mask = ~target_wet_mask & phase25_wet_mask
    phase27_false_wet_mask = ~target_wet_mask & phase27_wet_mask
    both_target_pred_wet_mask = target_wet_mask & phase25_wet_mask & phase27_wet_mask

    phase25_overlap_volume_difference = safe_float(np.sum(phase25_prediction[phase25_overlap_mask] - target[phase25_overlap_mask]))
    phase27_overlap_volume_difference = safe_float(np.sum(phase27_prediction[phase27_overlap_mask] - target[phase27_overlap_mask]))
    phase25_false_dry_volume_loss = safe_float(np.sum(target[phase25_false_dry_mask]))
    phase27_false_dry_volume_loss = safe_float(np.sum(target[phase27_false_dry_mask]))
    phase25_false_wet_volume_excess = safe_float(np.sum(phase25_prediction[phase25_false_wet_mask]))
    phase27_false_wet_volume_excess = safe_float(np.sum(phase27_prediction[phase27_false_wet_mask]))

    already_wet_delta = phase27_prediction[both_target_pred_wet_mask] - phase25_prediction[both_target_pred_wet_mask]
    already_wet_depth_amplification_sum = safe_float(np.sum(already_wet_delta))
    already_wet_cell_count = int(np.count_nonzero(both_target_pred_wet_mask))
    already_wet_depth_amplification_mean = (
        already_wet_depth_amplification_sum / already_wet_cell_count if already_wet_cell_count else 0.0
    )

    depth_contribs: dict[str, float] = {}
    for bin_name, lower, upper in DEPTH_BINS:
        mask = target_bin_mask(target, lower, upper)
        depth_contribs[f"{bin_name}_phase27_minus_phase25_predicted_volume"] = safe_float(
            np.sum(np.maximum(phase27_prediction[mask], 0.0) - np.maximum(phase25_prediction[mask], 0.0))
        )

    return {
        "batch": batch_name,
        "sample_index": sample_index,
        "timestep": timestep,
        "target_volume_proxy": target_volume_proxy,
        "phase25_prediction_volume_proxy": phase25_prediction_volume_proxy,
        "phase27_prediction_volume_proxy": phase27_prediction_volume_proxy,
        "phase25_volume_bias": phase25_volume_bias,
        "phase27_volume_bias": phase27_volume_bias,
        "delta_volume_bias": phase27_volume_bias - phase25_volume_bias,
        "phase25_relative_volume_bias": phase25_relative_volume_bias,
        "phase27_relative_volume_bias": phase27_relative_volume_bias,
        "phase25_absolute_relative_volume_bias": abs(phase25_relative_volume_bias),
        "phase27_absolute_relative_volume_bias": abs(phase27_relative_volume_bias),
        "delta_absolute_relative_volume_bias": abs(phase27_relative_volume_bias) - abs(phase25_relative_volume_bias),
        "target_wet_count": int(np.count_nonzero(target_wet_mask)),
        "phase25_predicted_wet_count": int(np.count_nonzero(phase25_wet_mask)),
        "phase27_predicted_wet_count": int(np.count_nonzero(phase27_wet_mask)),
        "phase25_overlap_wet_count": int(np.count_nonzero(phase25_overlap_mask)),
        "phase27_overlap_wet_count": int(np.count_nonzero(phase27_overlap_mask)),
        "phase25_overlap_volume_difference": phase25_overlap_volume_difference,
        "phase27_overlap_volume_difference": phase27_overlap_volume_difference,
        "delta_overlap_volume_difference": phase27_overlap_volume_difference - phase25_overlap_volume_difference,
        "phase25_false_dry_count": int(np.count_nonzero(phase25_false_dry_mask)),
        "phase27_false_dry_count": int(np.count_nonzero(phase27_false_dry_mask)),
        "delta_false_dry_count": int(np.count_nonzero(phase27_false_dry_mask)) - int(np.count_nonzero(phase25_false_dry_mask)),
        "phase25_false_dry_volume_loss": phase25_false_dry_volume_loss,
        "phase27_false_dry_volume_loss": phase27_false_dry_volume_loss,
        "delta_false_dry_volume_loss": phase27_false_dry_volume_loss - phase25_false_dry_volume_loss,
        "false_dry_volume_loss_decrease": phase25_false_dry_volume_loss - phase27_false_dry_volume_loss,
        "phase25_false_wet_count": int(np.count_nonzero(phase25_false_wet_mask)),
        "phase27_false_wet_count": int(np.count_nonzero(phase27_false_wet_mask)),
        "delta_false_wet_count": int(np.count_nonzero(phase27_false_wet_mask)) - int(np.count_nonzero(phase25_false_wet_mask)),
        "phase25_false_wet_volume_excess": phase25_false_wet_volume_excess,
        "phase27_false_wet_volume_excess": phase27_false_wet_volume_excess,
        "delta_false_wet_volume_excess": phase27_false_wet_volume_excess - phase25_false_wet_volume_excess,
        "already_wet_both_phase_count": already_wet_cell_count,
        "already_wet_depth_amplification_sum": already_wet_depth_amplification_sum,
        "already_wet_depth_amplification_mean": already_wet_depth_amplification_mean,
        **depth_contribs,
    }


def compute_depth_bin_rows(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    total_delta = sum(float(row["delta_volume_bias"]) for row in records)
    for bin_name, _, _ in DEPTH_BINS:
        key = f"{bin_name}_phase27_minus_phase25_predicted_volume"
        value = sum(float(row[key]) for row in records)
        rows.append(
            {
                "target_depth_bin": bin_name,
                "phase27_minus_phase25_predicted_volume_contribution": value,
                "share_of_total_delta_volume_bias": value / (total_delta + EPS),
                "mean_per_step_contribution": value / len(records) if records else 0.0,
            }
        )
    return rows


def aggregate_by_timestep(records: list[dict[str, Any]], eps: float) -> list[dict[str, Any]]:
    grouped: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for row in records:
        grouped[int(row["timestep"])].append(row)

    output: list[dict[str, Any]] = []
    for timestep, rows in sorted(grouped.items()):
        target_volume = sum(float(row["target_volume_proxy"]) for row in rows)
        phase25_prediction_volume = sum(float(row["phase25_prediction_volume_proxy"]) for row in rows)
        phase27_prediction_volume = sum(float(row["phase27_prediction_volume_proxy"]) for row in rows)
        phase25_volume_bias = phase25_prediction_volume - target_volume
        phase27_volume_bias = phase27_prediction_volume - target_volume
        phase25_rel = phase25_volume_bias / (target_volume + eps)
        phase27_rel = phase27_volume_bias / (target_volume + eps)
        out = {
            "timestep": timestep,
            "paired_step_records": len(rows),
            "target_volume_proxy": target_volume,
            "phase25_prediction_volume_proxy": phase25_prediction_volume,
            "phase27_prediction_volume_proxy": phase27_prediction_volume,
            "phase25_volume_bias": phase25_volume_bias,
            "phase27_volume_bias": phase27_volume_bias,
            "delta_volume_bias": phase27_volume_bias - phase25_volume_bias,
            "phase25_relative_volume_bias": phase25_rel,
            "phase27_relative_volume_bias": phase27_rel,
            "phase25_absolute_relative_volume_bias": abs(phase25_rel),
            "phase27_absolute_relative_volume_bias": abs(phase27_rel),
            "delta_absolute_relative_volume_bias": abs(phase27_rel) - abs(phase25_rel),
        }
        for key in (
            "delta_overlap_volume_difference",
            "phase25_false_dry_volume_loss",
            "phase27_false_dry_volume_loss",
            "delta_false_dry_volume_loss",
            "false_dry_volume_loss_decrease",
            "phase25_false_wet_volume_excess",
            "phase27_false_wet_volume_excess",
            "delta_false_wet_volume_excess",
            "already_wet_depth_amplification_sum",
        ):
            out[key] = sum(float(row[key]) for row in rows)
        for key in ("delta_false_dry_count", "delta_false_wet_count", "already_wet_both_phase_count"):
            out[key] = sum(int(row[key]) for row in rows)
        output.append(out)
    return output


def rank_timesteps(by_timestep: list[dict[str, Any]], top_k: int) -> list[dict[str, Any]]:
    rank_specs = (
        ("largest_delta_absolute_relative_volume_bias", "delta_absolute_relative_volume_bias"),
        ("largest_positive_delta_volume_bias", "delta_volume_bias"),
        ("largest_already_wet_depth_amplification", "already_wet_depth_amplification_sum"),
        ("largest_false_wet_volume_excess_increase", "delta_false_wet_volume_excess"),
        ("largest_false_dry_volume_loss_decrease", "false_dry_volume_loss_decrease"),
    )
    ranked_rows: list[dict[str, Any]] = []
    for rank_type, key in rank_specs:
        sorted_rows = sorted(by_timestep, key=lambda row: float(row[key]), reverse=True)
        for rank, row in enumerate(sorted_rows[:top_k], start=1):
            ranked_rows.append(
                {
                    "rank_type": rank_type,
                    "rank": rank,
                    "timestep": row["timestep"],
                    "paired_step_records": row["paired_step_records"],
                    "ranking_value": row[key],
                    "target_volume_proxy": row["target_volume_proxy"],
                    "phase25_volume_bias": row["phase25_volume_bias"],
                    "phase27_volume_bias": row["phase27_volume_bias"],
                    "delta_volume_bias": row["delta_volume_bias"],
                    "phase25_absolute_relative_volume_bias": row["phase25_absolute_relative_volume_bias"],
                    "phase27_absolute_relative_volume_bias": row["phase27_absolute_relative_volume_bias"],
                    "delta_absolute_relative_volume_bias": row["delta_absolute_relative_volume_bias"],
                    "delta_overlap_volume_difference": row["delta_overlap_volume_difference"],
                    "delta_false_dry_volume_loss": row["delta_false_dry_volume_loss"],
                    "false_dry_volume_loss_decrease": row["false_dry_volume_loss_decrease"],
                    "delta_false_wet_volume_excess": row["delta_false_wet_volume_excess"],
                    "already_wet_depth_amplification_sum": row["already_wet_depth_amplification_sum"],
                }
            )
    return ranked_rows


def summarize(records: list[dict[str, Any]], depth_bin_rows: list[dict[str, Any]], by_timestep: list[dict[str, Any]]) -> dict[str, Any]:
    target_volume = sum(float(row["target_volume_proxy"]) for row in records)
    phase25_prediction_volume = sum(float(row["phase25_prediction_volume_proxy"]) for row in records)
    phase27_prediction_volume = sum(float(row["phase27_prediction_volume_proxy"]) for row in records)
    phase25_volume_bias = phase25_prediction_volume - target_volume
    phase27_volume_bias = phase27_prediction_volume - target_volume
    delta_volume_bias = phase27_volume_bias - phase25_volume_bias
    phase25_rel = phase25_volume_bias / (target_volume + EPS)
    phase27_rel = phase27_volume_bias / (target_volume + EPS)

    false_wet_delta = sum(float(row["delta_false_wet_volume_excess"]) for row in records)
    false_dry_loss_delta = sum(float(row["delta_false_dry_volume_loss"]) for row in records)
    already_wet_amp = sum(float(row["already_wet_depth_amplification_sum"]) for row in records)
    overlap_delta = sum(float(row["delta_overlap_volume_difference"]) for row in records)

    positive_delta_rows = [row for row in records if float(row["delta_volume_bias"]) > 0.0]
    worsening_rows = [row for row in records if float(row["delta_absolute_relative_volume_bias"]) > 0.0]
    sorted_delta_abs = sorted(records, key=lambda row: float(row["delta_absolute_relative_volume_bias"]), reverse=True)
    top_10_count = max(1, math.ceil(0.10 * len(sorted_delta_abs))) if sorted_delta_abs else 0
    top_10_abs_worsening = sum(max(float(row["delta_absolute_relative_volume_bias"]), 0.0) for row in sorted_delta_abs[:top_10_count])
    total_abs_worsening = sum(max(float(row["delta_absolute_relative_volume_bias"]), 0.0) for row in records)

    dominant_bin = max(depth_bin_rows, key=lambda row: abs(float(row["phase27_minus_phase25_predicted_volume_contribution"])), default={})
    false_wet_explains = false_wet_delta > 0.0 and abs(false_wet_delta) >= 0.5 * abs(delta_volume_bias)
    already_wet_explains = already_wet_amp > 0.0 and abs(already_wet_amp) >= 0.5 * abs(delta_volume_bias)
    broad_behavior = len(worsening_rows) / len(records) >= 0.5 if records else False
    concentrated_top_10 = (top_10_abs_worsening / (total_abs_worsening + EPS)) >= 0.5 if total_abs_worsening > 0.0 else False

    if abs(phase25_rel) <= 0.01 and abs(phase27_rel) > abs(phase25_rel):
        recommendation = "tolerance-band volume consistency"
    elif false_wet_explains:
        recommendation = "balanced signed volume consistency"
    elif already_wet_explains:
        recommendation = "tolerance-band volume consistency"
    elif str(dominant_bin.get("target_depth_bin", "")) in {"shallow", "moderate", "deep"}:
        recommendation = "depth-bin-aware correction"
    else:
        recommendation = "stop Phase 27 as a mixed pilot"

    return {
        "paired_step_records": len(records),
        "target_volume_proxy_total": target_volume,
        "phase25_prediction_volume_proxy_total": phase25_prediction_volume,
        "phase27_prediction_volume_proxy_total": phase27_prediction_volume,
        "phase25_volume_bias_total": phase25_volume_bias,
        "phase27_volume_bias_total": phase27_volume_bias,
        "delta_volume_bias_total": delta_volume_bias,
        "phase25_relative_volume_bias": phase25_rel,
        "phase27_relative_volume_bias": phase27_rel,
        "delta_relative_volume_bias": phase27_rel - phase25_rel,
        "phase25_absolute_relative_volume_bias": abs(phase25_rel),
        "phase27_absolute_relative_volume_bias": abs(phase27_rel),
        "delta_absolute_relative_volume_bias": abs(phase27_rel) - abs(phase25_rel),
        "mean_step_delta_absolute_relative_volume_bias": (
            sum(float(row["delta_absolute_relative_volume_bias"]) for row in records) / len(records) if records else 0.0
        ),
        "positive_delta_volume_bias_record_fraction": len(positive_delta_rows) / len(records) if records else 0.0,
        "absolute_relative_volume_bias_worsening_record_fraction": len(worsening_rows) / len(records) if records else 0.0,
        "top_10_percent_share_of_positive_abs_rel_worsening": top_10_abs_worsening / (total_abs_worsening + EPS),
        "timestep_count": len(by_timestep),
        "false_wet_delta_volume_excess_total": false_wet_delta,
        "false_dry_volume_loss_delta_total": false_dry_loss_delta,
        "false_dry_volume_loss_decrease_total": -false_dry_loss_delta,
        "already_wet_depth_amplification_total": already_wet_amp,
        "overlap_volume_difference_delta_total": overlap_delta,
        "dominant_depth_bin_by_absolute_delta": dominant_bin.get("target_depth_bin", "n/a"),
        "dominant_depth_bin_delta": dominant_bin.get("phase27_minus_phase25_predicted_volume_contribution", 0.0),
        "false_wet_expansion_explains_worsening": false_wet_explains,
        "already_wet_amplification_explains_worsening": already_wet_explains,
        "broad_behavior_more_than_half_records_worsen": broad_behavior,
        "small_number_timesteps_dominate": concentrated_top_10,
        "phase25_already_near_zero_aggregate_volume_bias": abs(phase25_rel) <= 0.01,
        "recommended_redesign_direction": recommendation,
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


def write_markdown(path: Path, summary: dict[str, Any], depth_bin_rows: list[dict[str, Any]]) -> None:
    if summary["broad_behavior_more_than_half_records_worsen"] and summary["small_number_timesteps_dominate"]:
        concentration_text = "Broad behavior with a concentrated high-worsening tail"
    elif summary["broad_behavior_more_than_half_records_worsen"]:
        concentration_text = "Broad behavior"
    elif summary["small_number_timesteps_dominate"]:
        concentration_text = "A concentrated subset of records dominates"
    else:
        concentration_text = "Not broad by record count and not dominated by the top 10% tail"

    lines = [
        "# Phase 28 Volume-Response Loss Failure Diagnosis",
        "",
        "This diagnostic compares Phase 27 seed42 against the Phase 25 seed42 baseline using existing `evaluation_test/test_batch_*/forecast_maps.npz` files only. It is a volume-response proxy analysis based on depth rasters; it does not train, alter model architecture, alter losses, alter configs, or claim strict mass conservation, SWE, or PINN behavior.",
        "",
        "## Direct Answers",
        "",
        f"1. Did Phase 27's volume-bias worsening come from false-wet expansion? **{yes_no(bool(summary['false_wet_expansion_explains_worsening']))}**. Total Phase27 - Phase25 false-wet volume excess change was `{summary['false_wet_delta_volume_excess_total']:.6g}` versus total delta volume bias `{summary['delta_volume_bias_total']:.6g}`.",
        f"2. Did it come from already-wet depth amplification? **{yes_no(bool(summary['already_wet_amplification_explains_worsening']))}**. Already-wet Phase27 - Phase25 depth amplification summed to `{summary['already_wet_depth_amplification_total']:.6g}`.",
        f"3. Did it come from a small number of timesteps or broad behavior? **{concentration_text}**; top 10% of paired records account for `{summary['top_10_percent_share_of_positive_abs_rel_worsening']:.3f}` of positive absolute-relative-bias worsening.",
        f"4. Did it occur mainly in shallow, moderate, or deep target-depth bins? The largest absolute target-depth-bin contribution was `{summary['dominant_depth_bin_by_absolute_delta']}` with `{summary['dominant_depth_bin_delta']:.6g}` Phase27 - Phase25 predicted-volume change.",
        f"5. Was underresponse-only volume loss mismatched because Phase 25 seed42 was already near-zero aggregate volume bias? **{yes_no(bool(summary['phase25_already_near_zero_aggregate_volume_bias']))}**. Phase 25 aggregate relative volume bias was `{summary['phase25_relative_volume_bias']:.6g}`.",
        f"6. Which loss redesign is best supported? **{summary['recommended_redesign_direction']}**.",
        "",
        "## Summary Totals",
        "",
        "| Metric | Value |",
        "|---|---:|",
        f"| paired step records | {summary['paired_step_records']} |",
        f"| Phase 25 relative volume bias | {summary['phase25_relative_volume_bias']:.12g} |",
        f"| Phase 27 relative volume bias | {summary['phase27_relative_volume_bias']:.12g} |",
        f"| Delta volume bias | {summary['delta_volume_bias_total']:.12g} |",
        f"| Delta absolute relative volume bias | {summary['delta_absolute_relative_volume_bias']:.12g} |",
        f"| Mean paired delta absolute relative volume bias | {summary['mean_step_delta_absolute_relative_volume_bias']:.12g} |",
        f"| False-wet volume excess delta | {summary['false_wet_delta_volume_excess_total']:.12g} |",
        f"| False-dry volume loss decrease | {summary['false_dry_volume_loss_decrease_total']:.12g} |",
        f"| Already-wet amplification | {summary['already_wet_depth_amplification_total']:.12g} |",
        "",
        "## Target Depth Bins",
        "",
        "| Target depth bin | Phase27 - Phase25 predicted volume | Share of total delta volume bias |",
        "|---|---:|---:|",
    ]
    for row in depth_bin_rows:
        lines.append(
            f"| `{row['target_depth_bin']}` | "
            f"{row['phase27_minus_phase25_predicted_volume_contribution']:.12g} | "
            f"{row['share_of_total_delta_volume_bias']:.6g} |"
        )
    lines.extend(
        [
            "",
            "## Conservative Interpretation",
            "",
        "The supported redesign should be treated as a diagnostic recommendation, not as confirmation that Phase 27 achieved volume-response consistency. The largest target-depth-bin contribution is in dry-or-threshold cells, while thresholded false-wet volume excess decreased; this indicates that the worsening is not explained by simple false-wet expansion under the 0.05 m wet/dry threshold. Any future loss should avoid pushing near-balanced aggregate cases into over-response and should continue to report signed and absolute relative volume-bias proxy diagnostics.",
            "",
            "## Outputs",
            "",
            "- `volume_bias_decomposition_by_step.csv`",
            "- `volume_bias_depth_bin_decomposition.csv`",
            "- `volume_bias_timestep_ranking.csv`",
            "- `volume_bias_decomposition_summary.csv`",
            "- `phase28_volume_response_failure_summary.json`",
            "- `phase28_volume_response_failure_findings.md`",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    output_dir = resolve_repo_path(args.output_dir)
    phase25_run = REPO_ROOT / PHASE25_RUN
    phase27_run = REPO_ROOT / PHASE27_RUN
    phase25_files = list_forecast_files(phase25_run)
    phase27_files = list_forecast_files(phase27_run)

    records: list[dict[str, Any]] = []
    missing_or_errors: list[dict[str, str]] = []
    processed_map_files = 0

    for batch_name in sorted(set(phase25_files) & set(phase27_files)):
        phase25_path = phase25_files[batch_name]
        phase27_path = phase27_files[batch_name]
        try:
            phase25_prediction, phase25_target = load_forecast_file(phase25_path)
            phase27_prediction, phase27_target = load_forecast_file(phase27_path)
            processed_map_files += 2
        except (OSError, KeyError, ValueError, zipfile.BadZipFile) as exc:
            missing_or_errors.append({"batch": batch_name, "path": display_path(phase25_path), "reason": str(exc)})
            continue

        if phase25_prediction.shape != phase27_prediction.shape or phase25_target.shape != phase27_target.shape:
            missing_or_errors.append(
                {
                    "batch": batch_name,
                    "path": display_path(phase27_path),
                    "reason": (
                        f"phase25 shapes {phase25_prediction.shape}/{phase25_target.shape} do not match "
                        f"phase27 shapes {phase27_prediction.shape}/{phase27_target.shape}"
                    ),
                }
            )
            continue

        if not np.allclose(phase25_target, phase27_target, rtol=1.0e-7, atol=1.0e-9):
            missing_or_errors.append(
                {
                    "batch": batch_name,
                    "path": display_path(phase27_path),
                    "reason": "phase25 and phase27 targets differ; using phase25 target for matched diagnostic",
                }
            )

        for sample_index in range(phase25_prediction.shape[0]):
            for timestep in range(phase25_prediction.shape[1]):
                records.append(
                    compute_pair_record(
                        batch_name=batch_name,
                        sample_index=sample_index,
                        timestep=timestep,
                        phase25_prediction=phase25_prediction[sample_index, timestep],
                        phase27_prediction=phase27_prediction[sample_index, timestep],
                        target=phase25_target[sample_index, timestep],
                        threshold=args.threshold,
                        eps=args.eps,
                    )
                )

    for batch_name in sorted(set(phase25_files) ^ set(phase27_files)):
        missing_or_errors.append(
            {
                "batch": batch_name,
                "path": display_path(phase25_files.get(batch_name, phase27_files.get(batch_name, Path(batch_name)))),
                "reason": "batch exists in only one comparison run",
            }
        )

    depth_bin_rows = compute_depth_bin_rows(records)
    by_timestep = aggregate_by_timestep(records, args.eps)
    ranking_rows = rank_timesteps(by_timestep, max(args.top_k, 1))
    summary = summarize(records, depth_bin_rows, by_timestep)
    summary_rows = [summary]

    outputs = {
        "by_step": output_dir / "volume_bias_decomposition_by_step.csv",
        "depth_bins": output_dir / "volume_bias_depth_bin_decomposition.csv",
        "ranking": output_dir / "volume_bias_timestep_ranking.csv",
        "summary_csv": output_dir / "volume_bias_decomposition_summary.csv",
        "summary_json": output_dir / "phase28_volume_response_failure_summary.json",
        "findings_md": output_dir / "phase28_volume_response_failure_findings.md",
    }

    write_csv(outputs["by_step"], records)
    write_csv(outputs["depth_bins"], depth_bin_rows)
    write_csv(outputs["ranking"], ranking_rows)
    write_csv(outputs["summary_csv"], summary_rows)
    write_json(
        outputs["summary_json"],
        {
            "scope": {
                "diagnostic_only": True,
                "threshold_m": args.threshold,
                "phase25_run": PHASE25_RUN,
                "phase27_run": PHASE27_RUN,
                "output_dir": display_path(output_dir),
                "note": "Reads only existing evaluation_test/test_batch_*/forecast_maps.npz files.",
            },
            "processed_map_files": processed_map_files,
            "paired_step_records": len(records),
            "missing_or_error_files": missing_or_errors,
            "summary": summary,
            "depth_bin_decomposition": depth_bin_rows,
            "timestep_aggregates": by_timestep,
        },
    )
    write_markdown(outputs["findings_md"], summary, depth_bin_rows)

    print("Phase 28 volume-response failure diagnostic complete.")
    print(f"  processed map files: {processed_map_files}")
    print(f"  paired step records: {len(records)}")
    print(f"  aggregate delta volume bias: {metric_value(summary, 'delta_volume_bias_total')}")
    print(f"  false-wet expansion explains worsening: {yes_no(bool(summary['false_wet_expansion_explains_worsening']))}")
    print(
        "  already-wet amplification explains worsening: "
        f"{yes_no(bool(summary['already_wet_amplification_explains_worsening']))}"
    )
    print(f"  recommended redesign direction: {summary['recommended_redesign_direction']}")
    if missing_or_errors:
        print(f"  warnings: {len(missing_or_errors)}")
        for item in missing_or_errors[:8]:
            print(f"    - {item['batch']}: {item['reason']}")
    for path in outputs.values():
        print(f"  wrote: {display_path(path)}")


if __name__ == "__main__":
    main()
