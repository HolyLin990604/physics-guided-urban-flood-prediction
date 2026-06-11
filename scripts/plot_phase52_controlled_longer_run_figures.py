from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_METRICS_CSV = Path(
    "runs/phase52_full_downsample128_seed42_40e/metrics.csv"
)
DEFAULT_SUMMARY_JSON = Path(
    "analysis/phase52_controlled_128x128_seed42_longer_run/"
    "phase52_training_summary.json"
)
DEFAULT_OUTPUT_DIR = Path(
    "analysis/phase52_controlled_128x128_seed42_longer_run/figures"
)

COLORS = {
    "phase47": "#7A8793",
    "phase52": "#2F6B9A",
    "rmse": "#2F6B9A",
    "mae": "#2A7F78",
    "iou": "#C98200",
    "improvement": "#3C7D55",
    "dark": "#1F2933",
    "gray": "#65727E",
    "grid": "#D9DEE3",
    "white": "#FFFFFF",
}

TRAJECTORY_METRICS = (
    ("test_rmse", "Test RMSE", COLORS["rmse"]),
    ("test_mae", "Test MAE", COLORS["mae"]),
    ("test_wet_dry_iou", "Test wet/dry IoU", COLORS["iou"]),
)

COMPARISON_METRICS = (
    ("test_rmse", "Test RMSE", "lower"),
    ("test_mae", "Test MAE", "lower"),
    ("test_wet_dry_iou", "Wet/dry IoU", "higher"),
    ("test_rollout_stability", "Rollout stability", "higher"),
    ("test_step_rmse_std", "Step RMSE std", "lower"),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Generate Phase 52 controlled longer-run figures from existing metrics "
            "and summary artifacts. This script does not train or modify results."
        )
    )
    parser.add_argument("--metrics-csv", type=Path, default=DEFAULT_METRICS_CSV)
    parser.add_argument("--summary-json", type=Path, default=DEFAULT_SUMMARY_JSON)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--dpi", type=int, default=200)
    return parser.parse_args()


def resolve_repo_path(path: Path) -> Path:
    return path if path.is_absolute() else REPO_ROOT / path


def read_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise FileNotFoundError(f"Missing required summary JSON: {path}")
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"Expected a JSON object in {path}")
    return value


def as_finite_float(value: Any, field: str, source: Path) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(
            f"Field {field!r} in {source} is not numeric: {value!r}"
        ) from exc
    if not math.isfinite(number):
        raise ValueError(f"Field {field!r} in {source} is not finite: {value!r}")
    return number


def read_metrics(path: Path) -> list[dict[str, float]]:
    if not path.is_file():
        raise FileNotFoundError(f"Missing required metrics CSV: {path}")
    required = {"epoch", *(metric for metric, _, _ in COMPARISON_METRICS)}
    rows: list[dict[str, float]] = []
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        missing = required.difference(reader.fieldnames or [])
        if missing:
            raise ValueError(f"Missing CSV columns in {path}: {sorted(missing)}")
        for row_number, row in enumerate(reader, start=2):
            rows.append(
                {
                    field: as_finite_float(row[field], field, path)
                    for field in required
                }
            )
            if not rows[-1]["epoch"].is_integer():
                raise ValueError(
                    f"Non-integer epoch on row {row_number} of {path}: "
                    f"{rows[-1]['epoch']!r}"
                )
    if not rows:
        raise ValueError(f"Required metrics CSV is empty: {path}")
    return rows


def assert_close(name: str, left: float, right: float) -> None:
    if not math.isclose(left, right, rel_tol=1e-10, abs_tol=1e-13):
        raise ValueError(f"Inconsistent {name}: CSV={left!r}, JSON={right!r}")


