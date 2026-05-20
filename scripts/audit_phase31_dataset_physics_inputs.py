from __future__ import annotations

import argparse
import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable

import numpy as np


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = Path("analysis/phase31_physics_input_recovery_readiness")

REPO_SCAN_ROOTS = (
    "configs",
    "data",
    "datasets",
    "utils",
    "scripts",
    "analysis/phase26_strong_physics_constraint_feasibility",
)

DATASET_PATH_FIELD_NAMES = {
    "data_root",
    "dataset_root",
    "root",
    "data_dir",
    "dataset_dir",
    "input_dir",
    "dataset_config_path",
}

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

ARRAY_EXTENSIONS = {".npy", ".npz"}
METADATA_EXTENSIONS = {".json", ".csv", ".txt", ".md"}
AUDIT_EXTENSIONS = ARRAY_EXTENSIONS | METADATA_EXTENSIONS | {".py"}

STATIC_ROLE_TOKENS: dict[str, tuple[str, ...]] = {
    "dem_static_elevation": ("absolute_dem", "dem", "elev", "elevation", "topo", "topography", "terrain", "dtm", "dsm"),
    "impervious": ("impervious", "imperv"),
    "manhole_drainage": ("manhole", "drain", "drainage", "sewer", "inlet", "outlet", "pipe"),
    "domain_mask": ("domain_mask", "valid_mask", "valid", "mask", "nodata"),
    "boundary_mask": ("boundary_mask", "boundary", "bound", "edge", "border"),
}

PHYSICAL_EVIDENCE_PATTERNS: dict[str, tuple[str, ...]] = {
    "time_alignment": ("timestep", r"\bdt\b", "interval", "duration", "hours", "rainfall", "scenario", "input_steps", "pred_steps", "stride"),
    "spatial_resolution": ("grid", "resolution", r"\bdx\b", r"\bdy\b", "cell_size", "pixel_size", "spatial"),
    "velocity_flux_discharge": ("velocity", "flux", "discharge", "flow_rate", "u_velocity", "v_velocity"),
    "boundary_inflow_outflow": ("boundary", "inflow", "outflow", "open boundary"),
    "pump_gate_operations": ("pump", "gate", "sluice"),
    "drainage_sewer_manhole": ("drainage", "sewer", "manhole", "inlet", "outlet", "pipe"),
    "infiltration_source_sink": ("infiltration", "source", "sink"),
    "mask_domain_boundary": ("valid mask", "domain mask", "boundary mask", "valid_mask", "domain_mask", "boundary_mask"),
}

PREDICTION_TOKENS = ("prediction", "predictions", "pred", "forecast", "output", "y_pred")
TARGET_TOKENS = ("target", "targets", "truth", "ground_truth", "label", "labels", "y_true")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Phase 31 diagnostic-only inventory of repository and dataset physical inputs. "
            "The script does not train and writes only Phase 31 inventory outputs."
        )
    )
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--max-array-files", type=int, default=5000)
    parser.add_argument("--max-text-files", type=int, default=5000)
    parser.add_argument("--max-text-bytes", type=int, default=1_000_000)
    parser.add_argument("--max-array-bytes-for-stats", type=int, default=512 * 1024 * 1024)
    parser.add_argument("--max-forecast-map-files", type=int, default=250)
    return parser.parse_args()


def display_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT)).replace("\\", "/")
    except ValueError:
        return str(path)


def resolve_path(value: str, *, base_dir: Path | None = None) -> Path:
    path = Path(value).expanduser()
    if path.is_absolute():
        return path
    if base_dir is not None:
        candidate = (base_dir / path).resolve()
        if candidate.exists():
            return candidate
    return (REPO_ROOT / path).resolve()


def safe_float(value: Any) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError, OverflowError):
        return None
    if math.isnan(number) or math.isinf(number):
        return None
    return number


def safe_iter_files(
    roots: Iterable[Path],
    *,
    suffixes: set[str] | None = None,
    max_files: int | None = None,
) -> list[Path]:
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


def repo_roots() -> list[Path]:
    return [REPO_ROOT / root for root in REPO_SCAN_ROOTS if (REPO_ROOT / root).exists()]


