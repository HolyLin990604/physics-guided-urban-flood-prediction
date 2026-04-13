from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, Iterable, Tuple

import torch
import torch.nn.functional as F


LossFn = Callable[[torch.Tensor, torch.Tensor, Dict[str, torch.Tensor], Dict], torch.Tensor]


@dataclass(frozen=True)
class PhysicsLossTerm:
    name: str
    loss_fn: LossFn

    def compute(
        self,
        prediction: torch.Tensor,
        target: torch.Tensor,
        batch: Dict[str, torch.Tensor],
        config: Dict,
    ) -> torch.Tensor:
        value = self.loss_fn(prediction, target, batch, config)
        if value.ndim != 0:
            raise ValueError(f"Physics loss '{self.name}' must return a scalar tensor, got shape {tuple(value.shape)}.")
        if not torch.isfinite(value):
            raise ValueError(f"Physics loss '{self.name}' produced a non-finite value: {float(value.detach().item())}.")
        return value


class PhysicsLossController:
    """
    Optional physics-inspired loss terms.

    Scientific note:
    These terms are guidance and surrogate constraints, not a full hydrodynamic closure.
    They do not reconstruct the shallow-water equations and should be described as
    regularization or physically motivated guidance rather than full physics enforcement.
    """

    _TERMS: Tuple[PhysicsLossTerm, ...] = ()

    def __init__(self, config: Dict | None = None) -> None:
        self.config = config or {}
        self.terms = self._build_term_registry()

    def compute(
        self,
        prediction: torch.Tensor,
        target: torch.Tensor,
        batch: Dict[str, torch.Tensor],
    ) -> Tuple[torch.Tensor, Dict[str, float]]:
        device = prediction.device
        total = torch.zeros((), device=device, dtype=prediction.dtype)
        metrics: Dict[str, float] = {}

        for term in self.terms:
            total, metrics = self._apply_term(
                term=term,
                prediction=prediction,
                target=target,
                batch=batch,
                total=total,
                metrics=metrics,
            )

        metrics["physics_total"] = float(total.detach().item())
        return total, metrics

    @classmethod
    def term_names(cls) -> Tuple[str, ...]:
        return tuple(term.name for term in cls._build_term_registry())

    @classmethod
    def _build_term_registry(cls) -> Tuple[PhysicsLossTerm, ...]:
        if cls._TERMS:
            return cls._TERMS
        cls._TERMS = (
            PhysicsLossTerm("non_negativity", cls._non_negativity_loss),
            PhysicsLossTerm("wet_dry_consistency", cls._wet_dry_consistency_loss),
            PhysicsLossTerm("rainfall_depth_consistency", cls._rainfall_depth_consistency_loss),
            PhysicsLossTerm("topography_regularization", cls._topography_regularization),
            PhysicsLossTerm("continuity_inspired", cls._continuity_inspired_loss),
        )
        return cls._TERMS

    def _apply_term(
        self,
        *,
        term: PhysicsLossTerm,
        prediction: torch.Tensor,
        target: torch.Tensor,
        batch: Dict[str, torch.Tensor],
        total: torch.Tensor,
        metrics: Dict[str, float],
    ) -> Tuple[torch.Tensor, Dict[str, float]]:
        cfg = self.config.get(term.name, {})
        enabled = bool(cfg.get("enabled", False))
        weight = float(cfg.get("weight", 0.0))
        if not enabled or weight <= 0.0:
            metrics[term.name] = 0.0
            metrics[f"{term.name}_weighted"] = 0.0
            return total, metrics

        value = term.compute(prediction, target, batch, cfg)
        weighted = value * weight
        metrics[term.name] = float(value.detach().item())
        metrics[f"{term.name}_weighted"] = float(weighted.detach().item())
        return total + weighted, metrics

    @staticmethod
    def _non_negativity_loss(
        prediction: torch.Tensor,
        _target: torch.Tensor,
        _batch: Dict[str, torch.Tensor],
        _cfg: Dict,
    ) -> torch.Tensor:
        return torch.relu(-prediction).mean()

    @staticmethod
    def _wet_dry_consistency_loss(
        prediction: torch.Tensor,
        target: torch.Tensor,
        _batch: Dict[str, torch.Tensor],
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
        _target: torch.Tensor,
        batch: Dict[str, torch.Tensor],
        cfg: Dict,
    ) -> torch.Tensor:
        """
        Stronger guidance, not a hard constraint:
        matches the normalized temporal response of positive predicted storage change
        to normalized future rainfall forcing while remaining robust to event magnitude.
        """

        future_rainfall = batch["future_rainfall"]
        eps = float(cfg.get("eps", 1e-6))
        normalization = str(cfg.get("normalization", "cumulative_l1")).lower()
        detach_scale = bool(cfg.get("detach_scale", False))
        smooth_positive_beta = float(cfg.get("smooth_positive_beta", 8.0))
        use_cumulative = bool(cfg.get("use_cumulative", True))

        rain = future_rainfall.squeeze(-1).clamp_min(0.0)
        storage = prediction.clamp_min(0.0).mean(dim=(2, 3, 4))
        storage_increments = torch.cat([storage[:, :1], storage[:, 1:] - storage[:, :-1]], dim=1)

        if smooth_positive_beta > 0.0:
            response = F.softplus(storage_increments * smooth_positive_beta) / smooth_positive_beta
        else:
            response = torch.relu(storage_increments)

        if normalization == "cumulative_l1":
            rain_reference = torch.cumsum(rain, dim=1) if use_cumulative else rain
            response_reference = torch.cumsum(response, dim=1) if use_cumulative else response
            rain_norm = rain_reference / rain_reference.abs().sum(dim=1, keepdim=True).clamp_min(eps)
            response_norm = response_reference / response_reference.abs().sum(dim=1, keepdim=True).clamp_min(eps)
            return F.l1_loss(response_norm, rain_norm)

        if normalization == "per_sample_scale":
            scale = response.sum(dim=1, keepdim=True) / rain.sum(dim=1, keepdim=True).clamp_min(eps)
            if detach_scale:
                scale = scale.detach()
            scaled_rain = scale * rain
            return F.smooth_l1_loss(response, scaled_rain, beta=float(cfg.get("beta", 0.05)))

        raise ValueError(
            "Unsupported rainfall_depth_consistency normalization "
            f"'{normalization}'. Expected 'cumulative_l1' or 'per_sample_scale'."
        )

    @staticmethod
    def _topography_regularization(
        prediction: torch.Tensor,
        _target: torch.Tensor,
        batch: Dict[str, torch.Tensor],
        cfg: Dict,
    ) -> torch.Tensor:
        """
        Guidance, not constraint:
        discourages higher predicted ponding on locally higher DEM cells than their lower
        neighbors, but does not model momentum or drainage explicitly.
        """

        static_maps = batch["static_maps"]
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
        _target: torch.Tensor,
        batch: Dict[str, torch.Tensor],
        cfg: Dict,
    ) -> torch.Tensor:
        """
        Continuity-inspired guidance:
        fits a per-sample proportionality between positive storage increments and rainfall
        forcing, then penalizes mismatched temporal structure. This is not a closed mass
        balance because lateral fluxes, infiltration, and drainage are not explicitly modeled.
        """

        future_rainfall = batch["future_rainfall"]
        eps = float(cfg.get("eps", 1e-6))
        rain = future_rainfall.squeeze(-1).clamp_min(0.0)
        storage = prediction.clamp_min(0.0).mean(dim=(2, 3, 4))
        storage_increments = torch.cat([storage[:, :1], storage[:, 1:] - storage[:, :-1]], dim=1)
        positive_increments = torch.relu(storage_increments)

        scale = (positive_increments.sum(dim=1, keepdim=True) / rain.sum(dim=1, keepdim=True).clamp_min(eps)).detach()
        return F.mse_loss(positive_increments, scale * rain)


def list_physics_losses() -> Iterable[str]:
    return PhysicsLossController.term_names()
