from __future__ import annotations

import csv
import json
import math
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import torch


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.analyze_phase48_full_dataset_reliability import (  # noqa: E402
    EPS,
    MetricAccumulator,
    PeakAccumulator,
)
from scripts.build_phase49_warning_framework import (  # noqa: E402
    WARNING_ACTIONS,
    failure_drivers,
)
from scripts.train_phase47_full_downsample_baseline import (  # noqa: E402
    build_datasets,
    build_model,
    load_json,
    make_loader,
    set_seed,
    validate_indexes,
    validate_row_shapes,
)
from scripts.train_phase52_controlled_longer_run import (  # noqa: E402
    EXPECTED_TEST_WINDOWS,
    PHASE47_CONFIG,
    UNCHANGED_PHASE47_KEYS,
)


CONFIG_PATH = Path("configs/train_phase52_full_downsample128_seed42_40e.json")
CHECKPOINT_PATH = Path("runs/phase52_full_downsample128_seed42_40e/checkpoints/best.pt")
METRICS_CSV_PATH = Path("runs/phase52_full_downsample128_seed42_40e/metrics.csv")
METRICS_JSON_PATH = Path("runs/phase52_full_downsample128_seed42_40e/metrics.json")
TRAINING_SUMMARY_PATH = Path(
    "analysis/phase52_controlled_128x128_seed42_longer_run/phase52_training_summary.json"
)
PHASE48_DIR = Path("analysis/phase48_full_dataset_reliability_physical_proxy")
PHASE49_DIR = Path("analysis/phase49_full_dataset_warning_framework")
OUTPUT_DIR = Path("analysis/phase53_phase52_diagnostics_review")

SELECTED_DECISION = "phase53_phase52_diagnostics_review_completed"
BLOCKED_DECISION = "phase53_diagnostics_blocked_by_checkpoint_or_evaluation_issue"
EXPECTED_SCENARIOS = 48
REFERENCE_WARNING_COUNTS = {"reliable": 1, "caution": 12, "high-risk": 35}
WARNING_ORDER = {"reliable": 0, "caution": 1, "high-risk": 2}

REQUIRED_INPUTS = (
    CONFIG_PATH,
    CHECKPOINT_PATH,
    METRICS_CSV_PATH,
    METRICS_JSON_PATH,
    TRAINING_SUMMARY_PATH,
    PHASE48_DIR / "scenario_reliability_metrics.csv",
    PHASE48_DIR / "peak_depth_timing_metrics.csv",
    PHASE48_DIR / "volume_response_proxy_metrics.csv",
    PHASE48_DIR / "phase48_reliability_summary.json",
    PHASE49_DIR / "scenario_warning_framework.csv",
    PHASE49_DIR / "warning_framework_summary.json",
    Path("analysis/phase45_full_dataset_indexing/scenario_index.csv"),
    Path("analysis/phase45_full_dataset_indexing/static_geodata_index.csv"),
)


def repo_path(path: str | Path) -> Path:
    candidate = Path(path)
    return candidate if candidate.is_absolute() else REPO_ROOT / candidate


def display_path(path: str | Path) -> str:
    path = repo_path(path)
    try:
        return path.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return str(path.resolve())


def bool_text(value: Any) -> str:
    return str(bool(value)).lower()


def read_json(path: str | Path) -> dict[str, Any]:
    return json.loads(repo_path(path).read_text(encoding="utf-8"))


def read_csv(path: str | Path) -> list[dict[str, str]]:
    with repo_path(path).open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError(f"Missing CSV header: {display_path(path)}")
        return [dict(row) for row in reader]


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path = repo_path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    path = repo_path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def to_float(value: Any, default: float = 0.0) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return default
    return number if math.isfinite(number) else default


def mean(rows: list[dict[str, Any]], key: str) -> float | None:
    values = [to_float(row.get(key), math.nan) for row in rows]
    values = [value for value in values if math.isfinite(value)]
    return float(np.mean(values)) if values else None


def median(rows: list[dict[str, Any]], key: str) -> float | None:
    values = [to_float(row.get(key), math.nan) for row in rows]
    values = [value for value in values if math.isfinite(value)]
    return float(np.median(values)) if values else None


def scenario_key(row: dict[str, Any]) -> tuple[str, str, str, str]:
    return (
        str(row.get("split", "")),
        str(row.get("location", "")),
        str(row.get("scenario", "")),
        str(row.get("scenario_type", "")),
    )


def validate_config(config: dict[str, Any]) -> None:
    required = {
        "phase": 52,
        "seed": 42,
        "resolution": 128,
        "epochs": 40,
        "output_dir": "runs/phase52_full_downsample128_seed42_40e",
        "analysis_dir": "analysis/phase52_controlled_128x128_seed42_longer_run",
        "training_scope": "controlled_128x128_seed42_longer_run",
        "no_swe_pinn": True,
        "level5_supported": False,
    }
    for key, expected in required.items():
        actual = config.get(key)
        if key in {"output_dir", "analysis_dir"}:
            actual = Path(str(actual)).as_posix()
        if actual != expected:
            raise ValueError(f"Phase 53 requires Phase 52 config {key}={expected!r}, got {actual!r}.")

    phase47 = load_json(PHASE47_CONFIG)
    for key in UNCHANGED_PHASE47_KEYS:
        if config.get(key) != phase47.get(key):
            raise ValueError(f"Phase 52 {key!r} does not match the Phase 47 diagnostic basis.")


