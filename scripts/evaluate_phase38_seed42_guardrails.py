from __future__ import annotations

import argparse
import csv
import json
import math
import zipfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG_PATH = Path("configs/train_phase36_manhole_false_dry_guardrail_seed42_40e.json")
DEFAULT_RUN_ROOT = Path("runs/phase36_manhole_false_dry_guardrail_seed42_40e")
DEFAULT_THRESHOLD_DIR = Path("analysis/phase34_pilot_thresholds")
DEFAULT_PHASE31_DIR = Path("analysis/phase31_physics_input_recovery_readiness")
DEFAULT_DATASET_ROOT = Path(r"E:\BaiduNetdiskDownload\urbanflood24_lite_release\urbanflood24_lite")
DEFAULT_OUTPUT_DIR = Path("analysis/phase38_seed42_pilot_training_guardrail_evaluation")

DEM_VALID_THRESHOLD = 99.0
HIGH_IMPERVIOUS_THRESHOLD = 0.8
WET_THRESHOLD = 0.05
EPS = 1.0e-12

STANDARD_CHECK_IDS = ("AT08", "AT09", "AT10", "AT11", "AT12")
LOWER_IS_BETTER = {
    "rmse",
    "mae",
    "false_dry_rate",
    "false_wet_rate",
    "absolute_relative_volume_bias_proxy",
}

REGION_ORDER = (
    "valid_domain",
    "boundary_ring",
    "high_impervious_valid",
    "manhole_nonzero_valid",
)


@dataclass(frozen=True)
class MetricKey:
    metric_group: str
    metric_name: str
    region: str


def repo_path(path: Path) -> Path:
    path = path.expanduser()
    if path.is_absolute():
        return path
    return (REPO_ROOT / path).resolve()


def display_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT)).replace("\\", "/")
    except ValueError:
        return str(path)


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"Expected JSON object: {display_path(path)}")
    return data


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def safe_float(value: Any) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError, OverflowError):
        return None
    if math.isnan(number) or math.isinf(number):
        return None
    return number


def metric_text(value: Any) -> str:
    number = safe_float(value)
    if number is None:
        return "n/a"
    return f"{number:.12g}"


def pass_fail_status(value: float | None, threshold: float | None, direction: str) -> str:
    if value is None or threshold is None:
        return "not_evaluated"
    if direction == "lower_or_equal":
        return "pass" if value <= threshold else "fail"
    if direction == "higher_or_equal":
        return "pass" if value >= threshold else "fail"
    if direction == "claim_scope":
        return "pass"
    raise ValueError(f"Unsupported direction: {direction}")


def direction_for(metric_name: str, threshold_type: str) -> str:
    if threshold_type == "mandatory_claim_boundary" or metric_name == "claim_scope":
        return "claim_scope"
    if metric_name in {"wet_dry_iou", "rollout_stability"}:
        return "higher_or_equal"
    return "lower_or_equal"


def threshold_value(row: dict[str, str]) -> float | None:
    return safe_float(row.get("numeric_threshold"))


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


def adjacent_to_invalid_or_border(valid_mask: np.ndarray, invalid_or_high_mask: np.ndarray) -> np.ndarray:
    adjacent = np.zeros(valid_mask.shape, dtype=bool)
    adjacent[1:, :] |= invalid_or_high_mask[:-1, :]
    adjacent[:-1, :] |= invalid_or_high_mask[1:, :]
    adjacent[:, 1:] |= invalid_or_high_mask[:, :-1]
    adjacent[:, :-1] |= invalid_or_high_mask[:, 1:]

    border = np.zeros(valid_mask.shape, dtype=bool)
    border[0, :] = True
    border[-1, :] = True
    border[:, 0] = True
    border[:, -1] = True
    return valid_mask & (adjacent | border)


def finite_2d(array: np.ndarray, path: Path) -> np.ndarray:
    values = np.asarray(array, dtype=np.float64)
    if values.ndim != 2:
        raise ValueError(f"{display_path(path)} must be 2D, got shape {values.shape}")
    return values


