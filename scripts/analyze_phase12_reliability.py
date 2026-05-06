from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import numpy as np


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import torch
from torch.utils.data import DataLoader

from datasets.urbanflood24_lite_adapter import UrbanFlood24LiteProcessDataset
from scripts.train_model import build_model, collate_samples, load_json
from trainers.train import move_batch_to_device


DEFAULT_RUNS = (
    "runs/phase10_margin_aware_boundary_band_seed123_40e",
    "runs/phase10_margin_aware_boundary_band_seed42_40e",
    "runs/phase10_margin_aware_boundary_band_seed202_40e",
)

DEPTH_BINS = (
    ("dry_or_near_dry", -math.inf, 0.05),
    ("shallow", 0.05, 0.15),
    ("moderate", 0.15, 0.30),
    ("deep", 0.30, math.inf),
)

BOUNDARY_BANDS = (
    "boundary_0px",
    "near_boundary_1_3px",
    "far_field_gt3px",
    "no_target_boundary_frame",
)


@dataclass
class BatchRecord:
    run_root: Path
    run_name: str
    seed: str
    batch_index: int
    prediction: np.ndarray
    target: np.ndarray
    metadata: list[dict[str, Any]]
    source: str


class MetricAccumulator:
    def __init__(self) -> None:
        self.count = 0
        self.sum_sq = 0.0
        self.sum_abs = 0.0
        self.sum_bias = 0.0
        self.intersection = 0
        self.union = 0
        self.class_error = 0
        self.pred_wet = 0
        self.target_wet = 0

    def update(self, prediction: np.ndarray, target: np.ndarray, wet_threshold: float) -> None:
        if prediction.size == 0:
            return
        error = prediction - target
        self.count += int(error.size)
        self.sum_sq += float(np.square(error, dtype=np.float64).sum())
        self.sum_abs += float(np.abs(error).sum())
        self.sum_bias += float(error.sum())

        pred_wet = prediction > wet_threshold
        target_wet = target > wet_threshold
        self.intersection += int(np.logical_and(pred_wet, target_wet).sum())
        self.union += int(np.logical_or(pred_wet, target_wet).sum())
        self.class_error += int(np.logical_xor(pred_wet, target_wet).sum())
        self.pred_wet += int(pred_wet.sum())
        self.target_wet += int(target_wet.sum())

    def as_row(self) -> dict[str, Any]:
        if self.count == 0:
            return {
                "count": 0,
                "rmse": "",
                "mae": "",
                "bias": "",
                "wet_dry_iou": "",
                "wet_dry_class_error_rate": "",
                "pred_wet_fraction": "",
                "target_wet_fraction": "",
            }
        return {
            "count": self.count,
            "rmse": math.sqrt(self.sum_sq / self.count),
            "mae": self.sum_abs / self.count,
            "bias": self.sum_bias / self.count,
            "wet_dry_iou": self.intersection / self.union if self.union > 0 else 1.0,
            "wet_dry_class_error_rate": self.class_error / self.count,
            "pred_wet_fraction": self.pred_wet / self.count,
            "target_wet_fraction": self.target_wet / self.count,
        }

    def merge(self, other: "MetricAccumulator") -> None:
        self.count += other.count
        self.sum_sq += other.sum_sq
        self.sum_abs += other.sum_abs
        self.sum_bias += other.sum_bias
        self.intersection += other.intersection
        self.union += other.union
        self.class_error += other.class_error
        self.pred_wet += other.pred_wet
        self.target_wet += other.target_wet


def display_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def infer_seed(run_root: Path) -> str:
    name = run_root.name
    for token in name.split("_"):
        if token.startswith("seed"):
            return token
    return "unknown"


def load_summary_metadata(summary_path: Path) -> list[dict[str, Any]]:
    data = json.loads(summary_path.read_text(encoding="utf-8"))
    metadata = data.get("metadata")
    if not isinstance(metadata, list):
        raise ValueError(f"Missing metadata list in {display_path(summary_path)}")
    return metadata