def validate_inputs(
    rows: list[dict[str, float]], summary: dict[str, Any], summary_path: Path
) -> tuple[int, dict[str, float], dict[str, dict[str, float]]]:
    epochs = [int(row["epoch"]) for row in rows]
    expected_epochs = list(range(1, 41))
    if epochs != expected_epochs:
        raise ValueError(
            f"Expected exactly epochs 1-40 in order; found {epochs}"
        )

    best_epoch = int(
        as_finite_float(summary.get("best_epoch"), "best_epoch", summary_path)
    )
    epochs_completed = int(
        as_finite_float(
            summary.get("epochs_completed"), "epochs_completed", summary_path
        )
    )
    if best_epoch != 40 or epochs_completed != 40:
        raise ValueError(
            "Phase 52 figure contract requires epoch 40 to be both best and final"
        )
    if summary.get("level5_supported") is not False:
        raise ValueError(f"Expected level5_supported=false in {summary_path}")
    if summary.get("no_swe_pinn") is not True:
        raise ValueError(f"Expected no_swe_pinn=true in {summary_path}")

    final_metrics_raw = summary.get("final_epoch_metrics")
    best_metrics_raw = summary.get("best_epoch_metrics")
    comparisons_raw = summary.get("phase47_comparison")
    if not isinstance(final_metrics_raw, dict) or not isinstance(best_metrics_raw, dict):
        raise ValueError(f"Missing best/final metric objects in {summary_path}")
    if not isinstance(comparisons_raw, dict):
        raise ValueError(f"Missing phase47_comparison object in {summary_path}")

    final_metrics: dict[str, float] = {}
    comparisons: dict[str, dict[str, float]] = {}
    final_row = rows[-1]
    for metric, _, _ in COMPARISON_METRICS:
        final_value = as_finite_float(
            final_metrics_raw.get(metric), f"final_epoch_metrics.{metric}", summary_path
        )
        best_value = as_finite_float(
            best_metrics_raw.get(metric), f"best_epoch_metrics.{metric}", summary_path
        )
        assert_close(f"best/final {metric}", best_value, final_value)
        if metric in final_row:
            assert_close(metric, final_row[metric], final_value)
        comparison = comparisons_raw.get(metric)
        if not isinstance(comparison, dict):
            raise ValueError(f"Missing comparison for {metric} in {summary_path}")
        phase47_value = as_finite_float(
            comparison.get("phase47_reference"),
            f"phase47_comparison.{metric}.phase47_reference",
            summary_path,
        )
        phase52_value = as_finite_float(
            comparison.get("phase52_final_epoch_value"),
            f"phase47_comparison.{metric}.phase52_final_epoch_value",
            summary_path,
        )
        assert_close(f"comparison/final {metric}", phase52_value, final_value)
        final_metrics[metric] = final_value
        comparisons[metric] = {
            "phase47": phase47_value,
            "phase52": phase52_value,
        }
    return best_epoch, final_metrics, comparisons


def configure_style() -> None:
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 10,
            "axes.titleweight": "bold",
            "axes.titlesize": 13,
            "axes.labelcolor": COLORS["dark"],
            "text.color": COLORS["dark"],
            "figure.facecolor": COLORS["white"],
            "axes.facecolor": COLORS["white"],
            "savefig.facecolor": COLORS["white"],
        }
    )


def save_figure(fig: plt.Figure, output_path: Path, dpi: int) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=dpi, bbox_inches="tight")
    plt.close(fig)


def plot_trajectory(
    rows: list[dict[str, float]], best_epoch: int, output_path: Path, dpi: int
) -> None:
    epochs = [int(row["epoch"]) for row in rows]
    fig, axes = plt.subplots(3, 1, figsize=(10.5, 10.0), sharex=True)
    fig.suptitle("Phase 52 Test Metric Trajectory (40 Epochs)", fontsize=17, weight="bold")

    for ax, (metric, label, color) in zip(axes, TRAJECTORY_METRICS):
        values = [row[metric] for row in rows]
        final_value = values[-1]
        ax.plot(epochs, values, color=color, linewidth=2.2, label=label)
        ax.scatter(
            [best_epoch],
            [final_value],
            s=75,
            color=color,
            edgecolor=COLORS["white"],
            linewidth=1.2,
            zorder=4,
            label=f"Epoch {best_epoch} best/final",
        )
        ax.axvline(best_epoch, color=COLORS["gray"], linestyle="--", linewidth=1.0)
        ax.annotate(
            f"{final_value:.6f}",
            (best_epoch, final_value),
            xytext=(-8, 12),
            textcoords="offset points",
            ha="right",
            color=color,
            weight="bold",
        )
        ax.set_ylabel(label)
        ax.grid(axis="both", color=COLORS["grid"], alpha=0.65, linewidth=0.8)
        ax.legend(loc="best", frameon=False)

    axes[-1].set_xlabel("Epoch")
    axes[-1].set_xlim(1, 40.8)
    axes[-1].set_xticks([1, 5, 10, 15, 20, 25, 30, 35, 40])
    fig.tight_layout(rect=(0, 0, 1, 0.97))
    save_figure(fig, output_path, dpi)


