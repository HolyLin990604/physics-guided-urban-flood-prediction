from __future__ import annotations

import argparse
import csv
import json
import math
import textwrap
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT_DIR = Path("analysis/phase50_framework_consolidation")
DEFAULT_OUTPUT_DIR = DEFAULT_INPUT_DIR / "figures"

PHASE49_SUMMARY = Path(
    "analysis/phase49_full_dataset_warning_framework/warning_framework_summary.json"
)
PHASE48_SUMMARY = Path(
    "analysis/phase48_full_dataset_reliability_physical_proxy/"
    "phase48_reliability_summary.json"
)
PHASE47_SUMMARY = Path(
    "analysis/phase47_controlled_downsample_baseline/phase47_training_summary.json"
)

COLORS = {
    "navy": "#17324D",
    "blue": "#2F6B9A",
    "light_blue": "#DCEAF4",
    "teal": "#2A7F78",
    "light_teal": "#DCEFEB",
    "amber": "#C98200",
    "light_amber": "#FFF0CC",
    "red": "#B84A4A",
    "light_red": "#F8DEDE",
    "green": "#3C7D55",
    "light_green": "#DDEEE3",
    "gray": "#65727E",
    "light_gray": "#EDF0F2",
    "dark": "#1F2933",
    "white": "#FFFFFF",
}

METRIC_SPECS = (
    ("47", "best_test_rmse", "Best test RMSE", "error"),
    ("47", "test_mae", "Test MAE", "error"),
    ("47", "test_wet_dry_iou", "Test wet/dry IoU", "fraction"),
    ("48", "mean_rmse", "Mean RMSE", "error"),
    ("48", "mean_mae", "Mean MAE", "error"),
    ("48", "mean_wet_dry_iou", "Mean wet/dry IoU", "fraction"),
    ("48", "mean_false_dry_rate", "Mean false-dry rate", "fraction"),
    ("48", "mean_false_wet_rate", "Mean false-wet rate", "fraction"),
    (
        "48",
        "mean_absolute_relative_volume_bias_proxy",
        "Mean absolute relative\nvolume-bias proxy",
        "fraction",
    ),
)

SUPPORTED_CLAIMS = (
    "Level 4+ full-dataset\nproxy modeling route",
    "Controlled 128x128\nbaseline",
    "Reliability diagnostics",
    "Physical proxy diagnostics",
    "Conservative warning\nframework",
    "Paper-ready evidence\nsynthesis",
)

NOT_SUPPORTED_CLAIMS = (
    "Level 5",
    "SWE / PINN",
    "Strict conservation",
    "Full mass conservation",
    "Hydrodynamic closure",
    "Calibrated probability labels",
    "Final production readiness",
    "Uncontrolled training expansion",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Generate no-training Phase 50 README-facing framework summary figures "
            "from existing Phase 47-50 artifacts."
        )
    )
    parser.add_argument("--input-dir", type=Path, default=DEFAULT_INPUT_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--dpi", type=int, default=200)
    return parser.parse_args()


def resolve_repo_path(path: Path) -> Path:
    return path if path.is_absolute() else REPO_ROOT / path


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        raise FileNotFoundError(f"Missing required input artifact: {path}")
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise ValueError(f"Required CSV is empty: {path}")
    return rows


def read_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise FileNotFoundError(f"Missing required input artifact: {path}")
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"Expected a JSON object in {path}")
    return value


def require_key(mapping: dict[str, Any], key: str, source: Path) -> Any:
    if key not in mapping:
        raise ValueError(f"Missing required field {key!r} in {source}")
    return mapping[key]


def require_bool(mapping: dict[str, Any], key: str, expected: bool, source: Path) -> None:
    value = require_key(mapping, key, source)
    if value is not expected:
        raise ValueError(f"Expected {key}={expected!r} in {source}, found {value!r}")


def as_finite_float(value: Any, field: str, source: Path) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Field {field!r} in {source} is not numeric: {value!r}") from exc
    if not math.isfinite(number):
        raise ValueError(f"Field {field!r} in {source} is not finite: {value!r}")
    return number


def as_int(value: Any, field: str, source: Path) -> int:
    number = as_finite_float(value, field, source)
    if not number.is_integer():
        raise ValueError(f"Field {field!r} in {source} is not an integer: {value!r}")
    return int(number)