def iter_saved_batches(run_root: Path) -> Iterable[BatchRecord]:
    eval_dir = run_root / "evaluation_test"
    if not eval_dir.exists():
        return

    for batch_dir in sorted(eval_dir.glob("test_batch_*")):
        maps_path = batch_dir / "forecast_maps.npz"
        summary_path = batch_dir / "summary.json"
        if not maps_path.exists() or not summary_path.exists():
            continue
        try:
            batch_index = int(batch_dir.name.rsplit("_", 1)[1])
        except (IndexError, ValueError) as exc:
            raise ValueError(f"Cannot parse batch index from {display_path(batch_dir)}") from exc

        arrays = np.load(maps_path)
        if "prediction" not in arrays.files or "target" not in arrays.files:
            continue
        yield BatchRecord(
            run_root=run_root,
            run_name=run_root.name,
            seed=infer_seed(run_root),
            batch_index=batch_index,
            prediction=arrays["prediction"].astype(np.float64, copy=False),
            target=arrays["target"].astype(np.float64, copy=False),
            metadata=load_summary_metadata(summary_path),
            source="saved_evaluation_test_forecast_maps",
        )


@torch.no_grad()
def iter_recomputed_batches(run_root: Path, config_path: Path | None, device_arg: str | None) -> Iterable[BatchRecord]:
    checkpoint_path = run_root / "checkpoints" / "best.pt"
    if not checkpoint_path.exists():
        raise FileNotFoundError(f"Checkpoint not found: {display_path(checkpoint_path)}")

    device = torch.device(device_arg if device_arg and torch.cuda.is_available() else "cpu")
    checkpoint = torch.load(checkpoint_path, map_location=device)
    config = load_json(config_path) if config_path is not None else checkpoint.get("config")
    if not isinstance(config, dict):
        raise ValueError(f"Checkpoint has no embedded config: {display_path(checkpoint_path)}")

    model = build_model(config["model"]).to(device)
    model.load_state_dict(checkpoint["model_state"])
    model.eval()

    dataset = UrbanFlood24LiteProcessDataset.from_config(
        config["dataset"]["dataset_config_path"],
        split="test",
        debug=False,
    )
    dataloader = DataLoader(
        dataset,
        batch_size=config["optimization"]["eval_batch_size"],
        shuffle=False,
        num_workers=config["runtime"]["num_workers"],
        pin_memory=device.type == "cuda",
        collate_fn=collate_samples,
    )

    for batch_index, batch in enumerate(dataloader):
        batch = move_batch_to_device(batch, device)
        prediction = model(
            batch["past_flood"],
            batch["past_rainfall"],
            batch["future_rainfall"],
            batch["static_maps"],
        )
        target = batch["future_flood"]
        if prediction.shape != target.shape:
            raise ValueError(
                f"Prediction shape {tuple(prediction.shape)} does not match target shape {tuple(target.shape)}."
            )
        yield BatchRecord(
            run_root=run_root,
            run_name=run_root.name,
            seed=infer_seed(run_root),
            batch_index=batch_index,
            prediction=prediction.detach().cpu().numpy().astype(np.float64, copy=False),
            target=target.detach().cpu().numpy().astype(np.float64, copy=False),
            metadata=batch.get("metadata", []),
            source="checkpoint_recomputed_test_inference",
        )


def iter_run_batches(
    run_root: Path,
    *,
    config_path: Path | None,
    device: str | None,
    force_recompute: bool,
) -> Iterable[BatchRecord]:
    if not force_recompute:
        saved = list(iter_saved_batches(run_root))
        if saved:
            yield from saved
            return
    yield from iter_recomputed_batches(run_root, config_path, device)


def dilate_2d(mask: np.ndarray, radius: int) -> np.ndarray:
    if radius <= 0:
        return mask.astype(bool, copy=True)
    padded = np.pad(mask.astype(bool, copy=False), radius, mode="constant", constant_values=False)
    out = np.zeros_like(mask, dtype=bool)
    for dr in range(2 * radius + 1):
        for dc in range(2 * radius + 1):
            out |= padded[dr : dr + mask.shape[0], dc : dc + mask.shape[1]]
    return out


