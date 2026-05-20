from __future__ import annotations

import argparse
import csv
import json
import math
import zipfile
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATASET_ROOT = Path(r"E:\BaiduNetdiskDownload\urbanflood24_lite_release\urbanflood24_lite")
DEFAULT_OUTPUT_DIR = Path("analysis/phase31_physics_input_recovery_readiness")

DEM_VALID_THRESHOLD = 99.0
HIGH_IMPERVIOUS_THRESHOLD = 0.8
WET_THRESHOLD = 0.05
EPS = 1.0e-12
EXPECTED_SHAPE = (128, 128)

RUNS: dict[str, str] = {
    "phase25": "runs/phase25_target_wet_recall_seed42_40e",
    "phase27": "runs/phase27_volume_response_seed42_40e",
    "phase29": "runs/phase29_tolerance_band_volume_seed42_40e",
}

REGION_ORDER = (
    "valid_domain",
    "interior",
    "boundary_ring",
    "high_impervious_valid",
    "manhole_nonzero_valid",
    "invalid_or_high",
)

LOWER_IS_BETTER = {
    "rmse",
    "mae",
    "absolute_error_mean",
    "false_dry_rate",
    "false_wet_rate",
    "false_dry_volume_loss_proxy",
    "false_wet_volume_excess_proxy",
    "peak_depth_underprediction",
    "absolute_relative_volume_bias_proxy",
}


@dataclass
class BatchRecord:
    phase: str
    run_name: str
    run_dir: Path
    maps_path: Path
    summary_path: Path
    batch_name: str
    batch_index: int
    prediction: np.ndarray
    target: np.ndarray
    metadata: list[dict[str, Any]]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Phase 31 diagnostic-only masked physical error analysis. Reads existing "
            "evaluation_test/test_batch_*/forecast_maps.npz outputs and recovered static "
            "geodata masks only; does not train, alter architecture, alter losses, alter "
            "training configs, run seed123/seed202, or perform sweeps."
        )
    )
    parser.add_argument("--dataset-root", type=Path, default=DEFAULT_DATASET_ROOT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--threshold", type=float, default=WET_THRESHOLD)
    parser.add_argument("--eps", type=float, default=EPS)
    parser.add_argument("--skip-figures", action="store_true")
    return parser.parse_args()


def resolve_repo_path(path: Path) -> Path:
    path = path.expanduser()
    if path.is_absolute():
        return path
    return (REPO_ROOT / path).resolve()


def display_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT)).replace("\\", "/")
    except ValueError:
        return str(path)


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
    return f"{number:.6g}"


def yes_no(value: bool) -> str:
    return "Yes" if value else "No"


def json_ready(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): json_ready(item) for key, item in value.items()}
    if isinstance(value, list):
        return [json_ready(item) for item in value]
    if isinstance(value, tuple):
        return [json_ready(item) for item in value]
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, Path):
        return str(value)
    return value


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


