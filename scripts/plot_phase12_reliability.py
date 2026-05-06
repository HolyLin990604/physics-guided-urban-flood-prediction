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
import numpy as np


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT_DIR = REPO_ROOT / "analysis" / "phase12_reliability"

DEPTH_BIN_ORDER = ("dry_or_near_dry", "shallow", "moderate", "deep")
BOUNDARY_BAND_ORDER = (
    "boundary_0px",
    "near_boundary_1_3px",
    "far_field_gt3px",
    "no_target_boundary_frame",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Plot Phase 12 reliability figures from existing CSV/JSON outputs."
    )
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=DEFAULT_INPUT_DIR,
        help="Directory containing Phase 12 reliability CSV/JSON outputs.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Directory for generated figures. Defaults to <input-dir>/figures.",
    )
    parser.add_argument("--dpi", type=int, default=180, help="PNG output DPI.")
    parser.add_argument(
        "--top-n-failures",
        type=int,
        default=10,
        help="Number of failure cases to show in the RMSE ranking figure.",
    )
    parser.add_argument(
        "--max-seed-curves",
        type=int,
        default=5,
        help="Maximum seed-wise curves to include in timestep trend figure.",
    )
    return parser.parse_args()


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise FileNotFoundError(f"Missing required input file: {path}")
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def as_float(value: Any) -> float:
    if value is None or value == "":
        return math.nan
    try:
        return float(value)
    except (TypeError, ValueError):
        return math.nan


def as_int(value: Any) -> int:
    number = as_float(value)
    if math.isnan(number):
        return 0
    return int(number)


def finite_rows(rows: list[dict[str, str]], required_metric: str) -> list[dict[str, str]]:
    return [
        row
        for row in rows
        if as_int(row.get("count")) > 0 and math.isfinite(as_float(row.get(required_metric)))
    ]


def aggregate_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    selected = [
        row
        for row in rows
        if row.get("seed") == "all" or row.get("run_name") == "aggregate"
    ]
    return selected or rows


def sorted_by_order(
    rows: list[dict[str, str]], key: str, preferred_order: tuple[str, ...]
) -> list[dict[str, str]]:
    order = {name: index for index, name in enumerate(preferred_order)}
    return sorted(rows, key=lambda row: (order.get(row.get(key, ""), len(order)), row.get(key, "")))


def style_axis(ax: plt.Axes) -> None:
    ax.grid(axis="y", color="#d9dde3", linewidth=0.8, alpha=0.8)
    ax.set_axisbelow(True)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)


def save_figure(fig: plt.Figure, output_dir: Path, filename: str, dpi: int) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / filename
    fig.tight_layout()
    fig.savefig(path, dpi=dpi, bbox_inches="tight")
    plt.close(fig)
    return path


def plot_timestep_trend(
    rows: list[dict[str, str]], output_dir: Path, dpi: int, max_seed_curves: int
) -> Path:
    aggregate = sorted(
        finite_rows(aggregate_rows(rows), "rmse"),
        key=lambda row: as_float(row.get("forecast_step")),
    )
    if not aggregate:
        raise ValueError("No finite aggregate timestep metrics found.")

    fig, ax = plt.subplots(figsize=(8.5, 4.8))
    steps = [as_float(row["forecast_step"]) for row in aggregate]
    ax.plot(steps, [as_float(row["rmse"]) for row in aggregate], marker="o", linewidth=2.5, label="RMSE aggregate")
    ax.plot(steps, [as_float(row["mae"]) for row in aggregate], marker="s", linewidth=2.5, label="MAE aggregate")

    seed_names = sorted(
        {
            row.get("seed", "")
            for row in rows
            if row.get("seed") not in {"", "all"} and row.get("run_name") != "aggregate"
        }
    )
    if len(seed_names) <= max_seed_curves:
        for seed in seed_names:
            seed_rows = sorted(
                finite_rows([row for row in rows if row.get("seed") == seed], "rmse"),
                key=lambda row: as_float(row.get("forecast_step")),
            )
            if not seed_rows:
                continue
            seed_steps = [as_float(row["forecast_step"]) for row in seed_rows]
            ax.plot(
                seed_steps,
                [as_float(row["rmse"]) for row in seed_rows],
                color="#4c78a8",
                alpha=0.25,
                linewidth=1.0,
            )
            ax.plot(
                seed_steps,
                [as_float(row["mae"]) for row in seed_rows],
                color="#f58518",
                alpha=0.25,
                linewidth=1.0,
            )

    ax.set_title("Timestep Error Trend")
    ax.set_xlabel("Forecast step")
    ax.set_ylabel("Error")
    ax.legend(frameon=False)
    style_axis(ax)
    return save_figure(fig, output_dir, "timestep_rmse_mae_trend.png", dpi)