def boundary_distance_masks(target: np.ndarray, wet_threshold: float) -> dict[str, np.ndarray]:
    wet = np.squeeze(target > wet_threshold, axis=2)
    masks = {name: np.zeros_like(wet, dtype=bool) for name in BOUNDARY_BANDS}

    for sample_idx in range(wet.shape[0]):
        for step_idx in range(wet.shape[1]):
            frame = wet[sample_idx, step_idx]
            has_wet = bool(frame.any())
            has_dry = bool((~frame).any())
            if not has_wet or not has_dry:
                masks["no_target_boundary_frame"][sample_idx, step_idx] = True
                continue
            boundary = dilate_2d(frame, 1) & dilate_2d(~frame, 1)
            near_3 = dilate_2d(boundary, 3)
            masks["boundary_0px"][sample_idx, step_idx] = boundary
            masks["near_boundary_1_3px"][sample_idx, step_idx] = near_3 & ~boundary
            masks["far_field_gt3px"][sample_idx, step_idx] = ~near_3

    return {name: mask[:, :, None, :, :] for name, mask in masks.items()}


def update_group(
    groups: dict[tuple[Any, ...], MetricAccumulator],
    key: tuple[Any, ...],
    prediction: np.ndarray,
    target: np.ndarray,
    wet_threshold: float,
) -> None:
    groups.setdefault(key, MetricAccumulator()).update(prediction, target, wet_threshold)


def add_group_aggregates(groups: dict[tuple[Any, ...], MetricAccumulator], prefix_len: int) -> None:
    aggregate: dict[tuple[Any, ...], MetricAccumulator] = {}
    for key, metrics in list(groups.items()):
        aggregate_key = ("all", "aggregate", *key[prefix_len:])
        aggregate.setdefault(aggregate_key, MetricAccumulator()).merge(metrics)
    for key, metrics in aggregate.items():
        groups.setdefault(key, MetricAccumulator()).merge(metrics)


def scalar_metrics(prediction: np.ndarray, target: np.ndarray, wet_threshold: float) -> dict[str, Any]:
    acc = MetricAccumulator()
    acc.update(prediction, target, wet_threshold)
    return acc.as_row()


