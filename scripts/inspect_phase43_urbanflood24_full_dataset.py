from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import numpy as np


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATASET_PATH = Path(r"E:\BaiduNetdiskDownload\urbanflood24\urbanflood24")
DEFAULT_OUTPUT_DIR = Path("analysis/phase43_urbanflood24_full_dataset_inspection")
DEFAULT_MAX_SCENARIOS_PER_SPLIT_LOCATION = 3

SPLITS = ("train", "test")
GROUPS = ("flood", "geodata")
LOCATIONS = ("location1", "location2", "location3")

KEYWORDS = (
    "u",
    "v",
    "velocity",
    "qx",
    "qy",
    "flux",
    "discharge",
    "flow",
    "boundary",
    "inflow",
    "outflow",
    "stage",
    "water_level",
    "source",
    "sink",
    "pump",
    "gate",
    "dt",
    "dx",
    "dy",
    "metadata",
    "coordinate",
    "projection",
    "crs",
    "units",
    "timestep",
    "time_step",
)

PHASE42_FIELDS = (
    "water_depth_h",
    "velocity_u_v",
    "flux_qx_qy",
    "dx_dy_grid_spacing",
    "dt_time_step",
    "DEM_or_bed_elevation",
    "rainfall_source",
    "boundary_conditions",
    "source_sink_terms",
    "pump_gate_operations",
    "valid_domain_mask",
    "boundary_mask",
    "coordinate_reference_or_grid_metadata",
    "units_and_scaling",
    "scenario_metadata",
    "time_axis_metadata",
)

LEVEL4_PROXY_FIELDS = {
    "water_depth_h",
    "DEM_or_bed_elevation",
    "rainfall_source",
    "scenario_metadata",
    "time_axis_metadata",
}

DECISION_CANDIDATES = (
    "full_dataset_level5_ready",
    "full_dataset_level4_plus_only",
    "full_dataset_readiness_uncertain_needs_metadata",
    "inspection_incomplete_dataset_path_issue",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Phase 43 no-training, read-only UrbanFlood24 full dataset inspection. "
            "Inventories files and mmap-checks sampled array shapes only; it does not train, "
            "run seeds/sweeps, edit configs/losses/models, or implement SWE/PINN residuals."
        )
    )
    parser.add_argument("--dataset-path", type=Path, default=DEFAULT_DATASET_PATH)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument(
        "--max-scenarios-per-split-location",
        type=int,
        default=DEFAULT_MAX_SCENARIOS_PER_SPLIT_LOCATION,
    )
    return parser.parse_args()


def repo_path(path: Path) -> Path:
    path = path.expanduser()
    return path if path.is_absolute() else REPO_ROOT / path


def bool_text(value: bool) -> str:
    return str(value).lower()


def relative_path(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root)).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


def split_parts(rel_path: str) -> list[str]:
    return [part for part in rel_path.replace("\\", "/").split("/") if part]


def parse_dataset_context(rel_path: str) -> dict[str, str]:
    parts = split_parts(rel_path)
    split = parts[0] if len(parts) >= 1 and parts[0] in SPLITS else ""
    group = parts[1] if len(parts) >= 2 and parts[1] in GROUPS else ""
    location = ""
    for part in parts:
        if part in LOCATIONS:
            location = part
            break
    scenario = ""
    if split and group == "flood" and len(parts) >= 4 and parts[2] in LOCATIONS:
        scenario = parts[3]
    return {
        "split": split,
        "group": group,
        "location": location,
        "scenario": scenario,
    }


def safe_scandir_inventory(dataset_path: Path) -> list[dict[str, Any]]:
    if not dataset_path.exists():
        return []

    rows: list[dict[str, Any]] = []
    stack = [dataset_path]
    while stack:
        current = stack.pop()
        try:
            children = sorted(current.iterdir(), key=lambda item: item.name.lower())
        except OSError:
            continue
        for child in children:
            is_dir = child.is_dir()
            rel = relative_path(child, dataset_path)
            context = parse_dataset_context(rel)
            size = ""
            if child.is_file():
                try:
                    size = child.stat().st_size
                except OSError:
                    size = ""
            rows.append(
                {
                    "relative_path": rel,
                    "split": context["split"],
                    "group": context["group"],
                    "location": context["location"],
                    "scenario": context["scenario"],
                    "filename": child.name,
                    "suffix": child.suffix.lower() if child.is_file() else "",
                    "file_size_bytes": size,
                    "is_dir": bool_text(is_dir),
                }
            )
            if is_dir:
                stack.append(child)
    return sorted(rows, key=lambda row: str(row["relative_path"]).lower())


