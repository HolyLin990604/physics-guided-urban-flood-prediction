from __future__ import annotations

from pathlib import Path
from typing import Dict

import torch
from torch import nn

from trainers.train import move_batch_to_device
from utils.metrics import compute_forecast_metrics, merge_metric_sums, scale_metric_sums
from utils.physics_losses import PhysicsLossController
from utils.visualization import save_batch_visualizations


@torch.no_grad()
def validate_one_epoch(
    model: nn.Module,
    dataloader,
    device: torch.device,
    criterion: nn.Module,
    *,
    wet_threshold: float,
    artifact_dir: str | Path | None = None,
    max_visualizations: int = 0,
    physics_controller: PhysicsLossController | None = None,
    visualization_config: dict | None = None,
) -> Dict[str, float]:
    model.eval()
    metric_sums: Dict[str, float] = {}
    total_batches = 0
    visualized = 0

    for batch_idx, batch in enumerate(dataloader):
        total_batches += 1
        batch = move_batch_to_device(batch, device)
        prediction = model(
            batch["past_flood"],
            batch["past_rainfall"],
            batch["future_rainfall"],
            batch["static_maps"],
        )
        if prediction.shape != batch["future_flood"].shape:
            raise ValueError(
                f"Validation prediction shape {tuple(prediction.shape)} does not match "
                f"target shape {tuple(batch['future_flood'].shape)}."
            )
        data_loss = criterion(prediction, batch["future_flood"])
        physics_loss = torch.zeros((), device=device, dtype=prediction.dtype)
        physics_metrics: Dict[str, float] = {}
        if physics_controller is not None:
            physics_loss, physics_metrics = physics_controller.compute(prediction, batch["future_flood"], batch)
        loss = data_loss + physics_loss
        batch_metrics = compute_forecast_metrics(prediction, batch["future_flood"], wet_threshold=wet_threshold)
        batch_metrics["loss"] = float(loss.item())
        batch_metrics["data_loss"] = float(data_loss.item())
        batch_metrics.update(physics_metrics)
        merge_metric_sums(metric_sums, batch_metrics)

        if artifact_dir is not None and visualized < max_visualizations:
            save_batch_visualizations(
                prediction=prediction,
                target=batch["future_flood"],
                output_dir=Path(artifact_dir) / f"val_batch_{batch_idx:04d}",
                metadata=batch.get("metadata"),
                timeseries_config=visualization_config,
            )
            visualized += 1

    return scale_metric_sums(metric_sums, total_batches)
