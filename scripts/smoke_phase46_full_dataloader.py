from __future__ import annotations

import argparse
import ast
import csv
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SCENARIO_INDEX = Path("analysis/phase45_full_dataset_indexing/scenario_index.csv")
DEFAULT_STATIC_INDEX = Path("analysis/phase45_full_dataset_indexing/static_geodata_index.csv")
DEFAULT_OUTPUT_DIR = Path("analysis/phase46_dataloader_smoke_downsample_tiling")

REQUIRED_SCENARIO_COLUMNS = (
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
)

REQUIRED_STATIC_COLUMNS = (
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
    "static_coverage_status",
)

SAMPLE_SHAPE_COLUMNS = (
    "sample_id",
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
    "dem_shape",
    "dem_dtype",
    "impervious_shape",
    "impervious_dtype",
    "manhole_shape",
    "manhole_dtype",
    "flood_window_shape",
    "flood_spatial_500x500",
    "static_spatial_500x500",
    "rainfall_length_supported",
    "success",
    "notes",
)

DOWNSAMPLE_COLUMNS = (
    "sample_id",
    "split",
    "location",
    "scenario",
    "target_size",
    "component",
    "method",
    "input_shape",
    "output_shape",
    "input_dtype",
    "output_dtype",
    "success",
    "notes",
)

TILE_COLUMNS = (
    "sample_id",
    "split",
    "location",
    "scenario",
    "tile_size",
    "origin_y",
    "origin_x",
    "flood_tile_shape",
    "static_tile_shape",
    "success",
    "notes",
)

BATCH_COLUMNS = (
    "batch_id",
    "sample_ids",
    "batch_size",
    "smoke_window",
    "downsample_size",
    "flood_window_batch_shape",
    "static_stack_batch_shape",
    "rainfall_summary_batch_shape",
    "success",
    "notes",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Phase 46 no-training dataloader smoke test over Phase 45 UrbanFlood24 "
            "full dataset indexes. Uses mmap reads and bounded slices only."
        )
    )
    parser.add_argument("--scenario-index", type=Path, default=DEFAULT_SCENARIO_INDEX)
    parser.add_argument("--static-index", type=Path, default=DEFAULT_STATIC_INDEX)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--smoke-window", type=int, default=2)
    parser.add_argument("--batch-size", type=int, default=2)
    return parser.parse_args()


def repo_path(path: Path) -> Path:
    path = path.expanduser()
    return path if path.is_absolute() else REPO_ROOT / path


def bool_text(value: bool) -> str:
    return str(bool(value)).lower()


def path_text(path: Path) -> str:
    return str(path.resolve()).replace("\\", "/")


def parse_shape(value: Any) -> tuple[int, ...] | None:
    if value in (None, ""):
        return None
    try:
        parsed = ast.literal_eval(str(value))
    except (SyntaxError, ValueError):
        return None
    if not isinstance(parsed, tuple):
        return None
    try:
        return tuple(int(item) for item in parsed)
    except (TypeError, ValueError):
        return None