def build_location_masks(dataset_root: Path) -> tuple[dict[str, dict[str, np.ndarray]], list[str]]:
    geodata_root = dataset_root / "test" / "geodata"
    if not geodata_root.exists():
        raise FileNotFoundError(f"Missing test geodata directory: {geodata_root}")

    notes: list[str] = []
    masks_by_location: dict[str, dict[str, np.ndarray]] = {}
    for location_dir in sorted(path for path in geodata_root.glob("location*") if path.is_dir()):
        location = location_dir.name
        dem_path = location_dir / "absolute_DEM.npy"
        impervious_path = location_dir / "impervious.npy"
        manhole_path = location_dir / "manhole.npy"
        for required in (dem_path, impervious_path, manhole_path):
            if not required.exists():
                raise FileNotFoundError(f"Missing static mask input: {required}")

        dem = finite_2d(np.load(dem_path, allow_pickle=False), dem_path)
        impervious = finite_2d(np.load(impervious_path, allow_pickle=False), impervious_path)
        manhole = finite_2d(np.load(manhole_path, allow_pickle=False), manhole_path)
        if dem.shape != impervious.shape or dem.shape != manhole.shape:
            raise ValueError(
                f"Static map shapes differ for {location}: dem={dem.shape}, "
                f"impervious={impervious.shape}, manhole={manhole.shape}"
            )

        finite_dem = np.isfinite(dem)
        valid_domain = finite_dem & (dem < DEM_VALID_THRESHOLD)
        invalid_or_high = (~finite_dem) | (dem >= DEM_VALID_THRESHOLD)
        boundary_ring = adjacent_to_invalid_or_border(valid_domain, invalid_or_high)
        high_impervious_valid = valid_domain & np.isfinite(impervious) & (impervious >= HIGH_IMPERVIOUS_THRESHOLD)
        manhole_nonzero_valid = valid_domain & np.isfinite(manhole) & (manhole > 0.0)

        masks_by_location[location] = {
            "valid_domain": valid_domain,
            "boundary_ring": boundary_ring,
            "high_impervious_valid": high_impervious_valid,
            "manhole_nonzero_valid": manhole_nonzero_valid,
        }
        notes.append(
            f"{location}: valid={int(valid_domain.sum())}, boundary_ring={int(boundary_ring.sum())}, "
            f"high_impervious_valid={int(high_impervious_valid.sum())}, "
            f"manhole_nonzero_valid={int(manhole_nonzero_valid.sum())}"
        )
    if not masks_by_location:
        raise FileNotFoundError(f"No location* static masks found under {geodata_root}")
    return masks_by_location, notes


def empty_accumulator(region: str) -> dict[str, Any]:
    return {
        "region": region,
        "sample_frame_count": 0,
        "pixel_count": 0,
        "target_wet_count": 0,
        "prediction_wet_count": 0,
        "target_dry_count": 0,
        "false_dry_count": 0,
        "false_wet_count": 0,
        "sum_sq_error": 0.0,
        "sum_abs_error": 0.0,
        "sum_error": 0.0,
        "false_dry_volume_loss_proxy": 0.0,
        "false_wet_volume_excess_proxy": 0.0,
        "target_volume_proxy": 0.0,
        "predicted_volume_proxy": 0.0,
        "locations": set(),
        "batches": set(),
    }


def update_accumulator(
    acc: dict[str, Any],
    prediction: np.ndarray,
    target: np.ndarray,
    mask: np.ndarray,
    threshold: float,
) -> None:
    if mask.shape != target.shape:
        raise ValueError(f"Mask shape {mask.shape} does not match frame shape {target.shape}")
    if not np.any(mask):
        return

    pred = np.where(np.isfinite(prediction[mask]), prediction[mask], 0.0)
    tgt = np.where(np.isfinite(target[mask]), target[mask], 0.0)
    diff = pred - tgt
    pred_positive = np.maximum(pred, 0.0)
    target_positive = np.maximum(tgt, 0.0)

    target_wet = tgt > threshold
    prediction_wet = pred > threshold
    false_dry = target_wet & ~prediction_wet
    false_wet = ~target_wet & prediction_wet

    acc["sample_frame_count"] += 1
    acc["pixel_count"] += int(mask.sum())
    acc["target_wet_count"] += int(target_wet.sum())
    acc["prediction_wet_count"] += int(prediction_wet.sum())
    acc["target_dry_count"] += int((~target_wet).sum())
    acc["false_dry_count"] += int(false_dry.sum())
    acc["false_wet_count"] += int(false_wet.sum())
    acc["sum_sq_error"] += float(np.sum(diff * diff))
    acc["sum_abs_error"] += float(np.sum(np.abs(diff)))
    acc["sum_error"] += float(np.sum(diff))
    acc["target_volume_proxy"] += float(np.sum(target_positive))
    acc["predicted_volume_proxy"] += float(np.sum(pred_positive))
    acc["false_dry_volume_loss_proxy"] += float(np.sum(np.maximum(tgt[false_dry] - pred[false_dry], 0.0)))
    acc["false_wet_volume_excess_proxy"] += float(np.sum(np.maximum(pred[false_wet] - tgt[false_wet], 0.0)))


