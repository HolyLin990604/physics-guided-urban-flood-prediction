from __future__ import annotations

import argparse
import csv
import json
import math
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT_DIR = Path("analysis/phase48_full_dataset_reliability_physical_proxy")
DEFAULT_OUTPUT_DIR = Path("analysis/phase49_full_dataset_warning_framework")

REQUIRED_INPUTS = {
    "reliability_warning_levels": "reliability_warning_levels.csv",
    "scenario_reliability_metrics": "scenario_reliability_metrics.csv",
    "wet_dry_error_metrics": "wet_dry_error_metrics.csv",
    "peak_depth_timing_metrics": "peak_depth_timing_metrics.csv",
    "volume_response_proxy_metrics": "volume_response_proxy_metrics.csv",
    "location_type_summary": "location_type_summary.csv",
    "phase48_reliability_summary_json": "phase48_reliability_summary.json",
    "phase48_reliability_summary_md": "phase48_reliability_summary.md",
}

WARNING_ACTIONS = {
    "reliable": "normal_use_with_standard_monitoring",
    "caution": "use_with_caution_and_review_diagnostics",
    "high-risk": "high_risk_requires_review_or_supplemental_evidence",
}

MESSAGE_KEYS = {
    "reliable": "reliable_scenario_message",
    "caution": "caution_scenario_message",
    "high-risk": "high_risk_scenario_message",
}

INTERPRETATION_NOTE = (
    "Phase 49 preserves Phase 48 warning labels as conservative diagnostic screening labels; "
    "they are not calibrated probabilities, event likelihoods, or final production guarantees."
)

