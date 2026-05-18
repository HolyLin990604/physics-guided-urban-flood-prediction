from __future__ import annotations

import argparse
import json
import math
import re
from collections import Counter
from pathlib import Path
from typing import Any, Iterable

import numpy as np


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = Path("analysis/phase26_strong_physics_constraint_feasibility")

LIKELY_SCAN_DIRS = (
    "data",
    "dataset",
    "datasets",
    "outputs",
    "runs",
    "experiments",
    "analysis",
    "configs",
    "docs",
)
SKIP_DIR_NAMES = {
    ".git",
    ".idea",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    "__pycache__",
    "node_modules",
    "venv",
    ".venv",
}
TEXT_EXTENSIONS = {".json", ".yaml", ".yml", ".csv", ".md", ".txt", ".toml", ".ini", ".cfg"}
MAX_TEXT_BYTES = 2_000_000
PHASE25_COMPARISON_DIR = Path("analysis/phase25_target_wet_recall_comparison")
PHASE25_SEEDS = ("seed123", "seed42", "seed202")

CATEGORY_TOKENS: dict[str, tuple[str, ...]] = {
    "flood_depth": ("flood", "depth", "water_depth", "inundation", "target", "label", "y_true"),
    "rainfall": ("rain", "rainfall", "precip", "precipitation", "storm"),
    "dem_elevation": ("dem", "elev", "elevation", "topo", "topography", "terrain", "dtm", "dsm"),
    "impervious": ("impervious", "imperv", "landcover", "land_cover"),
    "manhole_drainage": ("manhole", "drain", "drainage", "sewer", "inlet", "outlet", "pipe"),
    "mask": ("mask", "valid", "nodata", "wetdry", "wet_dry"),
    "boundary": ("boundary", "bound", "edge", "border"),
}
STATIC_CATEGORIES = {"dem_elevation", "impervious", "manhole_drainage", "mask", "boundary"}

PREDICTION_TOKENS = ("prediction", "predictions", "pred", "forecast", "output", "y_pred")
TARGET_TOKENS = ("target", "targets", "truth", "ground_truth", "label", "labels", "y_true")
INPUT_TOKENS = ("input", "inputs", "x", "feature", "features")
RAINFALL_TOKENS = ("rain", "rainfall", "precip", "precipitation", "storm")
MAP_TOKENS = ("map", "maps", "flood", "depth", "prediction", "target", "forecast")

METADATA_PATTERNS: dict[str, tuple[str, ...]] = {
    "dt_or_time_interval": (
        r"\bdt\b",
        r"time[_ -]?(interval|step|resolution|delta)",
        r"temporal[_ -]?(resolution|interval)",
        r"input_steps",
        r"pred_steps",
        r"stride",
        r"rainfall.*alignment",
    ),
    "dx_dy_or_spatial_resolution": (
        r"\bdx\b",
        r"\bdy\b",
        r"spatial[_ -]?(resolution|step)",
        r"cell[_ -]?size",
        r"grid[_ -]?(resolution|spacing)",
    ),
    "grid_size": (r"grid[_ -]?size", r"grid[_ -]?shape", r"\bheight\b", r"\bwidth\b", r"\bH\b", r"\bW\b"),
    "scenario_metadata": (r"scenario", r"event", r"location", r"case_id", r"scenario_key"),
    "rainfall_scenario_names": (r"rainfall.*(scenario|event|name)", r"storm", r"return[_ -]?period", r"r\d+y"),
    "train_test_split": (r"\btrain\b", r"\btest\b", r"\bsplit\b", r"validation", r"val"),
    "boundary_conditions": (r"boundary[_ -]?condition", r"\bbc\b", r"inflow", r"outflow", r"open boundary"),
    "pump_gate_operations": (r"\bpump(s|ing)?\b", r"\bgate(s)?\b", r"\bsluice\b", r"pump[_ -]?operation", r"gate[_ -]?operation"),
    "source_sink_infiltration_drainage": (
        r"source",
        r"sink",
        r"infiltration",
        r"drainage",
        r"drain",
        r"sewer",
        r"manhole",
    ),
    "velocity_or_flux_fields": (r"\bvelocity\b", r"\bu_velocity\b", r"\bv_velocity\b", r"\bflux\b", r"\bdischarge\b", r"flow[_ -]?rate"),
}


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
            "Audit physics-relevant repository inputs for Phase 26. This is read-only except "
            "for writing Phase 26 audit outputs."
        )
    )
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--max-npy-files", type=int, default=1500)
    parser.add_argument("--max-npy-bytes-for-stats", type=int, default=512 * 1024 * 1024)
    parser.add_argument("--max-npz-files", type=int, default=3000)
    parser.add_argument("--max-npz-bytes-for-stats", type=int, default=512 * 1024 * 1024)
    parser.add_argument("--max-text-files", type=int, default=2500)
    return parser.parse_args()


