from __future__ import annotations

import argparse
import csv
import json
import math
import re
import warnings
from collections import Counter, deque
from pathlib import Path
from typing import Any, Iterable

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = Path("analysis/phase24_physical_consistency")
DEFAULT_RUN_GLOB = "runs/phase10_margin_aware_boundary_band_seed*_40e/evaluation_test"
DEFAULT_PHASE15_DIR = Path("analysis/phase15_reliability_screening")
DEFAULT_PHASE16_DIR = Path("analysis/phase16_warning_rules")
DEFAULT_PHASE23_DIR = Path("analysis/phase23_warning_case_study")

PREDICTION_KEYS = ("prediction", "predictions", "pred", "forecast", "forecast_maps")
TARGET_KEYS = ("target", "targets", "y_true", "target_maps", "label", "labels")
DEM_NAME_TOKENS = ("dem", "elev", "elevation", "topo", "topography", "terrain")
STATIC_NAME_TOKENS = ("static", "dem", "elev", "topo", "terrain")
WARNING_LEVEL_COLS = ("warning_level", "risk_category", "reliability_level", "category")
RISK_SCORE_COLS = ("risk_score", "scenario_risk_score", "score")
SCENARIO_ID_COLS = ("scenario_key", "scenario_id", "case_id", "scenario_identity")
WET_THRESHOLD = 0.05
WARNING_COLOR_MAP = {"reliable": "#2a9d8f", "caution": "#e9c46a", "high-risk": "#e76f51", "unlabeled": "#6c757d"}
WARNING_LEVEL_ORDER = ("reliable", "caution", "high-risk", "unlabeled")


