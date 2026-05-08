from __future__ import annotations

import argparse
import csv
import json
import math
import re
import warnings
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np

try:
    import pandas as pd
except ModuleNotFoundError:  # pragma: no cover - exercised only in lean runtime environments.
    pd = None


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = Path("analysis/phase15_reliability_screening")
DEFAULT_RUN_GLOB = "runs/phase10_margin_aware_boundary_band_seed*_40e/evaluation_test"
DEFAULT_PHASE12_DIR = Path("analysis/phase12_reliability")
DEFAULT_PHASE13_DIR = Path("analysis/phase13_failure_cases")
DEFAULT_PHASE14_DIR = Path("analysis/phase14_confidence")

PREDICTION_KEYS = ("prediction", "predictions", "pred", "forecast", "forecast_maps")
TARGET_KEYS = ("target", "targets", "y_true", "target_maps")
HIGH_INTENSITY_TOKENS = ("location2", "r300y", "p0.6_d3h", "p0.8_d3h", "p06_d3h", "p08_d3h")


@dataclass(frozen=True)
class MapRecord:
    run_root: Path
    eval_dir: Path
    maps_path: Path
    summary_path: Path | None
    run_name: str
    seed: str
    batch_index: int | None
    prediction: np.ndarray
    target: np.ndarray
    metadata: list[dict[str, Any]]
    prediction_key: str
    target_key: str


def display_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


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


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_metadata(summary_path: Path | None) -> list[dict[str, Any]]:
    if summary_path is None or not summary_path.exists():
        return []
    data = read_json(summary_path)
    metadata = data.get("metadata")
    if isinstance(metadata, list):
        return [item if isinstance(item, dict) else {} for item in metadata]
    warnings.warn(f"Metadata list unavailable in {display_path(summary_path)}.", stacklevel=2)
    return []


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


def normalize_map_array(array: np.ndarray, path: Path, key: str) -> np.ndarray:
    values = np.asarray(array, dtype=np.float64)
    if values.ndim == 5:
        return values
    if values.ndim == 4:
        return values[:, :, None, :, :]
    if values.ndim == 3:
        return values[:, None, None, :, :]
    if values.ndim == 2:
        return values[None, None, None, :, :]
    raise ValueError(
        f"Unsupported array shape for key {key!r} in {display_path(path)}: {values.shape}. "
        "Expected 2D, 3D, 4D, or 5D map data."
    )


def load_prediction_target(maps_path: Path) -> tuple[np.ndarray, np.ndarray, str, str]:
    with np.load(maps_path) as arrays:
        prediction_key = choose_key(arrays.files, PREDICTION_KEYS)
        target_key = choose_key(arrays.files, TARGET_KEYS)
        if prediction_key is None or target_key is None:
            raise ValueError(
                f"{display_path(maps_path)} does not contain recognizable prediction/target keys. "
                f"Available keys: {arrays.files}; prediction candidates: {PREDICTION_KEYS}; "
                f"target candidates: {TARGET_KEYS}."
            )
        prediction = normalize_map_array(arrays[prediction_key], maps_path, prediction_key)
        target = normalize_map_array(arrays[target_key], maps_path, target_key)
    if prediction.shape != target.shape:
        raise ValueError(
            f"Prediction shape {prediction.shape} does not match target shape {target.shape} "
            f"in {display_path(maps_path)}."
        )
    return prediction, target, prediction_key, target_key


def discover_map_files(run_glob: str) -> list[Path]:
    eval_dirs = sorted(path for path in REPO_ROOT.glob(run_glob) if path.is_dir())
    files: list[Path] = []
    for eval_dir in eval_dirs:
        files.extend(sorted(eval_dir.rglob("*.npz")))
    if not files:
        searched = display_path(REPO_ROOT / run_glob)
        raise FileNotFoundError(
            "No Phase 10 prediction map files were found. "
            f"Searched for .npz files under glob: {searched}. "
            "Run this from the repository root or pass --run-glob pointing to evaluation_test directories."
        )
    return files


