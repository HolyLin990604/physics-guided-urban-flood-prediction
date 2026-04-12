from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import torch


def _to_numpy(tensor: torch.Tensor) -> np.ndarray:
    return tensor.detach().cpu().numpy().astype(np.float32, copy=False)


def save_batch_visualizations(
    *,
    prediction: torch.Tensor,
    target: torch.Tensor,
    output_dir: str | Path,
    metadata: Any = None,
    max_batch_items: int = 2,
    max_forecast_steps: int = 4,
    timeseries_config: dict | None = None,
) -> None:
    if prediction.shape != target.shape:
        raise ValueError(
            f"Visualization expected prediction and target to match, got {tuple(prediction.shape)} and {tuple(target.shape)}."
        )
    if prediction.ndim != 5:
        raise ValueError(
            f"Visualization expected tensors with rank 5 [B, T, C, H, W], got {tuple(prediction.shape)}."
        )

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    pred_np = _to_numpy(prediction)
    target_np = _to_numpy(target)
    error_np = np.abs(pred_np - target_np)
    np.savez_compressed(output_dir / "forecast_maps.npz", prediction=pred_np, target=target_np, error=error_np)

    summary = {
        "prediction_shape": list(pred_np.shape),
        "target_shape": list(target_np.shape),
        "error_shape": list(error_np.shape),
        "metadata": metadata,
        "timeseries_config": timeseries_config,
    }
    (output_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    timeseries_payload = build_depth_timeseries_payload(
        prediction=pred_np,
        target=target_np,
        config=timeseries_config or {"mode": "region_average"},
    )
    (output_dir / "depth_timeseries.json").write_text(json.dumps(timeseries_payload, indent=2), encoding="utf-8")

    try:
        import matplotlib.pyplot as plt
    except ImportError:
        return

    num_batch = min(pred_np.shape[0], max_batch_items)
    num_steps = min(pred_np.shape[1], max_forecast_steps)
    for batch_idx in range(num_batch):
        for step_idx in range(num_steps):
            fig, axes = plt.subplots(1, 3, figsize=(12, 4))
            axes[0].imshow(pred_np[batch_idx, step_idx, 0], cmap="Blues")
            axes[0].set_title("Prediction")
            axes[1].imshow(target_np[batch_idx, step_idx, 0], cmap="Blues")
            axes[1].set_title("Target")
            axes[2].imshow(error_np[batch_idx, step_idx, 0], cmap="Reds")
            axes[2].set_title("Absolute Error")
            for ax in axes:
                ax.axis("off")
            fig.tight_layout()
            fig.savefig(output_dir / f"sample_{batch_idx:02d}_step_{step_idx:02d}.png", dpi=150)
            plt.close(fig)

    save_depth_timeseries_figure(timeseries_payload, output_dir / "depth_timeseries.png")


def build_depth_timeseries_payload(
    *,
    prediction: np.ndarray,
    target: np.ndarray,
    config: dict,
) -> dict:
    if prediction.ndim != 5 or target.ndim != 5:
        raise ValueError(
            f"Time-series visualization expected rank-5 arrays, got {prediction.shape} and {target.shape}."
        )
    mode = config.get("mode", "region_average")
    batch_index = int(config.get("batch_index", 0))
    if batch_index < 0 or batch_index >= prediction.shape[0]:
        raise ValueError(f"Invalid batch_index {batch_index} for batch size {prediction.shape[0]}.")

    pred_series = prediction[batch_index, :, 0]
    target_series = target[batch_index, :, 0]
    payload = {"mode": mode, "batch_index": batch_index, "series": []}

    if mode == "region_average":
        row_range = config.get("row_range", [0, pred_series.shape[1]])
        col_range = config.get("col_range", [0, pred_series.shape[2]])
        r0, r1 = int(row_range[0]), int(row_range[1])
        c0, c1 = int(col_range[0]), int(col_range[1])
        if not (0 <= r0 < r1 <= pred_series.shape[1] and 0 <= c0 < c1 <= pred_series.shape[2]):
            raise ValueError(
                f"Invalid region_average bounds rows={row_range} cols={col_range} for frame shape {pred_series.shape[1:]}."
            )
        pred_values = pred_series[:, r0:r1, c0:c1].mean(axis=(1, 2))
        target_values = target_series[:, r0:r1, c0:c1].mean(axis=(1, 2))
        payload["series"].append(
            {
                "label": f"region_r{r0}_{r1}_c{c0}_{c1}",
                "prediction": pred_values.tolist(),
                "target": target_values.tolist(),
            }
        )
        return payload

    if mode == "pixels":
        pixel_coords = config.get("pixel_coords", [[64, 64]])
        for coord in pixel_coords:
            row, col = int(coord[0]), int(coord[1])
            if not (0 <= row < pred_series.shape[1] and 0 <= col < pred_series.shape[2]):
                raise ValueError(
                    f"Pixel coordinate {(row, col)} is out of bounds for frame shape {pred_series.shape[1:]}."
                )
            payload["series"].append(
                {
                    "label": f"pixel_{row}_{col}",
                    "prediction": pred_series[:, row, col].tolist(),
                    "target": target_series[:, row, col].tolist(),
                }
            )
        return payload

    raise ValueError(
        f"Unsupported timeseries visualization mode '{mode}'. Expected 'region_average' or 'pixels'."
    )


def save_depth_timeseries_figure(payload: dict, output_path: Path) -> None:
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        return

    fig, ax = plt.subplots(figsize=(8, 4))
    for series in payload["series"]:
        x = list(range(len(series["prediction"])))
        ax.plot(x, series["prediction"], label=f"{series['label']} pred")
        ax.plot(x, series["target"], linestyle="--", label=f"{series['label']} target")
    ax.set_xlabel("Forecast Step")
    ax.set_ylabel("Flood Depth")
    ax.set_title("Predicted vs Target Flood Depth")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
