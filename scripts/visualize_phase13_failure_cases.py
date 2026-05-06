from __future__ import annotations

import argparse
import csv
import json
import math
import re
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import BoundaryNorm, ListedColormap
from matplotlib.patches import Patch


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_FAILURE_CASES_CSV = REPO_ROOT / "analysis" / "phase12_reliability" / "failure_cases.csv"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "analysis" / "phase13_failure_cases"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate Phase 13 representative failure-case visual summaries from saved Phase 10 maps."
    )
    parser.add_argument(
        "--failure-cases-csv",
        type=Path,
        default=DEFAULT_FAILURE_CASES_CSV,
        help="Phase 12 failure-case ranking CSV.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory for Phase 13 outputs.",
    )
    parser.add_argument("--top-n", type=int, default=6, help="Number of top-ranked failure cases to visualize.")
    parser.add_argument(
        "--wet-threshold",
        type=float,
        default=0.05,
        help="Depth threshold used to classify wet cells.",
    )
    parser.add_argument(
        "--timestep",
        choices=("final", "worst"),
        default="final",
        help="Forecast timestep to visualize: final step or per-case worst mean absolute error step.",
    )
    parser.add_argument("--dpi", type=int, default=180, help="PNG output DPI.")
    return parser.parse_args()


def display_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise FileNotFoundError(f"Missing failure-case CSV: {display_path(path)}")
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv_rows(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames: list[str] = []
    for row in rows:
        for key in row:
            if key not in fieldnames:
                fieldnames.append(key)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def as_int(value: Any, field_name: str) -> int:
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Expected integer {field_name}, got {value!r}") from exc


def as_float(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return math.nan


def sort_failure_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    return sorted(rows, key=lambda row: as_int(row.get("failure_rank"), "failure_rank"))


def resolve_repo_path(path_text: str) -> Path:
    path = Path(path_text)
    if not path.is_absolute():
        path = REPO_ROOT / path
    return path


def batch_dir_for_case(row: dict[str, str]) -> Path:
    run_root_text = row.get("run_root") or str(Path("runs") / row["run_name"])
    run_root = resolve_repo_path(run_root_text)
    batch_index = as_int(row.get("batch_index"), "batch_index")
    return run_root / "evaluation_test" / f"test_batch_{batch_index:04d}"


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def require_case_files(row: dict[str, str]) -> tuple[Path, Path, Path]:
    batch_dir = batch_dir_for_case(row)
    maps_path = batch_dir / "forecast_maps.npz"
    summary_path = batch_dir / "summary.json"
    if not batch_dir.exists():
        raise FileNotFoundError(f"Missing batch directory: {display_path(batch_dir)}")
    if not maps_path.exists():
        raise FileNotFoundError(f"Missing forecast maps: {display_path(maps_path)}")
    if not summary_path.exists():
        raise FileNotFoundError(f"Missing batch summary: {display_path(summary_path)}")
    return batch_dir, maps_path, summary_path


def sample_metadata(summary: dict[str, Any], sample_index: int) -> dict[str, Any]:
    metadata = summary.get("metadata")
    if not isinstance(metadata, list):
        raise ValueError("summary.json does not contain a metadata list.")
    if sample_index < 0 or sample_index >= len(metadata):
        raise IndexError(f"Sample index {sample_index} is outside metadata length {len(metadata)}.")
    item = metadata[sample_index]
    if not isinstance(item, dict):
        raise ValueError(f"Metadata entry {sample_index} is not an object.")
    return item


def verify_metadata(row: dict[str, str], metadata: dict[str, Any], summary_path: Path) -> None:
    for field in ("split", "location", "event", "alignment_mode"):
        expected = row.get(field)
        actual = metadata.get(field)
        if expected not in (None, "") and str(actual) != str(expected):
            raise ValueError(
                f"Metadata mismatch in {display_path(summary_path)} sample {row.get('sample_index')}: "
                f"{field} expected {expected!r}, got {actual!r}."
            )
    for field in ("start_idx", "input_steps", "pred_steps"):
        expected = row.get(field)
        actual = metadata.get(field)
        if expected not in (None, "") and int(actual) != as_int(expected, field):
            raise ValueError(
                f"Metadata mismatch in {display_path(summary_path)} sample {row.get('sample_index')}: "
                f"{field} expected {expected!r}, got {actual!r}."
            )


def load_case_arrays(maps_path: Path, sample_index: int) -> tuple[np.ndarray, np.ndarray]:
    arrays = np.load(maps_path)
    if "prediction" not in arrays.files or "target" not in arrays.files:
        raise ValueError(f"{display_path(maps_path)} must contain prediction and target arrays.")
    prediction = arrays["prediction"]
    target = arrays["target"]
    if prediction.shape != target.shape:
        raise ValueError(
            f"Prediction shape {prediction.shape} does not match target shape {target.shape} in {display_path(maps_path)}."
        )
    if prediction.ndim != 5:
        raise ValueError(f"Expected arrays shaped [batch, time, channel, height, width], got {prediction.shape}.")
    if sample_index < 0 or sample_index >= prediction.shape[0]:
        raise IndexError(f"Sample index {sample_index} is outside batch size {prediction.shape[0]}.")
    return prediction[sample_index, :, 0].astype(np.float64), target[sample_index, :, 0].astype(np.float64)


def choose_timestep(prediction: np.ndarray, target: np.ndarray, mode: str) -> tuple[int, list[float]]:
    abs_error = np.abs(prediction - target)
    step_mae = abs_error.reshape(abs_error.shape[0], -1).mean(axis=1)
    if mode == "final":
        return prediction.shape[0] - 1, step_mae.astype(float).tolist()
    if mode == "worst":
        return int(np.argmax(step_mae)), step_mae.astype(float).tolist()
    raise ValueError(f"Unsupported timestep mode: {mode}")


def wet_dry_mismatch(prediction: np.ndarray, target: np.ndarray, wet_threshold: float) -> np.ndarray:
    pred_wet = prediction > wet_threshold
    target_wet = target > wet_threshold
    categories = np.zeros(target.shape, dtype=np.uint8)
    categories[np.logical_and(target_wet, pred_wet)] = 1
    categories[np.logical_and(~target_wet, pred_wet)] = 2
    categories[np.logical_and(target_wet, ~pred_wet)] = 3
    return categories


def slugify(value: str) -> str:
    value = value.replace("p0.", "p0")
    value = re.sub(r"[^A-Za-z0-9]+", "_", value)
    return value.strip("_").lower()


def figure_filename(row: dict[str, str], timestep_index: int, timestep_mode: str) -> str:
    rank = as_int(row.get("failure_rank"), "failure_rank")
    parts = [
        f"rank{rank:02d}",
        row.get("seed", "seed"),
        row.get("location", "location"),
        row.get("event", "event"),
        f"start{row.get('start_idx', 'na')}",
        f"t{timestep_index + 1:02d}",
        timestep_mode,
        "maps",
    ]
    return f"{slugify('_'.join(parts))}.png"


def plot_case(
    row: dict[str, str],
    prediction_step: np.ndarray,
    target_step: np.ndarray,
    timestep_index: int,
    timestep_mode: str,
    wet_threshold: float,
    output_path: Path,
    dpi: int,
) -> None:
    abs_error = np.abs(prediction_step - target_step)
    mismatch = wet_dry_mismatch(prediction_step, target_step, wet_threshold)

    depth_max = max(float(np.nanmax(target_step)), float(np.nanmax(prediction_step)), wet_threshold)
    error_max = max(float(np.nanmax(abs_error)), 1.0e-12)

    fig, axes = plt.subplots(2, 2, figsize=(10.5, 9.0))
    axes = axes.ravel()
    title = (
        f"Rank {row.get('failure_rank')} | {row.get('seed')} | {row.get('location')} | "
        f"{row.get('event')} | start {row.get('start_idx')} | step {timestep_index + 1} ({timestep_mode})"
    )
    fig.suptitle(title, fontsize=12)

    depth_kwargs = {"cmap": "viridis", "vmin": 0.0, "vmax": depth_max}
    target_im = axes[0].imshow(target_step, **depth_kwargs)
    axes[0].set_title("Target flood depth")
    pred_im = axes[1].imshow(prediction_step, **depth_kwargs)
    axes[1].set_title("Predicted flood depth")
    error_im = axes[2].imshow(abs_error, cmap="magma", vmin=0.0, vmax=error_max)
    axes[2].set_title("Absolute error")

    mismatch_cmap = ListedColormap(["#f2f2f2", "#1f78b4", "#ff9f1c", "#d62828"])
    mismatch_norm = BoundaryNorm([-0.5, 0.5, 1.5, 2.5, 3.5], mismatch_cmap.N)
    axes[3].imshow(mismatch, cmap=mismatch_cmap, norm=mismatch_norm)
    axes[3].set_title(f"Wet/dry mismatch (threshold {wet_threshold:g})")

    for ax in axes:
        ax.set_xticks([])
        ax.set_yticks([])

    depth_cbar = fig.colorbar(target_im, ax=axes[:2], fraction=0.046, pad=0.03)
    depth_cbar.set_label("Depth")
    error_cbar = fig.colorbar(error_im, ax=axes[2], fraction=0.046, pad=0.03)
    error_cbar.set_label("Absolute error")
    legend_handles = [
        Patch(facecolor="#f2f2f2", edgecolor="black", linewidth=0.3, label="true dry"),
        Patch(facecolor="#1f78b4", edgecolor="black", linewidth=0.3, label="true wet"),
        Patch(facecolor="#ff9f1c", edgecolor="black", linewidth=0.3, label="false wet"),
        Patch(facecolor="#d62828", edgecolor="black", linewidth=0.3, label="false dry"),
    ]
    axes[3].legend(handles=legend_handles, loc="lower center", bbox_to_anchor=(0.5, -0.18), ncol=2, frameon=False)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=dpi, bbox_inches="tight")
    plt.close(fig)


def summarize_step(prediction_step: np.ndarray, target_step: np.ndarray, wet_threshold: float) -> dict[str, Any]:
    error = prediction_step - target_step
    abs_error = np.abs(error)
    pred_wet = prediction_step > wet_threshold
    target_wet = target_step > wet_threshold
    union = np.logical_or(pred_wet, target_wet)
    intersection = np.logical_and(pred_wet, target_wet)
    false_wet = np.logical_and(~target_wet, pred_wet)
    false_dry = np.logical_and(target_wet, ~pred_wet)
    return {
        "selected_step_rmse": float(np.sqrt(np.mean(np.square(error)))),
        "selected_step_mae": float(np.mean(abs_error)),
        "selected_step_bias": float(np.mean(error)),
        "selected_step_max_abs_error": float(np.max(abs_error)),
        "selected_step_target_max_depth": float(np.max(target_step)),
        "selected_step_target_mean_depth": float(np.mean(target_step)),
        "selected_step_prediction_max_depth": float(np.max(prediction_step)),
        "selected_step_prediction_mean_depth": float(np.mean(prediction_step)),
        "selected_step_wet_dry_iou": float(intersection.sum() / union.sum()) if union.any() else 1.0,
        "selected_step_false_wet_fraction": float(false_wet.mean()),
        "selected_step_false_dry_fraction": float(false_dry.mean()),
        "selected_step_target_wet_fraction": float(target_wet.mean()),
        "selected_step_prediction_wet_fraction": float(pred_wet.mean()),
    }


def process_case(
    row: dict[str, str],
    output_dir: Path,
    timestep_mode: str,
    wet_threshold: float,
    dpi: int,
) -> dict[str, Any]:
    sample_index = as_int(row.get("sample_index"), "sample_index")
    batch_dir, maps_path, summary_path = require_case_files(row)
    summary = load_json(summary_path)
    metadata = sample_metadata(summary, sample_index)
    verify_metadata(row, metadata, summary_path)

    prediction, target = load_case_arrays(maps_path, sample_index)
    timestep_index, step_mae = choose_timestep(prediction, target, timestep_mode)
    prediction_step = prediction[timestep_index]
    target_step = target[timestep_index]

    figures_dir = output_dir / "figures"
    figure_path = figures_dir / figure_filename(row, timestep_index, timestep_mode)
    plot_case(
        row=row,
        prediction_step=prediction_step,
        target_step=target_step,
        timestep_index=timestep_index,
        timestep_mode=timestep_mode,
        wet_threshold=wet_threshold,
        output_path=figure_path,
        dpi=dpi,
    )

    selected_row: dict[str, Any] = dict(row)
    selected_row.update(
        {
            "batch_dir": display_path(batch_dir),
            "forecast_maps_path": display_path(maps_path),
            "summary_path": display_path(summary_path),
            "figure_path": display_path(figure_path),
            "selected_timestep_mode": timestep_mode,
            "selected_timestep_index": timestep_index,
            "selected_forecast_step": timestep_index + 1,
            "step_mae_series": json.dumps(step_mae),
        }
    )
    selected_row.update(summarize_step(prediction_step, target_step, wet_threshold))
    return selected_row


def write_summary(path: Path, args: argparse.Namespace, selected_rows: list[dict[str, Any]]) -> None:
    summary = {
        "phase": "phase13_failure_case_visual_summary",
        "failure_cases_csv": display_path(args.failure_cases_csv),
        "output_dir": display_path(args.output_dir),
        "top_n": args.top_n,
        "wet_threshold": args.wet_threshold,
        "timestep": args.timestep,
        "dpi": args.dpi,
        "selected_case_count": len(selected_rows),
        "figures": [row["figure_path"] for row in selected_rows],
        "cases": [
            {
                "failure_rank": as_int(row.get("failure_rank"), "failure_rank"),
                "seed": row.get("seed"),
                "location": row.get("location"),
                "event": row.get("event"),
                "start_idx": as_int(row.get("start_idx"), "start_idx"),
                "batch_index": as_int(row.get("batch_index"), "batch_index"),
                "sample_index": as_int(row.get("sample_index"), "sample_index"),
                "selected_forecast_step": row.get("selected_forecast_step"),
                "selected_step_rmse": row.get("selected_step_rmse"),
                "selected_step_mae": row.get("selected_step_mae"),
                "selected_step_bias": row.get("selected_step_bias"),
                "selected_step_wet_dry_iou": row.get("selected_step_wet_dry_iou"),
                "debug_summary": {
                    "target_mean": row.get("selected_step_target_mean_depth"),
                    "target_max": row.get("selected_step_target_max_depth"),
                    "pred_mean": row.get("selected_step_prediction_mean_depth"),
                    "pred_max": row.get("selected_step_prediction_max_depth"),
                    "abs_error_mean": row.get("selected_step_mae"),
                    "target_wet_fraction": row.get("selected_step_target_wet_fraction"),
                    "pred_wet_fraction": row.get("selected_step_prediction_wet_fraction"),
                },
                "figure_path": row.get("figure_path"),
            }
            for row in selected_rows
        ],
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(summary, indent=2), encoding="utf-8")


def main() -> None:
    args = parse_args()
    if args.top_n <= 0:
        raise ValueError("--top-n must be positive.")
    if args.wet_threshold < 0:
        raise ValueError("--wet-threshold must be non-negative.")

    rows = sort_failure_rows(read_csv_rows(args.failure_cases_csv))
    selected_source_rows = rows[: args.top_n]
    selected_rows = [
        process_case(
            row=row,
            output_dir=args.output_dir,
            timestep_mode=args.timestep,
            wet_threshold=args.wet_threshold,
            dpi=args.dpi,
        )
        for row in selected_source_rows
    ]

    selected_csv = args.output_dir / "selected_failure_cases.csv"
    summary_json = args.output_dir / "summary.json"
    write_csv_rows(selected_csv, selected_rows)
    write_summary(summary_json, args, selected_rows)

    print(f"Wrote {display_path(selected_csv)}")
    print(f"Wrote {display_path(summary_json)}")
    print(f"Generated {len(selected_rows)} figure(s) under {display_path(args.output_dir / 'figures')}")


if __name__ == "__main__":
    main()
