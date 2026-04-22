from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import torch
from torch import nn
from torch.utils.data import DataLoader

from datasets.urbanflood24_lite_adapter import UrbanFlood24LiteProcessDataset
from scripts.train_model import collate_samples, load_json, split_train_val_by_event


ADAPTIVE_PREFIX = "temporal_rainfall_gate.adaptive_alpha_mlp."
PERCENTILES = (0, 1, 5, 25, 50, 75, 95, 99, 100)


def resolve_repo_path(path: str | Path) -> Path:
    path = Path(path)
    if path.is_absolute():
        return path
    return REPO_ROOT / path


def display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return str(path)


def load_config(run_root: Path, checkpoint: dict[str, Any], config_path: Path | None) -> dict[str, Any]:
    if config_path is not None:
        return load_json(config_path)
    config = checkpoint.get("config")
    if isinstance(config, dict):
        return config
    raise ValueError(
        "Checkpoint does not contain an embedded config. Pass --config with the matching training config."
    )


def build_adaptive_alpha_mlp(model_config: dict[str, Any]) -> nn.Sequential:
    rainfall_config = model_config.get("rainfall_conditioning") or {}
    if not rainfall_config.get("adaptive_alpha_enabled", False):
        raise ValueError("Model config does not enable rainfall_conditioning.adaptive_alpha_enabled.")
    rainfall_channels = int(model_config["rainfall_channels"])
    hidden_channels = int(rainfall_config["hidden_channels"])
    adaptive_hidden_channels = max(min(hidden_channels // 2, 16), 4)
    return nn.Sequential(
        nn.Linear(rainfall_channels, adaptive_hidden_channels),
        nn.SiLU(inplace=True),
        nn.Linear(adaptive_hidden_channels, 1),
    )


def load_adaptive_state(mlp: nn.Sequential, checkpoint: dict[str, Any]) -> None:
    model_state = checkpoint.get("model_state")
    if not isinstance(model_state, dict):
        raise ValueError("Checkpoint is missing model_state.")
    adaptive_state = {
        key[len(ADAPTIVE_PREFIX) :]: value
        for key, value in model_state.items()
        if key.startswith(ADAPTIVE_PREFIX)
    }
    if not adaptive_state:
        raise ValueError("Checkpoint model_state does not contain adaptive_alpha_mlp weights.")
    mlp.load_state_dict(adaptive_state)


def build_dataset(config: dict[str, Any], split: str):
    dataset_config_path = config["dataset"]["dataset_config_path"]
    if split == "val":
        train_dataset = UrbanFlood24LiteProcessDataset.from_config(
            dataset_config_path,
            split=config["dataset"]["train_split"],
            debug=False,
        )
        _, val_subset = split_train_val_by_event(
            train_dataset,
            val_fraction=config["dataset"]["val_fraction"],
            seed=config["runtime"]["seed"],
        )
        return val_subset
    return UrbanFlood24LiteProcessDataset.from_config(dataset_config_path, split=split, debug=False)


def summarize_values(values: np.ndarray, *, lower_bound: float, upper_bound: float, saturation_eps: float) -> dict[str, Any]:
    if values.size == 0:
        raise ValueError("Cannot summarize an empty adaptive alpha array.")
    percentiles = np.percentile(values, PERCENTILES)
    lower_saturation = values <= lower_bound + saturation_eps
    upper_saturation = values >= upper_bound - saturation_eps
    near_identity = np.abs(values - 1.0) <= saturation_eps
    return {
        "count": int(values.size),
        "min": float(values.min()),
        "max": float(values.max()),
        "mean": float(values.mean()),
        "std": float(values.std(ddof=0)),
        "percentiles": {f"p{percentile}": float(value) for percentile, value in zip(PERCENTILES, percentiles)},
        "lower_bound": lower_bound,
        "upper_bound": upper_bound,
        "saturation_eps": saturation_eps,
        "near_lower_bound_count": int(lower_saturation.sum()),
        "near_upper_bound_count": int(upper_saturation.sum()),
        "near_identity_count": int(near_identity.sum()),
        "near_lower_bound_ratio": float(lower_saturation.mean()),
        "near_upper_bound_ratio": float(upper_saturation.mean()),
        "near_identity_ratio": float(near_identity.mean()),
    }


def summarize_by_step(records: list[dict[str, Any]], *, lower_bound: float, upper_bound: float, saturation_eps: float) -> list[dict[str, Any]]:
    grouped: dict[int, list[float]] = {}
    for record in records:
        grouped.setdefault(int(record["forecast_step"]), []).append(float(record["adaptive_alpha_scale"]))

    rows: list[dict[str, Any]] = []
    for step, step_values in sorted(grouped.items()):
        values = np.asarray(step_values, dtype=np.float64)
        summary = summarize_values(
            values,
            lower_bound=lower_bound,
            upper_bound=upper_bound,
            saturation_eps=saturation_eps,
        )
        rows.append(
            {
                "forecast_step": step,
                "count": summary["count"],
                "min": summary["min"],
                "max": summary["max"],
                "mean": summary["mean"],
                "std": summary["std"],
                "p05": summary["percentiles"]["p5"],
                "p50": summary["percentiles"]["p50"],
                "p95": summary["percentiles"]["p95"],
                "near_lower_bound_count": summary["near_lower_bound_count"],
                "near_upper_bound_count": summary["near_upper_bound_count"],
                "near_identity_count": summary["near_identity_count"],
            }
        )
    return rows


def format_value(value: Any) -> str:
    if isinstance(value, float):
        return f"{value:.8g}"
    return str(value)


def write_step_csv(rows: list[dict[str, Any]], output_path: Path) -> None:
    fields = [
        "forecast_step",
        "count",
        "min",
        "max",
        "mean",
        "std",
        "p05",
        "p50",
        "p95",
        "near_lower_bound_count",
        "near_upper_bound_count",
        "near_identity_count",
    ]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: format_value(row[field]) for field in fields})