def display_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def resolve_repo_path(path: Path) -> Path:
    return path if path.is_absolute() else REPO_ROOT / path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Analyze physical consistency of existing Phase 10 forecast-map artifacts. "
            "This script only reads existing outputs; it does not retrain, tune, or generate predictions."
        )
    )
    parser.add_argument("--run-glob", default=DEFAULT_RUN_GLOB)
    parser.add_argument("--phase15-dir", type=Path, default=DEFAULT_PHASE15_DIR)
    parser.add_argument("--phase16-dir", type=Path, default=DEFAULT_PHASE16_DIR)
    parser.add_argument("--phase23-dir", type=Path, default=DEFAULT_PHASE23_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--wet-threshold", type=float, default=WET_THRESHOLD)
    return parser.parse_args()


def read_json_if_exists(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, sort_keys=True)
        handle.write("\n")


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            return []
        return [dict(row) for row in reader]


def write_csv_rows(path: Path, rows: list[dict[str, Any]], fieldnames: list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if fieldnames is None:
        fieldnames = []
        for row in rows:
            for key in row:
                if key not in fieldnames:
                    fieldnames.append(key)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def first_existing_col(row: dict[str, Any], candidates: Iterable[str]) -> str | None:
    lower_lookup = {key.lower(): key for key in row}
    for candidate in candidates:
        if candidate in row:
            return candidate
        if candidate.lower() in lower_lookup:
            return lower_lookup[candidate.lower()]
    return None


def get_value(row: dict[str, Any], candidates: Iterable[str], default: str = "") -> str:
    col = first_existing_col(row, candidates)
    if col is None:
        return default
    value = row.get(col, default)
    return default if value is None else str(value)


def to_float_value(value: Any, default: float = math.nan) -> float:
    if value in ("", None):
        return default
    try:
        number = float(value)
    except (TypeError, ValueError):
        return default
    return default if math.isnan(number) or math.isinf(number) else number


def safe_ratio(numerator: float, denominator: float, default: float = 0.0) -> float:
    return numerator / denominator if denominator else default


def choose_key(files: Iterable[str], candidates: tuple[str, ...]) -> str | None:
    file_set = set(files)
    for key in candidates:
        if key in file_set:
            return key
    lower_lookup = {key.lower(): key for key in file_set}
    for key in candidates:
        if key.lower() in lower_lookup:
            return lower_lookup[key.lower()]
    return None


def normalize_map_array(array: np.ndarray) -> np.ndarray:
    values = np.asarray(array, dtype=np.float64)
    if values.ndim == 5:
        return values
    if values.ndim == 4:
        return values[:, :, None, :, :]
    if values.ndim == 3:
        return values[:, None, None, :, :]
    if values.ndim == 2:
        return values[None, None, None, :, :]
    raise ValueError(f"Unsupported map array shape {values.shape}; expected 2D, 3D, 4D, or 5D.")


def load_prediction_target(maps_path: Path) -> tuple[np.ndarray, np.ndarray, str, str]:
    with np.load(maps_path) as arrays:
        prediction_key = choose_key(arrays.files, PREDICTION_KEYS)
        target_key = choose_key(arrays.files, TARGET_KEYS)
        if prediction_key is None or target_key is None:
            raise ValueError(
                f"{display_path(maps_path)} lacks recognizable prediction/target keys. "
                f"Available keys: {arrays.files}"
            )
        prediction = normalize_map_array(arrays[prediction_key])
        target = normalize_map_array(arrays[target_key])
    if prediction.shape != target.shape:
        raise ValueError(
            f"Prediction shape {prediction.shape} does not match target shape {target.shape} "
            f"in {display_path(maps_path)}."
        )
    return prediction, target, prediction_key, target_key


def infer_seed(path: Path) -> str:
    for part in path.parts:
        match = re.search(r"seed\d+", part)
        if match:
            return match.group(0)
    return "unknown"


def infer_run_root(eval_dir: Path) -> Path:
    return eval_dir.parent if eval_dir.name == "evaluation_test" else eval_dir


def parse_batch_index(path: Path) -> int | None:
    for part in reversed(path.parts):
        match = re.fullmatch(r"test_batch_(\d+)", part)
        if match:
            return int(match.group(1))
    return None


def scenario_key(metadata: dict[str, Any], run_name: str, batch_index: int | None, sample_index: int) -> str:
    parts = [metadata.get("location", ""), metadata.get("event", ""), metadata.get("start_idx", "")]
    if any(str(part) for part in parts):
        return "|".join(str(part) for part in parts)
    return f"{run_name}|batch{batch_index}|sample{sample_index}"


def discover_map_files(run_glob: str, reference_rows: list[dict[str, str]]) -> tuple[list[Path], list[str]]:
    notes: list[str] = []
    files = set()
    for eval_dir in sorted(path for path in REPO_ROOT.glob(run_glob) if path.is_dir()):
        files.update(eval_dir.rglob("*.npz"))
    for row in reference_rows:
        value = row.get("maps_path", "") or row.get("map_path", "") or row.get("forecast_maps_path", "")
        if not value:
            continue
        path = resolve_repo_path(Path(value))
        if path.exists():
            files.add(path)
        else:
            notes.append(f"Referenced map artifact not found: {value}")
    return sorted(files), notes


def load_metadata(summary_path: Path) -> list[dict[str, Any]]:
    summary = read_json_if_exists(summary_path)
    if not summary:
        return []
    metadata = summary.get("metadata")
    if not isinstance(metadata, list):
        return []
    return [item if isinstance(item, dict) else {} for item in metadata]


def normalize_level(value: str) -> str:
    cleaned = value.strip().lower().replace("_", "-")
    aliases = {
        "high risk": "high-risk",
        "highrisk": "high-risk",
        "safe": "reliable",
        "low-risk": "reliable",
        "low risk": "reliable",
        "medium-risk": "caution",
        "moderate": "caution",
    }
    return aliases.get(cleaned, cleaned)


def row_identity(row: dict[str, Any]) -> str:
    explicit = get_value(row, SCENARIO_ID_COLS)
    if explicit:
        return explicit
    parts = [row.get("location", ""), row.get("event", ""), row.get("start_idx", "")]
    if any(str(part) for part in parts):
        return "|".join(str(part) for part in parts)
    return ""


def make_label_lookup(rows: list[dict[str, str]]) -> dict[tuple[str, ...], dict[str, str]]:
    lookup: dict[tuple[str, ...], dict[str, str]] = {}
    for row in rows:
        maps_path = str(row.get("maps_path", "")).replace("/", "\\")
        sample = str(row.get("sample_index", ""))
        seed = str(row.get("seed", ""))
        scenario = row_identity(row)
        for key in (
            ("maps_sample", maps_path, sample),
            ("seed_scenario", seed, scenario),
            ("scenario", scenario),
        ):
            if key[1] or key[2:]:
                lookup.setdefault(key, row)
    return lookup


def find_label(
    label_lookup: dict[tuple[str, ...], dict[str, str]],
    maps_path: Path,
    sample_index: int,
    seed: str,
    scenario: str,
) -> dict[str, str] | None:
    rel = display_path(maps_path).replace("/", "\\")
    keys = (
        ("maps_sample", rel, str(sample_index)),
        ("seed_scenario", seed, scenario),
        ("scenario", scenario),
    )
    for key in keys:
        if key in label_lookup:
            return label_lookup[key]
    return None


def connected_component_metrics(mask: np.ndarray) -> tuple[int, int, float]:
    mask = np.asarray(mask, dtype=bool)
    wet_area = int(mask.sum())
    if wet_area == 0:
        return 0, 0, 0.0

    visited = np.zeros(mask.shape, dtype=bool)
    component_count = 0
    largest = 0
    rows, cols = mask.shape
    for row in range(rows):
        for col in range(cols):
            if not mask[row, col] or visited[row, col]:
                continue
            component_count += 1
            area = 0
            queue: deque[tuple[int, int]] = deque([(row, col)])
            visited[row, col] = True
            while queue:
                rr, cc = queue.popleft()
                area += 1
                for nr, nc in ((rr - 1, cc), (rr + 1, cc), (rr, cc - 1), (rr, cc + 1)):
                    if 0 <= nr < rows and 0 <= nc < cols and mask[nr, nc] and not visited[nr, nc]:
                        visited[nr, nc] = True
                        queue.append((nr, nc))
            largest = max(largest, area)
    return component_count, largest, safe_ratio(largest, wet_area)


def flatten_sample(sample: np.ndarray) -> np.ndarray:
    return np.asarray(sample, dtype=np.float64).reshape(-1)


def spatial_peak_map(sample: np.ndarray) -> np.ndarray:
    values = np.asarray(sample, dtype=np.float64)
    return np.nanmax(values[:, 0, :, :], axis=0)


def scenario_metrics(
    prediction_sample: np.ndarray,
    target_sample: np.ndarray,
    wet_threshold: float,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    pred = np.clip(np.asarray(prediction_sample, dtype=np.float64), 0.0, None)
    target = np.clip(np.asarray(target_sample, dtype=np.float64), 0.0, None)
    pred_flat = flatten_sample(pred)
    target_flat = flatten_sample(target)
    error = pred_flat - target_flat
    target_wet = target > wet_threshold
    pred_wet = pred > wet_threshold

    target_volume = float(target_flat.sum())
    pred_volume = float(pred_flat.sum())
    volume_bias = pred_volume - target_volume
    target_wet_area = int(target_wet.sum())
    pred_wet_area = int(pred_wet.sum())
    wet_area_bias = pred_wet_area - target_wet_area
    target_max = float(np.nanmax(target_flat)) if target_flat.size else 0.0
    pred_max = float(np.nanmax(pred_flat)) if pred_flat.size else 0.0

    false_dry = target_wet & ~pred_wet
    false_wet = pred_wet & ~target_wet
    target_peak_wet = spatial_peak_map(target) > wet_threshold
    pred_peak_wet = spatial_peak_map(pred) > wet_threshold
    target_cc_count, target_largest, target_largest_ratio = connected_component_metrics(target_peak_wet)
    pred_cc_count, pred_largest, pred_largest_ratio = connected_component_metrics(pred_peak_wet)

    metrics = {
        "target_inundation_volume": target_volume,
        "predicted_inundation_volume": pred_volume,
        "volume_bias": volume_bias,
        "relative_volume_bias": safe_ratio(volume_bias, target_volume, math.nan),
        "target_wet_area": target_wet_area,
        "predicted_wet_area": pred_wet_area,
        "wet_area_bias": wet_area_bias,
        "wet_area_contraction": max(0.0, safe_ratio(target_wet_area - pred_wet_area, target_wet_area)),
        "target_max_depth": target_max,
        "predicted_max_depth": pred_max,
        "peak_depth_bias": pred_max - target_max,
        "peak_depth_underprediction": max(0.0, target_max - pred_max),
        "rmse": float(np.sqrt(np.nanmean(error**2))) if error.size else math.nan,
        "mae": float(np.nanmean(np.abs(error))) if error.size else math.nan,
        "mean_bias": float(np.nanmean(error)) if error.size else math.nan,
        "false_dry_rate": safe_ratio(int(false_dry.sum()), target_wet_area),
        "false_wet_rate": safe_ratio(int(false_wet.sum()), int((~target_wet).sum())),
        "target_wet_component_count": target_cc_count,
        "predicted_wet_component_count": pred_cc_count,
        "target_largest_wet_component_area": target_largest,
        "predicted_largest_wet_component_area": pred_largest,
        "target_largest_wet_component_area_ratio": target_largest_ratio,
        "predicted_largest_wet_component_area_ratio": pred_largest_ratio,
        "wet_component_count_change": pred_cc_count - target_cc_count,
        "largest_component_ratio_change": pred_largest_ratio - target_largest_ratio,
        "fragmentation_indicator": int(pred_cc_count > target_cc_count and pred_largest_ratio < target_largest_ratio),
        "connectivity_loss_indicator": int(pred_largest_ratio + 0.05 < target_largest_ratio),
    }

    temporal_rows: list[dict[str, Any]] = []
    for step_idx in range(pred.shape[0]):
        p_step = pred[step_idx]
        t_step = target[step_idx]
        t_wet = t_step > wet_threshold
        p_wet = p_step > wet_threshold
        t_volume = float(t_step.sum())
        p_volume = float(p_step.sum())
        t_area = int(t_wet.sum())
        p_area = int(p_wet.sum())
        step_error = (p_step - t_step).reshape(-1)
        temporal_rows.append(
            {
                "timestep": step_idx,
                "target_volume": t_volume,
                "predicted_volume": p_volume,
                "volume_bias": p_volume - t_volume,
                "relative_volume_bias": safe_ratio(p_volume - t_volume, t_volume, math.nan),
                "target_wet_area": t_area,
                "predicted_wet_area": p_area,
                "wet_area_bias": p_area - t_area,
                "target_peak_depth": float(np.nanmax(t_step)) if t_step.size else 0.0,
                "predicted_peak_depth": float(np.nanmax(p_step)) if p_step.size else 0.0,
                "peak_depth_bias": float(np.nanmax(p_step) - np.nanmax(t_step)) if t_step.size else 0.0,
                "rmse": float(np.sqrt(np.nanmean(step_error**2))) if step_error.size else math.nan,
                "mae": float(np.nanmean(np.abs(step_error))) if step_error.size else math.nan,
                "false_dry_rate": safe_ratio(int((t_wet & ~p_wet).sum()), t_area),
                "false_wet_rate": safe_ratio(int((p_wet & ~t_wet).sum()), int((~t_wet).sum())),
            }
        )
    metrics["temporal_volume_bias_std"] = float(np.nanstd([row["volume_bias"] for row in temporal_rows]))
    metrics["temporal_peak_underprediction_max"] = max(
        0.0,
        max((row["target_peak_depth"] - row["predicted_peak_depth"] for row in temporal_rows), default=0.0),
    )
    return metrics, temporal_rows


def discover_dem_candidates() -> list[Path]:
    roots = [REPO_ROOT / "datasets", REPO_ROOT / "assets", REPO_ROOT / "configs", REPO_ROOT / "analysis", REPO_ROOT / "runs"]
    suffixes = {".npy", ".npz", ".csv", ".txt", ".tif", ".tiff"}
    candidates: list[Path] = []
    for root in roots:
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in suffixes:
                continue
            name = path.name.lower()
            if any(token in name for token in DEM_NAME_TOKENS) or (
                any(token in str(path.parent).lower() for token in STATIC_NAME_TOKENS)
                and any(token in name for token in ("height", "z", "elev"))
            ):
                candidates.append(path)
    return sorted(candidates)


def load_dem_array(path: Path) -> np.ndarray | None:
    try:
        if path.suffix.lower() == ".npy":
            return np.asarray(np.load(path), dtype=np.float64)
        if path.suffix.lower() == ".npz":
            with np.load(path) as arrays:
                for key in arrays.files:
                    if any(token in key.lower() for token in DEM_NAME_TOKENS):
                        return np.asarray(arrays[key], dtype=np.float64)
                if arrays.files:
                    return np.asarray(arrays[arrays.files[0]], dtype=np.float64)
        if path.suffix.lower() in {".csv", ".txt"}:
            return np.loadtxt(path, delimiter="," if path.suffix.lower() == ".csv" else None)
    except Exception as exc:  # noqa: BLE001 - diagnostics should record and continue.
        warnings.warn(f"Could not load DEM candidate {display_path(path)}: {exc}", stacklevel=2)
    return None


def find_shape_compatible_dem(target_shape: tuple[int, int]) -> tuple[np.ndarray | None, Path | None, list[str]]:
    notes: list[str] = []
    for candidate in discover_dem_candidates():
        dem = load_dem_array(candidate)
        if dem is None:
            notes.append(f"candidate unreadable: {display_path(candidate)}")
            continue
        dem = np.squeeze(dem)
        if dem.ndim > 2:
            dem = np.squeeze(dem)
        if dem.ndim != 2:
            notes.append(f"candidate not 2D after squeeze: {display_path(candidate)} shape={dem.shape}")
            continue
        if dem.shape != target_shape:
            notes.append(f"candidate shape incompatible: {display_path(candidate)} shape={dem.shape}, expected={target_shape}")
            continue
        return dem, candidate, notes
    return None, None, notes


def topographic_rows(
    scenario_rows: list[dict[str, Any]],
    sample_arrays: dict[str, tuple[np.ndarray, np.ndarray]],
    wet_threshold: float,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    if not sample_arrays:
        return (
            [{"status": "skipped", "reason": "no forecast map arrays were available"}],
            {"status": "skipped", "reason": "no forecast map arrays were available"},
        )
    first_target = next(iter(sample_arrays.values()))[1]
    target_shape = spatial_peak_map(first_target).shape
    dem, dem_path, notes = find_shape_compatible_dem(target_shape)
    if dem is None:
        return (
            [
                {
                    "status": "skipped",
                    "reason": "no shape-compatible DEM/static elevation layer found",
                    "expected_shape": str(target_shape),
                    "candidate_notes": " | ".join(notes[:20]),
                }
            ],
            {
                "status": "skipped",
                "reason": "no shape-compatible DEM/static elevation layer found",
                "expected_shape": list(target_shape),
                "candidate_count": len(discover_dem_candidates()),
                "candidate_notes": notes[:20],
            },
        )

    finite = np.isfinite(dem)
    if not finite.any():
        return (
            [{"status": "skipped", "reason": "DEM exists but contains no finite cells", "dem_path": display_path(dem_path)}],
            {"status": "skipped", "reason": "DEM exists but contains no finite cells", "dem_path": display_path(dem_path)},
        )

    low_threshold = float(np.nanpercentile(dem[finite], 25))
    high_threshold = float(np.nanpercentile(dem[finite], 75))
    rows: list[dict[str, Any]] = []
    for scenario in scenario_rows:
        key = scenario["phase24_case_key"]
        pred, target = sample_arrays[key]
        pred_peak = spatial_peak_map(np.clip(pred, 0.0, None))
        target_peak = spatial_peak_map(np.clip(target, 0.0, None))
        error = pred_peak - target_peak
        target_wet = target_peak > wet_threshold
        pred_wet = pred_peak > wet_threshold
        low_mask = dem <= low_threshold
        high_mask = dem >= high_threshold
        rows.append(
            {
                "status": "computed",
                "dem_path": display_path(dem_path),
                "phase24_case_key": key,
                "scenario_key": scenario.get("scenario_key", ""),
                "seed": scenario.get("seed", ""),
                "warning_level": scenario.get("warning_level", ""),
                "risk_score": scenario.get("risk_score", ""),
                "low_elevation_threshold": low_threshold,
                "high_elevation_threshold": high_threshold,
                "low_elevation_mean_error": float(np.nanmean(error[low_mask])),
                "mid_elevation_mean_error": float(np.nanmean(error[(dem > low_threshold) & (dem < high_threshold)])),
                "high_elevation_mean_error": float(np.nanmean(error[high_mask])),
                "low_elevation_false_dry_rate": safe_ratio(int((target_wet & ~pred_wet & low_mask).sum()), int((target_wet & low_mask).sum())),
                "high_elevation_false_wet_rate": safe_ratio(int((pred_wet & ~target_wet & high_mask).sum()), int((~target_wet & high_mask).sum())),
            }
        )
    return rows, {"status": "computed", "dem_path": display_path(dem_path), "row_count": len(rows)}


def grouped_mean(rows: list[dict[str, Any]], group_field: str, value_field: str) -> dict[str, float]:
    groups: dict[str, list[float]] = {}
    for row in rows:
        group = str(row.get(group_field, "") or "unlabeled")
        value = to_float_value(row.get(value_field), math.nan)
        if math.isfinite(value):
            groups.setdefault(group, []).append(value)
    return {group: float(np.mean(values)) for group, values in groups.items() if values}


def add_warning_level_legend(ax: plt.Axes, levels: Iterable[str], *, fontsize: int = 8) -> None:
    present = {str(level or "unlabeled") for level in levels}
    ordered = [level for level in WARNING_LEVEL_ORDER if level in present]
    ordered.extend(sorted(level for level in present if level not in ordered))
    handles = [
        plt.Line2D(
            [0],
            [0],
            marker="o",
            color="none",
            markerfacecolor=WARNING_COLOR_MAP.get(level, WARNING_COLOR_MAP["unlabeled"]),
            markeredgecolor="white",
            markersize=7,
            label=level,
        )
        for level in ordered
    ]
    if handles:
        ax.legend(handles=handles, title="Warning level", fontsize=fontsize, title_fontsize=fontsize, loc="best")


def pearson(x: list[float], y: list[float]) -> float | None:
    pairs = [(a, b) for a, b in zip(x, y) if math.isfinite(a) and math.isfinite(b)]
    if len(pairs) < 3:
        return None
    xx = np.asarray([p[0] for p in pairs], dtype=np.float64)
    yy = np.asarray([p[1] for p in pairs], dtype=np.float64)
    if float(np.std(xx)) == 0.0 or float(np.std(yy)) == 0.0:
        return None
    return float(np.corrcoef(xx, yy)[0, 1])


def plot_box_by_group(rows: list[dict[str, Any]], value_field: str, group_field: str, path: Path, ylabel: str) -> bool:
    groups: dict[str, list[float]] = {}
    for row in rows:
        value = to_float_value(row.get(value_field), math.nan)
        if math.isfinite(value):
            groups.setdefault(str(row.get(group_field, "") or "unlabeled"), []).append(value)
    groups = {key: values for key, values in groups.items() if values}
    if not groups:
        return False
    order = [level for level in ("reliable", "caution", "high-risk", "unlabeled") if level in groups]
    order.extend(sorted(level for level in groups if level not in order))
    fig, ax = plt.subplots(figsize=(7.0, 4.4))
    ax.boxplot([groups[level] for level in order], labels=order, showmeans=True)
    ax.set_xlabel(group_field.replace("_", " "))
    ax.set_ylabel(ylabel)
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)
    return True


def plot_scatter(rows: list[dict[str, Any]], x_field: str, y_field: str, path: Path, xlabel: str, ylabel: str) -> bool:
    xs: list[float] = []
    ys: list[float] = []
    colors: list[str] = []
    levels: list[str] = []
    for row in rows:
        x = to_float_value(row.get(x_field), math.nan)
        y = to_float_value(row.get(y_field), math.nan)
        if math.isfinite(x) and math.isfinite(y):
            level = str(row.get("warning_level", "") or "unlabeled")
            xs.append(x)
            ys.append(y)
            levels.append(level)
            colors.append(WARNING_COLOR_MAP.get(level, WARNING_COLOR_MAP["unlabeled"]))
    if not xs:
        return False
    fig, ax = plt.subplots(figsize=(6.5, 4.6))
    ax.scatter(xs, ys, c=colors, s=28, alpha=0.85, edgecolor="white", linewidth=0.4)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.grid(alpha=0.25)
    add_warning_level_legend(ax, levels)
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)
    return True


def plot_connectivity(rows: list[dict[str, Any]], path: Path) -> bool:
    values = [
        (
            str(row.get("warning_level", "") or "unlabeled"),
            to_float_value(row.get("wet_component_count_change"), math.nan),
            to_float_value(row.get("largest_component_ratio_change"), math.nan),
        )
        for row in rows
    ]
    values = [item for item in values if math.isfinite(item[1]) and math.isfinite(item[2])]
    if not values:
        return False
    fig, ax = plt.subplots(figsize=(6.5, 4.6))
    ax.scatter(
        [item[1] for item in values],
        [item[2] for item in values],
        c=[WARNING_COLOR_MAP.get(item[0], WARNING_COLOR_MAP["unlabeled"]) for item in values],
        s=28,
        alpha=0.85,
        edgecolor="white",
        linewidth=0.4,
    )
    ax.axhline(0.0, color="black", linewidth=0.8, alpha=0.4)
    ax.axvline(0.0, color="black", linewidth=0.8, alpha=0.4)
    ax.set_xlabel("Predicted minus target wet component count")
    ax.set_ylabel("Predicted minus target largest-component ratio")
    ax.grid(alpha=0.25)
    add_warning_level_legend(ax, [item[0] for item in values])
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)
    return True


def plot_temporal_examples(rows: list[dict[str, Any]], path: Path, max_cases: int = 6) -> bool:
    by_case: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        by_case.setdefault(str(row.get("phase24_case_key", "")), []).append(row)
    if not by_case:
        return False
    selected = sorted(
        by_case.items(),
        key=lambda item: max(abs(to_float_value(row.get("relative_volume_bias"), 0.0)) for row in item[1]),
        reverse=True,
    )[:max_cases]
    fig, ax = plt.subplots(figsize=(7.2, 4.6))
    label_counts = Counter(str(case_rows[0].get("scenario_key", key)) for key, case_rows in selected)
    used_labels: set[str] = set()
    for row_idx, (key, case_rows) in enumerate(selected, start=1):
        case_rows = sorted(case_rows, key=lambda row: int(float(row.get("timestep", 0))))
        base_label = str(case_rows[0].get("scenario_key", key))
        if label_counts[base_label] > 1:
            suffix_parts = [
                str(case_rows[0].get("warning_level", "") or "unlabeled"),
                str(case_rows[0].get("seed", "") or f"row{row_idx}"),
            ]
            label = f"{base_label} ({', '.join(suffix_parts)})"
            if label in used_labels:
                label = f"{base_label} ({', '.join(suffix_parts)}, row{row_idx})"
        else:
            label = base_label
        used_labels.add(label)
        ax.plot(
            [int(float(row.get("timestep", 0))) for row in case_rows],
            [to_float_value(row.get("relative_volume_bias"), math.nan) for row in case_rows],
            marker="o",
            linewidth=1.2,
            markersize=3,
            label=label,
        )
    ax.axhline(0.0, color="black", linewidth=0.8, alpha=0.5)
    ax.set_xlabel("Forecast timestep")
    ax.set_ylabel("Relative volume bias")
    ax.grid(alpha=0.25)
    ax.legend(fontsize=7, loc="best")
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)
    return True