def iter_map_records(run_glob: str) -> Iterable[MapRecord]:
    for maps_path in discover_map_files(run_glob):
        eval_dir = next((parent for parent in maps_path.parents if parent.name == "evaluation_test"), maps_path.parent)
        run_root = infer_run_root(eval_dir)
        summary_path = maps_path.parent / "summary.json"
        if not summary_path.exists():
            warnings.warn(f"Optional batch summary missing for {display_path(maps_path)}.", stacklevel=2)
            summary_path = None
        prediction, target, prediction_key, target_key = load_prediction_target(maps_path)
        yield MapRecord(
            run_root=run_root,
            eval_dir=eval_dir,
            maps_path=maps_path,
            summary_path=summary_path,
            run_name=run_root.name,
            seed=infer_seed(run_root),
            batch_index=parse_batch_index(maps_path),
            prediction=prediction,
            target=target,
            metadata=load_metadata(summary_path),
            prediction_key=prediction_key,
            target_key=target_key,
        )


def dilate_2d(mask: np.ndarray, radius: int) -> np.ndarray:
    if radius <= 0:
        return mask.astype(bool, copy=True)
    padded = np.pad(mask.astype(bool, copy=False), radius, mode="constant", constant_values=False)
    out = np.zeros_like(mask, dtype=bool)
    for dr in range(2 * radius + 1):
        for dc in range(2 * radius + 1):
            out |= padded[dr : dr + mask.shape[0], dc : dc + mask.shape[1]]
    return out


def boundary_mask(target: np.ndarray, wet_threshold: float) -> np.ndarray:
    target_wet = np.squeeze(target > wet_threshold, axis=2)
    masks = np.zeros_like(target_wet, dtype=bool)
    for sample_idx in range(target_wet.shape[0]):
        for step_idx in range(target_wet.shape[1]):
            frame = target_wet[sample_idx, step_idx]
            if not bool(frame.any()) or not bool((~frame).any()):
                continue
            masks[sample_idx, step_idx] = dilate_2d(frame, 1) & dilate_2d(~frame, 1)
    return masks[:, :, None, :, :]


def safe_ratio(numerator: float, denominator: float, default: float = 0.0) -> float:
    return numerator / denominator if denominator else default


def scenario_key(metadata: dict[str, Any], record: MapRecord, sample_idx: int) -> str:
    parts = [
        metadata.get("location", ""),
        metadata.get("event", ""),
        metadata.get("start_idx", ""),
    ]
    if any(str(part) for part in parts):
        return "|".join(str(part) for part in parts)
    return f"{record.run_name}|batch{record.batch_index}|sample{sample_idx}"


def high_intensity_metadata_component(text: str) -> tuple[float, str]:
    normalized = text.lower().replace("p0.", "p0")
    location2 = "location2" in normalized
    r300y = "r300y" in normalized
    p06 = "p06_d3h" in normalized or "p0.6_d3h" in text.lower()
    p08 = "p08_d3h" in normalized or "p0.8_d3h" in text.lower()
    if location2 and r300y and (p06 or p08):
        return 2.5, "location2_r300y_high_intensity"
    if location2 and (r300y or p06 or p08):
        return 1.5, "partial_location2_high_intensity"
    if any(token.replace("p0.", "p0") in normalized for token in HIGH_INTENSITY_TOKENS):
        return 0.5, "weak_high_intensity_token"
    return 0.0, ""


def linear_component(value: float, low: float, high: float, weight: float) -> float:
    if not math.isfinite(value) or value <= low:
        return 0.0
    if value >= high:
        return weight
    return weight * (value - low) / (high - low)


def category_from_score(score: float) -> str:
    if score >= 5.0:
        return "high-risk"
    if score >= 2.5:
        return "caution"
    return "reliable"


