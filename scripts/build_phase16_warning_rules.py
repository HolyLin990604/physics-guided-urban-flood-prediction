from __future__ import annotations

import argparse
import csv
import json
import math
import warnings
from collections import Counter
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np

try:
    import pandas as pd
except ModuleNotFoundError:  # pragma: no cover - exercised only in lean runtime environments.
    pd = None


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT_DIR = Path("analysis/phase15_reliability_screening")
DEFAULT_OUTPUT_DIR = Path("analysis/phase16_warning_rules")

REQUIRED_INPUTS = {
    "summary": "summary.json",
    "scenario": "scenario_risk_scores.csv",
    "pixel": "pixel_risk_summary.csv",
    "high_risk": "high_risk_cases.csv",
}

INTERPRETATION_NOTE = (
    "Warning labels are operational interpretation labels derived from deterministic Phase 15 "
    "screening outputs. They are not calibrated probabilities, Bayesian uncertainty estimates, "
    "or formal confidence intervals."
)

ACTION_MATRIX: dict[str, dict[str, str]] = {
    "reliable": {
        "recommendation": "use_as_rapid_reference",
        "review_level": "normal_review",
        "action": "use as rapid prediction reference",
        "use_note": "Prediction is within the stronger applicability range of the current surrogate model.",
    },
    "caution": {
        "recommendation": "use_with_targeted_review",
        "review_level": "targeted_review",
        "action": "use with targeted review",
        "use_note": (
            "Inspect wet/dry boundaries, shallow transition areas, local peak-depth areas, "
            "and pixel-level risk maps."
        ),
    },
    "high-risk": {
        "recommendation": "do_not_use_alone",
        "review_level": "mandatory_review",
        "action": "do not use alone for warning decisions",
        "use_note": (
            "Trigger conservative interpretation, hydrodynamic-model confirmation, or expert "
            "review before warning decisions."
        ),
    },
}

PIXEL_WARNING_THRESHOLDS = {
    "high_risk_case_fraction_high": 0.05,
    "false_dry_fraction_high": 0.10,
    "deep_underprediction_fraction_high": 0.25,
    "false_dry_fraction_caution": 0.0,
    "low_margin_fraction_caution": 0.10,
    "boundary_fraction_caution": 0.10,
    "deep_underprediction_fraction_caution": 0.10,
}

SCENARIO_WARNING_THRESHOLDS = {
    "false_dry_rate_warning": 0.10,
    "wet_fraction_contraction_warning": 0.15,
    "peak_underprediction_warning_m": 0.25,
}


def display_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def resolve_repo_path(path: Path) -> Path:
    return path if path.is_absolute() else REPO_ROOT / path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Build Phase 16 reliability-aware warning rules and applicability-boundary guidance "
            "from existing Phase 15 deterministic screening outputs."
        )
    )
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=DEFAULT_INPUT_DIR,
        help=f"Directory containing Phase 15 outputs. Default: {DEFAULT_INPUT_DIR}",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help=f"Directory for Phase 16 warning-rule outputs. Default: {DEFAULT_OUTPUT_DIR}",
    )
    return parser.parse_args()


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, data: dict[str, Any]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, sort_keys=True)
        handle.write("\n")


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError(f"{display_path(path)} does not contain a CSV header.")
        return [dict(row) for row in reader]


