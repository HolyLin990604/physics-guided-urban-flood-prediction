from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = Path("analysis/phase32_domain_boundary_aware_design")

INPUTS = {
    "phase32_plan": Path("docs/phase32_domain_boundary_aware_physical_consistency_plan.md"),
    "phase32_design": Path("docs/phase32_domain_boundary_aware_design.md"),
    "phase31_findings": Path("docs/phase31_physics_input_recovery_readiness_findings.md"),
    "phase31_masked_findings": Path(
        "analysis/phase31_physics_input_recovery_readiness/masked_physical_error_findings.md"
    ),
    "phase31_delta_csv": Path(
        "analysis/phase31_physics_input_recovery_readiness/"
        "masked_physical_error_delta_phase29_vs_phase27.csv"
    ),
}

CURRENT_DECISION = "design_ready_no_training_yet"
CLAIM_BOUNDARY = "Level 4+ proxy diagnostics supported; Level 5 remains unsupported."

GUARDRAIL_COLUMNS = (
    "guardrail_group",
    "metric_name",
    "region",
    "direction",
    "baseline_reference",
    "failure_mode_addressed",
    "required_before_training",
    "notes",
)

STOP_GO_COLUMNS = (
    "criterion_id",
    "criterion",
    "status_now",
    "required_for_seed42_pilot",
    "failure_if_not_met",
    "evidence_source",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Formalize Phase 32 domain-/boundary-aware guardrail metrics and stop/go "
            "criteria. Design-only: does not train, modify model architecture, modify "
            "losses, modify training configs, run seed123/seed202, or perform sweeps."
        )
    )
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    return parser.parse_args()


def repo_path(path: Path) -> Path:
    return path if path.is_absolute() else REPO_ROOT / path


def require_inputs() -> dict[str, Path]:
    resolved = {name: repo_path(path) for name, path in INPUTS.items()}
    missing = [str(path.relative_to(REPO_ROOT)) for path in resolved.values() if not path.exists()]
    if missing:
        raise FileNotFoundError("Missing required Phase 32/31 inputs: " + ", ".join(missing))
    return resolved


def read_text_inputs(paths: dict[str, Path]) -> dict[str, str]:
    return {
        name: path.read_text(encoding="utf-8")
        for name, path in paths.items()
        if path.suffix.lower() in {".md", ".txt"}
    }


def read_delta_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def metric_lookup(delta_rows: list[dict[str, str]]) -> dict[tuple[str, str], dict[str, str]]:
    return {
        (row["region"], row["metric"]): row
        for row in delta_rows
        if row.get("region") and row.get("metric")
    }


def fmt_float(value: str) -> str:
    try:
        return f"{float(value):.6g}"
    except (TypeError, ValueError):
        return value


def baseline_from_delta(
    lookup: dict[tuple[str, str], dict[str, str]],
    region: str,
    metric: str,
    fallback: str,
) -> str:
    row = lookup.get((region, metric))
    if not row:
        return fallback
    phase27 = fmt_float(row.get("phase27", ""))
    phase29 = fmt_float(row.get("phase29", ""))
    delta = fmt_float(row.get("delta", ""))
    improved = row.get("improved", "")
    improved_text = f", improved={improved}" if improved else ""
    return f"Phase 27={phase27}; Phase 29={phase29}; delta={delta}{improved_text}"