def write_rows_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames: list[str] = []
    for row in rows:
        for key in row:
            if key not in fieldnames:
                fieldnames.append(key)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def scenario_metrics(
    record: MapRecord,
    sample_idx: int,
    wet_threshold: float,
    low_margin_band: float,
    deep_underprediction_threshold: float,
) -> tuple[dict[str, Any], dict[str, np.ndarray]]:
    prediction = record.prediction[sample_idx : sample_idx + 1]
    target = record.target[sample_idx : sample_idx + 1]
    metadata = record.metadata[sample_idx] if sample_idx < len(record.metadata) else {}

    margin = np.abs(prediction - wet_threshold)
    pred_wet = prediction > wet_threshold
    target_wet = target > wet_threshold
    false_dry = target_wet & ~pred_wet
    underprediction = np.maximum(target - prediction, 0.0)
    deep_underprediction = underprediction >= deep_underprediction_threshold
    boundary = boundary_mask(target, wet_threshold)

    target_wet_count = int(target_wet.sum())
    pred_wet_count = int(pred_wet.sum())
    cell_count = int(target.size)
    low_margin_fraction = float((margin <= low_margin_band).mean())
    false_dry_rate = safe_ratio(float(false_dry.sum()), float(target_wet_count))
    wet_fraction_contraction = max(
        0.0,
        safe_ratio(float(target_wet_count - pred_wet_count), float(target_wet_count)),
    )
    target_peak_depth = float(target.max())
    prediction_peak_depth = float(prediction.max())
    peak_underprediction = max(0.0, target_peak_depth - prediction_peak_depth)
    mean_bias = float((prediction - target).mean())
    underprediction_bias = max(0.0, -mean_bias)
    boundary_target_wet = boundary & target_wet
    boundary_false_dry_rate = (
        safe_ratio(float((boundary & false_dry).sum()), float(boundary_target_wet.sum()))
        if bool(boundary_target_wet.any())
        else math.nan
    )

    metadata_text = " ".join(
        str(value)
        for value in [
            record.maps_path,
            record.run_name,
            metadata.get("location", ""),
            metadata.get("event", ""),
            metadata.get("start_idx", ""),
        ]
    )
    metadata_component, metadata_reason = high_intensity_metadata_component(metadata_text)

    components = {
        "low_margin_component": linear_component(low_margin_fraction, 0.05, 0.20, 1.5),
        "false_dry_component": linear_component(false_dry_rate, 0.10, 0.55, 2.0),
        "wet_fraction_contraction_component": linear_component(wet_fraction_contraction, 0.15, 0.65, 1.5),
        "peak_underprediction_component": linear_component(peak_underprediction, 0.25, 1.25, 1.5),
        "underprediction_bias_component": linear_component(underprediction_bias, 0.005, 0.035, 1.0),
        "boundary_component": linear_component(
            0.0 if math.isnan(boundary_false_dry_rate) else boundary_false_dry_rate,
            0.15,
            0.65,
            1.0,
        ),
        "high_intensity_location2_component": metadata_component,
        "cross_seed_disagreement_component": 0.0,
    }
    risk_score = float(sum(components.values()))

    row: dict[str, Any] = {
        "seed": record.seed,
        "run_name": record.run_name,
        "run_root": display_path(record.run_root),
        "maps_path": display_path(record.maps_path),
        "summary_path": display_path(record.summary_path) if record.summary_path else "",
        "batch_index": "" if record.batch_index is None else record.batch_index,
        "sample_index": sample_idx,
        "split": metadata.get("split", ""),
        "location": metadata.get("location", ""),
        "event": metadata.get("event", ""),
        "start_idx": metadata.get("start_idx", ""),
        "input_steps": metadata.get("input_steps", ""),
        "pred_steps": metadata.get("pred_steps", ""),
        "alignment_mode": metadata.get("alignment_mode", ""),
        "scenario_key": scenario_key(metadata, record, sample_idx),
        "cell_count": cell_count,
        "target_wet_fraction": float(target_wet.mean()),
        "pred_wet_fraction": float(pred_wet.mean()),
        "wet_fraction_contraction": float(wet_fraction_contraction),
        "low_margin_fraction": low_margin_fraction,
        "false_dry_rate": float(false_dry_rate),
        "false_dry_cell_fraction": float(false_dry.mean()),
        "target_peak_depth": target_peak_depth,
        "prediction_peak_depth": prediction_peak_depth,
        "peak_underprediction": float(peak_underprediction),
        "mean_bias": mean_bias,
        "underprediction_bias": float(underprediction_bias),
        "mae": float(np.abs(prediction - target).mean()),
        "rmse": float(np.sqrt(np.square(prediction - target).mean())),
        "boundary_available": bool(boundary.any()),
        "boundary_false_dry_rate": "" if math.isnan(boundary_false_dry_rate) else float(boundary_false_dry_rate),
        "high_intensity_reason": metadata_reason,
        **components,
        "risk_score": risk_score,
        "risk_category": category_from_score(risk_score),
    }
    masks = {
        "low_margin": np.squeeze(margin <= low_margin_band, axis=(0, 2)),
        "false_dry": np.squeeze(false_dry, axis=(0, 2)),
        "deep_underprediction": np.squeeze(deep_underprediction, axis=(0, 2)),
        "boundary": np.squeeze(boundary, axis=(0, 2)),
    }
    return row, masks