def safe_iter_files(roots: Iterable[Path], suffixes: set[str] | None = None, max_files: int | None = None) -> list[Path]:
    files: list[Path] = []
    seen: set[Path] = set()
    stack = [root for root in roots if root.exists()]
    while stack:
        root = stack.pop()
        try:
            children = sorted(root.iterdir(), key=lambda item: str(item).lower())
        except OSError:
            continue
        for child in children:
            if child.name in SKIP_DIR_NAMES:
                continue
            if child.is_dir():
                stack.append(child)
                continue
            if not child.is_file():
                continue
            if suffixes is not None and child.suffix.lower() not in suffixes:
                continue
            try:
                resolved = child.resolve()
            except OSError:
                resolved = child
            if resolved in seen:
                continue
            seen.add(resolved)
            files.append(child)
            if max_files is not None and len(files) >= max_files:
                return sorted(files, key=display_path)
    return sorted(files, key=display_path)


def scan_roots() -> list[Path]:
    roots = [REPO_ROOT / name for name in LIKELY_SCAN_DIRS if (REPO_ROOT / name).exists()]
    roots.append(REPO_ROOT)
    unique: list[Path] = []
    seen: set[Path] = set()
    for root in roots:
        try:
            resolved = root.resolve()
        except OSError:
            resolved = root
        if resolved not in seen:
            seen.add(resolved)
            unique.append(root)
    return unique


def infer_array_category(path: Path) -> str:
    text = display_path(path).lower()
    matches: list[str] = []
    for category, tokens in CATEGORY_TOKENS.items():
        if any(token in text for token in tokens):
            matches.append(category)
    if "boundary" in matches:
        return "boundary"
    if "mask" in matches:
        return "mask"
    if "dem_elevation" in matches:
        return "dem_elevation"
    if "impervious" in matches:
        return "impervious"
    if "manhole_drainage" in matches:
        return "manhole_drainage"
    if "rainfall" in matches:
        return "rainfall"
    if "flood_depth" in matches:
        return "flood_depth"
    return "unknown"


def safe_float(value: Any) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError, OverflowError):
        return None
    if math.isnan(number) or math.isinf(number):
        return None
    return number


def inspect_npy(path: Path, max_stats_bytes: int) -> dict[str, Any]:
    record: dict[str, Any] = {
        "relative_path": display_path(path),
        "category": infer_array_category(path),
        "shape": None,
        "dtype": None,
        "min": None,
        "max": None,
        "mean": None,
        "stats_status": "not_loaded",
        "error": None,
    }
    try:
        arr = np.load(path, mmap_mode="r", allow_pickle=False)
        record["shape"] = [int(dim) for dim in arr.shape]
        record["dtype"] = str(arr.dtype)
        if arr.dtype.fields is not None:
            record["stats_status"] = "skipped_structured_dtype"
        elif np.issubdtype(arr.dtype, np.number) or np.issubdtype(arr.dtype, np.bool_):
            if arr.nbytes <= max_stats_bytes:
                values = np.asarray(arr)
                if values.size:
                    record["min"] = safe_float(np.nanmin(values))
                    record["max"] = safe_float(np.nanmax(values))
                    record["mean"] = safe_float(np.nanmean(values))
                    record["stats_status"] = "computed"
                else:
                    record["stats_status"] = "empty_array"
            else:
                record["stats_status"] = f"skipped_large_array_{arr.nbytes}_bytes"
        else:
            record["stats_status"] = "skipped_non_numeric"
    except Exception as exc:  # noqa: BLE001 - audit should continue on bad files.
        record["error"] = f"{type(exc).__name__}: {exc}"
        record["stats_status"] = "error"
    return record


def classify_npz_key(key: str) -> str:
    lower = key.lower()
    if any(token == lower or token in lower for token in PREDICTION_TOKENS):
        return "prediction"
    if any(token == lower or token in lower for token in TARGET_TOKENS):
        return "target"
    if any(token == lower or token in lower for token in RAINFALL_TOKENS):
        return "rainfall"
    if any(token == lower or token in lower for token in INPUT_TOKENS):
        return "input"
    return "unknown"


def inspect_npz_array(key: str, arr: np.ndarray, max_stats_bytes: int) -> dict[str, Any]:
    record: dict[str, Any] = {
        "key": key,
        "role": classify_npz_key(key),
        "shape": [int(dim) for dim in arr.shape],
        "dtype": str(arr.dtype),
        "min": None,
        "max": None,
        "mean": None,
        "stats_status": "not_loaded",
    }
    if arr.dtype.fields is not None:
        record["stats_status"] = "skipped_structured_dtype"
    elif np.issubdtype(arr.dtype, np.number) or np.issubdtype(arr.dtype, np.bool_):
        if arr.nbytes <= max_stats_bytes:
            values = np.asarray(arr)
            if values.size:
                record["min"] = safe_float(np.nanmin(values))
                record["max"] = safe_float(np.nanmax(values))
                record["mean"] = safe_float(np.nanmean(values))
                record["stats_status"] = "computed"
            else:
                record["stats_status"] = "empty_array"
        else:
            record["stats_status"] = f"skipped_large_array_{arr.nbytes}_bytes"
    else:
        record["stats_status"] = "skipped_non_numeric"
    return record


def run_name_from_path(path: Path) -> str | None:
    parts = display_path(path).replace("\\", "/").split("/")
    try:
        runs_index = parts.index("runs")
    except ValueError:
        return None
    if runs_index + 1 >= len(parts):
        return None
    return parts[runs_index + 1]


def infer_phase(path: Path) -> str:
    lower = display_path(path).lower()
    if "phase10" in lower:
        return "phase10"
    if "phase25" in lower:
        return "phase25"
    return "other"