def build_guardrail_metrics(lookup: dict[tuple[str, str], dict[str, str]]) -> list[dict[str, str]]:
    fixed_standard = "Fixed Phase 25/27/29 standard evaluation baselines before any pilot"
    fixed_guardrail = "Fixed Phase 27 and Phase 29 masked diagnostic baselines before any pilot"

    rows: list[dict[str, str]] = [
        {
            "guardrail_group": "standard",
            "metric_name": "overall_rmse",
            "region": "all_evaluated_cells",
            "direction": "must_not_worsen_beyond_predeclared_tolerance",
            "baseline_reference": fixed_standard,
            "failure_mode_addressed": "Global depth accuracy regression hidden by proxy gains",
            "required_before_training": "yes",
            "notes": "Standard model-quality guardrail; threshold must be fixed before seed42 pilot.",
        },
        {
            "guardrail_group": "standard",
            "metric_name": "overall_mae",
            "region": "all_evaluated_cells",
            "direction": "must_not_worsen_beyond_predeclared_tolerance",
            "baseline_reference": fixed_standard,
            "failure_mode_addressed": "Global mean absolute depth error regression",
            "required_before_training": "yes",
            "notes": "Keeps future proxy design comparable to prior standard tables.",
        },
        {
            "guardrail_group": "standard",
            "metric_name": "wet_dry_iou",
            "region": "all_evaluated_cells",
            "direction": "must_not_decline_beyond_predeclared_tolerance",
            "baseline_reference": fixed_standard,
            "failure_mode_addressed": "Wet/dry classification degradation",
            "required_before_training": "yes",
            "notes": "Prevents a volume proxy from masking classification failures.",
        },
        {
            "guardrail_group": "standard",
            "metric_name": "rollout_stability",
            "region": "full_rollout",
            "direction": "must_not_degrade",
            "baseline_reference": fixed_standard,
            "failure_mode_addressed": "Unstable temporal rollout or accumulation behavior",
            "required_before_training": "yes",
            "notes": "Design-level criterion only; no rollout is executed by this script.",
        },
        {
            "guardrail_group": "valid_domain",
            "metric_name": "valid_domain_rmse",
            "region": "valid_domain",
            "direction": "lower_or_no_worse_than_predeclared_tolerance",
            "baseline_reference": baseline_from_delta(lookup, "valid_domain", "rmse", fixed_guardrail),
            "failure_mode_addressed": "Phase 29 valid-domain RMSE regression",
            "required_before_training": "yes",
            "notes": "Valid-domain mask is absolute_DEM < 99; proxy diagnostic only.",
        },
        {
            "guardrail_group": "valid_domain",
            "metric_name": "valid_domain_mae",
            "region": "valid_domain",
            "direction": "lower_or_no_worse_than_predeclared_tolerance",
            "baseline_reference": baseline_from_delta(lookup, "valid_domain", "mae", fixed_guardrail),
            "failure_mode_addressed": "Phase 29 valid-domain MAE regression",
            "required_before_training": "yes",
            "notes": "Rejects proxy designs that trade lower volume bias for worse depth errors.",
        },
        {
            "guardrail_group": "valid_domain",
            "metric_name": "valid_domain_false_dry_rate",
            "region": "valid_domain",
            "direction": "lower_or_no_worse_than_predeclared_tolerance",
            "baseline_reference": baseline_from_delta(
                lookup, "valid_domain", "false_dry_rate", fixed_guardrail
            ),
            "failure_mode_addressed": "False-dry expansion inside the physical target domain",
            "required_before_training": "yes",
            "notes": "Required because Phase 29 worsened valid-domain false-dry behavior.",
        },
        {
            "guardrail_group": "valid_domain",
            "metric_name": "valid_domain_false_wet_rate",
            "region": "valid_domain",
            "direction": "lower_or_no_worse_than_predeclared_tolerance",
            "baseline_reference": baseline_from_delta(
                lookup, "valid_domain", "false_wet_rate", fixed_guardrail
            ),
            "failure_mode_addressed": "False-wet expansion inside the physical target domain",
            "required_before_training": "yes",
            "notes": "Required because Phase 29 worsened valid-domain false-wet behavior.",
        },
        {
            "guardrail_group": "valid_domain",
            "metric_name": "valid_domain_relative_volume_bias_proxy",
            "region": "valid_domain",
            "direction": "absolute_value_lower_without_standard_metric_regression",
            "baseline_reference": baseline_from_delta(
                lookup, "valid_domain", "relative_volume_bias_proxy", fixed_guardrail
            ),
            "failure_mode_addressed": "Ungrounded volume-proxy improvement claim",
            "required_before_training": "yes",
            "notes": "Proxy only; does not imply strict or full mass conservation.",
        },
        {
            "guardrail_group": "boundary_ring",
            "metric_name": "boundary_ring_false_dry_rate",
            "region": "boundary_ring",
            "direction": "lower_or_no_worse_than_predeclared_tolerance",
            "baseline_reference": baseline_from_delta(
                lookup, "boundary_ring", "false_dry_rate", fixed_guardrail
            ),
            "failure_mode_addressed": "Boundary-ring false-dry degradation",
            "required_before_training": "yes",
            "notes": "Boundary-aware proxy guardrail; no boundary flux closure is claimed.",
        },
        {
            "guardrail_group": "boundary_ring",
            "metric_name": "boundary_ring_false_wet_rate",
            "region": "boundary_ring",
            "direction": "lower_or_no_worse_than_predeclared_tolerance",
            "baseline_reference": baseline_from_delta(
                lookup, "boundary_ring", "false_wet_rate", fixed_guardrail
            ),
            "failure_mode_addressed": "Spurious wet expansion near valid-domain edges",
            "required_before_training": "yes",
            "notes": "Boundary cells remain ambiguous without measured boundary conditions.",
        },
        {
            "guardrail_group": "boundary_ring",
            "metric_name": "boundary_ring_peak_depth_underprediction",
            "region": "boundary_ring",
            "direction": "lower_or_no_worse_than_predeclared_tolerance",
            "baseline_reference": baseline_from_delta(
                lookup, "boundary_ring", "peak_depth_underprediction", fixed_guardrail
            ),
            "failure_mode_addressed": "Boundary peak-depth underprediction",
            "required_before_training": "yes",
            "notes": "Depth-raster proxy only; not a boundary-condition residual.",
        },
        {
            "guardrail_group": "high_impervious_valid",
            "metric_name": "high_impervious_false_wet_rate",
            "region": "high_impervious_valid",
            "direction": "lower_or_no_worse_than_predeclared_tolerance",
            "baseline_reference": baseline_from_delta(
                lookup, "high_impervious_valid", "false_wet_rate", fixed_guardrail
            ),
            "failure_mode_addressed": "Highest Phase 29 region-specific false-wet behavior",
            "required_before_training": "yes",
            "notes": "Imperviousness is a static runoff proxy, not hydraulic forcing.",
        },
        {
            "guardrail_group": "high_impervious_valid",
            "metric_name": "high_impervious_false_wet_volume_excess_proxy",
            "region": "high_impervious_valid",
            "direction": "lower_or_no_worse_than_predeclared_tolerance",
            "baseline_reference": baseline_from_delta(
                lookup,
                "high_impervious_valid",
                "false_wet_volume_excess_proxy",
                fixed_guardrail,
            ),
            "failure_mode_addressed": "Spurious high-impervious predicted-volume excess",
            "required_before_training": "yes",
            "notes": "Volume-excess proxy only; no conservation claim.",
        },
        {
            "guardrail_group": "manhole_nonzero_valid",
            "metric_name": "manhole_nonzero_false_dry_rate",
            "region": "manhole_nonzero_valid",
            "direction": "lower_or_no_worse_than_predeclared_tolerance",
            "baseline_reference": baseline_from_delta(
                lookup, "manhole_nonzero_valid", "false_dry_rate", fixed_guardrail
            ),
            "failure_mode_addressed": "Highest Phase 29 region-specific false-dry behavior",
            "required_before_training": "yes",
            "notes": "Manholes are sparse indicators, not source/sink fields.",
        },
        {
            "guardrail_group": "manhole_nonzero_valid",
            "metric_name": "manhole_nonzero_false_dry_volume_loss_proxy",
            "region": "manhole_nonzero_valid",
            "direction": "lower_or_no_worse_than_predeclared_tolerance",
            "baseline_reference": baseline_from_delta(
                lookup,
                "manhole_nonzero_valid",
                "false_dry_volume_loss_proxy",
                fixed_guardrail,
            ),
            "failure_mode_addressed": "Manhole-region underprediction volume-loss proxy",
            "required_before_training": "yes",
            "notes": "Proxy diagnostic only; not drainage-network closure.",
        },
        {
            "guardrail_group": "dry_threshold",
            "metric_name": "dry_or_threshold_predicted_volume_contribution",
            "region": "dry_or_threshold_valid_domain",
            "direction": "must_be_predeclared_and_bounded",
            "baseline_reference": "Phase 28 dry_or_threshold failure diagnosis plus Phase 27/29 masked baselines",
            "failure_mode_addressed": "Low-depth accumulation and false-wet volume inflation",
            "required_before_training": "yes",
            "notes": "Threshold definitions must be fixed before any pilot.",
        },
        {
            "guardrail_group": "level_boundary",
            "metric_name": "no_level5_claim",
            "region": "claim_scope",
            "direction": "must_hold",
            "baseline_reference": "Phase 31/32 Level 4+ boundary statements",
            "failure_mode_addressed": "Overclaiming unsupported strong physics",
            "required_before_training": "yes",
            "notes": "Level 5 remains unsupported without hydrodynamic state, fluxes, dx/dy, dt, and boundary fields.",
        },
        {
            "guardrail_group": "level_boundary",
            "metric_name": "no_swe_pinn_claim",
            "region": "claim_scope",
            "direction": "must_hold",
            "baseline_reference": "Phase 31/32 Level 4+ boundary statements",
            "failure_mode_addressed": "Unsupported SWE/PINN residual claim",
            "required_before_training": "yes",
            "notes": "The design is not a SWE/PINN implementation.",
        },
        {
            "guardrail_group": "level_boundary",
            "metric_name": "no_strict_conservation_claim",
            "region": "claim_scope",
            "direction": "must_hold",
            "baseline_reference": "Phase 31/32 Level 4+ boundary statements",
            "failure_mode_addressed": "Unsupported strict or full mass-conservation claim",
            "required_before_training": "yes",
            "notes": "Only depth-raster volume-bias proxies are available.",
        },
    ]
    return rows


