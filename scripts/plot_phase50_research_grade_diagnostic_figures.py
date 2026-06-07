from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = Path(
    "analysis/phase50_framework_consolidation/research_figures"
)

SOURCE_PATHS = {
    "scenario_reliability_metrics": Path(
        "analysis/phase48_full_dataset_reliability_physical_proxy/"
        "scenario_reliability_metrics.csv"
    ),
    "wet_dry_error_metrics": Path(
        "analysis/phase48_full_dataset_reliability_physical_proxy/"
        "wet_dry_error_metrics.csv"
    ),
    "volume_response_proxy_metrics": Path(
        "analysis/phase48_full_dataset_reliability_physical_proxy/"
        "volume_response_proxy_metrics.csv"
    ),
    "peak_depth_timing_metrics": Path(
        "analysis/phase48_full_dataset_reliability_physical_proxy/"
        "peak_depth_timing_metrics.csv"
    ),
    "location_type_summary": Path(
        "analysis/phase48_full_dataset_reliability_physical_proxy/"
        "location_type_summary.csv"
    ),
    "scenario_warning_framework": Path(
        "analysis/phase49_full_dataset_warning_framework/"
        "scenario_warning_framework.csv"
    ),
    "location_type_warning_summary": Path(
        "analysis/phase49_full_dataset_warning_framework/"
        "location_type_warning_summary.csv"
    ),
    "high_risk_case_review_list": Path(
        "analysis/phase49_full_dataset_warning_framework/"
        "high_risk_case_review_list.csv"
    ),
    "warning_rule_table": Path(
        "analysis/phase49_full_dataset_warning_framework/warning_rule_table.csv"
    ),
}

WARNING_LEVELS = ("reliable", "caution", "high-risk")
WARNING_COLORS = {
    "reliable": "#3C7D55",
    "caution": "#D18B18",
    "high-risk": "#B84A4A",
}
WARNING_MARKERS = {"reliable": "o", "caution": "s", "high-risk": "^"}

BOXPLOT_METRICS = (
    ("rmse", "RMSE"),
    ("mae", "MAE"),
    ("wet_dry_iou", "Wet/dry IoU"),
    ("false_dry_rate", "False-dry rate"),
    ("false_wet_rate", "False-wet rate"),
    (
        "absolute_relative_volume_bias_proxy",
        "Absolute relative\nvolume-bias proxy",
    ),
)

HEATMAP_METRICS = (
    ("rmse", "RMSE"),
    ("wet_dry_iou", "Wet/dry\nIoU risk"),
    ("false_dry_rate", "False-dry\nrate"),
    ("false_wet_rate", "False-wet\nrate"),
    (
        "absolute_relative_volume_bias_proxy",
        "Abs. relative\nvolume bias",
    ),
    (
        "peak_depth_underprediction_proxy",
        "Peak-depth\nunderprediction",
    ),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Generate no-training Phase 50 research-grade diagnostic figures "
            "from existing Phase 48 and Phase 49 CSV outputs."
        )
    )
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--dpi", type=int, default=180)
    parser.add_argument("--top-cases", type=int, default=15)
    return parser.parse_args()


def resolve_repo_path(path: Path) -> Path:
    return path if path.is_absolute() else REPO_ROOT / path


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        raise FileNotFoundError(f"Missing required input CSV: {path}")
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise ValueError(f"Required input CSV is empty: {path}")
    return rows


def finite_float(value: Any) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def available_numeric_rows(
    rows: list[dict[str, str]], field: str
) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for row in rows:
        value = finite_float(row.get(field))
        if value is not None:
            output.append({**row, field: value})
    return output


def configure_style() -> None:
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 9.5,
            "axes.titlesize": 11,
            "axes.titleweight": "bold",
            "axes.labelsize": 10,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "savefig.facecolor": "white",
        }
    )


def save_figure(
    fig: plt.Figure, output_dir: Path, filename: str, dpi: int
) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / filename
    fig.savefig(path, dpi=dpi, bbox_inches="tight")
    plt.close(fig)
    return path


def scenario_label(row: dict[str, Any]) -> str:
    return f"{row.get('location', '?')} | {row.get('scenario', '?')}"


