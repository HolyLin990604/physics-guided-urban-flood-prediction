from __future__ import annotations

from typing import List

import torch
from torch import nn

from models.blocks import SpatialDecoder, SpatialEncoder, TemporalConvNet, assert_rank, assert_same_spatial


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

        future_seed = temporal_context.unsqueeze(1) + rainfall_embed + step_embed
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
