from __future__ import annotations

from typing import List

import torch
from torch import nn

from models.blocks import SpatialDecoder, SpatialEncoder, TemporalConvNet, assert_rank, assert_same_spatial


class RainfallConditionedTemporalGate(nn.Module):
    """
    Lightweight per-step conditioning for future temporal features.

    The gate maps future rainfall to a channel-wise residual scaling term and applies it
    to the repeated temporal context before the future TCN. The last layer is zero-
    initialized so the enabled module starts from near-identity behavior.
    """

    def __init__(
        self,
        *,
        rainfall_channels: int,
        feature_channels: int,
        hidden_channels: int,
        residual_alpha: float | None = None,
        conditioned_fraction: float = 1.0,
        learned_selective: bool = False,
        response_split: bool = False,
    ) -> None:
        super().__init__()
        self.residual_alpha = residual_alpha
        self.learned_selective = learned_selective
        self.response_split = response_split
        conditioned_channels = int(feature_channels * conditioned_fraction)
        self.conditioned_channels = conditioned_channels
        self.memory_channels = feature_channels - conditioned_channels
        conditioned_mask = torch.zeros(feature_channels, dtype=torch.float32)
        if conditioned_channels > 0:
            conditioned_mask[-conditioned_channels:] = 1.0
        self.register_buffer("conditioned_mask", conditioned_mask.view(1, 1, feature_channels, 1, 1))
        self.gate_mlp = nn.Sequential(
            nn.Linear(rainfall_channels, hidden_channels),
            nn.SiLU(inplace=True),
            nn.Linear(hidden_channels, conditioned_channels if response_split else feature_channels),
        )
        final_linear = self.gate_mlp[-1]
        if not isinstance(final_linear, nn.Linear):
            raise TypeError("Expected final layer of rainfall gate MLP to be nn.Linear.")
        nn.init.zeros_(final_linear.weight)
        nn.init.zeros_(final_linear.bias)
        if self.learned_selective:
            selector_prior_logits = torch.full((feature_channels,), -8.0, dtype=torch.float32)
            if conditioned_channels > 0:
                selector_prior_logits[-conditioned_channels:] = 8.0
            self.register_buffer(
                "selector_prior_logits",
                selector_prior_logits.view(1, 1, feature_channels, 1, 1),
            )
            self.selector_logits = nn.Parameter(torch.zeros(1, 1, feature_channels, 1, 1))
        else:
            self.register_buffer("selector_prior_logits", torch.zeros(1, 1, feature_channels, 1, 1))
            self.selector_logits = None

    def _get_selector(self, *, device: torch.device, dtype: torch.dtype) -> torch.Tensor:
        if self.selector_logits is None:
            return self.conditioned_mask.to(device=device, dtype=dtype)
        selector_logits = self.selector_prior_logits.to(device=device, dtype=dtype) + self.selector_logits.to(
            device=device,
            dtype=dtype,
        )
        return torch.sigmoid(selector_logits)

    def forward(self, temporal_context: torch.Tensor, future_rainfall: torch.Tensor) -> torch.Tensor:
        assert_rank("temporal_context", temporal_context, 4)
        assert_rank("future_rainfall", future_rainfall, 3)

        batch_size, channels, _, _ = temporal_context.shape
        rain_batch, future_steps, rain_channels = future_rainfall.shape
        if rain_batch != batch_size:
            raise ValueError(
                f"future_rainfall batch size {rain_batch} does not match temporal_context batch size {batch_size}."
            )

        gate = self.gate_mlp(future_rainfall.reshape(batch_size * future_steps, rain_channels))
        if self.response_split:
            if self.conditioned_channels == 0:
                return temporal_context.unsqueeze(1).expand(-1, future_steps, -1, -1, -1)

            gate = torch.tanh(gate).view(batch_size, future_steps, self.conditioned_channels, 1, 1)
            if self.residual_alpha is not None:
                gate = gate * self.residual_alpha

            memory_context = temporal_context[:, : self.memory_channels]
            response_context = temporal_context[:, self.memory_channels :]
            conditioned_response = response_context.unsqueeze(1) * (1.0 + gate)
            if self.memory_channels == 0:
                return conditioned_response
            preserved_memory = memory_context.unsqueeze(1).expand(-1, future_steps, -1, -1, -1)
            return torch.cat([preserved_memory, conditioned_response], dim=2)

        gate = torch.tanh(gate).view(batch_size, future_steps, channels, 1, 1)
        if self.residual_alpha is not None:
            gate = gate * self.residual_alpha
        gate = gate * self._get_selector(device=gate.device, dtype=gate.dtype)
        return temporal_context.unsqueeze(1) * (1.0 + gate)