def plot_metric_boxplots(
    rows: list[dict[str, str]], output_dir: Path, dpi: int
) -> tuple[Path | None, list[str]]:
    usable_metrics = []
    skipped = []
    for field, label in BOXPLOT_METRICS:
        grouped = [
            [
                value
                for row in rows
                if row.get("warning_level") == level
                and (value := finite_float(row.get(field))) is not None
            ]
            for level in WARNING_LEVELS
        ]
        if any(grouped):
            usable_metrics.append((field, label, grouped))
        else:
            skipped.append(field)

    if not usable_metrics:
        return None, skipped

    fig, axes = plt.subplots(2, 3, figsize=(13.2, 7.4))
    axes_flat = axes.ravel()
    for ax, (_, label, grouped) in zip(axes_flat, usable_metrics):
        box = ax.boxplot(
            grouped,
            labels=WARNING_LEVELS,
            patch_artist=True,
            widths=0.58,
            showfliers=True,
            medianprops={"color": "#20252A", "linewidth": 1.4},
            whiskerprops={"color": "#5B6570"},
            capprops={"color": "#5B6570"},
            flierprops={
                "marker": "o",
                "markersize": 3,
                "markerfacecolor": "#5B6570",
                "markeredgecolor": "none",
                "alpha": 0.55,
            },
        )
        for patch, level in zip(box["boxes"], WARNING_LEVELS):
            patch.set_facecolor(WARNING_COLORS[level])
            patch.set_alpha(0.72)
        ax.set_title(label)
        ax.grid(axis="y", alpha=0.25)
        ax.tick_params(axis="x", rotation=18)

    for ax in axes_flat[len(usable_metrics) :]:
        ax.set_visible(False)

    fig.suptitle(
        "Phase 50 reliability diagnostics by conservative warning level",
        fontsize=15,
        fontweight="bold",
        y=1.01,
    )
    fig.text(
        0.5,
        0.005,
        "Boxes show scenario-level distributions; warning labels are diagnostic screening categories.",
        ha="center",
        fontsize=9,
        color="#4B5563",
    )
    fig.tight_layout()
    path = save_figure(
        fig,
        output_dir,
        "phase50_reliability_metric_boxplots_by_warning_level.png",
        dpi,
    )
    return path, skipped


def plot_false_dry_volume_scatter(
    rows: list[dict[str, str]], output_dir: Path, dpi: int
) -> tuple[Path | None, list[str]]:
    x_field = "false_dry_rate"
    y_field = "absolute_relative_volume_bias_proxy"
    missing = [
        field
        for field in (x_field, y_field)
        if not available_numeric_rows(rows, field)
    ]
    if missing:
        return None, missing

    fig, ax = plt.subplots(figsize=(9.2, 6.6))
    plotted_rows: list[dict[str, Any]] = []
    for level in WARNING_LEVELS:
        level_rows = []
        for row in rows:
            x_value = finite_float(row.get(x_field))
            y_value = finite_float(row.get(y_field))
            if (
                row.get("warning_level") == level
                and x_value is not None
                and y_value is not None
            ):
                level_rows.append({**row, x_field: x_value, y_field: y_value})
        plotted_rows.extend(level_rows)
        ax.scatter(
            [row[x_field] for row in level_rows],
            [row[y_field] for row in level_rows],
            s=50,
            marker=WARNING_MARKERS[level],
            color=WARNING_COLORS[level],
            edgecolor="white",
            linewidth=0.6,
            alpha=0.82,
            label=f"{level} (n={len(level_rows)})",
        )

    worst = sorted(
        (
            row
            for row in plotted_rows
            if row.get("warning_level") == "high-risk"
        ),
        key=lambda row: row[x_field] + row[y_field],
        reverse=True,
    )[:4]
    for index, row in enumerate(worst):
        ax.annotate(
            scenario_label(row),
            (row[x_field], row[y_field]),
            xytext=(7, 7 + 10 * (index % 2)),
            textcoords="offset points",
            fontsize=7.5,
            arrowprops={"arrowstyle": "-", "color": "#6B7280", "lw": 0.7},
        )

    ax.set_xlabel("False-dry rate")
    ax.set_ylabel("Absolute relative volume-bias proxy")
    ax.set_title(
        "False-dry error versus volume-response bias\n"
        "Conservative diagnostic labels, not calibrated probabilities"
    )
    ax.grid(alpha=0.25)
    ax.legend(frameon=False, title="Warning level")
    fig.tight_layout()
    path = save_figure(
        fig, output_dir, "phase50_false_dry_vs_volume_bias_scatter.png", dpi
    )
    return path, []


