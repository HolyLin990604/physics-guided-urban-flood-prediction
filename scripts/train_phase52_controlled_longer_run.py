from __future__ import annotations

import argparse
import csv
import json
import math
import sys
import time
import tracemalloc
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import torch

from scripts.train_phase47_full_downsample_baseline import (
    build_datasets,
    build_model,
    load_json,
    make_loader,
    memory_snapshot,
    repo_path,
    set_seed,
    validate_indexes,
    validate_row_shapes,
)
from trainers.train import build_loss, train_one_epoch
from trainers.validate import validate_one_epoch


EXPECTED_CONFIG = Path("configs/train_phase52_full_downsample128_seed42_40e.json")
PHASE47_CONFIG = Path("configs/train_phase47_full_downsample128_seed42_10e.json")
EXPECTED_OUTPUT_DIR = Path("runs/phase52_full_downsample128_seed42_40e")
EXPECTED_ANALYSIS_DIR = Path("analysis/phase52_controlled_128x128_seed42_longer_run")
SUMMARY_JSON = "phase52_training_summary.json"
SUMMARY_MD = "phase52_training_summary.md"
EXPECTED_TRAIN_WINDOWS = 960
EXPECTED_TEST_WINDOWS = 384
EXPECTED_TRAINING_COMMAND = (
    "python scripts/train_phase52_controlled_longer_run.py "
    "--config configs/train_phase52_full_downsample128_seed42_40e.json"
)

CONTROLLED_TOP_LEVEL = {
    "phase": 52,
    "seed": 42,
    "resolution": 128,
    "epochs": 40,
    "output_dir": EXPECTED_OUTPUT_DIR.as_posix(),
    "analysis_dir": EXPECTED_ANALYSIS_DIR.as_posix(),
    "training_scope": "controlled_128x128_seed42_longer_run",
    "no_swe_pinn": True,
    "level5_supported": False,
}

UNCHANGED_PHASE47_KEYS = (
    "dataset_root",
    "scenario_index_path",
    "static_index_path",
    "dataset",
    "model",
    "optimization",
    "metrics",
    "runtime",
)

PROHIBITED_CONFIG_KEYS = {
    "seed123",
    "seed202",
    "seed_sweep",
    "seeds",
    "seed_replication",
    "sweep",
    "hyperparameter_sweep",
    "resolution_sweep",
    "resolutions",
    "tile_training",
    "multiscale_training",
    "full_500_training",
    "full_resolution_training",
    "pinn",
    "swe_residual",
    "level5_claim",
    "strict_conservation",
    "full_mass_conservation",
    "hydrodynamic_closure",
    "calibrated_probability",
    "production_ready",
}

PHASE47_REFERENCE = {
    "test_rmse": 0.01109213042097205,
    "test_mae": 0.00525291082279485,
    "test_wet_dry_iou": 0.8255524213115374,
    "test_rollout_stability": 0.998722607580324,
    "test_step_rmse_std": 0.0012824604989987165,
    "test_loss": 0.00110163203172912,
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the controlled Phase 52 128x128 seed42 longer-run baseline."
    )
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate indexes, windows, batches, and a forward pass without training or writes.",
    )
    return parser.parse_args()


def normalized_path(value: Any) -> str:
    return str(Path(value)).replace("\\", "/")


def flatten_key_names(value: Any) -> set[str]:
    names: set[str] = set()
    if isinstance(value, dict):
        for key, child in value.items():
            names.add(str(key))
            names.update(flatten_key_names(child))
    elif isinstance(value, list):
        for child in value:
            names.update(flatten_key_names(child))
    return names


def validate_config(config: dict[str, Any], config_path: Path) -> None:
    if repo_path(config_path).resolve() != repo_path(EXPECTED_CONFIG).resolve():
        raise ValueError(f"Phase 52 requires --config {EXPECTED_CONFIG.as_posix()}.")

    for key, expected in CONTROLLED_TOP_LEVEL.items():
        actual = config.get(key)
        if key in {"output_dir", "analysis_dir"}:
            actual = normalized_path(actual)
        if actual != expected:
            raise ValueError(f"Phase 52 requires {key}={expected!r}, got {actual!r}.")

    if int(config["epochs"]) > 40:
        raise ValueError("Phase 52 training must never exceed the 40-epoch cap.")

    phase47 = load_json(PHASE47_CONFIG)
    for key in UNCHANGED_PHASE47_KEYS:
        if config.get(key) != phase47.get(key):
            raise ValueError(f"Phase 52 {key!r} must exactly match the Phase 47 controlled basis.")

    prohibited = sorted(PROHIBITED_CONFIG_KEYS & flatten_key_names(config))
    if prohibited:
        raise ValueError(f"Prohibited Phase 52 config keys present: {prohibited}.")


