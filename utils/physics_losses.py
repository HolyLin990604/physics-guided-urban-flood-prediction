from __future__ import annotations

from typing import Dict, Tuple

import torch
import torch.nn.functional as F


class PhysicsLossController:
    """
    Optional physics-inspired loss terms for Stage 2B.

    Scientific note:
    These terms are guidance and surrogate constraints, not a full hydrodynamic closure.
    They do not reconstruct the shallow-water equations and should be described as
    regularization or physically motivated guidance rather than full physics enforcement.
    """

    def __init__(self, config: Dict | None = None) -> None:
        self.config = config or {}

    def compute(
        self,
        prediction: torch.Tensor,
        target: torch.Tensor,
        batch: Dict[str, torch.Tensor],
    ) -> Tuple[torch.Tensor, Dict[str, float]]:
        device = prediction.device
        total = torch.zeros((), device=device, dtype=prediction.dtype)
        metrics: Dict[str, float] = {}

        total, metrics = self._apply_term(
            name="non_negativity",
            total=total,
            metrics=metrics,
            loss_fn=lambda cfg: self._non_negativity_loss(prediction),
        )
        total, metrics = self._apply_term(
            name="wet_dry_consistency",
            total=total,
            metrics=metrics,
            loss_fn=lambda cfg: self._wet_dry_consistency_loss(prediction, target, cfg),
        )
        total, metrics = self._apply_term(
            name="rainfall_depth_consistency",
            total=total,
            metrics=metrics,
            loss_fn=lambda cfg: self._rainfall_depth_consistency_loss(prediction, batch["future_rainfall"], cfg),
        )
        total, metrics = self._apply_term(
            name="topography_regularization",
            total=total,
            metrics=metrics,
            loss_fn=lambda cfg: self._topography_regularization(prediction, batch["static_maps"], cfg),
        )
        total, metrics = self._apply_term(
            name="continuity_inspired",
            total=total,
            metrics=metrics,
            loss_fn=lambda cfg: self._continuity_inspired_loss(prediction, batch["future_rainfall"], cfg),
        )

        metrics["physics_total"] = float(total.detach().item())
        return total, metrics

    def _apply_term(self, *, name: str, total: torch.Tensor, metrics: Dict[str, float], loss_fn):
        cfg = self.config.get(name, {})
        enabled = bool(cfg.get("enabled", False))
        weight = float(cfg.get("weight", 0.0))
        if not enabled or weight <= 0.0:
            metrics[name] = 0.0
            metrics[f"{name}_weighted"] = 0.0
            return total, metrics

        value = loss_fn(cfg)
        weighted = value * weight
        metrics[name] = float(value.detach().item())
        metrics[f"{name}_weighted"] = float(weighted.detach().item())
        return total + weighted, metrics

    @staticmethod
    def _non_negativity_loss(prediction: torch.Tensor) -> torch.Tensor:
        return torch.relu(-prediction).mean()

    @staticmethod
    def _wet_dry_consistency_loss(
        prediction: torch.Tensor,
        target: torch.Tensor,
        cfg: Dict,
    ) -> torch.Tensor:
        threshold = float(cfg.get("threshold", 0.05))
        temperature = float(cfg.get("temperature", 0.02))
        target_wet = (target > threshold).float()
        pred_wet_logits = (prediction - threshold) / max(temperature, 1e-6)
        return F.binary_cross_entropy_with_logits(pred_wet_logits, target_wet)

    @staticmethod
    def _rainfall_depth_consistency_loss(
        prediction: torch.Tensor,
        future_rainfall: torch.Tensor,
        cfg: Dict,
    ) -> torch.Tensor:
        """
        Guidance, not constraint:
        compares normalized cumulative rainfall with normalized cumulative positive storage change.
        This is intentionally unit-agnostic because rainfall and flood depth are not directly
        converted through a trusted hydrodynamic mapping in this baseline.
        """

        eps = float(cfg.get("eps", 1e-6))
        rain = future_rainfall.squeeze(-1).clamp_min(0.0)
        storage = prediction.clamp_min(0.0).mean(dim=(2, 3, 4))
        storage_delta = torch.cat([storage[:, :1], torch.relu(storage[:, 1:] - storage[:, :-1])], dim=1)

        rain_cum = torch.cumsum(rain, dim=1)
        storage_cum = torch.cumsum(storage_delta, dim=1)
        rain_norm = rain_cum / (rain_cum[:, -1:].clamp_min(eps))
        storage_norm = storage_cum / (storage_cum[:, -1:].clamp_min(eps))
        return F.l1_loss(storage_norm, rain_norm)

    @staticmethod
    def _topography_regularization(
        prediction: torch.Tensor,
        static_maps: torch.Tensor,
        cfg: Dict,
    ) -> torch.Tensor:
        """
        Guidance, not constraint:
        discourages higher predicted ponding on locally higher DEM cells than their lower
        neighbors, but does not model momentum or drainage explicitly.
        """

        dem_channel = int(cfg.get("dem_channel", 0))
        eps = float(cfg.get("eps", 1e-6))
        dem = static_maps[:, dem_channel]
        water = prediction.clamp_min(0.0).squeeze(2)

        dx_dem = dem[..., 1:] - dem[..., :-1]
        dy_dem = dem[..., 1:, :] - dem[..., :-1, :]
        dx_water = water[..., 1:] - water[..., :-1]
        dy_water = water[..., 1:, :] - water[..., :-1, :]

        dx_penalty = torch.relu(dx_water * torch.sign(dx_dem).unsqueeze(1))
        dy_penalty = torch.relu(dy_water * torch.sign(dy_dem).unsqueeze(1))

        dx_weight = dx_dem.abs().unsqueeze(1) / dx_dem.abs().mean().clamp_min(eps)
        dy_weight = dy_dem.abs().unsqueeze(1) / dy_dem.abs().mean().clamp_min(eps)
        return (dx_penalty * dx_weight).mean() + (dy_penalty * dy_weight).mean()

    @staticmethod
    def _continuity_inspired_loss(
        prediction: torch.Tensor,
        future_rainfall: torch.Tensor,
        cfg: Dict,
    ) -> torch.Tensor:
        """
        Continuity-inspired guidance:
        fits a per-sample proportionality between positive storage increments and rainfall
        forcing, then penalizes mismatched temporal structure. This is not a closed mass
        balance because lateral fluxes, infiltration, and drainage are not explicitly modeled.
        """

        eps = float(cfg.get("eps", 1e-6))
        rain = future_rainfall.squeeze(-1).clamp_min(0.0)
        storage = prediction.clamp_min(0.0).mean(dim=(2, 3, 4))
        storage_increments = torch.cat([storage[:, :1], storage[:, 1:] - storage[:, :-1]], dim=1)
        positive_increments = torch.relu(storage_increments)

        scale = (positive_increments.sum(dim=1, keepdim=True) / rain.sum(dim=1, keepdim=True).clamp_min(eps)).detach()
        return F.mse_loss(positive_increments, scale * rain)