def write_csv_rows(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def require_inputs(input_dir: Path) -> dict[str, Path]:
    paths = {key: input_dir / name for key, name in REQUIRED_INPUTS.items()}
    missing = [display_path(path) for path in paths.values() if not path.exists()]
    if missing:
        raise FileNotFoundError(
            "Phase 16 requires existing Phase 15 outputs and does not regenerate them. "
            "Missing required file(s): " + ", ".join(missing)
        )
    return paths


def to_float(row: dict[str, Any], field: str, default: float = 0.0) -> float:
    value = row.get(field, "")
    if value in ("", None):
        return default
    try:
        number = float(value)
    except (TypeError, ValueError):
        return default
    if math.isnan(number) or math.isinf(number):
        return default
    return number


def to_int(row: dict[str, Any], field: str, default: int = 0) -> int:
    value = row.get(field, "")
    if value in ("", None):
        return default
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return default


def warn_missing_fields(rows: list[dict[str, str]], required_fields: list[str], source_name: str) -> list[str]:
    available = set(rows[0].keys()) if rows else set()
    missing = [field for field in required_fields if field not in available]
    for field in missing:
        warnings.warn(f"Optional field {field!r} is unavailable in {source_name}.", stacklevel=2)
    return missing


def ordered_counts(values: list[str], order: list[str]) -> dict[str, int]:
    counts = Counter(values)
    return {key: int(counts.get(key, 0)) for key in order}


def scenario_warning_reasons(row: dict[str, Any]) -> list[str]:
    reasons: list[str] = []
    category = row.get("risk_category", "")
    if category == "reliable":
        reasons.append("Phase 15 risk score is in the reliable screening range.")
    elif category == "caution":
        reasons.append("Phase 15 risk score is in the caution screening range.")
    elif category == "high-risk":
        reasons.append("Phase 15 risk score is in the high-risk screening range.")
    else:
        reasons.append("Phase 15 risk category is unavailable or unrecognized.")

    if to_float(row, "false_dry_rate") >= SCENARIO_WARNING_THRESHOLDS["false_dry_rate_warning"]:
        reasons.append("False-dry rate indicates possible missed-inundation risk.")
    if to_float(row, "wet_fraction_contraction") >= SCENARIO_WARNING_THRESHOLDS["wet_fraction_contraction_warning"]:
        reasons.append("Predicted wet fraction is contracted relative to the target.")
    if to_float(row, "peak_underprediction") >= SCENARIO_WARNING_THRESHOLDS["peak_underprediction_warning_m"]:
        reasons.append("Peak depth is underpredicted enough to require local-depth review.")
    if row.get("high_intensity_reason"):
        reasons.append(f"High-intensity metadata flag: {row['high_intensity_reason']}.")
    if to_float(row, "boundary_false_dry_rate") >= SCENARIO_WARNING_THRESHOLDS["false_dry_rate_warning"]:
        reasons.append("Boundary-zone false-dry signal requires wet/dry edge review.")
    return reasons


def convert_scenario_rows(rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    converted: list[dict[str, Any]] = []
    for row in rows:
        category = row.get("risk_category", "")
        action = ACTION_MATRIX.get(category, ACTION_MATRIX["caution"])
        warning_reasons = scenario_warning_reasons(row)
        out = dict(row)
        out.update(
            {
                "warning_level": category if category in ACTION_MATRIX else "caution",
                "recommendation": action["recommendation"],
                "review_level": action["review_level"],
                "warning_action": action["action"],
                "use_note": action["use_note"],
                "missed_inundation_warning": str(
                    to_float(row, "false_dry_rate") >= SCENARIO_WARNING_THRESHOLDS["false_dry_rate_warning"]
                ),
                "extent_underestimation_warning": str(
                    to_float(row, "wet_fraction_contraction")
                    >= SCENARIO_WARNING_THRESHOLDS["wet_fraction_contraction_warning"]
                ),
                "local_depth_underestimation_warning": str(
                    to_float(row, "peak_underprediction")
                    >= SCENARIO_WARNING_THRESHOLDS["peak_underprediction_warning_m"]
                ),
                "applicability_boundary_warning": str(bool(row.get("high_intensity_reason")) or category == "high-risk"),
                "warning_reasons": " | ".join(warning_reasons),
                "interpretation_note": INTERPRETATION_NOTE,
            }
        )
        converted.append(out)
    return converted


def pixel_warning_level(row: dict[str, str]) -> str:
    if (
        to_float(row, "high_risk_case_fraction") >= PIXEL_WARNING_THRESHOLDS["high_risk_case_fraction_high"]
        or to_float(row, "false_dry_fraction") >= PIXEL_WARNING_THRESHOLDS["false_dry_fraction_high"]
        or to_float(row, "deep_underprediction_fraction")
        >= PIXEL_WARNING_THRESHOLDS["deep_underprediction_fraction_high"]
    ):
        return "high-risk"
    if (
        to_float(row, "false_dry_fraction") > PIXEL_WARNING_THRESHOLDS["false_dry_fraction_caution"]
        or to_float(row, "low_margin_fraction") >= PIXEL_WARNING_THRESHOLDS["low_margin_fraction_caution"]
        or to_float(row, "boundary_fraction") >= PIXEL_WARNING_THRESHOLDS["boundary_fraction_caution"]
        or to_float(row, "deep_underprediction_fraction")
        >= PIXEL_WARNING_THRESHOLDS["deep_underprediction_fraction_caution"]
    ):
        return "caution"
    return "reliable"


def pixel_warning_reasons(row: dict[str, str], level: str) -> str:
    reasons: list[str] = []
    if to_float(row, "false_dry_fraction") > 0:
        reasons.append("repeated_false_dry")
    if to_float(row, "low_margin_fraction") >= PIXEL_WARNING_THRESHOLDS["low_margin_fraction_caution"]:
        reasons.append("low_confidence_margin")
    if to_float(row, "boundary_fraction") >= PIXEL_WARNING_THRESHOLDS["boundary_fraction_caution"]:
        reasons.append("wet_dry_boundary")
    if to_float(row, "deep_underprediction_fraction") >= PIXEL_WARNING_THRESHOLDS["deep_underprediction_fraction_caution"]:
        reasons.append("deep_underprediction")
    if to_float(row, "high_risk_case_fraction") >= PIXEL_WARNING_THRESHOLDS["high_risk_case_fraction_high"]:
        reasons.append("repeated_high_risk_case_pixel")
    if not reasons:
        reasons.append(f"{level}_pixel_screening_label")
    return " | ".join(reasons)


def convert_pixel_rows(rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    converted: list[dict[str, Any]] = []
    for row in rows:
        level = pixel_warning_level(row)
        action = ACTION_MATRIX[level]
        out = dict(row)
        out.update(
            {
                "pixel_warning_level": level,
                "recommendation": action["recommendation"],
                "review_level": action["review_level"],
                "pixel_warning_note": pixel_warning_reasons(row, level),
                "interpretation_note": INTERPRETATION_NOTE,
            }
        )
        converted.append(out)
    return converted


def build_applicability_boundary_rows() -> list[dict[str, str]]:
    return [
        {
            "condition_type": "ordinary test scenarios",
            "condition_description": "Scenarios with Phase 15 reliable labels and no strong risk components.",
            "reliability_level": "stronger applicability",
            "evidence_source": "Phase 15 scenario_risk_scores.csv reliable category",
            "recommended_use": "Use as a rapid flood-depth reference with normal review.",
            "caution_note": INTERPRETATION_NOTE,
        },
        {
            "condition_type": "wet/dry boundary cells",
            "condition_description": "Cells near predicted or target wet/dry transitions.",
            "reliability_level": "caution",
            "evidence_source": "Phase 15 boundary false-dry and pixel boundary fractions",
            "recommended_use": "Inspect with pixel risk maps and avoid overinterpreting exact edge placement.",
            "caution_note": "Wet/dry boundaries are sensitive to small depth and threshold changes.",
        },
        {
            "condition_type": "shallow threshold-adjacent cells",
            "condition_description": "Cells near the wet-depth threshold or low confidence-margin band.",
            "reliability_level": "caution",
            "evidence_source": "Phase 15 low_margin_fraction and pixel low_margin_count",
            "recommended_use": "Use with targeted review of shallow transition areas.",
            "caution_note": "These labels are screening indicators, not calibrated confidence intervals.",
        },
        {
            "condition_type": "high-intensity location2+r300y cases",
            "condition_description": "Known Phase 13-like location2+r300y high-intensity cases.",
            "reliability_level": "high-risk",
            "evidence_source": "Phase 15 high_intensity_reason and Phase 13 consistency check",
            "recommended_use": "Do not use prediction alone; trigger hydrodynamic-model or expert confirmation.",
            "caution_note": "This is an applicability-boundary warning for the current surrogate model.",
        },
        {
            "condition_type": "local peak-depth extremes",
            "condition_description": "Cases or pixels with peak-depth underprediction or deep-depth underprediction signals.",
            "reliability_level": "caution to high-risk",
            "evidence_source": "Phase 15 peak_underprediction and deep_underprediction_fraction",
            "recommended_use": "Check possible local-depth underprediction before warning decisions.",
            "caution_note": "Peak-depth review is required where local maxima control warning severity.",
        },
        {
            "condition_type": "repeated false-dry pixels",
            "condition_description": "Pixels repeatedly dry in prediction when wet in target across Phase 15 screening artifacts.",
            "reliability_level": "high-risk spatial caution",
            "evidence_source": "Phase 15 pixel false_dry_fraction",
            "recommended_use": "Treat as missed-inundation caution zones in spatial warning interpretation.",
            "caution_note": "Repeated false-dry labels indicate spatial screening risk, not event probability.",
        },
        {
            "condition_type": "strong wet-fraction contraction cases",
            "condition_description": "Scenarios where predicted inundation extent is substantially smaller than target extent.",
            "reliability_level": "caution to high-risk",
            "evidence_source": "Phase 15 wet_fraction_contraction component",
            "recommended_use": "Review inundation extent before operational warning use.",
            "caution_note": "Contraction can indicate extent underestimation in rapid surrogate predictions.",
        },
    ]


def save_warning_level_counts(path: Path, counts: dict[str, int]) -> None:
    labels = ["reliable", "caution", "high-risk"]
    values = [counts.get(label, 0) for label in labels]
    colors = ["#3b7f5c", "#c8922d", "#b84a4a"]
    fig, ax = plt.subplots(figsize=(7, 4.5))
    bars = ax.bar(labels, values, color=colors)
    ax.set_title("Phase 16 Warning-Level Counts")
    ax.set_ylabel("Scenario count")
    ax.set_xlabel("Operational warning label")
    ax.bar_label(bars, padding=3)
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)


def save_action_matrix(path: Path) -> None:
    labels = ["reliable", "caution", "high-risk"]
    table_data = [
        [label, ACTION_MATRIX[label]["recommendation"], ACTION_MATRIX[label]["review_level"]]
        for label in labels
    ]
    fig, ax = plt.subplots(figsize=(10, 3.5))
    ax.axis("off")
    table = ax.table(
        cellText=table_data,
        colLabels=["Warning label", "Recommendation", "Review level"],
        cellLoc="left",
        colLoc="left",
        loc="center",
    )
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 1.8)
    for (row, _col), cell in table.get_celld().items():
        if row == 0:
            cell.set_text_props(weight="bold")
            cell.set_facecolor("#e7e9ec")
    ax.set_title("Warning Action Matrix", pad=16)
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)