def build_stop_go_criteria() -> list[dict[str, str]]:
    return [
        {
            "criterion_id": "SG01",
            "criterion": "Phase 32 remains design/diagnostic-only before training.",
            "status_now": "met_design_formalized",
            "required_for_seed42_pilot": "yes",
            "failure_if_not_met": "Remain diagnostic-only; do not train.",
            "evidence_source": "docs/phase32_domain_boundary_aware_design.md",
        },
        {
            "criterion_id": "SG02",
            "criterion": "The future objective targets one diagnosed failure mode.",
            "status_now": "not_met_no_future_objective_selected",
            "required_for_seed42_pilot": "yes",
            "failure_if_not_met": "No seed42 pilot.",
            "evidence_source": "docs/phase32_domain_boundary_aware_design.md; Phase 31 masked findings",
        },
        {
            "criterion_id": "SG03",
            "criterion": "Target region and mask definitions are fixed before training.",
            "status_now": "partially_met_design_masks_defined",
            "required_for_seed42_pilot": "yes",
            "failure_if_not_met": "No seed42 pilot.",
            "evidence_source": "Phase 31 static-mask recovery and Phase 32 design",
        },
        {
            "criterion_id": "SG04",
            "criterion": "All standard and masked guardrail metrics are fixed before training.",
            "status_now": "met_metric_framework_defined_thresholds_not_fixed",
            "required_for_seed42_pilot": "yes",
            "failure_if_not_met": "No seed42 pilot.",
            "evidence_source": "guardrail_metrics.csv",
        },
        {
            "criterion_id": "SG05",
            "criterion": "Baseline comparisons are fixed before training.",
            "status_now": "partially_met_phase27_phase29_masked_baselines_available",
            "required_for_seed42_pilot": "yes",
            "failure_if_not_met": "No seed42 pilot.",
            "evidence_source": "masked_physical_error_delta_phase29_vs_phase27.csv",
        },
        {
            "criterion_id": "SG06",
            "criterion": "Acceptance and rejection thresholds are written before training.",
            "status_now": "not_met_thresholds_not_declared",
            "required_for_seed42_pilot": "yes",
            "failure_if_not_met": "No seed42 pilot.",
            "evidence_source": "Phase 32 design requires predeclared tolerances",
        },
        {
            "criterion_id": "SG07",
            "criterion": "The design avoids repeating the Phase 29 tolerance-band trade-off.",
            "status_now": "met_as_design_guardrail_not_yet_tested",
            "required_for_seed42_pilot": "yes",
            "failure_if_not_met": "No seed42 pilot; Phase 29 should not be continued directly.",
            "evidence_source": "Phase 31 masked findings; Phase 32 design",
        },
        {
            "criterion_id": "SG08",
            "criterion": "No model architecture, loss, or training-config changes occur in Phase 32A.",
            "status_now": "met_this_script_is_design_only",
            "required_for_seed42_pilot": "yes",
            "failure_if_not_met": "Revert to design review before any training code work.",
            "evidence_source": "scripts/design_phase32_domain_boundary_guardrails.py",
        },
        {
            "criterion_id": "SG09",
            "criterion": "No seed123, seed202, or sweep execution is included.",
            "status_now": "met_this_script_runs_no_training",
            "required_for_seed42_pilot": "yes",
            "failure_if_not_met": "Stop expanded runs; seed42 pilot review only.",
            "evidence_source": "Phase 32 guardrails",
        },
        {
            "criterion_id": "SG10",
            "criterion": "All claims stay at Level 4+ proxy level.",
            "status_now": "met",
            "required_for_seed42_pilot": "yes",
            "failure_if_not_met": "No pilot and no success claim.",
            "evidence_source": "docs/phase31_physics_input_recovery_readiness_findings.md; Phase 32 design",
        },
        {
            "criterion_id": "SG11",
            "criterion": "No strict conservation, full mass conservation, SWE/PINN, or hydrodynamic-closure claim is made.",
            "status_now": "met",
            "required_for_seed42_pilot": "yes",
            "failure_if_not_met": "No pilot and revise claims.",
            "evidence_source": "Phase 31/32 Level boundary",
        },
        {
            "criterion_id": "SG12",
            "criterion": "Current Phase 32 decision is design_ready_no_training_yet.",
            "status_now": CURRENT_DECISION,
            "required_for_seed42_pilot": "yes",
            "failure_if_not_met": "Training remains unjustified.",
            "evidence_source": "docs/phase32_domain_boundary_aware_design.md",
        },
    ]


