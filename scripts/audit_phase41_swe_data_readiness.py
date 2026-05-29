from __future__ import annotations

import argparse
import csv
import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable

import numpy as np


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = Path("analysis/phase41_swe_data_readiness_audit")
DEFAULT_DATASET_ROOT = Path(r"E:\BaiduNetdiskDownload\urbanflood24_lite_release\urbanflood24_lite")

REPO_SCAN_ROOTS = (
    "configs",
    "datasets",
    "scripts",
    "analysis/phase31_physics_input_recovery_readiness",
    "analysis/phase26_strong_physics_constraint_feasibility",
    "runs",
    "docs",
    "utils",
    "trainers",
    "models",
    "README.md",
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

TEXT_EXTENSIONS = {".json", ".csv", ".md", ".txt", ".py", ".yaml", ".yml"}
ARRAY_EXTENSIONS = {".npy", ".npz"}
AUDIT_EXTENSIONS = TEXT_EXTENSIONS | ARRAY_EXTENSIONS

DATASET_PATH_FIELD_NAMES = {
    "data_root",
    "dataset_root",
    "root",
    "data_dir",
    "dataset_dir",
    "input_dir",
    "dataset_config_path",
}

READINESS_LEVELS = (
    "present_aligned",
    "present_unverified_alignment",
    "partial",
    "missing",
    "uncertain_external_export_needed",
)

CATEGORY_DEFINITIONS: dict[str, dict[str, Any]] = {
    "velocity_or_flux_fields": {
        "terms": ("u", "v", "velocity_x", "velocity_y", "vel_x", "vel_y", "qx", "qy", "flux_x", "flux_y", "discharge", "flow"),
        "required_for_swe_residual": True,
        "why_required": "SWE momentum and continuity residuals need aligned velocities, fluxes, discharge, or momentum-like transport fields.",
        "minimum_evidence_needed": "Spatial-temporal arrays aligned to the flood/depth target grid and horizon.",
    },
    "dx_dy_grid_spacing": {
        "terms": ("dx", "dy", "resolution", "grid_spacing", "cell_size", "pixel_size", "spatial_resolution"),
        "required_for_swe_residual": True,
        "why_required": "Finite-difference residuals require physical grid spacing in x and y directions.",
        "minimum_evidence_needed": "Explicit numeric dx and dy, or a documented spatial resolution/cell size for the model grid.",
    },
    "dt_time_step": {
        "terms": ("dt", "timestep", "time_step", "interval", "temporal_resolution", "minutes", "seconds", "hours"),
        "required_for_swe_residual": True,
        "why_required": "Temporal derivative terms require a physical timestep.",
        "minimum_evidence_needed": "Explicit numeric dt or documented temporal cadence aligned to flood/depth sequences.",
    },
    "boundary_conditions": {
        "terms": ("boundary", "inflow", "outflow", "stage", "water_level", "open_boundary", "upstream", "downstream"),
        "required_for_swe_residual": True,
        "why_required": "Residual constraints need boundary treatment and, for open boundaries, flow or stage conditions.",
        "minimum_evidence_needed": "Boundary masks plus boundary condition values or typed open-boundary metadata aligned to the grid/time axis.",
    },
    "source_sink_terms": {
        "terms": ("source", "sink", "rainfall", "infiltration", "drainage", "sewer", "outfall", "lateral", "evaporation"),
        "required_for_swe_residual": True,
        "why_required": "Continuity residuals need source/sink terms such as rainfall, infiltration, drainage, or lateral exchange.",
        "minimum_evidence_needed": "Aligned rainfall and other source/sink arrays or documented zeros/closures for missing terms.",
    },
    "pump_gate_operations": {
        "terms": ("pump", "gate", "sluice", "operation", "control", "discharge", "station"),
        "required_for_swe_residual": False,
        "why_required": "Controlled infrastructure can dominate local fluxes and must be represented if present in the hydrodynamic system.",
        "minimum_evidence_needed": "Pump/gate operation schedules, station discharge, or explicit evidence that none are required.",
    },
    "hydrodynamic_state_variables": {
        "terms": ("water_depth", "depth", "h", "flood", "velocity", "flux", "momentum", "discharge"),
        "required_for_swe_residual": True,
        "why_required": "SWE residuals require state variables; depth alone supports limited proxy diagnostics, not full closure.",
        "minimum_evidence_needed": "Water depth plus velocity/flux/momentum fields aligned to the same grid and time axis.",
    },
    "rainfall_source_alignment": {
        "terms": ("rainfall", "precip", "alignment", "input_steps", "pred_steps", "mass_preserving", "future_rainfall"),
        "required_for_swe_residual": True,
        "why_required": "Rainfall source terms must align with flood/depth sequences to be usable in continuity-style diagnostics.",
        "minimum_evidence_needed": "Rainfall arrays or metadata showing time-axis alignment with flood/depth sequences.",
    },
    "DEM/static_elevation_alignment": {
        "terms": ("absolute_dem", "dem", "elevation", "static", "topography", "terrain", "slope"),
        "required_for_swe_residual": True,
        "why_required": "SWE-oriented diagnostics need aligned elevation/static grids for slope, valid-domain, and terrain-aware terms.",
        "minimum_evidence_needed": "DEM/static elevation arrays shape-compatible with flood/depth targets.",
    },
    "valid_domain_and_boundary_masks": {
        "terms": ("valid_domain", "domain_mask", "boundary_mask", "boundary_ring", "interior_mask", "mask"),
        "required_for_swe_residual": True,
        "why_required": "Residual evaluation must know which cells are valid and how boundary cells are handled.",
        "minimum_evidence_needed": "Valid-domain and boundary masks aligned to the flood/depth grid.",
    },
}

LEVEL5_CRITICAL = (
    "velocity_or_flux_fields",
    "dx_dy_grid_spacing",
    "dt_time_step",
    "boundary_conditions",
    "source_sink_terms",
    "hydrodynamic_state_variables",
)

LEVEL4_PROXY_CATEGORIES = (
    "rainfall_source_alignment",
    "DEM/static_elevation_alignment",
    "valid_domain_and_boundary_masks",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Phase 41 no-training SWE data readiness audit. The script inventories evidence only; "
            "it does not train, run seeds, edit configs/losses/models, or implement SWE/PINN residuals."
        )
    )
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--dataset-root", type=Path, default=None)
    parser.add_argument("--max-text-files", type=int, default=3000)
    parser.add_argument("--max-text-bytes", type=int, default=1_000_000)
    parser.add_argument("--max-dataset-array-files", type=int, default=5000)
    parser.add_argument("--max-repo-array-files", type=int, default=40)
    return parser.parse_args()