def plot_location_type_counts(
    rows: list[dict[str, str]], output_dir: Path, dpi: int
) -> tuple[Path | None, list[str]]:
    count_fields = (
        ("reliable_count", "reliable"),
        ("caution_count", "caution"),
        ("high_risk_count", "high-risk"),
    )
    missing = [
        field
        for field, _ in count_fields
        if not available_numeric_rows(rows, field)
    ]
    if missing:
        return None, missing

    ordered_rows = sorted(
        rows, key=lambda row: (row.get("location", ""), row.get("scenario_type", ""))
    )
    labels = [
        f"{row.get('location', '?')}\n{row.get('scenario_type', '?')}"
        for row in ordered_rows
    ]
    x = np.arange(len(ordered_rows))
    bottom = np.zeros(len(ordered_rows))

    fig, ax = plt.subplots(figsize=(10.2, 5.8))
    for field, level in count_fields:
        values = np.array([float(row[field]) for row in ordered_rows])
        bars = ax.bar(
            x,
            values,
            bottom=bottom,
            width=0.68,
            color=WARNING_COLORS[level],
            label=level,
        )
        for bar, value, base in zip(bars, values, bottom):
            if value > 0:
                ax.text(
                    bar.get_x() + bar.get_width() / 2,
                    base + value / 2,
                    f"{int(value)}",
                    ha="center",
                    va="center",
                    color="white",
                    fontsize=9,
                    fontweight="bold",
                )
        bottom += values

    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel("Scenario count")
    ax.set_title("Warning concentration by location and scenario type")
    ax.grid(axis="y", alpha=0.25)
    ax.legend(frameon=False, ncol=3, loc="upper left")
    fig.tight_layout()
    path = save_figure(
        fig,
        output_dir,
        "phase50_location_type_warning_stacked_counts.png",
        dpi,
    )
    return path, []


def minmax_scale(values: np.ndarray) -> np.ndarray:
    finite = np.isfinite(values)
    output = np.full(values.shape, np.nan)
    if not finite.any():
        return output
    low = np.nanmin(values)
    high = np.nanmax(values)
    if math.isclose(float(low), float(high)):
        output[finite] = 0.0 if math.isclose(float(high), 0.0) else 1.0
    else:
        output[finite] = (values[finite] - low) / (high - low)
    return output