def validate_sample_counts(train_dataset: Any, test_dataset: Any) -> None:
    if len(train_dataset) != EXPECTED_TRAIN_WINDOWS:
        raise ValueError(
            f"Expected {EXPECTED_TRAIN_WINDOWS} Phase 52 train windows, got {len(train_dataset)}."
        )
    if len(test_dataset) != EXPECTED_TEST_WINDOWS:
        raise ValueError(
            f"Expected {EXPECTED_TEST_WINDOWS} Phase 52 test windows, got {len(test_dataset)}."
        )


def run_dry_run(config: dict[str, Any], train_dataset: Any, test_dataset: Any) -> None:
    train_loader = make_loader(
        train_dataset,
        batch_size=int(config["optimization"]["batch_size"]),
        shuffle=False,
        config=config,
    )
    test_loader = make_loader(
        test_dataset,
        batch_size=int(config["optimization"]["eval_batch_size"]),
        shuffle=False,
        config=config,
    )
    train_batch = next(iter(train_loader))
    test_batch = next(iter(test_loader))
    model = build_model(config)
    model.eval()
    with torch.no_grad():
        prediction = model(
            train_batch["past_flood"].float(),
            train_batch["past_rainfall"].float(),
            train_batch["future_rainfall"].float(),
            train_batch["static_maps"].float(),
        )
        test_prediction = model(
            test_batch["past_flood"].float(),
            test_batch["past_rainfall"].float(),
            test_batch["future_rainfall"].float(),
            test_batch["static_maps"].float(),
        )

    target = train_batch["future_flood"]
    if prediction.shape != target.shape:
        raise ValueError(f"Prediction shape {tuple(prediction.shape)} != target shape {tuple(target.shape)}.")
    if test_prediction.shape != test_batch["future_flood"].shape:
        raise ValueError("Test-batch prediction and target shapes do not match.")
    if not torch.isfinite(prediction).all() or not torch.isfinite(test_prediction).all():
        raise ValueError("Dry-run produced non-finite predictions.")

    print(f"train_windows={len(train_dataset)}")
    print(f"test_windows={len(test_dataset)}")
    print(f"batch_shape={tuple(train_batch['past_flood'].shape)}")
    print(f"prediction_shape={tuple(prediction.shape)}")
    print(f"target_shape={tuple(target.shape)}")
    print("dry_run_passed=true")
    print("no_training=true")


def write_metrics(output_dir: Path, history: list[dict[str, float]], best_rmse: float | None) -> None:
    payload = {"history": history, "best_test_rmse": best_rmse}
    (output_dir / "metrics.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8"
    )
    if history:
        with (output_dir / "metrics.csv").open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(history[0].keys()))
            writer.writeheader()
            writer.writerows(history)


