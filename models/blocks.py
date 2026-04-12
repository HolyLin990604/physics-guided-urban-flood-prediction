from __future__ import annotations

from typing import List, Sequence, Tuple

import torch
from torch import nn


def assert_rank(name: str, tensor: torch.Tensor, expected_rank: int) -> None:
    if tensor.ndim != expected_rank:
        raise ValueError(
            f"Expected `{name}` to have rank {expected_rank}, got shape {tuple(tensor.shape)}."
        )


def assert_same_spatial(name_a: str, tensor_a: torch.Tensor, name_b: str, tensor_b: torch.Tensor) -> None:
    if tuple(tensor_a.shape[-2:]) != tuple(tensor_b.shape[-2:]):
        raise ValueError(
            f"Spatial size mismatch between `{name_a}` {tuple(tensor_a.shape)} and "
            f"`{name_b}` {tuple(tensor_b.shape)}."
        )


def _make_group_norm(num_channels: int, max_groups: int = 8) -> nn.GroupNorm:
    for groups in range(min(max_groups, num_channels), 0, -1):
        if num_channels % groups == 0:
            return nn.GroupNorm(groups, num_channels)
    raise ValueError(f"Could not construct GroupNorm for num_channels={num_channels}.")


class ConvNormAct(nn.Module):
    def __init__(
        self,
        in_channels: int,
        out_channels: int,
        *,
        kernel_size: int = 3,
        stride: int = 1,
        padding: int | None = None,
    ) -> None:
        super().__init__()
        if padding is None:
            padding = kernel_size // 2
        self.block = nn.Sequential(
            nn.Conv2d(in_channels, out_channels, kernel_size, stride=stride, padding=padding, bias=False),
            _make_group_norm(out_channels),
            nn.SiLU(inplace=True),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.block(x)


class ResidualConvBlock(nn.Module):
    def __init__(self, in_channels: int, out_channels: int) -> None:
        super().__init__()
        self.conv1 = ConvNormAct(in_channels, out_channels)
        self.conv2 = nn.Sequential(
            nn.Conv2d(out_channels, out_channels, kernel_size=3, padding=1, bias=False),
            _make_group_norm(out_channels),
        )
        self.shortcut = (
            nn.Identity()
            if in_channels == out_channels
            else nn.Conv2d(in_channels, out_channels, kernel_size=1, bias=False)
        )
        self.act = nn.SiLU(inplace=True)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        residual = self.shortcut(x)
        out = self.conv1(x)
        out = self.conv2(out)
        return self.act(out + residual)


class DownsampleBlock(nn.Module):
    def __init__(self, in_channels: int, out_channels: int) -> None:
        super().__init__()
        self.down = nn.Conv2d(in_channels, out_channels, kernel_size=3, stride=2, padding=1, bias=False)
        self.norm = _make_group_norm(out_channels)
        self.act = nn.SiLU(inplace=True)
        self.residual = ResidualConvBlock(out_channels, out_channels)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.act(self.norm(self.down(x)))
        return self.residual(x)


class UpsampleBlock(nn.Module):
    def __init__(self, in_channels: int, skip_channels: int, out_channels: int) -> None:
        super().__init__()
        self.up = nn.ConvTranspose2d(in_channels, out_channels, kernel_size=2, stride=2)
        self.block = ResidualConvBlock(out_channels + skip_channels, out_channels)

    def forward(self, x: torch.Tensor, skip: torch.Tensor) -> torch.Tensor:
        x = self.up(x)
        if tuple(x.shape[-2:]) != tuple(skip.shape[-2:]):
            raise ValueError(
                f"Upsample skip mismatch: upsampled tensor {tuple(x.shape)} vs skip {tuple(skip.shape)}."
            )
        x = torch.cat([x, skip], dim=1)
        return self.block(x)


class SpatialEncoder(nn.Module):
    def __init__(self, in_channels: int, base_channels: int = 16, levels: int = 3) -> None:
        super().__init__()
        if levels < 1:
            raise ValueError(f"levels must be >= 1, got {levels}.")

        self.stem = ResidualConvBlock(in_channels, base_channels)
        self.down_blocks = nn.ModuleList()
        self.skip_channels: List[int] = [base_channels]

        current_channels = base_channels
        for _ in range(levels):
            next_channels = current_channels * 2
            self.down_blocks.append(DownsampleBlock(current_channels, next_channels))
            current_channels = next_channels
            self.skip_channels.append(current_channels)

        self.bottleneck = ResidualConvBlock(current_channels, current_channels)
        self.out_channels = current_channels

    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, List[torch.Tensor]]:
        assert_rank("encoder_input", x, 4)
        skips: List[torch.Tensor] = []
        x = self.stem(x)
        skips.append(x)
        for block in self.down_blocks:
            x = block(x)
            skips.append(x)
        x = self.bottleneck(x)
        return x, skips


