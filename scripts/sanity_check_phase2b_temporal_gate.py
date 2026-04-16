from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from torch import nn


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
    residual_config = json.loads(json.dumps(base_config))
    residual_config.setdefault("model", {})
    residual_config["model"]["rainfall_conditioning"] = {
        "enabled": True,
        "mode": "temporal_gate_residual",
        "hidden_channels": 64,
        "residual_alpha": 0.10,
    }
    residual_identity_config = json.loads(json.dumps(residual_config))
    residual_identity_config["model"]["rainfall_conditioning"]["residual_alpha"] = 0.0
    partial_config = json.loads(json.dumps(base_config))
    partial_config.setdefault("model", {})
    partial_config["model"]["rainfall_conditioning"] = {
        "enabled": True,
        "mode": "temporal_gate_residual_partial",
        "hidden_channels": 64,
        "residual_alpha": 0.10,
        "conditioned_fraction": 0.50,
    }
    partial_identity_config = json.loads(json.dumps(partial_config))
    partial_identity_config["model"]["rainfall_conditioning"]["residual_alpha"] = 0.0
    partial_zero_fraction_config = json.loads(json.dumps(partial_config))
    partial_zero_fraction_config["model"]["rainfall_conditioning"]["conditioned_fraction"] = 0.0
    learned_selective_config = json.loads(json.dumps(base_config))
    learned_selective_config.setdefault("model", {})
    learned_selective_config["model"]["rainfall_conditioning"] = {
        "enabled": True,
        "mode": "temporal_gate_residual_learned_selective",
        "hidden_channels": 64,
        "residual_alpha": 0.10,
        "conditioned_fraction": 0.50,
    }
    learned_selective_identity_config = json.loads(json.dumps(learned_selective_config))
    learned_selective_identity_config["model"]["rainfall_conditioning"]["residual_alpha"] = 0.0

    torch.manual_seed(7)
    legacy_model = build_model(base_config["model"]).eval()
    torch.manual_seed(7)
    disabled_model = build_model(disabled_config["model"]).eval()
    torch.manual_seed(7)
    residual_model = build_model(residual_config["model"]).eval()
    torch.manual_seed(7)
    residual_identity_model = build_model(residual_identity_config["model"]).eval()
    torch.manual_seed(7)
    partial_model = build_model(partial_config["model"]).eval()
    torch.manual_seed(7)
    partial_identity_model = build_model(partial_identity_config["model"]).eval()
    torch.manual_seed(7)
    partial_zero_fraction_model = build_model(partial_zero_fraction_config["model"]).eval()
    torch.manual_seed(7)
    learned_selective_model = build_model(learned_selective_config["model"]).eval()
    torch.manual_seed(7)
    learned_selective_identity_model = build_model(learned_selective_identity_config["model"]).eval()
    residual_model.load_state_dict(disabled_model.state_dict(), strict=False)
    residual_identity_model.load_state_dict(disabled_model.state_dict(), strict=False)
    partial_model.load_state_dict(disabled_model.state_dict(), strict=False)
    partial_identity_model.load_state_dict(disabled_model.state_dict(), strict=False)
    partial_zero_fraction_model.load_state_dict(disabled_model.state_dict(), strict=False)
    learned_selective_model.load_state_dict(disabled_model.state_dict(), strict=False)
    learned_selective_identity_model.load_state_dict(disabled_model.state_dict(), strict=False)

    legacy_keys = list(legacy_model.state_dict().keys())
    disabled_keys = list(disabled_model.state_dict().keys())
    if legacy_keys != disabled_keys:
        raise RuntimeError("Disabled rainfall conditioning changed the model parameter structure.")

    final_linear = residual_identity_model.temporal_rainfall_gate.gate_mlp[-1]
    if not isinstance(final_linear, nn.Linear):
        raise TypeError("Expected rainfall gate final layer to be nn.Linear.")
    with torch.no_grad():
        final_linear.weight.fill_(0.5)
        final_linear.bias.fill_(0.25)
    residual_final_linear = residual_model.temporal_rainfall_gate.gate_mlp[-1]
    if not isinstance(residual_final_linear, nn.Linear):
        raise TypeError("Expected rainfall gate final layer to be nn.Linear.")
    with torch.no_grad():
        residual_final_linear.weight.fill_(0.5)
        residual_final_linear.bias.fill_(0.25)
    partial_active_final_linear = partial_model.temporal_rainfall_gate.gate_mlp[-1]
    if not isinstance(partial_active_final_linear, nn.Linear):
        raise TypeError("Expected rainfall gate final layer to be nn.Linear.")
    with torch.no_grad():
        partial_active_final_linear.weight.fill_(0.5)
        partial_active_final_linear.bias.fill_(0.25)
    partial_final_linear = partial_identity_model.temporal_rainfall_gate.gate_mlp[-1]
    if not isinstance(partial_final_linear, nn.Linear):
        raise TypeError("Expected rainfall gate final layer to be nn.Linear.")
    with torch.no_grad():
        partial_final_linear.weight.fill_(0.5)
        partial_final_linear.bias.fill_(0.25)

    partial_zero_fraction_final_linear = partial_zero_fraction_model.temporal_rainfall_gate.gate_mlp[-1]
    if not isinstance(partial_zero_fraction_final_linear, nn.Linear):
        raise TypeError("Expected rainfall gate final layer to be nn.Linear.")
    with torch.no_grad():
        partial_zero_fraction_final_linear.weight.fill_(0.5)
        partial_zero_fraction_final_linear.bias.fill_(0.25)
    learned_selective_final_linear = learned_selective_model.temporal_rainfall_gate.gate_mlp[-1]
    if not isinstance(learned_selective_final_linear, nn.Linear):
        raise TypeError("Expected rainfall gate final layer to be nn.Linear.")
    with torch.no_grad():
        learned_selective_final_linear.weight.fill_(0.5)
        learned_selective_final_linear.bias.fill_(0.25)
    learned_selective_identity_final_linear = learned_selective_identity_model.temporal_rainfall_gate.gate_mlp[-1]
    if not isinstance(learned_selective_identity_final_linear, nn.Linear):
        raise TypeError("Expected rainfall gate final layer to be nn.Linear.")
    with torch.no_grad():
        learned_selective_identity_final_linear.weight.fill_(0.5)
        learned_selective_identity_final_linear.bias.fill_(0.25)

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
        residual_output = residual_model(
            batch["past_flood"],
            batch["past_rainfall"],
            batch["future_rainfall"],
            batch["static_maps"],
        )
        residual_identity_output = residual_identity_model(
            batch["past_flood"],
            batch["past_rainfall"],
            batch["future_rainfall"],
            batch["static_maps"],
        )
        partial_output = partial_model(
            batch["past_flood"],
            batch["past_rainfall"],
            batch["future_rainfall"],
            batch["static_maps"],
        )
        partial_identity_output = partial_identity_model(
            batch["past_flood"],
            batch["past_rainfall"],
            batch["future_rainfall"],
            batch["static_maps"],
        )
        partial_zero_fraction_output = partial_zero_fraction_model(
            batch["past_flood"],
            batch["past_rainfall"],
            batch["future_rainfall"],
            batch["static_maps"],
        )
        learned_selective_output = learned_selective_model(
            batch["past_flood"],
            batch["past_rainfall"],
            batch["future_rainfall"],
            batch["static_maps"],
        )
        learned_selective_identity_output = learned_selective_identity_model(
            batch["past_flood"],
            batch["past_rainfall"],
            batch["future_rainfall"],
            batch["static_maps"],
        )

    max_abs_diff = float((legacy_output - disabled_output).abs().max().item())
    residual_identity_diff = float((disabled_output - residual_identity_output).abs().max().item())
    partial_identity_diff = float((disabled_output - partial_identity_output).abs().max().item())
    partial_zero_fraction_diff = float((disabled_output - partial_zero_fraction_output).abs().max().item())
    learned_selective_identity_diff = float((disabled_output - learned_selective_identity_output).abs().max().item())
    learned_selective_init_diff = float((partial_output - learned_selective_output).abs().max().item())
    partial_mask_channels = int(partial_model.temporal_rainfall_gate.conditioned_mask.sum().item())
    learned_selective_selector = learned_selective_model.temporal_rainfall_gate._get_selector(
        device=learned_selective_model.temporal_rainfall_gate.conditioned_mask.device,
        dtype=learned_selective_model.temporal_rainfall_gate.conditioned_mask.dtype,
    )
    learned_selective_selector_prior_diff = float(
        (learned_selective_selector - learned_selective_model.temporal_rainfall_gate.conditioned_mask).abs().max().item()
    )
    payload = {
        "base_config": str(args.base_config),
        "parameter_structure_matches": True,
        "max_abs_diff": max_abs_diff,
        "identity_when_disabled": max_abs_diff == 0.0,
        "residual_mode_output_shape": list(residual_output.shape),
        "residual_mode_finite": bool(torch.isfinite(residual_output).all().item()),
        "residual_alpha_zero_max_abs_diff": residual_identity_diff,
        "residual_alpha_zero_is_identity": residual_identity_diff == 0.0,
        "partial_mode_output_shape": list(partial_output.shape),
        "partial_mode_finite": bool(torch.isfinite(partial_output).all().item()),
        "partial_conditioned_channels": partial_mask_channels,
        "partial_residual_alpha_zero_max_abs_diff": partial_identity_diff,
        "partial_residual_alpha_zero_is_identity": partial_identity_diff == 0.0,
        "partial_fraction_zero_max_abs_diff": partial_zero_fraction_diff,
        "partial_fraction_zero_is_identity": partial_zero_fraction_diff == 0.0,
        "learned_selective_mode_output_shape": list(learned_selective_output.shape),
        "learned_selective_mode_finite": bool(torch.isfinite(learned_selective_output).all().item()),
        "learned_selective_residual_alpha_zero_max_abs_diff": learned_selective_identity_diff,
        "learned_selective_residual_alpha_zero_is_identity": learned_selective_identity_diff == 0.0,
        "learned_selective_init_max_abs_diff_vs_partial": learned_selective_init_diff,
        "learned_selective_selector_prior_max_abs_diff": learned_selective_selector_prior_diff,
    }
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
