from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


DEFAULT_BATCH_DIR = Path("evaluation_test") / "test_batch_0000"
DEFAULT_OUTPUT_DIR = Path("assets") / "images" / "final"
DEFAULT_REGION = (40, 88, 40, 88)
DEFAULT_STEP = 11


def _load_batch_artifacts(run_dir: Path) -> tuple[dict, np.lib.npyio.NpzFile]:
    batch_dir = run_dir / DEFAULT_BATCH_DIR
    maps_path = batch_dir / "forecast_maps.npz"
    summary_path = batch_dir / "summary.json"
    metrics_path = run_dir / "evaluation_test" / "metrics.json"

    missing = [path for path in (maps_path, summary_path, metrics_path) if not path.exists()]
    if missing:
        missing_text = ", ".join(str(path) for path in missing)
        raise FileNotFoundError(f"Missing required input artifacts: {missing_text}")

    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    return summary, np.load(maps_path)


def _save_map_comparison(
    *,
    contender_a: np.lib.npyio.NpzFile,
    contender_b: np.lib.npyio.NpzFile,
    label_a: str,
    label_b: str,
    step: int,
    output_path: Path,
    seed_tag: str,
) -> None:
    target = contender_a["target"][0, step, 0]
    pred_a = contender_a["prediction"][0, step, 0]
    pred_b = contender_b["prediction"][0, step, 0]
    err_a = np.abs(pred_a - target)
    err_b = np.abs(pred_b - target)

    main_vmin = min(target.min(), pred_a.min(), pred_b.min())
    main_vmax = max(target.max(), pred_a.max(), pred_b.max())
    err_vmax = max(err_a.max(), err_b.max())

    fig, axes = plt.subplots(1, 5, figsize=(20, 4))

    for ax, img, title in zip(
        axes[:3],
        [target, pred_a, pred_b],
        ["Target", label_a, label_b],
    ):
        im = ax.imshow(img, cmap="viridis", vmin=main_vmin, vmax=main_vmax)
        ax.set_title(title)
        ax.axis("off")
        plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)

    for ax, img, title in zip(
        axes[3:],
        [err_a, err_b],
        [f"{label_a} Error", f"{label_b} Error"],
    ):
        im = ax.imshow(img, cmap="viridis", vmin=0.0, vmax=err_vmax)
        ax.set_title(title)
        ax.axis("off")
        plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)

    plt.suptitle(f"{label_a} vs {label_b} spatial comparison ({seed_tag}, forecast step {step})")
    plt.tight_layout()
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)


def _save_timeseries_comparison(
    *,
    contender_a: np.lib.npyio.NpzFile,
    contender_b: np.lib.npyio.NpzFile,
    label_a: str,
    label_b: str,
    region: tuple[int, int, int, int],
    output_path: Path,
    seed_tag: str,
) -> None:
    r0, r1, c0, c1 = region
    target = contender_a["target"][0, :, 0, r0:r1, c0:c1].mean(axis=(1, 2))
    pred_a = contender_a["prediction"][0, :, 0, r0:r1, c0:c1].mean(axis=(1, 2))
    pred_b = contender_b["prediction"][0, :, 0, r0:r1, c0:c1].mean(axis=(1, 2))
    steps = np.arange(1, len(target) + 1)

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(steps, target, marker="o", label="Target")
    ax.plot(steps, pred_a, marker="s", label=label_a)
    ax.plot(steps, pred_b, marker="^", label=label_b)
    ax.set_xlabel("Forecast step")
    ax.set_ylabel("Region-averaged water depth")
    ax.set_title(f"Region-averaged process comparison ({seed_tag})")
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate final Phase 4 qualitative comparisons from existing evaluation artifacts.")
    parser.add_argument("--run-a", type=Path, required=True, help="Run directory for contender A.")
    parser.add_argument("--run-b", type=Path, required=True, help="Run directory for contender B.")
    parser.add_argument("--label-a", default="M3 f025", help="Display label for contender A.")
    parser.add_argument("--label-b", default="Phase 3.3 af025", help="Display label for contender B.")
    parser.add_argument("--seed-tag", required=True, help="Seed tag used in output file names, for example seed202.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR, help="Directory for generated figure outputs.")
    parser.add_argument("--step", type=int, default=DEFAULT_STEP, help="Forecast step index for spatial comparison.")
    parser.add_argument("--row-range", nargs=2, type=int, default=[DEFAULT_REGION[0], DEFAULT_REGION[1]])
    parser.add_argument("--col-range", nargs=2, type=int, default=[DEFAULT_REGION[2], DEFAULT_REGION[3]])
    args = parser.parse_args()

    summary_a, batch_a = _load_batch_artifacts(args.run_a.expanduser().resolve())
    summary_b, batch_b = _load_batch_artifacts(args.run_b.expanduser().resolve())

    if summary_a["prediction_shape"] != summary_b["prediction_shape"]:
        raise ValueError(
            "Contender outputs are not shape-compatible: "
            f"{summary_a['prediction_shape']} vs {summary_b['prediction_shape']}"
        )

    output_dir = args.output_dir.expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    maps_output = output_dir / f"m3_vs_phase33_af025_{args.seed_tag}_maps.png"
    timeseries_output = output_dir / f"m3_vs_phase33_af025_{args.seed_tag}_timeseries.png"
    region = (args.row_range[0], args.row_range[1], args.col_range[0], args.col_range[1])

    _save_map_comparison(
        contender_a=batch_a,
        contender_b=batch_b,
        label_a=args.label_a,
        label_b=args.label_b,
        step=args.step,
        output_path=maps_output,
        seed_tag=args.seed_tag,
    )
    _save_timeseries_comparison(
        contender_a=batch_a,
        contender_b=batch_b,
        label_a=args.label_a,
        label_b=args.label_b,
        region=region,
        output_path=timeseries_output,
        seed_tag=args.seed_tag,
    )

    print(json.dumps({"maps": str(maps_output), "timeseries": str(timeseries_output)}, indent=2))


if __name__ == "__main__":
    main()
