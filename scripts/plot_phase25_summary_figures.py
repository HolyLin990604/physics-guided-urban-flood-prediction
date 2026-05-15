from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = Path("analysis/phase25_target_wet_recall_comparison/figures")

SEEDS = ("seed123", "seed42", "seed202")

STANDARD_METRIC_DELTAS = {
    "RMSE": {
        "seed123": -0.004895,
        "seed42": -0.013841,
        "seed202": -0.002434,
    },
    "MAE": {
        "seed123": -0.000989,
        "seed42": -0.003476,
        "seed202": -0.000092,
    },
    "wet_dry_iou": {
        "seed123": 0.073429,
        "seed42": 0.121764,
        "seed202": 0.034817,
    },
    "rollout_stability": {
        "seed123": 0.000394,
        "seed42": 0.001689,
        "seed202": 0.001022,
    },
    "step_rmse_std": {
        "seed123": -0.000423,
        "seed42": -0.001733,
        "seed202": -0.001058,
    },
}

PHYSICAL_METRIC_DELTAS = {
    "false_dry_rate": {
        "seed123": -0.113020,
        "seed42": -0.152555,
        "seed202": -0.068388,
    },
    "wet_area_contraction": {
        "seed123": -0.081389,
        "seed42": -0.106194,
        "seed202": -0.049730,
    },
    "relative_volume_bias": {
        "seed123": 0.094689,
        "seed42": 0.157211,
        "seed202": 0.063380,
    },
    "peak_depth_underprediction": {
        "seed123": 0.002614,
        "seed42": -0.037269,
        "seed202": -0.010232,
    },
    "false_wet_rate": {
        "seed123": 0.005015,
        "seed42": 0.002350,
        "seed202": 0.004168,
    },
    "connectivity_loss_indicator": {
        "seed123": 0.078947,
        "seed42": 0.157895,
        "seed202": 0.000000,
    },
}


def resolve_repo_path(path: Path) -> Path:
    return path if path.is_absolute() else REPO_ROOT / path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Plot Phase 25 versus Phase 10 summary delta figures from fixed three-seed values."
    )
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    return parser.parse_args()


def plot_grouped_delta_bars(
    deltas: dict[str, dict[str, float]],
    title: str,
    ylabel: str,
    output_path: Path,
) -> None:
    metrics = list(deltas)
    x_positions = list(range(len(metrics)))
    bar_width = 0.24
    seed_offsets = {
        "seed123": -bar_width,
        "seed42": 0.0,
        "seed202": bar_width,
    }

    fig_width = max(10.0, len(metrics) * 1.35)
    fig, ax = plt.subplots(figsize=(fig_width, 5.8))

    for seed in SEEDS:
        values = [deltas[metric][seed] for metric in metrics]
        positions = [x + seed_offsets[seed] for x in x_positions]
        ax.bar(positions, values, width=bar_width, label=seed)

    ax.axhline(0.0, color="black", linewidth=0.8)
    ax.set_title(title)
    ax.set_ylabel(ylabel)
    ax.set_xlabel("Metric")
    ax.set_xticks(x_positions)
    ax.set_xticklabels(metrics, rotation=25, ha="right")
    ax.legend(title="Seed")
    ax.grid(axis="y", alpha=0.25)

    fig.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=200, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    args = parse_args()
    output_dir = resolve_repo_path(args.output_dir)

    plot_grouped_delta_bars(
        STANDARD_METRIC_DELTAS,
        "Phase 25 - Phase 10 Standard Test Metric Deltas",
        "Delta (Phase 25 - Phase 10)",
        output_dir / "phase25_standard_metric_deltas_three_seeds.png",
    )
    plot_grouped_delta_bars(
        PHYSICAL_METRIC_DELTAS,
        "Aligned Phase 25 - Phase 10 Physical Metric Deltas",
        "Delta (Phase 25 - Phase 10)",
        output_dir / "phase25_aligned_physical_deltas_three_seeds.png",
    )

    print(f"Wrote figures to {output_dir}")


if __name__ == "__main__":
    main()