def build_location_masks(dataset_root: Path) -> tuple[dict[str, dict[str, np.ndarray]], list[dict[str, Any]]]:
    geodata_root = dataset_root / "test" / "geodata"
    if not geodata_root.exists():
        raise FileNotFoundError(f"Missing test geodata directory: {geodata_root}")

    masks_by_location: dict[str, dict[str, np.ndarray]] = {}
    readiness_rows: list[dict[str, Any]] = []
    for location_dir in sorted(path for path in geodata_root.glob("location*") if path.is_dir()):
        location = location_dir.name
        dem_path = location_dir / "absolute_DEM.npy"
        impervious_path = location_dir / "impervious.npy"
        manhole_path = location_dir / "manhole.npy"

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
        interior = valid_domain & ~boundary_ring
        high_impervious_valid = valid_domain & np.isfinite(impervious) & (impervious >= HIGH_IMPERVIOUS_THRESHOLD)
        manhole_nonzero_valid = valid_domain & np.isfinite(manhole) & (manhole > 0.0)

        masks_by_location[location] = {
            "valid_domain": valid_domain,
            "interior": interior,
            "boundary_ring": boundary_ring,
            "high_impervious_valid": high_impervious_valid,
            "manhole_nonzero_valid": manhole_nonzero_valid,
            "invalid_or_high": invalid_or_high,
        }
        total_cells = int(np.prod(dem.shape))
        valid_count = int(valid_domain.sum())
        readiness_rows.append(
            {
                "location": location,
                "shape": list(dem.shape),
                "shape_is_128x128": tuple(dem.shape) == EXPECTED_SHAPE,
                "valid_domain_cells": valid_count,
                "invalid_or_high_cells": int(invalid_or_high.sum()),
                "boundary_ring_cells": int(boundary_ring.sum()),
                "interior_cells": int(interior.sum()),
                "high_impervious_valid_cells": int(high_impervious_valid.sum()),
                "manhole_nonzero_valid_cells": int(manhole_nonzero_valid.sum()),
                "valid_domain_ratio": valid_count / total_cells if total_cells else None,
                "boundary_ring_ratio_over_valid": int(boundary_ring.sum()) / valid_count if valid_count else None,
                "diagnostic_note": "invalid_or_high is diagnostic-only and not a physical target domain",
            }
        )
    return masks_by_location, readiness_rows


def list_forecast_files(run_dir: Path) -> list[Path]:
    eval_dir = run_dir / "evaluation_test"
    if not eval_dir.exists():
        return []
    return [
        batch_dir / "forecast_maps.npz"
        for batch_dir in sorted(eval_dir.glob("test_batch_*"), key=lambda item: item.name)
        if batch_dir.is_dir()
    ]


def load_summary_metadata(summary_path: Path) -> list[dict[str, Any]]:
    with summary_path.open("r", encoding="utf-8") as handle:
        summary = json.load(handle)
    metadata = summary.get("metadata")
    if not isinstance(metadata, list):
        raise ValueError(f"Missing metadata list in {display_path(summary_path)}")
    clean: list[dict[str, Any]] = []
    for index, item in enumerate(metadata):
        if not isinstance(item, dict):
            raise ValueError(f"Metadata entry {index} is not an object in {display_path(summary_path)}")
        clean.append(item)
    return clean


def load_batch(path: Path, phase: str, run_dir: Path) -> BatchRecord:
    with np.load(path, allow_pickle=False) as data:
        if "prediction" not in data or "target" not in data:
            raise KeyError(f"prediction or target missing from {display_path(path)}")
        prediction = normalize_forecast_array(data["prediction"], "prediction", path)
        target = normalize_forecast_array(data["target"], "target", path)
    if prediction.shape != target.shape:
        raise ValueError(
            f"prediction shape {prediction.shape} does not match target shape {target.shape} in {display_path(path)}"
        )

    summary_path = path.parent / "summary.json"
    metadata = load_summary_metadata(summary_path)
    if len(metadata) != prediction.shape[0]:
        raise ValueError(
            f"Metadata length {len(metadata)} does not match batch size {prediction.shape[0]} in "
            f"{display_path(summary_path)}"
        )

    batch_name = path.parent.name
    try:
        batch_index = int(batch_name.replace("test_batch_", ""))
    except ValueError:
        batch_index = -1
    return BatchRecord(
        phase=phase,
        run_name=run_dir.name,
        run_dir=run_dir,
        maps_path=path,
        summary_path=summary_path,
        batch_name=batch_name,
        batch_index=batch_index,
        prediction=prediction,
        target=target,
        metadata=metadata,
    )