DECISION_COMPLETED = "phase49_warning_framework_completed_with_conservative_labels"
DECISION_BLOCKED = "phase49_warning_framework_blocked_by_missing_phase48_inputs"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Build the no-training Phase 49 warning framework from existing Phase 48 "
            "full-dataset reliability and physical proxy diagnostics."
        )
    )
    parser.add_argument("--input-dir", type=Path, default=DEFAULT_INPUT_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    return parser.parse_args()


def repo_path(path: Path) -> Path:
    return path if path.is_absolute() else REPO_ROOT / path


def display_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError(f"{display_path(path)} does not contain a CSV header.")
        return [dict(row) for row in reader]


def write_csv_rows(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def to_float(value: Any, default: float = 0.0) -> float:
    if value in ("", None):
        return default
    try:
        number = float(value)
    except (TypeError, ValueError):
        return default
    if math.isnan(number) or math.isinf(number):
        return default
    return number


def mean(values: list[float]) -> float:
    return float(sum(values) / len(values)) if values else 0.0


def ordered_counts(values: list[str]) -> dict[str, int]:
    counts = Counter(values)
    return {level: int(counts.get(level, 0)) for level in WARNING_ACTIONS}


def scenario_key(row: dict[str, Any]) -> tuple[str, str, str, str]:
    return (
        str(row.get("split", "")),
        str(row.get("location", "")),
        str(row.get("scenario", "")),
        str(row.get("scenario_type", "")),
    )


def check_inputs(input_dir: Path) -> tuple[dict[str, Path], list[str]]:
    paths = {key: input_dir / filename for key, filename in REQUIRED_INPUTS.items()}
    missing = [display_path(path) for path in paths.values() if not path.exists()]
    return paths, missing


def write_blocked_outputs(output_dir: Path, input_dir: Path, missing_inputs: list[str]) -> None:
    now = datetime.now(timezone.utc).isoformat()
    decision = {
        "created_utc": now,
        "phase": 49,
        "selected_decision": DECISION_BLOCKED,
        "input_dir": display_path(input_dir),
        "input_files_found": False,
        "missing_inputs": missing_inputs,
        "no_training": True,
        "no_swe_pinn": True,
        "level5_supported": False,
        "warning_labels_are_probabilities": False,
        "next_recommended_action": "Regenerate or restore the missing Phase 48 diagnostic artifacts before building Phase 49 warning outputs.",
    }
    write_json(output_dir / "phase49_warning_framework_decision.json", decision)
    write_json(output_dir / "warning_framework_summary.json", decision)
    (output_dir / "warning_framework_summary.md").write_text(
        "# Phase 49 Warning Framework Summary\n\n"
        f"Selected decision: `{DECISION_BLOCKED}`.\n\n"
        "Phase 49 was blocked because required Phase 48 inputs were missing. "
        "No training was run, no SWE/PINN components were introduced, and no Level 5 support is claimed.\n",
        encoding="utf-8",
    )


def merge_metric_rows(base_rows: list[dict[str, str]], extra_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    merged = [dict(row) for row in base_rows]
    by_key = {scenario_key(row): row for row in extra_rows}
    for row in merged:
        extra = by_key.get(scenario_key(row), {})
        for field, value in extra.items():
            if field not in row or row[field] == "":
                row[field] = value
    return merged


def validate_labels_preserved(
    scenario_rows: list[dict[str, str]],
    warning_rows: list[dict[str, str]],
) -> None:
    warning_by_key = {scenario_key(row): row.get("warning_level", "") for row in warning_rows}
    missing_keys = [scenario_key(row) for row in scenario_rows if scenario_key(row) not in warning_by_key]
    mismatches = [
        scenario_key(row)
        for row in scenario_rows
        if warning_by_key.get(scenario_key(row), row.get("warning_level", "")) != row.get("warning_level", "")
    ]
    if missing_keys or mismatches:
        raise ValueError(
            "Phase 49 requires Phase 48 labels to be preserved. "
            f"Missing label rows: {len(missing_keys)}; mismatched labels: {len(mismatches)}."
        )


def thresholds_from_summary(summary: dict[str, Any]) -> dict[str, float]:
    raw = summary.get("warning_thresholds", {})
    return {key: to_float(value) for key, value in raw.items()}


def failure_drivers(row: dict[str, Any], thresholds: dict[str, float]) -> list[str]:
    drivers: list[str] = []
    if to_float(row.get("rmse")) >= thresholds.get("rmse_reliable_max", math.inf):
        drivers.append("high RMSE")
    if to_float(row.get("wet_dry_iou"), 1.0) <= thresholds.get("wet_dry_iou_reliable_min", -math.inf):
        drivers.append("low wet/dry IoU")
    if to_float(row.get("false_dry_rate")) >= thresholds.get("false_dry_reliable_max", math.inf):
        drivers.append("elevated false-dry rate")
    if to_float(row.get("false_wet_rate")) >= thresholds.get("false_wet_reliable_max", math.inf):
        drivers.append("elevated false-wet rate")
    if to_float(row.get("absolute_relative_volume_bias_proxy")) >= thresholds.get(
        "absolute_relative_volume_bias_reliable_max", math.inf
    ):
        drivers.append("elevated volume-bias proxy")
    if to_float(row.get("peak_depth_underprediction_proxy")) > 0.0:
        drivers.append("peak-depth underprediction proxy")
    if not drivers:
        drivers.append("no major Phase 48 failure driver flagged")
    return drivers


def scenario_priority_score(row: dict[str, Any], thresholds: dict[str, float]) -> float:
    rmse_scale = max(thresholds.get("rmse_high_risk_min", 0.0), 1.0e-8)
    iou_scale = max(1.0 - thresholds.get("wet_dry_iou_high_risk_max", 1.0), 1.0e-8)
    false_dry_scale = max(thresholds.get("false_dry_high_risk_min", 0.0), 1.0e-8)
    false_wet_scale = max(thresholds.get("false_wet_high_risk_min", 0.0), 1.0e-8)
    volume_scale = max(thresholds.get("absolute_relative_volume_bias_high_risk_min", 0.0), 1.0e-8)
    return float(
        to_float(row.get("rmse")) / rmse_scale
        + max(0.0, 1.0 - to_float(row.get("wet_dry_iou"), 1.0)) / iou_scale
        + to_float(row.get("false_dry_rate")) / false_dry_scale
        + to_float(row.get("false_wet_rate")) / false_wet_scale
        + to_float(row.get("absolute_relative_volume_bias_proxy")) / volume_scale
        + to_float(row.get("peak_depth_underprediction_proxy"))
    )


def build_scenario_framework(rows: list[dict[str, str]], thresholds: dict[str, float]) -> list[dict[str, Any]]:
    framework_rows: list[dict[str, Any]] = []
    for row in rows:
        level = row.get("warning_level", "")
        if level not in WARNING_ACTIONS:
            raise ValueError(f"Unexpected Phase 48 warning label: {level!r}")
        drivers = failure_drivers(row, thresholds)
        framework_rows.append(
            {
                "split": row.get("split", ""),
                "location": row.get("location", ""),
                "scenario": row.get("scenario", ""),
                "scenario_type": row.get("scenario_type", ""),
                "warning_level": level,
                "warning_action": WARNING_ACTIONS[level],
                "rmse": row.get("rmse", ""),
                "mae": row.get("mae", ""),
                "wet_dry_iou": row.get("wet_dry_iou", ""),
                "false_dry_rate": row.get("false_dry_rate", ""),
                "false_wet_rate": row.get("false_wet_rate", ""),
                "relative_volume_bias_proxy": row.get("relative_volume_bias_proxy", ""),
                "absolute_relative_volume_bias_proxy": row.get("absolute_relative_volume_bias_proxy", ""),
                "peak_depth_underprediction_proxy": row.get("peak_depth_underprediction_proxy", ""),
                "failure_drivers": " | ".join(drivers),
                "user_message_key": MESSAGE_KEYS[level],
                "interpretation_note": INTERPRETATION_NOTE,
            }
        )
    return framework_rows


def build_location_type_summary(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        groups[(str(row.get("location", "")), str(row.get("scenario_type", "")))].append(row)

    output: list[dict[str, Any]] = []
    for (location, scenario_type), group in sorted(groups.items()):
        counts = ordered_counts([str(row.get("warning_level", "")) for row in group])
        output.append(
            {
                "location": location,
                "scenario_type": scenario_type,
                "scenario_count": len(group),
                "reliable_count": counts["reliable"],
                "caution_count": counts["caution"],
                "high_risk_count": counts["high-risk"],
                "mean_rmse": mean([to_float(row.get("rmse")) for row in group]),
                "mean_mae": mean([to_float(row.get("mae")) for row in group]),
                "mean_wet_dry_iou": mean([to_float(row.get("wet_dry_iou")) for row in group]),
                "mean_false_dry_rate": mean([to_float(row.get("false_dry_rate")) for row in group]),
                "mean_false_wet_rate": mean([to_float(row.get("false_wet_rate")) for row in group]),
                "mean_absolute_relative_volume_bias_proxy": mean(
                    [to_float(row.get("absolute_relative_volume_bias_proxy")) for row in group]
                ),
            }
        )
    return output


def build_rule_table(thresholds: dict[str, float]) -> list[dict[str, Any]]:
    rows = [
        {
            "warning_level": "reliable",
            "warning_action": WARNING_ACTIONS["reliable"],
            "intended_use": "normal diagnostic reporting with standard monitoring",
            "interpretation": "Phase 48 diagnostics did not identify major reliability or physical proxy concerns for the evaluated scenario.",
            "required_review": "standard_monitoring",
            "not_a_probability": "true",
        },
        {
            "warning_level": "caution",
            "warning_action": WARNING_ACTIONS["caution"],
            "intended_use": "use only with diagnostic context and targeted review",
            "interpretation": "One or more diagnostics suggests degraded reliability or a possible warning failure mode.",
            "required_review": "review_failure_drivers_before_unqualified_use",
            "not_a_probability": "true",
        },
        {
            "warning_level": "high-risk",
            "warning_action": WARNING_ACTIONS["high-risk"],
            "intended_use": "screening category requiring case review or supplemental evidence",
            "interpretation": "Conservative diagnostics indicate elevated warning failure risk or physical proxy concern.",
            "required_review": "mandatory_case_review_or_supplemental_evidence",
            "not_a_probability": "true",
        },
    ]
    driver_rules = [
        ("high RMSE", f"rmse >= {thresholds.get('rmse_reliable_max', '')}", "Phase 48 summary threshold"),
        (
            "low wet/dry IoU",
            f"wet_dry_iou <= {thresholds.get('wet_dry_iou_reliable_min', '')}",
            "Phase 48 summary threshold",
        ),
        (
            "elevated false-dry rate",
            f"false_dry_rate >= {thresholds.get('false_dry_reliable_max', '')}",
            "Phase 48 summary threshold",
        ),
        (
            "elevated false-wet rate",
            f"false_wet_rate >= {thresholds.get('false_wet_reliable_max', '')}",
            "Phase 48 summary threshold",
        ),
        (
            "elevated volume-bias proxy",
            "absolute_relative_volume_bias_proxy >= "
            f"{thresholds.get('absolute_relative_volume_bias_reliable_max', '')}",
            "Phase 48 summary threshold",
        ),
        (
            "peak-depth underprediction proxy",
            "peak_depth_underprediction_proxy > 0",
            "Phase 49 transparent post-processing of Phase 48 metric",
        ),
    ]
    for driver, rule, source in driver_rules:
        rows.append(
            {
                "warning_level": f"failure_driver::{driver}",
                "warning_action": "diagnostic_explanation_only",
                "intended_use": source,
                "interpretation": rule,
                "required_review": "review_when_driver_is_listed",
                "not_a_probability": "true",
            }
        )
    return rows


def write_message_templates(path: Path) -> None:
    path.write_text(
        "# Phase 49 Warning Message Templates\n\n"
        "Global disclaimer: warning labels are conservative diagnostic screening labels. "
        "They are not calibrated probabilities, event likelihoods, final production guarantees, "
        "SWE/PINN validation claims, strict conservation claims, or hydrodynamic closure claims.\n\n"
        "## reliable_scenario_message\n\n"
        "Warning category: Reliable\n\n"
        "Recommended action: Normal use with standard monitoring.\n\n"
        "Interpretation: Phase 48 diagnostics did not identify major reliability or physical proxy concerns "
        "for `{scenario}` at `{location}` under the evaluated Phase 47 baseline.\n\n"
        "Limitations: This is a conservative diagnostic label, not a calibrated probability or final production guarantee.\n\n"
        "## caution_scenario_message\n\n"
        "Warning category: Caution\n\n"
        "Recommended action: Use with caution and review diagnostics.\n\n"
        "Interpretation: One or more diagnostics indicate degraded reliability or a potential warning failure mode "
        "for `{scenario}` at `{location}`. Review drivers: `{failure_drivers}`.\n\n"
        "Limitations: This label supports review and contextual interpretation. It is not a calibrated probability "
        "and does not prove model failure.\n\n"
        "## high_risk_scenario_message\n\n"
        "Warning category: High-risk\n\n"
        "Recommended action: Review before relying on the prediction, or supplement with additional evidence.\n\n"
        "Interpretation: Conservative diagnostics indicate elevated risk of warning failure or physical proxy "
        "inconsistency for `{scenario}` at `{location}`. Review drivers: `{failure_drivers}`.\n\n"
        "Limitations: This screening label is intentionally sensitive. It does not by itself prove poor overall "
        "model skill or establish event probability.\n",
        encoding="utf-8",
    )


def suggested_review_focus(drivers: str) -> str:
    focus: list[str] = []
    if "elevated false-dry rate" in drivers:
        focus.append("missed-inundation and target-wet regions")
    if "low wet/dry IoU" in drivers:
        focus.append("wet/dry extent and boundary agreement")
    if "high RMSE" in drivers:
        focus.append("depth-error hotspots")
    if "peak-depth underprediction proxy" in drivers:
        focus.append("local peak-depth underprediction")
    if "elevated false-wet rate" in drivers:
        focus.append("unnecessary wet predictions in target-dry regions")
    if "elevated volume-bias proxy" in drivers:
        focus.append("aggregate volume-response proxy bias")
    return " | ".join(focus) if focus else "general diagnostic review"


def build_high_risk_review_list(rows: list[dict[str, Any]], thresholds: dict[str, float]) -> list[dict[str, Any]]:
    high_risk_rows = [row for row in rows if row.get("warning_level") == "high-risk"]
    review_rows: list[dict[str, Any]] = []
    for row in high_risk_rows:
        score = scenario_priority_score(row, thresholds)
        review_rows.append(
            {
                "priority_rank": 0,
                "priority_score_uncalibrated": f"{score:.6f}",
                "split": row.get("split", ""),
                "location": row.get("location", ""),
                "scenario": row.get("scenario", ""),
                "scenario_type": row.get("scenario_type", ""),
                "warning_level": row.get("warning_level", ""),
                "warning_action": row.get("warning_action", ""),
                "rmse": row.get("rmse", ""),
                "wet_dry_iou": row.get("wet_dry_iou", ""),
                "false_dry_rate": row.get("false_dry_rate", ""),
                "false_wet_rate": row.get("false_wet_rate", ""),
                "absolute_relative_volume_bias_proxy": row.get("absolute_relative_volume_bias_proxy", ""),
                "peak_depth_underprediction_proxy": row.get("peak_depth_underprediction_proxy", ""),
                "top_failure_drivers": row.get("failure_drivers", ""),
                "suggested_review_focus": suggested_review_focus(str(row.get("failure_drivers", ""))),
            }
        )
    review_rows.sort(
        key=lambda row: (
            -to_float(row.get("priority_score_uncalibrated")),
            -to_float(row.get("false_dry_rate")),
            to_float(row.get("wet_dry_iou"), 1.0),
            -to_float(row.get("rmse")),
            -to_float(row.get("peak_depth_underprediction_proxy")),
            -to_float(row.get("absolute_relative_volume_bias_proxy")),
            str(row.get("location", "")),
            str(row.get("scenario", "")),
        )
    )
    for index, row in enumerate(review_rows, start=1):
        row["priority_rank"] = index
    return review_rows


def build_markdown_summary(summary: dict[str, Any], thresholds: dict[str, float]) -> str:
    counts = summary["warning_level_counts"]
    return (
        "# Phase 49 Full-Dataset Warning Framework Summary\n\n"
        f"Selected decision: `{summary['selected_decision']}`.\n\n"
        "Phase 49 converted fixed Phase 48 full-dataset reliability and physical proxy diagnostics "
        "into a conservative warning framework for the Phase 47 128x128 full-dataset baseline. "
        "No training, seed sweep, hyperparameter sweep, loss redesign, model modification, SWE residual, "
        "or PINN component was run or introduced.\n\n"
        "## Scenario Counts\n\n"
        f"- Input files found: `{str(summary['input_files_found']).lower()}`\n"
        f"- Scenario count: `{summary['scenario_count']}`\n"
        f"- Reliable: `{counts.get('reliable', 0)}`\n"
        f"- Caution: `{counts.get('caution', 0)}`\n"
        f"- High-risk: `{counts.get('high-risk', 0)}`\n"
        f"- High-risk review cases: `{summary['high_risk_case_count']}`\n\n"
        "## Interpretation\n\n"
        f"{INTERPRETATION_NOTE} High-risk is intentionally sensitive and does not by itself prove poor "
        "overall model skill. Phase 49 does not claim Level 5 support, strict conservation, full mass "
        "conservation, hydrodynamic closure, or final production readiness.\n\n"
        "## Failure-Driver Rules\n\n"
        "Failure drivers use Phase 48 summary thresholds where available. The key thresholds are:\n\n"
        f"- RMSE driver threshold: `{thresholds.get('rmse_reliable_max', '')}`\n"
        f"- Wet/dry IoU driver threshold: `{thresholds.get('wet_dry_iou_reliable_min', '')}`\n"
        f"- False-dry driver threshold: `{thresholds.get('false_dry_reliable_max', '')}`\n"
        f"- False-wet driver threshold: `{thresholds.get('false_wet_reliable_max', '')}`\n"
        "- Volume-bias proxy driver threshold: "
        f"`{thresholds.get('absolute_relative_volume_bias_reliable_max', '')}`\n"
        "- Peak-depth underprediction proxy driver threshold: `> 0`\n\n"
        f"Next recommended action: {summary['next_recommended_action']}\n"
    )


def main() -> None:
    args = parse_args()
    input_dir = repo_path(args.input_dir)
    output_dir = repo_path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    input_paths, missing_inputs = check_inputs(input_dir)
    if missing_inputs:
        write_blocked_outputs(output_dir, input_dir, missing_inputs)
        print("input_files_found: false")
        print("scenario_count: 0")
        print("warning_level_counts: {}")
        print(f"selected_decision: {DECISION_BLOCKED}")
        print("high_risk_case_count: 0")
        print("no_training: true")
        print("warning_labels_are_probabilities: false")
        return

    phase48_summary = read_json(input_paths["phase48_reliability_summary_json"])
    thresholds = thresholds_from_summary(phase48_summary)

    scenario_rows = read_csv_rows(input_paths["scenario_reliability_metrics"])
    warning_rows = read_csv_rows(input_paths["reliability_warning_levels"])
    validate_labels_preserved(scenario_rows, warning_rows)

    merged_rows = merge_metric_rows(scenario_rows, read_csv_rows(input_paths["wet_dry_error_metrics"]))
    merged_rows = merge_metric_rows(merged_rows, read_csv_rows(input_paths["peak_depth_timing_metrics"]))
    merged_rows = merge_metric_rows(merged_rows, read_csv_rows(input_paths["volume_response_proxy_metrics"]))

    scenario_framework_rows = build_scenario_framework(merged_rows, thresholds)
    location_type_rows = build_location_type_summary(scenario_framework_rows)
    rule_rows = build_rule_table(thresholds)
    high_risk_rows = build_high_risk_review_list(scenario_framework_rows, thresholds)

    scenario_fieldnames = [
        "split",
        "location",
        "scenario",
        "scenario_type",
        "warning_level",
        "warning_action",
        "rmse",
        "mae",
        "wet_dry_iou",
        "false_dry_rate",
        "false_wet_rate",
        "relative_volume_bias_proxy",
        "absolute_relative_volume_bias_proxy",
        "peak_depth_underprediction_proxy",
        "failure_drivers",
        "user_message_key",
        "interpretation_note",
    ]
    location_fieldnames = [
        "location",
        "scenario_type",
        "scenario_count",
        "reliable_count",
        "caution_count",
        "high_risk_count",
        "mean_rmse",
        "mean_mae",
        "mean_wet_dry_iou",
        "mean_false_dry_rate",
        "mean_false_wet_rate",
        "mean_absolute_relative_volume_bias_proxy",
    ]
    rule_fieldnames = [
        "warning_level",
        "warning_action",
        "intended_use",
        "interpretation",
        "required_review",
        "not_a_probability",
    ]
    high_risk_fieldnames = [
        "priority_rank",
        "priority_score_uncalibrated",
        "split",
        "location",
        "scenario",
        "scenario_type",
        "warning_level",
        "warning_action",
        "rmse",
        "wet_dry_iou",
        "false_dry_rate",
        "false_wet_rate",
        "absolute_relative_volume_bias_proxy",
        "peak_depth_underprediction_proxy",
        "top_failure_drivers",
        "suggested_review_focus",
    ]

    write_csv_rows(output_dir / "scenario_warning_framework.csv", scenario_framework_rows, scenario_fieldnames)
    write_csv_rows(output_dir / "location_type_warning_summary.csv", location_type_rows, location_fieldnames)
    write_csv_rows(output_dir / "warning_rule_table.csv", rule_rows, rule_fieldnames)
    write_message_templates(output_dir / "warning_message_templates.md")
    write_csv_rows(output_dir / "high_risk_case_review_list.csv", high_risk_rows, high_risk_fieldnames)

    warning_level_counts = ordered_counts([str(row.get("warning_level", "")) for row in scenario_framework_rows])
    selected_decision = DECISION_COMPLETED
    next_action = (
        "Use Phase 49 outputs for conservative case reporting and diagnostic screening, with manual review "
        "for high-risk cases and no probability interpretation."
    )
    now = datetime.now(timezone.utc).isoformat()
    summary = {
        "created_utc": now,
        "phase": 49,
        "selected_decision": selected_decision,
        "input_files_found": True,
        "input_files": {key: display_path(path) for key, path in input_paths.items()},
        "scenario_count": len(scenario_framework_rows),
        "warning_level_counts": warning_level_counts,
        "location_type_rows": len(location_type_rows),
        "high_risk_case_count": len(high_risk_rows),
        "no_training": True,
        "no_swe_pinn": True,
        "level5_supported": False,
        "warning_labels_are_probabilities": False,
        "phase48_labels_preserved": True,
        "phase47_final_production_model_claimed": False,
        "strict_conservation_claimed": False,
        "hydrodynamic_closure_claimed": False,
        "swe_residual_used": False,
        "pinn_used": False,
        "next_recommended_action": next_action,
        "source_phase48_decision": phase48_summary.get("selected_decision", ""),
        "source_phase48_warning_level_counts": phase48_summary.get("warning_level_counts", {}),
        "failure_driver_thresholds": thresholds,
        "outputs": {
            "warning_framework_summary_json": display_path(output_dir / "warning_framework_summary.json"),
            "warning_framework_summary_md": display_path(output_dir / "warning_framework_summary.md"),
            "scenario_warning_framework_csv": display_path(output_dir / "scenario_warning_framework.csv"),
            "location_type_warning_summary_csv": display_path(output_dir / "location_type_warning_summary.csv"),
            "warning_rule_table_csv": display_path(output_dir / "warning_rule_table.csv"),
            "warning_message_templates_md": display_path(output_dir / "warning_message_templates.md"),
            "high_risk_case_review_list_csv": display_path(output_dir / "high_risk_case_review_list.csv"),
            "phase49_warning_framework_decision_json": display_path(
                output_dir / "phase49_warning_framework_decision.json"
            ),
        },
    }
    decision = {
        "created_utc": now,
        "phase": 49,
        "selected_decision": selected_decision,
        "decision_candidates": [
            "phase49_warning_framework_ready_for_case_reporting",
            DECISION_COMPLETED,
            DECISION_BLOCKED,
            "phase49_warning_framework_deferred",
        ],
        "decision_rationale": (
            "Required Phase 48 inputs were present, labels were preserved, warning actions and diagnostic "
            "failure drivers were generated, and outputs remain conservative no-training screening artifacts."
        ),
        "input_files_found": True,
        "scenario_count": len(scenario_framework_rows),
        "warning_level_counts": warning_level_counts,
        "high_risk_case_count": len(high_risk_rows),
        "no_training": True,
        "no_swe_pinn": True,
        "level5_supported": False,
        "warning_labels_are_probabilities": False,
        "next_recommended_action": next_action,
    }

    write_json(output_dir / "warning_framework_summary.json", summary)
    write_json(output_dir / "phase49_warning_framework_decision.json", decision)
    (output_dir / "warning_framework_summary.md").write_text(
        build_markdown_summary(summary, thresholds),
        encoding="utf-8",
    )

    print("input_files_found: true")
    print(f"scenario_count: {len(scenario_framework_rows)}")
    print(f"warning_level_counts: {warning_level_counts}")
    print(f"selected_decision: {selected_decision}")
    print(f"high_risk_case_count: {len(high_risk_rows)}")
    print("no_training: true")
    print("warning_labels_are_probabilities: false")


if __name__ == "__main__":
    main()