def add_cross_seed_disagreement(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not rows:
        return rows
    by_key: dict[str, list[tuple[int, dict[str, Any]]]] = {}
    for index, row in enumerate(rows):
        by_key.setdefault(str(row.get("scenario_key", "")), []).append((index, row))

    additions: dict[int, float] = {}
    for group in by_key.values():
        if len({str(row.get("seed", "")) for _, row in group}) < 2:
            continue
        pred_wet = [float(row["pred_wet_fraction"]) for _, row in group]
        peaks = [float(row["prediction_peak_depth"]) for _, row in group]
        spread = max(pred_wet) - min(pred_wet)
        peak_spread = max(peaks) - min(peaks)
        component = min(1.0, linear_component(spread, 0.02, 0.12, 0.6) + linear_component(peak_spread, 0.15, 0.75, 0.4))
        for index, _ in group:
            additions[index] = component
    if not additions:
        warnings.warn("Cross-seed disagreement component unavailable; no comparable multi-seed cases found.", stacklevel=2)
        return rows
    component_cols = [key for key in rows[0] if key.endswith("_component")]
    for index, component in additions.items():
        rows[index]["cross_seed_disagreement_component"] = component
        score = float(sum(float(rows[index].get(column, 0.0)) for column in component_cols))
        rows[index]["risk_score"] = score
        rows[index]["risk_category"] = category_from_score(score)
    return rows


def init_pixel_counts(shape: tuple[int, int]) -> dict[str, np.ndarray]:
    return {
        "observation_count": np.zeros(shape, dtype=np.int64),
        "low_margin_count": np.zeros(shape, dtype=np.int64),
        "false_dry_count": np.zeros(shape, dtype=np.int64),
        "deep_underprediction_count": np.zeros(shape, dtype=np.int64),
        "boundary_count": np.zeros(shape, dtype=np.int64),
        "high_risk_case_count": np.zeros(shape, dtype=np.int64),
    }


def update_pixel_counts(counts: dict[str, np.ndarray], masks: dict[str, np.ndarray], high_risk: bool) -> None:
    frame_count = masks["low_margin"].shape[0]
    counts["observation_count"] += frame_count
    counts["low_margin_count"] += masks["low_margin"].sum(axis=0)
    counts["false_dry_count"] += masks["false_dry"].sum(axis=0)
    counts["deep_underprediction_count"] += masks["deep_underprediction"].sum(axis=0)
    counts["boundary_count"] += masks["boundary"].sum(axis=0)
    if high_risk:
        combined = masks["false_dry"] | masks["deep_underprediction"] | masks["low_margin"]
        counts["high_risk_case_count"] += combined.sum(axis=0)


def pixel_summary_rows(counts: dict[str, np.ndarray]) -> list[dict[str, Any]]:
    observations = np.maximum(counts["observation_count"], 1)
    rows = []
    height, width = counts["observation_count"].shape
    for row in range(height):
        for col in range(width):
            rows.append(
                {
                    "row": row,
                    "col": col,
                    "observation_count": int(counts["observation_count"][row, col]),
                    "low_margin_count": int(counts["low_margin_count"][row, col]),
                    "false_dry_count": int(counts["false_dry_count"][row, col]),
                    "deep_underprediction_count": int(counts["deep_underprediction_count"][row, col]),
                    "boundary_count": int(counts["boundary_count"][row, col]),
                    "high_risk_case_count": int(counts["high_risk_case_count"][row, col]),
                    "low_margin_fraction": float(counts["low_margin_count"][row, col] / observations[row, col]),
                    "false_dry_fraction": float(counts["false_dry_count"][row, col] / observations[row, col]),
                    "deep_underprediction_fraction": float(
                        counts["deep_underprediction_count"][row, col] / observations[row, col]
                    ),
                    "boundary_fraction": float(counts["boundary_count"][row, col] / observations[row, col]),
                    "high_risk_case_fraction": float(counts["high_risk_case_count"][row, col] / observations[row, col]),
                }
            )
    return rows


def save_risk_map_example(
    output_dir: Path,
    scenario_rows: list[dict[str, Any]],
    scenario_masks: list[dict[str, Any]],
    dpi: int,
) -> str | None:
    if not scenario_rows or not scenario_masks:
        return None
    top_index = int(max(range(len(scenario_rows)), key=lambda index: float(scenario_rows[index]["risk_score"])))
    item = next((entry for entry in scenario_masks if entry["index"] == top_index), None)
    if item is None:
        return None
    masks = item["masks"]
    low_margin = masks["low_margin"].mean(axis=0)
    false_dry = masks["false_dry"].mean(axis=0)
    deep_under = masks["deep_underprediction"].mean(axis=0)
    boundary = masks["boundary"].mean(axis=0)

    fig, axes = plt.subplots(2, 2, figsize=(9, 8))
    panels = [
        (low_margin, "Low-margin pixel frequency", "viridis"),
        (false_dry, "False-dry pixel frequency", "magma"),
        (deep_under, "Deep-underprediction frequency", "inferno"),
        (boundary, "Boundary-zone frequency", "cividis"),
    ]
    for ax, (values, title, cmap) in zip(axes.ravel(), panels):
        image = ax.imshow(values, cmap=cmap, vmin=0.0, vmax=max(float(values.max()), 1.0e-12))
        ax.set_title(title)
        ax.set_xticks([])
        ax.set_yticks([])
        fig.colorbar(image, ax=ax, fraction=0.046, pad=0.04)
    fig.suptitle(f"Pixel Risk Example: {item['label']}", fontsize=11)
    fig.tight_layout()
    path = output_dir / "figures" / "pixel_risk_map_example.png"
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=dpi, bbox_inches="tight")
    plt.close(fig)
    return display_path(path)