def plot_phase23_profiles(rows: list[dict[str, Any]], path: Path) -> bool:
    cases = [row for row in rows if row.get("phase23_case_role")]
    if not cases:
        return False
    fields = ["wet_area_contraction", "peak_depth_underprediction", "false_dry_rate", "connectivity_loss_indicator"]
    labels = ["wet area contraction", "peak underprediction", "false dry rate", "connectivity loss"]
    x = np.arange(len(fields))
    width = 0.22
    fig, ax = plt.subplots(figsize=(7.6, 4.6))
    legend_seen: set[str] = set()
    for idx, row in enumerate(cases[:4]):
        values = [to_float_value(row.get(field), 0.0) for field in fields]
        role = str(row.get("phase23_case_role", "") or row.get("warning_level", "") or "unlabeled")
        label = role if role in ("reliable", "caution", "high-risk") and role not in legend_seen else "_nolegend_"
        legend_seen.add(role)
        ax.bar(x + (idx - 1) * width, values, width=width, label=label)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=20, ha="right")
    ax.set_ylabel("Metric value")
    ax.grid(axis="y", alpha=0.25)
    handles, labels_for_handles = ax.get_legend_handles_labels()
    ordered_handles = [
        handles[labels_for_handles.index(level)]
        for level in ("reliable", "caution", "high-risk")
        if level in labels_for_handles
    ]
    if ordered_handles:
        ax.legend(handles=ordered_handles, labels=[handle.get_label() for handle in ordered_handles])
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)
    return True


