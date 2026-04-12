from __future__ import annotations

from pathlib import Path
from typing import Dict

import torch
from torch import nn

from trainers.train import move_batch_to_device
from utils.metrics import compute_forecast_metrics, merge_metric_sums, scale_metric_sums
from utils.visualization import save_batch_visualizations


@torch.no_grad()
def test_model(
    model: nn.Module,
    dataloader,
    device: torch.device,
    *,
    wet_threshold: float,
    artifact_dir: str | Path,
    visualization_config: dict | None = None,
) -> Dict[str, float]:
    model.eval()
    metric_sums: Dict[str, float] = {}
    total_batches = 0
    artifact_dir = Path(artifact_dir)
    artifact_dir.mkdir(parents=True, exist_ok=True)

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
                f"Test prediction shape {tuple(prediction.shape)} does not match "
                f"target shape {tuple(batch['future_flood'].shape)}."
            )
        batch_metrics = compute_forecast_metrics(prediction, batch["future_flood"], wet_threshold=wet_threshold)
        merge_metric_sums(metric_sums, batch_metrics)

        save_batch_visualizations(
            prediction=prediction,
            target=batch["future_flood"],
            output_dir=artifact_dir / f"test_batch_{batch_idx:04d}",
            metadata=batch.get("metadata"),
            timeseries_config=visualization_config,
        )

    return scale_metric_sums(metric_sums, total_batches)