def make_figures(output_dir: Path, scenario_rows: list[dict[str, Any]], pixel_rows: list[dict[str, Any]], dpi: int) -> list[str]:
    figures_dir = output_dir / "figures"
    figures_dir.mkdir(parents=True, exist_ok=True)
    figures: list[str] = []

    fig, ax = plt.subplots(figsize=(7, 4))
    ax.hist([float(row["risk_score"]) for row in scenario_rows], bins=12, color="#4c78a8", edgecolor="white")
    ax.axvline(2.5, color="#f58518", linestyle="--", linewidth=1.2, label="caution threshold")
    ax.axvline(5.0, color="#e45756", linestyle="--", linewidth=1.2, label="high-risk threshold")
    ax.set_title("Scenario Risk Score Distribution")
    ax.set_xlabel("Risk score")
    ax.set_ylabel("Scenario count")
    ax.legend(frameon=False)
    fig.tight_layout()
    path = figures_dir / "scenario_risk_score_distribution.png"
    fig.savefig(path, dpi=dpi)
    plt.close(fig)
    figures.append(display_path(path))

    category_order = ["reliable", "caution", "high-risk"]
    counts = {category: 0 for category in category_order}
    for row in scenario_rows:
        counts[str(row["risk_category"])] = counts.get(str(row["risk_category"]), 0) + 1
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(category_order, [counts[category] for category in category_order], color=["#54a24b", "#f58518", "#e45756"])
    ax.set_title("Scenario Risk Category Counts")
    ax.set_ylabel("Scenario count")
    fig.tight_layout()
    path = figures_dir / "scenario_risk_category_counts.png"
    fig.savefig(path, dpi=dpi)
    plt.close(fig)
    figures.append(display_path(path))

    component_cols = [key for key in scenario_rows[0] if key.endswith("_component")]
    top_rows = sorted(scenario_rows, key=lambda row: float(row["risk_score"]), reverse=True)[:30]
    heatmap_data = np.array([[float(row.get(column, 0.0)) for column in component_cols] for row in top_rows])
    fig, ax = plt.subplots(figsize=(10, 6))
    image = ax.imshow(heatmap_data, aspect="auto", cmap="YlOrRd", vmin=0.0)
    ax.set_title("Top Scenario Risk Components")
    ax.set_xlabel("Risk component")
    ax.set_ylabel("Top scenarios by score")
    ax.set_xticks(np.arange(len(component_cols)))
    ax.set_xticklabels([name.replace("_component", "") for name in component_cols], rotation=35, ha="right")
    ax.set_yticks([])
    fig.colorbar(image, ax=ax, label="Component score")
    fig.tight_layout()
    path = figures_dir / "risk_component_heatmap.png"
    fig.savefig(path, dpi=dpi, bbox_inches="tight")
    plt.close(fig)
    figures.append(display_path(path))

    if pixel_rows:
        height = max(int(row["row"]) for row in pixel_rows) + 1
        width = max(int(row["col"]) for row in pixel_rows) + 1
        values = np.zeros((height, width), dtype=np.float64)
        for row in pixel_rows:
            values[int(row["row"]), int(row["col"])] = float(row["false_dry_fraction"])
        fig, ax = plt.subplots(figsize=(6, 5))
        image = ax.imshow(values, cmap="magma", vmin=0.0)
        ax.set_title("Repeated False-Dry Pixel Risk")
        ax.set_xticks([])
        ax.set_yticks([])
        fig.colorbar(image, ax=ax, label="Fraction")
        fig.tight_layout()
        path = figures_dir / "repeated_false_dry_pixel_risk.png"
        fig.savefig(path, dpi=dpi)
        plt.close(fig)
        figures.append(display_path(path))

    return figures


