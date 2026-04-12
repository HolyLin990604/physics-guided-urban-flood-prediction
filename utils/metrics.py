from __future__ import annotations

from typing import Dict

import torch


def compute_forecast_metrics(
    prediction: torch.Tensor,
    target: torch.Tensor,
    *,
    wet_threshold: float = 0.05,
) -> Dict[str, float]:
    if prediction.shape != target.shape:
        raise ValueError(
            f"Metric inputs must have the same shape, got {tuple(prediction.shape)} and {tuple(target.shape)}."
        )
    if prediction.ndim != 5:
        raise ValueError(
            f"Expected prediction/target rank 5 [B, T, C, H, W], got {tuple(prediction.shape)}."
        )

    error = prediction - target
    rmse = torch.sqrt(torch.mean(error.pow(2)))
    mae = torch.mean(error.abs())

    pred_wet = prediction > wet_threshold
    target_wet = target > wet_threshold
    intersection = torch.logical_and(pred_wet, target_wet).float().sum()
    union = torch.logical_or(pred_wet, target_wet).float().sum()
    wet_dry_iou = (
        intersection / union
        if float(union.item()) > 0.0
        else torch.tensor(1.0, device=prediction.device)
    )

    step_rmse = torch.sqrt(torch.mean(error.pow(2), dim=(0, 2, 3, 4)))
    step_rmse_std = torch.std(step_rmse, unbiased=False)
    rollout_stability = 1.0 / (1.0 + step_rmse_std)

    return {
        "rmse": float(rmse.item()),
        "mae": float(mae.item()),
        "wet_dry_iou": float(wet_dry_iou.item()),
        "rollout_stability": float(rollout_stability.item()),
        "step_rmse_std": float(step_rmse_std.item()),
    }


def merge_metric_sums(metric_sums: Dict[str, float], metrics: Dict[str, float]) -> None:
    for key, value in metrics.items():
        metric_sums[key] = metric_sums.get(key, 0.0) + float(value)


def scale_metric_sums(metric_sums: Dict[str, float], count: int) -> Dict[str, float]:
    if count <= 0:
        raise ValueError(f"count must be positive, got {count}.")
    return {key: value / count for key, value in metric_sums.items()}