def validate_retained_artifacts(
    config: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    metrics_json = read_json(METRICS_JSON_PATH)
    training_summary = read_json(TRAINING_SUMMARY_PATH)
    metric_rows = read_csv(METRICS_CSV_PATH)
    if not metric_rows:
        raise ValueError("Phase 52 metrics.csv is empty.")
    final_row = metric_rows[-1]
    if int(to_float(final_row.get("epoch"))) != 40:
        raise ValueError("Phase 52 metrics.csv does not end at epoch 40.")
    if int(training_summary.get("best_epoch", 0)) != 40:
        raise ValueError("Phase 52 training summary does not select epoch 40.")
    if int(training_summary.get("epochs_completed", 0)) != 40:
        raise ValueError("Phase 52 training summary does not report 40 completed epochs.")
    expected_rmse = to_float(training_summary["best_epoch_metrics"]["test_rmse"])
    if not math.isclose(to_float(metrics_json.get("best_test_rmse")), expected_rmse, rel_tol=1e-9, abs_tol=1e-12):
        raise ValueError("Phase 52 metrics.json and training summary disagree on best test RMSE.")
    if not math.isclose(to_float(final_row.get("test_rmse")), expected_rmse, rel_tol=1e-9, abs_tol=1e-12):
        raise ValueError("Phase 52 metrics.csv and training summary disagree on epoch-40 test RMSE.")
    if config != training_summary.get("config", config):
        # Older summaries do not retain the full config; checkpoint validation below is authoritative.
        pass
    return metrics_json, training_summary, final_row


def load_checkpoint_metadata(config: dict[str, Any]) -> dict[str, Any]:
    checkpoint = torch.load(repo_path(CHECKPOINT_PATH), map_location="cpu")
    if not isinstance(checkpoint, dict) or "model_state" not in checkpoint:
        raise ValueError("Phase 52 best checkpoint does not contain model_state.")
    if int(checkpoint.get("epoch", 0)) != 40:
        raise ValueError(f"Expected Phase 52 best checkpoint epoch 40, got {checkpoint.get('epoch')}.")
    if checkpoint.get("config") != config:
        raise ValueError("Phase 52 best checkpoint config does not match the retained config.")
    return checkpoint


def base_readiness(
    *,
    selected_decision: str,
    checkpoint_found: bool,
    diagnostics_executed: bool,
    notes: list[str],
    checks: dict[str, Any],
) -> dict[str, Any]:
    return {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "phase": 53,
        "selected_decision": selected_decision,
        "checkpoint_found": checkpoint_found,
        "checkpoint_path": display_path(CHECKPOINT_PATH) if checkpoint_found else None,
        "diagnostics_executed": diagnostics_executed,
        "evaluated_split": "test",
        "input_checks": checks,
        "notes": notes,
        "no_training": True,
        "no_swe_pinn": True,
        "level5_supported": False,
        "warning_labels_are_probabilities": False,
    }


def phase48_thresholds() -> dict[str, float]:
    summary = read_json(PHASE48_DIR / "phase48_reliability_summary.json")
    thresholds = summary.get("warning_thresholds", {})
    required = {
        "rmse_reliable_max",
        "wet_dry_iou_reliable_min",
        "false_dry_reliable_max",
        "false_wet_reliable_max",
        "absolute_relative_volume_bias_reliable_max",
        "rmse_high_risk_min",
        "wet_dry_iou_high_risk_max",
        "false_dry_high_risk_min",
        "false_wet_high_risk_min",
        "absolute_relative_volume_bias_high_risk_min",
    }
    missing = sorted(required - set(thresholds))
    if missing:
        raise ValueError(f"Phase 48 summary is missing warning thresholds: {missing}")
    return {key: to_float(value) for key, value in thresholds.items()}


def warning_level(row: dict[str, Any], thresholds: dict[str, float]) -> str:
    reliable = (
        to_float(row["rmse"]) <= thresholds["rmse_reliable_max"]
        and to_float(row["wet_dry_iou"]) >= thresholds["wet_dry_iou_reliable_min"]
        and to_float(row["false_dry_rate"]) <= thresholds["false_dry_reliable_max"]
        and to_float(row["false_wet_rate"]) <= thresholds["false_wet_reliable_max"]
        and to_float(row["absolute_relative_volume_bias_proxy"])
        <= thresholds["absolute_relative_volume_bias_reliable_max"]
    )
    high_risk = (
        to_float(row["rmse"]) >= thresholds["rmse_high_risk_min"]
        or to_float(row["wet_dry_iou"]) <= thresholds["wet_dry_iou_high_risk_max"]
        or to_float(row["false_dry_rate"]) >= thresholds["false_dry_high_risk_min"]
        or to_float(row["false_wet_rate"]) >= thresholds["false_wet_high_risk_min"]
        or to_float(row["absolute_relative_volume_bias_proxy"])
        >= thresholds["absolute_relative_volume_bias_high_risk_min"]
    )
    if reliable:
        return "reliable"
    if high_risk:
        return "high-risk"
    return "caution"


def transition(old: str, new: str) -> str:
    if old not in WARNING_ORDER or new not in WARNING_ORDER:
        return "not_comparable"
    if WARNING_ORDER[new] < WARNING_ORDER[old]:
        return "improved"
    if WARNING_ORDER[new] > WARNING_ORDER[old]:
        return "worsened"
    return "unchanged"


def comparison_direction(metric: str, old: float, new: float, tolerance: float = 1.0e-12) -> str:
    if metric in {"peak_depth_bias", "signed_volume_bias_proxy"}:
        delta = abs(new) - abs(old)
        if abs(delta) <= tolerance:
            return "unchanged"
        return "improved" if delta < 0 else "degraded"
    delta = new - old
    if abs(delta) <= tolerance:
        return "unchanged"
    higher_is_better = metric in {"wet_dry_iou", "rollout_stability"}
    favorable = delta > 0 if higher_is_better else delta < 0
    return "improved" if favorable else "degraded"


def enrich_peak_metrics(metrics: dict[str, Any]) -> dict[str, Any]:
    target = to_float(metrics.get("peak_target_depth"))
    pred = to_float(metrics.get("peak_pred_depth"))
    bias = pred - target
    timing_signed: int | None = None
    if metrics.get("target_peak_global_step") is not None and metrics.get("pred_peak_global_step") is not None:
        timing_signed = int(metrics["pred_peak_global_step"]) - int(metrics["target_peak_global_step"])
    return {
        **metrics,
        "signed_peak_depth_bias": bias,
        "absolute_peak_depth_error": abs(bias),
        "relative_peak_depth_error": bias / max(abs(target), EPS),
        "peak_depth_underprediction_flag": bias < 0.0,
        "signed_peak_timing_error": timing_signed,
        "absolute_peak_timing_error": abs(timing_signed) if timing_signed is not None else None,
    }


def run_inference(config: dict[str, Any], checkpoint: dict[str, Any]) -> dict[str, Any]:
    scenario_index, _ = validate_indexes(config)
    validate_row_shapes(scenario_index)
    _, test_dataset = build_datasets(config, scenario_index)
    if len(test_dataset) != EXPECTED_TEST_WINDOWS:
        raise ValueError(f"Expected {EXPECTED_TEST_WINDOWS} test windows, got {len(test_dataset)}.")

    device = torch.device(config["runtime"]["device"] if torch.cuda.is_available() else "cpu")
    loader = make_loader(
        test_dataset,
        batch_size=int(config["optimization"]["eval_batch_size"]),
        shuffle=False,
        config=config,
    )
    model = build_model(config).to(device)
    model.load_state_dict(checkpoint["model_state"])
    model.eval()

    wet_threshold = float(config["metrics"]["wet_threshold"])
    scenario_acc: dict[tuple[str, str, str, str], MetricAccumulator] = defaultdict(MetricAccumulator)
    global_step_acc: dict[int, MetricAccumulator] = defaultdict(MetricAccumulator)
    scenario_step_acc: dict[tuple[tuple[str, str, str, str], int], MetricAccumulator] = defaultdict(
        MetricAccumulator
    )
    peak_acc: dict[tuple[str, str, str, str], PeakAccumulator] = defaultdict(PeakAccumulator)
    detailed_step_rows: list[dict[str, Any]] = []

    with torch.no_grad():
        for batch in loader:
            past_flood = batch["past_flood"].float().to(device)
            past_rainfall = batch["past_rainfall"].float().to(device)
            future_rainfall = batch["future_rainfall"].float().to(device)
            static_maps = batch["static_maps"].float().to(device)
            target = batch["future_flood"].float().to(device)
            pred = model(past_flood, past_rainfall, future_rainfall, static_maps)
            if pred.shape != target.shape:
                raise ValueError(f"Prediction shape {tuple(pred.shape)} != target shape {tuple(target.shape)}.")

            pred_wet = pred >= wet_threshold
            target_wet = target >= wet_threshold
            for sample_index, metadata in enumerate(batch["metadata"]):
                key = scenario_key(metadata)
                start_idx = int(metadata["start_idx"])
                sample_id = f"{key[1]}/{key[2]}/start{start_idx}"
                scenario_acc[key].update(
                    sample_id=sample_id,
                    pred=pred[sample_index],
                    target=target[sample_index],
                    pred_wet=pred_wet[sample_index],
                    target_wet=target_wet[sample_index],
                )
                for step in range(pred.shape[1]):
                    global_step = start_idx + int(metadata["input_steps"]) + step
                    step_sample_id = f"{sample_id}/step{step}"
                    kwargs = {
                        "sample_id": step_sample_id,
                        "pred": pred[sample_index, step],
                        "target": target[sample_index, step],
                        "pred_wet": pred_wet[sample_index, step],
                        "target_wet": target_wet[sample_index, step],
                    }
                    global_step_acc[step].update(**kwargs)
                    scenario_step_acc[(key, step)].update(**kwargs)
                    sample_step_acc = MetricAccumulator()
                    sample_step_acc.update(**kwargs)
                    sample_step_metrics = sample_step_acc.as_metrics()
                    detailed_step_rows.append(
                        {
                            "split": key[0],
                            "location": key[1],
                            "scenario": key[2],
                            "scenario_type": key[3],
                            "sample_id": sample_id,
                            "start_idx": start_idx,
                            "window_step": step,
                            "global_step": global_step,
                            "valid_pixel_count": sample_step_acc.count,
                            "rmse": sample_step_metrics["rmse"],
                            "mae": sample_step_metrics["mae"],
                            "wet_dry_iou": sample_step_metrics["wet_dry_iou"],
                            "false_dry_rate": sample_step_metrics["false_dry_rate"],
                            "false_wet_rate": sample_step_metrics["false_wet_rate"],
                            "mean_target_depth": sample_step_metrics["mean_target_depth"],
                            "mean_pred_depth": sample_step_metrics["mean_pred_depth"],
                            "signed_volume_bias_proxy": sample_step_metrics[
                                "relative_volume_bias_proxy"
                            ],
                        }
                    )
                    peak_acc[key].update(
                        target_peak=float(target[sample_index, step].max().item()),
                        pred_peak=float(pred[sample_index, step].max().item()),
                        global_step=global_step,
                    )

    thresholds = phase48_thresholds()
    phase48_scenarios = {scenario_key(row): row for row in read_csv(PHASE48_DIR / "scenario_reliability_metrics.csv")}
    phase49_warnings = {scenario_key(row): row for row in read_csv(PHASE49_DIR / "scenario_warning_framework.csv")}

    scenario_rows: list[dict[str, Any]] = []
    for key, acc in sorted(scenario_acc.items()):
        split, location, scenario, scenario_type = key
        step_rmses = [
            to_float(scenario_step_acc[(key, step)].as_metrics()["rmse"])
            for step in sorted(global_step_acc)
        ]
        step_std = float(np.std(step_rmses)) if step_rmses else 0.0
        row = {
            "split": split,
            "location": location,
            "scenario": scenario,
            "scenario_type": scenario_type,
            **acc.as_metrics(),
            "valid_window_count": len(acc.sample_ids),
            "valid_step_count": len(step_rmses),
            "step_rmse_mean": float(np.mean(step_rmses)) if step_rmses else 0.0,
            "step_rmse_std": step_std,
            "rollout_stability": 1.0 / (1.0 + step_std),
            "missing_or_invalid_metric": False,
        }
        row["warning_level"] = warning_level(row, thresholds)
        scenario_rows.append(row)

    peak_rows: list[dict[str, Any]] = []
    for key, acc in sorted(peak_acc.items()):
        split, location, scenario, scenario_type = key
        peak_rows.append(
            {
                "split": split,
                "location": location,
                "scenario": scenario,
                "scenario_type": scenario_type,
                **enrich_peak_metrics(acc.as_metrics()),
            }
        )
    peak_by_key = {scenario_key(row): row for row in peak_rows}

    volume_rows: list[dict[str, Any]] = []
    for row in scenario_rows:
        key = scenario_key(row)
        acc = scenario_acc[key]
        signed_bias = acc.pred_sum - acc.target_sum
        volume_rows.append(
            {
                "split": row["split"],
                "location": row["location"],
                "scenario": row["scenario"],
                "scenario_type": row["scenario_type"],
                "sum_target_depth": acc.target_sum,
                "sum_pred_depth": acc.pred_sum,
                "signed_summed_depth_bias": signed_bias,
                "absolute_summed_depth_error": abs(signed_bias),
                "signed_volume_bias_proxy": row["relative_volume_bias_proxy"],
                "relative_volume_bias_proxy": row["relative_volume_bias_proxy"],
                "absolute_relative_volume_bias_proxy": row["absolute_relative_volume_bias_proxy"],
            }
        )

    wet_dry_rows = [
        {
            "split": row["split"],
            "location": row["location"],
            "scenario": row["scenario"],
            "scenario_type": row["scenario_type"],
            "false_dry_count": scenario_acc[scenario_key(row)].false_dry,
            "false_wet_count": scenario_acc[scenario_key(row)].false_wet,
            "target_wet_count": scenario_acc[scenario_key(row)].target_wet,
            "target_dry_count": scenario_acc[scenario_key(row)].target_dry,
            "false_dry_rate": row["false_dry_rate"],
            "false_wet_rate": row["false_wet_rate"],
            "wet_dry_iou": row["wet_dry_iou"],
            "target_wet_prevalence": row["target_wet_fraction"],
            "predicted_wet_prevalence": row["pred_wet_fraction"],
        }
        for row in scenario_rows
    ]

    warning_rows: list[dict[str, Any]] = []
    comparison_rows: list[dict[str, Any]] = []
    phase48_peaks = {scenario_key(row): row for row in read_csv(PHASE48_DIR / "peak_depth_timing_metrics.csv")}
    phase48_volumes = {scenario_key(row): row for row in read_csv(PHASE48_DIR / "volume_response_proxy_metrics.csv")}
    compare_metrics = (
        "rmse",
        "mae",
        "wet_dry_iou",
        "false_dry_rate",
        "false_wet_rate",
        "peak_depth_bias",
        "absolute_peak_depth_error",
        "absolute_peak_timing_error",
        "signed_volume_bias_proxy",
        "absolute_relative_volume_bias_proxy",
    )
    for row in scenario_rows:
        key = scenario_key(row)
        old = phase48_scenarios.get(key)
        old_warning = phase49_warnings.get(key, {}).get("warning_level", "")
        new_warning = str(row["warning_level"])
        new_drivers = failure_drivers({**row, **peak_by_key[key]}, thresholds)
        old_drivers = str(phase49_warnings.get(key, {}).get("failure_drivers", ""))
        warning_rows.append(
            {
                "split": row["split"],
                "location": row["location"],
                "scenario": row["scenario"],
                "scenario_type": row["scenario_type"],
                "rmse": row["rmse"],
                "mae": row["mae"],
                "wet_dry_iou": row["wet_dry_iou"],
                "false_dry_rate": row["false_dry_rate"],
                "false_wet_rate": row["false_wet_rate"],
                "absolute_relative_volume_bias_proxy": row["absolute_relative_volume_bias_proxy"],
                "peak_depth_underprediction_proxy": peak_by_key[key]["peak_depth_underprediction_proxy"],
                "phase53_warning_level": new_warning,
                "warning_action": WARNING_ACTIONS[new_warning],
                "primary_failure_driver": new_drivers[0],
                "secondary_failure_drivers": " | ".join(new_drivers[1:]),
                "missing_metric_flags": "",
                "phase48_warning_level": old_warning,
                "phase48_failure_drivers": old_drivers,
                "warning_label_transition": transition(old_warning, new_warning),
                "warning_labels_are_probabilities": False,
            }
        )

        compare: dict[str, Any] = {
            "split": row["split"],
            "location": row["location"],
            "scenario": row["scenario"],
            "scenario_type": row["scenario_type"],
            "phase48_warning_level": old_warning,
            "phase53_warning_level": new_warning,
            "warning_label_transition": transition(old_warning, new_warning),
            "comparability_status": "matched" if old else "not_comparable",
            "comparability_reason": "" if old else "Phase 48 scenario row missing",
        }
        if old:
            old_peak = phase48_peaks.get(key, {})
            old_volume = phase48_volumes.get(key, {})
            old_peak_bias = to_float(old_peak.get("peak_pred_depth")) - to_float(old_peak.get("peak_target_depth"))
            old_values = {
                **old,
                "peak_depth_bias": old_peak_bias,
                "absolute_peak_depth_error": abs(old_peak_bias),
                "absolute_peak_timing_error": to_float(old_peak.get("peak_timing_error_proxy")),
                "signed_volume_bias_proxy": to_float(old_volume.get("relative_volume_bias_proxy")),
                "absolute_relative_volume_bias_proxy": to_float(
                    old_volume.get("absolute_relative_volume_bias_proxy")
                ),
            }
            new_values = {
                **row,
                "peak_depth_bias": peak_by_key[key]["signed_peak_depth_bias"],
                "absolute_peak_depth_error": peak_by_key[key]["absolute_peak_depth_error"],
                "absolute_peak_timing_error": peak_by_key[key]["absolute_peak_timing_error"],
                "signed_volume_bias_proxy": row["relative_volume_bias_proxy"],
            }
            for metric in compare_metrics:
                old_value = to_float(old_values.get(metric))
                new_value = to_float(new_values.get(metric))
                compare[f"phase48_{metric}"] = old_value
                compare[f"phase52_{metric}"] = new_value
                compare[f"delta_{metric}"] = new_value - old_value
                compare[f"relative_change_{metric}"] = (
                    (new_value - old_value) / abs(old_value) if abs(old_value) > EPS else ""
                )
                compare[f"direction_{metric}"] = comparison_direction(metric, old_value, new_value)
        comparison_rows.append(compare)

    location_groups: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in scenario_rows:
        location_groups[(str(row["location"]), str(row["scenario_type"]))].append(row)
    location_rows = []
    for (location, scenario_type), rows in sorted(location_groups.items()):
        counts = Counter(str(row["warning_level"]) for row in rows)
        location_rows.append(
            {
                "location": location,
                "scenario_type": scenario_type,
                "scenario_count": len(rows),
                "reliable_count": counts["reliable"],
                "caution_count": counts["caution"],
                "high_risk_count": counts["high-risk"],
                "mean_rmse": mean(rows, "rmse"),
                "mean_mae": mean(rows, "mae"),
                "mean_wet_dry_iou": mean(rows, "wet_dry_iou"),
                "mean_false_dry_rate": mean(rows, "false_dry_rate"),
                "mean_false_wet_rate": mean(rows, "false_wet_rate"),
                "mean_absolute_relative_volume_bias_proxy": mean(
                    rows, "absolute_relative_volume_bias_proxy"
                ),
            }
        )

    return {
        "scenario_rows": scenario_rows,
        "step_rows": detailed_step_rows,
        "wet_dry_rows": wet_dry_rows,
        "peak_rows": peak_rows,
        "volume_rows": volume_rows,
        "location_rows": location_rows,
        "warning_rows": warning_rows,
        "comparison_rows": comparison_rows,
        "thresholds": thresholds,
        "evaluated_windows": len(test_dataset),
        "device": str(device),
    }


def write_tables(result: dict[str, Any]) -> None:
    scenario_fields = [
        "split", "location", "scenario", "scenario_type", "sample_count", "valid_window_count",
        "valid_step_count", "rmse", "mae", "wet_dry_iou", "false_dry_rate", "false_wet_rate",
        "target_wet_fraction", "pred_wet_fraction", "mean_target_depth", "mean_pred_depth",
        "max_target_depth", "max_pred_depth", "absolute_volume_bias_proxy",
        "relative_volume_bias_proxy", "absolute_relative_volume_bias_proxy",
        "peak_depth_underprediction_proxy", "step_rmse_mean", "step_rmse_std",
        "rollout_stability", "missing_or_invalid_metric", "warning_level",
    ]
    write_csv(OUTPUT_DIR / "scenario_reliability_metrics.csv", result["scenario_rows"], scenario_fields)
    write_csv(
        OUTPUT_DIR / "step_reliability_metrics.csv",
        result["step_rows"],
        [
            "split", "location", "scenario", "scenario_type", "sample_id", "start_idx",
            "window_step", "global_step", "valid_pixel_count", "rmse", "mae",
            "wet_dry_iou", "false_dry_rate", "false_wet_rate", "mean_target_depth",
            "mean_pred_depth", "signed_volume_bias_proxy",
        ],
    )
    write_csv(
        OUTPUT_DIR / "wet_dry_error_metrics.csv",
        result["wet_dry_rows"],
        [
            "split", "location", "scenario", "scenario_type", "false_dry_count",
            "false_wet_count", "target_wet_count", "target_dry_count", "false_dry_rate",
            "false_wet_rate", "wet_dry_iou", "target_wet_prevalence", "predicted_wet_prevalence",
        ],
    )
    write_csv(
        OUTPUT_DIR / "peak_depth_timing_metrics.csv",
        result["peak_rows"],
        [
            "split", "location", "scenario", "scenario_type", "peak_target_depth",
            "peak_pred_depth", "signed_peak_depth_bias", "absolute_peak_depth_error",
            "relative_peak_depth_error", "peak_depth_underprediction_proxy",
            "peak_depth_underprediction_flag", "target_peak_global_step", "pred_peak_global_step",
            "signed_peak_timing_error", "absolute_peak_timing_error", "peak_timing_error_proxy",
        ],
    )
    write_csv(
        OUTPUT_DIR / "volume_response_proxy_metrics.csv",
        result["volume_rows"],
        [
            "split", "location", "scenario", "scenario_type", "sum_target_depth",
            "sum_pred_depth", "signed_summed_depth_bias", "absolute_summed_depth_error",
            "signed_volume_bias_proxy", "relative_volume_bias_proxy",
            "absolute_relative_volume_bias_proxy",
        ],
    )
    write_csv(
        OUTPUT_DIR / "location_type_summary.csv",
        result["location_rows"],
        [
            "location", "scenario_type", "scenario_count", "reliable_count", "caution_count",
            "high_risk_count", "mean_rmse", "mean_mae", "mean_wet_dry_iou",
            "mean_false_dry_rate", "mean_false_wet_rate",
            "mean_absolute_relative_volume_bias_proxy",
        ],
    )
    write_csv(
        OUTPUT_DIR / "reliability_warning_levels.csv",
        result["warning_rows"],
        [
            "split", "location", "scenario", "scenario_type", "rmse", "mae", "wet_dry_iou",
            "false_dry_rate", "false_wet_rate", "absolute_relative_volume_bias_proxy",
            "peak_depth_underprediction_proxy", "phase53_warning_level", "warning_action",
            "primary_failure_driver", "secondary_failure_drivers", "missing_metric_flags",
            "phase48_warning_level", "phase48_failure_drivers", "warning_label_transition",
            "warning_labels_are_probabilities",
        ],
    )
    comparison_fields = [
        "split", "location", "scenario", "scenario_type", "phase48_warning_level",
        "phase53_warning_level", "warning_label_transition", "comparability_status",
        "comparability_reason",
    ]
    metrics = (
        "rmse", "mae", "wet_dry_iou", "false_dry_rate", "false_wet_rate", "peak_depth_bias",
        "absolute_peak_depth_error", "absolute_peak_timing_error", "signed_volume_bias_proxy",
        "absolute_relative_volume_bias_proxy",
    )
    for metric in metrics:
        comparison_fields.extend(
            [
                f"phase48_{metric}", f"phase52_{metric}", f"delta_{metric}",
                f"relative_change_{metric}", f"direction_{metric}",
            ]
        )
    write_csv(
        OUTPUT_DIR / "phase52_vs_phase48_diagnostic_comparison.csv",
        result["comparison_rows"],
        comparison_fields,
    )


def ordered_warning_counts(rows: list[dict[str, Any]], key: str) -> dict[str, int]:
    counts = Counter(str(row.get(key, "")) for row in rows)
    return {level: int(counts.get(level, 0)) for level in ("reliable", "caution", "high-risk")}


def aggregate_comparison(result: dict[str, Any]) -> dict[str, Any]:
    comparisons = [row for row in result["comparison_rows"] if row["comparability_status"] == "matched"]
    metrics = (
        "rmse", "mae", "wet_dry_iou", "false_dry_rate", "false_wet_rate",
        "absolute_peak_depth_error", "absolute_peak_timing_error",
        "absolute_relative_volume_bias_proxy",
    )
    output: dict[str, Any] = {}
    for metric in metrics:
        directions = Counter(str(row.get(f"direction_{metric}", "")) for row in comparisons)
        output[metric] = {
            "phase48_mean": float(np.mean([to_float(row[f"phase48_{metric}"]) for row in comparisons])),
            "phase52_mean": float(np.mean([to_float(row[f"phase52_{metric}"]) for row in comparisons])),
            "mean_delta": float(np.mean([to_float(row[f"delta_{metric}"]) for row in comparisons])),
            "improved_scenarios": directions["improved"],
            "unchanged_scenarios": directions["unchanged"],
            "degraded_scenarios": directions["degraded"],
        }
    output["warning_transitions"] = dict(
        Counter(str(row["warning_label_transition"]) for row in comparisons)
    )
    output["matched_scenarios"] = len(comparisons)
    output["unmatched_scenarios"] = len(result["comparison_rows"]) - len(comparisons)
    return output


def interpretation_text(aggregate: dict[str, Any], warning_counts: dict[str, int]) -> str:
    favorable = all(
        aggregate[metric]["phase52_mean"] <= aggregate[metric]["phase48_mean"]
        for metric in (
            "rmse", "mae", "false_dry_rate", "false_wet_rate",
            "absolute_peak_depth_error", "absolute_peak_timing_error",
            "absolute_relative_volume_bias_proxy",
        )
    ) and aggregate["wet_dry_iou"]["phase52_mean"] >= aggregate["wet_dry_iou"]["phase48_mean"]
    warning_not_degraded = warning_counts["high-risk"] <= REFERENCE_WARNING_COUNTS["high-risk"]
    physical_degraded = (
        aggregate["absolute_relative_volume_bias_proxy"]["phase52_mean"]
        > aggregate["absolute_relative_volume_bias_proxy"]["phase48_mean"]
    )
    if favorable and warning_not_degraded:
        return (
            "Phase 52 improves the matched aggregate reliability, wet/dry, peak/timing, and "
            "volume-response proxy diagnostics without increasing high-risk warning counts. This "
            "supports considering a later reviewed seed-replication decision, but Phase 53 does "
            "not authorize seed replication or 256x256 training."
        )
    if physical_degraded or not warning_not_degraded:
        return (
            "Phase 52 retains aggregate gains, but warning or physical-proxy diagnostics degrade. "
            "Seed replication and 256x256 training remain deferred; Phase 53 authorizes no new training."
        )
    return (
        "Phase 52 shows mixed diagnostic improvement with persistent failure modes. Any seed "
        "replication decision requires a later review, and 256x256 training remains deferred."
    )


def build_summary(result: dict[str, Any], readiness: dict[str, Any]) -> dict[str, Any]:
    scenario_rows = result["scenario_rows"]
    warning_counts = ordered_warning_counts(result["warning_rows"], "phase53_warning_level")
    aggregate = aggregate_comparison(result)
    interpretation = interpretation_text(aggregate, warning_counts)
    return {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "phase": 53,
        "selected_decision": SELECTED_DECISION,
        "checkpoint_found": True,
        "checkpoint_path": display_path(CHECKPOINT_PATH),
        "checkpoint_epoch": 40,
        "diagnostics_executed": True,
        "evaluated_split": "test",
        "evaluated_scenarios": len(scenario_rows),
        "evaluated_windows": result["evaluated_windows"],
        "inference_device": result["device"],
        "phase52_mean_rmse": mean(scenario_rows, "rmse"),
        "phase52_median_rmse": median(scenario_rows, "rmse"),
        "phase52_mean_mae": mean(scenario_rows, "mae"),
        "phase52_median_mae": median(scenario_rows, "mae"),
        "phase52_mean_wet_dry_iou": mean(scenario_rows, "wet_dry_iou"),
        "phase52_median_wet_dry_iou": median(scenario_rows, "wet_dry_iou"),
        "phase52_mean_false_dry_rate": mean(scenario_rows, "false_dry_rate"),
        "phase52_median_false_dry_rate": median(scenario_rows, "false_dry_rate"),
        "phase52_mean_false_wet_rate": mean(scenario_rows, "false_wet_rate"),
        "phase52_median_false_wet_rate": median(scenario_rows, "false_wet_rate"),
        "phase52_mean_absolute_relative_volume_bias_proxy": mean(
            scenario_rows, "absolute_relative_volume_bias_proxy"
        ),
        "phase52_warning_level_counts": warning_counts,
        "phase48_reference_warning_level_counts": REFERENCE_WARNING_COUNTS,
        "warning_label_transition_counts": aggregate["warning_transitions"],
        "matched_diagnostic_comparison": aggregate,
        "diagnostic_change_interpretation": interpretation,
        "warning_thresholds_source": display_path(PHASE48_DIR / "phase48_reliability_summary.json"),
        "warning_thresholds": result["thresholds"],
        "warning_labels_are_probabilities": False,
        "volume_metrics_are_physical_proxies_only": True,
        "strict_conservation_claimed": False,
        "full_mass_conservation_claimed": False,
        "hydrodynamic_closure_claimed": False,
        "production_readiness_claimed": False,
        "seed_replication_authorized": False,
        "resolution_256_training_authorized": False,
        "no_training": True,
        "no_swe_pinn": True,
        "level5_supported": False,
        "readiness": readiness,
        "outputs": {
            name: display_path(OUTPUT_DIR / name)
            for name in (
                "phase53_diagnostic_readiness.json",
                "scenario_reliability_metrics.csv",
                "step_reliability_metrics.csv",
                "wet_dry_error_metrics.csv",
                "peak_depth_timing_metrics.csv",
                "volume_response_proxy_metrics.csv",
                "location_type_summary.csv",
                "reliability_warning_levels.csv",
                "phase52_vs_phase48_diagnostic_comparison.csv",
                "phase53_diagnostics_summary.json",
                "phase53_diagnostics_summary.md",
            )
        },
    }


def write_summary_markdown(summary: dict[str, Any]) -> None:
    counts = summary["phase52_warning_level_counts"]
    ref = summary["phase48_reference_warning_level_counts"]
    transitions = summary["warning_label_transition_counts"]
    lines = [
        "# Phase 53 Phase 52 Diagnostics Review",
        "",
        f"- selected_decision: `{summary['selected_decision']}`",
        f"- checkpoint_found: `{bool_text(summary['checkpoint_found'])}`",
        f"- diagnostics_executed: `{bool_text(summary['diagnostics_executed'])}`",
        f"- evaluated_split: `{summary['evaluated_split']}`",
        f"- evaluated_scenarios: `{summary['evaluated_scenarios']}`",
        f"- evaluated_windows: `{summary['evaluated_windows']}`",
        f"- phase52_mean_rmse: `{summary['phase52_mean_rmse']}`",
        f"- phase52_mean_mae: `{summary['phase52_mean_mae']}`",
        f"- phase52_mean_wet_dry_iou: `{summary['phase52_mean_wet_dry_iou']}`",
        f"- phase52_mean_false_dry_rate: `{summary['phase52_mean_false_dry_rate']}`",
        f"- phase52_mean_false_wet_rate: `{summary['phase52_mean_false_wet_rate']}`",
        "- phase52_mean_absolute_relative_volume_bias_proxy: "
        f"`{summary['phase52_mean_absolute_relative_volume_bias_proxy']}`",
        "",
        "## Warning Comparison",
        "",
        f"| Warning level | Phase 48/49 | Phase 52/53 |",
        "|---|---:|---:|",
        f"| reliable | {ref['reliable']} | {counts['reliable']} |",
        f"| caution | {ref['caution']} | {counts['caution']} |",
        f"| high-risk | {ref['high-risk']} | {counts['high-risk']} |",
        "",
        f"Transitions: `{transitions}`.",
        "",
        "## Interpretation",
        "",
        summary["diagnostic_change_interpretation"],
        "",
        "Warning labels are conservative diagnostic screening labels, not calibrated probabilities. "
        "Summed-depth volume metrics are physical-response proxies only and do not demonstrate strict "
        "conservation, full mass conservation, hydrodynamic closure, SWE consistency, or Level 5 support.",
        "",
        "Phase 53 ran no training and does not authorize seed replication, seed123, seed202, "
        "256x256, tile, multiscale, full-resolution, sweep, loss redesign, SWE, or PINN work.",
    ]
    repo_path(OUTPUT_DIR / "phase53_diagnostics_summary.md").write_text(
        "\n".join(lines), encoding="utf-8"
    )


def make_figures(summary: dict[str, Any], result: dict[str, Any]) -> list[str]:
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        return []

    figures_dir = repo_path(OUTPUT_DIR / "figures")
    figures_dir.mkdir(parents=True, exist_ok=True)
    generated: list[str] = []
    colors = ["#4778A8", "#F2B134", "#C44E52"]

    def save(name: str) -> None:
        plt.tight_layout()
        plt.savefig(figures_dir / name, dpi=180, bbox_inches="tight")
        plt.close()
        generated.append(name)

    levels = ["reliable", "caution", "high-risk"]
    ref = summary["phase48_reference_warning_level_counts"]
    current = summary["phase52_warning_level_counts"]
    x = np.arange(len(levels))
    plt.figure(figsize=(7, 4.5))
    plt.bar(x - 0.18, [ref[level] for level in levels], 0.36, label="Phase 48/49", color="#9EA3A8")
    plt.bar(x + 0.18, [current[level] for level in levels], 0.36, label="Phase 52/53", color=colors)
    plt.xticks(x, levels)
    plt.ylabel("Scenario count")
    plt.title("Conservative warning-level counts")
    plt.legend()
    save("phase53_warning_level_counts_comparison.png")

    aggregate = summary["matched_diagnostic_comparison"]
    labels = ["False dry", "False wet"]
    old = [aggregate["false_dry_rate"]["phase48_mean"], aggregate["false_wet_rate"]["phase48_mean"]]
    new = [aggregate["false_dry_rate"]["phase52_mean"], aggregate["false_wet_rate"]["phase52_mean"]]
    plt.figure(figsize=(7, 4.5))
    plt.bar(np.arange(2) - 0.18, old, 0.36, label="Phase 48", color="#9EA3A8")
    plt.bar(np.arange(2) + 0.18, new, 0.36, label="Phase 52", color="#4778A8")
    plt.xticks(np.arange(2), labels)
    plt.ylabel("Mean rate")
    plt.title("Wet/dry error comparison")
    plt.legend()
    save("phase53_false_dry_false_wet_comparison.png")

    comparison = result["comparison_rows"]
    old_volume = [to_float(row.get("phase48_signed_volume_bias_proxy")) for row in comparison]
    new_volume = [to_float(row.get("phase52_signed_volume_bias_proxy")) for row in comparison]
    plt.figure(figsize=(7, 4.5))
    plt.scatter(old_volume, new_volume, alpha=0.75, color="#4778A8")
    limit = max([abs(value) for value in old_volume + new_volume] + [0.01])
    plt.plot([-limit, limit], [-limit, limit], linestyle="--", color="#666666")
    plt.xlabel("Phase 48 signed volume-bias proxy")
    plt.ylabel("Phase 52 signed volume-bias proxy")
    plt.title("Matched scenario volume-response proxy")
    save("phase53_volume_bias_proxy_comparison.png")

    metric_labels = ["RMSE", "MAE", "1 - IoU", "False dry", "False wet", "Abs. volume bias"]
    old_values = [
        aggregate["rmse"]["phase48_mean"],
        aggregate["mae"]["phase48_mean"],
        1.0 - aggregate["wet_dry_iou"]["phase48_mean"],
        aggregate["false_dry_rate"]["phase48_mean"],
        aggregate["false_wet_rate"]["phase48_mean"],
        aggregate["absolute_relative_volume_bias_proxy"]["phase48_mean"],
    ]
    new_values = [
        aggregate["rmse"]["phase52_mean"],
        aggregate["mae"]["phase52_mean"],
        1.0 - aggregate["wet_dry_iou"]["phase52_mean"],
        aggregate["false_dry_rate"]["phase52_mean"],
        aggregate["false_wet_rate"]["phase52_mean"],
        aggregate["absolute_relative_volume_bias_proxy"]["phase52_mean"],
    ]
    positions = np.arange(len(metric_labels))
    plt.figure(figsize=(9, 4.8))
    plt.bar(positions - 0.18, old_values, 0.36, label="Phase 48", color="#9EA3A8")
    plt.bar(positions + 0.18, new_values, 0.36, label="Phase 52", color="#4778A8")
    plt.xticks(positions, metric_labels, rotation=20, ha="right")
    plt.ylabel("Mean diagnostic value (lower is favorable)")
    plt.title("Key matched diagnostic metrics")
    plt.legend()
    save("phase53_key_diagnostic_metric_comparison.png")

    (figures_dir / "phase53_figure_summary.md").write_text(
        "# Phase 53 Figure Summary\n\n"
        + "\n".join(f"- `{name}`" for name in generated)
        + "\n\nFigures use retained Phase 48 and Phase 53 diagnostic tables only. Warning labels "
        "are conservative screening labels, not calibrated probabilities.\n",
        encoding="utf-8",
    )
    generated.append("phase53_figure_summary.md")
    return generated


def print_terminal_summary(summary: dict[str, Any]) -> None:
    for key in (
        "selected_decision",
        "checkpoint_found",
        "diagnostics_executed",
        "evaluated_scenarios",
        "evaluated_windows",
        "phase52_warning_level_counts",
        "phase48_reference_warning_level_counts",
        "no_training",
        "level5_supported",
        "no_swe_pinn",
    ):
        value = summary.get(key)
        if isinstance(value, bool):
            value = bool_text(value)
        print(f"{key}={value}")


def write_blocked(reason: str, checks: dict[str, Any]) -> None:
    readiness = base_readiness(
        selected_decision=BLOCKED_DECISION,
        checkpoint_found=repo_path(CHECKPOINT_PATH).exists(),
        diagnostics_executed=False,
        notes=[reason],
        checks=checks,
    )
    write_json(OUTPUT_DIR / "phase53_diagnostic_readiness.json", readiness)
    summary = {
        **readiness,
        "evaluated_scenarios": 0,
        "evaluated_windows": 0,
        "phase52_mean_rmse": None,
        "phase52_mean_mae": None,
        "phase52_mean_wet_dry_iou": None,
        "phase52_mean_false_dry_rate": None,
        "phase52_mean_false_wet_rate": None,
        "phase52_mean_absolute_relative_volume_bias_proxy": None,
        "phase52_warning_level_counts": {"reliable": 0, "caution": 0, "high-risk": 0},
        "phase48_reference_warning_level_counts": REFERENCE_WARNING_COUNTS,
        "diagnostic_change_interpretation": reason,
    }
    write_json(OUTPUT_DIR / "phase53_diagnostics_summary.json", summary)
    print_terminal_summary(summary)


def main() -> None:
    repo_path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
    checks = {display_path(path): repo_path(path).exists() for path in REQUIRED_INPUTS}
    missing = [path for path, found in checks.items() if not found]
    if missing:
        write_blocked(f"Missing required Phase 53 inputs: {missing}", checks)
        return

    try:
        config = load_json(CONFIG_PATH)
        validate_config(config)
        _, training_summary, _ = validate_retained_artifacts(config)
        checkpoint = load_checkpoint_metadata(config)
        thresholds = phase48_thresholds()
        phase49_summary = read_json(PHASE49_DIR / "warning_framework_summary.json")
        if phase49_summary.get("warning_level_counts") != REFERENCE_WARNING_COUNTS:
            raise ValueError("Phase 49 reference warning counts do not match 1/12/35.")
        if int(training_summary.get("test_samples", 0)) != EXPECTED_TEST_WINDOWS:
            raise ValueError("Phase 52 training summary test-window count is not 384.")
        if not thresholds:
            raise ValueError("Phase 48 warning thresholds are unavailable.")
    except Exception as exc:
        write_blocked(f"Readiness validation failed: {exc}", checks)
        return

    readiness = base_readiness(
        selected_decision="phase53_diagnostics_requires_inference_pass",
        checkpoint_found=True,
        diagnostics_executed=False,
        notes=[
            "Phase 52 epoch-40 best checkpoint loaded successfully.",
            "Phase 52 retained metrics are mutually consistent.",
            "Phase 47/48 test basis and fixed Phase 48 warning thresholds were recovered.",
        ],
        checks={
            **checks,
            "config_valid": True,
            "checkpoint_epoch_40": True,
            "retained_metrics_consistent": True,
            "phase48_thresholds_recovered": True,
            "expected_test_scenarios": EXPECTED_SCENARIOS,
            "expected_test_windows": EXPECTED_TEST_WINDOWS,
            "inference_only": True,
        },
    )
    write_json(OUTPUT_DIR / "phase53_diagnostic_readiness.json", readiness)

    try:
        set_seed(int(config["seed"]))
        result = run_inference(config, checkpoint)
        if len(result["scenario_rows"]) != EXPECTED_SCENARIOS:
            raise ValueError(
                f"Expected {EXPECTED_SCENARIOS} evaluated scenarios, got {len(result['scenario_rows'])}."
            )
        write_tables(result)
        readiness.update(
            {
                "selected_decision": SELECTED_DECISION,
                "diagnostics_executed": True,
                "notes": readiness["notes"]
                + ["No-gradient Phase 52 inference completed on 48 test scenarios and 384 windows."],
            }
        )
        write_json(OUTPUT_DIR / "phase53_diagnostic_readiness.json", readiness)
        summary = build_summary(result, readiness)
        write_json(OUTPUT_DIR / "phase53_diagnostics_summary.json", summary)
        write_summary_markdown(summary)
        summary["figures_generated"] = make_figures(summary, result)
        write_json(OUTPUT_DIR / "phase53_diagnostics_summary.json", summary)
    except Exception as exc:
        write_blocked(f"Diagnostic evaluation failed: {exc}", checks)
        return

    print_terminal_summary(summary)


if __name__ == "__main__":
    main()
