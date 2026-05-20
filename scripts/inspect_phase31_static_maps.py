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
DEFAULT_INVENTORY = DEFAULT_OUTPUT_DIR / "physics_input_inventory.json"
DEFAULT_DATASET_ROOT = Path(r"E:\BaiduNetdiskDownload\urbanflood24_lite_release\urbanflood24_lite")

CHANNELS: dict[str, dict[str, str]] = {
    "absolute_DEM": {
        "filename": "absolute_DEM.npy",
        "semantic_role": "static elevation / topographic proxy",
    },
    "impervious": {
        "filename": "impervious.npy",
        "semantic_role": "static runoff / imperviousness proxy",
    },
    "manhole": {
        "filename": "manhole.npy",
        "semantic_role": "sparse drainage / manhole proxy",
    },
}
SPLITS = ("train", "test")
EXPECTED_SHAPE = (128, 128)
QUANTILES = (0, 1, 5, 50, 95, 99, 100)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Phase 31 diagnostic-only inspection of recovered static maps. "
            "This script does not train or modify models/configs/losses."
        )
    )
    parser.add_argument("--inventory", type=Path, default=DEFAULT_INVENTORY)
    parser.add_argument("--dataset-root", type=Path, default=None)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--skip-figures", action="store_true")
    return parser.parse_args()


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


def display_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT)).replace("\\", "/")
    except ValueError:
        return str(path)