def infer_seed(path: Path) -> str | None:
    match = re.search(r"seed\d+", display_path(path).lower())
    return match.group(0) if match else None


def infer_split(path: Path) -> str:
    lower = display_path(path).replace("\\", "/").lower()
    if "/evaluation_test/" in lower:
        return "evaluation_test"
    if "/visualizations/" in lower:
        return "visualizations"
    return "other"


def phase10_baseline_role(path: Path) -> str | None:
    if infer_phase(path) != "phase10":
        return None
    run_name = run_name_from_path(path) or ""
    lower = run_name.lower()
    if "_w15_" in lower or "boundary_weight_1.5" in lower:
        return "rollback_or_non_default_boundary_weight_1.5"
    if "_w20_" in lower or "boundary_weight_2.0" in lower or "phase10_margin_aware_boundary_band_seed" in lower:
        return "recommended_baseline_boundary_weight_2.0_w20"
    return "phase10_candidate_unclassified_boundary_weight"


def map_candidate_priority(path: Path) -> tuple[int, str, str, str]:
    split_priority = {"evaluation_test": 0, "visualizations": 1}.get(infer_split(path), 2)
    role = phase10_baseline_role(path) or ""
    role_priority = 0 if role == "recommended_baseline_boundary_weight_2.0_w20" else 1
    return (split_priority, role_priority, display_path(path).lower(), role)


def inspect_npz(path: Path, max_stats_bytes: int) -> dict[str, Any]:
    record: dict[str, Any] = {
        "relative_path": display_path(path),
        "phase": infer_phase(path),
        "seed": infer_seed(path),
        "split": infer_split(path),
        "run_name": run_name_from_path(path),
        "phase10_baseline_role": phase10_baseline_role(path),
        "keys": [],
        "arrays": [],
        "prediction_keys": [],
        "target_keys": [],
        "input_keys": [],
        "rainfall_keys": [],
        "unknown_keys": [],
        "prediction_target_shape_compatible": None,
        "error": None,
    }
    try:
        with np.load(path, allow_pickle=False) as arrays:
            keys = list(arrays.files)
            record["keys"] = keys
            for key in keys:
                array_record = inspect_npz_array(key, arrays[key], max_stats_bytes)
                record["arrays"].append(array_record)
                record[f"{array_record['role']}_keys"].append(key)
    except Exception as exc:  # noqa: BLE001 - audit should continue on bad files.
        record["error"] = f"{type(exc).__name__}: {exc}"
        return record

    prediction_shapes = {
        tuple(item["shape"]) for item in record["arrays"] if item["role"] == "prediction" and item["shape"]
    }
    target_shapes = {tuple(item["shape"]) for item in record["arrays"] if item["role"] == "target" and item["shape"]}
    if prediction_shapes and target_shapes:
        record["prediction_target_shape_compatible"] = bool(prediction_shapes & target_shapes)
    return record


def discover_map_npz_files(max_files: int) -> tuple[int, list[Path]]:
    runs_root = REPO_ROOT / "runs"
    if not runs_root.exists():
        return 0, []
    files = safe_iter_files([runs_root], suffixes={".npz"}, max_files=None)
    wanted = [
        path
        for path in files
        if path.name == "forecast_maps.npz"
        and infer_split(path) in {"evaluation_test", "visualizations"}
    ]
    sorted_wanted = sorted(wanted, key=map_candidate_priority)
    return len(sorted_wanted), sorted_wanted[:max_files]


def select_representative_npz_files(files: list[Path]) -> list[Path]:
    selected: list[Path] = []
    seen: set[tuple[str, str | None, str, str | None]] = set()
    for path in sorted(files, key=map_candidate_priority):
        key = (infer_phase(path), infer_seed(path), infer_split(path), phase10_baseline_role(path))
        if key in seen:
            continue
        seen.add(key)
        selected.append(path)
    return selected


def representative_npz_spatial_shape(npz_records: list[dict[str, Any]]) -> list[int] | None:
    spatial_counter: Counter[tuple[int, int]] = Counter()
    for record in npz_records:
        if record.get("split") != "evaluation_test":
            continue
        for item in record.get("arrays", []):
            if item.get("role") in {"prediction", "target"}:
                dims = spatial_dims(item.get("shape"))
                if dims:
                    spatial_counter[tuple(dims)] += 1
    if not spatial_counter:
        for record in npz_records:
            for item in record.get("arrays", []):
                if item.get("role") in {"prediction", "target"}:
                    dims = spatial_dims(item.get("shape"))
                    if dims:
                        spatial_counter[tuple(dims)] += 1
    return list(spatial_counter.most_common(1)[0][0]) if spatial_counter else None


def summarize_npz_maps(npz_records: list[dict[str, Any]], total_file_count: int) -> dict[str, Any]:
    by_phase: dict[str, dict[str, Any]] = {}
    for phase in ("phase10", "phase25", "other"):
        phase_items = [item for item in npz_records if item["phase"] == phase]
        by_phase[phase] = {
            "representative_files": phase_items,
            "representative_file_count": len(phase_items),
            "evaluation_test_prediction_target_available": any(
                item["split"] == "evaluation_test" and item["prediction_keys"] and item["target_keys"]
                for item in phase_items
            ),
            "prediction_target_shape_compatible": all(
                item["prediction_target_shape_compatible"] is not False
                for item in phase_items
                if item["prediction_keys"] and item["target_keys"]
            )
            if any(item["prediction_keys"] and item["target_keys"] for item in phase_items)
            else None,
        }
    return {
        "total_forecast_map_npz_count": total_file_count,
        "representative_forecast_maps": npz_records,
        "representative_flood_spatial_shape_from_npz": representative_npz_spatial_shape(npz_records),
        "by_phase": by_phase,
    }