def scenario_record(record: BatchRecord, sample_idx: int, wet_threshold: float) -> dict[str, Any]:
    prediction = record.prediction[sample_idx : sample_idx + 1]
    target = record.target[sample_idx : sample_idx + 1]
    metrics = scalar_metrics(prediction, target, wet_threshold)
    metadata = record.metadata[sample_idx] if sample_idx < len(record.metadata) else {}
    error = prediction - target
    abs_error = np.abs(error)
    target_wet = target > wet_threshold

    row = {
        "seed": record.seed,
        "run_name": record.run_name,
        "run_root": display_path(record.run_root),
        "batch_index": record.batch_index,
        "sample_index": sample_idx,
        "split": metadata.get("split", ""),
        "location": metadata.get("location", ""),
        "event": metadata.get("event", ""),
        "start_idx": metadata.get("start_idx", ""),
        "input_steps": metadata.get("input_steps", ""),
        "pred_steps": metadata.get("pred_steps", ""),
        "alignment_mode": metadata.get("alignment_mode", ""),
        "target_max_depth": float(target.max()),
        "target_mean_depth": float(target.mean()),
        "target_wet_fraction": float(target_wet.mean()),
        "prediction_max_depth": float(prediction.max()),
        "prediction_mean_depth": float(prediction.mean()),
        "max_abs_error": float(abs_error.max()),
        "source": record.source,
    }
    row.update(metrics)
    return row


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def metric_rows(
    groups: dict[tuple[Any, ...], MetricAccumulator],
    key_fields: list[str],
    sort_key,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for key, metrics in sorted(groups.items(), key=lambda item: sort_key(item[0])):
        row = dict(zip(key_fields, key))
        row.update(metrics.as_row())
        rows.append(row)
    return rows


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    wet_threshold = float(args.wet_threshold)
    timestep_groups: dict[tuple[Any, ...], MetricAccumulator] = {}
    depth_groups: dict[tuple[Any, ...], MetricAccumulator] = {}
    boundary_groups: dict[tuple[Any, ...], MetricAccumulator] = {}
    scenario_rows: list[dict[str, Any]] = []
    overall_by_run: dict[tuple[str, str], MetricAccumulator] = {}
    sources: dict[str, int] = {}
    run_batch_counts: dict[str, int] = {}

    for run in args.runs:
        run_root = run.resolve()
        config_path = args.config if args.config is not None else None
        for batch_count, record in enumerate(
            iter_run_batches(
                run_root,
                config_path=config_path,
                device=args.device,
                force_recompute=args.force_recompute,
            ),
            start=1,
        ):
            if args.max_batches is not None and batch_count > args.max_batches:
                break
            sources[record.source] = sources.get(record.source, 0) + 1
            run_batch_counts[record.run_name] = run_batch_counts.get(record.run_name, 0) + 1

            update_group(
                overall_by_run,
                (record.seed, record.run_name),
                record.prediction,
                record.target,
                wet_threshold,
            )

            for step_idx in range(record.prediction.shape[1]):
                update_group(
                    timestep_groups,
                    (record.seed, record.run_name, step_idx),
                    record.prediction[:, step_idx : step_idx + 1],
                    record.target[:, step_idx : step_idx + 1],
                    wet_threshold,
                )

            for bin_name, lower, upper in DEPTH_BINS:
                if math.isinf(lower):
                    mask = record.target <= upper
                elif math.isinf(upper):
                    mask = record.target > lower
                else:
                    mask = (record.target > lower) & (record.target <= upper)
                update_group(
                    depth_groups,
                    (record.seed, record.run_name, bin_name, lower, upper),
                    record.prediction[mask],
                    record.target[mask],
                    wet_threshold,
                )

            boundary_masks = boundary_distance_masks(record.target, wet_threshold)
            for band_name, mask in boundary_masks.items():
                update_group(
                    boundary_groups,
                    (record.seed, record.run_name, band_name),
                    record.prediction[mask],
                    record.target[mask],
                    wet_threshold,
                )

            for sample_idx in range(record.prediction.shape[0]):
                scenario_rows.append(scenario_record(record, sample_idx, wet_threshold))

    add_group_aggregates(timestep_groups, prefix_len=2)
    add_group_aggregates(depth_groups, prefix_len=2)
    add_group_aggregates(boundary_groups, prefix_len=2)

    timestep_rows = metric_rows(
        timestep_groups,
        ["seed", "run_name", "forecast_step"],
        lambda key: (str(key[0] != "all"), str(key[0]), str(key[1]), int(key[2])),
    )
    depth_rows = metric_rows(
        depth_groups,
        ["seed", "run_name", "depth_bin", "lower_bound_exclusive", "upper_bound_inclusive"],
        lambda key: (str(key[0] != "all"), str(key[0]), str(key[1]), str(key[2])),
    )
    boundary_rows = metric_rows(
        boundary_groups,
        ["seed", "run_name", "boundary_distance_band"],
        lambda key: (str(key[0] != "all"), str(key[0]), str(key[1]), str(key[2])),
    )

    failure_rows = sorted(scenario_rows, key=lambda row: float(row["rmse"]), reverse=True)
    for rank, row in enumerate(failure_rows, start=1):
        row["failure_rank"] = rank

    timestep_path = output_dir / "timestep_metrics.csv"
    depth_path = output_dir / "depth_bin_metrics.csv"
    boundary_path = output_dir / "boundary_distance_metrics.csv"
    scenario_path = output_dir / "scenario_metrics.csv"
    failure_path = output_dir / "failure_cases.csv"

    metric_fieldnames = [
        "count",
        "rmse",
        "mae",
        "bias",
        "wet_dry_iou",
        "wet_dry_class_error_rate",
        "pred_wet_fraction",
        "target_wet_fraction",
    ]
    write_csv(timestep_path, timestep_rows, ["seed", "run_name", "forecast_step", *metric_fieldnames])
    write_csv(
        depth_path,
        depth_rows,
        [
            "seed",
            "run_name",
            "depth_bin",
            "lower_bound_exclusive",
            "upper_bound_inclusive",
            *metric_fieldnames,
        ],
    )
    write_csv(boundary_path, boundary_rows, ["seed", "run_name", "boundary_distance_band", *metric_fieldnames])

    scenario_fields = [
        "seed",
        "run_name",
        "run_root",
        "batch_index",
        "sample_index",
        "split",
        "location",
        "event",
        "start_idx",
        "input_steps",
        "pred_steps",
        "alignment_mode",
        "count",
        "rmse",
        "mae",
        "bias",
        "wet_dry_iou",
        "wet_dry_class_error_rate",
        "pred_wet_fraction",
        "target_wet_fraction",
        "target_max_depth",
        "target_mean_depth",
        "prediction_max_depth",
        "prediction_mean_depth",
        "max_abs_error",
        "source",
    ]
    write_csv(scenario_path, scenario_rows, scenario_fields)
    write_csv(failure_path, failure_rows, ["failure_rank", *scenario_fields])

    run_summaries = []
    aggregate_acc = MetricAccumulator()
    for (seed, run_name), metrics in sorted(overall_by_run.items()):
        aggregate_acc.merge(metrics)
        run_summaries.append({"seed": seed, "run_name": run_name, **metrics.as_row()})

    summary = {
        "phase": "Phase 12 Reliability / Applicability Diagnosis",
        "diagnostic_object": {
            "boundary_band_pixels": 1,
            "boundary_weight": 2.0,
            "runs": [display_path(path.resolve()) for path in args.runs],
            "split": "test",
            "wet_threshold": wet_threshold,
        },
        "constraints": {
            "retrained": False,
            "modified_model_architecture": False,
            "modified_training_code": False,
            "modified_phase10_loss": False,
            "opened_new_sweep": False,
        },
        "data_sources": sources,
        "run_batch_counts": run_batch_counts,
        "overall": aggregate_acc.as_row(),
        "runs": run_summaries,
        "top_failure_cases": failure_rows[: min(args.failure_top_k, len(failure_rows))],
        "outputs": {
            "summary_json": display_path(output_dir / "summary.json"),
            "timestep_metrics_csv": display_path(timestep_path),
            "depth_bin_metrics_csv": display_path(depth_path),
            "boundary_distance_metrics_csv": display_path(boundary_path),
            "scenario_metrics_csv": display_path(scenario_path),
            "failure_cases_csv": display_path(failure_path),
        },
    }
    (output_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Analyze Phase 12 reliability diagnostics for existing Phase 10 test-facing outputs. "
            "Uses saved evaluation_test forecast maps when available and falls back to checkpoint inference."
        )
    )
    parser.add_argument(
        "--runs",
        type=Path,
        nargs="+",
        default=[Path(run) for run in DEFAULT_RUNS],
        help="Run roots to analyze.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("analysis/phase12_reliability"),
        help="Directory for summary JSON and CSV outputs.",
    )
    parser.add_argument("--wet-threshold", type=float, default=0.05, help="Wet/dry threshold in water-depth units.")
    parser.add_argument(
        "--config",
        type=Path,
        default=None,
        help="Optional config for checkpoint fallback. Defaults to checkpoint-embedded config.",
    )
    parser.add_argument("--device", default=None, help="Optional device for checkpoint fallback, e.g. cuda or cpu.")
    parser.add_argument(
        "--force-recompute",
        action="store_true",
        help="Ignore saved forecast_maps.npz files and recompute predictions from checkpoints.",
    )
    parser.add_argument(
        "--max-batches",
        type=int,
        default=None,
        help="Optional smoke-test limiter. Omit for the full test-facing analysis.",
    )
    parser.add_argument(
        "--failure-top-k",
        type=int,
        default=10,
        help="Number of top failure rows embedded in summary.json.",
    )
    return parser.parse_args()


def main() -> None:
    summary = analyze(parse_args())
    print(json.dumps({"outputs": summary["outputs"], "data_sources": summary["data_sources"]}, indent=2))


if __name__ == "__main__":
    main()
