from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import torch

from scripts.sanity_check_phase2_losses import make_synthetic_batch
from scripts.train_model import build_model, load_json


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run a minimal synthetic sanity check for Phase 2B rainfall conditioning."
    )
    parser.add_argument(
        "--base-config",
        type=Path,
        default=Path("configs/train_phase2_loss_only_debug.json"),
        help="Legacy or Phase 2A debug config without rainfall conditioning.",
    )
    parser.add_argument("--input-steps", type=int, default=12)
    parser.add_argument("--pred-steps", type=int, default=12)
    parser.add_argument("--height", type=int, default=32)
    parser.add_argument("--width", type=int, default=32)
    parser.add_argument("--batch-size", type=int, default=2)
    args = parser.parse_args()

    base_config = load_json(args.base_config)
    disabled_config = json.loads(json.dumps(base_config))
    disabled_config.setdefault("model", {})
    disabled_config["model"]["rainfall_conditioning"] = {
        "enabled": False,
        "mode": "temporal_gate",
        "hidden_channels": 64,
    }

    torch.manual_seed(7)
    legacy_model = build_model(base_config["model"]).eval()
    torch.manual_seed(7)
    disabled_model = build_model(disabled_config["model"]).eval()

    legacy_keys = list(legacy_model.state_dict().keys())
    disabled_keys = list(disabled_model.state_dict().keys())
    if legacy_keys != disabled_keys:
        raise RuntimeError("Disabled rainfall conditioning changed the model parameter structure.")

    with torch.no_grad():
        _, _, batch = make_synthetic_batch(
            batch_size=args.batch_size,
            input_steps=args.input_steps,
            pred_steps=args.pred_steps,
            height=args.height,
            width=args.width,
        )
        legacy_output = legacy_model(
            batch["past_flood"],
            batch["past_rainfall"],
            batch["future_rainfall"],
            batch["static_maps"],
        )
        disabled_output = disabled_model(
            batch["past_flood"],
            batch["past_rainfall"],
            batch["future_rainfall"],
            batch["static_maps"],
        )

    max_abs_diff = float((legacy_output - disabled_output).abs().max().item())
    payload = {
        "base_config": str(args.base_config),
        "parameter_structure_matches": True,
        "max_abs_diff": max_abs_diff,
        "identity_when_disabled": max_abs_diff == 0.0,
    }
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
