from __future__ import annotations

import argparse
import csv
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np


REPO_ROOT = Path(__file__).resolve().parents[1]

DEFAULT_RUNS = (
    "runs/phase10_margin_aware_boundary_band_seed123_40e",
    "runs/phase10_margin_aware_boundary_band_seed42_40e",
    "runs/phase10_margin_aware_boundary_band_seed202_40e",
)
DEFAULT_OUTPUT_DIR = Path("analysis/phase14_confidence")
DEFAULT_PHASE12_FAILURE_CASES = Path("analysis/phase12_reliability/failure_cases.csv")
DEFAULT_PHASE12_SCENARIO_METRICS = Path("analysis/phase12_reliability/scenario_metrics.csv")
DEFAULT_PHASE13_SUMMARY = Path("analysis/phase13_failure_cases/summary.json")

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


class MetricAccumulator:
    """Aggregates proxy bins against deterministic error outcomes."""

    def __init__(self) -> None:
        self.count = 0
        self.sum_sq = 0.0
        self.sum_abs = 0.0
        self.class_error = 0
        self.false_dry = 0
        self.false_wet = 0
        self.pred_wet = 0
        self.target_wet = 0
        self.margin_sum = 0.0
        self.margin_min = math.inf
        self.margin_max = -math.inf

    def update(
        self,
        prediction: np.ndarray,
        target: np.ndarray,
        wet_threshold: float,
        confidence_margin: np.ndarray | None = None,
    ) -> None:
        if prediction.size == 0:
            return

        prediction = np.asarray(prediction, dtype=np.float64)
        target = np.asarray(target, dtype=np.float64)
        error = prediction - target
        pred_wet = prediction > wet_threshold
        target_wet = target > wet_threshold
        false_dry = target_wet & ~pred_wet
        false_wet = ~target_wet & pred_wet

        self.count += int(error.size)
        self.sum_sq += float(np.square(error, dtype=np.float64).sum())
        self.sum_abs += float(np.abs(error).sum())
        self.class_error += int(np.logical_xor(pred_wet, target_wet).sum())
        self.false_dry += int(false_dry.sum())
        self.false_wet += int(false_wet.sum())
        self.pred_wet += int(pred_wet.sum())
        self.target_wet += int(target_wet.sum())

        if confidence_margin is None:
            confidence_margin = np.abs(prediction - wet_threshold)
        if confidence_margin.size:
            self.margin_sum += float(confidence_margin.sum())
            self.margin_min = min(self.margin_min, float(confidence_margin.min()))
            self.margin_max = max(self.margin_max, float(confidence_margin.max()))

    def merge(self, other: "MetricAccumulator") -> None:
        self.count += other.count
        self.sum_sq += other.sum_sq
        self.sum_abs += other.sum_abs
        self.class_error += other.class_error
        self.false_dry += other.false_dry
        self.false_wet += other.false_wet
        self.pred_wet += other.pred_wet
        self.target_wet += other.target_wet
        self.margin_sum += other.margin_sum
        self.margin_min = min(self.margin_min, other.margin_min)
        self.margin_max = max(self.margin_max, other.margin_max)

    def as_row(self) -> dict[str, Any]:
        target_dry = self.count - self.target_wet
        if self.count == 0:
            return {
                "cell_count": 0,
                "rmse": "",
                "mae": "",
                "wet_dry_class_error_rate": "",
                "false_dry_rate": "",
                "false_wet_rate": "",
                "false_dry_cell_fraction": "",
                "false_wet_cell_fraction": "",
                "pred_wet_fraction": "",
                "target_wet_fraction": "",
                "mean_confidence_margin": "",
                "min_confidence_margin": "",
                "max_confidence_margin": "",
            }
        return {
            "cell_count": self.count,
            "rmse": math.sqrt(self.sum_sq / self.count),
            "mae": self.sum_abs / self.count,
            "wet_dry_class_error_rate": self.class_error / self.count,
            "false_dry_rate": self.false_dry / self.target_wet if self.target_wet else 0.0,
            "false_wet_rate": self.false_wet / target_dry if target_dry else 0.0,
            "false_dry_cell_fraction": self.false_dry / self.count,
            "false_wet_cell_fraction": self.false_wet / self.count,
            "pred_wet_fraction": self.pred_wet / self.count,
            "target_wet_fraction": self.target_wet / self.count,
            "mean_confidence_margin": self.margin_sum / self.count,
            "min_confidence_margin": self.margin_min,
            "max_confidence_margin": self.margin_max,
        }