def nested_json_items(value: Any, prefix: tuple[str, ...] = ()) -> Iterable[tuple[tuple[str, ...], Any]]:
    if isinstance(value, dict):
        for key, child in value.items():
            yield from nested_json_items(child, prefix + (str(key),))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from nested_json_items(child, prefix + (str(index),))
    else:
        yield prefix, value


def looks_like_path(value: str) -> bool:
    lower = value.lower()
    if any(sep in value for sep in ("\\", "/")):
        return True
    return lower.endswith((".json", ".npy", ".npz", ".csv", ".txt", ".md"))


def discover_config_paths() -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    seen_values: set[tuple[str, str, str]] = set()
    for config_path in sorted((REPO_ROOT / "configs").glob("*.json")):
        try:
            data = json.loads(config_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        for key_path, value in nested_json_items(data):
            if not key_path or not isinstance(value, str) or not value:
                continue
            field = key_path[-1]
            if field not in DATASET_PATH_FIELD_NAMES:
                continue
            if not looks_like_path(value):
                continue
            resolved = resolve_path(value, base_dir=config_path.parent)
            key = (display_path(config_path), ".".join(key_path), str(resolved))
            if key in seen_values:
                continue
            seen_values.add(key)
            records.append(
                {
                    "config_file": display_path(config_path),
                    "field": ".".join(key_path),
                    "value": value,
                    "resolved_path": str(resolved),
                    "exists": resolved.exists(),
                    "is_dir": resolved.is_dir(),
                    "is_file": resolved.is_file(),
                }
            )

    # Follow config-referenced JSON files such as dataset_config_path and extract their roots.
    extra_records: list[dict[str, Any]] = []
    for record in records:
        path = Path(record["resolved_path"])
        if not record["exists"] or path.suffix.lower() != ".json":
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        for key_path, value in nested_json_items(data):
            if not key_path or not isinstance(value, str) or not value:
                continue
            field = key_path[-1]
            if field not in DATASET_PATH_FIELD_NAMES or not looks_like_path(value):
                continue
            resolved = resolve_path(value, base_dir=path.parent)
            extra_records.append(
                {
                    "config_file": display_path(path),
                    "field": ".".join(key_path),
                    "value": value,
                    "resolved_path": str(resolved),
                    "exists": resolved.exists(),
                    "is_dir": resolved.is_dir(),
                    "is_file": resolved.is_file(),
                }
            )

    for record in extra_records:
        key = (record["config_file"], record["field"], record["resolved_path"])
        if key not in seen_values:
            seen_values.add(key)
            records.append(record)
    return records


def dataset_roots_from_config(records: list[dict[str, Any]]) -> list[Path]:
    roots: list[Path] = []
    seen: set[Path] = set()
    for record in records:
        path = Path(record["resolved_path"])
        field_path = str(record["field"])
        field = field_path.split(".")[-1]
        if not record["exists"] or not record["is_dir"]:
            continue
        if field_path.startswith("output."):
            continue
        if field not in {"data_root", "dataset_root", "root", "data_dir", "dataset_dir", "input_dir"}:
            continue
        path_text = str(path).lower()
        if field == "root" and not any(token in path_text for token in ("data", "dataset", "urbanflood")):
            continue
        try:
            resolved = path.resolve()
        except OSError:
            resolved = path
        if resolved in seen:
            continue
        seen.add(resolved)
        roots.append(path)
    return roots


def infer_semantic_role(path: Path) -> str:
    lower = path.name.lower()
    stem = path.stem.lower()
    if lower == "rainfall.npy" or "rainfall" in stem or "precip" in stem:
        return "rainfall"
    if lower == "flood.npy" or "flood" in stem or "depth" in stem:
        return "flood_depth"
    for role, tokens in STATIC_ROLE_TOKENS.items():
        if any(token in stem for token in tokens):
            return role
    if any(token in stem for token in ("velocity", "flux", "discharge", "flow_rate")):
        return "velocity_flux_discharge"
    if any(token in stem for token in ("inflow", "outflow", "source", "sink", "infiltration")):
        return "source_sink_or_boundary"
    if path.suffix.lower() in ARRAY_EXTENSIONS:
        return "array_unknown"
    return "metadata"


def spatial_dims(shape: list[int] | None) -> list[int] | None:
    if not shape or len(shape) < 2:
        return None
    return [int(shape[-2]), int(shape[-1])]


def inspect_npy(path: Path, max_stats_bytes: int) -> dict[str, Any]:
    record: dict[str, Any] = {
        "path": display_path(path),
        "name": path.name,
        "semantic_role": infer_semantic_role(path),
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
    except Exception as exc:  # noqa: BLE001 - diagnostic audit should continue.
        record["error"] = f"{type(exc).__name__}: {exc}"
        record["stats_status"] = "error"
    return record


def classify_npz_key(key: str) -> str:
    lower = key.lower()
    if any(token == lower or token in lower for token in PREDICTION_TOKENS):
        return "prediction"
    if any(token == lower or token in lower for token in TARGET_TOKENS):
        return "target"
    return "unknown"


def inspect_forecast_npz(path: Path, max_stats_bytes: int) -> dict[str, Any]:
    record: dict[str, Any] = {
        "path": display_path(path),
        "keys": [],
        "arrays": [],
        "prediction_target_compatible": None,
        "representative_flood_spatial_shape": None,
        "error": None,
    }
    try:
        with np.load(path, allow_pickle=False) as arrays:
            record["keys"] = list(arrays.files)
            for key in arrays.files:
                arr = arrays[key]
                item: dict[str, Any] = {
                    "key": key,
                    "role": classify_npz_key(key),
                    "shape": [int(dim) for dim in arr.shape],
                    "dtype": str(arr.dtype),
                    "min": None,
                    "max": None,
                    "mean": None,
                    "stats_status": "not_loaded",
                }
                if np.issubdtype(arr.dtype, np.number) and arr.nbytes <= max_stats_bytes:
                    values = np.asarray(arr)
                    if values.size:
                        item["min"] = safe_float(np.nanmin(values))
                        item["max"] = safe_float(np.nanmax(values))
                        item["mean"] = safe_float(np.nanmean(values))
                        item["stats_status"] = "computed"
                    else:
                        item["stats_status"] = "empty_array"
                else:
                    item["stats_status"] = "skipped_large_or_non_numeric"
                record["arrays"].append(item)
    except Exception as exc:  # noqa: BLE001
        record["error"] = f"{type(exc).__name__}: {exc}"
        return record

    pred_shapes = {tuple(item["shape"]) for item in record["arrays"] if item["role"] == "prediction"}
    target_shapes = {tuple(item["shape"]) for item in record["arrays"] if item["role"] == "target"}
    if pred_shapes and target_shapes:
        record["prediction_target_compatible"] = bool(pred_shapes & target_shapes)
    for item in record["arrays"]:
        if item["role"] in {"prediction", "target"}:
            record["representative_flood_spatial_shape"] = spatial_dims(item["shape"])
            break
    return record


def discover_forecast_maps(max_files: int) -> tuple[int, list[Path]]:
    runs_root = REPO_ROOT / "runs"
    if not runs_root.exists():
        return 0, []
    files = sorted(runs_root.glob("**/evaluation_test/**/forecast_maps.npz"), key=display_path)
    return len(files), files[:max_files]


def inspect_text_file(path: Path, max_text_bytes: int) -> dict[str, Any] | None:
    try:
        if path.stat().st_size > max_text_bytes:
            return None
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    haystack = f"{display_path(path)}\n{text}".lower()
    matches: dict[str, list[str]] = {}
    for category, patterns in PHYSICAL_EVIDENCE_PATTERNS.items():
        found = []
        for pattern in patterns:
            if re.search(pattern, haystack, flags=re.IGNORECASE):
                found.append(pattern)
        if found:
            matches[category] = found[:8]
    if not matches:
        return None
    numeric_time_value = bool(
        re.search(r"\b(dt|timestep|time[_ -]?step|interval|duration|hours)\b[^0-9\n\r]{0,30}[0-9]+(\.[0-9]+)?", haystack)
    )
    numeric_spatial_value = bool(
        re.search(r"\b(dx|dy|cell[_ -]?size|pixel[_ -]?size|spatial[_ -]?resolution|grid[_ -]?resolution)\b[^0-9\n\r]{0,30}[0-9]+(\.[0-9]+)?", haystack)
    )
    return {
        "path": display_path(path),
        "matches": matches,
        "numeric_time_value": numeric_time_value,
        "numeric_spatial_value": numeric_spatial_value,
    }


def summarize_time_alignment(array_records: list[dict[str, Any]], text_hits: list[dict[str, Any]]) -> dict[str, Any]:
    flood_shapes = Counter(tuple(item["shape"]) for item in array_records if item["semantic_role"] == "flood_depth" and item["shape"])
    rainfall_shapes = Counter(tuple(item["shape"]) for item in array_records if item["semantic_role"] == "rainfall" and item["shape"])
    ratios = []
    flood_by_dir = {str(Path(item["path"]).parent): item for item in array_records if item["name"] == "flood.npy" and item["shape"]}
    rainfall_by_dir = {str(Path(item["path"]).parent): item for item in array_records if item["name"] == "rainfall.npy" and item["shape"]}
    for parent, flood in flood_by_dir.items():
        rain = rainfall_by_dir.get(parent)
        if not rain:
            continue
        flood_steps = flood["shape"][0] if flood["shape"] else None
        rainfall_steps = rain["shape"][0] if rain["shape"] else None
        ratio = safe_float(flood_steps / rainfall_steps) if flood_steps and rainfall_steps else None
        ratios.append(
            {
                "event_dir": parent.replace("\\", "/"),
                "flood_steps": flood_steps,
                "rainfall_steps": rainfall_steps,
                "possible_timestep_ratio": ratio,
            }
        )
    explicit_dt_hits = [hit for hit in text_hits if "time_alignment" in hit["matches"] and hit.get("numeric_time_value")]
    if explicit_dt_hits:
        status = "explicit_or_metadata_evidence_found"
    elif ratios:
        status = "inferred_ratio_only"
    elif flood_shapes or rainfall_shapes:
        status = "unclear"
    else:
        status = "missing"
    return {
        "flood_shapes": [{"shape": list(shape), "count": count} for shape, count in flood_shapes.most_common(10)],
        "rainfall_shapes": [{"shape": list(shape), "count": count} for shape, count in rainfall_shapes.most_common(10)],
        "paired_flood_rainfall_ratios": ratios[:50],
        "dt_status": status,
        "metadata_candidate_files": [hit for hit in text_hits if "time_alignment" in hit["matches"]][:50],
    }


def summarize_spatial_resolution(text_hits: list[dict[str, Any]]) -> dict[str, Any]:
    hits = [hit for hit in text_hits if "spatial_resolution" in hit["matches"]]
    explicit = [hit for hit in hits if hit.get("numeric_spatial_value")]
    if explicit:
        status = "metadata_evidence_found"
    elif hits:
        status = "candidate_mentions_only"
    else:
        status = "missing"
    return {"dx_dy_status": status, "candidate_files": hits[:50]}


def summarize_static_compatibility(array_records: list[dict[str, Any]], representative_flood_spatial: list[int] | None) -> dict[str, Any]:
    static_roles = set(STATIC_ROLE_TOKENS)
    static_records = [item for item in array_records if item["semantic_role"] in static_roles]
    for item in static_records:
        item["shape_compatible_with_representative_flood"] = (
            spatial_dims(item["shape"]) == representative_flood_spatial if representative_flood_spatial else None
        )
        item["shape_compatible_with_128x128"] = spatial_dims(item["shape"]) == [128, 128]
    compatible_elevation = [
        item for item in static_records if item["semantic_role"] == "dem_static_elevation" and item.get("shape_compatible_with_representative_flood")
    ]
    return {
        "static_map_records": static_records,
        "dem_static_elevation_compatible": bool(compatible_elevation),
        "compatible_dem_static_elevation_files": [item["path"] for item in compatible_elevation],
    }


def evidence_status(text_hits: list[dict[str, Any]], categories: Iterable[str]) -> dict[str, Any]:
    category_set = set(categories)
    hits = [hit for hit in text_hits if category_set & set(hit["matches"])]
    return {"status": "candidate_mentions_found" if hits else "missing", "candidate_files": hits[:50]}


def classify_readiness(
    raw_availability: dict[str, bool],
    static_summary: dict[str, Any],
    array_records: list[dict[str, Any]],
    text_hits: list[dict[str, Any]],
    spatial_summary: dict[str, Any],
    time_summary: dict[str, Any],
    forecast_summary: dict[str, Any],
) -> dict[str, Any]:
    has_raw = raw_availability["flood"] and raw_availability["rainfall"] and raw_availability["static"]
    has_compatible_dem = static_summary["dem_static_elevation_compatible"]
    mask_evidence = any(item["semantic_role"] in {"domain_mask", "boundary_mask"} for item in static_summary["static_map_records"]) or any(
        "mask_domain_boundary" in hit["matches"] for hit in text_hits
    )
    mask_construction_feasible_from_shapes = has_raw and has_compatible_dem and any(
        item.get("shape_compatible_with_representative_flood") for item in static_summary["static_map_records"]
    )
    has_velocity_flux = any(item["semantic_role"] == "velocity_flux_discharge" for item in array_records)
    has_boundary = any(item["semantic_role"] in {"boundary_mask", "source_sink_or_boundary"} for item in array_records)
    has_source_sink = any(item["semantic_role"] == "source_sink_or_boundary" for item in array_records)
    has_dt = time_summary["dt_status"] == "explicit_or_metadata_evidence_found"
    has_dxdy = spatial_summary["dx_dy_status"] == "metadata_evidence_found"
    has_forecast_maps = bool(forecast_summary["representative_forecast_maps"])

    if all([has_velocity_flux, has_boundary, has_source_sink, has_dt, has_dxdy, has_compatible_dem]):
        label = "Level 5 unsupported"
        reason = "Level 5 remains unsupported unless all ingredients are verified as aligned physical arrays and metadata."
    elif has_raw and has_compatible_dem and (mask_evidence or mask_construction_feasible_from_shapes):
        label = "Level 4+ possible"
        reason = (
            "Raw flood/rain/static arrays and shape-compatible DEM/static elevation are available, with mask or "
            "domain/boundary construction feasibility from aligned grid shapes. This supports structured proxy diagnostics, "
            "not strict conservation."
        )
    elif has_forecast_maps:
        label = "Level 4 only"
        reason = (
            "Representative forecast_maps.npz files expose prediction/target depth rasters, but required Level 4+ "
            "or Level 5 ingredients are incomplete or unclear."
        )
    else:
        label = "Level 4 only"
        reason = "The audit did not verify enough physical inputs beyond depth-raster proxy diagnostics."

    missing_level5 = []
    if not has_velocity_flux:
        missing_level5.append("aligned velocity/flux/discharge fields")
    if not has_boundary:
        missing_level5.append("aligned boundary inflow/outflow fields or masks")
    if not has_source_sink:
        missing_level5.append("source/sink, infiltration, or drainage terms as aligned physical fields")
    if not has_dxdy:
        missing_level5.append("explicit dx/dy or spatial resolution")
    if not has_dt:
        missing_level5.append("explicit dt")
    if not has_compatible_dem:
        missing_level5.append("shape-compatible DEM/static elevation")

    return {
        "classification": label,
        "reason": reason,
        "level5_status": "Level 5 unsupported",
        "level5_missing_or_unverified": missing_level5,
    }


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def md_bool(value: Any) -> str:
    return "`true`" if value else "`false`"


def write_markdown(path: Path, report: dict[str, Any]) -> None:
    raw = report["raw_array_availability"]
    forecast = report["forecast_map_evidence"]
    static = report["static_map_dem_evidence"]
    time = report["time_alignment_evidence"]
    spatial = report["grid_space_evidence"]
    boundary = report["boundary_operation_source_sink_evidence"]
    readiness = report["preliminary_readiness_classification"]
    file_inventory = report["file_inventory"]
    ratio_counts = Counter(
        (
            item["flood_steps"],
            item["rainfall_steps"],
            item["possible_timestep_ratio"],
        )
        for item in time["paired_flood_rainfall_ratios"]
    )

    lines = [
        "# Phase 31 Physics Input Inventory",
        "",
        "This diagnostic inventory is read-only except for the files in this Phase 31 output directory. It does not train models, modify architecture, modify losses, modify training configs, or claim strict mass conservation / full SWE/PINN support.",
        "",
        "## 1. Executive Summary",
        "",
        f"- Preliminary readiness classification: `{readiness['classification']}`",
        f"- Level 5 status: `{readiness['level5_status']}`",
        f"- Representative flood spatial shape: `{report['representative_shapes']['representative_flood_spatial_shape']}`",
        f"- Raw flood/rain/static availability: flood={raw['flood']}, rainfall={raw['rainfall']}, static={raw['static']}",
        f"- DEM/static elevation compatibility: {md_bool(static['dem_static_elevation_compatible'])}",
        f"- dt status: `{time['dt_status']}`",
        f"- dx/dy status: `{spatial['dx_dy_status']}`",
        "",
        "## 2. Repository and Dataset Paths Inspected",
        "",
        f"- Repository roots: {', '.join(f'`{item}`' for item in report['audit_scope']['repository_roots_inspected'])}",
        f"- Repository files inspected: {report['audit_scope']['inspected_repo_file_count']}",
        f"- Config path records found: {len(report['config_referenced_paths'])}",
        f"- Dataset roots inspected: {len(report['audit_scope']['dataset_roots_inspected'])}",
        "",
    ]
    for item in report["audit_scope"]["dataset_roots_inspected"]:
        lines.append(f"- `{item}`")
    if report["config_referenced_paths"]:
        lines.extend(["", "Config-referenced paths:"])
        for record in report["config_referenced_paths"][:40]:
            lines.append(
                f"- `{record['config_file']}` `{record['field']}` -> `{record['value']}` "
                f"(exists={record['exists']})"
            )
    lines.extend(
        [
            "",
            "## 3. Raw Flood/Rain/Static Array Availability",
            "",
            f"- `flood.npy` files: {raw['flood_file_count']}",
            f"- `rainfall.npy` files: {raw['rainfall_file_count']}",
            f"- Static array files: {raw['static_file_count']}",
            f"- Other `.npy` / `.npz` / metadata files inventoried: {raw['other_file_count']}",
            f"- Metadata files inventoried: {file_inventory['metadata_file_count']}",
            f"- Counts by extension: `{file_inventory['counts_by_extension']}`",
            "",
            "## 4. Representative Shapes",
            "",
            f"- Representative flood spatial shape: `{report['representative_shapes']['representative_flood_spatial_shape']}`",
            f"- Source: `{report['representative_shapes']['representative_flood_spatial_shape_source']}`",
            f"- Forecast prediction/target compatible: {md_bool(forecast['prediction_target_compatible'])}",
            f"- Representative `forecast_maps.npz` files inspected: {len(forecast['representative_forecast_maps'])}",
            "",
            "| Forecast map | Keys | Prediction/target compatible | Representative spatial shape |",
            "| --- | --- | --- | --- |",
        ]
    )
    for item in forecast["representative_forecast_maps"][:12]:
        lines.append(
            f"| `{item['path']}` | `{', '.join(item['keys'])}` | "
            f"`{item['prediction_target_compatible']}` | `{item['representative_flood_spatial_shape']}` |"
        )
    lines.extend(
        [
            "",
            "## 5. Static-Map / DEM Compatibility",
            "",
            f"- Shape-compatible DEM/static elevation found: {md_bool(static['dem_static_elevation_compatible'])}",
            f"- Compatible DEM/static elevation files: {', '.join(f'`{item}`' for item in static['compatible_dem_static_elevation_files']) or 'None'}",
            "",
            "| Path | Role | Shape | Dtype | Min | Max | Mean | Compatible With Flood |",
            "| --- | --- | --- | --- | ---: | ---: | ---: | --- |",
        ]
    )
    for item in static["static_map_records"][:50]:
        lines.append(
            f"| `{item['path']}` | {item['semantic_role']} | `{item['shape']}` | `{item['dtype']}` | "
            f"{item['min']} | {item['max']} | {item['mean']} | `{item['shape_compatible_with_representative_flood']}` |"
        )
    lines.extend(
        [
            "",
            "## 6. Time-Alignment Evidence",
            "",
            f"- dt status: `{time['dt_status']}`",
            f"- Flood shapes: `{time['flood_shapes']}`",
            f"- Rainfall shapes: `{time['rainfall_shapes']}`",
            f"- Paired flood/rainfall ratio examples: {len(time['paired_flood_rainfall_ratios'])}",
            f"- Observed timestep ratios: `{[{'flood_steps': k[0], 'rainfall_steps': k[1], 'ratio': k[2], 'count': v} for k, v in ratio_counts.most_common(10)]}`",
            f"- Metadata candidate files: {len(time['metadata_candidate_files'])}",
            "",
            "## 7. dx/dy / Spatial Resolution Evidence",
            "",
            f"- dx/dy status: `{spatial['dx_dy_status']}`",
            f"- Candidate files: {len(spatial['candidate_files'])}",
            "",
            "## 8. Boundary / Operation / Source-Sink Evidence",
            "",
        ]
    )
    for key, item in boundary.items():
        lines.append(f"- `{key}`: `{item['status']}` ({len(item['candidate_files'])} candidate files)")
    lines.extend(
        [
            "",
            "## 9. Preliminary Readiness Classification",
            "",
            f"- Classification: `{readiness['classification']}`",
            f"- Reason: {readiness['reason']}",
            f"- Level 5: `{readiness['level5_status']}`",
            "",
            "## 10. Missing Inputs",
            "",
        ]
    )
    for item in readiness["level5_missing_or_unverified"]:
        lines.append(f"- {item}")
    lines.extend(
        [
            "",
            "## 11. Recommended Next Script",
            "",
            "`scripts/inspect_phase31_static_maps.py` should inspect the recovered static maps in more detail, verify channel semantics/location coverage, and prepare evidence for any future domain or boundary mask construction. It should remain diagnostic-only.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    args = parse_args()
    output_dir = resolve_path(str(args.output_dir))

    config_paths = discover_config_paths()
    dataset_roots = dataset_roots_from_config(config_paths)
    repo_scan_roots = repo_roots()

    repo_files = safe_iter_files(repo_scan_roots, suffixes=AUDIT_EXTENSIONS, max_files=None)
    dataset_files = safe_iter_files(dataset_roots, suffixes=AUDIT_EXTENSIONS, max_files=None)

    all_array_files = [path for path in repo_files + dataset_files if path.suffix.lower() in ARRAY_EXTENSIONS]
    npy_records = [
        inspect_npy(path, args.max_array_bytes_for_stats)
        for path in all_array_files
        if path.suffix.lower() == ".npy"
    ][: args.max_array_files]

    total_forecast_files, forecast_files = discover_forecast_maps(args.max_forecast_map_files)
    forecast_records = [inspect_forecast_npz(path, args.max_array_bytes_for_stats) for path in forecast_files]

    text_files = [path for path in repo_files + dataset_files if path.suffix.lower() in METADATA_EXTENSIONS]
    text_hits = [
        hit
        for hit in (inspect_text_file(path, args.max_text_bytes) for path in text_files[: args.max_text_files])
        if hit is not None
    ]

    flood_spatial_from_forecast = next(
        (record["representative_flood_spatial_shape"] for record in forecast_records if record["representative_flood_spatial_shape"]),
        None,
    )
    flood_spatial_from_raw = next(
        (spatial_dims(record["shape"]) for record in npy_records if record["semantic_role"] == "flood_depth" and record["shape"]),
        None,
    )
    representative_flood_spatial = flood_spatial_from_forecast or flood_spatial_from_raw
    representative_source = "forecast_maps.npz" if flood_spatial_from_forecast else "raw flood.npy" if flood_spatial_from_raw else None

    static_summary = summarize_static_compatibility(npy_records, representative_flood_spatial)
    time_summary = summarize_time_alignment(npy_records, text_hits)
    spatial_summary = summarize_spatial_resolution(text_hits)

    raw_availability = {
        "flood": any(record["name"] == "flood.npy" for record in npy_records),
        "rainfall": any(record["name"] == "rainfall.npy" for record in npy_records),
        "static": any(record["semantic_role"] in set(STATIC_ROLE_TOKENS) for record in npy_records),
        "flood_file_count": sum(record["name"] == "flood.npy" for record in npy_records),
        "rainfall_file_count": sum(record["name"] == "rainfall.npy" for record in npy_records),
        "static_file_count": sum(record["semantic_role"] in set(STATIC_ROLE_TOKENS) for record in npy_records),
        "other_file_count": 0,
    }
    inventory_files = [path for path in repo_files + dataset_files if path.suffix.lower() in ARRAY_EXTENSIONS | METADATA_EXTENSIONS]
    raw_availability["other_file_count"] = sum(
        path.name not in {"flood.npy", "rainfall.npy", "absolute_DEM.npy", "impervious.npy", "manhole.npy"}
        for path in inventory_files
    )

    forecast_summary = {
        "total_forecast_map_files_found": total_forecast_files,
        "representative_forecast_maps": forecast_records,
        "prediction_target_compatible": any(record["prediction_target_compatible"] for record in forecast_records),
    }

    boundary_summary = {
        "velocity_flux_discharge": evidence_status(text_hits, ["velocity_flux_discharge"]),
        "boundary_inflow_outflow": evidence_status(text_hits, ["boundary_inflow_outflow"]),
        "pump_gate_operations": evidence_status(text_hits, ["pump_gate_operations"]),
        "drainage_sewer_manhole": evidence_status(text_hits, ["drainage_sewer_manhole"]),
        "infiltration_source_sink": evidence_status(text_hits, ["infiltration_source_sink"]),
        "valid_domain_boundary_mask": evidence_status(text_hits, ["mask_domain_boundary"]),
    }

    readiness = classify_readiness(raw_availability, static_summary, npy_records, text_hits, spatial_summary, time_summary, forecast_summary)

    report = {
        "audit_scope": {
            "repository_root": str(REPO_ROOT),
            "repository_roots_inspected": [display_path(path) for path in repo_scan_roots],
            "dataset_roots_inspected": [str(path) for path in dataset_roots],
            "inspected_repo_file_count": len(repo_files),
            "inspected_dataset_file_count": len(dataset_files),
            "read_only_note": "Script reads repository and dataset files and writes only Phase 31 inventory outputs.",
        },
        "config_referenced_paths": config_paths,
        "raw_array_availability": raw_availability,
        "raw_array_records": npy_records,
        "file_inventory": {
            "inventoried_file_count": len(inventory_files),
            "counts_by_extension": dict(Counter(path.suffix.lower() for path in inventory_files)),
            "metadata_file_count": sum(path.suffix.lower() in METADATA_EXTENSIONS for path in inventory_files),
            "metadata_file_examples": [display_path(path) for path in inventory_files if path.suffix.lower() in METADATA_EXTENSIONS][:100],
            "array_archive_file_count": sum(path.suffix.lower() in ARRAY_EXTENSIONS for path in inventory_files),
        },
        "static_map_dem_evidence": static_summary,
        "forecast_map_evidence": forecast_summary,
        "representative_shapes": {
            "representative_flood_spatial_shape": representative_flood_spatial,
            "representative_flood_spatial_shape_source": representative_source,
        },
        "time_alignment_evidence": time_summary,
        "grid_space_evidence": spatial_summary,
        "boundary_operation_source_sink_evidence": boundary_summary,
        "metadata_text_evidence": text_hits[:200],
        "preliminary_readiness_classification": readiness,
        "guardrail_note": (
            "This inventory does not train, modify model architecture, modify losses, modify training configs, "
            "run seed123/seed202, perform sweeps, claim strict mass conservation, or claim full SWE/PINN support."
        ),
    }

    json_path = output_dir / "physics_input_inventory.json"
    md_path = output_dir / "physics_input_inventory.md"
    write_json(json_path, report)
    write_markdown(md_path, report)

    print("Phase 31 physics input inventory complete.")
    print(f"  inspected repo files count: {len(repo_files)}")
    print(f"  dataset roots found: {len(dataset_roots)}")
    print(
        "  raw flood/rain/static availability: "
        f"flood={raw_availability['flood']} rainfall={raw_availability['rainfall']} static={raw_availability['static']}"
    )
    print(f"  representative flood shape: {representative_flood_spatial}")
    print(f"  DEM/static elevation compatibility: {static_summary['dem_static_elevation_compatible']}")
    print(f"  dt status: {time_summary['dt_status']}")
    print(f"  dx/dy status: {spatial_summary['dx_dy_status']}")
    print(f"  Level 4/4+/5 classification: {readiness['classification']} / {readiness['level5_status']}")
    print(f"  wrote: {display_path(json_path)}")
    print(f"  wrote: {display_path(md_path)}")


if __name__ == "__main__":
    main()