def plot_failure_driver_heatmap(
    scenario_rows: list[dict[str, str]],
    review_rows: list[dict[str, str]],
    output_dir: Path,
    dpi: int,
    top_cases: int,
) -> tuple[Path | None, list[str]]:
    available = []
    skipped = []
    for field, label in HEATMAP_METRICS:
        if available_numeric_rows(scenario_rows, field):
            available.append((field, label))
        else:
            skipped.append(field)
    if not available:
        return None, skipped

    scenario_index = {
        (row.get("split"), row.get("location"), row.get("scenario")): row
        for row in scenario_rows
    }
    ranked = sorted(
        review_rows,
        key=lambda row: finite_float(row.get("priority_rank")) or math.inf,
    )[:top_cases]
    merged_rows = []
    for review_row in ranked:
        key = (
            review_row.get("split"),
            review_row.get("location"),
            review_row.get("scenario"),
        )
        merged_rows.append({**scenario_index.get(key, {}), **review_row})
    if not merged_rows:
        return None, skipped

    columns = []
    for field, _ in available:
        raw = np.array(
            [
                finite_float(row.get(field))
                if finite_float(row.get(field)) is not None
                else np.nan
                for row in scenario_rows
            ],
            dtype=float,
        )
        display = np.array(
            [
                finite_float(row.get(field))
                if finite_float(row.get(field)) is not None
                else np.nan
                for row in merged_rows
            ],
            dtype=float,
        )
        if field == "wet_dry_iou":
            raw = 1.0 - raw
            display = 1.0 - display
        scaled_all = minmax_scale(raw)
        finite_raw = raw[np.isfinite(raw)]
        if finite_raw.size == 0:
            columns.append(np.full(display.shape, np.nan))
        elif math.isclose(float(np.min(finite_raw)), float(np.max(finite_raw))):
            columns.append(
                np.zeros(display.shape)
                if math.isclose(float(np.max(finite_raw)), 0.0)
                else np.ones(display.shape)
            )
        else:
            columns.append(
                np.clip(
                    (display - np.nanmin(raw))
                    / (np.nanmax(raw) - np.nanmin(raw)),
                    0.0,
                    1.0,
                )
            )
        del scaled_all

    matrix = np.column_stack(columns)
    row_labels = [
        f"#{row.get('priority_rank', '?')} {scenario_label(row)}" for row in merged_rows
    ]
    fig_height = max(6.2, 0.42 * len(merged_rows) + 1.8)
    fig, ax = plt.subplots(figsize=(10.8, fig_height))
    image = ax.imshow(matrix, cmap="YlOrRd", vmin=0.0, vmax=1.0, aspect="auto")
    ax.set_xticks(np.arange(len(available)))
    ax.set_xticklabels([label for _, label in available])
    ax.set_yticks(np.arange(len(merged_rows)))
    ax.set_yticklabels(row_labels, fontsize=8)
    ax.set_title(
        "Top high-risk cases: normalized diagnostic severity matrix\n"
        "Each metric is scaled across all Phase 49 scenarios"
    )
    ax.spines[:].set_visible(True)
    ax.set_xticks(np.arange(-0.5, len(available), 1), minor=True)
    ax.set_yticks(np.arange(-0.5, len(merged_rows), 1), minor=True)
    ax.grid(which="minor", color="white", linewidth=1.2)
    ax.tick_params(which="minor", bottom=False, left=False)
    colorbar = fig.colorbar(image, ax=ax, fraction=0.035, pad=0.025)
    colorbar.set_label("Normalized diagnostic severity")
    fig.tight_layout()
    path = save_figure(
        fig,
        output_dir,
        "phase50_high_risk_failure_driver_heatmap.png",
        dpi,
    )
    return path, skipped


def plot_priority_review_list(
    rows: list[dict[str, str]],
    output_dir: Path,
    dpi: int,
    top_cases: int,
) -> tuple[Path | None, list[str]]:
    score_field = "priority_score_uncalibrated"
    usable = available_numeric_rows(rows, score_field)
    if not usable:
        return None, [score_field]
    usable.sort(key=lambda row: row[score_field], reverse=True)
    selected = usable[:top_cases][::-1]

    labels = [
        f"#{row.get('priority_rank', '?')} {scenario_label(row)}"
        for row in selected
    ]
    values = [row[score_field] for row in selected]
    colors = [
        "#B84A4A" if row.get("scenario_type") == "design" else "#8F4D74"
        for row in selected
    ]

    fig_height = max(6.0, 0.42 * len(selected) + 1.8)
    fig, ax = plt.subplots(figsize=(10.8, fig_height))
    bars = ax.barh(np.arange(len(selected)), values, color=colors, alpha=0.88)
    ax.set_yticks(np.arange(len(selected)))
    ax.set_yticklabels(labels, fontsize=8)
    ax.set_xlabel("Uncalibrated diagnostic priority score")
    ax.set_title("Phase 51 review priority: top Phase 49 high-risk cases")
    ax.grid(axis="x", alpha=0.25)
    for bar, value in zip(bars, values):
        ax.text(
            value + max(values) * 0.012,
            bar.get_y() + bar.get_height() / 2,
            f"{value:.2f}",
            va="center",
            fontsize=8,
        )
    ax.set_xlim(0, max(values) * 1.13)
    fig.tight_layout()
    path = save_figure(
        fig, output_dir, "phase50_top_high_risk_case_priority.png", dpi
    )
    return path, []