def classify_behavior(summary: dict[str, Any]) -> str:
    near_identity_ratio = float(summary["near_identity_ratio"])
    near_bound_ratio = float(summary["near_lower_bound_ratio"]) + float(summary["near_upper_bound_ratio"])
    spread = float(summary["max"]) - float(summary["min"])
    if near_bound_ratio >= 0.10:
        return "frequently near configured bounds"
    if near_identity_ratio >= 0.80 and spread <= 0.02:
        return "mostly near identity"
    if spread >= 0.02:
        return "broadly varying within the configured range"
    return "modestly varying near identity"


def write_markdown(
    *,
    output_path: Path,
    summary: dict[str, Any],
    step_rows: list[dict[str, Any]],
) -> None:
    behavior = classify_behavior(summary["adaptive_alpha_scale"])
    lines = [
        "# Phase 9 Adaptive Mechanism Inspection",
        "",
        f"- run root: `{summary['run_root']}`",
        f"- checkpoint: `{summary['checkpoint_path']}`",
        f"- split: `{summary['split']}`",
        f"- inspected batches: `{summary['inspected_batches']}`",
        f"- inspected samples: `{summary['inspected_samples']}`",
        f"- adaptive alpha range: `{summary['adaptive_alpha_range']}`",
        "",
        "## What Was Inspected",
        "",
        "- Loaded the saved `temporal_rainfall_gate.adaptive_alpha_mlp` weights from the adapt010 checkpoint.",
        "- Recomputed the bounded adaptive multiplier from batch `future_rainfall` only.",
        "- Did not run training, update checkpoint files, or write into the run directory.",
        "",
        "## Available Signals",
        "",
        "- Available: per-sample, per-forecast-step adaptive multiplier `1 + adaptive_alpha_range * tanh(mlp(future_rainfall))`.",
        "- Not inspected in this first pass: gate channel values, decoder activations, gradients, or prediction changes with the scalar disabled.",
        "",
        "## First-Pass Reading",
        "",
        f"- The adaptive mechanism appears `{behavior}` for the inspected subset.",
        f"- Overall mean multiplier: `{summary['adaptive_alpha_scale']['mean']:.8g}`.",
        f"- Overall range: `{summary['adaptive_alpha_scale']['min']:.8g}` to `{summary['adaptive_alpha_scale']['max']:.8g}`.",
        f"- Near lower bound count: `{summary['adaptive_alpha_scale']['near_lower_bound_count']}`.",
        f"- Near upper bound count: `{summary['adaptive_alpha_scale']['near_upper_bound_count']}`.",
        "",
        "## Limitations",
        "",
        "- This is a limited evaluation-time inspection over the requested number of batches.",
        "- The scalar is derived from the checkpoint MLP and dataset rainfall, not from pre-existing saved scalar artifacts.",
        "- The scalar only multiplies the protected active response path; this report does not quantify downstream prediction sensitivity.",
        "",
        "## Per-Step Summary",
        "",
        "| step | count | mean | std | min | max | p05 | p50 | p95 | near lower | near upper |",
        "|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in step_rows:
        lines.append(
            "| {forecast_step} | {count} | {mean:.8g} | {std:.8g} | {min:.8g} | {max:.8g} | {p05:.8g} | {p50:.8g} | {p95:.8g} | {near_lower_bound_count} | {near_upper_bound_count} |".format(
                **row
            )
        )

    output_path.write_text("\n".join(lines), encoding="utf-8")


def inspect_adaptive_alpha(args: argparse.Namespace) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    run_root = resolve_repo_path(args.adapt010_run_root)
    output_dir = resolve_repo_path(args.output_dir)
    if not run_root.exists():
        raise FileNotFoundError(f"adapt010 run root not found: {display_path(run_root)}")
    checkpoint_path = run_root / "checkpoints" / "best.pt"
    if not checkpoint_path.exists():
        raise FileNotFoundError(f"Checkpoint not found: {display_path(checkpoint_path)}")

    device = torch.device(args.device if args.device != "auto" and torch.cuda.is_available() else "cpu")
    checkpoint = torch.load(checkpoint_path, map_location=device)
    config_path = resolve_repo_path(args.config) if args.config is not None else None
    config = load_config(run_root, checkpoint, config_path)
    model_config = config["model"]
    rainfall_config = model_config.get("rainfall_conditioning") or {}
    adaptive_alpha_range = float(rainfall_config["adaptive_alpha_range"])
    lower_bound = 1.0 - adaptive_alpha_range
    upper_bound = 1.0 + adaptive_alpha_range

    mlp = build_adaptive_alpha_mlp(model_config).to(device)
    load_adaptive_state(mlp, checkpoint)
    mlp.eval()

    dataset = build_dataset(config, args.split)
    dataloader = DataLoader(
        dataset,
        batch_size=int(config["optimization"]["eval_batch_size"]),
        shuffle=False,
        num_workers=int(config["runtime"]["num_workers"]),
        pin_memory=device.type == "cuda",
        collate_fn=collate_samples,
    )

    records: list[dict[str, Any]] = []
    inspected_batches = 0
    inspected_samples = 0
    with torch.no_grad():
        for batch_idx, batch in enumerate(dataloader):
            if args.max_batches is not None and inspected_batches >= args.max_batches:
                break
            future_rainfall = torch.as_tensor(batch["future_rainfall"], dtype=torch.float32, device=device)
            batch_size, future_steps, rain_channels = future_rainfall.shape
            raw_alpha = mlp(future_rainfall.reshape(batch_size * future_steps, rain_channels))
            scale = 1.0 + adaptive_alpha_range * torch.tanh(raw_alpha)
            scale = scale.view(batch_size, future_steps).detach().cpu().numpy()
            rainfall = future_rainfall.detach().cpu().numpy()

            for sample_idx in range(batch_size):
                metadata = batch.get("metadata", [{}])[sample_idx]
                for step_idx in range(future_steps):
                    records.append(
                        {
                            "batch_index": batch_idx,
                            "sample_index": sample_idx,
                            "forecast_step": step_idx,
                            "adaptive_alpha_scale": float(scale[sample_idx, step_idx]),
                            "future_rainfall": float(rainfall[sample_idx, step_idx, 0]),
                            "location": metadata.get("location", ""),
                            "event": metadata.get("event", ""),
                            "start_idx": metadata.get("start_idx", ""),
                        }
                    )
            inspected_batches += 1
            inspected_samples += batch_size

    if not records:
        raise ValueError("No batches were inspected; check split selection and --max-batches.")

    values = np.asarray([record["adaptive_alpha_scale"] for record in records], dtype=np.float64)
    alpha_summary = summarize_values(
        values,
        lower_bound=lower_bound,
        upper_bound=upper_bound,
        saturation_eps=args.saturation_eps,
    )
    step_rows = summarize_by_step(
        records,
        lower_bound=lower_bound,
        upper_bound=upper_bound,
        saturation_eps=args.saturation_eps,
    )
    summary = {
        "run_root": display_path(run_root),
        "checkpoint_path": display_path(checkpoint_path),
        "config_source": display_path(config_path) if config_path is not None else "checkpoint_embedded_config",
        "split": args.split,
        "max_batches": args.max_batches,
        "inspected_batches": inspected_batches,
        "inspected_samples": inspected_samples,
        "inspected_values": len(records),
        "checkpoint_epoch": checkpoint.get("epoch"),
        "checkpoint_best_metric": checkpoint.get("best_metric"),
        "adaptive_alpha_range": adaptive_alpha_range,
        "adaptive_alpha_lower_bound": lower_bound,
        "adaptive_alpha_upper_bound": upper_bound,
        "adaptive_alpha_scale": alpha_summary,
        "signals_available": [
            "future_rainfall",
            "adaptive_alpha_mlp_output",
            "bounded adaptive alpha scale",
        ],
        "inspection_path": "minimal evaluation-time scalar recomputation from checkpoint MLP and dataset future_rainfall",
    }

    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "adaptive_alpha_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    write_step_csv(step_rows, output_dir / "adaptive_alpha_by_step.csv")
    write_markdown(output_path=output_dir / "adaptive_alpha_inspection_summary.md", summary=summary, step_rows=step_rows)
    write_records_csv(records, output_dir / "adaptive_alpha_values.csv")
    return summary, step_rows


def write_records_csv(records: list[dict[str, Any]], output_path: Path) -> None:
    fields = [
        "batch_index",
        "sample_index",
        "forecast_step",
        "adaptive_alpha_scale",
        "future_rainfall",
        "location",
        "event",
        "start_idx",
    ]
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for record in records:
            writer.writerow({field: format_value(record[field]) for field in fields})


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Inspect adapt010 adaptive alpha behavior from an existing checkpoint and evaluation batches."
    )
    parser.add_argument("--adapt010-run-root", type=Path, required=True, help="Existing adapt010 run root.")
    parser.add_argument("--config", type=Path, default=None, help="Optional matching config path.")
    parser.add_argument("--split", default="val", choices=("train", "val", "test"), help="Dataset split/subset to inspect.")
    parser.add_argument("--output-dir", type=Path, required=True, help="Directory where analysis outputs are written.")
    parser.add_argument("--max-batches", type=int, default=8, help="Maximum number of batches to inspect.")
    parser.add_argument(
        "--saturation-eps",
        type=float,
        default=1.0e-3,
        help="Tolerance for near-identity and near-bound saturation counts.",
    )
    parser.add_argument("--device", default="auto", help="Use 'auto', 'cpu', or a CUDA device string.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    summary, _ = inspect_adaptive_alpha(args)
    output_dir = resolve_repo_path(args.output_dir)
    print(f"Wrote JSON: {display_path(output_dir / 'adaptive_alpha_summary.json')}")
    print(f"Wrote CSV: {display_path(output_dir / 'adaptive_alpha_by_step.csv')}")
    print(f"Wrote CSV: {display_path(output_dir / 'adaptive_alpha_values.csv')}")
    print(f"Wrote Markdown: {display_path(output_dir / 'adaptive_alpha_inspection_summary.md')}")
    print(f"Inspected run: {summary['run_root']}")
    print(f"Inspection path: {summary['inspection_path']}")


if __name__ == "__main__":
    main()