def spatial_dims(shape: list[int] | None) -> list[int] | None:
    if not shape or len(shape) < 2:
        return None
    return [int(shape[-2]), int(shape[-1])]


def summarize_shapes(array_records: list[dict[str, Any]], npz_map_summary: dict[str, Any] | None = None) -> dict[str, Any]:
    flood_shapes = Counter(tuple(item["shape"]) for item in array_records if item["category"] == "flood_depth" and item["shape"])
    static_shapes = Counter(tuple(item["shape"]) for item in array_records if item["category"] in STATIC_CATEGORIES and item["shape"])
    dem_records = [item for item in array_records if item["category"] == "dem_elevation" and item["shape"]]
    flood_spatial = Counter(tuple(spatial_dims(item["shape"]) or []) for item in array_records if item["category"] == "flood_depth")
    flood_spatial.pop((), None)
    npz_representative_flood_spatial = (
        npz_map_summary.get("representative_flood_spatial_shape_from_npz") if npz_map_summary else None
    )
    representative_flood_spatial = (
        npz_representative_flood_spatial if npz_representative_flood_spatial else list(flood_spatial.most_common(1)[0][0]) if flood_spatial else None
    )

    compatible_dem = []
    if representative_flood_spatial is not None:
        for item in dem_records:
            if spatial_dims(item["shape"]) == representative_flood_spatial:
                compatible_dem.append(item["relative_path"])

    return {
        "representative_flood_depth_shapes": [
            {"shape": list(shape), "count": count} for shape, count in flood_shapes.most_common(10)
        ],
        "representative_static_layer_shapes": [
            {"shape": list(shape), "count": count} for shape, count in static_shapes.most_common(10)
        ],
        "representative_flood_spatial_shape": representative_flood_spatial,
        "representative_flood_spatial_shape_source": "forecast_maps.npz"
        if npz_representative_flood_spatial
        else ".npy flood_depth arrays"
        if representative_flood_spatial
        else None,
        "dem_static_elevation_shape_compatible": bool(compatible_dem),
        "compatible_dem_static_elevation_files": compatible_dem,
        "explicit_report": (
            "Shape-compatible DEM/static elevation was found."
            if compatible_dem
            else "Shape-compatible DEM/static elevation was not found in the scanned repository files."
        ),
    }


def inspect_npz_keys(path: Path) -> dict[str, Any]:
    record = {
        "relative_path": display_path(path),
        "keys": [],
        "has_prediction_key": False,
        "has_target_key": False,
        "looks_like_map_array_file": False,
        "error": None,
    }
    try:
        with np.load(path, allow_pickle=False) as arrays:
            keys = list(arrays.files)
        lower_keys = [key.lower() for key in keys]
        record["keys"] = keys
        record["has_prediction_key"] = any(any(token == key or token in key for token in PREDICTION_TOKENS) for key in lower_keys)
        record["has_target_key"] = any(any(token == key or token in key for token in TARGET_TOKENS) for key in lower_keys)
        record["looks_like_map_array_file"] = any(any(token in key for token in MAP_TOKENS) for key in lower_keys)
    except Exception as exc:  # noqa: BLE001
        record["error"] = f"{type(exc).__name__}: {exc}"
    return record


def discover_phase_candidate_files(roots: list[Path], max_per_phase: int = 1000) -> dict[str, list[Path]]:
    wanted_suffixes = {".npz", ".npy", ".json", ".csv", ".md", ".png"}
    results = {"phase10": [], "phase25": []}
    seen: set[tuple[Path, tuple[str, ...]]] = set()
    stack = [root for root in roots if root.exists()]
    while stack:
        root = stack.pop()
        try:
            children = sorted(root.iterdir(), key=lambda item: str(item).lower())
        except OSError:
            continue
        for child in children:
            if child.name in SKIP_DIR_NAMES:
                continue
            if child.is_dir():
                stack.append(child)
                continue
            if not child.is_file() or child.suffix.lower() not in wanted_suffixes:
                continue
            rel = display_path(child).lower()
            phases = []
            if "phase10" in rel:
                phases.append("phase10")
            if "phase25" in rel:
                phases.append("phase25")
            if not phases:
                continue
            try:
                resolved = child.resolve()
            except OSError:
                resolved = child
            phase_seen_key = (resolved, tuple(phases))
            if phase_seen_key in seen:
                continue
            seen.add(phase_seen_key)
            for phase in phases:
                if len(results[phase]) < max_per_phase:
                    results[phase].append(child)
    for phase in results:
        results[phase] = sorted(results[phase], key=display_path)
    return results


