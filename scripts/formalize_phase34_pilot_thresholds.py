from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = Path("analysis/phase34_pilot_thresholds")

INPUTS = {
    "phase34_plan": Path("docs/phase34_pilot_threshold_formalization_plan.md"),
    "phase31_by_phase": Path(
        "analysis/phase31_physics_input_recovery_readiness/"
        "masked_physical_error_by_phase.csv"
    ),
    "phase31_by_region": Path(
        "analysis/phase31_physics_input_recovery_readiness/"
        "masked_physical_error_by_region.csv"
    ),
    "phase31_delta": Path(
        "analysis/phase31_physics_input_recovery_readiness/"
        "masked_physical_error_delta_phase29_vs_phase27.csv"
    ),
    "phase31_summary": Path(
        "analysis/phase31_physics_input_recovery_readiness/"
        "masked_physical_error_summary.json"
    ),
    "phase32_guardrails": Path(
        "analysis/phase32_domain_boundary_aware_design/guardrail_metrics.csv"
    ),
    "phase32_stop_go": Path(
        "analysis/phase32_domain_boundary_aware_design/stop_go_criteria.csv"
    ),
    "phase33_summary": Path(
        "analysis/phase33_seed42_pilot_readiness/phase33_readiness_summary.json"
    ),
    "phase33_readiness": Path(
        "analysis/phase33_seed42_pilot_readiness/readiness_criteria_status.csv"
    ),
    "phase25_standard": Path(
        "runs/phase25_target_wet_recall_seed42_40e/evaluation_test/metrics.json"
    ),
    "phase27_standard": Path(
        "runs/phase27_volume_response_seed42_40e/evaluation_test/metrics.json"
    ),
    "phase29_standard": Path(
        "runs/phase29_tolerance_band_volume_seed42_40e/evaluation_test/metrics.json"
    ),
}

PHASE_COLUMNS = {
    "phase25": "phase25_seed42",
    "phase27": "phase27_seed42",
    "phase29": "phase29_seed42",
}

BASELINE_COLUMNS = (
    "metric_group",
    "metric_name",
    "region",
    "phase25_seed42",
    "phase27_seed42",
    "phase29_seed42",
    "preferred_direction",
    "reference_baseline",
    "notes",
)

ACCEPTANCE_COLUMNS = (
    "threshold_id",
    "metric_group",
    "metric_name",
    "region",
    "baseline_reference",
    "acceptance_rule",
    "numeric_threshold",
    "threshold_type",
    "required_for_pilot_acceptance",
    "rationale",
)

REJECTION_COLUMNS = (
    "rejection_id",
    "rejection_rule",
    "trigger_metric_group",
    "trigger_metric_name",
    "trigger_region",
    "trigger_condition",
    "required_for_pilot_rejection",
    "rationale",
)

READINESS_COLUMNS = (
    "criterion",
    "status",
    "evidence",
    "blocker",
    "next_required_action",
)

STANDARD_METRICS = (
    "rmse",
    "mae",
    "wet_dry_iou",
    "rollout_stability",
    "step_rmse_std",
)

VALID_DOMAIN_METRICS = (
    "rmse",
    "mae",
    "false_dry_rate",
    "false_wet_rate",
    "false_dry_volume_loss_proxy",
    "false_wet_volume_excess_proxy",
    "relative_volume_bias_proxy",
    "absolute_relative_volume_bias_proxy",
    "peak_depth_underprediction",
)

MANHOLE_METRICS = (
    "false_dry_rate",
    "false_dry_volume_loss_proxy",
    "peak_depth_underprediction",
    "rmse",
    "mae",
)

GUARDRAIL_METRICS = (
    ("boundary_ring", "false_dry_rate"),
    ("boundary_ring", "false_wet_rate"),
    ("high_impervious_valid", "false_wet_rate"),
    ("high_impervious_valid", "false_wet_volume_excess_proxy"),
)