def discover_dataset_root(inventory_path: Path, explicit_root: Path | None) -> Path:
    if explicit_root is not None:
        return explicit_root
    try:
        data = json.loads(resolve_repo_path(inventory_path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return DEFAULT_DATASET_ROOT
    roots = data.get("audit_scope", {}).get("dataset_roots_inspected", [])
    for root in roots:
        path = Path(root)
        if path.exists():
            return path
    return DEFAULT_DATASET_ROOT


def load_array(path: Path) -> np.ndarray | None:
    if not path.exists():
        return None
    try:
        return np.asarray(np.load(path, allow_pickle=False))
    except Exception:  # noqa: BLE001 - diagnostic script should continue.
        return None


def quantile_dict(values: np.ndarray) -> dict[str, float | None]:
    finite = values[np.isfinite(values)]
    if finite.size == 0:
        return {f"q{q:g}": None for q in QUANTILES}
    quantiles = np.nanpercentile(finite, QUANTILES)
    return {f"q{q:g}": safe_float(value) for q, value in zip(QUANTILES, quantiles)}


def stats_for_array(path: Path, split: str, location: str, channel: str, arr: np.ndarray | None) -> dict[str, Any]:
    record: dict[str, Any] = {
        "path": str(path),
        "split": split,
        "location": location,
        "channel_name": channel,
        "semantic_role": CHANNELS[channel]["semantic_role"],
        "shape": None,
        "dtype": None,
        "min": None,
        "max": None,
        "mean": None,
        "std": None,
        "finite_ratio": None,
        "zero_ratio": None,
        "high_value_ratio_dem_ge_99": None,
        "candidate_valid_domain_ratio_dem_lt_99": None,
        "candidate_high_invalid_mask_count": None,
        "shape_is_128x128": False,
        "file_exists": path.exists(),
        "load_status": "missing" if arr is None else "loaded",
    }
    record.update({f"q{q:g}": None for q in QUANTILES})
    if arr is None:
        return record

    record["shape"] = list(arr.shape)
    record["dtype"] = str(arr.dtype)
    record["shape_is_128x128"] = tuple(arr.shape) == EXPECTED_SHAPE
    if arr.size == 0 or not (np.issubdtype(arr.dtype, np.number) or np.issubdtype(arr.dtype, np.bool_)):
        record["load_status"] = "empty_or_non_numeric"
        return record

    values = arr.astype(np.float64, copy=False)
    finite_mask = np.isfinite(values)
    finite_values = values[finite_mask]
    record["finite_ratio"] = safe_float(finite_mask.mean())
    if finite_values.size == 0:
        record["load_status"] = "no_finite_values"
        return record

    record["min"] = safe_float(np.min(finite_values))
    record["max"] = safe_float(np.max(finite_values))
    record["mean"] = safe_float(np.mean(finite_values))
    record["std"] = safe_float(np.std(finite_values))
    record["zero_ratio"] = safe_float(np.mean(finite_values == 0.0))
    record.update(quantile_dict(values))

    if channel == "absolute_DEM":
        high_invalid = finite_mask & (values >= 99.0)
        valid = finite_mask & (values < 99.0)
        record["high_value_ratio_dem_ge_99"] = safe_float(high_invalid.sum() / values.size)
        record["candidate_valid_domain_ratio_dem_lt_99"] = safe_float(valid.sum() / values.size)
        record["candidate_high_invalid_mask_count"] = int(high_invalid.sum())
    else:
        record["high_value_ratio_dem_ge_99"] = safe_float(np.mean(finite_values >= 99.0))
        record["candidate_valid_domain_ratio_dem_lt_99"] = None
        record["candidate_high_invalid_mask_count"] = None
    return record


def inspect_channels(dataset_root: Path) -> tuple[list[dict[str, Any]], dict[tuple[str, str, str], np.ndarray]]:
    rows: list[dict[str, Any]] = []
    arrays: dict[tuple[str, str, str], np.ndarray] = {}
    locations = sorted(
        {
            path.name
            for split in SPLITS
            for path in (dataset_root / split / "geodata").glob("location*")
            if path.is_dir()
        }
    )
    for split in SPLITS:
        for location in locations:
            for channel, spec in CHANNELS.items():
                path = dataset_root / split / "geodata" / location / spec["filename"]
                arr = load_array(path)
                if arr is not None:
                    arrays[(split, location, channel)] = arr
                rows.append(stats_for_array(path, split, location, channel, arr))
    return rows, arrays


def train_test_consistency_rows(
    arrays: dict[tuple[str, str, str], np.ndarray],
    channel_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    row_lookup = {(row["split"], row["location"], row["channel_name"]): row for row in channel_rows}
    locations = sorted({key[1] for key in arrays})
    rows: list[dict[str, Any]] = []
    for location in locations:
        for channel in CHANNELS:
            train = arrays.get(("train", location, channel))
            test = arrays.get(("test", location, channel))
            row = {
                "location": location,
                "channel_name": channel,
                "train_path": row_lookup.get(("train", location, channel), {}).get("path"),
                "test_path": row_lookup.get(("test", location, channel), {}).get("path"),
                "train_exists": train is not None,
                "test_exists": test is not None,
                "same_shape": None,
                "exact_equal": None,
                "allclose": None,
                "max_abs_diff": None,
                "mean_abs_diff": None,
            }
            if train is not None and test is not None:
                row["same_shape"] = train.shape == test.shape
                if train.shape == test.shape:
                    diff = np.abs(train.astype(np.float64, copy=False) - test.astype(np.float64, copy=False))
                    finite_diff = diff[np.isfinite(diff)]
                    row["exact_equal"] = bool(np.array_equal(train, test))
                    row["allclose"] = bool(np.allclose(train, test, equal_nan=True))
                    row["max_abs_diff"] = safe_float(np.max(finite_diff)) if finite_diff.size else None
                    row["mean_abs_diff"] = safe_float(np.mean(finite_diff)) if finite_diff.size else None
            rows.append(row)
    return rows


def location_summary_rows(
    channel_rows: list[dict[str, Any]],
    consistency_rows: list[dict[str, Any]],
    arrays: dict[tuple[str, str, str], np.ndarray],
) -> list[dict[str, Any]]:
    locations = sorted({row["location"] for row in channel_rows})
    consistency_lookup = {(row["location"], row["channel_name"]): row for row in consistency_rows}
    rows: list[dict[str, Any]] = []
    for location in locations:
        dem = arrays.get(("train", location, "absolute_DEM"))
        if dem is None:
            dem = arrays.get(("test", location, "absolute_DEM"))
        valid_mask = None
        if dem is not None:
            values = dem.astype(np.float64, copy=False)
            valid_mask = np.isfinite(values) & (values < 99.0)

        location_rows = [row for row in channel_rows if row["location"] == location]
        train_rows = [row for row in location_rows if row["split"] == "train"]
        dem_train = next((row for row in train_rows if row["channel_name"] == "absolute_DEM"), {})
        imperv_train = next((row for row in train_rows if row["channel_name"] == "impervious"), {})
        manhole_train = next((row for row in train_rows if row["channel_name"] == "manhole"), {})

        imperv = arrays.get(("train", location, "impervious"))
        if imperv is None:
            imperv = arrays.get(("test", location, "impervious"))
        manhole = arrays.get(("train", location, "manhole"))
        if manhole is None:
            manhole = arrays.get(("test", location, "manhole"))
        imperv_valid_mean = masked_mean(imperv, valid_mask)
        manhole_valid_nonzero_ratio = masked_nonzero_ratio(manhole, valid_mask)
        manhole_valid_mean = masked_mean(manhole, valid_mask)

        row = {
            "location": location,
            "channels_present_train": sum(bool(row["file_exists"]) for row in train_rows),
            "channels_shape_128x128_train": sum(bool(row["shape_is_128x128"]) for row in train_rows),
            "all_train_channels_shape_128x128": all(bool(row["shape_is_128x128"]) for row in train_rows) if train_rows else False,
            "train_test_all_channels_allclose": all(
                bool(consistency_lookup.get((location, channel), {}).get("allclose")) for channel in CHANNELS
            ),
            "dem_valid_pixel_count": int(valid_mask.sum()) if valid_mask is not None else None,
            "dem_valid_ratio": safe_float(valid_mask.mean()) if valid_mask is not None else None,
            "dem_high_invalid_count": dem_train.get("candidate_high_invalid_mask_count"),
            "dem_high_invalid_ratio": dem_train.get("high_value_ratio_dem_ge_99"),
            "dem_min": dem_train.get("min"),
            "dem_max": dem_train.get("max"),
            "dem_mean": dem_train.get("mean"),
            "dem_has_100_value": array_has_value(dem, 100.0),
            "dem_100_count": array_value_count(dem, 100.0),
            "impervious_min": imperv_train.get("min"),
            "impervious_max": imperv_train.get("max"),
            "impervious_mean": imperv_train.get("mean"),
            "impervious_valid_domain_mean": imperv_valid_mean,
            "impervious_mostly_between_0_and_1": mostly_between_zero_one(imperv),
            "manhole_min": manhole_train.get("min"),
            "manhole_max": manhole_train.get("max"),
            "manhole_mean": manhole_train.get("mean"),
            "manhole_nonzero_ratio": manhole_train.get("zero_ratio") if manhole_train.get("zero_ratio") is None else 1.0 - manhole_train["zero_ratio"],
            "manhole_valid_domain_nonzero_ratio": manhole_valid_nonzero_ratio,
            "manhole_valid_domain_mean": manhole_valid_mean,
        }
        rows.append(row)
    return rows


def array_has_value(arr: np.ndarray | None, value: float) -> bool | None:
    if arr is None:
        return None
    return bool(np.any(np.isclose(arr.astype(np.float64, copy=False), value)))


def array_value_count(arr: np.ndarray | None, value: float) -> int | None:
    if arr is None:
        return None
    return int(np.sum(np.isclose(arr.astype(np.float64, copy=False), value)))


def mostly_between_zero_one(arr: np.ndarray | None) -> bool | None:
    if arr is None:
        return None
    values = arr.astype(np.float64, copy=False)
    finite = values[np.isfinite(values)]
    if finite.size == 0:
        return None
    return bool(np.mean((finite >= 0.0) & (finite <= 1.0)) >= 0.99)


def masked_mean(arr: np.ndarray | None, mask: np.ndarray | None) -> float | None:
    if arr is None or mask is None or arr.shape != mask.shape:
        return None
    values = arr.astype(np.float64, copy=False)
    selected = values[mask & np.isfinite(values)]
    if selected.size == 0:
        return None
    return safe_float(np.mean(selected))


def masked_nonzero_ratio(arr: np.ndarray | None, mask: np.ndarray | None) -> float | None:
    if arr is None or mask is None or arr.shape != mask.shape:
        return None
    values = arr.astype(np.float64, copy=False)
    selected = values[mask & np.isfinite(values)]
    if selected.size == 0:
        return None
    return safe_float(np.mean(selected != 0.0))


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


def build_summary(
    dataset_root: Path,
    channel_rows: list[dict[str, Any]],
    location_rows: list[dict[str, Any]],
    consistency_rows: list[dict[str, Any]],
    figure_paths: list[str],
) -> dict[str, Any]:
    expected_files = len(SPLITS) * len({row["location"] for row in channel_rows}) * len(CHANNELS)
    inspected_files = sum(bool(row["file_exists"]) for row in channel_rows)
    all_shape_compatible = all(bool(row["shape_is_128x128"]) for row in channel_rows)
    consistency_ok = all(bool(row["allclose"]) for row in consistency_rows)
    dem_rows = [row for row in channel_rows if row["channel_name"] == "absolute_DEM" and row["split"] == "train"]
    imperv_rows = [row for row in channel_rows if row["channel_name"] == "impervious" and row["split"] == "train"]
    manhole_rows = [row for row in channel_rows if row["channel_name"] == "manhole" and row["split"] == "train"]
    dem_has_high_invalid = any((row.get("candidate_high_invalid_mask_count") or 0) > 0 for row in dem_rows)
    dem_valid_mask_ok = all((row.get("candidate_valid_domain_ratio_dem_lt_99") or 0.0) > 0 for row in dem_rows)
    imperv_ok = all(row.get("min") is not None and row.get("max") is not None and row["min"] >= 0 and row["max"] <= 1 for row in imperv_rows)
    manhole_sparse = all((row.get("zero_ratio") or 0.0) > 0.80 for row in manhole_rows)
    level4_static_ready = all_shape_compatible and consistency_ok and dem_valid_mask_ok and imperv_ok and bool(manhole_rows)

    return {
        "dataset_root": str(dataset_root),
        "guardrail_note": (
            "Diagnostic-only inspection. No training, model architecture changes, loss changes, "
            "training config changes, seed123/seed202 runs, or sweeps were performed."
        ),
        "static_maps_inspected": inspected_files,
        "expected_static_map_files": expected_files,
        "all_expected_static_maps_found": inspected_files == expected_files,
        "all_static_maps_shape_128x128": all_shape_compatible,
        "train_test_consistency_status": "consistent_allclose" if consistency_ok else "inconsistent_or_missing",
        "dem_valid_domain_candidate_status": "supported_dem_lt_99" if dem_valid_mask_ok else "unsupported_or_incomplete",
        "dem_100_high_boundary_invalid_nodata_candidate": dem_has_high_invalid,
        "impervious_static_runoff_proxy_status": "usable" if imperv_ok else "needs_review",
        "manhole_sparse_drainage_proxy_status": "usable_sparse_indicator" if manhole_sparse else "needs_review",
        "level4_plus_static_map_aware_readiness": "supported" if level4_static_ready else "not_supported",
        "level5_status": "unsupported",
        "level5_reason": (
            "No aligned velocity/flux, boundary inflow/outflow, source-sink, dx/dy, or dt variables were found by this static-map inspection."
        ),
        "supports_next_domain_boundary_mask_script": bool(level4_static_ready and dem_has_high_invalid),
        "figure_paths": figure_paths,
        "location_summaries": location_rows,
    }


def write_markdown(path: Path, summary: dict[str, Any]) -> None:
    lines = [
        "# Phase 31 Static Map Inspection",
        "",
        "This diagnostic inspection reads recovered static maps and writes only Phase 31 analysis outputs. It does not train models, modify architecture, modify losses, modify training configs, run seed123/seed202, or perform sweeps.",
        "",
        "## Executive Summary",
        "",
        f"- Static maps inspected: {summary['static_maps_inspected']} / {summary['expected_static_map_files']}",
        f"- Shape-compatible with 128 x 128 flood maps: `{summary['all_static_maps_shape_128x128']}`",
        f"- Train/test geodata consistency: `{summary['train_test_consistency_status']}`",
        f"- DEM valid-domain candidate: `{summary['dem_valid_domain_candidate_status']}`",
        f"- Level 4+ static-map-aware readiness: `{summary['level4_plus_static_map_aware_readiness']}`",
        f"- Level 5 status: `{summary['level5_status']}`",
        "",
        "## Direct Answers",
        "",
        f"1. Static maps are shape-compatible with flood maps: `{summary['all_static_maps_shape_128x128']}`. The inspected static maps have the expected 128 x 128 grid shape.",
        f"2. Train/test geodata are consistent: `{summary['train_test_consistency_status']}`. Consistency here means numerically close for the same location/channel.",
        f"3. DEM is usable as a Level 4+ static elevation proxy: `{summary['dem_valid_domain_candidate_status'] == 'supported_dem_lt_99'}`. This supports DEM-aware proxy diagnostics, not SWE/PINN closure.",
        f"4. DEM=100.0 likely indicates an invalid, high-boundary, or no-data candidate: `{summary['dem_100_high_boundary_invalid_nodata_candidate']}`.",
        f"5. A candidate valid-domain mask can be constructed from `absolute_DEM < 99`: `{summary['dem_valid_domain_candidate_status'] == 'supported_dem_lt_99'}`.",
        f"6. Impervious and manhole maps are usable as static runoff/drainage proxies: impervious=`{summary['impervious_static_runoff_proxy_status']}`, manhole=`{summary['manhole_sparse_drainage_proxy_status']}`.",
        f"7. This supports a next domain/boundary mask construction script: `{summary['supports_next_domain_boundary_mask_script']}`.",
        "8. This does not change Level 5 status. Level 5 remains unsupported unless aligned velocity/flux, boundary/source-sink variables, dx/dy, and dt are found.",
        "",
        "## Location Summary",
        "",
        "| Location | DEM valid ratio | DEM=100 count | Impervious mean | Impervious valid mean | Manhole nonzero ratio | Train/test allclose |",
        "| --- | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for row in summary["location_summaries"]:
        lines.append(
            f"| {row['location']} | {row['dem_valid_ratio']} | {row['dem_100_count']} | "
            f"{row['impervious_mean']} | {row['impervious_valid_domain_mean']} | "
            f"{row['manhole_nonzero_ratio']} | `{row['train_test_all_channels_allclose']}` |"
        )
    lines.extend(
        [
            "",
            "## Classification",
            "",
            "Because DEM, impervious, and manhole maps are shape-compatible and consistent across train/test, Level 4+ static-map-aware diagnostics are supported. Level 5 remains unsupported by this inspection because hydrodynamic state, velocity/flux, boundary/source-sink, dx/dy, and dt variables were not found.",
            "",
        ]
    )
    if summary["figure_paths"]:
        lines.extend(["## Optional Figures", ""])
        for figure_path in summary["figure_paths"]:
            lines.append(f"- `{figure_path}`")
        lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def write_figures(
    output_dir: Path,
    arrays: dict[tuple[str, str, str], np.ndarray],
    location_rows: list[dict[str, Any]],
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
    for row in location_rows:
        location = row["location"]
        fig, axes = plt.subplots(1, 3, figsize=(10, 3.2), constrained_layout=True)
        for axis, channel in zip(axes, CHANNELS):
            arr = arrays.get(("train", location, channel))
            axis.set_title(channel)
            axis.axis("off")
            if arr is None:
                continue
            image = axis.imshow(arr, cmap="viridis")
            fig.colorbar(image, ax=axis, fraction=0.046, pad=0.04)
        path = figure_dir / f"static_map_{location}_preview.png"
        fig.suptitle(f"{location} static maps")
        fig.savefig(path, dpi=160)
        plt.close(fig)
        paths.append(display_path(path))
    return paths


def main() -> None:
    args = parse_args()
    output_dir = resolve_repo_path(args.output_dir)
    dataset_root = discover_dataset_root(args.inventory, args.dataset_root)

    channel_rows, arrays = inspect_channels(dataset_root)
    consistency_rows = train_test_consistency_rows(arrays, channel_rows)
    location_rows = location_summary_rows(channel_rows, consistency_rows, arrays)
    figure_paths = write_figures(output_dir, arrays, location_rows, args.skip_figures)
    summary = build_summary(dataset_root, channel_rows, location_rows, consistency_rows, figure_paths)

    write_csv(output_dir / "static_map_channel_summary.csv", channel_rows)
    write_csv(output_dir / "static_map_location_summary.csv", location_rows)
    write_csv(output_dir / "static_map_train_test_consistency.csv", consistency_rows)
    write_json(output_dir / "static_map_inspection_summary.json", summary)
    write_markdown(output_dir / "static_map_inspection.md", summary)

    print("Phase 31 static map inspection complete.")
    print(f"  static maps inspected: {summary['static_maps_inspected']} / {summary['expected_static_map_files']}")
    print(f"  train/test consistency status: {summary['train_test_consistency_status']}")
    print(f"  DEM valid-domain candidate status: {summary['dem_valid_domain_candidate_status']}")
    print(f"  Level 4+ static-map-aware readiness: {summary['level4_plus_static_map_aware_readiness']}")
    print(f"  Level 5 status: {summary['level5_status']}")
    print(f"  wrote: {display_path(output_dir / 'static_map_channel_summary.csv')}")
    print(f"  wrote: {display_path(output_dir / 'static_map_location_summary.csv')}")
    print(f"  wrote: {display_path(output_dir / 'static_map_train_test_consistency.csv')}")
    print(f"  wrote: {display_path(output_dir / 'static_map_inspection_summary.json')}")
    print(f"  wrote: {display_path(output_dir / 'static_map_inspection.md')}")


if __name__ == "__main__":
    main()