def read_optional_input_counts() -> dict[str, Any]:
    inputs = {}
    for name, path in {
        "phase12_reliability_dir": DEFAULT_PHASE12_DIR,
        "phase13_failure_cases_dir": DEFAULT_PHASE13_DIR,
        "phase14_confidence_dir": DEFAULT_PHASE14_DIR,
    }.items():
        inputs[name] = {
            "path": display_path(path),
            "available": path.exists(),
            "csv_files": sorted(child.name for child in path.glob("*.csv")) if path.exists() else [],
            "summary_json_available": (path / "summary.json").exists(),
        }
        if not path.exists():
            warnings.warn(f"Optional diagnostic directory unavailable: {display_path(path)}.", stacklevel=2)
    return inputs


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "figures").mkdir(parents=True, exist_ok=True)

    scenario_rows: list[dict[str, Any]] = []
    scenario_masks: list[dict[str, Any]] = []
    map_files_loaded = 0
    map_key_usage: dict[str, int] = {}

    for record in iter_map_records(args.run_glob):
        map_files_loaded += 1
        map_key_usage[f"{record.prediction_key}->{record.target_key}"] = (
            map_key_usage.get(f"{record.prediction_key}->{record.target_key}", 0) + 1
        )
        for sample_idx in range(record.prediction.shape[0]):
            row, masks = scenario_metrics(
                record,
                sample_idx,
                args.wet_threshold,
                args.low_margin_band,
                args.deep_underprediction_threshold,
            )
            scenario_rows.append(row)
            scenario_masks.append(
                {
                    "index": len(scenario_rows) - 1,
                    "masks": masks,
                    "label": f"{row['seed']} {row.get('location')} {row.get('event')} start {row.get('start_idx')}",
                }
            )

    if not scenario_rows:
        raise RuntimeError("Map files were found, but no scenario rows could be built from their arrays.")

    if pd is None:
        warnings.warn(
            "pandas is not installed in the active environment; using the built-in CSV/table fallback. "
            "Install requirements.txt to use pandas-backed table handling.",
            stacklevel=2,
        )
    scenario_rows = add_cross_seed_disagreement(scenario_rows)

    first_mask = scenario_masks[0]["masks"]["low_margin"]
    pixel_counts = init_pixel_counts(first_mask.shape[1:])
    for item in scenario_masks:
        category = str(scenario_rows[item["index"]]["risk_category"])
        update_pixel_counts(pixel_counts, item["masks"], high_risk=category == "high-risk")
    pixel_rows = pixel_summary_rows(pixel_counts)

    high_risk_rows = sorted(
        [row for row in scenario_rows if row["risk_category"] == "high-risk"],
        key=lambda row: float(row["risk_score"]),
        reverse=True,
    )
    sorted_scenario_rows = sorted(scenario_rows, key=lambda row: float(row["risk_score"]), reverse=True)

    scenario_path = output_dir / "scenario_risk_scores.csv"
    pixel_path = output_dir / "pixel_risk_summary.csv"
    high_risk_path = output_dir / "high_risk_cases.csv"
    write_rows_csv(scenario_path, sorted_scenario_rows)
    write_rows_csv(pixel_path, pixel_rows)
    write_rows_csv(high_risk_path, high_risk_rows)

    figures = make_figures(output_dir, sorted_scenario_rows, pixel_rows, args.dpi)
    pixel_example = save_risk_map_example(output_dir, scenario_rows, scenario_masks, args.dpi)
    if pixel_example is not None:
        figures.append(pixel_example)
    else:
        warnings.warn("Pixel-level risk map example could not be generated.", stacklevel=2)

    phase13_like = [
        row
        for row in scenario_rows
        if "location2_r300y" in str(row.get("high_intensity_reason", ""))
    ]
    phase13_like_flagged = sum(1 for row in phase13_like if row["risk_category"] != "reliable")
    category_counts: dict[str, int] = {}
    for row in scenario_rows:
        category = str(row["risk_category"])
        category_counts[category] = category_counts.get(category, 0) + 1

    summary = {
        "phase": "Phase 15 Reliability Screening and Risk Mapping",
        "interpretation_note": (
            "Risk categories are deterministic screening labels derived from existing prediction artifacts. "
            "They are not calibrated probabilities or new model evaluations."
        ),
        "constraints": {
            "retrained": False,
            "evaluated_model_from_checkpoint": False,
            "modified_model_architecture": False,
            "modified_phase10_loss": False,
            "tuned_boundary_weight": False,
            "tuned_boundary_band_pixels": False,
            "opened_new_sweep": False,
        },
        "inputs": {
            "run_glob": args.run_glob,
            "map_files_loaded": map_files_loaded,
            "map_key_usage": map_key_usage,
            "pandas_available": pd is not None,
            "optional_diagnostics": read_optional_input_counts(),
        },
        "settings": {
            "wet_threshold": args.wet_threshold,
            "low_margin_band": args.low_margin_band,
            "deep_underprediction_threshold": args.deep_underprediction_threshold,
        },
        "scoring_rules": {
            "category_thresholds": {
                "reliable": "risk_score < 2.5",
                "caution": "2.5 <= risk_score < 5.0",
                "high-risk": "risk_score >= 5.0",
            },
            "components": {
                "low_margin_component": "linear 0 to 1.5 for low_margin_fraction 0.05 to 0.20",
                "false_dry_component": "linear 0 to 2.0 for false_dry_rate 0.10 to 0.55",
                "wet_fraction_contraction_component": "linear 0 to 1.5 for contraction 0.15 to 0.65",
                "peak_underprediction_component": "linear 0 to 1.5 for peak underprediction 0.25 to 1.25",
                "underprediction_bias_component": "linear 0 to 1.0 for negative mean bias 0.005 to 0.035",
                "boundary_component": "linear 0 to 1.0 for boundary false-dry rate 0.15 to 0.65",
                "high_intensity_location2_component": (
                    "2.5 for location2+r300y+(p0.6_d3h or p0.8_d3h), 1.5 for partial location2 intensity, "
                    "0.5 for weak high-intensity token"
                ),
                "cross_seed_disagreement_component": (
                    "optional 0 to 1.0 from comparable scenario spread in predicted wet fraction and peak depth"
                ),
            },
        },
        "row_counts": {
            "scenario_risk_scores": int(len(sorted_scenario_rows)),
            "pixel_risk_summary": int(len(pixel_rows)),
            "high_risk_cases": int(len(high_risk_rows)),
        },
        "category_counts": dict(sorted(category_counts.items())),
        "phase13_like_location2_check": {
            "matching_rows": int(len(phase13_like)),
            "flagged_caution_or_high_risk": phase13_like_flagged,
            "all_matching_rows_flagged": bool(len(phase13_like) > 0 and phase13_like_flagged == len(phase13_like)),
        },
        "outputs": {
            "summary_json": display_path(output_dir / "summary.json"),
            "scenario_risk_scores_csv": display_path(scenario_path),
            "pixel_risk_summary_csv": display_path(pixel_path),
            "high_risk_cases_csv": display_path(high_risk_path),
            "figures": figures,
        },
    }
    (output_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Screen Phase 10 saved prediction maps for Phase 15 scenario-level reliability risk and "
            "pixel-level risk summaries. This script only reads existing .npz evaluation artifacts; "
            "it does not train, tune, or run checkpoint inference."
        )
    )
    parser.add_argument(
        "--run-glob",
        default=DEFAULT_RUN_GLOB,
        help="Repository-root glob for Phase 10 evaluation_test directories.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Output directory for Phase 15 CSV, JSON, and figure artifacts.",
    )
    parser.add_argument("--wet-threshold", type=float, default=0.05, help="Wet/dry depth threshold.")
    parser.add_argument(
        "--low-margin-band",
        type=float,
        default=0.02,
        help="Pixels within this absolute distance of wet_threshold are low-margin pixels.",
    )
    parser.add_argument(
        "--deep-underprediction-threshold",
        type=float,
        default=0.10,
        help="Per-pixel target-prediction underprediction depth threshold for deep-underprediction maps.",
    )
    parser.add_argument("--dpi", type=int, default=180, help="Figure output DPI.")
    return parser.parse_args()


def main() -> None:
    summary = analyze(parse_args())
    print(json.dumps({"outputs": summary["outputs"], "row_counts": summary["row_counts"]}, indent=2))


if __name__ == "__main__":
    main()