LOWER_IS_BETTER = {
    "rmse",
    "mae",
    "step_rmse_std",
    "false_dry_rate",
    "false_wet_rate",
    "false_dry_volume_loss_proxy",
    "false_wet_volume_excess_proxy",
    "relative_volume_bias_proxy",
    "absolute_relative_volume_bias_proxy",
    "peak_depth_underprediction",
}

HIGHER_IS_BETTER = {"wet_dry_iou", "rollout_stability"}

DESIGN_ONLY_GUARDRAILS = {
    "does_not_train": True,
    "does_not_modify_model_architecture": True,
    "does_not_modify_losses": True,
    "does_not_modify_training_configs": True,
    "does_not_run_seed42": True,
    "does_not_run_seed123_or_seed202": True,
    "does_not_perform_sweeps": True,
    "does_not_continue_phase29": True,
    "does_not_claim_phase29_success": True,
    "does_not_claim_strict_conservation": True,
    "does_not_claim_full_mass_conservation": True,
    "does_not_claim_swe_pinn": True,
    "does_not_claim_hydrodynamic_closure": True,
    "keeps_claims_level4_plus_proxy": True,
    "does_not_authorize_training_directly": True,
}

DECISION = "thresholds_formalized_training_still_blocked"
NEXT_ALLOWED_STEP = "pilot_implementation_plan"
CANDIDATE = "manhole_nonzero_false_dry_guardrail"
TARGET_REGION = "manhole_nonzero_valid"
TARGET_METRIC = "false_dry_rate"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Formalize Phase 34 diagnostic-only acceptance and rejection thresholds "
            "for a possible future seed42 pilot. This script does not train, modify "
            "losses, modify configs, modify architecture, run seeds, or perform sweeps."
        )
    )
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    return parser.parse_args()


def repo_path(path: Path) -> Path:
    return path if path.is_absolute() else REPO_ROOT / path


