from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import torch
from torch.utils.data import DataLoader, Subset

from datasets.urbanflood24_lite_adapter import UrbanFlood24LiteProcessDataset
from models.unet_tcn import UNetTCNForecaster
from trainers.train import build_loss, train_one_epoch
from trainers.validate import validate_one_epoch
from utils.physics_losses import PhysicsLossController


def load_json(path: str | Path) -> Dict:
    path = Path(path).expanduser().resolve()
    return json.loads(path.read_text(encoding="utf-8"))


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)


def collate_samples(samples):
    return UrbanFlood24LiteProcessDataset.collate_numpy(samples)


def split_train_val_by_event(dataset: UrbanFlood24LiteProcessDataset, val_fraction: float, seed: int) -> Tuple[Subset, Subset]:
    if not 0.0 < val_fraction < 1.0:
        raise ValueError(f"val_fraction must be in (0, 1), got {val_fraction}.")

    event_to_indices: Dict[str, List[int]] = {}
    for sample_idx in range(len(dataset)):
        key = dataset.get_sample_event_key(sample_idx)
        event_to_indices.setdefault(key, []).append(sample_idx)

    event_keys = list(event_to_indices.keys())
    rng = random.Random(seed)
    rng.shuffle(event_keys)
    val_count = max(1, int(round(len(event_keys) * val_fraction)))
    val_keys = set(event_keys[:val_count])

    train_indices: List[int] = []
    val_indices: List[int] = []
    for key, indices in event_to_indices.items():
        if key in val_keys:
            val_indices.extend(indices)
        else:
            train_indices.extend(indices)

    if not train_indices or not val_indices:
        raise ValueError(
            "Event-based train/val split produced an empty subset. "
            f"train={len(train_indices)} val={len(val_indices)}."
        )

    return Subset(dataset, train_indices), Subset(dataset, val_indices)


def build_model(model_cfg: Dict) -> UNetTCNForecaster:
    return UNetTCNForecaster(
        flood_channels=model_cfg["flood_channels"],
        static_channels=model_cfg["static_channels"],
        rainfall_channels=model_cfg["rainfall_channels"],
        out_channels=model_cfg["out_channels"],
        base_channels=model_cfg["base_channels"],
        encoder_levels=model_cfg["encoder_levels"],
        temporal_hidden_channels=model_cfg["temporal_hidden_channels"],
        temporal_layers=model_cfg["temporal_layers"],
        temporal_kernel_size=model_cfg["temporal_kernel_size"],
        dropout=model_cfg["dropout"],
        skip_fusion_mode=model_cfg.get("skip_fusion_mode", "temporal_mean"),
        rainfall_conditioning=model_cfg.get("rainfall_conditioning"),
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Train the baseline U-Net + TCN flood forecasting model.")
    parser.add_argument(
        "--config",
        type=Path,
       default=Path("configs/train_baseline.json"),
        help="Training config JSON file.",
    )
    args = parser.parse_args()

    config = load_json(args.config)
    set_seed(config["runtime"]["seed"])

    device = torch.device(config["runtime"]["device"] if torch.cuda.is_available() else "cpu")
    output_dir = Path(config["output"]["root"]).expanduser().resolve()
    checkpoints_dir = output_dir / "checkpoints"
    visuals_dir = output_dir / "visualizations"
    output_dir.mkdir(parents=True, exist_ok=True)
    checkpoints_dir.mkdir(parents=True, exist_ok=True)
    visuals_dir.mkdir(parents=True, exist_ok=True)

    train_dataset_full = UrbanFlood24LiteProcessDataset.from_config(
        config["dataset"]["dataset_config_path"],
        split=config["dataset"]["train_split"],
        debug=False,
    )
    train_subset, val_subset = split_train_val_by_event(
        train_dataset_full,
        val_fraction=config["dataset"]["val_fraction"],
        seed=config["runtime"]["seed"],
    )

    train_loader = DataLoader(
        train_subset,
        batch_size=config["optimization"]["batch_size"],
        shuffle=True,
        num_workers=config["runtime"]["num_workers"],
        pin_memory=device.type == "cuda",
        collate_fn=collate_samples,
    )
    val_loader = DataLoader(
        val_subset,
        batch_size=config["optimization"]["eval_batch_size"],
        shuffle=False,
        num_workers=config["runtime"]["num_workers"],
        pin_memory=device.type == "cuda",
        collate_fn=collate_samples,
    )

    model = build_model(config["model"]).to(device)
    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=config["optimization"]["lr"],
        weight_decay=config["optimization"]["weight_decay"],
    )
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=config["optimization"]["epochs"])
    criterion = build_loss(config["optimization"]["loss"])
    scaler = torch.cuda.amp.GradScaler(enabled=device.type == "cuda" and config["runtime"]["use_amp"])
    physics_controller = PhysicsLossController(config.get("physics_losses", {}))

    best_metric = None
    history: List[Dict[str, float]] = []
    for epoch in range(1, config["optimization"]["epochs"] + 1):
        train_metrics = train_one_epoch(
            model,
            train_loader,
            optimizer,
            device,
            criterion,
            wet_threshold=config["metrics"]["wet_threshold"],
            scaler=scaler,
            grad_clip_norm=config["optimization"]["grad_clip_norm"],
            use_amp=config["runtime"]["use_amp"],
            physics_controller=physics_controller,
        )
        val_metrics = validate_one_epoch(
            model,
            val_loader,
            device,
            criterion,
            wet_threshold=config["metrics"]["wet_threshold"],
            artifact_dir=visuals_dir / f"epoch_{epoch:03d}",
            max_visualizations=config["output"]["max_visualization_batches"],
            physics_controller=physics_controller,
            visualization_config=config["output"].get("timeseries"),
        )
        scheduler.step()

        record = {
            "epoch": epoch,
            **{f"train_{k}": v for k, v in train_metrics.items()},
            **{f"val_{k}": v for k, v in val_metrics.items()},
        }
        history.append(record)
        print(json.dumps(record, indent=2))

        current_metric = val_metrics[config["output"]["selection_metric"]]
        if best_metric is None or current_metric < best_metric:
            best_metric = current_metric
            torch.save(
                {
                    "epoch": epoch,
                    "model_state": model.state_dict(),
                    "optimizer_state": optimizer.state_dict(),
                    "scheduler_state": scheduler.state_dict(),
                    "config": config,
                    "best_metric": best_metric,
                },
                checkpoints_dir / "best.pt",
            )

    (output_dir / "history.json").write_text(json.dumps(history, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