def keyword_pattern(keyword: str) -> re.Pattern[str]:
    if keyword in {"u", "v"}:
        return re.compile(rf"(?<![A-Za-z0-9]){re.escape(keyword)}(?![A-Za-z0-9])", re.IGNORECASE)
    if keyword in {"dx", "dy", "dt", "qx", "qy"}:
        return re.compile(rf"(?<![A-Za-z0-9]){re.escape(keyword)}(?![A-Za-z0-9])", re.IGNORECASE)
    return re.compile(re.escape(keyword), re.IGNORECASE)


KEYWORD_PATTERNS = {keyword: keyword_pattern(keyword) for keyword in KEYWORDS}


def keyword_hits(inventory_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for item in inventory_rows:
        rel = str(item["relative_path"])
        filename = str(item["filename"])
        searchable = f"{rel} {filename}"
        for keyword, pattern in KEYWORD_PATTERNS.items():
            if not pattern.search(searchable):
                continue
            rows.append(
                {
                    "keyword": keyword,
                    "relative_path": rel,
                    "split": item["split"],
                    "group": item["group"],
                    "location": item["location"],
                    "scenario": item["scenario"],
                    "filename": filename,
                    "suffix": item["suffix"],
                    "is_dir": item["is_dir"],
                    "match_scope": "path_or_name",
                    "notes": (
                        "Single-letter token match; recorded conservatively."
                        if keyword in {"u", "v"}
                        else "Path/name keyword match only; not proof of usable Level 5 data."
                    ),
                }
            )
    return rows


def role_guess(path: Path) -> str:
    name = path.name.lower()
    if name == "flood.npy":
        return "flood_depth"
    if name == "rainfall.npy":
        return "rainfall"
    if name == "absolute_dem.npy":
        return "static_dem"
    if name == "impervious.npy":
        return "static_impervious"
    if name == "manhole.npy":
        return "static_manhole"
    return "unknown"


def static_npy_paths(dataset_path: Path) -> list[Path]:
    paths: list[Path] = []
    for split in SPLITS:
        for location in LOCATIONS:
            root = dataset_path / split / "geodata" / location
            if not root.exists():
                continue
            paths.extend(sorted(root.glob("*.npy"), key=lambda path: path.name.lower()))
    return paths


def sampled_scenario_npy_paths(dataset_path: Path, max_scenarios: int) -> list[Path]:
    paths: list[Path] = []
    for split in SPLITS:
        for location in LOCATIONS:
            root = dataset_path / split / "flood" / location
            if not root.exists():
                continue
            scenarios = [item for item in root.iterdir() if item.is_dir()]
            for scenario_dir in sorted(scenarios, key=lambda path: path.name.lower())[:max_scenarios]:
                paths.extend(sorted(scenario_dir.glob("*.npy"), key=lambda path: path.name.lower()))
    return paths


def inspect_npy_metadata(path: Path, dataset_path: Path) -> dict[str, Any]:
    rel = relative_path(path, dataset_path)
    context = parse_dataset_context(rel)
    record = {
        "relative_path": rel,
        "array_name": path.name,
        "shape": "",
        "dtype": "",
        "split": context["split"],
        "group": context["group"],
        "location": context["location"],
        "scenario": context["scenario"],
        "role_guess": role_guess(path),
        "notes": "",
    }
    try:
        array = np.load(path, mmap_mode="r", allow_pickle=False)
        record["shape"] = str(tuple(int(dim) for dim in array.shape))
        record["dtype"] = str(array.dtype)
    except Exception as exc:  # noqa: BLE001 - inspection should continue.
        record["notes"] = f"mmap metadata inspection failed: {type(exc).__name__}: {exc}"
    return record


def sample_array_inventory(dataset_path: Path, max_scenarios: int) -> list[dict[str, Any]]:
    if not dataset_path.exists():
        return []
    selected: list[Path] = []
    seen: set[Path] = set()
    for path in static_npy_paths(dataset_path) + sampled_scenario_npy_paths(dataset_path, max_scenarios):
        try:
            resolved = path.resolve()
        except OSError:
            resolved = path
        if resolved in seen:
            continue
        seen.add(resolved)
        selected.append(path)
    return [inspect_npy_metadata(path, dataset_path) for path in selected]


def evidence_paths(rows: Iterable[dict[str, Any]], predicate: Any, limit: int = 30) -> list[str]:
    paths: list[str] = []
    seen: set[str] = set()
    for row in rows:
        if not predicate(row):
            continue
        path = str(row.get("relative_path", ""))
        if path and path not in seen:
            seen.add(path)
            paths.append(path)
        if len(paths) >= limit:
            break
    return paths


def any_role(shape_rows: list[dict[str, Any]], roles: set[str]) -> bool:
    return any(row.get("role_guess") in roles and row.get("shape") for row in shape_rows)


def keyword_path_map(keyword_rows: list[dict[str, Any]]) -> dict[str, list[str]]:
    by_keyword: dict[str, list[str]] = defaultdict(list)
    seen: set[tuple[str, str]] = set()
    for row in keyword_rows:
        keyword = str(row["keyword"])
        path = str(row["relative_path"])
        key = (keyword, path)
        if key in seen:
            continue
        seen.add(key)
        by_keyword[keyword].append(path)
    return by_keyword


def build_contract_matrix(
    inventory_rows: list[dict[str, Any]],
    keyword_rows: list[dict[str, Any]],
    shape_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    keyword_paths = keyword_path_map(keyword_rows)
    shape_paths = {str(row["relative_path"]): row for row in shape_rows}
    all_metadata_paths = evidence_paths(
        inventory_rows,
        lambda row: str(row.get("suffix", "")).lower() in {".json", ".csv", ".txt", ".md", ".xml", ".yaml", ".yml"}
        or "metadata" in str(row.get("relative_path", "")).lower(),
    )
    scenario_paths = evidence_paths(inventory_rows, lambda row: bool(row.get("scenario")) and row.get("is_dir") == "true")

    direct_depth = evidence_paths(shape_rows, lambda row: row.get("role_guess") == "flood_depth")
    direct_rain = evidence_paths(shape_rows, lambda row: row.get("role_guess") == "rainfall")
    direct_dem = evidence_paths(shape_rows, lambda row: row.get("role_guess") == "static_dem")
    direct_proxy_static = evidence_paths(
        shape_rows,
        lambda row: row.get("role_guess") in {"static_impervious", "static_manhole"},
    )
    time_shape_paths = evidence_paths(
        shape_rows,
        lambda row: row.get("role_guess") in {"flood_depth", "rainfall"} and bool(row.get("shape")),
    )

    def row(
        field: str,
        status: str,
        evidence_type: str,
        paths: list[str],
        sufficient: bool,
        notes: str,
    ) -> dict[str, Any]:
        return {
            "field": field,
            "status": status,
            "evidence_type": evidence_type,
            "evidence_paths": "; ".join(paths[:40]),
            "level5_required": "true",
            "level4_proxy_support": bool_text(field in LEVEL4_PROXY_FIELDS or bool(paths and not sufficient)),
            "sufficient_for_level5": bool_text(sufficient),
            "notes": notes,
        }

    velocity_paths = sorted(set(keyword_paths.get("u", []) + keyword_paths.get("v", []) + keyword_paths.get("velocity", [])))
    flux_paths = sorted(
        set(
            keyword_paths.get("qx", [])
            + keyword_paths.get("qy", [])
            + keyword_paths.get("flux", [])
            + keyword_paths.get("discharge", [])
            + keyword_paths.get("flow", [])
        )
    )
    dxdy_paths = sorted(set(keyword_paths.get("dx", []) + keyword_paths.get("dy", [])))
    dt_paths = sorted(set(keyword_paths.get("dt", []) + keyword_paths.get("timestep", []) + keyword_paths.get("time_step", [])))
    boundary_paths = sorted(
        set(
            keyword_paths.get("boundary", [])
            + keyword_paths.get("inflow", [])
            + keyword_paths.get("outflow", [])
            + keyword_paths.get("stage", [])
            + keyword_paths.get("water_level", [])
        )
    )
    source_sink_paths = sorted(set(keyword_paths.get("source", []) + keyword_paths.get("sink", [])))
    pump_gate_paths = sorted(set(keyword_paths.get("pump", []) + keyword_paths.get("gate", [])))
    coordinate_paths = sorted(
        set(
            keyword_paths.get("coordinate", [])
            + keyword_paths.get("projection", [])
            + keyword_paths.get("crs", [])
        )
    )
    units_paths = sorted(set(keyword_paths.get("units", [])))

    rows = [
        row(
            "water_depth_h",
            "present" if direct_depth else "absent",
            "direct_array" if direct_depth else "missing",
            direct_depth,
            bool(direct_depth),
            "flood.npy is treated conservatively as water-depth/flood-state evidence only.",
        ),
        row(
            "velocity_u_v",
            "uncertain" if velocity_paths else "absent",
            "filename_keyword" if velocity_paths else "missing",
            velocity_paths,
            False,
            "Only explicit velocity/u/v files or fields would satisfy this field; path keywords alone are not sufficient.",
        ),
        row(
            "flux_qx_qy",
            "uncertain" if flux_paths else "absent",
            "filename_keyword" if flux_paths else "missing",
            flux_paths,
            False,
            "Only explicit qx/qy/flux/discharge arrays or metadata would satisfy this field.",
        ),
        row(
            "dx_dy_grid_spacing",
            "uncertain" if dxdy_paths or all_metadata_paths else "absent",
            "filename_keyword" if dxdy_paths else ("inferred_from_shape_or_known_dataset" if all_metadata_paths else "missing"),
            dxdy_paths or all_metadata_paths,
            False,
            "Shape compatibility is not physical dx/dy. This is not present without explicit local grid-spacing metadata.",
        ),
        row(
            "dt_time_step",
            "uncertain" if dt_paths or all_metadata_paths or time_shape_paths else "absent",
            "filename_keyword" if dt_paths else ("inferred_from_shape_or_known_dataset" if time_shape_paths else "missing"),
            dt_paths or time_shape_paths or all_metadata_paths,
            False,
            "Flood/rainfall lengths indicate sequence axes but do not establish physical dt.",
        ),
        row(
            "DEM_or_bed_elevation",
            "present" if direct_dem else "absent",
            "direct_array" if direct_dem else "missing",
            direct_dem,
            bool(direct_dem),
            "absolute_DEM.npy supports terrain/bed-elevation proxy evidence; vertical units/datum remain a metadata concern.",
        ),
        row(
            "rainfall_source",
            "present" if direct_rain else "absent",
            "direct_array" if direct_rain else "missing",
            direct_rain,
            bool(direct_rain),
            "rainfall.npy supports rainfall forcing evidence, not complete source/sink closure.",
        ),
        row(
            "boundary_conditions",
            "uncertain" if boundary_paths else "absent",
            "filename_keyword" if boundary_paths else "missing",
            boundary_paths,
            False,
            "Boundary conditions require explicit boundary locations/types/values; no inference is made from grid edges.",
        ),
        row(
            "source_sink_terms",
            "uncertain" if source_sink_paths or direct_proxy_static else "absent",
            "filename_keyword" if source_sink_paths else ("inferred_from_shape_or_known_dataset" if direct_proxy_static else "missing"),
            source_sink_paths or direct_proxy_static,
            False,
            "Rainfall, imperviousness, and manhole maps do not establish complete non-rain source/sink terms or closure.",
        ),
        row(
            "pump_gate_operations",
            "uncertain" if pump_gate_paths else "absent",
            "filename_keyword" if pump_gate_paths else "missing",
            pump_gate_paths,
            False,
            "Pump/gate operations require explicit asset states, schedules, flows, or documented absence.",
        ),
        row(
            "valid_domain_mask",
            "absent",
            "missing",
            [],
            False,
            "No explicit valid-domain mask is inferred from flood/static array extents.",
        ),
        row(
            "boundary_mask",
            "uncertain" if boundary_paths else "absent",
            "filename_keyword" if boundary_paths else "missing",
            boundary_paths,
            False,
            "A boundary mask is distinct from boundary-condition values and is not inferred from raster borders.",
        ),
        row(
            "coordinate_reference_or_grid_metadata",
            "uncertain" if coordinate_paths or all_metadata_paths else "absent",
            "filename_keyword" if coordinate_paths else ("inferred_from_shape_or_known_dataset" if all_metadata_paths else "missing"),
            coordinate_paths or all_metadata_paths,
            False,
            "CRS, projection, origin, orientation, and grid metadata must be explicit.",
        ),
        row(
            "units_and_scaling",
            "uncertain" if units_paths or all_metadata_paths else "absent",
            "filename_keyword" if units_paths else ("inferred_from_shape_or_known_dataset" if all_metadata_paths else "missing"),
            units_paths or all_metadata_paths,
            False,
            "Units and scaling are not inferred from file names, shapes, or dtype.",
        ),
        row(
            "scenario_metadata",
            "uncertain" if scenario_paths else "absent",
            "inferred_from_shape_or_known_dataset" if scenario_paths else "missing",
            scenario_paths,
            False,
            "Scenario folder names provide partial event identifiers only, not complete machine-readable scenario metadata.",
        ),
        row(
            "time_axis_metadata",
            "uncertain" if time_shape_paths or dt_paths else "absent",
            "inferred_from_shape_or_known_dataset" if time_shape_paths else ("filename_keyword" if dt_paths else "missing"),
            time_shape_paths or dt_paths,
            False,
            "Flood/rainfall time dimensions are observed, but timestamps, cadence, units, and alignment metadata are incomplete.",
        ),
    ]

    # Ensure matrix row ordering follows the Phase 42 contract exactly.
    by_field = {item["field"]: item for item in rows}
    return [by_field[field] for field in PHASE42_FIELDS]


def scenarios_count_by_split_location(inventory_rows: list[dict[str, Any]]) -> dict[str, int]:
    scenarios: dict[str, set[str]] = defaultdict(set)
    for row in inventory_rows:
        split = str(row.get("split", ""))
        location = str(row.get("location", ""))
        scenario = str(row.get("scenario", ""))
        if split and location and scenario:
            scenarios[f"{split}/{location}"].add(scenario)
    return {key: len(value) for key, value in sorted(scenarios.items())}


def split_locations_found(inventory_rows: list[dict[str, Any]]) -> tuple[list[str], list[str]]:
    splits = sorted({str(row["split"]) for row in inventory_rows if row.get("split")})
    locations = sorted({str(row["location"]) for row in inventory_rows if row.get("location")})
    return splits, locations


def select_decision(dataset_exists: bool, matrix_rows: list[dict[str, Any]]) -> str:
    if not dataset_exists:
        return "inspection_incomplete_dataset_path_issue"
    status = {row["field"]: row["status"] for row in matrix_rows}
    sufficient = {row["field"]: row["sufficient_for_level5"] == "true" for row in matrix_rows}
    if all(sufficient.get(field, False) for field in PHASE42_FIELDS):
        return "full_dataset_level5_ready"
    uncertain_blockers = [
        field
        for field in PHASE42_FIELDS
        if field not in {"water_depth_h", "DEM_or_bed_elevation", "rainfall_source"}
        and status.get(field) == "uncertain"
    ]
    if uncertain_blockers:
        return "full_dataset_readiness_uncertain_needs_metadata"
    return "full_dataset_level4_plus_only"


def readiness_rows(selected_decision: str) -> list[dict[str, Any]]:
    rows = []
    reasons = {
        "full_dataset_level5_ready": "All Phase 42 Level 5 fields are directly present and aligned.",
        "full_dataset_level4_plus_only": "Depth/rainfall/static-map evidence is present, but SWE-critical velocity/flux/boundary/source-sink/grid/time metadata are absent.",
        "full_dataset_readiness_uncertain_needs_metadata": "Some metadata-like or keyword evidence exists, but it is not sufficient to claim aligned Level 5 SWE fields.",
        "inspection_incomplete_dataset_path_issue": "The requested dataset path does not exist or could not be inventoried.",
    }
    for candidate in DECISION_CANDIDATES:
        rows.append(
            {
                "decision_candidate": candidate,
                "selected": bool_text(candidate == selected_decision),
                "reason": reasons[candidate],
            }
        )
    return rows


def level4_plus_supported(matrix_rows: list[dict[str, Any]]) -> bool:
    status = {row["field"]: row["status"] for row in matrix_rows}
    return (
        status.get("water_depth_h") == "present"
        and status.get("rainfall_source") == "present"
        and status.get("DEM_or_bed_elevation") == "present"
    )


def build_summary(
    dataset_path: Path,
    dataset_exists: bool,
    inventory_rows: list[dict[str, Any]],
    shape_rows: list[dict[str, Any]],
    matrix_rows: list[dict[str, Any]],
    selected_decision: str,
) -> dict[str, Any]:
    status_counts = Counter(row["status"] for row in matrix_rows)
    splits, locations = split_locations_found(inventory_rows)
    level5_blockers = [
        row["field"]
        for row in matrix_rows
        if row["level5_required"] == "true" and row["sufficient_for_level5"] != "true"
    ]
    level5_supported = selected_decision == "full_dataset_level5_ready" and not level5_blockers
    proxy_supported = level4_plus_supported(matrix_rows)
    return {
        "phase": 43,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "script": "scripts/inspect_phase43_urbanflood24_full_dataset.py",
        "dataset_path": str(dataset_path),
        "dataset_path_exists": dataset_exists,
        "total_files": sum(1 for row in inventory_rows if row["is_dir"] == "false"),
        "total_dirs": sum(1 for row in inventory_rows if row["is_dir"] == "true"),
        "splits_found": splits,
        "locations_found": locations,
        "scenarios_count_by_split_location": scenarios_count_by_split_location(inventory_rows),
        "sampled_arrays_count": len(shape_rows),
        "required_fields_present_count": status_counts.get("present", 0),
        "required_fields_absent_count": status_counts.get("absent", 0),
        "required_fields_uncertain_count": status_counts.get("uncertain", 0),
        "level5_blocking_fields": level5_blockers,
        "decision_candidates": list(DECISION_CANDIDATES),
        "selected_decision": selected_decision,
        "level5_supported": level5_supported,
        "level4_plus_supported": proxy_supported,
        "training_authorized": False,
        "seed_runs_authorized": False,
        "sweeps_authorized": False,
        "loss_config_model_edits_authorized": False,
        "swe_residual_implementation_authorized": False,
        "pinn_implementation_authorized": False,
        "strict_conservation_claim_authorized": False,
        "full_mass_conservation_claim_authorized": False,
        "hydrodynamic_closure_claim_authorized": False,
        "next_recommended_action": (
            "Use the dataset for Level 4+ proxy diagnostics only and recover/export explicit velocity or flux, "
            "boundary/source-sink, pump/gate, dx/dy, dt, CRS/grid, units, scenario, and time-axis metadata before any Level 5 review."
            if selected_decision != "inspection_incomplete_dataset_path_issue"
            else "Verify the UrbanFlood24 full dataset path and rerun the read-only inspection."
        ),
    }


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    columns = fieldnames or (list(rows[0].keys()) if rows else [])
    if not rows:
        if columns:
            with path.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=columns)
                writer.writeheader()
        else:
            path.write_text("", encoding="utf-8")
        return
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_markdown(path: Path, summary: dict[str, Any], matrix_rows: list[dict[str, Any]]) -> None:
    lines = [
        "# Phase 43 UrbanFlood24 Full Dataset Inspection",
        "",
        "This is a no-training, read-only inspection of the downloaded UrbanFlood24 full dataset against the Phase 42 hydrodynamic export/data contract.",
        "",
        "## Decision",
        "",
        f"- Dataset path: `{summary['dataset_path']}`",
        f"- Dataset path exists: `{bool_text(summary['dataset_path_exists'])}`",
        f"- Selected decision: `{summary['selected_decision']}`",
        f"- Level 5 supported: `{bool_text(summary['level5_supported'])}`",
        f"- Level 4+ supported: `{bool_text(summary['level4_plus_supported'])}`",
        f"- Training authorized: `{bool_text(summary['training_authorized'])}`",
        f"- SWE residual implementation authorized: `{bool_text(summary['swe_residual_implementation_authorized'])}`",
        "",
        "## Dataset Evidence",
        "",
        f"- Total files inventoried: `{summary['total_files']}`",
        f"- Total directories inventoried: `{summary['total_dirs']}`",
        f"- Splits found: `{', '.join(summary['splits_found']) if summary['splits_found'] else 'none'}`",
        f"- Locations found: `{', '.join(summary['locations_found']) if summary['locations_found'] else 'none'}`",
        f"- Sampled arrays inspected with mmap: `{summary['sampled_arrays_count']}`",
        "",
        "UrbanFlood24 full dataset appears to provide higher-resolution flood/rain/static-map data where `flood.npy`, `rainfall.npy`, and geodata arrays are present.",
        "",
        "## Phase 42 Contract Matrix",
        "",
        "| Field | Status | Evidence type | Sufficient for Level 5 | Notes |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in matrix_rows:
        lines.append(
            f"| `{row['field']}` | `{row['status']}` | `{row['evidence_type']}` | "
            f"`{row['sufficient_for_level5']}` | {row['notes']} |"
        )
    lines.extend(
        [
            "",
            "## Level 5 Blocking Fields",
            "",
        ]
    )
    lines.extend([f"- `{field}`" for field in summary["level5_blocking_fields"]] or ["- None"])
    lines.extend(
        [
            "",
            "If no velocity/flux/boundary/source-sink/pump-gate/dx/dy/dt metadata are found, the dataset supports Level 4+ proxy diagnostics but not direct Level 5 SWE residual constraints.",
            "",
            "No SWE/PINN, strict conservation, full mass conservation, hydrodynamic closure, or Level 5 support is claimed.",
            "",
            "## Next Recommended Action",
            "",
            summary["next_recommended_action"],
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    args = parse_args()
    dataset_path = args.dataset_path.expanduser()
    output_dir = repo_path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    dataset_exists = dataset_path.exists() and dataset_path.is_dir()
    inventory_rows = safe_scandir_inventory(dataset_path)
    keyword_rows = keyword_hits(inventory_rows)
    shape_rows = sample_array_inventory(dataset_path, args.max_scenarios_per_split_location)
    matrix_rows = build_contract_matrix(inventory_rows, keyword_rows, shape_rows)
    selected_decision = select_decision(dataset_exists, matrix_rows)
    assessment_rows = readiness_rows(selected_decision)
    summary = build_summary(dataset_path, dataset_exists, inventory_rows, shape_rows, matrix_rows, selected_decision)

    write_csv(
        output_dir / "full_dataset_file_inventory.csv",
        inventory_rows,
        [
            "relative_path",
            "split",
            "group",
            "location",
            "scenario",
            "filename",
            "suffix",
            "file_size_bytes",
            "is_dir",
        ],
    )
    write_csv(
        output_dir / "field_keyword_search_results.csv",
        keyword_rows,
        [
            "keyword",
            "relative_path",
            "split",
            "group",
            "location",
            "scenario",
            "filename",
            "suffix",
            "is_dir",
            "match_scope",
            "notes",
        ],
    )
    write_csv(
        output_dir / "sample_array_shape_inventory.csv",
        shape_rows,
        [
            "relative_path",
            "array_name",
            "shape",
            "dtype",
            "split",
            "group",
            "location",
            "scenario",
            "role_guess",
            "notes",
        ],
    )
    write_csv(output_dir / "phase42_contract_compliance_matrix.csv", matrix_rows)
    write_csv(output_dir / "level5_readiness_assessment.csv", assessment_rows)
    write_json(output_dir / "phase43_urbanflood24_full_dataset_summary.json", summary)
    write_markdown(output_dir / "phase43_urbanflood24_full_dataset_summary.md", summary, matrix_rows)

    print(f"dataset_path_exists={bool_text(summary['dataset_path_exists'])}")
    print(f"total_files={summary['total_files']}")
    print(f"total_dirs={summary['total_dirs']}")
    print(f"sampled_arrays_count={summary['sampled_arrays_count']}")
    print(f"selected_decision={summary['selected_decision']}")
    print(f"level5_supported={bool_text(summary['level5_supported'])}")
    print(f"level4_plus_supported={bool_text(summary['level4_plus_supported'])}")
    print(f"training_authorized={bool_text(summary['training_authorized'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
