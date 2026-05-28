from __future__ import annotations

import argparse
import csv
import json
import math
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PHASE38_DIR = Path("analysis/phase38_seed42_pilot_training_guardrail_evaluation")
DEFAULT_EVALUATION_DIR = Path("runs/phase36_manhole_false_dry_guardrail_seed42_40e/evaluation_test")
DEFAULT_PHASE34_DIR = Path("analysis/phase34_pilot_thresholds")
DEFAULT_PHASE31_DIR = Path("analysis/phase31_physics_input_recovery_readiness")
DEFAULT_OUTPUT_DIR = Path("analysis/phase39_failed_pilot_tradeoff_diagnosis")

FAILED_AT_IDS = {"AT02", "AT03", "AT04", "AT06", "AT07", "AT08", "AT09", "AT10"}
TRIGGERED_RT_IDS = {"RT01", "RT05", "RT07"}
REGIONS = (
    "valid_domain",
    "manhole_nonzero_valid",
    "high_impervious_valid",
    "boundary_ring",
    "all_evaluated_cells",
)
FOCUS_METRICS = (
    ("standard", "rmse", "all_evaluated_cells"),
    ("standard", "mae", "all_evaluated_cells"),
    ("standard", "wet_dry_iou", "all_evaluated_cells"),
    ("standard", "rollout_stability", "all_evaluated_cells"),
    ("standard", "step_rmse_std", "all_evaluated_cells"),
    ("valid_domain_masked", "rmse", "valid_domain"),
    ("valid_domain_masked", "mae", "valid_domain"),
    ("valid_domain_masked", "false_dry_rate", "valid_domain"),
    ("valid_domain_masked", "false_wet_rate", "valid_domain"),
    ("valid_domain_masked", "absolute_relative_volume_bias_proxy", "valid_domain"),
    ("manhole_nonzero_target", "false_dry_rate", "manhole_nonzero_valid"),
    ("guardrail_masked", "false_wet_rate", "high_impervious_valid"),
    ("guardrail_masked", "false_dry_rate", "boundary_ring"),
)
LOWER_IS_BETTER = {
    "rmse",
    "mae",
    "step_rmse_std",
    "false_dry_rate",
    "false_wet_rate",
    "absolute_relative_volume_bias_proxy",
}
HIGHER_IS_BETTER = {"wet_dry_iou", "rollout_stability"}
WET_THRESHOLD = 0.05


def repo_path(path: Path) -> Path:
    path = path.expanduser()
    if path.is_absolute():
        return path
    return (REPO_ROOT / path).resolve()


def display_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT)).replace("\\", "/")
    except ValueError:
        return str(path)


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def safe_float(value: Any) -> float | None:
    if value in (None, ""):
        return None
    try:
        number = float(value)
    except (TypeError, ValueError, OverflowError):
        return None
    if math.isnan(number) or math.isinf(number):
        return None
    return number


def fmt(value: Any) -> str:
    number = safe_float(value)
    if number is None:
        return "" if value in (None, "") else str(value)
    return f"{number:.12g}"


