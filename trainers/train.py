from __future__ import annotations

from typing import Dict

import numpy as np
import torch
from torch import nn

from utils.metrics import compute_forecast_metrics, merge_metric_sums, scale_metric_sums
from utils.physics_losses import PhysicsLossController


def build_loss(loss_name: str) -> nn.Module:
    normalized = loss_name.lower()
    if normalized == "mse":
        return nn.MSELoss()
    if normalized == "l1":
        return nn.L1Loss()
    if normalized == "smooth_l1":
        return nn.SmoothL1Loss(beta=0.05)
    raise ValueError(f"Unsupported loss '{loss_name}'. Expected one of: mse, l1, smooth_l1.")


def move_batch_to_device(batch: Dict[str, torch.Tensor], device: torch.device) -> Dict[str, torch.Tensor]:
    required = ("past_flood", "past_rainfall", "future_rainfall", "static_maps", "future_flood")
    missing = [key for key in required if key not in batch]
    if missing:
        raise KeyError(f"Batch is missing required keys: {missing}")

    moved: Dict[str, torch.Tensor] = {}
    for key, value in batch.items():
        if isinstance(value, torch.Tensor):
            moved[key] = value.to(device, non_blocking=True).float()
        elif isinstance(value, np.ndarray):
            moved[key] = torch.from_numpy(value).to(device, non_blocking=True).float()
        else:
            moved[key] = value
    return moved


def train_one_epoch(
    model: nn.Module,
    dataloader,
    optimizer: torch.optim.Optimizer,
    device: torch.device,
    criterion: nn.Module,
    *,
    wet_threshold: float,
    scaler: torch.cuda.amp.GradScaler | None = None,
    grad_clip_norm: float | None = None,
    use_amp: bool = True,
    physics_controller: PhysicsLossController | None = None,
) -> Dict[str, float]:
    model.train()
    metric_sums: Dict[str, float] = {}
    total_batches = 0

    for batch in dataloader:
        total_batches += 1
        batch = move_batch_to_device(batch, device)
        optimizer.zero_grad(set_to_none=True)

        amp_enabled = use_amp and device.type == "cuda"
        with torch.cuda.amp.autocast(enabled=amp_enabled):
            prediction = model(
                batch["past_flood"],
                batch["past_rainfall"],
                batch["future_rainfall"],
                batch["static_maps"],
            )
            if prediction.shape != batch["future_flood"].shape:
                raise ValueError(
                    f"Model output shape {tuple(prediction.shape)} does not match target shape "
                    f"{tuple(batch['future_flood'].shape)}."
                )
            data_loss = criterion(prediction, batch["future_flood"])
            physics_loss = torch.zeros((), device=device, dtype=prediction.dtype)
            physics_metrics: Dict[str, float] = {}
            if physics_controller is not None:
                physics_loss, physics_metrics = physics_controller.compute(prediction, batch["future_flood"], batch)
            loss = data_loss + physics_loss

        if scaler is not None and amp_enabled:
            scaler.scale(loss).backward()
            if grad_clip_norm is not None:
                scaler.unscale_(optimizer)
                torch.nn.utils.clip_grad_norm_(model.parameters(), grad_clip_norm)
            scaler.step(optimizer)
            scaler.update()
        else:
            loss.backward()
            if grad_clip_norm is not None:
                torch.nn.utils.clip_grad_norm_(model.parameters(), grad_clip_norm)
            optimizer.step()

        batch_metrics = compute_forecast_metrics(prediction.detach(), batch["future_flood"], wet_threshold=wet_threshold)
        batch_metrics["loss"] = float(loss.detach().item())
        batch_metrics["data_loss"] = float(data_loss.detach().item())
        batch_metrics.update(physics_metrics)
        merge_metric_sums(metric_sums, batch_metrics)

    return scale_metric_sums(metric_sums, total_batches)
