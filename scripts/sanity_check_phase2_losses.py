from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import torch

from scripts.train_model import load_json
from utils.physics_losses import PhysicsLossController, list_physics_losses


def make_synthetic_batch(
    *,
    batch_size: int,
    input_steps: int,
    pred_steps: int,
    height: int,
    width: int,
) -> tuple[torch.Tensor, torch.Tensor, dict[str, torch.Tensor]]:
    target = torch.rand(batch_size, pred_steps, 1, height, width)
    prediction = target + 0.05 * torch.randn_like(target)
    prediction[:, :, :, : height // 4, : width // 4] -= 0.02

    batch = {
        "past_flood": torch.rand(batch_size, input_steps, 1, height, width),
        "past_rainfall": torch.rand(batch_size, input_steps, 1),
        "future_rainfall": torch.rand(batch_size, pred_steps, 1),
        "static_maps": torch.rand(batch_size, 3, height, width),
        "future_flood": target,
    }
    return prediction, target, batch


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run a minimal synthetic sanity check for Phase 2 loss-only configs."
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("configs/train_phase2_loss_only_debug.json"),
        help="Training config JSON file.",
    )
    parser.add_argument("--input-steps", type=int, default=12)
    parser.add_argument("--pred-steps", type=int, default=12)
    parser.add_argument("--height", type=int, default=32)
    parser.add_argument("--width", type=int, default=32)
    parser.add_argument("--batch-size", type=int, default=2)
    args = parser.parse_args()

    config = load_json(args.config)
    prediction, target, batch = make_synthetic_batch(
        batch_size=args.batch_size,
        input_steps=args.input_steps,
        pred_steps=args.pred_steps,
        height=args.height,
        width=args.width,
    )

    controller = PhysicsLossController(config.get("physics_losses", {}))
    physics_total, metrics = controller.compute(prediction, target, batch)
    payload = {
        "config": str(args.config),
        "available_terms": list(list_physics_losses()),
        "physics_total": float(physics_total.detach().item()),
        "metrics": metrics,
    }
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()