def save_applicability_summary(path: Path, rows: list[dict[str, str]]) -> None:
    order = ["stronger applicability", "caution", "high-risk", "caution to high-risk", "high-risk spatial caution"]
    counts = ordered_counts([row["reliability_level"] for row in rows], order)
    labels = [label for label, value in counts.items() if value > 0]
    values = [counts[label] for label in labels]
    fig, ax = plt.subplots(figsize=(9, 4.8))
    bars = ax.barh(labels, values, color="#58799a")
    ax.set_title("Applicability-Boundary Guidance Rows")
    ax.set_xlabel("Row count")
    ax.bar_label(bars, padding=3)
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)


def save_high_risk_distribution(path: Path, high_risk_rows: list[dict[str, Any]]) -> None:
    if not high_risk_rows:
        fig, ax = plt.subplots(figsize=(7, 4))
        ax.text(0.5, 0.5, "No high-risk warning cases", ha="center", va="center")
        ax.axis("off")
        fig.tight_layout()
        fig.savefig(path, dpi=180)
        plt.close(fig)
        return
    keys = [f"{row.get('location', 'unknown')} | {row.get('event', 'unknown')}" for row in high_risk_rows]
    counts = Counter(keys)
    labels, values = zip(*sorted(counts.items(), key=lambda item: (-item[1], item[0])))
    fig_height = max(4.5, 0.38 * len(labels) + 1.5)
    fig, ax = plt.subplots(figsize=(10, fig_height))
    bars = ax.barh(list(labels), list(values), color="#b84a4a")
    ax.invert_yaxis()
    ax.set_title("High-Risk Warning Case Distribution")
    ax.set_xlabel("Case count")
    ax.bar_label(bars, padding=3)
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)


