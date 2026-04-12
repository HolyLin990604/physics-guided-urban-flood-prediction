from __future__ import annotations

from typing import Dict, Tuple

import numpy as np


SUPPORTED_ALIGNMENT_MODES: Tuple[str, ...] = (
    "piecewise_constant",
    "linear",
    "mass_preserving",
    "repeat_if_integer_ratio",
)


def align_rainfall_sequence(
    rainfall: np.ndarray,
    target_steps: int,
    *,
    mode: str,
) -> np.ndarray:
    rainfall = np.asarray(rainfall, dtype=np.float32)
    _validate_alignment_inputs(rainfall, target_steps, mode)

    if rainfall.shape[0] == target_steps:
        return rainfall.astype(np.float32, copy=False)
    if rainfall.shape[0] == 1:
        if mode == "mass_preserving":
            return np.repeat(rainfall / target_steps, target_steps).astype(np.float32, copy=False)
        return np.repeat(rainfall, target_steps).astype(np.float32, copy=False)

    if mode == "piecewise_constant":
        return _piecewise_constant_alignment(rainfall, target_steps)
    if mode == "linear":
        return _linear_alignment(rainfall, target_steps)
    if mode == "mass_preserving":
        return _mass_preserving_alignment(rainfall, target_steps)
    if mode == "repeat_if_integer_ratio":
        return _repeat_if_integer_ratio_alignment(rainfall, target_steps)

    raise ValueError(
        f"Unsupported rainfall alignment mode '{mode}'. Expected one of {SUPPORTED_ALIGNMENT_MODES}."
    )


def summarize_alignment_change(raw_rainfall: np.ndarray, aligned_rainfall: np.ndarray) -> Dict[str, float]:
    raw_rainfall = np.asarray(raw_rainfall, dtype=np.float32)
    aligned_rainfall = np.asarray(aligned_rainfall, dtype=np.float32)
    raw_sum = float(raw_rainfall.sum())
    aligned_sum = float(aligned_rainfall.sum())
    return {
        "raw_steps": int(raw_rainfall.shape[0]),
        "aligned_steps": int(aligned_rainfall.shape[0]),
        "raw_sum": raw_sum,
        "aligned_sum": aligned_sum,
        "sum_difference": aligned_sum - raw_sum,
        "sum_ratio": aligned_sum / raw_sum if raw_sum != 0.0 else float("nan"),
    }


def _validate_alignment_inputs(rainfall: np.ndarray, target_steps: int, mode: str) -> None:
    if rainfall.ndim != 1:
        raise ValueError(
            f"Rainfall alignment expects a 1D rainfall series, got shape {rainfall.shape}."
        )
    if rainfall.shape[0] <= 0:
        raise ValueError("Rainfall series is empty; cannot align an empty sequence.")
    if target_steps <= 0:
        raise ValueError(f"target_steps must be positive, got {target_steps}.")
    if mode not in SUPPORTED_ALIGNMENT_MODES:
        raise ValueError(
            f"Unsupported rainfall alignment mode '{mode}'. Expected one of {SUPPORTED_ALIGNMENT_MODES}."
        )


def _piecewise_constant_alignment(rainfall: np.ndarray, target_steps: int) -> np.ndarray:
    source_idx = np.floor(np.arange(target_steps, dtype=np.float32) * rainfall.shape[0] / target_steps)
    source_idx = np.clip(source_idx.astype(np.int64), 0, rainfall.shape[0] - 1)
    return rainfall[source_idx].astype(np.float32, copy=False)


def _linear_alignment(rainfall: np.ndarray, target_steps: int) -> np.ndarray:
    source_x = np.linspace(0.0, 1.0, num=rainfall.shape[0], dtype=np.float32)
    target_x = np.linspace(0.0, 1.0, num=target_steps, dtype=np.float32)
    return np.interp(target_x, source_x, rainfall).astype(np.float32, copy=False)


def _repeat_if_integer_ratio_alignment(rainfall: np.ndarray, target_steps: int) -> np.ndarray:
    if target_steps % rainfall.shape[0] != 0:
        raise ValueError(
            "repeat_if_integer_ratio requires flood_steps to be an integer multiple of rainfall_steps, "
            f"but got flood_steps={target_steps} and rainfall_steps={rainfall.shape[0]}."
        )
    repeat_factor = target_steps // rainfall.shape[0]
    return np.repeat(rainfall, repeat_factor).astype(np.float32, copy=False)


def _mass_preserving_alignment(rainfall: np.ndarray, target_steps: int) -> np.ndarray:
    """
    Redistribute rainfall mass from coarse bins to target bins by interval overlap.

    Scientific note:
    This preserves cumulative rainfall exactly up to floating-point error if the raw
    rainfall values are interpreted as rainfall amount per original time bin. That is
    still a modeling assumption, but it is a more honest choice when sum preservation
    matters downstream.
    """

    source_steps = rainfall.shape[0]
    source_edges = np.linspace(0.0, float(source_steps), num=source_steps + 1, dtype=np.float32)
    target_edges = np.linspace(0.0, float(source_steps), num=target_steps + 1, dtype=np.float32)
    aligned = np.zeros(target_steps, dtype=np.float32)

    source_idx = 0
    for target_idx in range(target_steps):
        start = float(target_edges[target_idx])
        end = float(target_edges[target_idx + 1])
        while source_idx < source_steps - 1 and float(source_edges[source_idx + 1]) <= start:
            source_idx += 1

        current_idx = source_idx
        while current_idx < source_steps and float(source_edges[current_idx]) < end:
            overlap_start = max(start, float(source_edges[current_idx]))
            overlap_end = min(end, float(source_edges[current_idx + 1]))
            overlap = overlap_end - overlap_start
            if overlap > 0.0:
                aligned[target_idx] += rainfall[current_idx] * overlap
            current_idx += 1

    return aligned.astype(np.float32, copy=False)
