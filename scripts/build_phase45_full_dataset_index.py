from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATASET_ROOT = Path(r"E:\BaiduNetdiskDownload\urbanflood24\urbanflood24")
OUTPUT_DIR = REPO_ROOT / "analysis" / "phase45_full_dataset_indexing"

SPLITS = ("train", "test")
STATIC_FILES = {
    "dem": "absolute_DEM.npy",
    "impervious": "impervious.npy",
    "manhole": "manhole.npy",
}

SCENARIO_COLUMNS = (
    "split",
    "location",
    "scenario",
    "scenario_type",
    "flood_path",
    "rainfall_path",
    "flood_shape",
    "flood_dtype",
    "rainfall_shape",
    "rainfall_dtype",
    "rainfall_length",
    "static_dem_path",
    "static_impervious_path",
    "static_manhole_path",
    "flood_file_size_bytes",
    "rainfall_file_size_bytes",
    "notes",
)

STATIC_COLUMNS = (
    "split",
    "location",
    "absolute_dem_path",
    "impervious_path",
    "manhole_path",
    "dem_shape",
    "impervious_shape",
    "manhole_shape",
    "dem_dtype",
    "impervious_dtype",
    "manhole_dtype",
    "dem_file_size_bytes",
    "impervious_file_size_bytes",
    "manhole_file_size_bytes",
    "static_coverage_status",
)

DESIGN_SCENARIO_RE = re.compile(
    r"^r\d+y_p\d+(?:\.\d+)?_d\d+(?:\.\d+)?h$", re.IGNORECASE
)
MEASURED_SCENARIO_RE = re.compile(r"^G\d+_intensity_\d+(?:\.\d+)?$", re.IGNORECASE)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Phase 45 no-training UrbanFlood24 full dataset index builder. "
            "Indexes paths and mmap-inspected shapes/dtypes only; does not train, "
            "run seeds/sweeps, edit configs/losses/models, or implement SWE/PINN components."
        )
    )
    parser.add_argument("--dataset-root", type=Path, default=DEFAULT_DATASET_ROOT)
    return parser.parse_args()


def bool_text(value: bool) -> str:
    return str(value).lower()


def path_text(path: Path) -> str:
    return str(path.resolve()).replace("\\", "/")


def shape_text(shape: tuple[int, ...] | None) -> str:
    return "" if shape is None else str(tuple(int(dim) for dim in shape))