def save_pixel_warning_map(path: Path, pixel_rows: list[dict[str, Any]]) -> bool:
    if not pixel_rows:
        warnings.warn("Pixel warning map was not generated because pixel rows are unavailable.", stacklevel=2)
        return False
    max_row = max(to_int(row, "row") for row in pixel_rows)
    max_col = max(to_int(row, "col") for row in pixel_rows)
    if max_row < 0 or max_col < 0:
        warnings.warn("Pixel warning map was not generated because row/col coordinates are invalid.", stacklevel=2)
        return False
    grid = np.zeros((max_row + 1, max_col + 1), dtype=np.float64)
    level_values = {"reliable": 0.0, "caution": 1.0, "high-risk": 2.0}
    for row in pixel_rows:
        grid[to_int(row, "row"), to_int(row, "col")] = level_values.get(str(row.get("pixel_warning_level")), 1.0)
    fig, ax = plt.subplots(figsize=(6, 5.4))
    cmap = matplotlib.colors.ListedColormap(["#3b7f5c", "#c8922d", "#b84a4a"])
    image = ax.imshow(grid, cmap=cmap, vmin=-0.5, vmax=2.5, origin="upper")
    cbar = fig.colorbar(image, ax=ax, ticks=[0, 1, 2], fraction=0.046, pad=0.04)
    cbar.ax.set_yticklabels(["reliable", "caution", "high-risk"])
    ax.set_title("Pixel Warning Map Example")
    ax.set_xlabel("Column")
    ax.set_ylabel("Row")
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)
    return True