def read_csv_rows(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    with path.open("r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        rows = [dict(row) for row in reader]
        return rows, list(reader.fieldnames or [])


def write_csv(path: Path, rows: list[dict[str, Any]], columns: tuple[str, ...]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        for row in rows:
            writer.writerow({column: row.get(column, "") for column in columns})


def count_values(rows: list[dict[str, Any]], column: str) -> dict[str, int]:
    counts = Counter(str(row.get(column, "")) for row in rows if str(row.get(column, "")) != "")
    return dict(sorted(counts.items()))


def count_by_location(rows: list[dict[str, Any]]) -> dict[str, int]:
    counts = Counter(f"{row.get('split', '')}/{row.get('location', '')}" for row in rows)
    return dict(sorted(counts.items()))


def path_exists(value: str) -> bool:
    return Path(value).exists()


def validate_indexes(
    scenario_index_path: Path,
    static_index_path: Path,
) -> tuple[list[dict[str, str]], list[dict[str, str]], dict[str, Any], list[str]]:
    warnings: list[str] = []
    validation: dict[str, Any] = {
        "scenario_index_loaded": False,
        "static_index_loaded": False,
        "scenario_required_columns_present": False,
        "static_required_columns_present": False,
        "scenario_referenced_paths_exist": False,
        "static_referenced_paths_exist": False,
        "scenario_count_total": 0,
        "static_index_rows": 0,
    }

    if not scenario_index_path.exists():
        warnings.append(f"missing_scenario_index:{path_text(scenario_index_path)}")
        return [], [], validation, warnings
    if not static_index_path.exists():
        warnings.append(f"missing_static_index:{path_text(static_index_path)}")
        return [], [], validation, warnings

    scenario_rows, scenario_columns = read_csv_rows(scenario_index_path)
    static_rows, static_columns = read_csv_rows(static_index_path)
    validation["scenario_index_loaded"] = True
    validation["static_index_loaded"] = True
    validation["scenario_count_total"] = len(scenario_rows)
    validation["static_index_rows"] = len(static_rows)

    missing_scenario_columns = sorted(set(REQUIRED_SCENARIO_COLUMNS) - set(scenario_columns))
    missing_static_columns = sorted(set(REQUIRED_STATIC_COLUMNS) - set(static_columns))
    validation["scenario_required_columns_present"] = not missing_scenario_columns
    validation["static_required_columns_present"] = not missing_static_columns
    if missing_scenario_columns:
        warnings.append(f"missing_scenario_columns:{','.join(missing_scenario_columns)}")
    if missing_static_columns:
        warnings.append(f"missing_static_columns:{','.join(missing_static_columns)}")

    if missing_scenario_columns or missing_static_columns:
        return scenario_rows, static_rows, validation, warnings

    scenario_path_columns = (
        "flood_path",
        "rainfall_path",
        "static_dem_path",
        "static_impervious_path",
        "static_manhole_path",
    )
    static_path_columns = ("absolute_dem_path", "impervious_path", "manhole_path")
    missing_scenario_paths = [
        f"{row.get('split')}/{row.get('location')}/{row.get('scenario')}:{column}"
        for row in scenario_rows
        for column in scenario_path_columns
        if not path_exists(str(row.get(column, "")))
    ]
    missing_static_paths = [
        f"{row.get('split')}/{row.get('location')}:{column}"
        for row in static_rows
        for column in static_path_columns
        if not path_exists(str(row.get(column, "")))
    ]
    validation["scenario_referenced_paths_exist"] = not missing_scenario_paths
    validation["static_referenced_paths_exist"] = not missing_static_paths
    if missing_scenario_paths:
        warnings.append(f"missing_scenario_referenced_paths:{len(missing_scenario_paths)}")
    if missing_static_paths:
        warnings.append(f"missing_static_referenced_paths:{len(missing_static_paths)}")

    return scenario_rows, static_rows, validation, warnings


def select_representative_samples(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    selected: list[dict[str, str]] = []
    selected_keys: set[tuple[str, str, str]] = set()

    def add_first(label: str, predicate: Any) -> None:
        for row in rows:
            key = (row["split"], row["location"], row["scenario"])
            if key in selected_keys:
                continue
            if predicate(row):
                item = dict(row)
                item["_selection_reason"] = label
                selected.append(item)
                selected_keys.add(key)
                return

    for split in ("train", "test"):
        add_first(f"cover_split_{split}", lambda row, split=split: row["split"] == split)
    for location in ("location1", "location2", "location3"):
        add_first(f"cover_location_{location}", lambda row, location=location: row["location"] == location)
    for scenario_type in ("design", "measured"):
        add_first(
            f"cover_scenario_type_{scenario_type}",
            lambda row, scenario_type=scenario_type: row["scenario_type"] == scenario_type,
        )
    add_first(
        "cover_flood_shape_360_1_500_500",
        lambda row: parse_shape(row.get("flood_shape")) == (360, 1, 500, 500),
    )
    add_first(
        "cover_flood_shape_480_1_500_500",
        lambda row: parse_shape(row.get("flood_shape")) == (480, 1, 500, 500),
    )
    for rainfall_length in ("180", "360"):
        add_first(
            f"cover_rainfall_length_{rainfall_length}",
            lambda row, rainfall_length=rainfall_length: str(row.get("rainfall_length")) == rainfall_length,
        )

    return selected


def close_mmap(array: Any) -> None:
    mmap_obj = getattr(array, "_mmap", None)
    if mmap_obj is not None:
        mmap_obj.close()


def load_mmap(path: str) -> np.ndarray:
    return np.load(Path(path), mmap_mode="r")


def sample_id(row: dict[str, Any], index: int) -> str:
    return f"{index:02d}_{row['split']}_{row['location']}_{row['scenario']}"


def run_shape_checks(samples: list[dict[str, str]], smoke_window: int) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for index, sample in enumerate(samples, start=1):
        arrays: list[Any] = []
        notes: list[str] = []
        success = False
        result: dict[str, Any] = {
            "sample_id": sample_id(sample, index),
            "split": sample["split"],
            "location": sample["location"],
            "scenario": sample["scenario"],
            "scenario_type": sample["scenario_type"],
            "flood_path": sample["flood_path"],
            "rainfall_path": sample["rainfall_path"],
        }
        try:
            flood = load_mmap(sample["flood_path"])
            rainfall = load_mmap(sample["rainfall_path"])
            dem = load_mmap(sample["static_dem_path"])
            impervious = load_mmap(sample["static_impervious_path"])
            manhole = load_mmap(sample["static_manhole_path"])
            arrays.extend([flood, rainfall, dem, impervious, manhole])

            flood_window = np.asarray(flood[:smoke_window])
            flood_spatial_ok = tuple(flood.shape[-2:]) == (500, 500)
            static_spatial_ok = all(tuple(array.shape) == (500, 500) for array in (dem, impervious, manhole))
            rainfall_length_ok = int(rainfall.shape[0]) in {180, 360}
            success = bool(
                len(flood.shape) == 4
                and flood_window.shape[0] <= smoke_window
                and flood_spatial_ok
                and static_spatial_ok
                and rainfall_length_ok
            )
            if not flood_spatial_ok:
                notes.append("flood_spatial_shape_not_500x500")
            if not static_spatial_ok:
                notes.append("static_shape_not_500x500")
            if not rainfall_length_ok:
                notes.append("rainfall_length_not_180_or_360")

            result.update(
                {
                    "flood_shape": str(tuple(int(dim) for dim in flood.shape)),
                    "flood_dtype": str(flood.dtype),
                    "rainfall_shape": str(tuple(int(dim) for dim in rainfall.shape)),
                    "rainfall_dtype": str(rainfall.dtype),
                    "rainfall_length": int(rainfall.shape[0]),
                    "dem_shape": str(tuple(int(dim) for dim in dem.shape)),
                    "dem_dtype": str(dem.dtype),
                    "impervious_shape": str(tuple(int(dim) for dim in impervious.shape)),
                    "impervious_dtype": str(impervious.dtype),
                    "manhole_shape": str(tuple(int(dim) for dim in manhole.shape)),
                    "manhole_dtype": str(manhole.dtype),
                    "flood_window_shape": str(tuple(int(dim) for dim in flood_window.shape)),
                    "flood_spatial_500x500": success and flood_spatial_ok,
                    "static_spatial_500x500": success and static_spatial_ok,
                    "rainfall_length_supported": success and rainfall_length_ok,
                    "success": success,
                    "notes": "; ".join(notes),
                }
            )
        except Exception as exc:  # noqa: BLE001 - smoke output should preserve failures.
            result.update({"success": False, "notes": f"{type(exc).__name__}:{exc}"})
        finally:
            for array in arrays:
                close_mmap(array)
        rows.append(result)
    return rows


def interpolate_array(array: np.ndarray, target_size: int, is_static: bool) -> tuple[tuple[int, ...], str]:
    import torch
    import torch.nn.functional as functional

    tensor = torch.from_numpy(np.array(array, copy=True)).to(dtype=torch.float32)
    if is_static:
        tensor = tensor.unsqueeze(0)
    with torch.no_grad():
        resized = functional.interpolate(
            tensor,
            size=(target_size, target_size),
            mode="bilinear",
            align_corners=False,
        )
    if is_static:
        resized = resized.squeeze(0)
    return tuple(int(dim) for dim in resized.shape), str(resized.numpy().dtype)


def run_downsample_checks(
    samples: list[dict[str, str]],
    smoke_window: int,
    target_sizes: tuple[int, ...] = (128, 256),
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for index, sample in enumerate(samples, start=1):
        arrays: list[Any] = []
        sid = sample_id(sample, index)
        try:
            flood = load_mmap(sample["flood_path"])
            dem = load_mmap(sample["static_dem_path"])
            impervious = load_mmap(sample["static_impervious_path"])
            manhole = load_mmap(sample["static_manhole_path"])
            arrays.extend([flood, dem, impervious, manhole])
            flood_window = np.asarray(flood[:smoke_window])
            static_stack = np.stack(
                [
                    np.asarray(dem),
                    np.asarray(impervious),
                    np.asarray(manhole),
                ],
                axis=0,
            )
            for target_size in target_sizes:
                for component, input_array, is_static in (
                    ("flood_window", flood_window, False),
                    ("static_stack", static_stack, True),
                ):
                    result = {
                        "sample_id": sid,
                        "split": sample["split"],
                        "location": sample["location"],
                        "scenario": sample["scenario"],
                        "target_size": target_size,
                        "component": component,
                        "method": "torch.nn.functional.interpolate_bilinear",
                        "input_shape": str(tuple(int(dim) for dim in input_array.shape)),
                        "input_dtype": str(input_array.dtype),
                    }
                    try:
                        output_shape, output_dtype = interpolate_array(input_array, target_size, is_static)
                        expected_shape = (
                            (3, target_size, target_size)
                            if is_static
                            else (min(smoke_window, int(flood.shape[0])), 1, target_size, target_size)
                        )
                        success = output_shape == expected_shape
                        result.update(
                            {
                                "output_shape": str(output_shape),
                                "output_dtype": output_dtype,
                                "success": success,
                                "notes": "" if success else f"unexpected_output_shape_expected_{expected_shape}",
                            }
                        )
                    except Exception as exc:  # noqa: BLE001
                        result.update(
                            {
                                "output_shape": "",
                                "output_dtype": "",
                                "success": False,
                                "notes": f"{type(exc).__name__}:{exc}",
                            }
                        )
                    rows.append(result)
        except Exception as exc:  # noqa: BLE001
            for target_size in target_sizes:
                rows.append(
                    {
                        "sample_id": sid,
                        "split": sample["split"],
                        "location": sample["location"],
                        "scenario": sample["scenario"],
                        "target_size": target_size,
                        "component": "sample_open",
                        "method": "torch.nn.functional.interpolate_bilinear",
                        "success": False,
                        "notes": f"{type(exc).__name__}:{exc}",
                    }
                )
        finally:
            for array in arrays:
                close_mmap(array)
    return rows


def tile_origins(height: int, width: int, tile_size: int) -> list[tuple[int, int]]:
    if height < tile_size or width < tile_size:
        return []
    center_y = (height - tile_size) // 2
    center_x = (width - tile_size) // 2
    bottom_y = height - tile_size
    bottom_x = width - tile_size
    origins = [(0, 0), (center_y, center_x), (bottom_y, bottom_x)]
    deduped: list[tuple[int, int]] = []
    for origin in origins:
        if origin not in deduped:
            deduped.append(origin)
    return deduped


def run_tile_checks(samples: list[dict[str, str]], smoke_window: int, tile_size: int = 256) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for index, sample in enumerate(samples, start=1):
        arrays: list[Any] = []
        sid = sample_id(sample, index)
        try:
            flood = load_mmap(sample["flood_path"])
            dem = load_mmap(sample["static_dem_path"])
            impervious = load_mmap(sample["static_impervious_path"])
            manhole = load_mmap(sample["static_manhole_path"])
            arrays.extend([flood, dem, impervious, manhole])
            flood_window = np.asarray(flood[:smoke_window])
            static_stack = np.stack([np.asarray(dem), np.asarray(impervious), np.asarray(manhole)], axis=0)
            for origin_y, origin_x in tile_origins(flood_window.shape[-2], flood_window.shape[-1], tile_size):
                flood_tile = flood_window[
                    ...,
                    origin_y : origin_y + tile_size,
                    origin_x : origin_x + tile_size,
                ]
                static_tile = static_stack[
                    ...,
                    origin_y : origin_y + tile_size,
                    origin_x : origin_x + tile_size,
                ]
                expected_flood_shape = (min(smoke_window, int(flood.shape[0])), 1, tile_size, tile_size)
                expected_static_shape = (3, tile_size, tile_size)
                success = tuple(flood_tile.shape) == expected_flood_shape and tuple(static_tile.shape) == expected_static_shape
                rows.append(
                    {
                        "sample_id": sid,
                        "split": sample["split"],
                        "location": sample["location"],
                        "scenario": sample["scenario"],
                        "tile_size": tile_size,
                        "origin_y": origin_y,
                        "origin_x": origin_x,
                        "flood_tile_shape": str(tuple(int(dim) for dim in flood_tile.shape)),
                        "static_tile_shape": str(tuple(int(dim) for dim in static_tile.shape)),
                        "success": success,
                        "notes": "" if success else "unexpected_tile_shape",
                    }
                )
        except Exception as exc:  # noqa: BLE001
            rows.append(
                {
                    "sample_id": sid,
                    "split": sample["split"],
                    "location": sample["location"],
                    "scenario": sample["scenario"],
                    "tile_size": tile_size,
                    "success": False,
                    "notes": f"{type(exc).__name__}:{exc}",
                }
            )
        finally:
            for array in arrays:
                close_mmap(array)
    return rows


def run_batch_smoke_check(
    samples: list[dict[str, str]],
    smoke_window: int,
    batch_size: int,
    downsample_size: int = 128,
) -> list[dict[str, Any]]:
    selected = select_batch_samples(samples, batch_size)
    if len(selected) < batch_size:
        return [
            {
                "batch_id": "batch_001",
                "sample_ids": ",".join(sample_id(sample, index) for index, sample in enumerate(selected, start=1)),
                "batch_size": len(selected),
                "smoke_window": smoke_window,
                "downsample_size": downsample_size,
                "success": False,
                "notes": f"insufficient_samples_for_batch_size_{batch_size}",
            }
        ]

    flood_items: list[np.ndarray] = []
    static_items: list[np.ndarray] = []
    rainfall_summaries: list[np.ndarray] = []
    used_sample_ids: list[str] = []
    arrays: list[Any] = []
    try:
        for index, sample in enumerate(selected, start=1):
            flood = load_mmap(sample["flood_path"])
            rainfall = load_mmap(sample["rainfall_path"])
            dem = load_mmap(sample["static_dem_path"])
            impervious = load_mmap(sample["static_impervious_path"])
            manhole = load_mmap(sample["static_manhole_path"])
            arrays.extend([flood, rainfall, dem, impervious, manhole])

            flood_window = np.asarray(flood[:smoke_window])
            static_stack = np.stack([np.asarray(dem), np.asarray(impervious), np.asarray(manhole)], axis=0)
            flood_shape, _ = interpolate_array(flood_window, downsample_size, is_static=False)
            static_shape, _ = interpolate_array(static_stack, downsample_size, is_static=True)
            if flood_shape != (smoke_window, 1, downsample_size, downsample_size):
                raise ValueError(f"unexpected_flood_downsample_shape:{flood_shape}")
            if static_shape != (3, downsample_size, downsample_size):
                raise ValueError(f"unexpected_static_downsample_shape:{static_shape}")

            import torch
            import torch.nn.functional as functional

            with torch.no_grad():
                flood_tensor = torch.from_numpy(np.array(flood_window, copy=True)).to(dtype=torch.float32)
                flood_items.append(
                    functional.interpolate(
                        flood_tensor,
                        size=(downsample_size, downsample_size),
                        mode="bilinear",
                        align_corners=False,
                    ).numpy()
                )
                static_tensor = torch.from_numpy(np.array(static_stack, copy=True)).to(dtype=torch.float32).unsqueeze(0)
                static_items.append(
                    functional.interpolate(
                        static_tensor,
                        size=(downsample_size, downsample_size),
                        mode="bilinear",
                        align_corners=False,
                    )
                    .squeeze(0)
                    .numpy()
                )
            rainfall_prefix = np.asarray(rainfall[:smoke_window], dtype=np.float32)
            rainfall_summaries.append(
                np.asarray(
                    [
                        float(rainfall.shape[0]),
                        float(rainfall_prefix[0]) if rainfall_prefix.size else 0.0,
                        float(rainfall_prefix.mean()) if rainfall_prefix.size else 0.0,
                    ],
                    dtype=np.float32,
                )
            )
            used_sample_ids.append(sample_id(sample, index))

        flood_batch = np.stack(flood_items, axis=0)
        static_batch = np.stack(static_items, axis=0)
        rainfall_summary_batch = np.stack(rainfall_summaries, axis=0)
        success = (
            flood_batch.shape == (batch_size, smoke_window, 1, downsample_size, downsample_size)
            and static_batch.shape == (batch_size, 3, downsample_size, downsample_size)
            and rainfall_summary_batch.shape == (batch_size, 3)
        )
        return [
            {
                "batch_id": "batch_001",
                "sample_ids": ",".join(used_sample_ids),
                "batch_size": batch_size,
                "smoke_window": smoke_window,
                "downsample_size": downsample_size,
                "flood_window_batch_shape": str(tuple(int(dim) for dim in flood_batch.shape)),
                "static_stack_batch_shape": str(tuple(int(dim) for dim in static_batch.shape)),
                "rainfall_summary_batch_shape": str(tuple(int(dim) for dim in rainfall_summary_batch.shape)),
                "success": success,
                "notes": "" if success else "unexpected_batch_shape",
            }
        ]
    except Exception as exc:  # noqa: BLE001
        return [
            {
                "batch_id": "batch_001",
                "sample_ids": ",".join(used_sample_ids),
                "batch_size": len(used_sample_ids),
                "smoke_window": smoke_window,
                "downsample_size": downsample_size,
                "success": False,
                "notes": f"{type(exc).__name__}:{exc}",
            }
        ]
    finally:
        for array in arrays:
            close_mmap(array)


def select_batch_samples(samples: list[dict[str, str]], batch_size: int) -> list[dict[str, str]]:
    selected: list[dict[str, str]] = []
    selected_keys: set[tuple[str, str, str]] = set()

    def add_first(predicate: Any) -> None:
        if len(selected) >= batch_size:
            return
        for sample in samples:
            key = (sample["split"], sample["location"], sample["scenario"])
            if key in selected_keys:
                continue
            if predicate(sample):
                selected.append(sample)
                selected_keys.add(key)
                return

    add_first(lambda sample: parse_shape(sample.get("flood_shape")) == (360, 1, 500, 500) and str(sample.get("rainfall_length")) == "360")
    add_first(lambda sample: parse_shape(sample.get("flood_shape")) == (480, 1, 500, 500))
    add_first(lambda sample: str(sample.get("rainfall_length")) == "180")
    for sample in samples:
        add_first(lambda candidate, sample=sample: candidate is sample)

    return selected[:batch_size]


def all_success(rows: list[dict[str, Any]]) -> bool:
    return bool(rows) and all(str(row.get("success")) == "True" or row.get("success") is True for row in rows)


def count_target_success(rows: list[dict[str, Any]], target_size: int) -> bool:
    target_rows = [row for row in rows if row.get("target_size") == target_size]
    return all_success(target_rows)


def build_summary(
    scenario_index_path: Path,
    static_index_path: Path,
    output_dir: Path,
    scenario_rows: list[dict[str, str]],
    static_rows: list[dict[str, str]],
    validation: dict[str, Any],
    representative_samples: list[dict[str, str]],
    shape_rows: list[dict[str, Any]],
    downsample_rows: list[dict[str, Any]],
    tile_rows: list[dict[str, Any]],
    batch_rows: list[dict[str, Any]],
    warnings: list[str],
    smoke_window: int,
) -> dict[str, Any]:
    scenario_index_valid = bool(
        validation["scenario_index_loaded"]
        and validation["static_index_loaded"]
        and validation["scenario_required_columns_present"]
        and validation["static_required_columns_present"]
        and validation["scenario_referenced_paths_exist"]
        and validation["static_referenced_paths_exist"]
    )
    sample_shape_checks_passed = all_success(shape_rows)
    downsample_128_passed = count_target_success(downsample_rows, 128)
    downsample_256_passed = count_target_success(downsample_rows, 256)
    tile_checks_passed = all_success(tile_rows)
    batch_smoke_passed = all_success(batch_rows)
    memory_safe = bool(
        sample_shape_checks_passed
        and downsample_128_passed
        and downsample_256_passed
        and tile_checks_passed
        and batch_smoke_passed
    )

    if not scenario_index_valid:
        selected_decision = "dataloader_smoke_blocked_by_index_issue"
    elif not memory_safe:
        selected_decision = "dataloader_smoke_blocked_by_shape_or_memory_issue"
    elif warnings:
        selected_decision = "dataloader_smoke_passed_with_warnings"
    else:
        selected_decision = "dataloader_smoke_ready_for_downsample_baseline"

    return {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "input_indexes": {
            "scenario_index_csv": path_text(scenario_index_path),
            "static_geodata_index_csv": path_text(static_index_path),
        },
        "outputs": {
            "output_dir": path_text(output_dir),
            "dataloader_smoke_summary_json": path_text(output_dir / "dataloader_smoke_summary.json"),
            "dataloader_smoke_summary_md": path_text(output_dir / "dataloader_smoke_summary.md"),
            "sample_shape_checks_csv": path_text(output_dir / "sample_shape_checks.csv"),
            "downsample_feasibility_checks_csv": path_text(output_dir / "downsample_feasibility_checks.csv"),
            "tile_feasibility_checks_csv": path_text(output_dir / "tile_feasibility_checks.csv"),
            "batch_smoke_checks_csv": path_text(output_dir / "batch_smoke_checks.csv"),
            "memory_safety_notes_md": path_text(output_dir / "memory_safety_notes.md"),
        },
        "scenario_index_loaded": validation["scenario_index_loaded"],
        "static_index_loaded": validation["static_index_loaded"],
        "scenario_count_total": len(scenario_rows),
        "static_index_rows": len(static_rows),
        "scenario_count_by_split": count_values(scenario_rows, "split"),
        "scenario_count_by_location": count_by_location(scenario_rows),
        "scenario_type_counts": count_values(scenario_rows, "scenario_type"),
        "flood_shape_counts": count_values(scenario_rows, "flood_shape"),
        "rainfall_length_counts": count_values(scenario_rows, "rainfall_length"),
        "static_coverage_status_counts": count_values(static_rows, "static_coverage_status"),
        "representative_samples_count": len(representative_samples),
        "representative_selection_reasons": [
            {
                "sample_id": sample_id(sample, index),
                "selection_reason": sample.get("_selection_reason", ""),
                "split": sample["split"],
                "location": sample["location"],
                "scenario": sample["scenario"],
                "scenario_type": sample["scenario_type"],
                "flood_shape": sample["flood_shape"],
                "rainfall_length": sample["rainfall_length"],
            }
            for index, sample in enumerate(representative_samples, start=1)
        ],
        "smoke_window": smoke_window,
        "sample_shape_checks_passed": sample_shape_checks_passed,
        "downsample_128_passed": downsample_128_passed,
        "downsample_256_passed": downsample_256_passed,
        "tile_checks_passed": tile_checks_passed,
        "batch_smoke_passed": batch_smoke_passed,
        "memory_safe": memory_safe,
        "warning_count": len(warnings),
        "warnings": warnings,
        "selected_decision": selected_decision,
        "selected_decision_candidates": [
            "dataloader_smoke_ready_for_downsample_baseline",
            "dataloader_smoke_passed_with_warnings",
            "dataloader_smoke_blocked_by_shape_or_memory_issue",
            "dataloader_smoke_blocked_by_index_issue",
        ],
        "level4_plus_supported": True,
        "level5_supported": False,
        "training_authorized": False,
        "next_recommended_action": (
            "Review Phase 46 evidence, then prepare a separate Phase 47 downsample baseline plan "
            "before any training authorization."
        ),
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
        "# Phase 46 Dataloader Smoke Summary",
        "",
        "No training, seed runs, sweeps, loss/config/model edits, SWE residuals, or PINN components were executed.",
        "",
        "## Decision",
        "",
        f"- scenario_index_loaded: `{bool_text(summary['scenario_index_loaded'])}`",
        f"- static_index_loaded: `{bool_text(summary['static_index_loaded'])}`",
        f"- representative_samples_count: `{summary['representative_samples_count']}`",
        f"- sample_shape_checks_passed: `{bool_text(summary['sample_shape_checks_passed'])}`",
        f"- downsample_128_passed: `{bool_text(summary['downsample_128_passed'])}`",
        f"- downsample_256_passed: `{bool_text(summary['downsample_256_passed'])}`",
        f"- tile_checks_passed: `{bool_text(summary['tile_checks_passed'])}`",
        f"- batch_smoke_passed: `{bool_text(summary['batch_smoke_passed'])}`",
        f"- memory_safe: `{bool_text(summary['memory_safe'])}`",
        f"- selected_decision: `{summary['selected_decision']}`",
        f"- level4_plus_supported: `{bool_text(summary['level4_plus_supported'])}`",
        f"- level5_supported: `{bool_text(summary['level5_supported'])}`",
        f"- training_authorized: `{bool_text(summary['training_authorized'])}`",
        f"- next_recommended_action: `{summary['next_recommended_action']}`",
        "",
        "## Representative Samples",
        "",
    ]
    for item in summary["representative_selection_reasons"]:
        lines.append(
            "- "
            f"`{item['sample_id']}`: `{item['selection_reason']}`, "
            f"`{item['split']}/{item['location']}/{item['scenario']}`, "
            f"type `{item['scenario_type']}`, flood `{item['flood_shape']}`, rainfall length `{item['rainfall_length']}`"
        )
    lines.append("")
    lines.extend(markdown_counts("Scenario Count By Split", summary["scenario_count_by_split"]))
    lines.extend(markdown_counts("Scenario Count By Location", summary["scenario_count_by_location"]))
    lines.extend(markdown_counts("Scenario Type Counts", summary["scenario_type_counts"]))
    lines.extend(markdown_counts("Flood Shape Counts", summary["flood_shape_counts"]))
    lines.extend(markdown_counts("Rainfall Length Counts", summary["rainfall_length_counts"]))
    lines.extend(markdown_counts("Static Coverage Status Counts", summary["static_coverage_status_counts"]))
    if summary["warnings"]:
        lines.extend(["## Warnings", ""])
        lines.extend(f"- `{warning}`" for warning in summary["warnings"])
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def write_memory_safety_notes(path: Path, smoke_window: int) -> None:
    path.write_text(
        "\n".join(
            [
                "# Phase 46 Memory Safety Notes",
                "",
                "- The smoke script used `numpy.load(..., mmap_mode=\"r\")` for flood, rainfall, and static `.npy` access.",
                f"- Flood reads were bounded to the first `{smoke_window}` temporal frames per representative sample.",
                "- Full flood sequences were not materialized in memory.",
                "- No transformed training samples or downsampled datasets were written to disk.",
                "- Downsample checks used small in-memory slices only and wrote compact CSV metadata.",
                "- Tile checks extracted deterministic patches in memory only and did not write tiles to disk.",
                "- No training, model forward pass, optimizer, loss computation, seed run, or sweep was executed.",
                "- Variable full flood lengths 360 and 480 must be handled by future fixed-window sampling.",
                "- Variable rainfall lengths 180 and 360 must be handled by future alignment rules.",
                "- Phase 46 supports Level 4+ dataloader readiness evidence only; Level 5 support remains false.",
            ]
        ),
        encoding="utf-8",
    )


def main() -> None:
    args = parse_args()
    scenario_index_path = repo_path(args.scenario_index)
    static_index_path = repo_path(args.static_index)
    output_dir = repo_path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    scenario_rows, static_rows, validation, warnings = validate_indexes(scenario_index_path, static_index_path)
    index_valid = bool(
        validation["scenario_index_loaded"]
        and validation["static_index_loaded"]
        and validation["scenario_required_columns_present"]
        and validation["static_required_columns_present"]
        and validation["scenario_referenced_paths_exist"]
        and validation["static_referenced_paths_exist"]
    )

    representative_samples = select_representative_samples(scenario_rows) if index_valid else []
    shape_rows = run_shape_checks(representative_samples, args.smoke_window) if index_valid else []
    downsample_rows = run_downsample_checks(representative_samples, args.smoke_window) if index_valid else []
    tile_rows = run_tile_checks(representative_samples, args.smoke_window) if index_valid else []
    batch_rows = (
        run_batch_smoke_check(representative_samples, args.smoke_window, args.batch_size)
        if index_valid
        else []
    )

    write_csv(output_dir / "sample_shape_checks.csv", shape_rows, SAMPLE_SHAPE_COLUMNS)
    write_csv(output_dir / "downsample_feasibility_checks.csv", downsample_rows, DOWNSAMPLE_COLUMNS)
    write_csv(output_dir / "tile_feasibility_checks.csv", tile_rows, TILE_COLUMNS)
    write_csv(output_dir / "batch_smoke_checks.csv", batch_rows, BATCH_COLUMNS)
    write_memory_safety_notes(output_dir / "memory_safety_notes.md", args.smoke_window)

    summary = build_summary(
        scenario_index_path=scenario_index_path,
        static_index_path=static_index_path,
        output_dir=output_dir,
        scenario_rows=scenario_rows,
        static_rows=static_rows,
        validation=validation,
        representative_samples=representative_samples,
        shape_rows=shape_rows,
        downsample_rows=downsample_rows,
        tile_rows=tile_rows,
        batch_rows=batch_rows,
        warnings=warnings,
        smoke_window=args.smoke_window,
    )
    (output_dir / "dataloader_smoke_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8"
    )
    write_summary_md(output_dir / "dataloader_smoke_summary.md", summary)

    print(f"scenario_index_loaded={bool_text(summary['scenario_index_loaded'])}")
    print(f"static_index_loaded={bool_text(summary['static_index_loaded'])}")
    print(f"representative_samples_count={summary['representative_samples_count']}")
    print(f"downsample_128_passed={bool_text(summary['downsample_128_passed'])}")
    print(f"downsample_256_passed={bool_text(summary['downsample_256_passed'])}")
    print(f"tile_checks_passed={bool_text(summary['tile_checks_passed'])}")
    print(f"batch_smoke_passed={bool_text(summary['batch_smoke_passed'])}")
    print(f"selected_decision={summary['selected_decision']}")
    print(f"training_authorized={bool_text(summary['training_authorized'])}")


if __name__ == "__main__":
    main()