def write_csv(path: Path, rows: list[dict[str, Any]], columns: tuple[str, ...]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        for row in rows:
            writer.writerow({column: row.get(column, "") for column in columns})


def inspect_npy(path: Path) -> dict[str, Any]:
    result: dict[str, Any] = {
        "exists": path.exists(),
        "shape": None,
        "dtype": "",
        "file_size_bytes": "",
        "error": "",
    }
    if not result["exists"]:
        result["error"] = "missing_file"
        return result

    try:
        result["file_size_bytes"] = path.stat().st_size
    except OSError as exc:
        result["error"] = f"stat_error:{type(exc).__name__}:{exc}"
        return result

    array = None
    try:
        array = np.load(path, mmap_mode="r")
        result["shape"] = tuple(int(dim) for dim in array.shape)
        result["dtype"] = str(array.dtype)
    except Exception as exc:  # noqa: BLE001 - index must preserve inspection failures.
        result["error"] = f"inspection_error:{type(exc).__name__}:{exc}"
    finally:
        if array is not None:
            mmap_obj = getattr(array, "_mmap", None)
            if mmap_obj is not None:
                mmap_obj.close()
            del array

    return result


def classify_scenario(name: str) -> tuple[str, str]:
    if DESIGN_SCENARIO_RE.match(name):
        return "design", ""
    if MEASURED_SCENARIO_RE.match(name):
        return "measured", ""
    return "unknown", "warning:unknown_scenario_type"


def discover_locations(dataset_root: Path) -> list[tuple[str, str]]:
    pairs: set[tuple[str, str]] = set()
    for split in SPLITS:
        for group in ("flood", "geodata"):
            group_dir = dataset_root / split / group
            if not group_dir.exists():
                continue
            try:
                for location_dir in sorted(group_dir.iterdir(), key=lambda item: item.name.lower()):
                    if location_dir.is_dir():
                        pairs.add((split, location_dir.name))
            except OSError:
                continue
    return sorted(pairs, key=lambda item: (item[0], item[1]))


def build_static_index(dataset_root: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for split, location in discover_locations(dataset_root):
        static_dir = dataset_root / split / "geodata" / location
        paths = {key: static_dir / filename for key, filename in STATIC_FILES.items()}
        inspected = {key: inspect_npy(path) for key, path in paths.items()}

        missing = [key for key, item in inspected.items() if item["error"] == "missing_file"]
        inspection_errors = [
            key for key, item in inspected.items() if str(item["error"]).startswith("inspection_error")
        ]
        shapes = [item["shape"] for item in inspected.values() if item["shape"] is not None]
        dtypes = [item["dtype"] for item in inspected.values() if item["dtype"]]

        if inspection_errors:
            status = "inspection_error"
        elif missing:
            status = "incomplete_missing_files"
        elif any(shape != (500, 500) for shape in shapes):
            status = "incomplete_shape_mismatch"
        elif len(set(dtypes)) > 1:
            status = "complete_with_warnings"
        else:
            status = "complete_500x500"

        rows.append(
            {
                "split": split,
                "location": location,
                "absolute_dem_path": path_text(paths["dem"]),
                "impervious_path": path_text(paths["impervious"]),
                "manhole_path": path_text(paths["manhole"]),
                "dem_shape": shape_text(inspected["dem"]["shape"]),
                "impervious_shape": shape_text(inspected["impervious"]["shape"]),
                "manhole_shape": shape_text(inspected["manhole"]["shape"]),
                "dem_dtype": inspected["dem"]["dtype"],
                "impervious_dtype": inspected["impervious"]["dtype"],
                "manhole_dtype": inspected["manhole"]["dtype"],
                "dem_file_size_bytes": inspected["dem"]["file_size_bytes"],
                "impervious_file_size_bytes": inspected["impervious"]["file_size_bytes"],
                "manhole_file_size_bytes": inspected["manhole"]["file_size_bytes"],
                "static_coverage_status": status,
            }
        )
    return rows


def static_lookup(static_rows: list[dict[str, Any]]) -> dict[tuple[str, str], dict[str, Any]]:
    return {(str(row["split"]), str(row["location"])): row for row in static_rows}


def build_scenario_index(dataset_root: Path, static_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    static_by_key = static_lookup(static_rows)

    for split in SPLITS:
        flood_root = dataset_root / split / "flood"
        if not flood_root.exists():
            continue
        try:
            locations = sorted(
                [item for item in flood_root.iterdir() if item.is_dir()],
                key=lambda item: item.name.lower(),
            )
        except OSError:
            continue

        for location_dir in locations:
            try:
                scenario_dirs = sorted(
                    [item for item in location_dir.iterdir() if item.is_dir()],
                    key=lambda item: item.name.lower(),
                )
            except OSError:
                continue

            for scenario_dir in scenario_dirs:
                scenario_type, type_note = classify_scenario(scenario_dir.name)
                flood_path = scenario_dir / "flood.npy"
                rainfall_path = scenario_dir / "rainfall.npy"
                flood = inspect_npy(flood_path)
                rainfall = inspect_npy(rainfall_path)

                notes = [type_note] if type_note else []
                if flood["error"]:
                    notes.append(f"flood_{flood['error']}")
                if rainfall["error"]:
                    notes.append(f"rainfall_{rainfall['error']}")
                if rainfall["shape"] and len(rainfall["shape"]) == 1:
                    rainfall_length: int | str = rainfall["shape"][0]
                else:
                    rainfall_length = "unknown"
                    notes.append("warning:unexpected_rainfall_shape")

                static = static_by_key.get((split, location_dir.name))
                if static is None:
                    static_dem_path = path_text(dataset_root / split / "geodata" / location_dir.name / STATIC_FILES["dem"])
                    static_impervious_path = path_text(
                        dataset_root / split / "geodata" / location_dir.name / STATIC_FILES["impervious"]
                    )
                    static_manhole_path = path_text(
                        dataset_root / split / "geodata" / location_dir.name / STATIC_FILES["manhole"]
                    )
                    notes.append("warning:missing_static_index_row")
                else:
                    static_dem_path = static["absolute_dem_path"]
                    static_impervious_path = static["impervious_path"]
                    static_manhole_path = static["manhole_path"]
                    if static["static_coverage_status"] != "complete_500x500":
                        notes.append(f"warning:static_{static['static_coverage_status']}")

                rows.append(
                    {
                        "split": split,
                        "location": location_dir.name,
                        "scenario": scenario_dir.name,
                        "scenario_type": scenario_type,
                        "flood_path": path_text(flood_path),
                        "rainfall_path": path_text(rainfall_path),
                        "flood_shape": shape_text(flood["shape"]),
                        "flood_dtype": flood["dtype"],
                        "rainfall_shape": shape_text(rainfall["shape"]),
                        "rainfall_dtype": rainfall["dtype"],
                        "rainfall_length": rainfall_length,
                        "static_dem_path": static_dem_path,
                        "static_impervious_path": static_impervious_path,
                        "static_manhole_path": static_manhole_path,
                        "flood_file_size_bytes": flood["file_size_bytes"],
                        "rainfall_file_size_bytes": rainfall["file_size_bytes"],
                        "notes": "; ".join(notes),
                    }
                )
    return rows


def count_values(rows: list[dict[str, Any]], column: str) -> dict[str, int]:
    values = Counter(str(row.get(column, "")) for row in rows if str(row.get(column, "")) != "")
    return dict(sorted(values.items()))


def count_by_location(rows: list[dict[str, Any]]) -> dict[str, int]:
    counts = Counter(f"{row['split']}/{row['location']}" for row in rows)
    return dict(sorted(counts.items()))


def warning_count(scenario_rows: list[dict[str, Any]], static_rows: list[dict[str, Any]]) -> int:
    scenario_warnings = sum(1 for row in scenario_rows if str(row.get("notes", "")).strip())
    static_warnings = sum(
        1 for row in static_rows if row.get("static_coverage_status") != "complete_500x500"
    )
    return scenario_warnings + static_warnings


def build_summary(
    dataset_root: Path,
    dataset_root_exists: bool,
    scenario_rows: list[dict[str, Any]],
    static_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    missing_flood_count = sum(1 for row in scenario_rows if not row["flood_file_size_bytes"])
    missing_rainfall_count = sum(1 for row in scenario_rows if not row["rainfall_file_size_bytes"])
    missing_static_count = sum(
        1 for row in static_rows if row["static_coverage_status"] in {"incomplete_missing_files", "inspection_error"}
    )
    valid_scenarios = (
        dataset_root_exists
        and len(scenario_rows) > 0
        and missing_flood_count == 0
        and missing_rainfall_count == 0
    )
    valid_static = any(row["static_coverage_status"] == "complete_500x500" for row in static_rows)
    level4_plus_supported = bool(valid_scenarios and valid_static)

    if not dataset_root_exists:
        selected_decision = "indexing_incomplete_dataset_path_issue"
    elif not valid_scenarios or not valid_static:
        selected_decision = "indexing_complete_with_warnings"
    else:
        selected_decision = "indexing_ready_for_dataloader_smoke"

    dtype_counter: Counter[str] = Counter()
    for column in ("flood_dtype", "rainfall_dtype"):
        dtype_counter.update(str(row[column]) for row in scenario_rows if str(row[column]))
    for column in ("dem_dtype", "impervious_dtype", "manhole_dtype"):
        dtype_counter.update(str(row[column]) for row in static_rows if str(row[column]))

    return {
        "dataset_root": path_text(dataset_root),
        "dataset_root_exists": dataset_root_exists,
        "path_style": "absolute_forward_slash",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "scenario_count_total": len(scenario_rows),
        "scenario_count_by_split": count_values(scenario_rows, "split"),
        "scenario_count_by_location": count_by_location(scenario_rows),
        "scenario_type_counts": count_values(scenario_rows, "scenario_type"),
        "static_index_rows": len(static_rows),
        "missing_flood_count": missing_flood_count,
        "missing_rainfall_count": missing_rainfall_count,
        "missing_static_count": missing_static_count,
        "flood_shape_counts": count_values(scenario_rows, "flood_shape"),
        "rainfall_shape_counts": count_values(scenario_rows, "rainfall_shape"),
        "rainfall_length_counts": count_values(scenario_rows, "rainfall_length"),
        "dtype_counts": dict(sorted(dtype_counter.items())),
        "static_coverage_status_counts": count_values(static_rows, "static_coverage_status"),
        "warning_count": warning_count(scenario_rows, static_rows),
        "selected_decision": selected_decision,
        "level4_plus_supported": level4_plus_supported,
        "level5_supported": False,
        "training_authorized": False,
        "next_recommended_action": (
            "Phase 46 dataloader smoke test and downsample/tiling feasibility"
        ),
        "outputs": {
            "scenario_index_csv": path_text(OUTPUT_DIR / "scenario_index.csv"),
            "static_geodata_index_csv": path_text(OUTPUT_DIR / "static_geodata_index.csv"),
            "dataset_index_summary_json": path_text(OUTPUT_DIR / "dataset_index_summary.json"),
            "dataset_index_summary_md": path_text(OUTPUT_DIR / "dataset_index_summary.md"),
            "adapter_design_notes_md": path_text(OUTPUT_DIR / "adapter_design_notes.md"),
        },
    }


def markdown_counts(title: str, counts: dict[str, int]) -> list[str]:
    lines = [f"## {title}", ""]
    if not counts:
        lines.append("- none")
    else:
        lines.extend(f"- `{key}`: `{value}`" for key, value in counts.items())
    lines.append("")
    return lines


def write_summary_md(path: Path, summary: dict[str, Any]) -> None:
    lines = [
        "# Phase 45 Full Dataset Index Summary",
        "",
        "No training, seed runs, sweeps, loss/config/model edits, SWE residuals, or PINN components were executed.",
        "",
        "## Decision",
        "",
        f"- dataset_root: `{summary['dataset_root']}`",
        f"- dataset_root_exists: `{bool_text(summary['dataset_root_exists'])}`",
        f"- scenario_count_total: `{summary['scenario_count_total']}`",
        f"- static_index_rows: `{summary['static_index_rows']}`",
        f"- missing_flood_count: `{summary['missing_flood_count']}`",
        f"- missing_rainfall_count: `{summary['missing_rainfall_count']}`",
        f"- missing_static_count: `{summary['missing_static_count']}`",
        f"- warning_count: `{summary['warning_count']}`",
        f"- selected_decision: `{summary['selected_decision']}`",
        f"- level4_plus_supported: `{bool_text(summary['level4_plus_supported'])}`",
        f"- level5_supported: `{bool_text(summary['level5_supported'])}`",
        f"- training_authorized: `{bool_text(summary['training_authorized'])}`",
        f"- next_recommended_action: `{summary['next_recommended_action']}`",
        "",
    ]
    lines.extend(markdown_counts("Scenario Count By Split", summary["scenario_count_by_split"]))
    lines.extend(markdown_counts("Scenario Count By Location", summary["scenario_count_by_location"]))
    lines.extend(markdown_counts("Scenario Type Counts", summary["scenario_type_counts"]))
    lines.extend(markdown_counts("Flood Shape Counts", summary["flood_shape_counts"]))
    lines.extend(markdown_counts("Rainfall Shape Counts", summary["rainfall_shape_counts"]))
    lines.extend(markdown_counts("Rainfall Length Counts", summary["rainfall_length_counts"]))
    lines.extend(markdown_counts("Dtype Counts", summary["dtype_counts"]))
    lines.extend(
        markdown_counts("Static Coverage Status Counts", summary["static_coverage_status_counts"])
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def write_adapter_notes(path: Path, summary: dict[str, Any]) -> None:
    path.write_text(
        "\n".join(
            [
                "# Phase 45 Lightweight Adapter Design Notes",
                "",
                "These notes define the intended Phase 46 data access contract. Phase 45 produced indexes only and did not train models.",
                "",
                "## Inputs",
                "",
                "- `scenario_index.csv` is the canonical scenario table. Phase 46 should read it once, validate required columns, and use each row as a lazy record pointing to flood, rainfall, and static geodata paths.",
                "- `static_geodata_index.csv` is the canonical static coverage table. Phase 46 should join it by `split` and `location` or use the static path columns already copied into each scenario row.",
                f"- Paths are stored as `{summary['path_style']}` for reproducibility on this workstation. A future adapter should allow a configurable dataset root so indexes can be relocated without rescanning.",
                "",
                "## Lazy Loading Contract",
                "",
                "- Do not load full arrays during adapter initialization.",
                "- Open `flood.npy`, `rainfall.npy`, `absolute_DEM.npy`, `impervious.npy`, and `manhole.npy` only when a caller requests a sample or metadata check.",
                "- Use `numpy.load(path, mmap_mode=\"r\")` for heavy arrays and slice only the timesteps or spatial windows needed for a smoke test.",
                "- Do not compute statistics, normalization constants, histograms, conservation residuals, or derived physics fields in the adapter.",
                "",
                "## Filtering Contract",
                "",
                "- Support filtering by `split`, `location`, `scenario_type`, and `rainfall_length` before any array is opened.",
                "- Preserve both `design` and `measured` scenario types; treat `unknown` rows as opt-in records for diagnostics.",
                "- Require valid flood/rainfall/static paths before a Phase 46 smoke-test sample is materialized.",
                "",
                "## Future Downsample And Tiling Checks",
                "",
                "- Phase 46 may test read-time downsample candidates at `128x128` and `256x256` for shape feasibility only.",
                "- Tile or multiscale sampling can be explored by slicing mmap arrays into spatial windows, but Phase 46 should first verify boundary handling, static map alignment, rainfall length variability, and batch collation.",
                "- Any downsample, tile, or multiscale path should remain a smoke-test data access check until a later phase explicitly authorizes training.",
                "",
                "## Guardrails",
                "",
                "- Phase 45 performed no training.",
                "- Phase 45 did not run `seed42`, `seed123`, `seed202`, or sweeps.",
                "- Phase 45 did not modify loss functions, configs, model architecture, SWE residuals, or PINN components.",
                "- Phase 45 makes no Level 5, SWE, PINN, strict conservation, or hydrodynamic closure claim.",
                "- `level5_supported` remains `false` and `training_authorized` remains `false`.",
            ]
        ),
        encoding="utf-8",
    )


def main() -> None:
    args = parse_args()
    dataset_root = args.dataset_root.expanduser()
    dataset_root_exists = dataset_root.exists()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    static_rows = build_static_index(dataset_root) if dataset_root_exists else []
    scenario_rows = build_scenario_index(dataset_root, static_rows) if dataset_root_exists else []
    summary = build_summary(dataset_root, dataset_root_exists, scenario_rows, static_rows)

    write_csv(OUTPUT_DIR / "scenario_index.csv", scenario_rows, SCENARIO_COLUMNS)
    write_csv(OUTPUT_DIR / "static_geodata_index.csv", static_rows, STATIC_COLUMNS)
    (OUTPUT_DIR / "dataset_index_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8"
    )
    write_summary_md(OUTPUT_DIR / "dataset_index_summary.md", summary)
    write_adapter_notes(OUTPUT_DIR / "adapter_design_notes.md", summary)

    print(f"dataset_root_exists={bool_text(summary['dataset_root_exists'])}")
    print(f"scenario_count_total={summary['scenario_count_total']}")
    print(f"static_index_rows={summary['static_index_rows']}")
    print(f"warning_count={summary['warning_count']}")
    print(f"selected_decision={summary['selected_decision']}")
    print(f"level4_plus_supported={bool_text(summary['level4_plus_supported'])}")
    print(f"level5_supported={bool_text(summary['level5_supported'])}")
    print(f"training_authorized={bool_text(summary['training_authorized'])}")


if __name__ == "__main__":
    main()