def finalize_accumulator(acc: dict[str, Any]) -> dict[str, Any]:
    pixel_count = int(acc["pixel_count"])
    target_wet = int(acc["target_wet_count"])
    target_dry = int(acc["target_dry_count"])
    target_volume = float(acc["target_volume_proxy"])
    volume_bias = float(acc["predicted_volume_proxy"]) - target_volume
    row = dict(acc)
    row["rmse"] = math.sqrt(float(acc["sum_sq_error"]) / pixel_count) if pixel_count else None
    row["mae"] = float(acc["sum_abs_error"]) / pixel_count if pixel_count else None
    row["false_dry_rate"] = int(acc["false_dry_count"]) / target_wet if target_wet else None
    row["false_wet_rate"] = int(acc["false_wet_count"]) / target_dry if target_dry else None
    row["volume_bias_proxy"] = volume_bias
    row["relative_volume_bias_proxy"] = volume_bias / target_volume if target_volume > EPS else None
    row["absolute_relative_volume_bias_proxy"] = (
        abs(row["relative_volume_bias_proxy"]) if row["relative_volume_bias_proxy"] is not None else None
    )
    row["locations"] = ",".join(sorted(acc["locations"]))
    row["batch_count"] = len(acc["batches"])
    del row["batches"]
    return row


def list_forecast_files(run_root: Path) -> list[Path]:
    eval_dir = run_root / "evaluation_test"
    return [
        batch_dir / "forecast_maps.npz"
        for batch_dir in sorted(eval_dir.glob("test_batch_*"), key=lambda item: item.name)
        if batch_dir.is_dir() and (batch_dir / "forecast_maps.npz").exists()
    ]


def load_summary_metadata(summary_path: Path) -> list[dict[str, Any]]:
    summary = read_json(summary_path)
    metadata = summary.get("metadata")
    if not isinstance(metadata, list):
        raise ValueError(f"Missing metadata list in {display_path(summary_path)}")
    clean: list[dict[str, Any]] = []
    for index, item in enumerate(metadata):
        if not isinstance(item, dict):
            raise ValueError(f"Metadata entry {index} is not an object in {display_path(summary_path)}")
        clean.append(item)
    return clean


def compute_masked_metrics(run_root: Path, dataset_root: Path, threshold: float) -> tuple[dict[MetricKey, float], list[dict[str, Any]], str]:
    masks_by_location, mask_notes = build_location_masks(dataset_root)
    forecast_files = list_forecast_files(run_root)
    if not forecast_files:
        raise FileNotFoundError(f"No forecast_maps.npz files found under {display_path(run_root / 'evaluation_test')}")

    aggregates = {region: empty_accumulator(region) for region in REGION_ORDER}
    for forecast_file in forecast_files:
        try:
            with np.load(forecast_file, allow_pickle=False) as data:
                if "prediction" not in data or "target" not in data:
                    raise KeyError("prediction or target missing")
                prediction = normalize_forecast_array(data["prediction"], "prediction", forecast_file)
                target = normalize_forecast_array(data["target"], "target", forecast_file)
        except (OSError, KeyError, ValueError, zipfile.BadZipFile) as exc:
            raise ValueError(f"Could not read {display_path(forecast_file)}: {exc}") from exc
        if prediction.shape != target.shape:
            raise ValueError(
                f"prediction shape {prediction.shape} does not match target shape {target.shape} in "
                f"{display_path(forecast_file)}"
            )

        summary_path = forecast_file.parent / "summary.json"
        metadata = load_summary_metadata(summary_path)
        if len(metadata) != prediction.shape[0]:
            raise ValueError(
                f"Metadata length {len(metadata)} does not match batch size {prediction.shape[0]} in "
                f"{display_path(summary_path)}"
            )

        for sample_index, sample_metadata in enumerate(metadata):
            location = str(sample_metadata.get("location", ""))
            if location not in masks_by_location:
                raise ValueError(f"Metadata location {location!r} has no recovered static mask")
            for timestep in range(prediction.shape[1]):
                pred_frame = prediction[sample_index, timestep, 0]
                target_frame = target[sample_index, timestep, 0]
                for region in REGION_ORDER:
                    acc = aggregates[region]
                    acc["locations"].add(location)
                    acc["batches"].add(forecast_file.parent.name)
                    update_accumulator(acc, pred_frame, target_frame, masks_by_location[location][region], threshold)

    rows = [finalize_accumulator(aggregates[region]) for region in REGION_ORDER]
    metric_lookup: dict[MetricKey, float] = {}
    for row in rows:
        region = str(row["region"])
        group = "valid_domain_masked" if region == "valid_domain" else "guardrail_masked"
        if region == "manhole_nonzero_valid":
            group = "manhole_nonzero_target"
        for metric_name in (
            "rmse",
            "mae",
            "false_dry_rate",
            "false_wet_rate",
            "absolute_relative_volume_bias_proxy",
        ):
            value = safe_float(row.get(metric_name))
            if value is not None:
                metric_lookup[MetricKey(group, metric_name, region)] = value
    evidence = (
        f"computed from {len(forecast_files)} forecast map batches and static masks under "
        f"{dataset_root}; {'; '.join(mask_notes)}"
    )
    return metric_lookup, rows, evidence