def write_csv(path: Path, rows: list[dict[str, Any]], columns: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({column: fmt(row.get(column)) for column in columns})


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def metric_direction(metric_name: str, fallback: str = "") -> str:
    if metric_name in LOWER_IS_BETTER:
        return "lower_is_better"
    if metric_name in HIGHER_IS_BETTER:
        return "higher_is_better"
    if fallback in {"lower_is_better", "higher_is_better"}:
        return fallback
    return "context_dependent"


def worsened(candidate: float | None, baseline: float | None, direction: str) -> bool | None:
    if candidate is None or baseline is None:
        return None
    if direction == "lower_is_better":
        return candidate > baseline
    if direction == "higher_is_better":
        return candidate < baseline
    return None


def improved(candidate: float | None, baseline: float | None, direction: str) -> bool | None:
    if candidate is None or baseline is None:
        return None
    if direction == "lower_is_better":
        return candidate < baseline
    if direction == "higher_is_better":
        return candidate > baseline
    return None


def delta_to_threshold(observed: float | None, threshold: float | None, direction: str) -> float | None:
    if observed is None or threshold is None:
        return None
    if direction == "lower_or_equal":
        return observed - threshold
    if direction == "higher_or_equal":
        return threshold - observed
    return None


def acceptance_interpretation(row: dict[str, str]) -> str:
    at_id = row.get("threshold_id", "")
    interpretations = {
        "AT02": "Valid-domain RMSE exceeded the Phase 27 plus tolerance guardrail, indicating broader depth-error degradation.",
        "AT03": "Valid-domain MAE exceeded the Phase 27 plus tolerance guardrail, so aggregate valid-cell error worsened.",
        "AT04": "Valid-domain false-dry rate exceeded the Phase 27 guardrail, repeating the dry-miss concern outside the target-only view.",
        "AT06": "High-impervious valid false-wet rate exceeded its regional tolerance, indicating the pilot introduced wet overprediction in a guardrail region.",
        "AT07": "Boundary-ring false-dry rate exceeded its tolerance, consistent with a boundary-sensitive trade-off rather than a clean target improvement.",
        "AT08": "Standard RMSE failed the global quality guardrail.",
        "AT09": "Standard MAE failed the global quality guardrail.",
        "AT10": "Standard wet/dry IoU fell below the required floor, indicating wet/dry classification quality was not maintained.",
    }
    return interpretations.get(at_id, "Failed required Phase 34 acceptance component.")


def rejection_interpretation(row: dict[str, str]) -> str:
    rt_id = row.get("rejection_id", "")
    interpretations = {
        "RT01": "The result matches the Phase 29-like pattern: valid-domain volume-bias proxy improves while multiple error metrics worsen versus Phase 27.",
        "RT05": "At least one standard global error metric exceeded the hard rejection tolerance, so the pilot cannot be treated as a localized-only change.",
        "RT07": "Valid-domain RMSE or MAE exceeded the acceptance tolerance, blocking expansion despite target-region improvement.",
    }
    return interpretations.get(rt_id, "Triggered Phase 34 rejection rule.")


def build_failed_acceptance(rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for row in rows:
        if row.get("threshold_id") not in FAILED_AT_IDS or row.get("status") != "fail":
            continue
        observed = safe_float(row.get("observed_value"))
        threshold = safe_float(row.get("numeric_threshold"))
        direction = row.get("direction", "")
        output.append(
            {
                "acceptance_id": row.get("threshold_id"),
                "metric_group": row.get("metric_group"),
                "metric_name": row.get("metric_name"),
                "region": row.get("region"),
                "observed": observed,
                "threshold": threshold,
                "direction": direction,
                "delta_to_threshold": delta_to_threshold(observed, threshold, direction),
                "status": row.get("status"),
                "diagnostic_interpretation": acceptance_interpretation(row),
            }
        )
    return output


def build_triggered_rejections(rows: list[dict[str, str]], phase34_rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    phase34_by_id = {row.get("rejection_id"): row for row in phase34_rows}
    output: list[dict[str, Any]] = []
    for row in rows:
        triggered = row.get("status") == "triggered" or row.get("triggered") == "True"
        if row.get("rejection_id") not in TRIGGERED_RT_IDS or not triggered:
            continue
        threshold_row = phase34_by_id.get(row.get("rejection_id"), {})
        output.append(
            {
                "rejection_id": row.get("rejection_id"),
                "rule": row.get("rejection_rule"),
                "status": row.get("status"),
                "trigger_metric_group": threshold_row.get("trigger_metric_group", ""),
                "trigger_metric_name": threshold_row.get("trigger_metric_name", ""),
                "trigger_region": threshold_row.get("trigger_region", ""),
                "observed": row.get("notes", ""),
                "threshold_or_condition": threshold_row.get("trigger_condition") or row.get("notes", ""),
                "diagnostic_interpretation": rejection_interpretation(row),
            }
        )
    return output


def standard_metric_index(metrics_path: Path) -> dict[tuple[str, str, str], float]:
    if not metrics_path.exists():
        return {}
    metrics = read_json(metrics_path)
    return {
        ("standard", key, "all_evaluated_cells"): value
        for key, value in metrics.items()
        if safe_float(value) is not None
    }


def phase38_metric_index(
    acceptance_rows: list[dict[str, str]],
    decision: dict[str, Any],
    metrics_path: Path,
) -> dict[tuple[str, str, str], float]:
    index = standard_metric_index(metrics_path)
    for row in acceptance_rows:
        value = safe_float(row.get("observed_value"))
        if value is None:
            continue
        index[(row["metric_group"], row["metric_name"], row["region"])] = value

    for row in decision.get("masked_metric_rows", []):
        if not isinstance(row, dict):
            continue
        region = str(row.get("region", ""))
        if region == "valid_domain":
            group = "valid_domain_masked"
        elif region == "manhole_nonzero_valid":
            group = "manhole_nonzero_target"
        elif region in {"boundary_ring", "high_impervious_valid"}:
            group = "guardrail_masked"
        else:
            group = "masked"
        for metric_name, value in row.items():
            number = safe_float(value)
            if number is not None:
                index[(group, metric_name, region)] = number
    return index


def baseline_index(rows: list[dict[str, str]]) -> dict[tuple[str, str, str], dict[str, Any]]:
    output: dict[tuple[str, str, str], dict[str, Any]] = {}
    for row in rows:
        key = (row["metric_group"], row["metric_name"], row["region"])
        output[key] = {
            "phase25_seed42": safe_float(row.get("phase25_seed42")),
            "phase27_seed42": safe_float(row.get("phase27_seed42")),
            "phase29_seed42": safe_float(row.get("phase29_seed42")),
            "preferred_direction": row.get("preferred_direction", metric_direction(row["metric_name"])),
            "notes": row.get("notes", ""),
        }
    return output


def tradeoff_flag(
    key: tuple[str, str, str],
    phase38: float | None,
    base: dict[str, Any],
    failed_keys: set[tuple[str, str, str]],
) -> str:
    direction = metric_direction(key[1], str(base.get("preferred_direction", "")))
    if phase38 is None:
        return "phase38_missing"
    if key in failed_keys:
        return "failed_acceptance_component"
    if key == ("manhole_nonzero_target", "false_dry_rate", "manhole_nonzero_valid"):
        p27_improved = improved(phase38, base.get("phase27_seed42"), direction)
        p29_improved = improved(phase38, base.get("phase29_seed42"), direction)
        if p27_improved and p29_improved:
            return "target_metric_improved_vs_phase27_and_phase29"
    if worsened(phase38, base.get("phase27_seed42"), direction):
        return "worsened_vs_phase27"
    if worsened(phase38, base.get("phase29_seed42"), direction):
        return "worsened_vs_phase29"
    if improved(phase38, base.get("phase27_seed42"), direction):
        return "improved_vs_phase27"
    return "available_no_adverse_flag"


def build_baseline_comparison(
    baselines: dict[tuple[str, str, str], dict[str, Any]],
    phase38: dict[tuple[str, str, str], float],
    failed_acceptance: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    failed_keys = {
        (row["metric_group"], row["metric_name"], row["region"])
        for row in failed_acceptance
    }
    rows: list[dict[str, Any]] = []
    for key in FOCUS_METRICS:
        base = baselines.get(key, {})
        value = phase38.get(key)
        direction = metric_direction(key[1], str(base.get("preferred_direction", "")))
        rows.append(
            {
                "metric_group": key[0],
                "metric_name": key[1],
                "region": key[2],
                "phase25_seed42": base.get("phase25_seed42"),
                "phase27_seed42": base.get("phase27_seed42"),
                "phase29_seed42": base.get("phase29_seed42"),
                "phase38_seed42": value,
                "preferred_direction": direction,
                "phase38_minus_phase25": None if value is None or base.get("phase25_seed42") is None else value - base["phase25_seed42"],
                "phase38_minus_phase27": None if value is None or base.get("phase27_seed42") is None else value - base["phase27_seed42"],
                "phase38_minus_phase29": None if value is None or base.get("phase29_seed42") is None else value - base["phase29_seed42"],
                "tradeoff_flag": tradeoff_flag(key, value, base, failed_keys),
                "notes": base.get("notes", "baseline row unavailable"),
            }
        )
    return rows


def metric_values_for_region(region: str, comparison_rows: list[dict[str, Any]]) -> str:
    entries = []
    for row in comparison_rows:
        if row["region"] == region and row.get("phase38_seed42") is not None:
            entries.append(f"{row['metric_group']}/{row['metric_name']}={fmt(row['phase38_seed42'])}")
    return "; ".join(entries) if entries else "no Phase38 metric values available in requested focus set"


def region_conclusion(region: str, failed: list[str], worsened_vs_27: bool, target_improved: bool) -> str:
    if region == "manhole_nonzero_valid" and target_improved:
        return "Target-region false-dry improved, but this did not overcome broader Level 4+ guardrail failures."
    if failed and worsened_vs_27:
        return "Region contributes to the broader degradation diagnosis."
    if failed:
        return "Region has failed acceptance evidence but baseline worsening evidence is incomplete or mixed."
    if region == "all_evaluated_cells" and worsened_vs_27:
        return "Global standard metrics worsened relative to Phase 27, supporting rejection rather than expansion."
    return "No failed acceptance component identified for this region in the requested diagnostics."


def build_region_summary(
    comparison_rows: list[dict[str, Any]],
    failed_acceptance: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for region in REGIONS:
        failed = [
            f"{row['acceptance_id']}:{row['metric_group']}/{row['metric_name']}"
            for row in failed_acceptance
            if row["region"] == region
        ]
        region_rows = [row for row in comparison_rows if row["region"] == region]
        worsened_vs_27 = any(row["tradeoff_flag"] in {"failed_acceptance_component", "worsened_vs_phase27"} for row in region_rows)
        worsened_vs_29 = any(row["tradeoff_flag"] == "worsened_vs_phase29" for row in region_rows)
        target_improved = any(row["tradeoff_flag"] == "target_metric_improved_vs_phase27_and_phase29" for row in region_rows)
        supports = (
            "yes" if (target_improved or failed or worsened_vs_27 or worsened_vs_29) else "not_from_available_rows"
        )
        rows.append(
            {
                "region": region,
                "available_failed_checks": "; ".join(failed) if failed else "none",
                "available_phase38_metric_values": metric_values_for_region(region, comparison_rows),
                "worsened_relative_to_phase27": "yes" if worsened_vs_27 else "no_or_unavailable",
                "worsened_relative_to_phase29": "yes" if worsened_vs_29 else "no_or_unavailable",
                "supports_localized_target_improvement_vs_broader_degradation": supports,
                "diagnostic_conclusion": region_conclusion(region, failed, worsened_vs_27, target_improved),
            }
        )
    return rows


def normalize_forecast(arr: np.ndarray) -> np.ndarray:
    arr = np.asarray(arr, dtype=np.float64)
    if arr.ndim == 5:
        return arr
    if arr.ndim == 4:
        return arr[:, :, np.newaxis, :, :]
    if arr.ndim == 3:
        return arr[np.newaxis, :, np.newaxis, :, :]
    if arr.ndim == 2:
        return arr[np.newaxis, np.newaxis, np.newaxis, :, :]
    raise ValueError(f"unsupported forecast shape {arr.shape}")


def batch_metrics(forecast_path: Path) -> dict[str, Any]:
    with np.load(forecast_path, allow_pickle=False) as data:
        prediction = normalize_forecast(data["prediction"])
        target = normalize_forecast(data["target"])
    if prediction.shape != target.shape:
        raise ValueError(f"prediction shape {prediction.shape} != target shape {target.shape}")

    diff = prediction - target
    pred_wet = prediction > WET_THRESHOLD
    target_wet = target > WET_THRESHOLD
    intersection = np.logical_and(pred_wet, target_wet).sum()
    union = np.logical_or(pred_wet, target_wet).sum()
    false_dry = np.logical_and(target_wet, ~pred_wet).sum()
    false_wet = np.logical_and(~target_wet, pred_wet).sum()
    target_wet_count = target_wet.sum()
    target_dry_count = (~target_wet).sum()
    return {
        "scenario_or_batch": forecast_path.parent.name,
        "rmse": math.sqrt(float(np.mean(diff * diff))),
        "mae": float(np.mean(np.abs(diff))),
        "wet_dry_iou": float(intersection / union) if union else None,
        "false_dry_rate": float(false_dry / target_wet_count) if target_wet_count else None,
        "false_wet_rate": float(false_wet / target_dry_count) if target_dry_count else None,
        "sample_count": int(prediction.shape[0]),
        "timestep_count": int(prediction.shape[1]),
        "limitation_note": "Phase38 per-batch aggregate only; no per-batch Phase25/Phase27/Phase29 baseline available.",
    }


def build_scenario_summary(evaluation_dir: Path) -> list[dict[str, Any]]:
    forecast_paths = sorted(evaluation_dir.glob("test_batch_*/forecast_maps.npz"))
    rows: list[dict[str, Any]] = []
    if not forecast_paths:
        return [
            {
                "scenario_or_batch": "not_available",
                "rmse": None,
                "mae": None,
                "wet_dry_iou": None,
                "false_dry_rate": None,
                "false_wet_rate": None,
                "sample_count": None,
                "timestep_count": None,
                "limitation_note": "No forecast_maps.npz files available; scenario claims are not made.",
            }
        ]
    for path in forecast_paths:
        try:
            rows.append(batch_metrics(path))
        except (OSError, KeyError, ValueError, zipfile.BadZipFile) as exc:
            rows.append(
                {
                    "scenario_or_batch": path.parent.name,
                    "rmse": None,
                    "mae": None,
                    "wet_dry_iou": None,
                    "false_dry_rate": None,
                    "false_wet_rate": None,
                    "sample_count": None,
                    "timestep_count": None,
                    "limitation_note": f"Could not read existing forecast map safely: {exc}",
                }
            )
    return rows


def write_markdown(path: Path, payload: dict[str, Any]) -> None:
    lines = [
        "# Phase 39 Failed Pilot Trade-Off Diagnosis",
        "",
        "This is a diagnostic-only Level 4+ proxy summary. It does not train, sweep, change thresholds, modify losses/configs/model architecture, or claim strict conservation, full mass conservation, SWE/PINN behavior, hydrodynamic closure, or Level 5 support.",
        "",
        "## Decision",
        "",
        f"- final_decision: `{payload['final_decision']}`",
        f"- phase39_decision: `{payload['phase39_decision']}`",
        f"- failed_acceptance_count: `{payload['failed_acceptance_count']}`",
        f"- triggered_rejection_count: `{payload['triggered_rejection_count']}`",
        "",
        "## Key Diagnosis",
        "",
        "- RT01 indicates a Phase29-like trade-off pattern.",
        "- The current manhole_nonzero_false_dry_guardrail did not pass broader Level 4+ guardrails.",
        "- The result should not be expanded to seed123/seed202 or rescued by sweep/post-hoc edits.",
        "- Next recommended step: failed-pilot diagnosis / design review, not training.",
        "",
        "## Failed Acceptance Components",
        "",
    ]
    for row in payload["failed_acceptance_components"]:
        lines.append(
            f"- `{row['acceptance_id']}` `{row['metric_group']}/{row['metric_name']}/{row['region']}`: "
            f"observed `{fmt(row['observed'])}` vs threshold `{fmt(row['threshold'])}`. "
            f"{row['diagnostic_interpretation']}"
        )
    lines.extend(["", "## Triggered Rejection Rules", ""])
    for row in payload["triggered_rejection_rules"]:
        lines.append(f"- `{row['rejection_id']}` `{row['rule']}`: {row['diagnostic_interpretation']}")
    lines.extend(["", "## Missing Optional Inputs", ""])
    if payload["missing_optional_inputs"]:
        for item in payload["missing_optional_inputs"]:
            lines.append(f"- {item}")
    else:
        lines.append("- None recorded.")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def required_inputs(args: argparse.Namespace) -> dict[str, Path]:
    phase38_dir = repo_path(args.phase38_dir)
    phase34_dir = repo_path(args.phase34_dir)
    return {
        "phase38_standard_metric_check": phase38_dir / "phase38_standard_metric_check.csv",
        "phase38_acceptance_check": phase38_dir / "phase38_acceptance_check.csv",
        "phase38_rejection_check": phase38_dir / "phase38_rejection_check.csv",
        "phase38_guardrail_decision_json": phase38_dir / "phase38_guardrail_decision.json",
        "phase38_guardrail_decision_md": phase38_dir / "phase38_guardrail_decision.md",
        "evaluation_dir": repo_path(args.evaluation_dir),
        "phase34_baseline_metric_table": phase34_dir / "baseline_metric_table.csv",
        "phase34_acceptance_thresholds": phase34_dir / "acceptance_thresholds.csv",
        "phase34_rejection_thresholds": phase34_dir / "rejection_thresholds.csv",
        "phase34_threshold_summary": phase34_dir / "phase34_threshold_summary.json",
        "phase31_dir": repo_path(args.phase31_dir),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Diagnose the rejected Phase 38 seed42 pilot using existing artifacts only. "
            "This script does not train, modify losses/configs/model architecture, run "
            "seed123/seed202, sweep, or rescue Phase 38 post hoc."
        )
    )
    parser.add_argument("--phase38-dir", type=Path, default=DEFAULT_PHASE38_DIR)
    parser.add_argument("--evaluation-dir", type=Path, default=DEFAULT_EVALUATION_DIR)
    parser.add_argument("--phase34-dir", type=Path, default=DEFAULT_PHASE34_DIR)
    parser.add_argument("--phase31-dir", type=Path, default=DEFAULT_PHASE31_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    paths = required_inputs(args)
    missing_required = [display_path(path) for path in paths.values() if not path.exists()]
    if missing_required:
        raise FileNotFoundError("Missing required Phase 39 input(s): " + ", ".join(missing_required))

    output_dir = repo_path(args.output_dir)
    phase38_acceptance = read_csv_rows(paths["phase38_acceptance_check"])
    phase38_rejection = read_csv_rows(paths["phase38_rejection_check"])
    phase34_rejection = read_csv_rows(paths["phase34_rejection_thresholds"])
    baseline_rows = read_csv_rows(paths["phase34_baseline_metric_table"])
    decision = read_json(paths["phase38_guardrail_decision_json"])

    metrics_path = paths["evaluation_dir"] / "metrics.json"
    failed_acceptance = build_failed_acceptance(phase38_acceptance)
    triggered_rejections = build_triggered_rejections(phase38_rejection, phase34_rejection)
    baselines = baseline_index(baseline_rows)
    phase38_metrics = phase38_metric_index(phase38_acceptance, decision, metrics_path)
    comparison = build_baseline_comparison(baselines, phase38_metrics, failed_acceptance)
    region_summary = build_region_summary(comparison, failed_acceptance)
    scenario_summary = build_scenario_summary(paths["evaluation_dir"])

    missing_optional = []
    for row in comparison:
        missing = [
            column
            for column in ("phase25_seed42", "phase27_seed42", "phase29_seed42", "phase38_seed42")
            if row.get(column) is None
        ]
        if missing:
            missing_optional.append(
                f"{row['metric_group']}/{row['metric_name']}/{row['region']}: missing {', '.join(missing)}"
            )
    if all("no per-batch Phase25/Phase27/Phase29 baseline" in row.get("limitation_note", "") for row in scenario_summary):
        missing_optional.append("Per-batch/scenario Phase25/Phase27/Phase29 baselines are unavailable; scenario summary is Phase38-only.")

    phase39_decision = (
        "tradeoff_diagnosis_completed_with_missing_optional_inputs"
        if missing_optional
        else "tradeoff_diagnosis_completed"
    )
    summary = {
        "phase": 39,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "script": "scripts/diagnose_phase39_failed_pilot_tradeoffs.py",
        "final_decision": "seed42_pilot_rejected",
        "phase38_recorded_final_decision": decision.get("final_decision"),
        "phase39_decision": phase39_decision,
        "failed_acceptance_count": len(failed_acceptance),
        "triggered_rejection_count": len(triggered_rejections),
        "comparison_rows": len(comparison),
        "region_rows": len(region_summary),
        "scenario_rows": len(scenario_summary),
        "key_diagnosis": {
            "rt01": "RT01 indicates a Phase29-like trade-off pattern.",
            "guardrail_result": "The current manhole_nonzero_false_dry_guardrail did not pass broader Level 4+ guardrails.",
            "do_not_expand_or_rescue": "The result should not be expanded to seed123/seed202 or rescued by sweep/post-hoc edits.",
        },
        "next_recommended_step": "failed-pilot diagnosis / design review, not training",
        "guardrails": {
            "no_training": True,
            "no_seed42_training_again": True,
            "no_seed123": True,
            "no_seed202": True,
            "no_sweep": True,
            "no_loss_modification": True,
            "no_config_modification": True,
            "no_threshold_changes": True,
            "no_phase38_relabel": True,
            "level4_plus_proxy_scope_only": True,
        },
        "missing_optional_inputs": missing_optional,
        "failed_acceptance_components": failed_acceptance,
        "triggered_rejection_rules": triggered_rejections,
        "input_sources": {name: display_path(path) for name, path in paths.items()},
    }

    write_csv(
        output_dir / "failed_acceptance_components.csv",
        failed_acceptance,
        [
            "acceptance_id",
            "metric_group",
            "metric_name",
            "region",
            "observed",
            "threshold",
            "direction",
            "delta_to_threshold",
            "status",
            "diagnostic_interpretation",
        ],
    )
    write_csv(
        output_dir / "triggered_rejection_rules.csv",
        triggered_rejections,
        [
            "rejection_id",
            "rule",
            "status",
            "trigger_metric_group",
            "trigger_metric_name",
            "trigger_region",
            "observed",
            "threshold_or_condition",
            "diagnostic_interpretation",
        ],
    )
    write_csv(
        output_dir / "phase38_vs_baselines_metric_comparison.csv",
        comparison,
        [
            "metric_group",
            "metric_name",
            "region",
            "phase25_seed42",
            "phase27_seed42",
            "phase29_seed42",
            "phase38_seed42",
            "preferred_direction",
            "phase38_minus_phase25",
            "phase38_minus_phase27",
            "phase38_minus_phase29",
            "tradeoff_flag",
            "notes",
        ],
    )
    write_csv(
        output_dir / "region_tradeoff_summary.csv",
        region_summary,
        [
            "region",
            "available_failed_checks",
            "available_phase38_metric_values",
            "worsened_relative_to_phase27",
            "worsened_relative_to_phase29",
            "supports_localized_target_improvement_vs_broader_degradation",
            "diagnostic_conclusion",
        ],
    )
    write_csv(
        output_dir / "scenario_tradeoff_summary.csv",
        scenario_summary,
        [
            "scenario_or_batch",
            "rmse",
            "mae",
            "wet_dry_iou",
            "false_dry_rate",
            "false_wet_rate",
            "sample_count",
            "timestep_count",
            "limitation_note",
        ],
    )
    write_json(output_dir / "phase39_tradeoff_diagnosis_summary.json", summary)
    write_markdown(output_dir / "phase39_tradeoff_diagnosis_summary.md", summary)

    print(f"failed_acceptance_count={len(failed_acceptance)}")
    print(f"triggered_rejection_count={len(triggered_rejections)}")
    print(f"comparison_rows={len(comparison)}")
    print(f"region_rows={len(region_summary)}")
    print(f"scenario_rows={len(scenario_summary)}")
    print(f"phase39_decision={phase39_decision}")


if __name__ == "__main__":
    main()