def write_csv(path: Path, fieldnames: tuple[str, ...], rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_summary_json(
    path: Path,
    input_paths: dict[str, Path],
    texts: dict[str, str],
    delta_rows: list[dict[str, str]],
    guardrails: list[dict[str, str]],
    stop_go: list[dict[str, str]],
) -> dict[str, Any]:
    summary: dict[str, Any] = {
        "phase": 32,
        "script": "scripts/design_phase32_domain_boundary_guardrails.py",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "current_decision": CURRENT_DECISION,
        "claim_boundary": CLAIM_BOUNDARY,
        "design_only_guardrails": {
            "does_not_train": True,
            "does_not_modify_model_architecture": True,
            "does_not_modify_losses": True,
            "does_not_modify_training_configs": True,
            "does_not_run_seed123_or_seed202": True,
            "does_not_perform_sweeps": True,
            "does_not_claim_strict_conservation": True,
            "does_not_claim_full_mass_conservation": True,
            "does_not_claim_swe_pinn": True,
            "does_not_claim_full_hydrodynamic_closure": True,
            "keeps_claims_level4_plus_proxy": True,
        },
        "input_sources": {
            name: str(path.relative_to(REPO_ROOT)).replace("\\", "/")
            for name, path in input_paths.items()
        },
        "source_text_checks": {
            name: {
                "contains_level4_plus": "Level 4+" in text,
                "contains_level5": "Level 5" in text,
                "contains_no_training": "No training" in text or "not train" in text,
            }
            for name, text in texts.items()
        },
        "phase31_delta_rows_read": len(delta_rows),
        "guardrail_metrics_count": len(guardrails),
        "stop_go_criteria_count": len(stop_go),
        "guardrail_groups": sorted({row["guardrail_group"] for row in guardrails}),
        "required_summary_statements": [
            "Phase 32 has a design and guardrail framework.",
            "No training is currently justified.",
            "A future seed42 pilot would require all guardrails and baseline comparisons to be fixed before training.",
            "Phase 29 should not be continued directly.",
            "Level 5 remains unsupported.",
        ],
    }
    path.write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    return summary


def write_markdown_summary(
    path: Path,
    guardrails: list[dict[str, str]],
    stop_go: list[dict[str, str]],
) -> None:
    groups = sorted({row["guardrail_group"] for row in guardrails})
    lines = [
        "# Phase 32 Guardrail Summary",
        "",
        "Phase 32 has a design and guardrail framework.",
        "",
        f"Current decision: `{CURRENT_DECISION}`.",
        "",
        "No training is currently justified.",
        "",
        (
            "A future seed42 pilot would require all guardrails and baseline comparisons "
            "to be fixed before training."
        ),
        "",
        "Phase 29 should not be continued directly.",
        "",
        "Level 5 remains unsupported.",
        "",
        "## Scope Boundary",
        "",
        CLAIM_BOUNDARY,
        "",
        "This formalization does not claim strict conservation, full mass conservation, SWE/PINN, "
        "or full hydrodynamic closure.",
        "",
        "## Guardrail Groups",
        "",
    ]
    lines.extend(f"- `{group}`" for group in groups)
    lines.extend(
        [
            "",
            "## Output Counts",
            "",
            f"- Guardrail metrics: `{len(guardrails)}`",
            f"- Stop/go criteria: `{len(stop_go)}`",
            "",
            "## Stop/Go Position",
            "",
            (
                "The project should remain design/diagnostic-only until a seed42 pilot objective, "
                "fixed target region, baseline comparisons, and acceptance/rejection thresholds are "
                "all documented before training."
            ),
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    args = parse_args()
    input_paths = require_inputs()
    texts = read_text_inputs(input_paths)
    delta_rows = read_delta_rows(input_paths["phase31_delta_csv"])
    lookup = metric_lookup(delta_rows)

    guardrails = build_guardrail_metrics(lookup)
    stop_go = build_stop_go_criteria()

    output_dir = repo_path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    write_csv(output_dir / "guardrail_metrics.csv", GUARDRAIL_COLUMNS, guardrails)
    write_csv(output_dir / "stop_go_criteria.csv", STOP_GO_COLUMNS, stop_go)
    summary = write_summary_json(
        output_dir / "design_summary.json",
        input_paths,
        texts,
        delta_rows,
        guardrails,
        stop_go,
    )
    write_markdown_summary(output_dir / "phase32_guardrail_summary.md", guardrails, stop_go)

    print(f"guardrail metrics count: {summary['guardrail_metrics_count']}")
    print(f"stop/go criteria count: {summary['stop_go_criteria_count']}")
    print(f"current decision: {summary['current_decision']}")
    print(f"Level 4+/Level 5 boundary: {summary['claim_boundary']}")


if __name__ == "__main__":
    main()