def aggregate_numeric(rows: list[dict[str, Any]], field: str) -> dict[str, float]:
    values = np.asarray([to_float(row, field) for row in rows], dtype=np.float64)
    if values.size == 0:
        return {"mean": 0.0, "max": 0.0}
    return {"mean": float(np.mean(values)), "max": float(np.max(values))}


def main() -> None:
    args = parse_args()
    input_dir = resolve_repo_path(args.input_dir)
    output_dir = resolve_repo_path(args.output_dir)
    figures_dir = output_dir / "figures"
    output_dir.mkdir(parents=True, exist_ok=True)
    figures_dir.mkdir(parents=True, exist_ok=True)

    input_paths = require_inputs(input_dir)
    phase15_summary = read_json(input_paths["summary"])
    scenario_rows = read_csv_rows(input_paths["scenario"])
    pixel_rows = read_csv_rows(input_paths["pixel"])
    high_risk_rows = read_csv_rows(input_paths["high_risk"])

    if not scenario_rows:
        raise ValueError(f"{display_path(input_paths['scenario'])} contains no scenario rows.")
    if not pixel_rows:
        raise ValueError(f"{display_path(input_paths['pixel'])} contains no pixel rows.")

    missing_scenario_fields = warn_missing_fields(
        scenario_rows,
        ["risk_category", "false_dry_rate", "wet_fraction_contraction", "peak_underprediction"],
        "scenario_risk_scores.csv",
    )
    missing_pixel_fields = warn_missing_fields(
        pixel_rows,
        ["row", "col", "false_dry_fraction", "low_margin_fraction", "boundary_fraction"],
        "pixel_risk_summary.csv",
    )

    scenario_warning_rows = convert_scenario_rows(scenario_rows)
    high_risk_warning_rows = convert_scenario_rows(high_risk_rows)
    pixel_warning_rows = convert_pixel_rows(pixel_rows)
    applicability_rows = build_applicability_boundary_rows()

    scenario_fieldnames = list(scenario_rows[0].keys()) + [
        "warning_level",
        "recommendation",
        "review_level",
        "warning_action",
        "use_note",
        "missed_inundation_warning",
        "extent_underestimation_warning",
        "local_depth_underestimation_warning",
        "applicability_boundary_warning",
        "warning_reasons",
        "interpretation_note",
    ]
    pixel_fieldnames = list(pixel_rows[0].keys()) + [
        "pixel_warning_level",
        "recommendation",
        "review_level",
        "pixel_warning_note",
        "interpretation_note",
    ]
    applicability_fieldnames = [
        "condition_type",
        "condition_description",
        "reliability_level",
        "evidence_source",
        "recommended_use",
        "caution_note",
    ]

    write_csv_rows(output_dir / "scenario_warning_summary.csv", scenario_warning_rows, scenario_fieldnames)
    write_csv_rows(output_dir / "high_risk_warning_cases.csv", high_risk_warning_rows, scenario_fieldnames)
    write_csv_rows(output_dir / "pixel_warning_summary.csv", pixel_warning_rows, pixel_fieldnames)
    write_csv_rows(output_dir / "applicability_boundary_table.csv", applicability_rows, applicability_fieldnames)

    scenario_counts = ordered_counts([str(row.get("warning_level")) for row in scenario_warning_rows], list(ACTION_MATRIX))
    pixel_counts = ordered_counts([str(row.get("pixel_warning_level")) for row in pixel_warning_rows], list(ACTION_MATRIX))

    rules = {
        "phase": "Phase 16 Reliability-Aware Warning Rules and Applicability Boundary",
        "interpretation_note": INTERPRETATION_NOTE,
        "constraints": {
            "reads_existing_phase15_outputs_only": True,
            "trained_model": False,
            "evaluated_model_from_checkpoint": False,
            "modified_model_architecture": False,
            "modified_phase10_loss": False,
            "tuned_boundary_weight": False,
            "tuned_boundary_band_pixels": False,
            "opened_new_sweep": False,
        },
        "action_matrix": ACTION_MATRIX,
        "scenario_warning_thresholds": SCENARIO_WARNING_THRESHOLDS,
        "pixel_warning_thresholds": PIXEL_WARNING_THRESHOLDS,
        "applicability_boundary_rows": applicability_rows,
        "limitations": [
            INTERPRETATION_NOTE,
            "The rules convert Phase 15 screening labels into operational guidance; they do not replace hydrodynamic simulation or expert judgment in high-stakes final warning decisions.",
            "Pixel warning labels summarize repeated screening signals and should be interpreted as spatial caution guidance.",
        ],
    }
    write_json(output_dir / "warning_rules.json", rules)

    generated_figures = {
        "warning_level_counts": figures_dir / "warning_level_counts.png",
        "warning_action_matrix": figures_dir / "warning_action_matrix.png",
        "applicability_boundary_summary": figures_dir / "applicability_boundary_summary.png",
        "high_risk_warning_case_distribution": figures_dir / "high_risk_warning_case_distribution.png",
    }
    save_warning_level_counts(generated_figures["warning_level_counts"], scenario_counts)
    save_action_matrix(generated_figures["warning_action_matrix"])
    save_applicability_summary(generated_figures["applicability_boundary_summary"], applicability_rows)
    save_high_risk_distribution(generated_figures["high_risk_warning_case_distribution"], high_risk_warning_rows)
    pixel_map_generated = save_pixel_warning_map(figures_dir / "pixel_warning_map_example.png", pixel_warning_rows)

    if pixel_map_generated:
        generated_figures["pixel_warning_map_example"] = figures_dir / "pixel_warning_map_example.png"

    phase13_check = phase15_summary.get("phase13_like_location2_check", {})
    summary = {
        "phase": "Phase 16 Reliability-Aware Warning Rules and Applicability Boundary",
        "interpretation_note": INTERPRETATION_NOTE,
        "inputs": {
            "input_dir": display_path(input_dir),
            "phase15_summary": display_path(input_paths["summary"]),
            "scenario_risk_scores_csv": display_path(input_paths["scenario"]),
            "pixel_risk_summary_csv": display_path(input_paths["pixel"]),
            "high_risk_cases_csv": display_path(input_paths["high_risk"]),
            "pandas_available": pd is not None,
            "missing_optional_fields": {
                "scenario": missing_scenario_fields,
                "pixel": missing_pixel_fields,
            },
        },
        "constraints": rules["constraints"],
        "warning_rules": {
            "action_matrix": ACTION_MATRIX,
            "scenario_warning_thresholds": SCENARIO_WARNING_THRESHOLDS,
            "pixel_warning_thresholds": PIXEL_WARNING_THRESHOLDS,
        },
        "row_counts": {
            "scenario_warning_summary": len(scenario_warning_rows),
            "pixel_warning_summary": len(pixel_warning_rows),
            "high_risk_warning_cases": len(high_risk_warning_rows),
            "applicability_boundary_table": len(applicability_rows),
        },
        "warning_level_counts": scenario_counts,
        "pixel_warning_level_counts": pixel_counts,
        "scenario_metric_summaries": {
            "risk_score": aggregate_numeric(scenario_warning_rows, "risk_score"),
            "false_dry_rate": aggregate_numeric(scenario_warning_rows, "false_dry_rate"),
            "wet_fraction_contraction": aggregate_numeric(scenario_warning_rows, "wet_fraction_contraction"),
            "peak_underprediction": aggregate_numeric(scenario_warning_rows, "peak_underprediction"),
        },
        "phase15_consistency": {
            "phase15_category_counts": phase15_summary.get("category_counts", {}),
            "phase15_high_risk_case_count": phase15_summary.get("row_counts", {}).get("high_risk_cases"),
            "phase16_high_risk_warning_case_count": len(high_risk_warning_rows),
            "phase13_like_location2_check": phase13_check,
        },
        "outputs": {
            "summary_json": display_path(output_dir / "summary.json"),
            "warning_rules_json": display_path(output_dir / "warning_rules.json"),
            "scenario_warning_summary_csv": display_path(output_dir / "scenario_warning_summary.csv"),
            "applicability_boundary_table_csv": display_path(output_dir / "applicability_boundary_table.csv"),
            "high_risk_warning_cases_csv": display_path(output_dir / "high_risk_warning_cases.csv"),
            "pixel_warning_summary_csv": display_path(output_dir / "pixel_warning_summary.csv"),
            "figures": [display_path(path) for path in generated_figures.values()],
        },
        "limitations": rules["limitations"],
    }
    write_json(output_dir / "summary.json", summary)

    print(f"Wrote Phase 16 warning-rule outputs to {display_path(output_dir)}")
    print(f"Scenario warning counts: {scenario_counts}")
    print(f"Pixel warning counts: {pixel_counts}")


if __name__ == "__main__":
    main()
