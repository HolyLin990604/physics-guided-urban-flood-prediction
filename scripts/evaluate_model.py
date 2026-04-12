from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import torch
from torch.utils.data import DataLoader

from datasets.urbanflood24_lite_adapter import UrbanFlood24LiteProcessDataset
from scripts.train_model import build_model, collate_samples, load_json
from trainers.test import test_model


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate the baseline U-Net + TCN flood forecasting model.")
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("configs/train_baseline.json"),
        help="Training config JSON file.",
    )
    parser.add_argument(
        "--checkpoint",
        type=Path,
        default=None,
        help="Checkpoint to load. Defaults to <output>/checkpoints/best.pt.",
    )
    parser.add_argument("--split", default="test", choices=("train", "test"))
    args = parser.parse_args()

    config = load_json(args.config)
    device = torch.device(config["runtime"]["device"] if torch.cuda.is_available() else "cpu")
    checkpoint_path = (
        args.checkpoint
        if args.checkpoint is not None
        else Path(config["output"]["root"]).expanduser().resolve() / "checkpoints" / "best.pt"
    )
    checkpoint = torch.load(checkpoint_path, map_location=device)

    model = build_model(config["model"]).to(device)
    model.load_state_dict(checkpoint["model_state"])

    dataset = UrbanFlood24LiteProcessDataset.from_config(
        config["dataset"]["dataset_config_path"],
        split=args.split,
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

    artifact_dir = Path(config["output"]["root"]).expanduser().resolve() / f"evaluation_{args.split}"
    metrics = test_model(
        model,
        dataloader,
        device,
        wet_threshold=config["metrics"]["wet_threshold"],
        artifact_dir=artifact_dir,
        visualization_config=config["output"].get("timeseries"),
    )
    print(json.dumps(metrics, indent=2))
    (artifact_dir / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