class UNetTCNForecaster(nn.Module):
    """
    Baseline spatiotemporal flood forecaster.

    Tensor flow:
    1. Concatenate each past flood frame with static maps and encode spatially with a shared U-Net encoder.
    2. Inject past rainfall into bottleneck features and run a TCN over time for each bottleneck cell.
    3. Combine temporal context with future rainfall and step embeddings, then refine future bottleneck seeds with a second TCN.
    4. Decode each future bottleneck with U-Net skip summaries to produce future flood maps.

    Scientific note:
    The future bottleneck seeds are latent forecast-conditioned representations. They are
    useful decoder inputs, but they are not explicit hydrodynamic state variables.
    """

    def __init__(
        self,
        *,
        flood_channels: int = 1,
        static_channels: int = 3,
        rainfall_channels: int = 1,
        out_channels: int = 1,
        base_channels: int = 16,
        encoder_levels: int = 3,
        temporal_hidden_channels: int = 128,
        temporal_layers: int = 4,
        temporal_kernel_size: int = 3,
        dropout: float = 0.1,
        skip_fusion_mode: str = "temporal_mean",
        rainfall_conditioning: dict | None = None,
    ) -> None:
        super().__init__()
        self.flood_channels = flood_channels
        self.static_channels = static_channels
        self.rainfall_channels = rainfall_channels
        self.out_channels = out_channels
        self.skip_fusion_mode = skip_fusion_mode

        self.encoder = SpatialEncoder(
            in_channels=flood_channels + static_channels,
            base_channels=base_channels,
            levels=encoder_levels,
        )
        bottleneck_channels = self.encoder.out_channels
        temporal_sequence = [temporal_hidden_channels] * max(temporal_layers - 1, 0) + [bottleneck_channels]
        self.past_rainfall_embed = self._make_rainfall_embedder(rainfall_channels, bottleneck_channels)
        self.future_rainfall_embed = self._make_rainfall_embedder(rainfall_channels, bottleneck_channels)
        self.future_step_embed = nn.Sequential(
            nn.Linear(1, bottleneck_channels),
            nn.SiLU(inplace=True),
            nn.Linear(bottleneck_channels, bottleneck_channels),
        )
        self.past_temporal_tcn = TemporalConvNet(
            in_channels=bottleneck_channels,
            channel_sequence=temporal_sequence,
            kernel_size=temporal_kernel_size,
            dropout=dropout,
        )
        self.future_temporal_tcn = TemporalConvNet(
            in_channels=bottleneck_channels,
            channel_sequence=temporal_sequence,
            kernel_size=temporal_kernel_size,
            dropout=dropout,
        )
        self.decoder = SpatialDecoder(
            bottleneck_channels=bottleneck_channels,
            skip_channels=self.encoder.skip_channels,
            out_channels=out_channels,
        )
        self._validate_skip_fusion_mode()
        self.rainfall_conditioning = self._normalize_rainfall_conditioning(
            rainfall_conditioning=rainfall_conditioning,
            bottleneck_channels=bottleneck_channels,
            temporal_hidden_channels=temporal_hidden_channels,
        )
        if self.rainfall_conditioning["enabled"]:
            self.temporal_rainfall_gate = RainfallConditionedTemporalGate(
                rainfall_channels=rainfall_channels,
                feature_channels=bottleneck_channels,
                hidden_channels=self.rainfall_conditioning["hidden_channels"],
                residual_alpha=self.rainfall_conditioning["residual_alpha"],
                conditioned_fraction=self.rainfall_conditioning["conditioned_fraction"],
                learned_selective=self.rainfall_conditioning["mode"] == "temporal_gate_residual_learned_selective",
                response_split=self.rainfall_conditioning["mode"] == "temporal_gate_residual_response_split",
            )
        else:
            self.temporal_rainfall_gate = None
        if self.skip_fusion_mode == "learned_weighted":
            self.skip_fusion_layers = nn.ModuleList(
                [nn.Linear(channels, 1) for channels in self.encoder.skip_channels]
            )
        else:
            self.skip_fusion_layers = None

    def _validate_skip_fusion_mode(self) -> None:
        allowed = {"temporal_mean", "last_step", "learned_weighted"}
        if self.skip_fusion_mode not in allowed:
            raise ValueError(
                f"Unsupported skip_fusion_mode '{self.skip_fusion_mode}'. Expected one of {sorted(allowed)}."
            )

    @staticmethod
    def _make_rainfall_embedder(in_channels: int, out_channels: int) -> nn.Sequential:
        return nn.Sequential(
            nn.Linear(in_channels, out_channels),
            nn.SiLU(inplace=True),
            nn.Linear(out_channels, out_channels),
        )

    @staticmethod
    def _normalize_rainfall_conditioning(
        *,
        rainfall_conditioning: dict | None,
        bottleneck_channels: int,
        temporal_hidden_channels: int,
    ) -> dict:
        config = dict(rainfall_conditioning or {})
        mode = config.get("mode", "temporal_gate")
        normalized = {
            "enabled": bool(config.get("enabled", False)),
            "mode": mode,
            "hidden_channels": int(config.get("hidden_channels", max(bottleneck_channels // 2, 16))),
            "residual_alpha": None,
            "conditioned_fraction": 1.0,
        }
        allowed_modes = {
            "temporal_gate",
            "temporal_gate_residual",
            "temporal_gate_residual_partial",
            "temporal_gate_residual_learned_selective",
            "temporal_gate_residual_response_split",
        }
        if normalized["mode"] not in allowed_modes:
            raise ValueError(
                f"Unsupported rainfall_conditioning mode '{normalized['mode']}'. "
                f"Expected one of {sorted(allowed_modes)}."
            )
        if normalized["hidden_channels"] <= 0:
            raise ValueError("rainfall_conditioning.hidden_channels must be > 0.")
        if normalized["hidden_channels"] > max(temporal_hidden_channels, bottleneck_channels) * 4:
            raise ValueError("rainfall_conditioning.hidden_channels is unexpectedly large.")
        if normalized["mode"] == "temporal_gate_residual":
            if "residual_alpha" not in config:
                raise ValueError(
                    "rainfall_conditioning.residual_alpha must be set explicitly for 'temporal_gate_residual'."
                )
            normalized["residual_alpha"] = float(config["residual_alpha"])
            if not 0.0 <= normalized["residual_alpha"] <= 1.0:
                raise ValueError("rainfall_conditioning.residual_alpha must be in [0, 1].")
        if normalized["mode"] in {
            "temporal_gate_residual_partial",
            "temporal_gate_residual_learned_selective",
            "temporal_gate_residual_response_split",
        }:
            if "residual_alpha" not in config:
                raise ValueError(
                    "rainfall_conditioning.residual_alpha must be set explicitly for "
                    f"'{normalized['mode']}'."
                )
            if "conditioned_fraction" not in config:
                raise ValueError(
                    "rainfall_conditioning.conditioned_fraction must be set explicitly for "
                    f"'{normalized['mode']}'."
                )
            normalized["residual_alpha"] = float(config["residual_alpha"])
            if not 0.0 <= normalized["residual_alpha"] <= 1.0:
                raise ValueError("rainfall_conditioning.residual_alpha must be in [0, 1].")
            normalized["conditioned_fraction"] = float(config["conditioned_fraction"])
            if not 0.0 <= normalized["conditioned_fraction"] <= 1.0:
                raise ValueError("rainfall_conditioning.conditioned_fraction must be in [0, 1].")
        return normalized

    def forward(
        self,
        past_flood: torch.Tensor,
        past_rainfall: torch.Tensor,
        future_rainfall: torch.Tensor,
        static_maps: torch.Tensor,
    ) -> torch.Tensor:
        assert_rank("past_flood", past_flood, 5)
        assert_rank("past_rainfall", past_rainfall, 3)
        assert_rank("future_rainfall", future_rainfall, 3)
        assert_rank("static_maps", static_maps, 4)

        batch_size, input_steps, flood_channels, height, width = past_flood.shape
        future_steps = future_rainfall.shape[1]

        if flood_channels != self.flood_channels:
            raise ValueError(
                f"Expected past_flood channels={self.flood_channels}, got {flood_channels}."
            )
        if past_rainfall.shape[:2] != (batch_size, input_steps):
            raise ValueError(
                f"past_rainfall shape {tuple(past_rainfall.shape)} is incompatible with "
                f"past_flood shape {tuple(past_flood.shape)}."
            )
        if past_rainfall.shape[-1] != self.rainfall_channels:
            raise ValueError(
                f"Expected past_rainfall channels={self.rainfall_channels}, got {past_rainfall.shape[-1]}."
            )
        if future_rainfall.shape[0] != batch_size or future_rainfall.shape[-1] != self.rainfall_channels:
            raise ValueError(
                f"future_rainfall shape {tuple(future_rainfall.shape)} is incompatible with "
                f"batch size {batch_size} and rainfall_channels={self.rainfall_channels}."
            )
        if static_maps.shape[0] != batch_size or static_maps.shape[1] != self.static_channels:
            raise ValueError(
                f"Expected static_maps shape [B, {self.static_channels}, H, W], got {tuple(static_maps.shape)}."
            )
        assert_same_spatial("past_flood", past_flood[:, 0], "static_maps", static_maps)

        expanded_static = static_maps.unsqueeze(1).expand(-1, input_steps, -1, -1, -1)
        encoder_input = torch.cat([past_flood, expanded_static], dim=2)
        encoder_input = encoder_input.reshape(batch_size * input_steps, -1, height, width)

        bottleneck, skip_sequence = self.encoder(encoder_input)
        bottleneck_channels, bottleneck_h, bottleneck_w = bottleneck.shape[1:]
        bottleneck = bottleneck.view(batch_size, input_steps, bottleneck_channels, bottleneck_h, bottleneck_w)

        past_rainfall_embed = self.past_rainfall_embed(
            past_rainfall.reshape(batch_size * input_steps, self.rainfall_channels)
        )
        past_rainfall_embed = past_rainfall_embed.view(batch_size, input_steps, bottleneck_channels, 1, 1)
        bottleneck = bottleneck + past_rainfall_embed

        temporal_context = self._run_temporal_encoder(bottleneck)
        future_latents = self._build_future_latents(temporal_context, future_rainfall, future_steps)

        aggregated_skips = self._aggregate_skip_sequence(skip_sequence, batch_size, input_steps)
        decoder_skips = [
            skip.unsqueeze(1).expand(-1, future_steps, -1, -1, -1).reshape(batch_size * future_steps, *skip.shape[1:])
            for skip in reversed(aggregated_skips[:-1])
        ]

        decoder_input = future_latents.reshape(batch_size * future_steps, bottleneck_channels, bottleneck_h, bottleneck_w)
        decoded = self.decoder(decoder_input, decoder_skips)
        return decoded.view(batch_size, future_steps, self.out_channels, height, width)

    def _run_temporal_encoder(self, bottleneck_seq: torch.Tensor) -> torch.Tensor:
        batch_size, steps, channels, bottleneck_h, bottleneck_w = bottleneck_seq.shape
        sequence = bottleneck_seq.permute(0, 3, 4, 2, 1).reshape(batch_size * bottleneck_h * bottleneck_w, channels, steps)
        encoded = self.past_temporal_tcn(sequence)
        last_context = encoded[:, :, -1]
        return last_context.view(batch_size, bottleneck_h, bottleneck_w, channels).permute(0, 3, 1, 2).contiguous()

    def _build_future_latents(
        self,
        temporal_context: torch.Tensor,
        future_rainfall: torch.Tensor,
        future_steps: int,
    ) -> torch.Tensor:
        batch_size, channels, bottleneck_h, bottleneck_w = temporal_context.shape
        if self.temporal_rainfall_gate is None:
            conditioned_context = temporal_context.unsqueeze(1).expand(-1, future_steps, -1, -1, -1)
        else:
            conditioned_context = self.temporal_rainfall_gate(temporal_context, future_rainfall)

        rainfall_embed = self.future_rainfall_embed(
            future_rainfall.reshape(batch_size * future_steps, self.rainfall_channels)
        )
        rainfall_embed = rainfall_embed.view(batch_size, future_steps, channels, 1, 1)

        step_positions = torch.linspace(
            0.0,
            1.0,
            steps=future_steps,
            device=temporal_context.device,
            dtype=temporal_context.dtype,
        ).view(1, future_steps, 1)
        step_embed = self.future_step_embed(step_positions.reshape(future_steps, 1))
        step_embed = step_embed.view(1, future_steps, channels, 1, 1)

        future_seed = conditioned_context + rainfall_embed + step_embed
        future_seed = future_seed.permute(0, 3, 4, 2, 1).reshape(batch_size * bottleneck_h * bottleneck_w, channels, future_steps)
        refined = self.future_temporal_tcn(future_seed)
        return refined.view(batch_size, bottleneck_h, bottleneck_w, channels, future_steps).permute(0, 4, 3, 1, 2).contiguous()

    def _aggregate_skip_sequence(
        self,
        skip_sequence: List[torch.Tensor],
        batch_size: int,
        input_steps: int,
    ) -> List[torch.Tensor]:
        aggregated: List[torch.Tensor] = []
        for idx, skip in enumerate(skip_sequence):
            if skip.shape[0] != batch_size * input_steps:
                raise ValueError(
                    f"Skip tensor {idx} has unexpected batch dimension {skip.shape[0]} for "
                    f"batch_size={batch_size} and input_steps={input_steps}."
                )
            reshaped = skip.view(batch_size, input_steps, *skip.shape[1:])
            if self.skip_fusion_mode == "temporal_mean":
                aggregated_skip = reshaped.mean(dim=1)
            elif self.skip_fusion_mode == "last_step":
                aggregated_skip = reshaped[:, -1]
            else:
                if self.skip_fusion_layers is None:
                    raise RuntimeError("learned_weighted skip fusion requested without fusion layers.")
                pooled = reshaped.mean(dim=(-1, -2))
                weights = torch.softmax(self.skip_fusion_layers[idx](pooled).squeeze(-1), dim=1)
                aggregated_skip = torch.sum(
                    reshaped * weights[:, :, None, None, None],
                    dim=1,
                )
            aggregated.append(aggregated_skip)
        return aggregated