def assert_close(name: str, left: float, right: float) -> None:
    if not math.isclose(left, right, rel_tol=1e-12, abs_tol=1e-15):
        raise ValueError(f"Inconsistent {name}: {left!r} != {right!r}")


def configure_style() -> None:
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 10,
            "axes.titleweight": "bold",
            "axes.titlesize": 16,
            "figure.facecolor": COLORS["white"],
            "axes.facecolor": COLORS["white"],
            "savefig.facecolor": COLORS["white"],
        }
    )


def save_figure(fig: plt.Figure, output_dir: Path, filename: str, dpi: int) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / filename
    fig.savefig(path, dpi=dpi, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    return path


def validate_and_load(
    input_dir: Path,
) -> tuple[
    list[dict[str, str]],
    dict[str, float],
    list[dict[str, str]],
    list[dict[str, str]],
    dict[str, Any],
    dict[str, int],
]:
    evidence_path = input_dir / "phase50_evidence_chain_table.csv"
    metrics_path = input_dir / "phase50_key_metrics_summary.csv"
    claims_path = input_dir / "phase50_claim_boundary_table.csv"
    next_steps_path = input_dir / "phase50_recommended_next_steps.csv"
    synthesis_path = input_dir / "phase50_framework_synthesis.json"
    phase49_path = resolve_repo_path(PHASE49_SUMMARY)
    phase48_path = resolve_repo_path(PHASE48_SUMMARY)
    phase47_path = resolve_repo_path(PHASE47_SUMMARY)

    evidence_rows = read_csv(evidence_path)
    metric_rows = read_csv(metrics_path)
    claim_rows = read_csv(claims_path)
    next_step_rows = read_csv(next_steps_path)
    synthesis = read_json(synthesis_path)
    phase49 = read_json(phase49_path)
    phase48 = read_json(phase48_path)
    phase47 = read_json(phase47_path)

    require_bool(synthesis, "no_training", True, synthesis_path)
    require_bool(synthesis, "level5_supported", False, synthesis_path)
    require_bool(synthesis, "warning_labels_are_probabilities", False, synthesis_path)
    require_bool(synthesis, "strict_conservation_supported", False, synthesis_path)
    require_bool(synthesis, "full_mass_conservation_supported", False, synthesis_path)
    require_bool(synthesis, "hydrodynamic_closure_supported", False, synthesis_path)
    require_bool(phase49, "no_training", True, phase49_path)
    require_bool(phase49, "level5_supported", False, phase49_path)
    require_bool(phase49, "warning_labels_are_probabilities", False, phase49_path)
    require_bool(phase48, "no_training", True, phase48_path)
    require_bool(phase48, "level5_supported", False, phase48_path)
    require_bool(phase47, "level5_supported", False, phase47_path)
    require_bool(phase47, "no_swe_pinn", True, phase47_path)

    phases = {as_int(row.get("phase"), "phase", evidence_path) for row in evidence_rows}
    expected_phases = set(range(43, 50))
    if phases != expected_phases:
        raise ValueError(
            f"Evidence chain must contain Phases 43-49; found {sorted(phases)}"
        )

    metric_raw_values: dict[str, str] = {}
    for row in metric_rows:
        metric = row.get("metric", "")
        if metric:
            metric_raw_values[metric] = row.get("value", "")

    metric_values: dict[str, float] = {}
    for _, metric, _, _ in METRIC_SPECS:
        if metric not in metric_raw_values:
            raise ValueError(f"Missing required metric {metric!r} in {metrics_path}")
        metric_values[metric] = as_finite_float(
            metric_raw_values[metric], metric, metrics_path
        )

    phase47_rmse = as_finite_float(
        require_key(phase47, "best_test_rmse", phase47_path),
        "best_test_rmse",
        phase47_path,
    )
    assert_close("best_test_rmse", metric_values["best_test_rmse"], phase47_rmse)
    for key in (
        "mean_rmse",
        "mean_mae",
        "mean_wet_dry_iou",
        "mean_false_dry_rate",
        "mean_false_wet_rate",
        "mean_absolute_relative_volume_bias_proxy",
    ):
        assert_close(
            key,
            metric_values[key],
            as_finite_float(require_key(phase48, key, phase48_path), key, phase48_path),
        )

    warning_counts: dict[str, int] = {}
    phase49_counts = require_key(phase49, "warning_level_counts", phase49_path)
    phase48_counts = require_key(phase48, "warning_level_counts", phase48_path)
    if not isinstance(phase49_counts, dict) or not isinstance(phase48_counts, dict):
        raise ValueError("warning_level_counts must be JSON objects in Phases 48 and 49")
    for label in ("reliable", "caution", "high-risk"):
        phase49_count = as_int(phase49_counts.get(label), label, phase49_path)
        phase48_count = as_int(phase48_counts.get(label), label, phase48_path)
        if phase49_count != phase48_count:
            raise ValueError(
                f"Inconsistent warning count for {label}: "
                f"Phase 48={phase48_count}, Phase 49={phase49_count}"
            )
        csv_key = f"warning_level_{label}"
        if csv_key not in metric_raw_values:
            raise ValueError(f"Missing {csv_key!r} in {metrics_path}")
        csv_count = as_int(metric_raw_values[csv_key], csv_key, metrics_path)
        if phase49_count != csv_count:
            raise ValueError(
                f"Inconsistent warning count for {label} between CSV and JSON"
            )
        warning_counts[label] = phase49_count

    claim_statuses = {(row.get("claim_status", ""), row.get("claim", "")) for row in claim_rows}
    required_claim_fragments = (
        ("supported", "Level 4+"),
        ("supported", "128x128"),
        ("supported", "Reliability"),
        ("supported", "warning framework"),
        ("not_supported", "Level 5"),
        ("not_supported", "SWE"),
        ("not_supported", "Strict conservation"),
        ("not_supported", "Full mass conservation"),
        ("not_supported", "Hydrodynamic closure"),
        ("not_supported", "Calibrated probability"),
        ("not_supported", "Final production readiness"),
    )
    for status, fragment in required_claim_fragments:
        if not any(
            row_status == status and fragment.lower() in claim.lower()
            for row_status, claim in claim_statuses
        ):
            raise ValueError(
                f"Missing {status!r} claim containing {fragment!r} in {claims_path}"
            )

    return (
        sorted(evidence_rows, key=lambda row: int(row["phase"])),
        metric_values,
        claim_rows,
        next_step_rows,
        synthesis,
        warning_counts,
    )


def plot_evidence_chain(
    evidence_rows: list[dict[str, str]],
    output_dir: Path,
    dpi: int,
) -> Path:
    stage_labels = {
        43: "Dataset\ninspection",
        44: "Level 4+\nreplanning",
        45: "Full-dataset\nindexing",
        46: "Dataloader\nfeasibility",
        47: "Controlled 128x128\nbaseline",
        48: "Reliability +\nproxy diagnostics",
        49: "Conservative\nwarning framework",
        50: "Evidence\nsynthesis",
    }
    stage_types = {
        43: ("Inspection", COLORS["light_blue"], COLORS["blue"]),
        44: ("Planning", COLORS["light_gray"], COLORS["gray"]),
        45: ("Preparation", COLORS["light_blue"], COLORS["blue"]),
        46: ("No-training check", COLORS["light_teal"], COLORS["teal"]),
        47: ("Controlled training", COLORS["light_amber"], COLORS["amber"]),
        48: ("No-training diagnostics", COLORS["light_teal"], COLORS["teal"]),
        49: ("No-training framework", COLORS["light_teal"], COLORS["teal"]),
        50: ("No-training synthesis", COLORS["light_gray"], COLORS["navy"]),
    }
    phases = [int(row["phase"]) for row in evidence_rows] + [50]
    if phases != list(range(43, 51)):
        raise ValueError(f"Unexpected evidence-chain order: {phases}")

    fig, ax = plt.subplots(figsize=(14, 6.2))
    ax.set_xlim(0, 4)
    ax.set_ylim(0, 2)
    ax.axis("off")
    top_x = (0.55, 1.52, 2.49, 3.46)
    bottom_x = tuple(reversed(top_x))
    positions = {
        phase: (
            top_x[index] if index < 4 else bottom_x[index - 4],
            1.37 if index < 4 else 0.57,
        )
        for index, phase in enumerate(phases)
    }
    ordered_positions = [positions[phase] for phase in phases]

    for index in range(len(ordered_positions) - 1):
        start = ordered_positions[index]
        end = ordered_positions[index + 1]
        if index == 3:
            arrow = FancyArrowPatch(
                (start[0], start[1] - 0.23),
                (end[0], end[1] + 0.23),
                arrowstyle="-|>",
                mutation_scale=13,
                linewidth=1.8,
                color=COLORS["gray"],
            )
        else:
            direction = 1 if end[0] > start[0] else -1
            arrow = FancyArrowPatch(
                (start[0] + direction * 0.39, start[1]),
                (end[0] - direction * 0.39, end[1]),
                arrowstyle="-|>",
                mutation_scale=13,
                linewidth=1.8,
                color=COLORS["gray"],
            )
        ax.add_patch(arrow)

    for phase in phases:
        x, y = positions[phase]
        stage_type, facecolor, edgecolor = stage_types[phase]
        box = FancyBboxPatch(
            (x - 0.38, y - 0.22),
            0.76,
            0.44,
            boxstyle="round,pad=0.025,rounding_size=0.04",
            linewidth=1.8,
            edgecolor=edgecolor,
            facecolor=facecolor,
        )
        ax.add_patch(box)
        ax.text(
            x,
            y + 0.08,
            f"Phase {phase}",
            ha="center",
            va="center",
            fontsize=9.5,
            fontweight="bold",
            color=edgecolor,
        )
        ax.text(
            x,
            y - 0.055,
            stage_labels[phase],
            ha="center",
            va="center",
            fontsize=9.5,
            color=COLORS["dark"],
            linespacing=1.2,
        )
        ax.text(
            x,
            y - 0.31,
            stage_type,
            ha="center",
            va="center",
            fontsize=8.2,
            color=edgecolor,
            fontweight="bold",
        )

    ax.text(
        2,
        1.91,
        "UrbanFlood24 Full-Dataset Level 4+ Evidence Chain",
        ha="center",
        va="center",
        fontsize=17,
        fontweight="bold",
        color=COLORS["navy"],
    )
    ax.text(
        2,
        0.08,
        "Only Phase 47 adds controlled training evidence; Phases 46 and 48-50 are no-training checks, diagnostics, and synthesis.",
        ha="center",
        va="center",
        fontsize=9.5,
        color=COLORS["gray"],
    )
    return save_figure(fig, output_dir, "phase50_evidence_chain_overview.png", dpi)


def metric_value_text(value: float, kind: str) -> str:
    if kind == "fraction":
        return f"{value:.4f}\n({value * 100:.2f}%)"
    return f"{value:.6f}"


def draw_metric_card(
    ax: plt.Axes,
    title: str,
    value: float,
    kind: str,
    facecolor: str,
    edgecolor: str,
) -> None:
    ax.axis("off")
    card = FancyBboxPatch(
        (0.03, 0.08),
        0.94,
        0.84,
        boxstyle="round,pad=0.025,rounding_size=0.05",
        transform=ax.transAxes,
        linewidth=1.5,
        edgecolor=edgecolor,
        facecolor=facecolor,
    )
    ax.add_patch(card)
    ax.text(
        0.5,
        0.68,
        title,
        transform=ax.transAxes,
        ha="center",
        va="center",
        fontsize=9.5,
        color=COLORS["dark"],
        linespacing=1.15,
    )
    ax.text(
        0.5,
        0.36,
        metric_value_text(value, kind),
        transform=ax.transAxes,
        ha="center",
        va="center",
        fontsize=14,
        fontweight="bold",
        color=edgecolor,
        linespacing=1.2,
    )


def plot_key_metrics(
    metric_values: dict[str, float],
    output_dir: Path,
    dpi: int,
) -> Path:
    fig = plt.figure(figsize=(13, 7.3))
    grid = fig.add_gridspec(
        3,
        6,
        height_ratios=(0.38, 1, 1),
        hspace=0.35,
        wspace=0.28,
    )
    title_ax = fig.add_subplot(grid[0, :])
    title_ax.axis("off")
    title_ax.text(
        0.5,
        0.8,
        "Phase 47 Baseline and Phase 48 Diagnostic Metrics",
        ha="center",
        va="center",
        fontsize=17,
        fontweight="bold",
        color=COLORS["navy"],
    )
    title_ax.text(
        0.5,
        0.15,
        "Metric cards preserve distinct meanings and scales; the volume-bias value is a physical proxy diagnostic.",
        ha="center",
        va="center",
        fontsize=9.5,
        color=COLORS["gray"],
    )

    phase47_specs = METRIC_SPECS[:3]
    phase48_specs = METRIC_SPECS[3:]
    for index, (_, metric, label, kind) in enumerate(phase47_specs):
        ax = fig.add_subplot(grid[1, index * 2 : index * 2 + 2])
        draw_metric_card(
            ax,
            label,
            metric_values[metric],
            kind,
            COLORS["light_amber"],
            COLORS["amber"],
        )
    for index, (_, metric, label, kind) in enumerate(phase48_specs):
        ax = fig.add_subplot(grid[2, index])
        draw_metric_card(
            ax,
            label,
            metric_values[metric],
            kind,
            COLORS["light_teal"],
            COLORS["teal"],
        )

    fig.text(
        0.02,
        0.61,
        "Phase 47\ncontrolled baseline",
        ha="left",
        va="center",
        fontsize=10,
        fontweight="bold",
        color=COLORS["amber"],
    )
    fig.text(
        0.02,
        0.245,
        "Phase 48\nno-training diagnostics",
        ha="left",
        va="center",
        fontsize=10,
        fontweight="bold",
        color=COLORS["teal"],
    )
    return save_figure(fig, output_dir, "phase50_key_metrics_summary.png", dpi)


def plot_warning_counts(
    warning_counts: dict[str, int],
    output_dir: Path,
    dpi: int,
) -> Path:
    labels = ("reliable", "caution", "high-risk")
    display_labels = ("Reliable", "Caution", "High-risk")
    values = [warning_counts[label] for label in labels]
    colors = (COLORS["green"], COLORS["amber"], COLORS["red"])
    total = sum(values)
    if total != 48:
        raise ValueError(f"Expected 48 warning scenarios, found {total}")

    fig, ax = plt.subplots(figsize=(9.5, 5.8))
    bars = ax.barh(display_labels, values, color=colors, height=0.58)
    ax.invert_yaxis()
    ax.set_xlim(0, max(values) * 1.18)
    ax.set_xlabel("Scenario count")
    ax.set_title("Phase 48/49 Conservative Warning-Level Counts", pad=18)
    ax.grid(axis="x", color="#D9DDE3", linewidth=0.8)
    ax.set_axisbelow(True)
    for spine in ("top", "right", "left"):
        ax.spines[spine].set_visible(False)
    for bar, value in zip(bars, values):
        ax.text(
            value + 0.6,
            bar.get_y() + bar.get_height() / 2,
            f"{value}  ({value / total:.1%} of reviewed scenarios)",
            va="center",
            fontsize=11,
            fontweight="bold",
            color=COLORS["dark"],
        )
    ax.text(
        0.0,
        -0.24,
        f"Total: {total} test scenarios",
        transform=ax.transAxes,
        fontsize=10.5,
        fontweight="bold",
        color=COLORS["navy"],
    )
    ax.text(
        0.0,
        -0.34,
        "Counts summarize conservative diagnostic screening labels. They are not calibrated probabilities or forecast likelihoods.",
        transform=ax.transAxes,
        fontsize=9.5,
        color=COLORS["red"],
        fontweight="bold",
    )
    fig.subplots_adjust(left=0.18, right=0.94, top=0.84, bottom=0.25)
    return save_figure(fig, output_dir, "phase50_warning_level_counts.png", dpi)


def plot_claim_boundary(
    output_dir: Path,
    dpi: int,
) -> Path:
    max_rows = max(len(SUPPORTED_CLAIMS), len(NOT_SUPPORTED_CLAIMS))
    fig, axes = plt.subplots(1, 2, figsize=(13, 8.2), sharey=True)
    fig.suptitle(
        "Phase 50 Claim Boundary",
        fontsize=18,
        fontweight="bold",
        color=COLORS["navy"],
        y=0.965,
    )

    columns = (
        (
            axes[0],
            "SUPPORTED",
            SUPPORTED_CLAIMS,
            COLORS["light_green"],
            COLORS["green"],
            "Evidence-backed within the Level 4+ proxy route",
        ),
        (
            axes[1],
            "NOT SUPPORTED",
            NOT_SUPPORTED_CLAIMS,
            COLORS["light_red"],
            COLORS["red"],
            "Must not be inferred from Phase 43-50 evidence",
        ),
    )
    for ax, heading, claims, facecolor, edgecolor, subtitle in columns:
        ax.set_xlim(0, 1)
        ax.set_ylim(max_rows + 0.55, -1.15)
        ax.axis("off")
        ax.text(
            0.5,
            -0.72,
            heading,
            ha="center",
            va="center",
            fontsize=15,
            fontweight="bold",
            color=edgecolor,
        )
        ax.text(
            0.5,
            -0.28,
            subtitle,
            ha="center",
            va="center",
            fontsize=9,
            color=COLORS["gray"],
        )
        for index, claim in enumerate(claims):
            box = FancyBboxPatch(
                (0.06, index + 0.08),
                0.88,
                0.7,
                boxstyle="round,pad=0.02,rounding_size=0.035",
                linewidth=1.4,
                edgecolor=edgecolor,
                facecolor=facecolor,
            )
            ax.add_patch(box)
            symbol = "SUPPORTED" if heading == "SUPPORTED" else "NOT SUPPORTED"
            ax.text(
                0.11,
                index + 0.43,
                symbol,
                ha="left",
                va="center",
                fontsize=7.5,
                fontweight="bold",
                color=edgecolor,
            )
            ax.text(
                0.34,
                index + 0.43,
                claim,
                ha="left",
                va="center",
                fontsize=10,
                color=COLORS["dark"],
                linespacing=1.15,
            )

    fig.text(
        0.5,
        0.035,
        "Physical proxy diagnostics do not establish conservation-law enforcement or hydrodynamic closure.",
        ha="center",
        va="center",
        fontsize=9.5,
        color=COLORS["red"],
        fontweight="bold",
    )
    fig.subplots_adjust(left=0.04, right=0.98, top=0.88, bottom=0.09, wspace=0.08)
    return save_figure(fig, output_dir, "phase50_claim_boundary_matrix.png", dpi)


def find_next_step(
    rows: list[dict[str, str]], fragment: str, source: Path
) -> dict[str, str]:
    matches = [
        row for row in rows if fragment.lower() in row.get("next_step", "").lower()
    ]
    if len(matches) != 1:
        raise ValueError(
            f"Expected one next-step row containing {fragment!r} in {source}, "
            f"found {len(matches)}"
        )
    return matches[0]


def plot_next_steps(
    next_step_rows: list[dict[str, str]],
    input_dir: Path,
    output_dir: Path,
    dpi: int,
) -> Path:
    source = input_dir / "phase50_recommended_next_steps.csv"
    requested = (
        ("128x128 seed42 longer-run review", "longer run review"),
        ("128x128 seed replication after review", "seed replication"),
        ("256x256 pilot after explicit authorization", "256x256 pilot"),
        ("Warning-framework case reporting", "case reporting"),
        ("Manuscript development", "manuscript outline"),
    )
    status_display = {
        "allowed": ("Allowed reporting work", COLORS["light_green"], COLORS["green"]),
        "allowed_after_review": (
            "Requires review",
            COLORS["light_amber"],
            COLORS["amber"],
        ),
        "not_allowed_without_explicit_authorization": (
            "Explicit authorization required",
            COLORS["light_red"],
            COLORS["red"],
        ),
    }
    selected: list[tuple[str, str, str, str]] = []
    for display_name, fragment in requested:
        row = find_next_step(next_step_rows, fragment, source)
        status = row.get("allowed", "")
        if status not in status_display:
            raise ValueError(f"Unknown next-step status {status!r} in {source}")
        status_label, facecolor, edgecolor = status_display[status]
        selected.append((display_name, status_label, facecolor, edgecolor))

    fig, ax = plt.subplots(figsize=(12, 6.8))
    ax.set_xlim(0, 1)
    ax.set_ylim(len(selected) + 0.4, -1.15)
    ax.axis("off")
    ax.text(
        0.5,
        -0.82,
        "Reviewed Phase 51 Candidate Options",
        ha="center",
        va="center",
        fontsize=17,
        fontweight="bold",
        color=COLORS["navy"],
    )
    ax.text(
        0.5,
        -0.38,
        "Candidate listing is not experiment authorization.",
        ha="center",
        va="center",
        fontsize=10,
        color=COLORS["red"],
        fontweight="bold",
    )
    for index, (name, status_label, facecolor, edgecolor) in enumerate(selected):
        box = FancyBboxPatch(
            (0.05, index + 0.05),
            0.9,
            0.72,
            boxstyle="round,pad=0.02,rounding_size=0.035",
            linewidth=1.4,
            edgecolor=edgecolor,
            facecolor=facecolor,
        )
        ax.add_patch(box)
        ax.text(
            0.09,
            index + 0.41,
            textwrap.fill(name, width=43),
            ha="left",
            va="center",
            fontsize=11,
            color=COLORS["dark"],
        )
        ax.text(
            0.91,
            index + 0.41,
            status_label,
            ha="right",
            va="center",
            fontsize=10,
            fontweight="bold",
            color=edgecolor,
        )
    return save_figure(fig, output_dir, "phase50_reviewed_next_steps_matrix.png", dpi)


def write_summary(
    output_dir: Path,
    generated: list[Path],
    input_dir: Path,
) -> Path:
    summary_path = output_dir / "phase50_figure_summary.md"
    source_paths = (
        input_dir / "phase50_evidence_chain_table.csv",
        input_dir / "phase50_key_metrics_summary.csv",
        input_dir / "phase50_claim_boundary_table.csv",
        input_dir / "phase50_recommended_next_steps.csv",
        input_dir / "phase50_framework_synthesis.json",
        resolve_repo_path(PHASE49_SUMMARY),
        resolve_repo_path(PHASE48_SUMMARY),
        resolve_repo_path(PHASE47_SUMMARY),
    )
    lines = [
        "# Phase 50 Figure Summary",
        "",
        "Generated README-facing figures:",
        "",
        *[f"- `{path.name}`" for path in generated],
        "",
        "Source artifacts:",
        "",
        *[
            f"- `{path.relative_to(REPO_ROOT).as_posix()}`"
            for path in source_paths
        ],
        "",
        "Guardrails:",
        "",
        "- Visualization only; no training or new experiments.",
        "- Level 5 is not supported.",
        "- Warning labels are conservative diagnostic screening labels, not calibrated probabilities.",
        "- Physical proxy diagnostics do not establish strict conservation, full mass conservation, or hydrodynamic closure.",
        "- Candidate Phase 51 training options remain subject to review or explicit authorization.",
        "",
    ]
    summary_path.write_text("\n".join(lines), encoding="utf-8")
    return summary_path


def main() -> None:
    args = parse_args()
    input_dir = resolve_repo_path(args.input_dir).resolve()
    output_dir = resolve_repo_path(args.output_dir).resolve()
    if args.dpi <= 0:
        raise ValueError("--dpi must be positive")

    configure_style()
    (
        evidence_rows,
        metric_values,
        _claim_rows,
        next_step_rows,
        synthesis,
        warning_counts,
    ) = validate_and_load(input_dir)

    generated = [
        plot_evidence_chain(evidence_rows, output_dir, args.dpi),
        plot_key_metrics(metric_values, output_dir, args.dpi),
        plot_warning_counts(warning_counts, output_dir, args.dpi),
        plot_claim_boundary(output_dir, args.dpi),
        plot_next_steps(next_step_rows, input_dir, output_dir, args.dpi),
    ]
    write_summary(output_dir, generated, input_dir)

    print(f"figures_written={len(generated)}")
    print(f"output_dir={output_dir.relative_to(REPO_ROOT).as_posix()}")
    print(f"no_training={str(synthesis['no_training']).lower()}")
    print(f"level5_supported={str(synthesis['level5_supported']).lower()}")
    print(
        "warning_labels_are_probabilities="
        f"{str(synthesis['warning_labels_are_probabilities']).lower()}"
    )


if __name__ == "__main__":
    main()