def plot_topographic(rows: list[dict[str, Any]], path: Path) -> bool:
    computed = [row for row in rows if row.get("status") == "computed"]
    if not computed:
        return False
    fields = ["low_elevation_mean_error", "mid_elevation_mean_error", "high_elevation_mean_error"]
    means = [np.nanmean([to_float_value(row.get(field), math.nan) for row in computed]) for field in fields]
    fig, ax = plt.subplots(figsize=(6.4, 4.2))
    ax.bar(["low", "mid", "high"], means, color=["#457b9d", "#a8dadc", "#f4a261"])
    ax.axhline(0.0, color="black", linewidth=0.8)
    ax.set_xlabel("DEM elevation stratum")
    ax.set_ylabel("Mean peak-depth error")
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)
    return True


def risk_linkage_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    fields = [
        "relative_volume_bias",
        "wet_area_contraction",
        "peak_depth_underprediction",
        "false_dry_rate",
        "false_wet_rate",
        "wet_component_count_change",
        "largest_component_ratio_change",
        "connectivity_loss_indicator",
        "rmse",
        "mae",
    ]
    out: list[dict[str, Any]] = []
    risk_scores = [to_float_value(row.get("risk_score"), math.nan) for row in rows]
    for field in fields:
        values = [to_float_value(row.get(field), math.nan) for row in rows]
        corr = pearson(risk_scores, values)
        out.append(
            {
                "metric": field,
                "pearson_correlation_with_risk_score": "" if corr is None else corr,
                "mean_reliable": grouped_mean(rows, "warning_level", field).get("reliable", ""),
                "mean_caution": grouped_mean(rows, "warning_level", field).get("caution", ""),
                "mean_high_risk": grouped_mean(rows, "warning_level", field).get("high-risk", ""),
                "row_count": sum(1 for value in values if math.isfinite(value)),
            }
        )
    return out