def plot_grouped_bars(
    rows: list[dict[str, str]],
    label_key: str,
    preferred_order: tuple[str, ...],
    metrics: tuple[str, str],
    title: str,
    ylabel: str,
    output_dir: Path,
    filename: str,
    dpi: int,
) -> Path:
    selected = sorted_by_order(finite_rows(aggregate_rows(rows), metrics[0]), label_key, preferred_order)
    selected = [row for row in selected if all(math.isfinite(as_float(row.get(metric))) for metric in metrics)]
    if not selected:
        raise ValueError(f"No finite aggregate rows found for {filename}.")

    labels = [row[label_key] for row in selected]
    x = np.arange(len(labels))
    width = 0.36

    fig, ax = plt.subplots(figsize=(8.5, 4.8))
    ax.bar(x - width / 2, [as_float(row[metrics[0]]) for row in selected], width, label=metrics[0].upper())
    ax.bar(x + width / 2, [as_float(row[metrics[1]]) for row in selected], width, label=metrics[1].upper())
    ax.set_title(title)
    ax.set_ylabel(ylabel)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=20, ha="right")
    ax.legend(frameon=False)
    style_axis(ax)
    return save_figure(fig, output_dir, filename, dpi)


def plot_single_metric_bars(
    rows: list[dict[str, str]],
    label_key: str,
    preferred_order: tuple[str, ...],
    metric: str,
    title: str,
    ylabel: str,
    output_dir: Path,
    filename: str,
    dpi: int,
) -> Path:
    selected = sorted_by_order(finite_rows(aggregate_rows(rows), metric), label_key, preferred_order)
    if not selected:
        raise ValueError(f"No finite aggregate rows found for {filename}.")

    labels = [row[label_key] for row in selected]
    values = [as_float(row[metric]) for row in selected]
    colors = ["#4c78a8" if value >= 0 else "#e45756" for value in values]

    fig, ax = plt.subplots(figsize=(8.5, 4.8))
    ax.bar(labels, values, color=colors)
    ax.axhline(0.0, color="#333333", linewidth=1.0)
    ax.set_title(title)
    ax.set_ylabel(ylabel)
    ax.tick_params(axis="x", rotation=20)
    for label in ax.get_xticklabels():
        label.set_ha("right")
    style_axis(ax)
    return save_figure(fig, output_dir, filename, dpi)


def failure_label(row: dict[str, str]) -> str:
    parts = [
        row.get("failure_rank", ""),
        row.get("seed", ""),
        row.get("location", ""),
        row.get("event", ""),
        f"start {row.get('start_idx', '')}",
    ]
    return " | ".join(part for part in parts if part)


def plot_top_failures(
    rows: list[dict[str, str]], output_dir: Path, dpi: int, top_n: int
) -> Path:
    selected = sorted(finite_rows(rows, "rmse"), key=lambda row: as_float(row["rmse"]), reverse=True)[:top_n]
    if not selected:
        raise ValueError("No finite failure case RMSE values found.")
    selected = list(reversed(selected))

    labels = [failure_label(row) for row in selected]
    values = [as_float(row["rmse"]) for row in selected]

    fig, ax = plt.subplots(figsize=(9.5, 5.8))
    ax.barh(labels, values, color="#4c78a8")
    ax.set_title(f"Top {len(selected)} Failure Cases by RMSE")
    ax.set_xlabel("RMSE")
    style_axis(ax)
    return save_figure(fig, output_dir, "top_failure_cases_rmse.png", dpi)


def plot_seed_level_overview(summary: dict[str, Any], output_dir: Path, dpi: int) -> Path | None:
    runs = summary.get("runs")
    if not isinstance(runs, list) or not runs:
        return None

    selected = [
        run
        for run in runs
        if all(math.isfinite(as_float(run.get(metric))) for metric in ("rmse", "mae", "wet_dry_class_error_rate"))
    ]
    if not selected:
        return None
    selected = sorted(selected, key=lambda run: str(run.get("seed", "")))

    labels = [str(run.get("seed", run.get("run_name", ""))) for run in selected]
    x = np.arange(len(labels))
    width = 0.26

    fig, ax = plt.subplots(figsize=(8.5, 4.8))
    ax.bar(x - width, [as_float(run["rmse"]) for run in selected], width, label="RMSE")
    ax.bar(x, [as_float(run["mae"]) for run in selected], width, label="MAE")
    ax.bar(
        x + width,
        [as_float(run["wet_dry_class_error_rate"]) for run in selected],
        width,
        label="Wet/dry class error rate",
    )
    ax.set_title("Seed-Level Overview")
    ax.set_ylabel("Metric value")
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend(frameon=False)
    style_axis(ax)
    return save_figure(fig, output_dir, "seed_level_overview.png", dpi)