def display_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT)).replace("\\", "/")
    except ValueError:
        return str(path)


def resolve_repo_path(path: Path) -> Path:
    path = path.expanduser()
    if path.is_absolute():
        return path
    return (REPO_ROOT / path).resolve()


def safe_float(value: Any) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError, OverflowError):
        return None
    if math.isnan(number) or math.isinf(number):
        return None
    return number


def term_regex(term: str) -> re.Pattern[str]:
    if term in {"u", "v", "h", "dx", "dy", "dt"}:
        return re.compile(rf"(?<![A-Za-z0-9_]){re.escape(term)}(?![A-Za-z0-9_])", re.IGNORECASE)
    return re.compile(re.escape(term), re.IGNORECASE)


TERM_PATTERNS = {
    category: {term: term_regex(term) for term in spec["terms"]}
    for category, spec in CATEGORY_DEFINITIONS.items()
}


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
        if root.is_file():
            children = [root]
        else:
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
    roots: list[Path] = []
    for item in REPO_SCAN_ROOTS:
        path = REPO_ROOT / item
        if path.exists():
            roots.append(path)
    return roots


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
    return any(sep in value for sep in ("\\", "/")) or lower.endswith((".json", ".npy", ".npz", ".csv", ".txt", ".md"))


def discover_config_paths() -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    seen: set[tuple[str, str, str]] = set()
    for config_path in sorted((REPO_ROOT / "configs").glob("*.json")):
        try:
            data = json.loads(config_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        for key_path, value in nested_json_items(data):
            if not key_path or not isinstance(value, str) or not value:
                continue
            if key_path[-1] not in DATASET_PATH_FIELD_NAMES or not looks_like_path(value):
                continue
            resolved = Path(value).expanduser()
            if not resolved.is_absolute():
                resolved = (config_path.parent / resolved).resolve()
                if not resolved.exists():
                    resolved = (REPO_ROOT / value).resolve()
            key = (display_path(config_path), ".".join(key_path), str(resolved))
            if key in seen:
                continue
            seen.add(key)
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
    return records


def dataset_roots_from_config(config_records: list[dict[str, Any]], explicit_root: Path | None) -> list[Path]:
    candidates: list[Path] = []
    if explicit_root is not None:
        candidates.append(explicit_root)
    candidates.append(DEFAULT_DATASET_ROOT)
    for record in config_records:
        field_path = str(record["field"])
        if field_path.startswith("output."):
            continue
        field = str(record["field"]).split(".")[-1]
        if field in {"data_root", "dataset_root", "root", "data_dir", "dataset_dir", "input_dir"}:
            candidates.append(Path(record["resolved_path"]))

    roots: list[Path] = []
    seen: set[Path] = set()
    for candidate in candidates:
        path = candidate.expanduser()
        try:
            resolved = path.resolve()
        except OSError:
            resolved = path
        if resolved in seen:
            continue
        seen.add(resolved)
        if path.exists() and path.is_dir():
            roots.append(path)
    return roots


def match_categories(text: str) -> dict[str, list[str]]:
    matches: dict[str, list[str]] = {}
    for category, patterns in TERM_PATTERNS.items():
        found = [term for term, pattern in patterns.items() if pattern.search(text)]
        if found:
            matches[category] = found
    return matches


def evidence_type_for_path(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".py":
        return "code_or_script"
    if suffix == ".json":
        return "json_or_config"
    if suffix == ".csv":
        return "csv_or_table"
    if suffix in {".md", ".txt"}:
        return "documentation_or_report"
    if suffix in ARRAY_EXTENSIONS:
        return "array_file"
    return "file"


def source_scope(path_text: str) -> str:
    normalized = path_text.replace("\\", "/").lower()
    if normalized.startswith("configs/"):
        return "config"
    if normalized.startswith("datasets/"):
        return "dataset_code"
    if normalized.startswith("scripts/"):
        return "script"
    if normalized.startswith("runs/"):
        return "run_output"
    if normalized.startswith("analysis/"):
        return "prior_analysis"
    if normalized.startswith("docs/") or normalized == "readme.md":
        return "documentation"
    return "repository"


def inspect_text_file(path: Path, max_bytes: int) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    try:
        if path.stat().st_size > max_bytes:
            return [], []
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return [], []

    search_text = f"{display_path(path)}\n{text}"
    category_matches = match_categories(search_text)
    search_rows: list[dict[str, Any]] = []
    for category, terms in category_matches.items():
        for term in terms:
            search_rows.append(
                {
                    "category": category,
                    "search_term": term,
                    "path": display_path(path),
                    "evidence_type": evidence_type_for_path(path),
                    "usable_for_readiness": "no" if path.suffix.lower() in {".md", ".txt"} else "candidate_only",
                    "notes": "Text/path mention; structured fields or arrays are needed for readiness.",
                }
            )

    field_rows: list[dict[str, Any]] = []
    suffix = path.suffix.lower()
    if suffix == ".json":
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            data = None
        if data is not None:
            for key_path, value in nested_json_items(data):
                key = ".".join(key_path)
                value_text = "" if value is None else str(value)
                matches = match_categories(f"{key} {value_text}")
                for category, terms in matches.items():
                    field_rows.append(
                        {
                            "path": display_path(path),
                            "file_type": "json",
                            "source_scope": source_scope(display_path(path)),
                            "field_or_key": key,
                            "shape_or_columns": "",
                            "category_mapping": category,
                            "spatial_alignment_evidence": "",
                            "temporal_alignment_evidence": "",
                            "notes": f"Matched terms: {', '.join(terms[:8])}",
                        }
                    )
    elif suffix == ".csv":
        try:
            with path.open("r", newline="", encoding="utf-8", errors="replace") as handle:
                reader = csv.reader(handle)
                header = next(reader, [])
        except OSError:
            header = []
        for column in header:
            matches = match_categories(column)
            for category, terms in matches.items():
                field_rows.append(
                    {
                        "path": display_path(path),
                        "file_type": "csv",
                        "source_scope": source_scope(display_path(path)),
                        "field_or_key": column,
                        "shape_or_columns": ", ".join(header[:60]),
                        "category_mapping": category,
                        "spatial_alignment_evidence": "",
                        "temporal_alignment_evidence": "",
                        "notes": f"Matched terms: {', '.join(terms[:8])}",
                    }
                )
    return search_rows, field_rows


def inspect_array_file(path: Path, source: str) -> dict[str, Any]:
    record: dict[str, Any] = {
        "path": display_path(path) if source == "repository" else str(path),
        "file_type": path.suffix.lower().lstrip("."),
        "field_or_key": path.name,
        "shape_or_columns": "",
        "category_mapping": "",
        "spatial_alignment_evidence": "",
        "temporal_alignment_evidence": "",
        "notes": "",
        "source": source,
        "source_scope": source,
    }
    categories = match_categories(path.name)
    category_names = sorted(categories)
    record["category_mapping"] = "; ".join(category_names)
    try:
        if path.suffix.lower() == ".npy":
            arr = np.load(path, mmap_mode="r", allow_pickle=False)
            shape = tuple(int(dim) for dim in arr.shape)
            record["shape_or_columns"] = str(list(shape))
            record["spatial_alignment_evidence"] = "last_two_dims_128x128" if len(shape) >= 2 and shape[-2:] == (128, 128) else ""
            record["temporal_alignment_evidence"] = f"time_steps={shape[0]}" if len(shape) >= 3 else ""
            record["notes"] = f"dtype={arr.dtype}"
        elif path.suffix.lower() == ".npz":
            with np.load(path, allow_pickle=False) as arrays:
                keys = list(arrays.files)
                key_rows = []
                for key in keys:
                    arr = arrays[key]
                    key_rows.append(f"{key}:{list(arr.shape)}")
                    key_matches = match_categories(key)
                    for category in key_matches:
                        if category not in category_names:
                            category_names.append(category)
                record["field_or_key"] = ", ".join(keys)
                record["shape_or_columns"] = "; ".join(key_rows[:30])
                record["category_mapping"] = "; ".join(sorted(category_names))
                record["spatial_alignment_evidence"] = "contains_128x128_array" if any(arrays[key].shape[-2:] == (128, 128) for key in keys if arrays[key].ndim >= 2) else ""
                record["temporal_alignment_evidence"] = "npz_keys_inspected"
                record["notes"] = "metadata-only npz inspection"
    except Exception as exc:  # noqa: BLE001 - audit should continue.
        record["notes"] = f"array inspection failed: {type(exc).__name__}: {exc}"
    return record


def summarize_repository_search(search_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in search_rows:
        grouped[(row["category"], row["search_term"])].append(row)

    summary_rows: list[dict[str, Any]] = []
    for category, spec in CATEGORY_DEFINITIONS.items():
        for term in spec["terms"]:
            rows = grouped.get((category, term), [])
            paths = sorted({row["path"] for row in rows})
            evidence_types = sorted({row["evidence_type"] for row in rows})
            usable_values = sorted({row["usable_for_readiness"] for row in rows})
            summary_rows.append(
                {
                    "category": category,
                    "search_term": term,
                    "matches_found": len(rows),
                    "candidate_paths": "; ".join(paths[:30]),
                    "evidence_type": "; ".join(evidence_types),
                    "usable_for_readiness": "; ".join(usable_values) if usable_values else "no",
                    "notes": "Documentation mentions are treated as context only, not aligned data evidence.",
                }
            )
    return summary_rows


def discover_dataset_files(dataset_roots: list[Path], max_array_files: int) -> list[Path]:
    files = safe_iter_files(dataset_roots, suffixes=AUDIT_EXTENSIONS, max_files=None)
    array_count = 0
    selected: list[Path] = []
    for path in files:
        if path.suffix.lower() in ARRAY_EXTENSIONS:
            array_count += 1
            if array_count > max_array_files:
                continue
        selected.append(path)
    return selected


def direct_data_evidence(row: dict[str, Any], category: str) -> bool:
    if category not in str(row.get("category_mapping", "")):
        return False
    if row.get("source") == "dataset":
        return True
    scope = row.get("source_scope")
    if scope in {"config", "dataset_code"}:
        key_matches = match_categories(str(row.get("field_or_key", "")))
        return category in key_matches and row.get("file_type") in {"json", "csv", "npy", "npz"}
    return False


def infer_dataset_alignment(dataset_rows: list[dict[str, Any]]) -> dict[str, Any]:
    flood_rows = [row for row in dataset_rows if Path(str(row["path"])).name == "flood.npy"]
    rainfall_rows = [row for row in dataset_rows if Path(str(row["path"])).name == "rainfall.npy"]
    dem_rows = [row for row in dataset_rows if Path(str(row["path"])).name.lower() == "absolute_dem.npy"]
    static_rows = [
        row
        for row in dataset_rows
        if Path(str(row["path"])).name.lower() in {"absolute_dem.npy", "impervious.npy", "manhole.npy"}
    ]

    flood_shapes = Counter(row["shape_or_columns"] for row in flood_rows if row["shape_or_columns"])
    rainfall_shapes = Counter(row["shape_or_columns"] for row in rainfall_rows if row["shape_or_columns"])
    static_128 = bool(static_rows) and all(row["spatial_alignment_evidence"] == "last_two_dims_128x128" for row in static_rows)
    flood_128 = bool(flood_rows) and all("128, 128" in row["shape_or_columns"] for row in flood_rows)
    dem_128 = bool(dem_rows) and all(row["spatial_alignment_evidence"] == "last_two_dims_128x128" for row in dem_rows)
    rainfall_present = bool(rainfall_rows)
    flood_present = bool(flood_rows)

    paired_events = 0
    flood_by_parent = {str(Path(str(row["path"])).parent): row for row in flood_rows}
    rainfall_by_parent = {str(Path(str(row["path"])).parent): row for row in rainfall_rows}
    ratio_examples = []
    for parent, flood_row in flood_by_parent.items():
        rain_row = rainfall_by_parent.get(parent)
        if not rain_row:
            continue
        paired_events += 1
        ratio_examples.append(
            {
                "event_dir": parent,
                "flood_shape": flood_row["shape_or_columns"],
                "rainfall_shape": rain_row["shape_or_columns"],
            }
        )

    return {
        "flood_present": flood_present,
        "rainfall_present": rainfall_present,
        "static_present": bool(static_rows),
        "flood_grid_128x128": flood_128,
        "static_grid_128x128": static_128,
        "dem_grid_128x128": dem_128,
        "paired_flood_rainfall_events": paired_events,
        "flood_shapes": dict(flood_shapes),
        "rainfall_shapes": dict(rainfall_shapes),
        "paired_event_examples": ratio_examples[:20],
    }


def load_json_if_exists(path: Path) -> dict[str, Any] | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def classify_categories(
    dataset_rows: list[dict[str, Any]],
    field_rows: list[dict[str, Any]],
    search_rows: list[dict[str, Any]],
    dataset_alignment: dict[str, Any],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    by_category_paths: dict[str, set[str]] = defaultdict(set)
    by_category_notes: dict[str, list[str]] = defaultdict(list)
    for row in dataset_rows + field_rows:
        for category in str(row.get("category_mapping", "")).split(";"):
            category = category.strip()
            if category in CATEGORY_DEFINITIONS:
                by_category_paths[category].add(str(row["path"]))
                note = str(row.get("notes", ""))
                if note:
                    by_category_notes[category].append(note)

    for row in search_rows:
        by_category_paths[row["category"]].add(row["path"])

    phase31_mask = load_json_if_exists(REPO_ROOT / "analysis/phase31_physics_input_recovery_readiness/domain_boundary_mask_summary.json")
    phase31_static = load_json_if_exists(REPO_ROOT / "analysis/phase31_physics_input_recovery_readiness/static_map_inspection_summary.json")

    category_rows: list[dict[str, Any]] = []
    statuses: dict[str, str] = {}

    for category, spec in CATEGORY_DEFINITIONS.items():
        paths = sorted(by_category_paths.get(category, set()))
        notes = []
        alignment_status = "not_verified"
        readiness_level = "missing"
        supports_level4_proxy_only = False
        supports_level5_swe_residual = False

        if category == "rainfall_source_alignment":
            if dataset_alignment["rainfall_present"] and dataset_alignment["flood_present"] and dataset_alignment["paired_flood_rainfall_events"] > 0:
                readiness_level = "present_aligned"
                alignment_status = "paired rainfall.npy and flood.npy event directories; adapter alignment mode is configured"
                supports_level4_proxy_only = True
                notes.append("Rainfall and flood/depth sequences are paired by event; this supports rainfall-source proxy diagnostics.")
            elif dataset_alignment["rainfall_present"]:
                readiness_level = "present_unverified_alignment"
                supports_level4_proxy_only = True
            else:
                readiness_level = "missing"
        elif category == "DEM/static_elevation_alignment":
            if dataset_alignment["dem_grid_128x128"] or (phase31_static and phase31_static.get("all_static_maps_shape_128x128")):
                readiness_level = "present_aligned"
                alignment_status = "absolute_DEM/static maps are shape-compatible with 128x128 flood grid"
                supports_level4_proxy_only = True
                notes.append("DEM/static elevation supports terrain-aware proxy diagnostics.")
            elif dataset_alignment["static_present"]:
                readiness_level = "present_unverified_alignment"
                supports_level4_proxy_only = True
            else:
                readiness_level = "missing"
        elif category == "valid_domain_and_boundary_masks":
            if phase31_mask and phase31_mask.get("level4_plus_domain_boundary_readiness") == "supported":
                readiness_level = "present_aligned"
                alignment_status = "Phase 31 valid-domain and boundary-ring masks are 128x128 and train/test consistent"
                supports_level4_proxy_only = True
                notes.append("Phase 31 masks support valid-domain and boundary-aware proxy diagnostics.")
            elif paths:
                readiness_level = "partial"
                supports_level4_proxy_only = True
            else:
                readiness_level = "missing"
        elif category == "source_sink_terms":
            has_rainfall = dataset_alignment["rainfall_present"]
            has_other_source_sink = any(
                any(term in str(row.get("field_or_key", "")).lower() for term in ("infiltration", "sewer", "outfall", "lateral", "evaporation", "sink", "source"))
                for row in dataset_rows + field_rows
                if direct_data_evidence(row, category)
            )
            if has_rainfall and has_other_source_sink:
                readiness_level = "present_unverified_alignment"
                supports_level4_proxy_only = True
            elif has_rainfall:
                readiness_level = "partial"
                supports_level4_proxy_only = True
                notes.append("Rainfall source exists, but infiltration/drainage/sewer/outfall/lateral/evaporation terms are missing or only proxies.")
            elif paths:
                readiness_level = "uncertain_external_export_needed"
            else:
                readiness_level = "missing"
        elif category == "hydrodynamic_state_variables":
            has_depth = dataset_alignment["flood_present"] or any("flood" in str(path).lower() or "depth" in str(path).lower() for path in paths)
            has_transport = any(
                any(term in str(row.get("field_or_key", "")).lower() for term in ("velocity", "flux", "momentum", "discharge", "qx", "qy"))
                for row in dataset_rows + field_rows
                if direct_data_evidence(row, category)
            )
            if has_depth and has_transport:
                readiness_level = "present_unverified_alignment"
                notes.append("Depth plus transport-like state mentions found, but alignment needs verification.")
            elif has_depth:
                readiness_level = "partial"
                supports_level4_proxy_only = True
                notes.append("Water-depth/flood arrays are available; velocity/flux/momentum state variables are missing.")
            elif paths:
                readiness_level = "uncertain_external_export_needed"
            else:
                readiness_level = "missing"
        elif category == "dx_dy_grid_spacing":
            explicit_numeric = any(
                re.search(r"\b(dx|dy|grid_spacing|cell_size|pixel_size|spatial_resolution|resolution)\b[^0-9\r\n]{0,30}[0-9]+(\.[0-9]+)?", str(row), re.IGNORECASE)
                for row in field_rows
                if row.get("category_mapping") == category and row.get("source_scope") in {"config", "dataset_code"}
            )
            if explicit_numeric:
                readiness_level = "present_unverified_alignment"
                notes.append("Numeric grid-spacing metadata was found but physical unit and full alignment require review.")
            elif paths:
                readiness_level = "uncertain_external_export_needed"
                notes.append("Grid-size terms are mentioned, but explicit dx/dy physical values were not verified.")
            else:
                readiness_level = "missing"
        elif category == "dt_time_step":
            explicit_numeric = any(
                re.search(r"\b(dt|timestep|time_step|interval|temporal_resolution|minutes|seconds|hours)\b[^0-9\r\n]{0,30}[0-9]+(\.[0-9]+)?", str(row), re.IGNORECASE)
                for row in field_rows
                if row.get("category_mapping") == category and row.get("source_scope") in {"config", "dataset_code"}
            )
            if explicit_numeric:
                readiness_level = "present_unverified_alignment"
                notes.append("Numeric timestep-like metadata was found, but physical dt alignment requires review.")
            elif paths:
                readiness_level = "uncertain_external_export_needed"
                notes.append("Time-step terms are mentioned, but explicit physical dt was not verified.")
            else:
                readiness_level = "missing"
        elif category in {"velocity_or_flux_fields", "boundary_conditions", "pump_gate_operations"}:
            direct_array_or_field = any(
                direct_data_evidence(row, category) and row.get("source") == "dataset"
                for row in dataset_rows + field_rows
            )
            if direct_array_or_field:
                readiness_level = "present_unverified_alignment"
                notes.append("Direct candidate field/file evidence exists, but SWE residual alignment was not proven.")
            elif paths:
                readiness_level = "uncertain_external_export_needed"
                notes.append("Only mentions or proxy/context evidence were found; current export does not expose aligned data.")
            else:
                readiness_level = "missing"

        if readiness_level == "missing" and paths:
            readiness_level = "uncertain_external_export_needed"

        if category in LEVEL5_CRITICAL and readiness_level == "present_aligned":
            supports_level5_swe_residual = True
        elif category not in LEVEL5_CRITICAL and readiness_level == "present_aligned":
            supports_level5_swe_residual = False

        statuses[category] = readiness_level
        category_rows.append(
            {
                "category": category,
                "required_for_swe_residual": spec["required_for_swe_residual"],
                "why_required": spec["why_required"],
                "minimum_evidence_needed": spec["minimum_evidence_needed"],
                "present_status": readiness_level,
                "alignment_status": alignment_status,
                "candidate_paths": "; ".join(paths[:40]),
                "notes": " ".join(notes + by_category_notes.get(category, [])[:3]),
                "supports_level4_proxy_only": supports_level4_proxy_only,
                "supports_level5_swe_residual": supports_level5_swe_residual,
            }
        )

    meta = {
        "phase31_mask_summary_available": bool(phase31_mask),
        "phase31_static_summary_available": bool(phase31_static),
    }
    return category_rows, {"statuses": statuses, **meta}


def build_readiness_matrix(category_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in category_rows:
        category = row["category"]
        readiness_level = row["present_status"]
        critical = category in LEVEL5_CRITICAL
        missing_or_uncertain = "" if readiness_level in {"present_aligned", "present_unverified_alignment", "partial"} else row["minimum_evidence_needed"]
        if readiness_level == "partial" and critical:
            missing_or_uncertain = row["minimum_evidence_needed"]
        supports_proxy = bool(row["supports_level4_proxy_only"])
        supports_level5 = bool(row["supports_level5_swe_residual"])
        if supports_level5:
            interpretation = "Aligned evidence found for a critical SWE input."
        elif supports_proxy:
            interpretation = "Supports Level 4+ proxy diagnostics only; not enough for Level 5 SWE residual closure."
        elif readiness_level == "uncertain_external_export_needed":
            interpretation = "Repository mentions exist, but current local export lacks verified aligned data."
        else:
            interpretation = "Missing or unverified for SWE residual use."
        rows.append(
            {
                "category": category,
                "readiness_level": readiness_level,
                "critical_for_level5": critical,
                "present_evidence": row["candidate_paths"],
                "missing_or_uncertain_evidence": missing_or_uncertain,
                "supports_level4_proxy_only": supports_proxy,
                "supports_level5_swe_residual": supports_level5,
                "interpretation": interpretation,
            }
        )
    return rows


def decide_overall(category_rows: list[dict[str, Any]], dataset_roots: list[Path]) -> dict[str, Any]:
    status = {row["category"]: row["present_status"] for row in category_rows}
    supported = [row["category"] for row in category_rows if row["present_status"] in {"present_aligned", "present_unverified_alignment", "partial"}]
    missing = [row["category"] for row in category_rows if row["present_status"] == "missing"]
    uncertain = [row["category"] for row in category_rows if row["present_status"] == "uncertain_external_export_needed"]
    level5_ready = all(status.get(category) == "present_aligned" for category in LEVEL5_CRITICAL)
    proxy_ready = all(status.get(category) == "present_aligned" for category in LEVEL4_PROXY_CATEGORIES)

    if level5_ready and all(status.get(category) == "present_aligned" for category in CATEGORY_DEFINITIONS):
        decision = "swe_data_ready_for_residual_prototype"
        next_action = "Document exact units and alignment assumptions before any separate SWE residual prototype planning."
    elif uncertain and dataset_roots:
        decision = "readiness_uncertain_requires_external_data_export"
        next_action = "Recover or export hydrodynamic model fields: velocity/flux, dx/dy, dt, boundary conditions, and complete source/sink terms."
    elif supported and (status.get("velocity_or_flux_fields") != "present_aligned" or status.get("boundary_conditions") != "present_aligned"):
        decision = "partial_readiness_needs_data_recovery" if proxy_ready else "not_ready_for_swe_constraints"
        next_action = "Use existing data for Level 4+ proxy diagnostics only, and request external hydrodynamic exports before Level 5 planning."
    else:
        decision = "not_ready_for_swe_constraints"
        next_action = "Do not implement SWE/PINN residuals; first recover the missing hydrodynamic and numerical metadata inputs."

    blockers = [
        category
        for category in LEVEL5_CRITICAL
        if status.get(category) != "present_aligned"
    ]
    return {
        "readiness_decision": decision,
        "level5_supported": bool(decision == "swe_data_ready_for_residual_prototype"),
        "categories_evaluated": len(CATEGORY_DEFINITIONS),
        "categories_supported": supported,
        "categories_missing": missing,
        "categories_uncertain": uncertain,
        "level5_blocking_categories": blockers,
        "level4_proxy_supported": bool(proxy_ready),
        "external_hydrodynamic_model_export_needed": bool(blockers),
        "next_recommended_action": next_action,
    }


def build_missing_inputs(matrix_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in matrix_rows:
        if row["supports_level5_swe_residual"]:
            continue
        category = row["category"]
        if category in LEVEL5_CRITICAL or row["readiness_level"] in {"missing", "uncertain_external_export_needed"}:
            rows.append(
                {
                    "category": category,
                    "missing_input": row["missing_or_uncertain_evidence"] or CATEGORY_DEFINITIONS[category]["minimum_evidence_needed"],
                    "blocking_level": "blocks_level5" if category in LEVEL5_CRITICAL else "limits_level5_context",
                    "needed_for": CATEGORY_DEFINITIONS[category]["why_required"],
                    "recommended_recovery_action": recovery_action(category),
                    "notes": row["interpretation"],
                }
            )
    return rows


def recovery_action(category: str) -> str:
    actions = {
        "velocity_or_flux_fields": "Export aligned u/v, qx/qy, discharge, or flux fields from the hydrodynamic model.",
        "dx_dy_grid_spacing": "Recover physical cell size or dx/dy metadata for the 128x128 grid.",
        "dt_time_step": "Recover physical timestep/cadence for flood and rainfall sequences.",
        "boundary_conditions": "Export boundary masks plus inflow/outflow/stage/open-boundary values.",
        "source_sink_terms": "Export rainfall plus infiltration, drainage/sewer/outfall, lateral, and evaporation terms or explicit closures.",
        "pump_gate_operations": "Export pump/gate/sluice station operations or document that no controlled infrastructure is represented.",
        "hydrodynamic_state_variables": "Recover complete hydrodynamic state variables beyond water depth.",
        "rainfall_source_alignment": "Verify rainfall-to-flood alignment and physical units.",
        "DEM/static_elevation_alignment": "Verify DEM/static map units and grid alignment.",
        "valid_domain_and_boundary_masks": "Persist and version valid-domain/boundary masks aligned to model targets.",
    }
    return actions[category]


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fields = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_markdown(path: Path, summary: dict[str, Any], matrix_rows: list[dict[str, Any]]) -> None:
    supported = summary["categories_supported"]
    missing = summary["categories_missing"]
    uncertain = summary["categories_uncertain"]
    blockers = summary["level5_blocking_categories"]

    lines = [
        "# Phase 41 SWE Data Readiness Audit",
        "",
        "This is a no-training data-readiness audit. It does not modify losses, configs, model architecture, or training behavior; it does not run seeds or implement SWE/PINN residuals.",
        "",
        "## Final Readiness Decision",
        "",
        f"- Final readiness decision: `{summary['readiness_decision']}`",
        f"- Level 5 SWE residual support: `{summary['level5_supported']}`",
        f"- External hydrodynamic model export needed: `{summary['external_hydrodynamic_model_export_needed']}`",
        f"- Next recommended action: {summary['next_recommended_action']}",
        "",
        "## Supported Data Categories",
        "",
    ]
    lines.extend([f"- `{category}`" for category in supported] or ["- None"])
    lines.extend(["", "## Missing Or Uncertain Data Categories", ""])
    for category in missing:
        lines.append(f"- `{category}`: missing")
    for category in uncertain:
        lines.append(f"- `{category}`: uncertain, likely requires external export or metadata recovery")
    if not missing and not uncertain:
        lines.append("- None")

    lines.extend(
        [
            "",
            "## What Supports Level 4+ Proxy Diagnostics",
            "",
            "- Flood/depth target arrays and evaluation prediction/target rasters support depth-based proxy diagnostics.",
            "- Rainfall fields are paired with flood/depth event sequences and are handled by the existing adapter alignment modes.",
            "- `absolute_DEM`, impervious, and manhole static maps are available as static proxy inputs.",
            "- Phase 31 valid-domain and boundary-ring masks support domain-aware and boundary-aware proxy diagnostics.",
            "",
            "## What Blocks Level 5 SWE/PINN Residual Constraints",
            "",
        ]
    )
    for category in blockers:
        lines.append(f"- `{category}`")
    if not blockers:
        lines.append("- No blocking category was detected by this audit.")
    lines.extend(
        [
            "",
            "Missing velocity/flux, physical dx/dy, physical dt, boundary conditions, complete source/sink terms, pump/gate operations, or complete hydrodynamic state variables blocks Level 5 SWE residual claims. Current evidence must not be described as strict conservation, full mass conservation, hydrodynamic closure, SWE/PINN support, or Level 5 support.",
            "",
            "## Readiness Matrix",
            "",
            "| Category | Readiness | Critical for Level 5 | Level 4 Proxy Only | Level 5 Residual |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    for row in matrix_rows:
        lines.append(
            f"| `{row['category']}` | `{row['readiness_level']}` | `{row['critical_for_level5']}` | "
            f"`{row['supports_level4_proxy_only']}` | `{row['supports_level5_swe_residual']}` |"
        )
    lines.extend(
        [
            "",
            "## External Export Need",
            "",
            "External hydrodynamic model export is needed before any Level 5 residual prototype planning unless the missing categories are recovered locally with explicit grid/time alignment and physical units.",
            "",
            "## Guardrail Conclusion",
            "",
            "Phase 41 supports continued no-training data recovery and Level 4+ proxy diagnostics. It does not authorize training and does not justify SWE/PINN residual implementation.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    args = parse_args()
    output_dir = resolve_repo_path(args.output_dir)

    config_records = discover_config_paths()
    dataset_roots = dataset_roots_from_config(config_records, args.dataset_root)
    repo_files = safe_iter_files(repo_roots(), suffixes=AUDIT_EXTENSIONS, max_files=None)
    dataset_files = discover_dataset_files(dataset_roots, args.max_dataset_array_files)

    search_rows: list[dict[str, Any]] = []
    field_rows: list[dict[str, Any]] = []
    for path in repo_files[: args.max_text_files]:
        if path.suffix.lower() in TEXT_EXTENSIONS:
            search, fields = inspect_text_file(path, args.max_text_bytes)
            search_rows.extend(search)
            field_rows.extend(fields)

    repo_array_files = [path for path in repo_files if path.suffix.lower() in ARRAY_EXTENSIONS][: args.max_repo_array_files]
    repo_array_rows = [inspect_array_file(path, "repository") for path in repo_array_files]
    dataset_array_files = [path for path in dataset_files if path.suffix.lower() in ARRAY_EXTENSIONS]
    dataset_rows = [inspect_array_file(path, "dataset") for path in dataset_array_files]

    for row in repo_array_rows:
        for category in str(row.get("category_mapping", "")).split(";"):
            category = category.strip()
            if category in CATEGORY_DEFINITIONS:
                search_rows.append(
                    {
                        "category": category,
                        "search_term": row["field_or_key"],
                        "path": row["path"],
                        "evidence_type": "array_file",
                        "usable_for_readiness": "candidate_only",
                        "notes": "Array metadata inspected.",
                    }
                )

    repository_summary = summarize_repository_search(search_rows)
    dataset_alignment = infer_dataset_alignment(dataset_rows)
    inventory_rows, classification_meta = classify_categories(dataset_rows, field_rows + repo_array_rows, search_rows, dataset_alignment)
    matrix_rows = build_readiness_matrix(inventory_rows)
    overall = decide_overall(inventory_rows, dataset_roots)
    missing_rows = build_missing_inputs(matrix_rows)

    dataset_field_inventory = dataset_rows + field_rows + repo_array_rows
    summary = {
        "guardrail_note": (
            "No training, seed runs, sweeps, loss/config/model edits, SWE residual implementation, "
            "PINN implementation, strict conservation claim, full mass conservation claim, hydrodynamic closure claim, "
            "or Level 5 support claim was made."
        ),
        "audit_scope": {
            "repository_root": str(REPO_ROOT),
            "repository_roots_inspected": [display_path(path) for path in repo_roots()],
            "repository_files_inspected": len(repo_files),
            "dataset_roots_inspected": [str(path) for path in dataset_roots],
            "dataset_files_inspected": len(dataset_files),
            "config_referenced_paths": config_records,
        },
        "dataset_alignment_evidence": dataset_alignment,
        "category_status": classification_meta["statuses"],
        "phase31_mask_summary_available": classification_meta["phase31_mask_summary_available"],
        "phase31_static_summary_available": classification_meta["phase31_static_summary_available"],
        **overall,
    }

    write_csv(output_dir / "swe_required_data_inventory.csv", inventory_rows)
    write_csv(output_dir / "repository_search_summary.csv", repository_summary)
    write_csv(output_dir / "dataset_field_inventory.csv", dataset_field_inventory)
    write_csv(output_dir / "swe_readiness_matrix.csv", matrix_rows)
    write_csv(output_dir / "missing_swe_inputs.csv", missing_rows)
    write_json(output_dir / "phase41_swe_data_readiness_summary.json", summary)
    write_markdown(output_dir / "phase41_swe_data_readiness_summary.md", summary, matrix_rows)

    print("Phase 41 SWE data readiness audit complete.")
    print(f"categories_evaluated: {overall['categories_evaluated']}")
    print(f"categories_supported: {len(overall['categories_supported'])} ({', '.join(overall['categories_supported'])})")
    print(f"categories_missing: {len(overall['categories_missing'])} ({', '.join(overall['categories_missing'])})")
    print(f"readiness_decision: {overall['readiness_decision']}")
    print(f"level5_supported: {overall['level5_supported']}")
    print(f"next_recommended_action: {overall['next_recommended_action']}")


if __name__ == "__main__":
    main()