def interpretation(
    rows: list[dict[str, Any]],
    linkage: list[dict[str, Any]],
    topographic_summary: dict[str, Any],
    skipped: list[dict[str, Any]],
) -> dict[str, Any]:
    warning_counts = Counter(str(row.get("warning_level", "") or "unlabeled") for row in rows)
    mean_by_warning = {
        field: grouped_mean(rows, "warning_level", field)
        for field in (
            "relative_volume_bias",
            "wet_area_contraction",
            "peak_depth_underprediction",
            "false_dry_rate",
            "connectivity_loss_indicator",
            "largest_component_ratio_change",
        )
    }
    linkage_lookup = {row["metric"]: row for row in linkage}
    high_risk_stronger = False
    for field in ("wet_area_contraction", "peak_depth_underprediction", "false_dry_rate"):
        means = mean_by_warning.get(field, {})
        if means.get("high-risk", -math.inf) > means.get("reliable", math.inf):
            high_risk_stronger = True

    promising = []
    for field in ("false_dry_rate", "wet_area_contraction", "peak_depth_underprediction", "connectivity_loss_indicator"):
        corr = to_float_value(linkage_lookup.get(field, {}).get("pearson_correlation_with_risk_score"), math.nan)
        means = mean_by_warning.get(field, {})
        if math.isfinite(corr) and abs(corr) >= 0.3:
            promising.append(field)
        elif means.get("high-risk", -math.inf) > means.get("reliable", math.inf):
            promising.append(field)

    return {
        "warning_level_counts": dict(warning_counts),
        "grouped_metric_means": mean_by_warning,
        "high_risk_cases_show_stronger_physical_inconsistency": high_risk_stronger,
        "high_risk_interpretation": (
            "High-risk cases show stronger physical inconsistency in at least one core diagnostic "
            "(false-dry, wet-area contraction, or peak underprediction)."
            if high_risk_stronger
            else "The available grouped metrics do not show a uniform high-risk increase across core diagnostics."
        ),
        "phase13_phase23_failure_mode_alignment": (
            "Peak-depth underprediction, wet-area contraction, and false-dry behavior are reported explicitly. "
            "When these metrics rise in caution or high-risk cases, they support the Phase 13/23 interpretation "
            "that model risk is concentrated in missed extent and attenuated local maxima."
        ),
        "connectivity_explanation": (
            "Connectivity-loss indicators compare peak wet-area component structure. Positive component-count "
            "changes with lower largest-component ratios indicate fragmented predicted inundation, which can "
            "explain false-dry gaps inside otherwise connected target flood extents."
        ),
        "topographic_diagnostics": topographic_summary,
        "skipped_diagnostics": skipped,
        "promising_phase25_constraints": sorted(set(promising))
        or ["false_dry_rate", "wet_area_contraction", "peak_depth_underprediction"],
    }