def empty_accumulator(phase: str, run_name: str, run_dir: str, region: str) -> dict[str, Any]:
    return {
        "phase": phase,
        "seed": 42,
        "run_name": run_name,
        "run_dir": run_dir,
        "region": region,
        "region_is_physical_target_domain": region != "invalid_or_high",
        "diagnostic_note": "invalid_or_high is diagnostic-only and not a physical target domain"
        if region == "invalid_or_high"
        else "",
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
        "peak_depth_underprediction_sum": 0.0,
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
    acc["peak_depth_underprediction_sum"] += max(float(np.max(tgt)) - float(np.max(pred)), 0.0)


def finalize_accumulator(acc: dict[str, Any], eps: float) -> dict[str, Any]:
    pixel_count = int(acc["pixel_count"])
    target_wet = int(acc["target_wet_count"])
    target_dry = int(acc["target_dry_count"])
    target_volume = float(acc["target_volume_proxy"])
    volume_bias = float(acc["predicted_volume_proxy"]) - target_volume
    frame_count = int(acc["sample_frame_count"])

    row = dict(acc)
    row["rmse"] = math.sqrt(float(acc["sum_sq_error"]) / pixel_count) if pixel_count else None
    row["mae"] = float(acc["sum_abs_error"]) / pixel_count if pixel_count else None
    row["bias"] = float(acc["sum_error"]) / pixel_count if pixel_count else None
    row["absolute_error_mean"] = row["mae"]
    row["false_dry_rate"] = int(acc["false_dry_count"]) / target_wet if target_wet else None
    row["false_wet_rate"] = int(acc["false_wet_count"]) / target_dry if target_dry else None
    row["volume_bias_proxy"] = volume_bias
    row["relative_volume_bias_proxy"] = volume_bias / target_volume if target_volume > eps else None
    row["absolute_relative_volume_bias_proxy"] = abs(row["relative_volume_bias_proxy"]) if row["relative_volume_bias_proxy"] is not None else None
    row["peak_depth_underprediction"] = (
        float(acc["peak_depth_underprediction_sum"]) / frame_count if frame_count else None
    )
    row["locations"] = ",".join(sorted(acc["locations"]))
    row["batch_count"] = len(acc["batches"])
    del row["batches"]
    del row["peak_depth_underprediction_sum"]
    return row


def process_batches(
    masks_by_location: dict[str, dict[str, np.ndarray]],
    threshold: float,
    eps: float,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, str]], dict[str, Any]]:
    aggregates: dict[tuple[str, str], dict[str, Any]] = {}
    sample_mapping_rows: list[dict[str, Any]] = []
    missing_or_error_files: list[dict[str, str]] = []
    mapping_evidence = {
        "forecast_maps_npz_keys_checked": True,
        "forecast_maps_npz_contains_location_metadata": False,
        "adjacent_summary_json_contains_metadata": False,
        "dataset_adapter_metadata_location_field": True,
        "sample_to_location_mapping_status": "not_recovered",
        "mapping_source": "",
        "blocked_reason": "",
    }

    for phase, run_rel in RUNS.items():
        run_dir = REPO_ROOT / run_rel
        for region in REGION_ORDER:
            aggregates[(phase, region)] = empty_accumulator(phase, run_dir.name, run_rel, region)

        forecast_files = list_forecast_files(run_dir)
        if not forecast_files:
            missing_or_error_files.append(
                {"phase": phase, "path": display_path(run_dir / "evaluation_test"), "reason": "no forecast files found"}
            )
            continue

        for forecast_file in forecast_files:
            try:
                with np.load(forecast_file, allow_pickle=False) as data:
                    if any("location" in key.lower() or "metadata" in key.lower() for key in data.files):
                        mapping_evidence["forecast_maps_npz_contains_location_metadata"] = True
                batch = load_batch(forecast_file, phase, run_dir)
                mapping_evidence["adjacent_summary_json_contains_metadata"] = True
            except (OSError, KeyError, ValueError, json.JSONDecodeError, zipfile.BadZipFile) as exc:
                missing_or_error_files.append(
                    {"phase": phase, "path": display_path(forecast_file), "reason": f"read error: {exc}"}
                )
                continue

            for sample_index, metadata in enumerate(batch.metadata):
                location = str(metadata.get("location", ""))
                sample_mapping_rows.append(
                    {
                        "phase": phase,
                        "batch_name": batch.batch_name,
                        "batch_index": batch.batch_index,
                        "sample_index": sample_index,
                        "location": location,
                        "event": metadata.get("event", ""),
                        "start_idx": metadata.get("start_idx", ""),
                        "summary_path": display_path(batch.summary_path),
                        "mapping_source": "adjacent_summary_json.metadata.location",
                    }
                )
                if location not in masks_by_location:
                    missing_or_error_files.append(
                        {
                            "phase": phase,
                            "path": display_path(batch.summary_path),
                            "reason": f"metadata location {location!r} has no recovered static mask",
                        }
                    )
                    continue

                location_masks = masks_by_location[location]
                for timestep in range(batch.prediction.shape[1]):
                    pred_frame = batch.prediction[sample_index, timestep, 0]
                    target_frame = batch.target[sample_index, timestep, 0]
                    for region in REGION_ORDER:
                        acc = aggregates[(phase, region)]
                        acc["locations"].add(location)
                        acc["batches"].add(batch.batch_name)
                        update_accumulator(acc, pred_frame, target_frame, location_masks[region], threshold)

    if sample_mapping_rows and all(row.get("location") for row in sample_mapping_rows):
        mapping_evidence["sample_to_location_mapping_status"] = "recovered"
        mapping_evidence["mapping_source"] = "adjacent evaluation_test/test_batch_*/summary.json metadata.location"
    else:
        mapping_evidence["blocked_reason"] = (
            "Masked per-location diagnostics require sample-to-location mapping. "
            "No complete location metadata was recovered from forecast_maps.npz or adjacent sidecars."
        )

    by_region = [finalize_accumulator(aggregates[(phase, region)], eps) for phase in RUNS for region in REGION_ORDER]
    return by_region, sample_mapping_rows, missing_or_error_files, mapping_evidence