def plot_scenario_scatter(rows: list[dict[str, str]], output_dir: Path, dpi: int) -> Path | None:
    selected = [
        row
        for row in finite_rows(rows, "rmse")
        if row.get("seed") not in {"", "all"}
        and math.isfinite(as_float(row.get("target_wet_fraction")))
    ]
    if not selected:
        return None

    seeds = sorted({row.get("seed", "") for row in selected})
    cmap = plt.get_cmap("tab10")
    color_by_seed = {seed: cmap(index % 10) for index, seed in enumerate(seeds)}

    fig, ax = plt.subplots(figsize=(7.2, 5.2))
    for seed in seeds:
        seed_rows = [row for row in selected if row.get("seed") == seed]
        ax.scatter(
            [as_float(row["target_wet_fraction"]) for row in seed_rows],
            [as_float(row["rmse"]) for row in seed_rows],
            s=28,
            alpha=0.75,
            label=seed,
            color=color_by_seed[seed],
        )
    ax.set_title("Scenario RMSE vs Target Wet Fraction")
    ax.set_xlabel("Target wet fraction")
    ax.set_ylabel("RMSE")
    ax.legend(frameon=False)
    style_axis(ax)
    return save_figure(fig, output_dir, "scenario_scatter_rmse_vs_target_wet_fraction.png", dpi)


def main() -> None:
    args = parse_args()
    input_dir = args.input_dir.resolve()
    output_dir = (args.output_dir or input_dir / "figures").resolve()

    timestep_rows = read_csv_rows(input_dir / "timestep_metrics.csv")
    depth_rows = read_csv_rows(input_dir / "depth_bin_metrics.csv")
    boundary_rows = read_csv_rows(input_dir / "boundary_distance_metrics.csv")
    failure_rows = read_csv_rows(input_dir / "failure_cases.csv")
    scenario_rows = read_csv_rows(input_dir / "scenario_metrics.csv")
    summary = read_json(input_dir / "summary.json")

    generated: list[Path] = []
    generated.append(plot_timestep_trend(timestep_rows, output_dir, args.dpi, args.max_seed_curves))
    generated.append(
        plot_grouped_bars(
            depth_rows,
            "depth_bin",
            DEPTH_BIN_ORDER,
            ("rmse", "mae"),
            "Depth-Bin Error Comparison",
            "Error",
            output_dir,
            "depth_bin_error_comparison.png",
            args.dpi,
        )
    )
    generated.append(
        plot_single_metric_bars(
            depth_rows,
            "depth_bin",
            DEPTH_BIN_ORDER,
            "bias",
            "Depth-Bin Bias Comparison",
            "Bias",
            output_dir,
            "depth_bin_bias_comparison.png",
            args.dpi,
        )
    )
    generated.append(
        plot_grouped_bars(
            boundary_rows,
            "boundary_distance_band",
            BOUNDARY_BAND_ORDER,
            ("rmse", "mae"),
            "Boundary-Distance Error Comparison",
            "Error",
            output_dir,
            "boundary_distance_error_comparison.png",
            args.dpi,
        )
    )
    generated.append(
        plot_single_metric_bars(
            boundary_rows,
            "boundary_distance_band",
            BOUNDARY_BAND_ORDER,
            "wet_dry_class_error_rate",
            "Boundary-Distance Wet/Dry Class Error",
            "Wet/dry class error rate",
            output_dir,
            "boundary_distance_class_error.png",
            args.dpi,
        )
    )
    generated.append(plot_top_failures(failure_rows, output_dir, args.dpi, args.top_n_failures))

    optional_seed = plot_seed_level_overview(summary, output_dir, args.dpi)
    if optional_seed is not None:
        generated.append(optional_seed)

    optional_scatter = plot_scenario_scatter(scenario_rows, output_dir, args.dpi)
    if optional_scatter is not None:
        generated.append(optional_scatter)

    print(f"Generated {len(generated)} figures under {output_dir}")
    for path in generated:
        print(f"- {path.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