def read_phase25_aligned_comparison_hints() -> dict[str, Any]:
    base = REPO_ROOT / PHASE25_COMPARISON_DIR
    outputs: dict[str, Any] = {}
    if not base.exists():
        return outputs
    for path in sorted(base.glob("aligned_comparison*/aligned_comparison_summary.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        alignment = data.get("alignment", {})
        phase10_filter = alignment.get("phase10_subset_filter", {})
        phase25_filter = alignment.get("phase25_subset_filter", {})
        phase25_token = str(phase25_filter.get("run_token", ""))
        seed = infer_seed(Path(phase25_token)) or infer_seed(path) or "unknown"
        outputs[seed] = {
            "summary_path": display_path(path),
            "phase10_run_token": phase10_filter.get("run_token"),
            "phase25_run_token": phase25_filter.get("run_token"),
            "common_rows": alignment.get("common_rows"),
            "key_columns": alignment.get("key_columns"),
            "phase25_improves_false_dry_rate": data.get("phase25_improves_false_dry_rate"),
            "phase25_improves_wet_area_contraction": data.get("phase25_improves_wet_area_contraction"),
        }
    return outputs


def discover_phase25_seed_runs(npz_files: list[Path]) -> dict[str, Any]:
    found: dict[str, Any] = {}
    for seed in PHASE25_SEEDS:
        matching_runs = sorted(
            {
                run_name_from_path(path)
                for path in npz_files
                if f"phase25_target_wet_recall_{seed}" in display_path(path).lower()
            }
            - {None}
        )
        found[seed] = {
            "target_wet_recall_run_found": bool(matching_runs),
            "run_names": matching_runs,
        }
    return found


def discover_phase_outputs(
    roots: list[Path],
    npz_map_summary: dict[str, Any],
    phase25_run_search: dict[str, Any],
    aligned_hints: dict[str, Any],
) -> dict[str, Any]:
    candidates_by_phase = discover_phase_candidate_files(roots)
    phase_records: dict[str, dict[str, Any]] = {
        "phase10": {"candidate_files": [], "map_array_candidates": [], "prediction_target_maps_available": "unclear"},
        "phase25": {"candidate_files": [], "map_array_candidates": [], "prediction_target_maps_available": "unclear"},
    }
    for phase, candidates in candidates_by_phase.items():
        total_candidates = len(candidates)
        for path in candidates:
            rel = display_path(path)
            lower = rel.lower()
            phase_records[phase]["candidate_files"].append(rel)
            if path.suffix.lower() == ".npz":
                npz_record = inspect_npz_keys(path)
                if (
                    npz_record["has_prediction_key"]
                    or npz_record["has_target_key"]
                    or npz_record["looks_like_map_array_file"]
                ):
                    phase_records[phase]["map_array_candidates"].append(npz_record)
            elif path.suffix.lower() == ".npy" and any(token in lower for token in (*PREDICTION_TOKENS, *TARGET_TOKENS, "map")):
                phase_records[phase]["map_array_candidates"].append({"relative_path": rel, "type": "npy_candidate"})
        phase_records[phase]["total_candidate_file_count"] = total_candidates

    for phase, record in phase_records.items():
        phase_npz = npz_map_summary["by_phase"].get(phase, {})
        record["representative_forecast_maps"] = phase_npz.get("representative_files", [])
        record["evaluation_test_prediction_target_available"] = phase_npz.get(
            "evaluation_test_prediction_target_available", False
        )
        record["prediction_target_shape_compatible"] = phase_npz.get("prediction_target_shape_compatible")
        exact = [
            item
            for item in record["representative_forecast_maps"]
            if item.get("prediction_keys") and item.get("target_keys")
        ]
        if record["evaluation_test_prediction_target_available"]:
            record["prediction_target_maps_available"] = "supported"
            record["availability_note"] = (
                "Evaluation-test forecast_maps.npz files have recognizable prediction and target arrays; "
                "these are preferred over visualization epoch artifacts."
            )
        elif exact:
            record["prediction_target_maps_available"] = "supported"
            record["availability_note"] = (
                "Visualization forecast_maps.npz files have recognizable prediction and target arrays, "
                "but evaluation-test paired maps were not found among representatives."
            )
        elif record["representative_forecast_maps"]:
            record["prediction_target_maps_available"] = "unclear"
            record["availability_note"] = "Candidate map files exist, but exact paired prediction/target arrays are uncertain."
        else:
            record["prediction_target_maps_available"] = "not supported"
            record["availability_note"] = "No obvious prediction/target map array files were found for this phase."
        record["candidate_files"] = record["candidate_files"][:200]
        record["candidate_file_count"] = len(record["candidate_files"])
        record.setdefault("total_candidate_file_count", record["candidate_file_count"])
    phase_records["phase10"]["recommended_baseline_policy"] = (
        "Use boundary_weight=2.0 / w20 when available. Phase 10 runs without an explicit w suffix are treated as "
        "the recommended boundary_weight=2.0 baseline when their run token is phase10_margin_aware_boundary_band_seed*. "
        "w15 / boundary_weight=1.5 runs are rollback or non-default candidates."
    )
    phase_records["phase25_target_wet_recall_seed_search"] = phase25_run_search
    phase_records["aligned_phase10_vs_phase25_comparison_hints"] = aligned_hints
    return phase_records


def read_text_sample(path: Path) -> str | None:
    try:
        if path.stat().st_size > MAX_TEXT_BYTES:
            return None
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None


def metadata_matches(text: str, path: Path) -> dict[str, list[str]]:
    haystack = f"{display_path(path)}\n{text}".lower()
    matches: dict[str, list[str]] = {}
    for key, patterns in METADATA_PATTERNS.items():
        hit_patterns = []
        for pattern in patterns:
            if re.search(pattern, haystack, flags=re.IGNORECASE):
                hit_patterns.append(pattern)
        if hit_patterns:
            matches[key] = hit_patterns[:5]
    return matches


def audit_metadata(roots: list[Path], max_files: int) -> dict[str, Any]:
    files = safe_iter_files(roots, suffixes=TEXT_EXTENSIONS, max_files=max_files)
    items = {key: {"status": "missing", "candidate_files": []} for key in METADATA_PATTERNS}
    dataset_roots = []
    for path in files:
        text = read_text_sample(path)
        if text is None:
            continue
        if path.suffix.lower() in {".json", ".yaml", ".yml"} and "dataset_root" in text:
            dataset_roots.extend(extract_dataset_roots(text, path))
        for key, patterns in metadata_matches(text, path).items():
            items[key]["candidate_files"].append({"relative_path": display_path(path), "matched_patterns": patterns})

    for key, item in items.items():
        if item["candidate_files"]:
            if key in {"dt_or_time_interval", "scenario_metadata", "train_test_split", "source_sink_infiltration_drainage"}:
                item["status"] = "found"
            else:
                item["status"] = "unclear"
            item["candidate_files"] = item["candidate_files"][:25]
        item["candidate_count"] = len(item["candidate_files"])
    return {"items": items, "referenced_dataset_roots": dataset_roots}


def extract_dataset_roots(text: str, path: Path) -> list[dict[str, Any]]:
    roots = []
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        data = None
    if isinstance(data, dict) and "dataset_root" in data:
        root_value = str(data["dataset_root"])
        root_path = Path(root_value)
        roots.append(
            {
                "config_file": display_path(path),
                "dataset_root": root_value,
                "exists": root_path.exists() if root_path.is_absolute() else (REPO_ROOT / root_path).exists(),
                "note": "Recorded as configured metadata; not recursively scanned unless it is inside the repository.",
            }
        )
    return roots


def classify_feasibility(
    arrays: list[dict[str, Any]],
    shape_summary: dict[str, Any],
    phase_outputs: dict[str, Any],
    metadata: dict[str, Any],
) -> dict[str, Any]:
    categories = Counter(item["category"] for item in arrays)
    has_flood = categories["flood_depth"] > 0
    has_rain = categories["rainfall"] > 0
    has_static = any(categories[name] > 0 for name in STATIC_CATEGORIES)
    has_dem = categories["dem_elevation"] > 0
    has_compatible_dem = bool(shape_summary["dem_static_elevation_shape_compatible"])
    has_phase_maps = any(
        record.get("prediction_target_maps_available") in {"supported", "unclear"} for record in phase_outputs.values()
    )
    meta_items = metadata["items"]
    has_dt = meta_items["dt_or_time_interval"]["status"] in {"found", "unclear"}
    has_dxdy = meta_items["dx_dy_or_spatial_resolution"]["status"] in {"found", "unclear"}
    has_boundary = meta_items["boundary_conditions"]["status"] == "found" or categories["boundary"] > 0
    has_source_sink = meta_items["source_sink_infiltration_drainage"]["status"] == "found"
    has_pumps = meta_items["pump_gate_operations"]["status"] == "found"
    has_velocity_flux = meta_items["velocity_or_flux_fields"]["status"] == "found"

    exact_phase_maps = any(record.get("prediction_target_maps_available") == "supported" for record in phase_outputs.values())
    if exact_phase_maps:
        diagnostics_status = "partially supported"
        diagnostics_reason = (
            "Paired Phase 10/25 prediction and target map artifacts are available, so conservation/volume-response "
            "diagnostics are feasible at a volume-proxy or aggregate depth level. Strict conservation residuals "
            "remain limited by missing or unclear dx/dy, boundary fluxes, and source/sink terms."
        )
    elif has_phase_maps and (has_flood or phase_outputs["phase10"]["map_array_candidates"] or phase_outputs["phase25"]["map_array_candidates"]):
        diagnostics_status = "partially supported"
        diagnostics_reason = (
            "Existing Phase 10/25 outputs and physical consistency summaries provide candidates for "
            "conservation/volume-response diagnostics, but direct paired prediction/target map arrays are not "
            "fully confirmed by this audit unless marked supported above."
        )
    elif has_flood and has_rain:
        diagnostics_status = "partially supported"
        diagnostics_reason = (
            "Raw flood-depth and rainfall arrays can support volume-response diagnostics, but existing paired "
            "prediction/target map outputs were not confirmed."
        )
    else:
        diagnostics_status = "unclear"
        diagnostics_reason = "The scanned repository lacks enough obvious raw arrays or paired prediction maps."

    if has_flood and has_rain and has_static:
        loss_status = "partially supported"
        loss_reason = (
            "Flood, rainfall, and static-layer inputs are enough to design a conservative volume-response loss "
            "at a high level, but missing or unclear dt/dx/dy, source/sink terms, and boundary fluxes prevent a "
            "strict conservation loss from being fully specified."
        )
    else:
        loss_status = "unclear"
        loss_reason = "The scanned repository does not expose all raw flood/rain/static arrays needed for a concrete future loss design."

    if has_velocity_flux and has_boundary and has_source_sink and has_dt and has_dxdy and has_compatible_dem:
        swe_status = "partially supported"
        swe_reason = (
            "Some SWE/PINN ingredients appear in metadata, but this audit does not verify complete velocity, flux, "
            "boundary, pump/gate, and source/sink fields as aligned arrays."
        )
    else:
        swe_status = "not supported"
        missing = []
        if not has_velocity_flux:
            missing.append("velocity fields or flux/discharge fields")
        if not has_boundary:
            missing.append("boundary inflow/outflow conditions")
        if not has_pumps:
            missing.append("pump/gate operations")
        if not has_source_sink:
            missing.append("source/sink, infiltration, or drainage terms")
        if not has_dt:
            missing.append("dt or explicit time interval")
        if not has_dxdy:
            missing.append("dx/dy or spatial resolution")
        if not has_compatible_dem:
            missing.append("shape-compatible DEM/static elevation")
        swe_reason = "Full SWE/PINN residual constraints are not supported by the current scanned evidence; missing: " + ", ".join(missing) + "."

    return {
        "level_4_conservation_oriented_diagnostics": {
            "classification": diagnostics_status,
            "explanation": diagnostics_reason,
        },
        "level_4_conservation_aware_loss_design": {
            "classification": loss_status,
            "explanation": loss_reason,
        },
        "level_5_full_swe_pinn_residual_constraints": {
            "classification": swe_status,
            "explanation": swe_reason,
        },
        "explicit_answers": {
            "current_data_support_conservation_volume_response_diagnostics": diagnostics_status,
            "future_conservative_volume_response_loss": loss_status,
            "full_swe_pinn_residuals": swe_status,
        },
    }


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def format_count_table(counter: Counter[str]) -> str:
    if not counter:
        return "- None found\n"
    return "\n".join(f"- `{key}`: {count}" for key, count in sorted(counter.items())) + "\n"


def write_markdown(path: Path, report: dict[str, Any]) -> None:
    arrays = report["dataset_and_array_availability"]["npy_files"]
    npz_maps = report["dataset_and_array_availability"]["npz_forecast_maps"]
    category_counts = Counter(item["category"] for item in arrays)
    shape_summary = report["shape_compatibility"]
    phase_outputs = report["existing_model_output_availability"]
    feasibility = report["strong_physics_feasibility_classification"]
    metadata = report["metadata_availability"]["items"]

    lines = [
        "# Phase 26 Physics Input Audit",
        "",
        "This diagnostic audit is read-only except for the files in this Phase 26 output directory. It does not train models or change model/loss code.",
        "",
        "## Dataset and Array Availability",
        "",
        f"- `.npy` files inspected: {len(arrays)}",
        f"- `forecast_maps.npz` files found under `runs/`: {npz_maps['total_forecast_map_npz_count']}",
        f"- `forecast_maps.npz` files considered for representative selection: {report['dataset_and_array_availability']['npz_forecast_map_files_considered']}",
        f"- Representative `forecast_maps.npz` files inspected: {len(npz_maps['representative_forecast_maps'])}",
        "",
        format_count_table(category_counts),
        "Top discovered `.npy` files:",
        "",
    ]
    if arrays:
        lines.extend(["| Path | Category | Shape | Dtype | Min | Max | Mean |", "| --- | --- | --- | --- | ---: | ---: | ---: |"])
        for item in arrays[:40]:
            lines.append(
                f"| `{item['relative_path']}` | {item['category']} | {item['shape']} | {item['dtype']} | "
                f"{item['min']} | {item['max']} | {item['mean']} |"
            )
    else:
        lines.append("No `.npy` files were found in the scanned repository directories.")

    lines.extend(
        [
            "",
            "## Shape Compatibility",
            "",
            f"- Representative flood spatial shape: `{shape_summary['representative_flood_spatial_shape']}`",
            f"- Representative flood spatial shape source: `{shape_summary['representative_flood_spatial_shape_source']}`",
            f"- DEM/static elevation shape-compatible: `{shape_summary['dem_static_elevation_shape_compatible']}`",
            f"- Report: {shape_summary['explicit_report']}",
            "",
            "## Representative Forecast Map Archives",
            "",
            "| Phase | Seed | Split | Baseline role | Path | Keys | Prediction/target compatible |",
            "| --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for item in npz_maps["representative_forecast_maps"]:
        lines.append(
            f"| {item['phase']} | {item['seed']} | {item['split']} | "
            f"{item.get('phase10_baseline_role') or ''} | `{item['relative_path']}` | "
            f"`{', '.join(item['keys'])}` | `{item['prediction_target_shape_compatible']}` |"
        )
    lines.extend(
        [
            "",
            "## Existing Model Output Availability",
            "",
        ]
    )
    for phase in ("phase10", "phase25"):
        item = phase_outputs[phase]
        lines.extend(
            [
                f"### {phase.capitalize()}",
                "",
                f"- Prediction/target map arrays: `{item['prediction_target_maps_available']}`",
                f"- Evaluation-test prediction/target arrays available: `{item['evaluation_test_prediction_target_available']}`",
                f"- Prediction/target arrays shape-compatible: `{item['prediction_target_shape_compatible']}`",
                f"- Candidate files found: {item['total_candidate_file_count']} (showing {item['candidate_file_count']})",
                f"- Note: {item['availability_note']}",
                "",
            ]
        )
        for candidate in item["representative_forecast_maps"]:
            roles = ", ".join(
                f"{array['key']}:{array['role']} {array['shape']} {array['dtype']} "
                f"min={array['min']} max={array['max']} mean={array['mean']}"
                for array in candidate.get("arrays", [])
            )
            lines.append(f"- Representative map: `{candidate['relative_path']}` ({roles})")
        lines.append("")

    lines.extend(
        [
            "### Phase 10 Baseline Policy",
            "",
            f"- {phase_outputs['phase10']['recommended_baseline_policy']}",
            "",
            "### Phase 25 Target-Wet Recall Seed Search",
            "",
        ]
    )
    for seed, item in phase_outputs["phase25_target_wet_recall_seed_search"].items():
        lines.append(f"- `{seed}`: found `{item['target_wet_recall_run_found']}`; runs: `{', '.join(item['run_names'])}`")

    lines.extend(["", "### Aligned Phase 10 vs Phase 25 Comparison Hints", ""])
    for seed, item in phase_outputs["aligned_phase10_vs_phase25_comparison_hints"].items():
        lines.append(
            f"- `{seed}`: Phase 10 `{item['phase10_run_token']}` vs Phase 25 `{item['phase25_run_token']}`, "
            f"common rows `{item['common_rows']}`, source `{item['summary_path']}`"
        )

    lines.extend(["## Metadata Availability", ""])
    for key, item in metadata.items():
        lines.append(f"- `{key}`: {item['status']} ({item['candidate_count']} candidate files)")

    lines.extend(["", "## Strong Physics Feasibility Classification", ""])
    for key, item in feasibility.items():
        if key == "explicit_answers":
            continue
        lines.extend(
            [
                f"### {key.replace('_', ' ').title()}",
                "",
                f"- Classification: `{item['classification']}`",
                f"- Explanation: {item['explanation']}",
                "",
            ]
        )

    lines.extend(
        [
            "## Missing Inputs for Full SWE/PINN Residuals",
            "",
            "The audit is conservative. Full residual constraints require aligned velocity or flux fields, boundary inflow/outflow, pump/gate operations, source/sink or infiltration/drainage terms, explicit dt, dx/dy, and shape-compatible DEM/static elevation. Items not directly found above should be treated as missing or unclear, not inferred.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    args = parse_args()
    output_dir = resolve_repo_path(args.output_dir)
    roots = scan_roots()
    npy_files = safe_iter_files(roots, suffixes={".npy"}, max_files=args.max_npy_files)
    npy_records = [inspect_npy(path, args.max_npy_bytes_for_stats) for path in npy_files]
    total_npz_files, npz_files = discover_map_npz_files(args.max_npz_files)
    representative_npz_files = select_representative_npz_files(npz_files)
    npz_records = [inspect_npz(path, args.max_npz_bytes_for_stats) for path in representative_npz_files]
    npz_map_summary = summarize_npz_maps(npz_records, total_npz_files)
    phase25_run_search = discover_phase25_seed_runs(npz_files)
    aligned_hints = read_phase25_aligned_comparison_hints()
    shape_summary = summarize_shapes(npy_records, npz_map_summary)
    phase_outputs = discover_phase_outputs(roots, npz_map_summary, phase25_run_search, aligned_hints)
    metadata = audit_metadata(roots, args.max_text_files)
    feasibility = classify_feasibility(npy_records, shape_summary, phase_outputs, metadata)

    report = {
        "audit_scope": {
            "repository_root": str(REPO_ROOT),
            "scanned_roots": [display_path(path) for path in roots],
            "read_only_note": "Script reads repository files and writes only Phase 26 audit outputs.",
        },
        "dataset_and_array_availability": {
            "npy_file_count": len(npy_records),
            "npy_files": npy_records,
            "npz_forecast_map_file_count": total_npz_files,
            "npz_forecast_map_files_considered": len(npz_files),
            "npz_forecast_maps": npz_map_summary,
            "category_counts": dict(Counter(item["category"] for item in npy_records)),
        },
        "shape_compatibility": shape_summary,
        "existing_model_output_availability": phase_outputs,
        "metadata_availability": metadata,
        "strong_physics_feasibility_classification": feasibility,
    }

    json_path = output_dir / "physics_input_audit.json"
    md_path = output_dir / "physics_input_audit.md"
    write_json(json_path, report)
    write_markdown(md_path, report)

    print("Phase 26 physics input audit complete.")
    print(f"  npy files inspected: {len(npy_records)}")
    print(f"  forecast_maps.npz files found: {total_npz_files}")
    print(f"  forecast_maps.npz files considered: {len(npz_files)}")
    print(f"  representative forecast_maps.npz files inspected: {len(npz_records)}")
    print(f"  Representative flood spatial shape: {shape_summary['representative_flood_spatial_shape']}")
    print(f"  DEM/static elevation shape-compatible: {shape_summary['dem_static_elevation_shape_compatible']}")
    print(f"  Phase 10 map availability: {phase_outputs['phase10']['prediction_target_maps_available']}")
    print(f"  Phase 25 map availability: {phase_outputs['phase25']['prediction_target_maps_available']}")
    print(f"  Wrote: {display_path(json_path)}")
    print(f"  Wrote: {display_path(md_path)}")


if __name__ == "__main__":
    main()