def format_metric_value(metric: str, value: float) -> str:
    if metric in {"test_wet_dry_iou", "test_rollout_stability"}:
        return f"{value:.4f}"
    return f"{value:.6f}"


def plot_phase_comparison(
    comparisons: dict[str, dict[str, float]], output_path: Path, dpi: int
) -> None:
    fig, axes = plt.subplots(1, 5, figsize=(17.0, 5.2))
    fig.suptitle(
        "Phase 47 vs Phase 52: Controlled 128x128 Seed-42 Metrics",
        fontsize=17,
        weight="bold",
    )

    for ax, (metric, label, direction) in zip(axes, COMPARISON_METRICS):
        phase47 = comparisons[metric]["phase47"]
        phase52 = comparisons[metric]["phase52"]
        bars = ax.bar(
            ["Phase 47", "Phase 52"],
            [phase47, phase52],
            color=[COLORS["phase47"], COLORS["phase52"]],
            width=0.62,
        )
        ax.set_title(label)
        ax.set_ylim(0, max(phase47, phase52) * 1.24)
        ax.grid(axis="y", color=COLORS["grid"], alpha=0.65, linewidth=0.8)
        ax.set_axisbelow(True)
        ax.tick_params(axis="x", rotation=20)
        ax.text(
            0.5,
            0.98,
            f"{direction} is better",
            transform=ax.transAxes,
            ha="center",
            va="top",
            fontsize=9,
            color=COLORS["gray"],
        )
        for bar, value in zip(bars, [phase47, phase52]):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height(),
                format_metric_value(metric, value),
                ha="center",
                va="bottom",
                fontsize=9,
                weight="bold",
            )

    fig.tight_layout(rect=(0, 0, 1, 0.91))
    save_figure(fig, output_path, dpi)


def calculate_improvements(
    comparisons: dict[str, dict[str, float]]
) -> dict[str, float]:
    def reduction(metric: str) -> float:
        phase47 = comparisons[metric]["phase47"]
        phase52 = comparisons[metric]["phase52"]
        return (phase47 - phase52) / phase47 * 100.0

    return {
        "RMSE reduction": reduction("test_rmse"),
        "MAE reduction": reduction("test_mae"),
        "Wet/dry IoU gain": (
            comparisons["test_wet_dry_iou"]["phase52"]
            - comparisons["test_wet_dry_iou"]["phase47"]
        )
        * 100.0,
        "Step RMSE std reduction": reduction("test_step_rmse_std"),
    }


def plot_improvement_summary(
    improvements: dict[str, float], output_path: Path, dpi: int
) -> None:
    labels = list(improvements)
    values = [improvements[label] for label in labels]
    display_labels = [
        "RMSE reduction (%)",
        "MAE reduction (%)",
        "Wet/dry IoU gain (percentage points)",
        "Step RMSE std reduction (%)",
    ]

    fig, ax = plt.subplots(figsize=(10.5, 5.8))
    bars = ax.barh(
        display_labels,
        values,
        color=[
            COLORS["rmse"],
            COLORS["mae"],
            COLORS["iou"],
            COLORS["improvement"],
        ],
        height=0.62,
    )
    ax.invert_yaxis()
    ax.set_title("Phase 52 Improvement Relative to Phase 47", pad=14)
    ax.set_xlabel("Favorable change")
    ax.set_xlim(0, max(values) * 1.18)
    ax.grid(axis="x", color=COLORS["grid"], alpha=0.65, linewidth=0.8)
    ax.set_axisbelow(True)
    for bar, label, value in zip(bars, labels, values):
        suffix = " pp" if label == "Wet/dry IoU gain" else "%"
        ax.text(
            value + max(values) * 0.015,
            bar.get_y() + bar.get_height() / 2,
            f"{value:.2f}{suffix}",
            va="center",
            weight="bold",
            color=COLORS["dark"],
        )
    fig.tight_layout()
    save_figure(fig, output_path, dpi)


