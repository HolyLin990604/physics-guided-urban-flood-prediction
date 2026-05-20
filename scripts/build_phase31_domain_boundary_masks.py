from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
from typing import Any

import numpy as np


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = Path("analysis/phase31_physics_input_recovery_readiness")
DEFAULT_DATASET_ROOT = Path(r"E:\BaiduNetdiskDownload\urbanflood24_lite_release\urbanflood24_lite")

SPLITS = ("train", "test")
CHANNELS = ("absolute_DEM", "impervious", "manhole")
EXPECTED_SHAPE = (128, 128)
DEM_VALID_THRESHOLD = 99.0
HIGH_IMPERVIOUS_THRESHOLD = 0.8


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Phase 31 diagnostic-only construction of candidate domain/boundary masks "
            "from recovered DEM/static maps. This script does not train or modify "
            "models/configs/losses."
        )
    )
    parser.add_argument("--dataset-root", type=Path, default=DEFAULT_DATASET_ROOT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
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


def safe_ratio(numerator: int, denominator: int) -> float | None:
    if denominator == 0:
        return None
    return safe_float(numerator / denominator)


def discover_locations(dataset_root: Path) -> list[str]:
    locations = {
        path.name
        for split in SPLITS
        for path in (dataset_root / split / "geodata").glob("location*")
        if path.is_dir()
    }
    return sorted(locations)


def load_array(path: Path) -> np.ndarray | None:
    if not path.exists():
        return None
    try:
        return np.asarray(np.load(path, allow_pickle=False))
    except Exception:  # noqa: BLE001 - diagnostic script should continue.
        return None


def finite_numeric(arr: np.ndarray | None) -> np.ndarray | None:
    if arr is None:
        return None
    if not (np.issubdtype(arr.dtype, np.number) or np.issubdtype(arr.dtype, np.bool_)):
        return None
    return arr.astype(np.float64, copy=False)


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


def build_masks(dem: np.ndarray | None, impervious: np.ndarray | None, manhole: np.ndarray | None) -> dict[str, np.ndarray] | None:
    dem_values = finite_numeric(dem)
    if dem_values is None or dem_values.ndim != 2:
        return None

    finite_dem = np.isfinite(dem_values)
    valid_domain_mask = finite_dem & (dem_values < DEM_VALID_THRESHOLD)
    invalid_or_high_mask = (~finite_dem) | (dem_values >= DEM_VALID_THRESHOLD)
    boundary_ring_mask = adjacent_to_invalid_or_border(valid_domain_mask, invalid_or_high_mask)
    interior_mask = valid_domain_mask & ~boundary_ring_mask

    outer_border_mask = np.zeros(valid_domain_mask.shape, dtype=bool)
    outer_border_mask[0, :] = True
    outer_border_mask[-1, :] = True
    outer_border_mask[:, 0] = True
    outer_border_mask[:, -1] = True

    manhole_values = finite_numeric(manhole)
    if manhole_values is not None and manhole_values.shape == valid_domain_mask.shape:
        manhole_nonzero_mask = np.isfinite(manhole_values) & (manhole_values > 0.0)
    else:
        manhole_nonzero_mask = np.zeros(valid_domain_mask.shape, dtype=bool)

    impervious_values = finite_numeric(impervious)
    if impervious_values is not None and impervious_values.shape == valid_domain_mask.shape:
        high_impervious_mask = np.isfinite(impervious_values) & (impervious_values >= HIGH_IMPERVIOUS_THRESHOLD)
    else:
        high_impervious_mask = np.zeros(valid_domain_mask.shape, dtype=bool)

    return {
        "valid_domain_mask": valid_domain_mask,
        "invalid_or_high_mask": invalid_or_high_mask,
        "boundary_ring_mask": boundary_ring_mask,
        "interior_mask": interior_mask,
        "outer_border_mask": outer_border_mask,
        "manhole_nonzero_mask": manhole_nonzero_mask,
        "high_impervious_mask": high_impervious_mask,
    }


def load_location_arrays(dataset_root: Path, split: str, location: str) -> dict[str, np.ndarray | None]:
    geodata_dir = dataset_root / split / "geodata" / location
    return {channel: load_array(geodata_dir / f"{channel}.npy") for channel in CHANNELS}


def mask_counts(masks: dict[str, np.ndarray]) -> dict[str, int]:
    return {name: int(mask.sum()) for name, mask in masks.items()}


def summary_row(
    dataset_root: Path,
    split: str,
    location: str,
    arrays: dict[str, np.ndarray | None],
    masks: dict[str, np.ndarray] | None,
) -> dict[str, Any]:
    dem = arrays["absolute_DEM"]
    shape = list(dem.shape) if dem is not None else None
    total_cells = int(np.prod(dem.shape)) if dem is not None and dem.ndim == 2 else 0

    row: dict[str, Any] = {
        "split": split,
        "location": location,
        "absolute_dem_path": str(dataset_root / split / "geodata" / location / "absolute_DEM.npy"),
        "impervious_path": str(dataset_root / split / "geodata" / location / "impervious.npy"),
        "manhole_path": str(dataset_root / split / "geodata" / location / "manhole.npy"),
        "shape": shape,
        "shape_is_128x128": tuple(shape or ()) == EXPECTED_SHAPE,
        "valid_domain_count": None,
        "valid_domain_ratio": None,
        "invalid_or_high_count": None,
        "invalid_or_high_ratio": None,
        "boundary_ring_count": None,
        "boundary_ring_ratio_over_valid": None,
        "interior_count": None,
        "interior_ratio_over_valid": None,
        "outer_border_valid_count": None,
        "manhole_nonzero_count": None,
        "manhole_nonzero_ratio_over_valid": None,
        "high_impervious_count": None,
        "high_impervious_ratio_over_valid": None,
        "load_status": "loaded" if masks is not None else "missing_or_invalid",
    }
    if masks is None:
        return row

    counts = mask_counts(masks)
    valid_count = counts["valid_domain_mask"]
    row.update(
        {
            "valid_domain_count": valid_count,
            "valid_domain_ratio": safe_ratio(valid_count, total_cells),
            "invalid_or_high_count": counts["invalid_or_high_mask"],
            "invalid_or_high_ratio": safe_ratio(counts["invalid_or_high_mask"], total_cells),
            "boundary_ring_count": counts["boundary_ring_mask"],
            "boundary_ring_ratio_over_valid": safe_ratio(counts["boundary_ring_mask"], valid_count),
            "interior_count": counts["interior_mask"],
            "interior_ratio_over_valid": safe_ratio(counts["interior_mask"], valid_count),
            "outer_border_valid_count": int((masks["outer_border_mask"] & masks["valid_domain_mask"]).sum()),
            "manhole_nonzero_count": counts["manhole_nonzero_mask"],
            "manhole_nonzero_ratio_over_valid": safe_ratio(int((masks["manhole_nonzero_mask"] & masks["valid_domain_mask"]).sum()), valid_count),
            "high_impervious_count": counts["high_impervious_mask"],
            "high_impervious_ratio_over_valid": safe_ratio(int((masks["high_impervious_mask"] & masks["valid_domain_mask"]).sum()), valid_count),
        }
    )
    return row


def consistency_rows(mask_sets: dict[tuple[str, str], dict[str, np.ndarray] | None]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    locations = sorted({location for _, location in mask_sets})
    mask_names = (
        "valid_domain_mask",
        "invalid_or_high_mask",
        "boundary_ring_mask",
        "interior_mask",
        "outer_border_mask",
        "manhole_nonzero_mask",
        "high_impervious_mask",
    )
    for location in locations:
        train = mask_sets.get(("train", location))
        test = mask_sets.get(("test", location))
        row: dict[str, Any] = {
            "location": location,
            "train_masks_loaded": train is not None,
            "test_masks_loaded": test is not None,
            "same_shape": None,
            "all_masks_equal": None,
        }
        if train is not None and test is not None:
            row["same_shape"] = all(train[name].shape == test[name].shape for name in mask_names)
            for name in mask_names:
                row[f"{name}_equal"] = bool(np.array_equal(train[name], test[name]))
            row["all_masks_equal"] = all(bool(row[f"{name}_equal"]) for name in mask_names)
        else:
            for name in mask_names:
                row[f"{name}_equal"] = None
        rows.append(row)
    return rows


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


def build_report(
    dataset_root: Path,
    summary_rows: list[dict[str, Any]],
    consistency: list[dict[str, Any]],
    figure_paths: list[str],
) -> dict[str, Any]:
    loaded_rows = [row for row in summary_rows if row["load_status"] == "loaded"]
    locations = sorted({row["location"] for row in summary_rows})
    all_shape_128 = bool(loaded_rows) and all(bool(row["shape_is_128x128"]) for row in loaded_rows)
    all_valid_masks = bool(loaded_rows) and all((row["valid_domain_count"] or 0) > 0 for row in loaded_rows)
    all_boundary_masks = bool(loaded_rows) and all((row["boundary_ring_count"] or 0) > 0 for row in loaded_rows)
    all_interior_masks = bool(loaded_rows) and all((row["interior_count"] or 0) > 0 for row in loaded_rows)
    train_test_consistent = bool(consistency) and all(bool(row["all_masks_equal"]) for row in consistency)
    manhole_supported = bool(loaded_rows) and any((row["manhole_nonzero_count"] or 0) > 0 for row in loaded_rows)
    impervious_supported = bool(loaded_rows) and any((row["high_impervious_count"] or 0) > 0 for row in loaded_rows)
    level4_ready = all_shape_128 and all_valid_masks and all_boundary_masks and train_test_consistent

    return {
        "dataset_root": str(dataset_root),
        "guardrail_note": (
            "Diagnostic-only mask construction. No training, architecture changes, loss changes, "
            "training config changes, seed123/seed202 runs, sweeps, strict mass-conservation claims, "
            "full SWE/PINN claims, or hydrodynamic-closure claims were performed."
        ),
        "locations_processed": len(locations),
        "locations": locations,
        "records_processed": len(loaded_rows),
        "expected_records": len(locations) * len(SPLITS),
        "all_masks_shape_128x128": all_shape_128,
        "valid_domain_mask_status": "supported_dem_lt_99" if all_shape_128 and all_valid_masks else "unsupported_or_incomplete",
        "boundary_ring_mask_status": "supported" if all_shape_128 and all_boundary_masks else "unsupported_or_incomplete",
        "interior_mask_status": "supported" if all_shape_128 and all_interior_masks else "unsupported_or_incomplete",
        "train_test_mask_consistency": "consistent_equal" if train_test_consistent else "inconsistent_or_missing",
        "manhole_static_proxy_status": "supported_nonzero_indicator" if manhole_supported else "unsupported_or_empty",
        "impervious_static_proxy_status": "supported_high_impervious_indicator" if impervious_supported else "unsupported_or_empty",
        "level4_plus_domain_boundary_readiness": "supported" if level4_ready else "not_supported",
        "level5_status": "unsupported",
        "level5_reason": (
            "Level 5 remains unsupported because aligned velocity/flux, boundary source/sink fields, dx/dy, dt, "
            "and hydrodynamic state variables were not recovered by this mask diagnostic."
        ),
        "summary_rows": summary_rows,
        "train_test_mask_consistency_rows": consistency,
        "figure_paths": figure_paths,
    }


def write_markdown(path: Path, report: dict[str, Any]) -> None:
    rows = report["summary_rows"]
    train_rows = [row for row in rows if row["split"] == "train"]

    lines = [
        "# Phase 31 Domain Boundary Mask Inspection",
        "",
        "This diagnostic constructs candidate masks from recovered DEM/static maps and writes only Phase 31 analysis outputs. It does not train, modify architecture, modify losses, modify training configs, run seed123/seed202, or perform sweeps.",
        "",
        "## Executive Summary",
        "",
        f"- Locations processed: {report['locations_processed']}",
        f"- All masks shape-compatible with 128 x 128 flood maps: `{report['all_masks_shape_128x128']}`",
        f"- Valid-domain mask status: `{report['valid_domain_mask_status']}`",
        f"- Boundary-ring mask status: `{report['boundary_ring_mask_status']}`",
        f"- Interior mask status: `{report['interior_mask_status']}`",
        f"- Train/test mask consistency: `{report['train_test_mask_consistency']}`",
        f"- Level 4+ domain/boundary-aware readiness: `{report['level4_plus_domain_boundary_readiness']}`",
        f"- Level 5 status: `{report['level5_status']}`",
        "",
        "## Direct Answers",
        "",
        f"1. A valid-domain mask can be constructed from `absolute_DEM < 99`: `{report['valid_domain_mask_status'] == 'supported_dem_lt_99'}`. This is a Level 4+ proxy support, not a conservation proof.",
        f"2. Train/test masks are consistent: `{report['train_test_mask_consistency']}`.",
        f"3. A boundary-ring mask can be constructed from valid cells adjacent to invalid/high cells or the image border: `{report['boundary_ring_mask_status'] == 'supported'}`.",
        f"4. An interior mask can be constructed as valid cells not in the boundary ring: `{report['interior_mask_status'] == 'supported'}`.",
        f"5. Manhole and impervious maps support additional static proxy diagnostics: manhole=`{report['manhole_static_proxy_status']}`, impervious=`{report['impervious_static_proxy_status']}`.",
        f"6. This supports Level 4+ domain-aware / boundary-aware diagnostics: `{report['level4_plus_domain_boundary_readiness']}`.",
        "7. This does not change Level 5 status. Level 5 remains unsupported unless velocity/flux, boundary source/sink, dx/dy, dt, and hydrodynamic state variables are found.",
        "8. Recommended next technical step: implement a diagnostic-only Level 4+ script that applies these masks to existing prediction/target flood-depth rasters and reports domain-interior, boundary-ring, high-impervious, and manhole-proximal proxy errors without changing training.",
        "",
        "## Train Split Location Summary",
        "",
        "| Location | Valid ratio | Invalid/high ratio | Boundary/valid | Interior/valid | Border valid count | Manhole/valid | High impervious/valid |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in train_rows:
        lines.append(
            f"| {row['location']} | {row['valid_domain_ratio']} | {row['invalid_or_high_ratio']} | "
            f"{row['boundary_ring_ratio_over_valid']} | {row['interior_ratio_over_valid']} | "
            f"{row['outer_border_valid_count']} | {row['manhole_nonzero_ratio_over_valid']} | "
            f"{row['high_impervious_ratio_over_valid']} |"
        )

    lines.extend(
        [
            "",
            "## Train/Test Mask Consistency",
            "",
            "| Location | Same shape | All masks equal | Valid domain | Boundary ring | Interior | Manhole nonzero | High impervious |",
            "| --- | --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for row in report["train_test_mask_consistency_rows"]:
        lines.append(
            f"| {row['location']} | `{row['same_shape']}` | `{row['all_masks_equal']}` | "
            f"`{row['valid_domain_mask_equal']}` | `{row['boundary_ring_mask_equal']}` | "
            f"`{row['interior_mask_equal']}` | `{row['manhole_nonzero_mask_equal']}` | "
            f"`{row['high_impervious_mask_equal']}` |"
        )

    lines.extend(
        [
            "",
            "## Classification",
            "",
            "Because the valid-domain and boundary-ring masks are shape-compatible and train/test consistent, Level 4+ domain-aware and boundary-aware proxy diagnostics are supported. Level 5 remains unsupported because this diagnostic does not recover aligned hydrodynamic state, velocity/flux, boundary/source-sink, dx/dy, or dt variables.",
            "",
        ]
    )
    if report["figure_paths"]:
        lines.extend(["## Optional Figures", ""])
        for figure_path in report["figure_paths"]:
            lines.append(f"- `{figure_path}`")
        lines.append("")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def write_figures(
    output_dir: Path,
    mask_sets: dict[tuple[str, str], dict[str, np.ndarray] | None],
    skip: bool,
) -> list[str]:
    if skip:
        return []
    try:
        import matplotlib.pyplot as plt
    except Exception:  # noqa: BLE001 - optional figures only.
        return []

    figure_dir = output_dir / "figures"
    figure_dir.mkdir(parents=True, exist_ok=True)
    paths: list[str] = []
    locations = sorted({location for split, location in mask_sets if split == "train"})
    panels = (
        ("valid_domain_mask", "DEM valid domain"),
        ("invalid_or_high_mask", "Invalid/high"),
        ("boundary_ring_mask", "Boundary ring"),
        ("interior_mask", "Interior"),
        ("manhole_nonzero_mask", "Manhole nonzero"),
        ("high_impervious_mask", "High impervious"),
    )
    for location in locations:
        masks = mask_sets.get(("train", location))
        if masks is None:
            continue
        fig, axes = plt.subplots(2, 3, figsize=(10, 6), constrained_layout=True)
        for axis, (name, title) in zip(axes.ravel(), panels):
            axis.imshow(masks[name], cmap="gray", vmin=0, vmax=1)
            axis.set_title(title)
            axis.axis("off")
        fig.suptitle(f"{location} domain/boundary mask candidates")
        path = figure_dir / f"domain_boundary_mask_{location}.png"
        fig.savefig(path, dpi=160)
        plt.close(fig)
        paths.append(display_path(path))
    return paths


def main() -> None:
    args = parse_args()
    dataset_root = args.dataset_root
    output_dir = resolve_repo_path(args.output_dir)

    locations = discover_locations(dataset_root)
    summary_rows: list[dict[str, Any]] = []
    mask_sets: dict[tuple[str, str], dict[str, np.ndarray] | None] = {}

    for split in SPLITS:
        for location in locations:
            arrays = load_location_arrays(dataset_root, split, location)
            masks = build_masks(arrays["absolute_DEM"], arrays["impervious"], arrays["manhole"])
            mask_sets[(split, location)] = masks
            summary_rows.append(summary_row(dataset_root, split, location, arrays, masks))

    consistency = consistency_rows(mask_sets)
    figure_paths = write_figures(output_dir, mask_sets, args.skip_figures)
    report = build_report(dataset_root, summary_rows, consistency, figure_paths)

    write_csv(output_dir / "domain_boundary_mask_summary.csv", summary_rows)
    write_json(output_dir / "domain_boundary_mask_summary.json", report)
    write_markdown(output_dir / "domain_boundary_mask_inspection.md", report)

    print("Phase 31 domain/boundary mask diagnostic complete.")
    print(f"  locations processed: {report['locations_processed']}")
    print(f"  valid-domain mask status: {report['valid_domain_mask_status']}")
    print(f"  boundary-ring mask status: {report['boundary_ring_mask_status']}")
    print(f"  train/test mask consistency: {report['train_test_mask_consistency']}")
    print(f"  Level 4+ domain/boundary-aware readiness: {report['level4_plus_domain_boundary_readiness']}")
    print(f"  Level 5 status: {report['level5_status']}")
    print(f"  wrote: {display_path(output_dir / 'domain_boundary_mask_summary.csv')}")
    print(f"  wrote: {display_path(output_dir / 'domain_boundary_mask_summary.json')}")
    print(f"  wrote: {display_path(output_dir / 'domain_boundary_mask_inspection.md')}")


if __name__ == "__main__":
    main()