def main() -> None:
    args = parse_args()
    output_dir = resolve_repo_path(args.output_dir)
    figures_dir = output_dir / "figures"
    figures_dir.mkdir(parents=True, exist_ok=True)

    phase15_dir = resolve_repo_path(args.phase15_dir)
    phase16_dir = resolve_repo_path(args.phase16_dir)
    phase23_dir = resolve_repo_path(args.phase23_dir)
    phase15_rows = read_csv_rows(phase15_dir / "scenario_risk_scores.csv")
    phase16_rows = read_csv_rows(phase16_dir / "scenario_warning_summary.csv")
    phase23_rows = read_csv_rows(phase23_dir / "selected_cases.csv")
    label_lookup = make_label_lookup(phase16_rows or phase15_rows)
    phase23_lookup = make_label_lookup(phase23_rows)
    reference_rows = phase15_rows + phase16_rows + phase23_rows

    map_files, discovery_notes = discover_map_files(args.run_glob, reference_rows)
    skipped: list[dict[str, Any]] = []
    if discovery_notes:
        skipped.append({"diagnostic": "map_artifact_discovery", "reason": "some referenced artifacts missing", "notes": discovery_notes[:20]})

    scenario_rows: list[dict[str, Any]] = []
    volume_rows: list[dict[str, Any]] = []
    peak_rows: list[dict[str, Any]] = []
    wet_rows: list[dict[str, Any]] = []
    temporal_rows: list[dict[str, Any]] = []
    sample_arrays: dict[str, tuple[np.ndarray, np.ndarray]] = {}

    for maps_path in map_files:
        try:
            prediction, target, prediction_key, target_key = load_prediction_target(maps_path)
        except Exception as exc:  # noqa: BLE001 - keep diagnostics robust to malformed artifacts.
            skipped.append({"diagnostic": "forecast_map_loading", "path": display_path(maps_path), "reason": str(exc)})
            continue

        eval_dir = next((parent for parent in maps_path.parents if parent.name == "evaluation_test"), maps_path.parent)
        run_root = infer_run_root(eval_dir)
        seed = infer_seed(run_root)
        batch_index = parse_batch_index(maps_path)
        metadata = load_metadata(maps_path.parent / "summary.json")
        rel_maps_path = display_path(maps_path)

        for sample_index in range(prediction.shape[0]):
            meta = metadata[sample_index] if sample_index < len(metadata) else {}
            scen_key = scenario_key(meta, run_root.name, batch_index, sample_index)
            label = find_label(label_lookup, maps_path, sample_index, seed, scen_key) or {}
            phase23 = find_label(phase23_lookup, maps_path, sample_index, seed, scen_key) or {}
            warning_level = normalize_level(get_value(label, WARNING_LEVEL_COLS, "")) or normalize_level(
                str(phase23.get("warning_level", ""))
            )
            risk_score = get_value(label, RISK_SCORE_COLS, "")
            case_key = f"{seed}|batch{batch_index}|sample{sample_index}|{scen_key}"

            metrics, timestep_rows = scenario_metrics(prediction[sample_index], target[sample_index], args.wet_threshold)
            base = {
                "phase24_case_key": case_key,
                "seed": seed,
                "run_name": run_root.name,
                "run_root": display_path(run_root),
                "maps_path": rel_maps_path,
                "summary_path": display_path(maps_path.parent / "summary.json"),
                "batch_index": batch_index if batch_index is not None else "",
                "sample_index": sample_index,
                "split": meta.get("split", ""),
                "location": meta.get("location", ""),
                "event": meta.get("event", ""),
                "start_idx": meta.get("start_idx", ""),
                "input_steps": meta.get("input_steps", ""),
                "pred_steps": meta.get("pred_steps", ""),
                "alignment_mode": meta.get("alignment_mode", ""),
                "scenario_key": scen_key,
                "warning_level": warning_level,
                "risk_score": risk_score,
                "risk_category": label.get("risk_category", ""),
                "phase23_case_role": phase23.get("case_role", ""),
                "phase23_selection_basis": phase23.get("selection_basis", ""),
                "prediction_key": prediction_key,
                "target_key": target_key,
                "wet_threshold": args.wet_threshold,
            }
            row = {**base, **metrics}
            scenario_rows.append(row)
            sample_arrays[case_key] = (prediction[sample_index], target[sample_index])

            volume_rows.append(
                {
                    **base,
                    "target_inundation_volume": metrics["target_inundation_volume"],
                    "predicted_inundation_volume": metrics["predicted_inundation_volume"],
                    "volume_bias": metrics["volume_bias"],
                    "relative_volume_bias": metrics["relative_volume_bias"],
                    "target_wet_area": metrics["target_wet_area"],
                    "predicted_wet_area": metrics["predicted_wet_area"],
                    "wet_area_bias": metrics["wet_area_bias"],
                    "wet_area_contraction": metrics["wet_area_contraction"],
                }
            )
            peak_rows.append(
                {
                    **base,
                    "target_max_depth": metrics["target_max_depth"],
                    "predicted_max_depth": metrics["predicted_max_depth"],
                    "peak_depth_bias": metrics["peak_depth_bias"],
                    "peak_depth_underprediction": metrics["peak_depth_underprediction"],
                    "rmse": metrics["rmse"],
                    "mae": metrics["mae"],
                    "false_dry_rate": metrics["false_dry_rate"],
                    "false_wet_rate": metrics["false_wet_rate"],
                }
            )
            wet_rows.append(
                {
                    **base,
                    "target_wet_area": metrics["target_wet_area"],
                    "predicted_wet_area": metrics["predicted_wet_area"],
                    "target_wet_component_count": metrics["target_wet_component_count"],
                    "predicted_wet_component_count": metrics["predicted_wet_component_count"],
                    "target_largest_wet_component_area_ratio": metrics["target_largest_wet_component_area_ratio"],
                    "predicted_largest_wet_component_area_ratio": metrics["predicted_largest_wet_component_area_ratio"],
                    "wet_component_count_change": metrics["wet_component_count_change"],
                    "largest_component_ratio_change": metrics["largest_component_ratio_change"],
                    "fragmentation_indicator": metrics["fragmentation_indicator"],
                    "connectivity_loss_indicator": metrics["connectivity_loss_indicator"],
                    "false_dry_rate": metrics["false_dry_rate"],
                }
            )
            for timestep_row in timestep_rows:
                temporal_rows.append({**base, **timestep_row})

    if not scenario_rows:
        skipped.append({"diagnostic": "all_map_based_diagnostics", "reason": "no loadable forecast maps found"})

    topographic, topographic_summary = topographic_rows(scenario_rows, sample_arrays, args.wet_threshold)
    if topographic_summary.get("status") == "skipped":
        skipped.append({"diagnostic": "topographic_consistency", "reason": topographic_summary.get("reason", "")})

    linkage = risk_linkage_rows(scenario_rows)
    figures_generated: list[str] = []
    figure_specs = [
        ("volume_bias_by_warning_level.png", plot_box_by_group, (scenario_rows, "relative_volume_bias", "warning_level", "Relative volume bias")),
        (
            "peak_underprediction_by_warning_level.png",
            plot_box_by_group,
            (scenario_rows, "peak_depth_underprediction", "warning_level", "Peak-depth underprediction"),
        ),
        (
            "physics_consistency_vs_risk_score.png",
            plot_scatter,
            (scenario_rows, "risk_score", "false_dry_rate", "Risk score", "False-dry rate"),
        ),
    ]
    for filename, func, params in figure_specs:
        path = figures_dir / filename
        if func(*params[:3], path, *params[3:]):  # type: ignore[arg-type]
            figures_generated.append(display_path(path))
    if plot_connectivity(scenario_rows, figures_dir / "wet_connectivity_fragmentation.png"):
        figures_generated.append(display_path(figures_dir / "wet_connectivity_fragmentation.png"))
    if plot_temporal_examples(temporal_rows, figures_dir / "temporal_volume_bias_examples.png"):
        figures_generated.append(display_path(figures_dir / "temporal_volume_bias_examples.png"))
    if plot_phase23_profiles(scenario_rows, figures_dir / "phase23_case_physical_failure_profiles.png"):
        figures_generated.append(display_path(figures_dir / "phase23_case_physical_failure_profiles.png"))
    if plot_topographic(topographic, figures_dir / "topographic_error_pattern.png"):
        figures_generated.append(display_path(figures_dir / "topographic_error_pattern.png"))

    write_csv_rows(output_dir / "scenario_physical_consistency_metrics.csv", scenario_rows)
    write_csv_rows(output_dir / "volume_response_metrics.csv", volume_rows)
    write_csv_rows(output_dir / "peak_depth_consistency.csv", peak_rows)
    write_csv_rows(output_dir / "topographic_consistency.csv", topographic)
    write_csv_rows(output_dir / "wet_connectivity_metrics.csv", wet_rows)
    write_csv_rows(output_dir / "temporal_consistency_metrics.csv", temporal_rows)
    write_csv_rows(output_dir / "physics_risk_linkage.csv", linkage)

    row_counts = {
        "scenario_physical_consistency_metrics.csv": len(scenario_rows),
        "volume_response_metrics.csv": len(volume_rows),
        "peak_depth_consistency.csv": len(peak_rows),
        "topographic_consistency.csv": len(topographic),
        "wet_connectivity_metrics.csv": len(wet_rows),
        "temporal_consistency_metrics.csv": len(temporal_rows),
        "physics_risk_linkage.csv": len(linkage),
    }
    summary = {
        "phase": "Phase 24 physical consistency deepening",
        "repo_root": str(REPO_ROOT),
        "output_dir": display_path(output_dir),
        "run_glob": args.run_glob,
        "wet_threshold": args.wet_threshold,
        "phase10_recommended_setting": {"boundary_band_pixels": 1, "boundary_weight": 2.0},
        "explicit_non_actions": [
            "no model retraining",
            "no architecture modification",
            "no new prediction generation",
            "no Phase 10 boundary_weight tuning",
            "no boundary_band_pixels tuning",
            "no new loss-function deployment",
            "no new parameter sweep",
            "no metric-chasing experiment",
            "no traffic-impact modeling",
        ],
        "input_sources": {
            "phase15_scenario_rows": len(phase15_rows),
            "phase16_scenario_warning_rows": len(phase16_rows),
            "phase23_selected_cases": len(phase23_rows),
            "map_artifacts_discovered": len(map_files),
            "map_artifacts_loaded": len(set(row["maps_path"] for row in scenario_rows)),
        },
        "row_counts": row_counts,
        "figures_generated": figures_generated,
        "skipped_diagnostics": skipped,
        "topographic_summary": topographic_summary,
        "interpretation": interpretation(scenario_rows, linkage, topographic_summary, skipped),
    }
    write_json(output_dir / "summary.json", summary)

    print(json.dumps({"output_dir": display_path(output_dir), "row_counts": row_counts, "figures": figures_generated}, indent=2))


if __name__ == "__main__":
    main()