def write_summary(
    output_path: Path,
    metrics_path: Path,
    summary_path: Path,
    final_metrics: dict[str, float],
    comparisons: dict[str, dict[str, float]],
    improvements: dict[str, float],
) -> None:
    lines = [
        "# Phase 52 Figure Summary",
        "",
        "Generated figures:",
        "",
        "- `phase52_metric_trajectory_40e.png`: test RMSE, test MAE, and "
        "test wet/dry IoU trajectories; epoch 40 is marked as best and final.",
        "- `phase52_vs_phase47_key_metrics.png`: direct Phase 47 versus Phase 52 "
        "comparison for five key test metrics.",
        "- `phase52_improvement_summary.png`: favorable changes relative to Phase 47.",
        "",
        "Phase 52 epoch-40 test metrics:",
        "",
        "| Metric | Phase 47 | Phase 52 | Change |",
        "|---|---:|---:|---:|",
    ]
    for metric, label, _ in COMPARISON_METRICS:
        phase47 = comparisons[metric]["phase47"]
        phase52 = final_metrics[metric]
        delta = phase52 - phase47
        lines.append(
            f"| {label} | {phase47:.12g} | {phase52:.12g} | {delta:+.12g} |"
        )

    lines.extend(
        [
            "",
            "Improvement summary:",
            "",
            f"- RMSE reduction: `{improvements['RMSE reduction']:.2f}%`.",
            f"- MAE reduction: `{improvements['MAE reduction']:.2f}%`.",
            "- Wet/dry IoU gain: "
            f"`{improvements['Wet/dry IoU gain']:.2f}` percentage points.",
            "- Step RMSE std reduction: "
            f"`{improvements['Step RMSE std reduction']:.2f}%`.",
            "",
            "Source artifacts:",
            "",
            f"- `{metrics_path.relative_to(REPO_ROOT).as_posix()}`",
            f"- `{summary_path.relative_to(REPO_ROOT).as_posix()}`",
            "",
            "Scope and claim boundaries:",
            "",
            "- Visualization only; no training was rerun and no training result was modified.",
            "- These controlled metrics do not establish Level 5 capability, SWE/PINN "
            "modeling, strict conservation, hydrodynamic closure, calibrated "
            "probabilities, or production readiness.",
            "",
        ]
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    args = parse_args()
    metrics_path = resolve_repo_path(args.metrics_csv)
    summary_path = resolve_repo_path(args.summary_json)
    output_dir = resolve_repo_path(args.output_dir)

    rows = read_metrics(metrics_path)
    summary = read_json(summary_path)
    best_epoch, final_metrics, comparisons = validate_inputs(
        rows, summary, summary_path
    )
    improvements = calculate_improvements(comparisons)

    configure_style()
    plot_trajectory(
        rows,
        best_epoch,
        output_dir / "phase52_metric_trajectory_40e.png",
        args.dpi,
    )
    plot_phase_comparison(
        comparisons,
        output_dir / "phase52_vs_phase47_key_metrics.png",
        args.dpi,
    )
    plot_improvement_summary(
        improvements,
        output_dir / "phase52_improvement_summary.png",
        args.dpi,
    )
    write_summary(
        output_dir / "phase52_figure_summary.md",
        metrics_path,
        summary_path,
        final_metrics,
        comparisons,
        improvements,
    )
    print(f"Wrote Phase 52 figures and summary to {output_dir}")


if __name__ == "__main__":
    main()