def make_by_phase_rows(by_region: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for phase in RUNS:
        valid = next(row for row in by_region if row["phase"] == phase and row["region"] == "valid_domain")
        row = {key: valid[key] for key in valid if key not in {"region", "diagnostic_note", "region_is_physical_target_domain"}}
        row["source_region"] = "valid_domain"
        rows.append(row)
    return rows


def make_phase29_delta_rows(by_region: list[dict[str, Any]]) -> list[dict[str, Any]]:
    lookup = {(row["phase"], row["region"]): row for row in by_region}
    rows: list[dict[str, Any]] = []
    for region in REGION_ORDER:
        base = lookup.get(("phase27", region))
        comp = lookup.get(("phase29", region))
        if not base or not comp:
            continue
        for metric in (
            "rmse",
            "mae",
            "bias",
            "absolute_error_mean",
            "false_dry_rate",
            "false_wet_rate",
            "false_dry_volume_loss_proxy",
            "false_wet_volume_excess_proxy",
            "peak_depth_underprediction",
            "predicted_volume_proxy",
            "target_volume_proxy",
            "relative_volume_bias_proxy",
            "absolute_relative_volume_bias_proxy",
        ):
            base_value = base.get(metric)
            comp_value = comp.get(metric)
            delta = None
            improved = None
            if base_value is not None and comp_value is not None:
                delta = float(comp_value) - float(base_value)
                if metric in LOWER_IS_BETTER:
                    improved = delta < 0.0
            rows.append(
                {
                    "comparison": "phase29_minus_phase27",
                    "region": region,
                    "metric": metric,
                    "phase27": base_value,
                    "phase29": comp_value,
                    "delta": delta,
                    "lower_is_better": metric in LOWER_IS_BETTER,
                    "improved": improved,
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


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(json_ready(data), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def region_extreme(by_region: list[dict[str, Any]], metric: str, phase: str = "phase29") -> dict[str, Any] | None:
    candidates = [
        row
        for row in by_region
        if row["phase"] == phase and row["region"] != "invalid_or_high" and row.get(metric) is not None
    ]
    if not candidates:
        return None
    return max(candidates, key=lambda row: float(row[metric]))


def metric_delta(delta_rows: list[dict[str, Any]], region: str, metric: str) -> dict[str, Any] | None:
    return next((row for row in delta_rows if row["region"] == region and row["metric"] == metric), None)


def summarize_findings(
    by_region: list[dict[str, Any]],
    by_phase: list[dict[str, Any]],
    delta_rows: list[dict[str, Any]],
    mapping_evidence: dict[str, Any],
    readiness_rows: list[dict[str, Any]],
    missing_or_error_files: list[dict[str, str]],
    figure_paths: list[str],
    output_dir: Path,
    dataset_root: Path,
    threshold: float,
) -> dict[str, Any]:
    lookup = {(row["phase"], row["region"]): row for row in by_region}
    phase29_rmse_region = region_extreme(by_region, "rmse", "phase29")
    phase29_mae_region = region_extreme(by_region, "mae", "phase29")
    phase29_fd_region = region_extreme(by_region, "false_dry_rate", "phase29")
    phase29_fw_region = region_extreme(by_region, "false_wet_rate", "phase29")
    boundary = lookup.get(("phase29", "boundary_ring"), {})
    interior = lookup.get(("phase29", "interior"), {})
    boundary_worse_than_interior = {
        "rmse": (
            boundary.get("rmse") is not None
            and interior.get("rmse") is not None
            and float(boundary["rmse"]) > float(interior["rmse"])
        ),
        "mae": (
            boundary.get("mae") is not None
            and interior.get("mae") is not None
            and float(boundary["mae"]) > float(interior["mae"])
        ),
        "false_dry_rate": (
            boundary.get("false_dry_rate") is not None
            and interior.get("false_dry_rate") is not None
            and float(boundary["false_dry_rate"]) > float(interior["false_dry_rate"])
        ),
        "false_wet_rate": (
            boundary.get("false_wet_rate") is not None
            and interior.get("false_wet_rate") is not None
            and float(boundary["false_wet_rate"]) > float(interior["false_wet_rate"])
        ),
    }
    phase29_vs_phase27 = {
        row["metric"]: row
        for row in delta_rows
        if row["region"] == "valid_domain" and row.get("delta") is not None
    }
    improved_count = sum(1 for row in phase29_vs_phase27.values() if row.get("improved") is True)
    worsened_count = sum(1 for row in phase29_vs_phase27.values() if row.get("improved") is False)
    mapping_recovered = mapping_evidence["sample_to_location_mapping_status"] == "recovered"
    level4_status = "supported" if mapping_recovered and by_region else "partially_blocked"

    return {
        "scope": {
            "diagnostic_only": True,
            "threshold_m": threshold,
            "dataset_root": str(dataset_root),
            "runs": RUNS,
            "output_dir": display_path(output_dir),
            "guardrail_note": (
                "Depth-raster proxy diagnostics only. No training, architecture changes, loss changes, "
                "training config changes, seed123/seed202 training, sweeps, strict mass-conservation claims, "
                "full SWE/PINN claims, or hydrodynamic-closure claims were performed."
            ),
        },
        "sample_to_location_mapping": mapping_evidence,
        "static_mask_readiness": readiness_rows,
        "missing_or_error_files": missing_or_error_files,
        "processed": {
            "phases": list(RUNS),
            "regions": list(REGION_ORDER),
            "by_region_rows": len(by_region),
            "by_phase_rows": len(by_phase),
        },
        "answers": {
            "sample_to_location_mapping_recovered": mapping_recovered,
            "masked_diagnostics_status": "fully_supported" if mapping_recovered else "partially_blocked",
            "largest_phase29_rmse_region": phase29_rmse_region,
            "largest_phase29_mae_region": phase29_mae_region,
            "highest_phase29_false_dry_region": phase29_fd_region,
            "highest_phase29_false_wet_region": phase29_fw_region,
            "boundary_ring_worse_than_interior_phase29": boundary_worse_than_interior,
            "high_impervious_phase29": lookup.get(("phase29", "high_impervious_valid")),
            "manhole_nonzero_phase29": lookup.get(("phase29", "manhole_nonzero_valid")),
            "phase29_vs_phase27_valid_domain_improved_lower_is_better_metric_count": improved_count,
            "phase29_vs_phase27_valid_domain_worsened_lower_is_better_metric_count": worsened_count,
            "level4_plus_masked_physical_diagnostics_status": level4_status,
            "level5_status": "unsupported",
            "level5_reason": (
                "The diagnostic uses prediction/target flood-depth rasters and static masks only. It does not "
                "recover velocity/flux, boundary source/sink fields, dx/dy, dt, or full hydrodynamic state."
            ),
        },
        "run_level_valid_domain": by_phase,
        "phase29_minus_phase27_deltas": delta_rows,
        "figure_paths": figure_paths,
    }


def write_markdown(path: Path, summary: dict[str, Any]) -> None:
    answers = summary["answers"]
    mapping = summary["sample_to_location_mapping"]
    by_phase = {row["phase"]: row for row in summary["run_level_valid_domain"]}
    deltas = summary["phase29_minus_phase27_deltas"]
    boundary = answers["boundary_ring_worse_than_interior_phase29"]
    high_imp = answers["high_impervious_phase29"] or {}
    manhole = answers["manhole_nonzero_phase29"] or {}

    lines = [
        "# Phase 31 Masked Physical Error Diagnostics",
        "",
        "This diagnostic applies recovered domain, boundary, impervious, and manhole masks to existing prediction/target flood-depth rasters. All values are depth-raster proxy diagnostics, not strict mass conservation, full SWE/PINN residuals, or hydrodynamic closure.",
        "",
        "## Direct Answers",
        "",
        f"1. Could sample-to-location mapping be recovered? **{yes_no(answers['sample_to_location_mapping_recovered'])}**. Source: `{mapping.get('mapping_source') or 'n/a'}`. `forecast_maps.npz` stores only arrays; adjacent `summary.json` metadata supplies `location`.",
        f"2. Are masked diagnostics fully supported or partially blocked? **{answers['masked_diagnostics_status']}**.",
        f"3. Largest Phase 29 RMSE region: `{(answers['largest_phase29_rmse_region'] or {}).get('region', 'n/a')}` with RMSE `{metric_text((answers['largest_phase29_rmse_region'] or {}).get('rmse'))}`. Largest MAE region: `{(answers['largest_phase29_mae_region'] or {}).get('region', 'n/a')}` with MAE `{metric_text((answers['largest_phase29_mae_region'] or {}).get('mae'))}`.",
        f"4. Highest Phase 29 false-dry region: `{(answers['highest_phase29_false_dry_region'] or {}).get('region', 'n/a')}` at `{metric_text((answers['highest_phase29_false_dry_region'] or {}).get('false_dry_rate'))}`. Highest false-wet region: `{(answers['highest_phase29_false_wet_region'] or {}).get('region', 'n/a')}` at `{metric_text((answers['highest_phase29_false_wet_region'] or {}).get('false_wet_rate'))}`.",
        f"5. Do boundary-ring cells behave worse than interior cells in Phase 29? RMSE `{boundary['rmse']}`, MAE `{boundary['mae']}`, false-dry `{boundary['false_dry_rate']}`, false-wet `{boundary['false_wet_rate']}`.",
        f"6. Do high-impervious or manhole-nonzero regions show distinct errors? High-impervious Phase 29 RMSE `{metric_text(high_imp.get('rmse'))}`, false-dry `{metric_text(high_imp.get('false_dry_rate'))}`; manhole-nonzero Phase 29 RMSE `{metric_text(manhole.get('rmse'))}`, false-dry `{metric_text(manhole.get('false_dry_rate'))}`.",
        f"7. Does Phase 29 improve or worsen masked physical errors relative to Phase 27? On valid-domain lower-is-better metrics, improved `{answers['phase29_vs_phase27_valid_domain_improved_lower_is_better_metric_count']}` and worsened `{answers['phase29_vs_phase27_valid_domain_worsened_lower_is_better_metric_count']}`.",
        f"8. Does this support Level 4+ masked physical diagnostics? **{answers['level4_plus_masked_physical_diagnostics_status']}**.",
        f"9. Does this change Level 5 status? **No. Level 5 remains `{answers['level5_status']}`**.",
        "",
        "## Valid-Domain Phase Summary",
        "",
        "| Phase | RMSE | MAE | Bias | False dry | False wet | Rel. volume bias proxy | Peak underprediction |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for phase in ("phase25", "phase27", "phase29"):
        row = by_phase.get(phase, {})
        lines.append(
            f"| `{phase}` | {metric_text(row.get('rmse'))} | {metric_text(row.get('mae'))} | "
            f"{metric_text(row.get('bias'))} | {metric_text(row.get('false_dry_rate'))} | "
            f"{metric_text(row.get('false_wet_rate'))} | {metric_text(row.get('relative_volume_bias_proxy'))} | "
            f"{metric_text(row.get('peak_depth_underprediction'))} |"
        )

    lines.extend(
        [
            "",
            "## Phase29 - Phase27 Valid-Domain Deltas",
            "",
            "| Metric | Phase 27 | Phase 29 | Delta | Improved |",
            "| --- | ---: | ---: | ---: | --- |",
        ]
    )
    for metric in (
        "rmse",
        "mae",
        "absolute_error_mean",
        "false_dry_rate",
        "false_wet_rate",
        "false_dry_volume_loss_proxy",
        "false_wet_volume_excess_proxy",
        "relative_volume_bias_proxy",
    ):
        row = metric_delta(deltas, "valid_domain", metric) or {}
        lines.append(
            f"| `{metric}` | {metric_text(row.get('phase27'))} | {metric_text(row.get('phase29'))} | "
            f"{metric_text(row.get('delta'))} | `{row.get('improved')}` |"
        )

    lines.extend(
        [
            "",
            "## Interpretation Guardrail",
            "",
            "`invalid_or_high` is included only as a diagnostic contrast and is not treated as a physical target domain. The supported claim is Level 4+ masked physical error diagnostics from static masks and depth rasters. Level 5 remains unsupported because the needed hydrodynamic state and flux variables are absent.",
            "",
            "## Output Files",
            "",
            "- `masked_physical_error_by_region.csv`",
            "- `masked_physical_error_by_phase.csv`",
            "- `masked_physical_error_delta_phase29_vs_phase27.csv`",
            "- `masked_physical_error_summary.json`",
            "- `masked_physical_error_findings.md`",
        ]
    )
    if summary["figure_paths"]:
        lines.extend(["", "## Optional Figures", ""])
        for figure_path in summary["figure_paths"]:
            lines.append(f"- `{figure_path}`")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_figures(output_dir: Path, by_region: list[dict[str, Any]], skip: bool) -> list[str]:
    if skip:
        return []
    try:
        import matplotlib.pyplot as plt
    except Exception:
        return []

    figure_dir = output_dir / "figures"
    figure_dir.mkdir(parents=True, exist_ok=True)
    paths: list[str] = []

    def plot_metric(metric: str, filename: str, ylabel: str) -> None:
        phases = list(RUNS)
        regions = list(REGION_ORDER)
        x = np.arange(len(regions))
        width = 0.24
        fig, ax = plt.subplots(figsize=(11, 5))
        for index, phase in enumerate(phases):
            values = []
            for region in regions:
                row = next(item for item in by_region if item["phase"] == phase and item["region"] == region)
                value = row.get(metric)
                values.append(float(value) if value is not None else np.nan)
            ax.bar(x + (index - 1) * width, values, width=width, label=phase)
        ax.set_xticks(x)
        ax.set_xticklabels(regions, rotation=25, ha="right")
        ax.set_ylabel(ylabel)
        ax.legend(fontsize=8)
        ax.grid(axis="y", alpha=0.25)
        fig.tight_layout()
        path = figure_dir / filename
        fig.savefig(path, dpi=160)
        plt.close(fig)
        paths.append(display_path(path))

    plot_metric("rmse", "masked_error_region_rmse.png", "RMSE")
    plot_metric("false_dry_rate", "masked_error_false_dry_rate.png", "False-dry rate")
    plot_metric("relative_volume_bias_proxy", "masked_error_volume_bias.png", "Relative volume bias proxy")
    return paths


def main() -> None:
    args = parse_args()
    dataset_root = args.dataset_root
    output_dir = resolve_repo_path(args.output_dir)

    masks_by_location, readiness_rows = build_location_masks(dataset_root)
    by_region, sample_mapping_rows, missing_or_error_files, mapping_evidence = process_batches(
        masks_by_location,
        threshold=args.threshold,
        eps=args.eps,
    )
    by_phase = make_by_phase_rows(by_region)
    delta_rows = make_phase29_delta_rows(by_region)
    figure_paths = write_figures(output_dir, by_region, args.skip_figures)
    summary = summarize_findings(
        by_region=by_region,
        by_phase=by_phase,
        delta_rows=delta_rows,
        mapping_evidence=mapping_evidence,
        readiness_rows=readiness_rows,
        missing_or_error_files=missing_or_error_files,
        figure_paths=figure_paths,
        output_dir=output_dir,
        dataset_root=dataset_root,
        threshold=args.threshold,
    )

    write_csv(output_dir / "masked_physical_error_by_region.csv", by_region)
    write_csv(output_dir / "masked_physical_error_by_phase.csv", by_phase)
    write_csv(output_dir / "masked_physical_error_delta_phase29_vs_phase27.csv", delta_rows)
    write_csv(output_dir / "masked_physical_error_sample_location_mapping.csv", sample_mapping_rows)
    write_json(output_dir / "masked_physical_error_summary.json", summary)
    write_markdown(output_dir / "masked_physical_error_findings.md", summary)

    print("Phase 31 masked physical error diagnostic complete.")
    print(f"  sample-to-location mapping: {mapping_evidence['sample_to_location_mapping_status']}")
    print(f"  phases processed: {', '.join(RUNS)}")
    print(f"  mask regions processed: {', '.join(REGION_ORDER)}")
    print(
        "  Level 4+ masked diagnostic status: "
        f"{summary['answers']['level4_plus_masked_physical_diagnostics_status']}"
    )
    print(f"  Level 5 status: {summary['answers']['level5_status']}")
    if missing_or_error_files:
        print(f"  missing/error files: {len(missing_or_error_files)}")
    print(f"  wrote: {display_path(output_dir / 'masked_physical_error_by_region.csv')}")
    print(f"  wrote: {display_path(output_dir / 'masked_physical_error_by_phase.csv')}")
    print(f"  wrote: {display_path(output_dir / 'masked_physical_error_delta_phase29_vs_phase27.csv')}")
    print(f"  wrote: {display_path(output_dir / 'masked_physical_error_summary.json')}")
    print(f"  wrote: {display_path(output_dir / 'masked_physical_error_findings.md')}")


if __name__ == "__main__":
    main()