def write_runtime_notes(path: Path, config: dict[str, Any], memory: dict[str, Any]) -> None:
    lines = [
        "# Phase 52 Runtime And Memory Notes",
        "",
        "- Scope: controlled 128x128 seed42 longer-run baseline.",
        "- Maximum epochs: `40`.",
        "- Data route: Phase 45 indexed arrays with in-memory bilinear downsampling.",
        "- Future rainfall: known forcing with proportional-bin-mean alignment.",
        "- SWE residuals or PINN components: `false`.",
        f"- Batch size: `{config['optimization']['batch_size']}`.",
        f"- Eval batch size: `{config['optimization']['eval_batch_size']}`.",
        f"- Runtime seconds: `{memory['runtime_seconds']:.3f}`.",
        f"- Tracemalloc current MB: `{memory['tracemalloc_current_mb']:.3f}`.",
        f"- Tracemalloc peak MB: `{memory['tracemalloc_peak_mb']:.3f}`.",
    ]
    if "cuda_max_allocated_mb" in memory:
        lines.extend(
            [
                f"- CUDA max allocated MB: `{memory['cuda_max_allocated_mb']:.3f}`.",
                f"- CUDA max reserved MB: `{memory['cuda_max_reserved_mb']:.3f}`.",
            ]
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def comparison_for(best: dict[str, float], final: dict[str, float]) -> dict[str, Any]:
    comparison: dict[str, Any] = {}
    for metric, reference in PHASE47_REFERENCE.items():
        best_value = float(best[metric])
        final_value = float(final[metric])
        comparison[metric] = {
            "phase47_reference": reference,
            "phase52_best_epoch_value": best_value,
            "phase52_final_epoch_value": final_value,
            "best_minus_phase47": best_value - reference,
            "final_minus_phase47": final_value - reference,
        }
    return comparison


def write_summary_md(path: Path, summary: dict[str, Any]) -> None:
    lines = [
        "# Phase 52 Controlled Longer-Run Training Summary",
        "",
        f"- selected_decision: `{summary['selected_decision']}`",
        f"- seed: `{summary['seed']}`",
        f"- resolution: `{summary['resolution']}`",
        f"- epochs_configured: `{summary['epochs_configured']}`",
        f"- train_samples: `{summary['train_samples']}`",
        f"- test_samples: `{summary['test_samples']}`",
        f"- best_epoch: `{summary['best_epoch']}`",
        f"- phase47_reference_best_test_rmse: `{summary['phase47_reference_best_test_rmse']}`",
        f"- phase47_reference_test_mae: `{summary['phase47_reference_test_mae']}`",
        f"- phase47_reference_test_wet_dry_iou: `{summary['phase47_reference_test_wet_dry_iou']}`",
        f"- no_swe_pinn: `{str(summary['no_swe_pinn']).lower()}`",
        f"- level5_supported: `{str(summary['level5_supported']).lower()}`",
        "",
        "## Direct Phase 47 Comparison",
        "",
        "| Metric | Phase 47 | Phase 52 best | Phase 52 final | Best - Phase 47 | Final - Phase 47 |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for metric, values in summary["phase47_comparison"].items():
        lines.append(
            f"| {metric} | {values['phase47_reference']} | "
            f"{values['phase52_best_epoch_value']} | {values['phase52_final_epoch_value']} | "
            f"{values['best_minus_phase47']} | {values['final_minus_phase47']} |"
        )
    lines.extend(
        [
            "",
            "This controlled run does not support Level 5, strict conservation, hydrodynamic closure, "
            "calibrated probability warning labels, or production-readiness claims.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_training(config: dict[str, Any], train_dataset: Any, test_dataset: Any) -> None:
    output_dir = repo_path(config["output_dir"])
    analysis_dir = repo_path(config["analysis_dir"])
    checkpoints_dir = output_dir / "checkpoints"
    protected = (
        output_dir / "metrics.json",
        checkpoints_dir / "best.pt",
        checkpoints_dir / "final.pt",
        analysis_dir / SUMMARY_JSON,
    )
    existing = [str(path) for path in protected if path.exists()]
    if existing:
        raise FileExistsError(f"Refusing to overwrite existing Phase 52 training artifacts: {existing}")

    output_dir.mkdir(parents=True, exist_ok=True)
    analysis_dir.mkdir(parents=True, exist_ok=True)
    checkpoints_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "training_config_snapshot.json").write_text(
        json.dumps(config, indent=2, sort_keys=True), encoding="utf-8"
    )

    device = torch.device(config["runtime"]["device"] if torch.cuda.is_available() else "cpu")
    if device.type == "cuda":
        torch.cuda.reset_peak_memory_stats(device)
    train_loader = make_loader(
        train_dataset,
        batch_size=int(config["optimization"]["batch_size"]),
        shuffle=True,
        config=config,
    )
    test_loader = make_loader(
        test_dataset,
        batch_size=int(config["optimization"]["eval_batch_size"]),
        shuffle=False,
        config=config,
    )
    model = build_model(config).to(device)
    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=float(config["optimization"]["lr"]),
        weight_decay=float(config["optimization"]["weight_decay"]),
    )
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=int(config["epochs"]))
    criterion = build_loss(config["optimization"]["loss"])
    scaler = torch.cuda.amp.GradScaler(
        enabled=device.type == "cuda" and bool(config["runtime"]["use_amp"])
    )

    history: list[dict[str, float]] = []
    best_record: dict[str, float] | None = None
    best_rmse: float | None = None
    start_time = time.perf_counter()
    tracemalloc.start()

    for epoch in range(1, min(int(config["epochs"]), 40) + 1):
        learning_rate = float(optimizer.param_groups[0]["lr"])
        train_metrics = train_one_epoch(
            model,
            train_loader,
            optimizer,
            device,
            criterion,
            wet_threshold=float(config["metrics"]["wet_threshold"]),
            scaler=scaler,
            grad_clip_norm=float(config["optimization"]["grad_clip_norm"]),
            use_amp=bool(config["runtime"]["use_amp"]),
            physics_controller=None,
        )
        test_metrics = validate_one_epoch(
            model,
            test_loader,
            device,
            criterion,
            wet_threshold=float(config["metrics"]["wet_threshold"]),
            physics_controller=None,
        )
        record = {
            "epoch": float(epoch),
            "learning_rate": learning_rate,
            **{f"train_{key}": float(value) for key, value in train_metrics.items()},
            **{f"test_{key}": float(value) for key, value in test_metrics.items()},
        }
        if not all(math.isfinite(value) for value in record.values()):
            raise FloatingPointError(f"Non-finite Phase 52 metric at epoch {epoch}: {record}")
        history.append(record)
        current_rmse = record["test_rmse"]
        if best_rmse is None or current_rmse < best_rmse:
            best_rmse = current_rmse
            best_record = dict(record)
            torch.save(
                {
                    "epoch": epoch,
                    "model_state": model.state_dict(),
                    "optimizer_state": optimizer.state_dict(),
                    "scheduler_state": scheduler.state_dict(),
                    "config": config,
                    "best_test_rmse": best_rmse,
                },
                checkpoints_dir / "best.pt",
            )
        scheduler.step()
        write_metrics(output_dir, history, best_rmse)
        print(json.dumps(record, sort_keys=True))

    final_record = history[-1]
    torch.save(
        {
            "epoch": int(final_record["epoch"]),
            "model_state": model.state_dict(),
            "optimizer_state": optimizer.state_dict(),
            "scheduler_state": scheduler.state_dict(),
            "config": config,
            "final_test_rmse": final_record["test_rmse"],
        },
        checkpoints_dir / "final.pt",
    )
    memory = memory_snapshot(device, start_time)
    tracemalloc.stop()
    write_runtime_notes(output_dir / "runtime_memory_notes.md", config, memory)

    assert best_record is not None
    summary = {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "selected_decision": "phase52_controlled_128x128_seed42_longer_run_completed",
        "phase": 52,
        "seed": 42,
        "resolution": 128,
        "epochs_configured": 40,
        "epochs_completed": len(history),
        "train_samples": len(train_dataset),
        "test_samples": len(test_dataset),
        "best_epoch": int(best_record["epoch"]),
        "best_epoch_metrics": best_record,
        "final_epoch_metrics": final_record,
        "phase47_reference_best_test_rmse": PHASE47_REFERENCE["test_rmse"],
        "phase47_reference_test_mae": PHASE47_REFERENCE["test_mae"],
        "phase47_reference_test_wet_dry_iou": PHASE47_REFERENCE["test_wet_dry_iou"],
        "phase47_reference_test_rollout_stability": PHASE47_REFERENCE[
            "test_rollout_stability"
        ],
        "phase47_comparison": comparison_for(best_record, final_record),
        "no_swe_pinn": True,
        "level5_supported": False,
        "training_command": EXPECTED_TRAINING_COMMAND,
        "runtime_memory": memory,
    }
    (analysis_dir / SUMMARY_JSON).write_text(
        json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8"
    )
    write_summary_md(analysis_dir / SUMMARY_MD, summary)


def main() -> None:
    args = parse_args()
    config = load_json(args.config)
    validate_config(config, args.config)
    set_seed(int(config["seed"]))
    scenario_rows, _static_rows = validate_indexes(config)
    validate_row_shapes(scenario_rows)
    train_dataset, test_dataset = build_datasets(config, scenario_rows)
    validate_sample_counts(train_dataset, test_dataset)

    if args.dry_run:
        run_dry_run(config, train_dataset, test_dataset)
        return

    run_training(config, train_dataset, test_dataset)


if __name__ == "__main__":
    main()