def require_inputs() -> dict[str, Path]:
    resolved = {name: repo_path(path) for name, path in INPUTS.items()}
    missing = [
        str(path.relative_to(REPO_ROOT)).replace("\\", "/")
        for path in resolved.values()
        if not path.exists()
    ]
    if missing:
        raise FileNotFoundError("Missing required Phase 34 inputs: " + ", ".join(missing))
    return resolved


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv_rows(path: Path, columns: tuple[str, ...], rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        for row in rows:
            writer.writerow({column: format_cell(row.get(column)) for column in columns})


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def format_cell(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, float):
        return f"{value:.12g}"
    return str(value)


def as_float(value: Any) -> float | None:
    if value in (None, ""):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def fmt(value: float | None) -> str:
    return "NA" if value is None else f"{value:.12g}"


def build_masked_index(rows: list[dict[str, str]]) -> dict[tuple[str, str], dict[str, str]]:
    return {(row["phase"], row["region"]): row for row in rows}


def metric_direction(metric_name: str) -> str:
    if metric_name in HIGHER_IS_BETTER:
        return "higher_is_better"
    if metric_name in LOWER_IS_BETTER:
        return "lower_is_better"
    return "context_dependent"


def metric_reference(metric_name: str, region: str) -> str:
    if metric_name == "relative_volume_bias_proxy":
        return "Phase 27 and Phase 29 signed proxy values; absolute proxy is preferred for thresholding"
    if metric_name == "absolute_relative_volume_bias_proxy":
        return "Phase 27/Phase 29 absolute proxy; improvement cannot override error regressions"
    if region == TARGET_REGION and metric_name == TARGET_METRIC:
        return "Phase 27 and Phase 29 seed42 masked baselines"
    return "Phase 27 seed42 baseline with Phase 29 trade-off check"


def get_metric_values(
    index: dict[tuple[str, str], dict[str, str]], region: str, metric_name: str
) -> dict[str, float | None]:
    values: dict[str, float | None] = {}
    for phase, column in PHASE_COLUMNS.items():
        row = index.get((phase, region), {})
        values[column] = as_float(row.get(metric_name))
    return values


def make_baseline_row(
    metric_group: str,
    metric_name: str,
    region: str,
    values: dict[str, float | None],
    notes: str,
) -> dict[str, Any]:
    return {
        "metric_group": metric_group,
        "metric_name": metric_name,
        "region": region,
        "phase25_seed42": values.get("phase25_seed42"),
        "phase27_seed42": values.get("phase27_seed42"),
        "phase29_seed42": values.get("phase29_seed42"),
        "preferred_direction": metric_direction(metric_name),
        "reference_baseline": metric_reference(metric_name, region),
        "notes": notes,
    }


def build_baseline_rows(
    standard_metrics: dict[str, dict[str, float]],
    masked_index: dict[tuple[str, str], dict[str, str]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []

    for metric_name in STANDARD_METRICS:
        values = {
            column: standard_metrics[phase].get(metric_name)
            for phase, column in PHASE_COLUMNS.items()
        }
        rows.append(
            make_baseline_row(
                "standard",
                metric_name,
                "all_evaluated_cells",
                values,
                "Standard evaluation_test metric from fixed seed42 baseline runs.",
            )
        )

    for metric_name in VALID_DOMAIN_METRICS:
        rows.append(
            make_baseline_row(
                "valid_domain_masked",
                metric_name,
                "valid_domain",
                get_metric_values(masked_index, "valid_domain", metric_name),
                "Phase 31 masked valid-domain diagnostic; Level 4+ proxy only.",
            )
        )

    for metric_name in MANHOLE_METRICS:
        rows.append(
            make_baseline_row(
                "manhole_nonzero_target",
                metric_name,
                TARGET_REGION,
                get_metric_values(masked_index, TARGET_REGION, metric_name),
                "Future candidate target region fixed by Phase 33 readiness review.",
            )
        )

    for region, metric_name in GUARDRAIL_METRICS:
        rows.append(
            make_baseline_row(
                "guardrail_masked",
                metric_name,
                region,
                get_metric_values(masked_index, region, metric_name),
                "Phase 32 guardrail metric fixed before any possible pilot.",
            )
        )

    return rows


def row_value(
    baseline_rows: list[dict[str, Any]], metric_group: str, metric_name: str, region: str, phase: str
) -> float:
    column = PHASE_COLUMNS[phase]
    for row in baseline_rows:
        if (
            row["metric_group"] == metric_group
            and row["metric_name"] == metric_name
            and row["region"] == region
        ):
            value = row.get(column)
            if value is None:
                raise ValueError(f"Missing value for {metric_group}/{metric_name}/{region}/{phase}")
            return float(value)
    raise KeyError(f"Missing baseline row for {metric_group}/{metric_name}/{region}")


def add_acceptance(
    rows: list[dict[str, Any]],
    metric_group: str,
    metric_name: str,
    region: str,
    baseline_reference: str,
    acceptance_rule: str,
    numeric_threshold: float | None,
    threshold_type: str,
    rationale: str,
    required: bool = True,
) -> None:
    rows.append(
        {
            "threshold_id": f"AT{len(rows) + 1:02d}",
            "metric_group": metric_group,
            "metric_name": metric_name,
            "region": region,
            "baseline_reference": baseline_reference,
            "acceptance_rule": acceptance_rule,
            "numeric_threshold": numeric_threshold,
            "threshold_type": threshold_type,
            "required_for_pilot_acceptance": "yes" if required else "no",
            "rationale": rationale,
        }
    )


def build_acceptance_rows(baseline_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []

    target_phase27 = row_value(
        baseline_rows, "manhole_nonzero_target", TARGET_METRIC, TARGET_REGION, "phase27"
    )
    target_phase29 = row_value(
        baseline_rows, "manhole_nonzero_target", TARGET_METRIC, TARGET_REGION, "phase29"
    )
    add_acceptance(
        rows,
        "manhole_nonzero_target",
        TARGET_METRIC,
        TARGET_REGION,
        f"Phase 27={fmt(target_phase27)}; Phase 29={fmt(target_phase29)}",
        "candidate value must be below Phase 29 and no higher than Phase 27",
        target_phase27,
        "improvement_required_and_no_worse_than_phase27",
        "The selected candidate targets the manhole-nonzero false-dry failure mode.",
    )

    for metric_name in ("rmse", "mae"):
        phase27 = row_value(baseline_rows, "valid_domain_masked", metric_name, "valid_domain", "phase27")
        add_acceptance(
            rows,
            "valid_domain_masked",
            metric_name,
            "valid_domain",
            f"Phase 27={fmt(phase27)}",
            "candidate value must be <= Phase 27 plus 2 percent tolerance",
            phase27 * 1.02,
            "small_tolerance_no_worse_than_phase27",
            "Depth-error regressions cannot be traded for a single proxy improvement.",
        )

    valid_false_dry_phase27 = row_value(
        baseline_rows, "valid_domain_masked", "false_dry_rate", "valid_domain", "phase27"
    )
    add_acceptance(
        rows,
        "valid_domain_masked",
        "false_dry_rate",
        "valid_domain",
        f"Phase 27={fmt(valid_false_dry_phase27)}",
        "candidate value must be <= Phase 27",
        valid_false_dry_phase27,
        "no_worse_than_phase27",
        "Phase 29 worsened this metric; a future pilot must not repeat that pattern.",
    )

    for metric_group, metric_name, region, tolerance in (
        ("valid_domain_masked", "false_wet_rate", "valid_domain", 0.0005),
        ("guardrail_masked", "false_wet_rate", "high_impervious_valid", 0.0005),
        ("guardrail_masked", "false_dry_rate", "boundary_ring", 0.0010),
    ):
        phase27 = row_value(baseline_rows, metric_group, metric_name, region, "phase27")
        add_acceptance(
            rows,
            metric_group,
            metric_name,
            region,
            f"Phase 27={fmt(phase27)}",
            f"candidate value must be <= Phase 27 plus {tolerance:g} absolute tolerance",
            phase27 + tolerance,
            "absolute_tolerance_no_worse_than_phase27",
            "Conservative pre-pilot tolerance for region-specific masked proxy guardrails.",
        )

    for metric_name in ("rmse", "mae"):
        phase27 = row_value(baseline_rows, "standard", metric_name, "all_evaluated_cells", "phase27")
        add_acceptance(
            rows,
            "standard",
            metric_name,
            "all_evaluated_cells",
            f"Phase 27={fmt(phase27)}",
            "candidate value must be <= Phase 27 plus 2 percent tolerance",
            phase27 * 1.02,
            "small_tolerance_no_worse_than_phase27",
            "Standard test metrics remain required global quality guardrails.",
        )

    wet_dry_iou_phase27 = row_value(
        baseline_rows, "standard", "wet_dry_iou", "all_evaluated_cells", "phase27"
    )
    add_acceptance(
        rows,
        "standard",
        "wet_dry_iou",
        "all_evaluated_cells",
        f"Phase 27={fmt(wet_dry_iou_phase27)}",
        "candidate value must be >= Phase 27 minus 0.005 absolute tolerance",
        wet_dry_iou_phase27 - 0.005,
        "minimum_no_material_decline",
        "Wet/dry classification quality cannot be sacrificed for proxy gains.",
    )

    rollout_phase27 = row_value(
        baseline_rows, "standard", "rollout_stability", "all_evaluated_cells", "phase27"
    )
    add_acceptance(
        rows,
        "standard",
        "rollout_stability",
        "all_evaluated_cells",
        f"Phase 27={fmt(rollout_phase27)}",
        "candidate value must be >= Phase 27 minus 0.001 absolute tolerance",
        rollout_phase27 - 0.001,
        "minimum_no_material_decline",
        "Temporal rollout behavior must not degrade under a future pilot.",
    )

    step_std_phase27 = row_value(
        baseline_rows, "standard", "step_rmse_std", "all_evaluated_cells", "phase27"
    )
    add_acceptance(
        rows,
        "standard",
        "step_rmse_std",
        "all_evaluated_cells",
        f"Phase 27={fmt(step_std_phase27)}",
        "candidate value must be <= Phase 27 plus 5 percent tolerance",
        step_std_phase27 * 1.05,
        "small_tolerance_no_worse_than_phase27",
        "Step-wise error variability must remain bounded.",
    )

    abs_bias_phase29 = row_value(
        baseline_rows,
        "valid_domain_masked",
        "absolute_relative_volume_bias_proxy",
        "valid_domain",
        "phase29",
    )
    add_acceptance(
        rows,
        "valid_domain_masked",
        "absolute_relative_volume_bias_proxy",
        "valid_domain",
        f"Phase 29={fmt(abs_bias_phase29)}",
        "candidate value may improve this proxy only if all required error guardrails pass",
        abs_bias_phase29,
        "conditional_proxy_improvement_not_sufficient",
        "Volume-bias proxy improvement alone cannot authorize pilot acceptance.",
        required=False,
    )

    add_acceptance(
        rows,
        "level_boundary",
        "claim_scope",
        "all_outputs",
        "Phase 31/32/33 Level 4+ boundary statements",
        (
            "all claims must remain Level 4+ proxy diagnostics with no Level 5, "
            "SWE/PINN, strict conservation, full mass conservation, or hydrodynamic "
            "closure claim"
        ),
        None,
        "mandatory_claim_boundary",
        "A future pilot remains proxy-scoped and cannot rely on unavailable Level 5 variables.",
    )

    return rows


def build_rejection_rows(baseline_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    def reject(
        rejection_rule: str,
        group: str,
        metric: str,
        region: str,
        condition: str,
        rationale: str,
    ) -> dict[str, Any]:
        return {
            "rejection_id": "",
            "rejection_rule": rejection_rule,
            "trigger_metric_group": group,
            "trigger_metric_name": metric,
            "trigger_region": region,
            "trigger_condition": condition,
            "required_for_pilot_rejection": "yes",
            "rationale": rationale,
        }

    valid_rmse_27 = row_value(baseline_rows, "valid_domain_masked", "rmse", "valid_domain", "phase27")
    valid_mae_27 = row_value(baseline_rows, "valid_domain_masked", "mae", "valid_domain", "phase27")
    manhole_fdr_29 = row_value(
        baseline_rows, "manhole_nonzero_target", "false_dry_rate", TARGET_REGION, "phase29"
    )
    high_fwr_29 = row_value(
        baseline_rows, "guardrail_masked", "false_wet_rate", "high_impervious_valid", "phase29"
    )
    boundary_fdr_29 = row_value(
        baseline_rows, "guardrail_masked", "false_dry_rate", "boundary_ring", "phase29"
    )
    standard_rmse_27 = row_value(
        baseline_rows, "standard", "rmse", "all_evaluated_cells", "phase27"
    )
    standard_mae_27 = row_value(
        baseline_rows, "standard", "mae", "all_evaluated_cells", "phase27"
    )
    iou_27 = row_value(baseline_rows, "standard", "wet_dry_iou", "all_evaluated_cells", "phase27")

    rows = [
        reject(
            "phase29_tradeoff_pattern",
            "multi_metric",
            "absolute_relative_volume_bias_proxy_plus_error_metrics",
            "valid_domain",
            (
                "absolute relative volume-bias proxy improves while RMSE, MAE, "
                "false-dry rate, and false-wet rate all worsen versus Phase 27"
            ),
            "This is the Phase 29 trade-off pattern and is a hard rejection.",
        ),
        reject(
            "target_metric_worsens_under_targeted_pilot",
            "manhole_nonzero_target",
            "false_dry_rate",
            TARGET_REGION,
            f"candidate false_dry_rate > Phase 29 value {fmt(manhole_fdr_29)}",
            "A manhole false-dry pilot cannot worsen the selected target failure metric.",
        ),
        reject(
            "high_impervious_false_wet_substantial_worsening",
            "guardrail_masked",
            "false_wet_rate",
            "high_impervious_valid",
            f"candidate false_wet_rate > Phase 29 value {fmt(high_fwr_29)}",
            "Substantial high-impervious false-wet expansion blocks acceptance.",
        ),
        reject(
            "boundary_ring_false_dry_substantial_worsening",
            "guardrail_masked",
            "false_dry_rate",
            "boundary_ring",
            f"candidate false_dry_rate > Phase 29 value {fmt(boundary_fdr_29)}",
            "Substantial boundary-ring false-dry degradation blocks acceptance.",
        ),
        reject(
            "standard_rmse_or_mae_worsens_beyond_tolerance",
            "standard",
            "rmse_or_mae",
            "all_evaluated_cells",
            (
                f"standard RMSE > {fmt(standard_rmse_27 * 1.05)} or "
                f"standard MAE > {fmt(standard_mae_27 * 1.05)}"
            ),
            "Global error regressions beyond a hard tolerance reject the pilot.",
        ),
        reject(
            "wet_dry_iou_declines_beyond_tolerance",
            "standard",
            "wet_dry_iou",
            "all_evaluated_cells",
            f"wet_dry_iou < {fmt(iou_27 - 0.01)}",
            "Wet/dry classification decline beyond tolerance rejects the pilot.",
        ),
        reject(
            "valid_domain_error_worsens_beyond_acceptance_tolerance",
            "valid_domain_masked",
            "rmse_or_mae",
            "valid_domain",
            f"valid RMSE > {fmt(valid_rmse_27 * 1.02)} or valid MAE > {fmt(valid_mae_27 * 1.02)}",
            "Masked valid-domain depth errors remain required guardrails.",
        ),
        reject(
            "requires_seed_expansion_or_sweep_to_interpret",
            "study_design",
            "interpretability",
            "seed42_only",
            "result cannot be interpreted without seed123, seed202, or a sweep",
            "Phase 34 does not authorize seed expansion or sweeps to rescue ambiguous results.",
        ),
        reject(
            "claim_exceeds_level4_plus_proxy_scope",
            "level_boundary",
            "claim_scope",
            "all_outputs",
            (
                "any claim states or implies Level 5 support, SWE/PINN residuals, strict "
                "conservation, full mass conservation, or hydrodynamic closure"
            ),
            "Unsupported strong-physics claims are hard rejection conditions.",
        ),
    ]
    for index, row in enumerate(rows, start=1):
        row["rejection_id"] = f"RT{index:02d}"
    return rows


def build_readiness_rows(
    baseline_rows: list[dict[str, Any]],
    acceptance_rows: list[dict[str, Any]],
    rejection_rows: list[dict[str, Any]],
    phase33_summary: dict[str, Any],
) -> list[dict[str, Any]]:
    return [
        {
            "criterion": "baseline_metric_table_generated",
            "status": "met",
            "evidence": f"{len(baseline_rows)} Phase 25/27/29 baseline metric rows fixed",
            "blocker": "none",
            "next_required_action": "Use fixed baselines in a future pilot implementation plan.",
        },
        {
            "criterion": "single_future_candidate_locked_for_thresholds",
            "status": "met",
            "evidence": f"candidate={CANDIDATE}; region={TARGET_REGION}; metric={TARGET_METRIC}",
            "blocker": "none",
            "next_required_action": "Do not train; translate this into a separate implementation plan first.",
        },
        {
            "criterion": "acceptance_thresholds_fixed",
            "status": "met_pre_pilot_thresholds_formalized",
            "evidence": f"{len(acceptance_rows)} acceptance thresholds generated",
            "blocker": "training still blocked",
            "next_required_action": "Review thresholds in the future pilot implementation plan.",
        },
        {
            "criterion": "rejection_thresholds_fixed",
            "status": "met_pre_pilot_thresholds_formalized",
            "evidence": f"{len(rejection_rows)} hard rejection rules generated",
            "blocker": "training still blocked",
            "next_required_action": "Carry rejection rules forward unchanged unless explicitly revised.",
        },
        {
            "criterion": "phase29_tradeoff_rejection_rule_written",
            "status": "met",
            "evidence": "RT01 rejects volume-bias proxy improvement with concurrent RMSE/MAE/false-dry/false-wet worsening.",
            "blocker": "none",
            "next_required_action": "Do not claim Phase 29 success.",
        },
        {
            "criterion": "level4_plus_scope_preserved",
            "status": "met",
            "evidence": "Acceptance and rejection rules include mandatory Level 4+ proxy claim boundary.",
            "blocker": "none",
            "next_required_action": "Keep all future pilot wording at proxy-diagnostic scope.",
        },
        {
            "criterion": "phase34_training_authorization",
            "status": "not_authorized",
            "evidence": f"Phase 33 prior decision={phase33_summary.get('final_decision', 'unknown')}; Phase 34 decision={DECISION}",
            "blocker": "Phase 34 is threshold formalization only.",
            "next_required_action": NEXT_ALLOWED_STEP,
        },
    ]


def markdown_table(rows: list[dict[str, Any]], columns: tuple[str, ...]) -> str:
    lines = ["| " + " | ".join(columns) + " |", "| " + " | ".join(["---"] * len(columns)) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(format_cell(row.get(column)) for column in columns) + " |")
    return "\n".join(lines)


def write_summary_markdown(
    path: Path,
    baseline_rows: list[dict[str, Any]],
    acceptance_rows: list[dict[str, Any]],
    rejection_rows: list[dict[str, Any]],
    readiness_rows: list[dict[str, Any]],
    summary: dict[str, Any],
) -> None:
    baseline_preview = baseline_rows[:12]
    content = f"""# Phase 34 Pilot Threshold Summary

## 1. Executive summary

Phase 34 formalized diagnostic-only pre-pilot acceptance and rejection thresholds for a possible future seed42 pilot. The recommended future candidate is `{CANDIDATE}`, targeting `{TARGET_REGION}` `{TARGET_METRIC}`. Training remains unauthorized.

## 2. Baselines fixed

Fixed baseline metric rows: {len(baseline_rows)}.

{markdown_table(baseline_preview, BASELINE_COLUMNS)}

Full table: `baseline_metric_table.csv`.

## 3. Acceptance thresholds

Acceptance threshold rows: {len(acceptance_rows)}.

{markdown_table(acceptance_rows, ACCEPTANCE_COLUMNS)}

## 4. Rejection thresholds

Rejection threshold rows: {len(rejection_rows)}.

{markdown_table(rejection_rows, REJECTION_COLUMNS)}

## 5. Phase 29 trade-off rejection rule

RT01 rejects any future result that improves the absolute relative volume-bias proxy while worsening valid-domain RMSE, MAE, false-dry rate, and false-wet rate versus Phase 27. This prevents repeating the Phase 29 pattern and does not claim Phase 29 success.

## 6. Manhole-nonzero false-dry pilot target

The future candidate is fixed only for threshold design: `{CANDIDATE}`. Acceptance requires `{TARGET_REGION}` `{TARGET_METRIC}` to improve versus Phase 29 and be no higher than Phase 27.

## 7. Threshold readiness status

Readiness rows: {len(readiness_rows)}.

{markdown_table(readiness_rows, READINESS_COLUMNS)}

## 8. Current decision

Decision: `{summary["decision"]}`.

Training authorized: `{str(summary["training_authorized"]).lower()}`.

## 9. Why training remains blocked

Phase 34 only formalizes thresholds. It does not implement a loss, config, architecture change, or training run. A separate pilot implementation plan is still required before any future training decision.

## 10. Next allowed step

Next allowed step: `{summary["next_allowed_step"]}`.

## 11. Level boundary

All conclusions remain Level 4+ proxy diagnostics. This script does not claim strict conservation, full mass conservation, SWE/PINN behavior, or hydrodynamic closure.
"""
    path.write_text(content, encoding="utf-8")


def main() -> None:
    args = parse_args()
    paths = require_inputs()
    output_dir = repo_path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    standard_metrics = {
        "phase25": read_json(paths["phase25_standard"]),
        "phase27": read_json(paths["phase27_standard"]),
        "phase29": read_json(paths["phase29_standard"]),
    }
    masked_rows = read_csv_rows(paths["phase31_by_region"])
    masked_index = build_masked_index(masked_rows)
    phase31_delta_rows = read_csv_rows(paths["phase31_delta"])
    phase32_guardrail_rows = read_csv_rows(paths["phase32_guardrails"])
    phase32_stop_go_rows = read_csv_rows(paths["phase32_stop_go"])
    phase33_readiness_rows = read_csv_rows(paths["phase33_readiness"])
    phase31_summary = read_json(paths["phase31_summary"])
    phase33_summary = read_json(paths["phase33_summary"])

    baseline_rows = build_baseline_rows(standard_metrics, masked_index)
    acceptance_rows = build_acceptance_rows(baseline_rows)
    rejection_rows = build_rejection_rows(baseline_rows)
    readiness_rows = build_readiness_rows(
        baseline_rows, acceptance_rows, rejection_rows, phase33_summary
    )

    summary = {
        "phase": 34,
        "purpose": "diagnostic-only pilot threshold formalization",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "script": "scripts/formalize_phase34_pilot_thresholds.py",
        "candidate": CANDIDATE,
        "target_region": TARGET_REGION,
        "target_metric": TARGET_METRIC,
        "baseline_metrics_count": len(baseline_rows),
        "acceptance_thresholds_count": len(acceptance_rows),
        "rejection_thresholds_count": len(rejection_rows),
        "readiness_criteria_count": len(readiness_rows),
        "decision": DECISION,
        "training_authorized": False,
        "next_allowed_step": NEXT_ALLOWED_STEP,
        "design_only_guardrails": DESIGN_ONLY_GUARDRAILS,
        "level_boundary": (
            "All conclusions remain Level 4+ proxy diagnostics. This script does not "
            "claim strict conservation, full mass conservation, SWE/PINN behavior, or "
            "hydrodynamic closure."
        ),
        "input_sources": {
            name: str(path.relative_to(REPO_ROOT)).replace("\\", "/")
            for name, path in paths.items()
        },
        "input_row_counts": {
            "phase31_masked_by_region": len(masked_rows),
            "phase31_delta": len(phase31_delta_rows),
            "phase32_guardrail_metrics": len(phase32_guardrail_rows),
            "phase32_stop_go_criteria": len(phase32_stop_go_rows),
            "phase33_readiness_criteria": len(phase33_readiness_rows),
        },
        "phase31_processed": phase31_summary.get("processed", {}),
        "phase33_prior_decision": phase33_summary.get("final_decision"),
        "phase33_training_authorized": phase33_summary.get("training_authorized"),
    }

    write_csv_rows(output_dir / "baseline_metric_table.csv", BASELINE_COLUMNS, baseline_rows)
    write_csv_rows(
        output_dir / "acceptance_thresholds.csv", ACCEPTANCE_COLUMNS, acceptance_rows
    )
    write_csv_rows(output_dir / "rejection_thresholds.csv", REJECTION_COLUMNS, rejection_rows)
    write_csv_rows(
        output_dir / "threshold_readiness_status.csv", READINESS_COLUMNS, readiness_rows
    )
    write_json(output_dir / "phase34_threshold_summary.json", summary)
    write_summary_markdown(
        output_dir / "phase34_threshold_summary.md",
        baseline_rows,
        acceptance_rows,
        rejection_rows,
        readiness_rows,
        summary,
    )

    print(f"baseline metrics count: {len(baseline_rows)}")
    print(f"acceptance thresholds count: {len(acceptance_rows)}")
    print(f"rejection thresholds count: {len(rejection_rows)}")
    print(f"readiness criteria count: {len(readiness_rows)}")
    print(f"decision: {DECISION}")
    print("training_authorized: false")


if __name__ == "__main__":
    main()