def write_summary(
    output_dir: Path,
    source_rows: dict[str, int],
    written: list[Path],
    skipped: dict[str, list[str]],
    top_cases: int,
) -> Path:
    lines = [
        "# Phase 50 Research Figure Summary",
        "",
        "These figures use existing Phase 48 reliability/physical-proxy diagnostics "
        "and Phase 49 conservative warning-framework outputs. No training, seed runs, "
        "sweeps, or model/configuration changes were performed.",
        "",
        "Warning levels are conservative diagnostic screening labels. They are not "
        "calibrated probabilities, event likelihoods, or production-readiness guarantees.",
        "",
        "## Figures",
        "",
    ]
    descriptions = {
        "phase50_reliability_metric_boxplots_by_warning_level.png": (
            "Scenario-level distributions of six reliability and physical-proxy "
            "metrics by warning level."
        ),
        "phase50_false_dry_vs_volume_bias_scatter.png": (
            "Joint false-dry and absolute relative volume-bias proxy diagnostics, "
            "colored and marked by warning level."
        ),
        "phase50_location_type_warning_stacked_counts.png": (
            "Reliable, caution, and high-risk counts by location and scenario type."
        ),
        "phase50_high_risk_failure_driver_heatmap.png": (
            f"Normalized diagnostic severity matrix for the top {top_cases} ranked "
            "high-risk cases."
        ),
        "phase50_top_high_risk_case_priority.png": (
            f"Top {top_cases} high-risk cases by the Phase 49 uncalibrated "
            "diagnostic priority score."
        ),
    }
    for path in written:
        if path.suffix == ".png":
            lines.append(f"- `{path.name}`: {descriptions[path.name]}")

    lines.extend(["", "## Source Rows Loaded", ""])
    for name, count in source_rows.items():
        lines.append(f"- `{SOURCE_PATHS[name].as_posix()}`: {count} rows")

    lines.extend(["", "## Missing or Skipped Metrics", ""])
    if skipped:
        for figure, fields in skipped.items():
            lines.append(f"- `{figure}`: skipped {', '.join(f'`{f}`' for f in fields)}")
    else:
        lines.append("- None. All requested metric fields were available.")

    lines.extend(
        [
            "",
            "## Interpretation Boundaries",
            "",
            "- Visualization support only; this is not a new experiment.",
            "- No SWE residual, PINN, or Level 5 support claim.",
            "- No strict conservation, full mass conservation, or hydrodynamic closure claim.",
            "- No calibrated probability or final production-readiness claim.",
            "- Heatmap values are display-only min-max severity scaling across the "
            "48 scenario rows; original CSV values are unchanged.",
            "",
        ]
    )
    path = output_dir / "phase50_research_figure_summary.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def main() -> None:
    args = parse_args()
    configure_style()
    output_dir = resolve_repo_path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    sources = {
        name: read_csv(resolve_repo_path(path))
        for name, path in SOURCE_PATHS.items()
    }
    source_rows = {name: len(rows) for name, rows in sources.items()}
    scenario_rows = sources["scenario_warning_framework"]
    location_rows = sources["location_type_warning_summary"]
    review_rows = sources["high_risk_case_review_list"]

    results = [
        plot_metric_boxplots(scenario_rows, output_dir, args.dpi),
        plot_false_dry_volume_scatter(scenario_rows, output_dir, args.dpi),
        plot_location_type_counts(location_rows, output_dir, args.dpi),
        plot_failure_driver_heatmap(
            scenario_rows, review_rows, output_dir, args.dpi, args.top_cases
        ),
        plot_priority_review_list(
            review_rows, output_dir, args.dpi, args.top_cases
        ),
    ]

    written = [path for path, _ in results if path is not None]
    figure_names = (
        "phase50_reliability_metric_boxplots_by_warning_level.png",
        "phase50_false_dry_vs_volume_bias_scatter.png",
        "phase50_location_type_warning_stacked_counts.png",
        "phase50_high_risk_failure_driver_heatmap.png",
        "phase50_top_high_risk_case_priority.png",
    )
    skipped = {
        figure_name: fields
        for figure_name, (_, fields) in zip(figure_names, results)
        if fields
    }
    summary_path = write_summary(
        output_dir, source_rows, written, skipped, args.top_cases
    )
    written.append(summary_path)

    print(f"figures_written={sum(path.suffix == '.png' for path in written)}")
    print(f"output_dir={output_dir}")
    print(f"source_rows_loaded={sum(source_rows.values())}")
    print("no_training=true")
    print("warning_labels_are_probabilities=false")


if __name__ == "__main__":
    main()