def display_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def infer_seed(run_root: Path) -> str:
    for token in run_root.name.split("_"):
        if token.startswith("seed"):
            return token
    return "unknown"


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def iter_saved_batches(run_root: Path) -> Iterable[BatchRecord]:
    eval_dir = run_root / "evaluation_test"
    if not eval_dir.exists():
        return

    for batch_dir in sorted(eval_dir.glob("test_batch_*")):
        maps_path = batch_dir / "forecast_maps.npz"
        summary_path = batch_dir / "summary.json"
        if not maps_path.exists() or not summary_path.exists():
            continue
        batch_index = int(batch_dir.name.rsplit("_", 1)[1])
        arrays = np.load(maps_path)
        if "prediction" not in arrays.files or "target" not in arrays.files:
            continue
        summary = read_json(summary_path)
        metadata = summary.get("metadata")
        if not isinstance(metadata, list):
            raise ValueError(f"Missing metadata list in {display_path(summary_path)}")
        prediction = arrays["prediction"].astype(np.float64, copy=False)
        target = arrays["target"].astype(np.float64, copy=False)
        if prediction.shape != target.shape:
            raise ValueError(f"Prediction/target shape mismatch in {display_path(maps_path)}")
        yield BatchRecord(
            run_root=run_root,
            run_name=run_root.name,
            seed=infer_seed(run_root),
            batch_index=batch_index,
            prediction=prediction,
            target=target,
            metadata=metadata,
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


def boundary_distance_masks(target: np.ndarray, wet_threshold: float) -> dict[str, np.ndarray]:
    wet = np.squeeze(target > wet_threshold, axis=2)
    masks = {name: np.zeros_like(wet, dtype=bool) for name in BOUNDARY_BANDS}

    for sample_idx in range(wet.shape[0]):
        for step_idx in range(wet.shape[1]):
            frame = wet[sample_idx, step_idx]
            if not bool(frame.any()) or not bool((~frame).any()):
                masks["no_target_boundary_frame"][sample_idx, step_idx] = True
                continue
            boundary = dilate_2d(frame, 1) & dilate_2d(~frame, 1)
            near_3 = dilate_2d(boundary, 3)
            masks["boundary_0px"][sample_idx, step_idx] = boundary
            masks["near_boundary_1_3px"][sample_idx, step_idx] = near_3 & ~boundary
            masks["far_field_gt3px"][sample_idx, step_idx] = ~near_3

    return {name: mask[:, :, None, :, :] for name, mask in masks.items()}


def parse_bins(bin_text: str) -> list[float]:
    bins = [float(part.strip()) for part in bin_text.split(",") if part.strip()]
    if len(bins) < 2:
        raise ValueError("--margin-bins must provide at least two comma-separated edges.")
    if bins != sorted(bins):
        raise ValueError("--margin-bins edges must be sorted ascending.")
    return bins


def margin_bin_label(lower: float, upper: float) -> str:
    return f"[{lower:g},{upper:g})"


def update_group(
    groups: dict[tuple[Any, ...], MetricAccumulator],
    key: tuple[Any, ...],
    prediction: np.ndarray,
    target: np.ndarray,
    wet_threshold: float,
    confidence_margin: np.ndarray | None = None,
) -> None:
    groups.setdefault(key, MetricAccumulator()).update(prediction, target, wet_threshold, confidence_margin)


def add_aggregate(groups: dict[tuple[Any, ...], MetricAccumulator], prefix_len: int) -> None:
    aggregate: dict[tuple[Any, ...], MetricAccumulator] = {}
    for key, metrics in list(groups.items()):
        aggregate_key = ("all", "aggregate", *key[prefix_len:])
        aggregate.setdefault(aggregate_key, MetricAccumulator()).merge(metrics)
    for key, metrics in aggregate.items():
        groups.setdefault(key, MetricAccumulator()).merge(metrics)


def metric_rows(groups: dict[tuple[Any, ...], MetricAccumulator], fields: list[str]) -> list[dict[str, Any]]:
    rows = []
    for key, metrics in sorted(groups.items(), key=lambda item: tuple(str(part) for part in item[0])):
        row = dict(zip(fields, key))
        row.update(metrics.as_row())
        rows.append(row)
    return rows


def scenario_key(metadata: dict[str, Any]) -> tuple[str, str, str]:
    return (str(metadata.get("location", "")), str(metadata.get("event", "")), str(metadata.get("start_idx", "")))


def scenario_key_text(key: tuple[str, str, str]) -> str:
    return "|".join(key)


def phase13_failure_keys(summary_path: Path) -> set[tuple[str, str, str]]:
    if not summary_path.exists():
        return set()
    data = read_json(summary_path)
    keys = set()
    for case in data.get("cases", []):
        if isinstance(case, dict):
            keys.add((str(case.get("location", "")), str(case.get("event", "")), str(case.get("start_idx", ""))))
    return keys


def high_error_keys(failure_rows: list[dict[str, str]], top_k: int = 10) -> set[tuple[str, str, str]]:
    keys = set()
    for row in failure_rows[:top_k]:
        keys.add((str(row.get("location", "")), str(row.get("event", "")), str(row.get("start_idx", ""))))
    return keys


def scalar_metrics(prediction: np.ndarray, target: np.ndarray, wet_threshold: float) -> dict[str, Any]:
    acc = MetricAccumulator()
    acc.update(prediction, target, wet_threshold)
    return acc.as_row()


def scenario_confidence_row(
    record: BatchRecord,
    sample_idx: int,
    wet_threshold: float,
    failure_keys: set[tuple[str, str, str]],
    top_failure_keys: set[tuple[str, str, str]],
) -> dict[str, Any]:
    prediction = record.prediction[sample_idx : sample_idx + 1]
    target = record.target[sample_idx : sample_idx + 1]
    margin = np.abs(prediction - wet_threshold)
    metadata = record.metadata[sample_idx] if sample_idx < len(record.metadata) else {}
    pred_wet = prediction > wet_threshold
    target_wet = target > wet_threshold
    false_dry = target_wet & ~pred_wet
    false_wet = ~target_wet & pred_wet
    key = scenario_key(metadata)
    metrics = scalar_metrics(prediction, target, wet_threshold)

    return {
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
        "scenario_key": scenario_key_text(key),
        "phase13_failure_case": key in failure_keys,
        "phase12_top_failure_scenario": key in top_failure_keys,
        "mean_confidence_margin": float(margin.mean()),
        "median_confidence_margin": float(np.median(margin)),
        "p10_confidence_margin": float(np.percentile(margin, 10)),
        "low_margin_fraction_lt_0_01": float((margin < 0.01).mean()),
        "low_margin_fraction_lt_0_02": float((margin < 0.02).mean()),
        "false_dry_mean_margin": float(margin[false_dry].mean()) if false_dry.any() else "",
        "false_wet_mean_margin": float(margin[false_wet].mean()) if false_wet.any() else "",
        "mismatch_mean_margin": float(margin[np.logical_xor(pred_wet, target_wet)].mean())
        if np.logical_xor(pred_wet, target_wet).any()
        else "",
        "target_max_depth": float(target.max()),
        "target_mean_depth": float(target.mean()),
        "prediction_max_depth": float(prediction.max()),
        "prediction_mean_depth": float(prediction.mean()),
        **metrics,
    }


def analyze_seed_disagreement(
    scenario_predictions: dict[tuple[str, str, str], dict[str, dict[str, Any]]],
    wet_threshold: float,
) -> list[dict[str, Any]]:
    rows = []
    for key, by_seed in sorted(scenario_predictions.items()):
        if len(by_seed) < 2:
            continue
        seed_names = sorted(by_seed)
        predictions = np.stack([by_seed[seed]["prediction"] for seed in seed_names], axis=0)
        target = by_seed[seed_names[0]]["target"]
        pred_std = np.std(predictions, axis=0)
        wet_votes = predictions > wet_threshold
        wet_disagree = wet_votes.any(axis=0) & ~wet_votes.all(axis=0)
        mean_prediction = predictions.mean(axis=0)
        metrics = scalar_metrics(mean_prediction, target, wet_threshold)
        per_seed_rmse = [
            math.sqrt(float(np.square(by_seed[seed]["prediction"] - target, dtype=np.float64).mean()))
            for seed in seed_names
        ]
        rows.append(
            {
                "scenario_key": scenario_key_text(key),
                "location": key[0],
                "event": key[1],
                "start_idx": key[2],
                "matched_seed_count": len(seed_names),
                "matched_seeds": ";".join(seed_names),
                "mean_prediction_std": float(pred_std.mean()),
                "max_prediction_std": float(pred_std.max()),
                "p95_prediction_std": float(np.percentile(pred_std, 95)),
                "wet_dry_disagreement_rate": float(wet_disagree.mean()),
                "mean_seed_rmse": float(np.mean(per_seed_rmse)),
                "max_seed_rmse": float(np.max(per_seed_rmse)),
                "target_max_depth": float(target.max()),
                "target_mean_depth": float(target.mean()),
                **metrics,
            }
        )
    return rows


def make_figures(
    output_dir: Path,
    margin_rows: list[dict[str, Any]],
    disagreement_rows: list[dict[str, Any]],
    dpi: int,
) -> list[str]:
    figures_dir = output_dir / "figures"
    figures_dir.mkdir(parents=True, exist_ok=True)
    figures = []

    aggregate_margin = [
        row
        for row in margin_rows
        if row["seed"] == "all" and row["run_name"] == "aggregate" and int(row["cell_count"]) > 0
    ]
    if aggregate_margin:
        labels = [str(row["margin_bin"]) for row in aggregate_margin]
        x = np.arange(len(labels))
        class_error = [float(row["wet_dry_class_error_rate"]) for row in aggregate_margin]
        false_dry = [float(row["false_dry_rate"]) for row in aggregate_margin]

        fig, ax = plt.subplots(figsize=(8, 4))
        ax.plot(x, class_error, marker="o", label="wet/dry class error")
        ax.plot(x, false_dry, marker="o", label="false-dry rate")
        ax.set_xticks(x)
        ax.set_xticklabels(labels, rotation=35, ha="right")
        ax.set_ylabel("Rate")
        ax.set_xlabel("Confidence-margin bin")
        ax.set_title("Confidence-margin proxy vs wet/dry error")
        ax.grid(alpha=0.25)
        ax.legend()
        fig.tight_layout()
        path = figures_dir / "confidence_margin_vs_wet_dry_error.png"
        fig.savefig(path, dpi=dpi)
        plt.close(fig)
        figures.append(display_path(path))

    if disagreement_rows:
        x = [float(row["mean_prediction_std"]) for row in disagreement_rows]
        y = [float(row["rmse"]) for row in disagreement_rows]
        c = [float(row["wet_dry_class_error_rate"]) for row in disagreement_rows]
        fig, ax = plt.subplots(figsize=(6, 4))
        scatter = ax.scatter(x, y, c=c, cmap="viridis", s=36)
        ax.set_xlabel("Mean prediction std across seeds")
        ax.set_ylabel("Scenario RMSE using mean prediction")
        ax.set_title("Seed disagreement proxy vs scenario error")
        ax.grid(alpha=0.25)
        fig.colorbar(scatter, ax=ax, label="wet/dry class error")
        fig.tight_layout()
        path = figures_dir / "seed_disagreement_vs_rmse.png"
        fig.savefig(path, dpi=dpi)
        plt.close(fig)
        figures.append(display_path(path))

    return figures


def summarize_proxy_relationships(
    margin_rows: list[dict[str, Any]],
    risk_rows: list[dict[str, Any]],
    disagreement_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    aggregate_margin = [
        row for row in margin_rows if row["seed"] == "all" and row["run_name"] == "aggregate" and row["cell_count"]
    ]
    low_margin = aggregate_margin[0] if aggregate_margin else None
    high_margin = aggregate_margin[-1] if aggregate_margin else None

    false_dry_rows = [
        row
        for row in risk_rows
        if row.get("risk_proxy_group") == "wet_dry_outcome" and row.get("risk_proxy_value") == "false_dry"
    ]
    correct_wet_rows = [
        row
        for row in risk_rows
        if row.get("risk_proxy_group") == "wet_dry_outcome" and row.get("risk_proxy_value") == "correct_wet"
    ]

    disagreement_rmse = [float(row["mean_seed_rmse"]) for row in disagreement_rows]
    disagreement_std = [float(row["mean_prediction_std"]) for row in disagreement_rows]
    corr = ""
    if len(disagreement_rmse) >= 2 and np.std(disagreement_rmse) > 0 and np.std(disagreement_std) > 0:
        corr = float(np.corrcoef(disagreement_std, disagreement_rmse)[0, 1])

    return {
        "interpretation_note": (
            "These diagnostics use confidence proxies, risk proxies, and disagreement proxies. "
            "They are not calibrated probabilistic uncertainty estimates."
        ),
        "lowest_margin_bin": low_margin,
        "highest_margin_bin": high_margin,
        "false_dry_proxy_rows": false_dry_rows,
        "correct_wet_proxy_rows": correct_wet_rows,
        "seed_disagreement_mean_std_vs_mean_seed_rmse_correlation": corr,
    }


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    wet_threshold = float(args.wet_threshold)
    margin_bins = parse_bins(args.margin_bins)

    phase12_failure_rows = read_csv_rows(args.phase12_failure_cases)
    phase12_scenario_rows = read_csv_rows(args.phase12_scenario_metrics)
    phase13_keys = phase13_failure_keys(args.phase13_summary)
    top_failure_keys = high_error_keys(phase12_failure_rows, top_k=10)

    margin_groups: dict[tuple[Any, ...], MetricAccumulator] = {}
    risk_groups: dict[tuple[Any, ...], MetricAccumulator] = {}
    scenario_rows: list[dict[str, Any]] = []
    scenario_predictions: dict[tuple[str, str, str], dict[str, dict[str, Any]]] = {}
    run_batch_counts: dict[str, int] = {}

    for run in args.runs:
        run_root = run.resolve()
        for batch_count, record in enumerate(iter_saved_batches(run_root), start=1):
            if args.max_batches is not None and batch_count > args.max_batches:
                break
            run_batch_counts[record.run_name] = run_batch_counts.get(record.run_name, 0) + 1
            confidence_margin = np.abs(record.prediction - wet_threshold)
            pred_wet = record.prediction > wet_threshold
            target_wet = record.target > wet_threshold

            for lower, upper in zip(margin_bins[:-1], margin_bins[1:]):
                if upper == margin_bins[-1]:
                    mask = (confidence_margin >= lower) & (confidence_margin <= upper)
                else:
                    mask = (confidence_margin >= lower) & (confidence_margin < upper)
                update_group(
                    margin_groups,
                    (record.seed, record.run_name, margin_bin_label(lower, upper), lower, upper),
                    record.prediction[mask],
                    record.target[mask],
                    wet_threshold,
                    confidence_margin[mask],
                )

            boundary_masks = boundary_distance_masks(record.target, wet_threshold)
            for band_name, mask in boundary_masks.items():
                update_group(
                    risk_groups,
                    (record.seed, record.run_name, "boundary_distance_band", band_name),
                    record.prediction[mask],
                    record.target[mask],
                    wet_threshold,
                    confidence_margin[mask],
                )

            for bin_name, lower, upper in DEPTH_BINS:
                if math.isinf(lower):
                    mask = record.target <= upper
                elif math.isinf(upper):
                    mask = record.target > lower
                else:
                    mask = (record.target > lower) & (record.target <= upper)
                update_group(
                    risk_groups,
                    (record.seed, record.run_name, "target_depth_bin", bin_name),
                    record.prediction[mask],
                    record.target[mask],
                    wet_threshold,
                    confidence_margin[mask],
                )

            outcome_masks = {
                "correct_dry": ~target_wet & ~pred_wet,
                "correct_wet": target_wet & pred_wet,
                "false_dry": target_wet & ~pred_wet,
                "false_wet": ~target_wet & pred_wet,
            }
            for outcome, mask in outcome_masks.items():
                update_group(
                    risk_groups,
                    (record.seed, record.run_name, "wet_dry_outcome", outcome),
                    record.prediction[mask],
                    record.target[mask],
                    wet_threshold,
                    confidence_margin[mask],
                )

            for sample_idx in range(record.prediction.shape[0]):
                metadata = record.metadata[sample_idx] if sample_idx < len(record.metadata) else {}
                key = scenario_key(metadata)
                row = scenario_confidence_row(record, sample_idx, wet_threshold, phase13_keys, top_failure_keys)
                scenario_rows.append(row)
                scenario_predictions.setdefault(key, {})[record.seed] = {
                    "prediction": record.prediction[sample_idx : sample_idx + 1],
                    "target": record.target[sample_idx : sample_idx + 1],
                }

    add_aggregate(margin_groups, prefix_len=2)
    add_aggregate(risk_groups, prefix_len=2)
    margin_rows = metric_rows(
        margin_groups,
        ["seed", "run_name", "margin_bin", "lower_bound_inclusive", "upper_bound_exclusive"],
    )
    risk_rows = metric_rows(risk_groups, ["seed", "run_name", "risk_proxy_group", "risk_proxy_value"])
    disagreement_rows = analyze_seed_disagreement(scenario_predictions, wet_threshold)

    margin_path = output_dir / "confidence_margin_metrics.csv"
    disagreement_path = output_dir / "seed_disagreement_metrics.csv"
    risk_path = output_dir / "risk_proxy_metrics.csv"
    scenario_path = output_dir / "scenario_confidence_metrics.csv"
    summary_path = output_dir / "summary.json"

    metric_fields = [
        "cell_count",
        "rmse",
        "mae",
        "wet_dry_class_error_rate",
        "false_dry_rate",
        "false_wet_rate",
        "false_dry_cell_fraction",
        "false_wet_cell_fraction",
        "pred_wet_fraction",
        "target_wet_fraction",
        "mean_confidence_margin",
        "min_confidence_margin",
        "max_confidence_margin",
    ]
    write_csv(
        margin_path,
        margin_rows,
        ["seed", "run_name", "margin_bin", "lower_bound_inclusive", "upper_bound_exclusive", *metric_fields],
    )
    write_csv(
        risk_path,
        risk_rows,
        ["seed", "run_name", "risk_proxy_group", "risk_proxy_value", *metric_fields],
    )
    write_csv(
        disagreement_path,
        disagreement_rows,
        [
            "scenario_key",
            "location",
            "event",
            "start_idx",
            "matched_seed_count",
            "matched_seeds",
            "mean_prediction_std",
            "max_prediction_std",
            "p95_prediction_std",
            "wet_dry_disagreement_rate",
            "mean_seed_rmse",
            "max_seed_rmse",
            "target_max_depth",
            "target_mean_depth",
            *metric_fields,
        ],
    )
    scenario_metric_fields = [field for field in metric_fields if field != "mean_confidence_margin"]
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
        "scenario_key",
        "phase13_failure_case",
        "phase12_top_failure_scenario",
        "mean_confidence_margin",
        "median_confidence_margin",
        "p10_confidence_margin",
        "low_margin_fraction_lt_0_01",
        "low_margin_fraction_lt_0_02",
        "false_dry_mean_margin",
        "false_wet_mean_margin",
        "mismatch_mean_margin",
        "target_max_depth",
        "target_mean_depth",
        "prediction_max_depth",
        "prediction_mean_depth",
        *scenario_metric_fields,
    ]
    write_csv(scenario_path, scenario_rows, scenario_fields)
    figures = make_figures(output_dir, margin_rows, disagreement_rows, args.dpi) if args.figures else []

    proxy_summary = summarize_proxy_relationships(margin_rows, risk_rows, disagreement_rows)
    phase13_location2_rows = [
        row
        for row in scenario_rows
        if row["phase13_failure_case"] and str(row.get("location")) == "location2"
    ]
    summary = {
        "phase": "Phase 14 Uncertainty / Confidence Diagnostics",
        "diagnostic_type": "proxy_based_confidence_diagnosis",
        "interpretation_note": (
            "confidence_margin and seed disagreement are deterministic confidence/disagreement proxies, "
            "not calibrated probabilistic uncertainty."
        ),
        "constraints": {
            "retrained": False,
            "modified_model_architecture": False,
            "modified_training_code": False,
            "modified_phase10_loss": False,
            "modified_phase12_scripts": False,
            "modified_phase13_scripts": False,
            "tuned_boundary_weight": False,
            "tuned_boundary_band_pixels": False,
            "opened_new_sweep": False,
            "recomputed_predictions": False,
        },
        "inputs": {
            "runs": [display_path(path.resolve()) for path in args.runs],
            "phase12_failure_cases_csv": display_path(args.phase12_failure_cases),
            "phase12_scenario_metrics_csv": display_path(args.phase12_scenario_metrics),
            "phase13_summary_json": display_path(args.phase13_summary),
            "phase12_failure_case_rows": len(phase12_failure_rows),
            "phase12_scenario_metric_rows": len(phase12_scenario_rows),
            "phase13_failure_scenario_count": len(phase13_keys),
        },
        "settings": {
            "wet_threshold": wet_threshold,
            "margin_bins": margin_bins,
            "boundary_bands_recomputed_from_target_wet_dry": True,
        },
        "run_batch_counts": run_batch_counts,
        "row_counts": {
            "confidence_margin_metrics": len(margin_rows),
            "seed_disagreement_metrics": len(disagreement_rows),
            "risk_proxy_metrics": len(risk_rows),
            "scenario_confidence_metrics": len(scenario_rows),
        },
        "risk_proxy_relationships": proxy_summary,
        "phase13_location2_failure_proxy_summary": {
            "scenario_rows": len(phase13_location2_rows),
            "mean_confidence_margin": float(np.mean([float(row["mean_confidence_margin"]) for row in phase13_location2_rows]))
            if phase13_location2_rows
            else "",
            "mean_low_margin_fraction_lt_0_02": float(
                np.mean([float(row["low_margin_fraction_lt_0_02"]) for row in phase13_location2_rows])
            )
            if phase13_location2_rows
            else "",
            "mean_wet_dry_class_error_rate": float(
                np.mean([float(row["wet_dry_class_error_rate"]) for row in phase13_location2_rows])
            )
            if phase13_location2_rows
            else "",
        },
        "outputs": {
            "summary_json": display_path(summary_path),
            "confidence_margin_metrics_csv": display_path(margin_path),
            "seed_disagreement_metrics_csv": display_path(disagreement_path),
            "risk_proxy_metrics_csv": display_path(risk_path),
            "scenario_confidence_metrics_csv": display_path(scenario_path),
            "figures": figures,
        },
    }
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Generate Phase 14 proxy-based confidence diagnostics from saved Phase 10 forecast maps. "
            "This does not retrain, tune, or estimate calibrated probabilistic uncertainty."
        )
    )
    parser.add_argument("--runs", type=Path, nargs="+", default=[Path(run) for run in DEFAULT_RUNS])
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--wet-threshold", type=float, default=0.05)
    parser.add_argument(
        "--margin-bins",
        default="0,0.005,0.01,0.02,0.05,0.1,0.2,5",
        help="Comma-separated confidence-margin bin edges.",
    )
    parser.add_argument("--phase12-failure-cases", type=Path, default=DEFAULT_PHASE12_FAILURE_CASES)
    parser.add_argument("--phase12-scenario-metrics", type=Path, default=DEFAULT_PHASE12_SCENARIO_METRICS)
    parser.add_argument("--phase13-summary", type=Path, default=DEFAULT_PHASE13_SUMMARY)
    parser.add_argument("--max-batches", type=int, default=None, help="Optional smoke-check limiter per run.")
    parser.add_argument("--dpi", type=int, default=180)
    parser.add_argument("--figures", dest="figures", action="store_true", default=True)
    parser.add_argument("--no-figures", dest="figures", action="store_false")
    return parser.parse_args()


def main() -> None:
    summary = analyze(parse_args())
    print(json.dumps({"outputs": summary["outputs"], "row_counts": summary["row_counts"]}, indent=2))


if __name__ == "__main__":
    main()