class SpatialDecoder(nn.Module):
    def __init__(self, bottleneck_channels: int, skip_channels: Sequence[int], out_channels: int = 1) -> None:
        super().__init__()
        if not skip_channels:
            raise ValueError("skip_channels cannot be empty.")

        reversed_skips = list(reversed(skip_channels[:-1]))
        current_channels = bottleneck_channels
        self.up_blocks = nn.ModuleList()
        for skip_ch in reversed_skips:
            out_ch = max(skip_ch, 16)
            self.up_blocks.append(UpsampleBlock(current_channels, skip_ch, out_ch))
            current_channels = out_ch
        self.head = nn.Conv2d(current_channels, out_channels, kernel_size=1)

    def forward(self, x: torch.Tensor, skip_features: Sequence[torch.Tensor]) -> torch.Tensor:
        assert_rank("decoder_input", x, 4)
        if len(skip_features) != len(self.up_blocks):
            raise ValueError(
                f"Decoder expected {len(self.up_blocks)} skip tensors, got {len(skip_features)}."
            )
        for block, skip in zip(self.up_blocks, skip_features):
            x = block(x, skip)
        return self.head(x)


class Chomp1d(nn.Module):
    def __init__(self, chomp_size: int) -> None:
        super().__init__()
        self.chomp_size = chomp_size

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        if self.chomp_size == 0:
            return x
        return x[:, :, :-self.chomp_size].contiguous()


class TemporalBlock(nn.Module):
    def __init__(
        self,
        in_channels: int,
        out_channels: int,
        *,
        kernel_size: int,
        dilation: int,
        dropout: float,
    ) -> None:
        super().__init__()
        padding = (kernel_size - 1) * dilation
        self.net = nn.Sequential(
            nn.Conv1d(in_channels, out_channels, kernel_size, padding=padding, dilation=dilation),
            Chomp1d(padding),
            nn.SiLU(inplace=True),
            nn.Dropout(dropout),
            nn.Conv1d(out_channels, out_channels, kernel_size, padding=padding, dilation=dilation),
            Chomp1d(padding),
            nn.SiLU(inplace=True),
            nn.Dropout(dropout),
        )
        self.downsample = (
            nn.Identity() if in_channels == out_channels else nn.Conv1d(in_channels, out_channels, kernel_size=1)
        )
        self.out_act = nn.SiLU(inplace=True)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        assert_rank("temporal_block_input", x, 3)
        out = self.net(x)
        residual = self.downsample(x)
        if out.shape != residual.shape:
            raise ValueError(
                f"Temporal residual mismatch: block output {tuple(out.shape)} vs residual {tuple(residual.shape)}."
            )
        return self.out_act(out + residual)


class TemporalConvNet(nn.Module):
    def __init__(
        self,
        in_channels: int,
        channel_sequence: Sequence[int],
        *,
        kernel_size: int = 3,
        dropout: float = 0.1,
    ) -> None:
        super().__init__()
        if not channel_sequence:
            raise ValueError("channel_sequence must contain at least one channel size.")
        layers = []
        current = in_channels
        for level, out_channels in enumerate(channel_sequence):
            layers.append(
                TemporalBlock(
                    current,
                    out_channels,
                    kernel_size=kernel_size,
                    dilation=2**level,
                    dropout=dropout,
                )
            )
            current = out_channels
        self.network = nn.Sequential(*layers)
        self.out_channels = current

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        assert_rank("temporal_net_input", x, 3)
        return self.network(x)