def standard_metric_lookup(metrics: dict[str, Any]) -> dict[MetricKey, float]:
    lookup: dict[MetricKey, float] = {}
    for metric_name in ("rmse", "mae", "wet_dry_iou", "rollout_stability", "step_rmse_std"):
        value = safe_float(metrics.get(metric_name))
        if value is not None:
            lookup[MetricKey("standard", metric_name, "all_evaluated_cells")] = value
    return lookup


def baseline_lookup(baseline_rows: list[dict[str, str]]) -> dict[MetricKey, dict[str, float]]:
    lookup: dict[MetricKey, dict[str, float]] = {}
    for row in baseline_rows:
        key = MetricKey(row["metric_group"], row["metric_name"], row["region"])
        lookup[key] = {
            "phase25": float(row["phase25_seed42"]),
            "phase27": float(row["phase27_seed42"]),
            "phase29": float(row["phase29_seed42"]),
        }
    return lookup


def build_standard_checks(
    acceptance_rows: list[dict[str, str]], metrics_lookup: dict[MetricKey, float]
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in acceptance_rows:
        if row.get("threshold_id") not in STANDARD_CHECK_IDS:
            continue
        key = MetricKey(row["metric_group"], row["metric_name"], row["region"])
        value = metrics_lookup.get(key)
        threshold = threshold_value(row)
        direction = direction_for(row["metric_name"], row.get("threshold_type", ""))
        status = pass_fail_status(value, threshold, direction)
        rows.append(
            {
                "threshold_id": row["threshold_id"],
                "metric_group": row["metric_group"],
                "metric_name": row["metric_name"],
                "region": row["region"],
                "observed_value": value,
                "direction": direction,
                "numeric_threshold": threshold,
                "status": status,
                "required_for_pilot_acceptance": row["required_for_pilot_acceptance"],
                "evidence": "runs/phase36_manhole_false_dry_guardrail_seed42_40e/evaluation_test/metrics.json",
            }
        )
    return rows


def build_acceptance_checks(
    acceptance_rows: list[dict[str, str]],
    all_metrics: dict[MetricKey, float],
    masked_evidence: str,
    masked_error: str | None,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in acceptance_rows:
        key = MetricKey(row["metric_group"], row["metric_name"], row["region"])
        direction = direction_for(row["metric_name"], row.get("threshold_type", ""))
        threshold = threshold_value(row)
        value = all_metrics.get(key)
        evidence = "standard evaluation metrics"
        status = pass_fail_status(value, threshold, direction)
        note = row["acceptance_rule"]

        if row["threshold_id"] == "AT14":
            value = "Level 4+ proxy diagnostics only"
            status = "pass"
            evidence = "script output wording and claim scope"
            note = "No Level 5, SWE/PINN residual, strict conservation, full mass conservation, or hydrodynamic closure claim is made."
        elif value is None and row["metric_group"] != "standard":
            status = "not_evaluated"
            evidence = masked_error or "masked forecast-map inputs were unavailable"
            note = "Masked metric was not computed; pilot success cannot be claimed from incomplete evidence."
        elif row["metric_group"] != "standard":
            evidence = masked_evidence

        rows.append(
            {
                "threshold_id": row["threshold_id"],
                "metric_group": row["metric_group"],
                "metric_name": row["metric_name"],
                "region": row["region"],
                "observed_value": value,
                "direction": direction,
                "numeric_threshold": threshold,
                "status": status,
                "required_for_pilot_acceptance": row["required_for_pilot_acceptance"],
                "evidence": evidence,
                "notes": note,
            }
        )
    return rows


def metric_value(metrics: dict[MetricKey, float], group: str, metric: str, region: str) -> float | None:
    return metrics.get(MetricKey(group, metric, region))


def build_rejection_checks(
    rejection_rows: list[dict[str, str]],
    all_metrics: dict[MetricKey, float],
    baselines: dict[MetricKey, dict[str, float]],
    masked_evidence: str,
    masked_error: str | None,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []

    def missing_masked(rule: dict[str, str]) -> dict[str, Any]:
        return {
            "rejection_id": rule["rejection_id"],
            "rejection_rule": rule["rejection_rule"],
            "triggered": False,
            "status": "not_evaluated",
            "evidence": masked_error or "masked forecast-map inputs were unavailable",
            "notes": "Required masked evidence was not available; this rule cannot be used to claim acceptance.",
        }

    for rule in rejection_rows:
        rejection_id = rule["rejection_id"]
        triggered = False
        status = "not_triggered"
        evidence = "standard evaluation metrics"
        notes = rule["trigger_condition"]

        if rejection_id == "RT01":
            candidate = {
                "absolute_relative_volume_bias_proxy": metric_value(
                    all_metrics, "valid_domain_masked", "absolute_relative_volume_bias_proxy", "valid_domain"
                ),
                "rmse": metric_value(all_metrics, "valid_domain_masked", "rmse", "valid_domain"),
                "mae": metric_value(all_metrics, "valid_domain_masked", "mae", "valid_domain"),
                "false_dry_rate": metric_value(all_metrics, "valid_domain_masked", "false_dry_rate", "valid_domain"),
                "false_wet_rate": metric_value(all_metrics, "valid_domain_masked", "false_wet_rate", "valid_domain"),
            }
            base = {
                metric: baselines[MetricKey("valid_domain_masked", metric, "valid_domain")]["phase27"]
                for metric in candidate
                if MetricKey("valid_domain_masked", metric, "valid_domain") in baselines
            }
            if len(candidate) != len(base) or any(value is None for value in candidate.values()):
                rows.append(missing_masked(rule))
                continue
            triggered = (
                candidate["absolute_relative_volume_bias_proxy"] < base["absolute_relative_volume_bias_proxy"]
                and candidate["rmse"] > base["rmse"]
                and candidate["mae"] > base["mae"]
                and candidate["false_dry_rate"] > base["false_dry_rate"]
                and candidate["false_wet_rate"] > base["false_wet_rate"]
            )
            evidence = masked_evidence
            notes = f"candidate={candidate}; phase27={base}"
        elif rejection_id == "RT02":
            value = metric_value(all_metrics, "manhole_nonzero_target", "false_dry_rate", "manhole_nonzero_valid")
            if value is None:
                rows.append(missing_masked(rule))
                continue
            triggered = value > 0.131297982994
            evidence = masked_evidence
            notes = f"candidate false_dry_rate={metric_text(value)}; hard threshold=0.131297982994"
        elif rejection_id == "RT03":
            value = metric_value(all_metrics, "guardrail_masked", "false_wet_rate", "high_impervious_valid")
            if value is None:
                rows.append(missing_masked(rule))
                continue
            triggered = value > 0.0239893681941
            evidence = masked_evidence
            notes = f"candidate false_wet_rate={metric_text(value)}; hard threshold=0.0239893681941"
        elif rejection_id == "RT04":
            value = metric_value(all_metrics, "guardrail_masked", "false_dry_rate", "boundary_ring")
            if value is None:
                rows.append(missing_masked(rule))
                continue
            triggered = value > 0.105112739216
            evidence = masked_evidence
            notes = f"candidate false_dry_rate={metric_text(value)}; hard threshold=0.105112739216"
        elif rejection_id == "RT05":
            rmse = metric_value(all_metrics, "standard", "rmse", "all_evaluated_cells")
            mae = metric_value(all_metrics, "standard", "mae", "all_evaluated_cells")
            triggered = (rmse is not None and rmse > 0.0445000304105) or (
                mae is not None and mae > 0.0181490102048
            )
            notes = f"rmse={metric_text(rmse)} threshold=0.0445000304105; mae={metric_text(mae)} threshold=0.0181490102048"
        elif rejection_id == "RT06":
            value = metric_value(all_metrics, "standard", "wet_dry_iou", "all_evaluated_cells")
            triggered = value is not None and value < 0.802801373632
            notes = f"wet_dry_iou={metric_text(value)} threshold=0.802801373632"
        elif rejection_id == "RT07":
            rmse = metric_value(all_metrics, "valid_domain_masked", "rmse", "valid_domain")
            mae = metric_value(all_metrics, "valid_domain_masked", "mae", "valid_domain")
            if rmse is None or mae is None:
                rows.append(missing_masked(rule))
                continue
            triggered = rmse > 0.0470043492351 or mae > 0.0187366452965
            evidence = masked_evidence
            notes = f"valid rmse={metric_text(rmse)}; valid mae={metric_text(mae)}"
        elif rejection_id == "RT08":
            triggered = False
            evidence = "Phase 38 seed42-only evaluation; no seed123/seed202 or sweep executed"
            notes = "Not triggered by this script. Seed expansion or sweeps remain unauthorized and are not used to rescue the result."
        elif rejection_id == "RT09":
            triggered = False
            evidence = "script output wording and claim scope"
            notes = "Not triggered. Outputs are explicitly Level 4+ static-map-aware proxy diagnostics only."

        if triggered:
            status = "triggered"
        rows.append(
            {
                "rejection_id": rejection_id,
                "rejection_rule": rule["rejection_rule"],
                "triggered": triggered,
                "status": status,
                "evidence": evidence,
                "notes": notes,
            }
        )
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
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
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
    if isinstance(value, set):
        return sorted(json_ready(item) for item in value)
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, Path):
        return display_path(value)
    return value


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(json_ready(payload), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def decision_from_checks(
    core_inputs_ok: bool,
    acceptance_rows: list[dict[str, Any]],
    rejection_rows: list[dict[str, Any]],
) -> str:
    if not core_inputs_ok:
        return "training_or_evaluation_failed"
    hard_rt_triggered = any(row["status"] == "triggered" for row in rejection_rows)
    if hard_rt_triggered:
        return "seed42_pilot_rejected"
    required_acceptance = [
        row for row in acceptance_rows if str(row.get("required_for_pilot_acceptance", "")).lower() == "yes"
    ]
    all_required_pass = all(row["status"] == "pass" for row in required_acceptance)
    no_rt_incomplete = all(row["status"] != "not_evaluated" for row in rejection_rows)
    if all_required_pass and no_rt_incomplete:
        return "seed42_pilot_accepted"
    return "seed42_pilot_mixed_requires_review"


def summarize_counts(
    standard_rows: list[dict[str, Any]],
    acceptance_rows: list[dict[str, Any]],
    rejection_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "standard_checks_passed": sum(1 for row in standard_rows if row["status"] == "pass"),
        "standard_checks_failed": sum(1 for row in standard_rows if row["status"] == "fail"),
        "acceptance_checks_passed": sum(1 for row in acceptance_rows if row["status"] == "pass"),
        "acceptance_checks_failed": sum(1 for row in acceptance_rows if row["status"] == "fail"),
        "acceptance_checks_not_evaluated": sum(1 for row in acceptance_rows if row["status"] == "not_evaluated"),
        "rejection_rules_triggered": sum(1 for row in rejection_rows if row["status"] == "triggered"),
        "rejection_rules_not_evaluated": sum(1 for row in rejection_rows if row["status"] == "not_evaluated"),
    }


def write_markdown(path: Path, payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    standard_rows = payload["standard_checks"]
    acceptance_rows = payload["acceptance_checks"]
    rejection_rows = payload["rejection_checks"]
    lines = [
        "# Phase 38 Seed42 Pilot Training Guardrail Evaluation",
        "",
        "This evaluation is Level 4+ static-map-aware proxy scope only. It does not claim Level 5 support, SWE/PINN residuals, strict conservation, full mass conservation, or hydrodynamic closure.",
        "",
        "## Decision",
        "",
        f"- final_decision: `{payload['final_decision']}`",
        f"- standard_checks_passed: `{summary['standard_checks_passed']}`",
        f"- standard_checks_failed: `{summary['standard_checks_failed']}`",
        f"- acceptance_checks_passed: `{summary['acceptance_checks_passed']}`",
        f"- acceptance_checks_failed: `{summary['acceptance_checks_failed']}`",
        f"- acceptance_checks_not_evaluated: `{summary['acceptance_checks_not_evaluated']}`",
        f"- rejection_rules_triggered: `{summary['rejection_rules_triggered']}`",
        f"- rejection_rules_not_evaluated: `{summary['rejection_rules_not_evaluated']}`",
        "",
        "## Standard AT08-AT12",
        "",
        "| ID | Metric | Observed | Threshold | Direction | Status |",
        "| --- | --- | ---: | ---: | --- | --- |",
    ]
    for row in standard_rows:
        lines.append(
            f"| `{row['threshold_id']}` | `{row['metric_name']}` | {metric_text(row['observed_value'])} | "
            f"{metric_text(row['numeric_threshold'])} | `{row['direction']}` | `{row['status']}` |"
        )

    lines.extend(["", "## Failed Acceptance Checks", ""])
    failed_or_missing = [row for row in acceptance_rows if row["status"] != "pass"]
    if not failed_or_missing:
        lines.append("- None.")
    else:
        for row in failed_or_missing:
            lines.append(
                f"- `{row['threshold_id']}` `{row['metric_group']}/{row['metric_name']}/{row['region']}`: "
                f"`{row['status']}` observed `{metric_text(row['observed_value'])}` threshold "
                f"`{metric_text(row['numeric_threshold'])}`. {row['evidence']}"
            )

    lines.extend(["", "## Rejection Rules", ""])
    triggered = [row for row in rejection_rows if row["status"] == "triggered"]
    if not triggered:
        lines.append("- No evaluated hard RT rule triggered.")
    else:
        for row in triggered:
            lines.append(f"- `{row['rejection_id']}` `{row['rejection_rule']}` triggered. {row['notes']}")
    not_evaluated = [row for row in rejection_rows if row["status"] == "not_evaluated"]
    if not_evaluated:
        lines.extend(["", "## Incomplete RT Evidence", ""])
        for row in not_evaluated:
            lines.append(f"- `{row['rejection_id']}` `{row['rejection_rule']}`: {row['evidence']}")

    lines.extend(
        [
            "",
            "## Inputs",
            "",
        ]
    )
    for key, value in payload["inputs"].items():
        lines.append(f"- {key}: `{value}`")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def required_paths(config_path: Path, metrics_path: Path, threshold_dir: Path) -> list[Path]:
    return [
        config_path,
        metrics_path,
        threshold_dir / "acceptance_thresholds.csv",
        threshold_dir / "rejection_thresholds.csv",
        threshold_dir / "baseline_metric_table.csv",
    ]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Evaluate completed Phase 38 seed42 pilot results against Phase 34 AT01-AT14 "
            "and RT01-RT09. This script does not train, modify outputs, run seed123/seed202, "
            "or perform sweeps."
        )
    )
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG_PATH)
    parser.add_argument("--run-root", type=Path, default=DEFAULT_RUN_ROOT)
    parser.add_argument("--threshold-dir", type=Path, default=DEFAULT_THRESHOLD_DIR)
    parser.add_argument("--phase31-dir", type=Path, default=DEFAULT_PHASE31_DIR)
    parser.add_argument("--dataset-root", type=Path, default=DEFAULT_DATASET_ROOT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--wet-threshold", type=float, default=WET_THRESHOLD)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config_path = repo_path(args.config)
    run_root = repo_path(args.run_root)
    threshold_dir = repo_path(args.threshold_dir)
    phase31_dir = repo_path(args.phase31_dir)
    dataset_root = args.dataset_root.expanduser()
    output_dir = repo_path(args.output_dir)
    metrics_path = run_root / "evaluation_test" / "metrics.json"

    missing = [display_path(path) for path in required_paths(config_path, metrics_path, threshold_dir) if not path.exists()]
    core_inputs_ok = not missing
    if missing:
        payload = {
            "phase": 38,
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "claim_scope": "Level 4+ static-map-aware proxy diagnostics only",
            "final_decision": "training_or_evaluation_failed",
            "missing_required_inputs": missing,
            "summary": {
                "standard_checks_passed": 0,
                "standard_checks_failed": 0,
                "acceptance_checks_passed": 0,
                "acceptance_checks_failed": 0,
                "acceptance_checks_not_evaluated": 14,
                "rejection_rules_triggered": 0,
                "rejection_rules_not_evaluated": 9,
            },
            "inputs": {
                "config": display_path(config_path),
                "metrics": display_path(metrics_path),
                "threshold_dir": display_path(threshold_dir),
            },
            "standard_checks": [],
            "acceptance_checks": [],
            "rejection_checks": [],
        }
        output_dir.mkdir(parents=True, exist_ok=True)
        write_json(output_dir / "phase38_guardrail_decision.json", payload)
        write_markdown(output_dir / "phase38_guardrail_decision.md", payload)
        print("standard_checks_passed=0")
        print("standard_checks_failed=0")
        print("acceptance_checks_passed=0")
        print("acceptance_checks_failed=0")
        print("rejection_rules_triggered=0")
        print("final_decision=training_or_evaluation_failed")
        return

    config = read_json(config_path)
    metrics = read_json(metrics_path)
    acceptance_rows = read_csv_rows(threshold_dir / "acceptance_thresholds.csv")
    rejection_rows = read_csv_rows(threshold_dir / "rejection_thresholds.csv")
    baseline_rows = read_csv_rows(threshold_dir / "baseline_metric_table.csv")

    all_metrics = standard_metric_lookup(metrics)
    masked_rows: list[dict[str, Any]] = []
    masked_evidence = ""
    masked_error: str | None = None
    try:
        masked_lookup, masked_rows, masked_evidence = compute_masked_metrics(run_root, dataset_root, args.wet_threshold)
        all_metrics.update(masked_lookup)
    except (FileNotFoundError, ValueError, OSError, json.JSONDecodeError) as exc:
        masked_error = f"not_evaluated: {exc}"

    baselines = baseline_lookup(baseline_rows)
    standard_checks = build_standard_checks(acceptance_rows, all_metrics)
    acceptance_checks = build_acceptance_checks(acceptance_rows, all_metrics, masked_evidence, masked_error)
    rejection_checks = build_rejection_checks(rejection_rows, all_metrics, baselines, masked_evidence, masked_error)
    final_decision = decision_from_checks(core_inputs_ok, acceptance_checks, rejection_checks)
    summary = summarize_counts(standard_checks, acceptance_checks, rejection_checks)

    payload = {
        "phase": 38,
        "candidate": "manhole_nonzero_false_dry_guardrail",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "claim_scope": "Level 4+ static-map-aware proxy diagnostics only",
        "training_command_reviewed": (
            "python scripts/train_model.py --config "
            "configs/train_phase36_manhole_false_dry_guardrail_seed42_40e.json"
        ),
        "evaluation_command_reviewed": (
            "python scripts/evaluate_model.py --config "
            "configs/train_phase36_manhole_false_dry_guardrail_seed42_40e.json --split test"
        ),
        "no_retraining_performed": True,
        "no_seed123_or_seed202_performed": True,
        "no_sweeps_performed": True,
        "config_output_root": config.get("output", {}).get("root"),
        "inputs": {
            "config": display_path(config_path),
            "metrics": display_path(metrics_path),
            "forecast_maps": f"{display_path(run_root / 'evaluation_test')}/test_batch_*/forecast_maps.npz",
            "acceptance_thresholds": display_path(threshold_dir / "acceptance_thresholds.csv"),
            "rejection_thresholds": display_path(threshold_dir / "rejection_thresholds.csv"),
            "baseline_metric_table": display_path(threshold_dir / "baseline_metric_table.csv"),
            "phase31_masked_inputs": display_path(phase31_dir),
            "dataset_root_for_static_masks": str(dataset_root),
        },
        "standard_metrics": metrics,
        "masked_metric_status": "computed" if masked_error is None else "not_evaluated",
        "masked_metric_evidence": masked_evidence if masked_error is None else masked_error,
        "masked_metric_rows": masked_rows,
        "standard_checks": standard_checks,
        "acceptance_checks": acceptance_checks,
        "rejection_checks": rejection_checks,
        "summary": summary,
        "final_decision": final_decision,
        "decision_guardrail": "Do not claim pilot success unless all required acceptance checks pass and no RT rule triggers.",
    }

    output_dir.mkdir(parents=True, exist_ok=True)
    write_csv(output_dir / "phase38_standard_metric_check.csv", standard_checks)
    write_csv(output_dir / "phase38_acceptance_check.csv", acceptance_checks)
    write_csv(output_dir / "phase38_rejection_check.csv", rejection_checks)
    write_json(output_dir / "phase38_guardrail_decision.json", payload)
    write_markdown(output_dir / "phase38_guardrail_decision.md", payload)

    print(f"standard_checks_passed={summary['standard_checks_passed']}")
    print(f"standard_checks_failed={summary['standard_checks_failed']}")
    print(f"acceptance_checks_passed={summary['acceptance_checks_passed']}")
    print(f"acceptance_checks_failed={summary['acceptance_checks_failed']}")
    print(f"rejection_rules_triggered={summary['rejection_rules_triggered']}")
    print(f"final_decision={final_decision}")


if __name__ == "__main__":
    main()
