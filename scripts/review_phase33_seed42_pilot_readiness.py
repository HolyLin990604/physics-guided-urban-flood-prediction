from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = Path("analysis/phase33_seed42_pilot_readiness")

INPUTS = {
    "phase33_plan": Path("docs/phase33_seed42_pilot_readiness_review_plan.md"),
    "phase32_findings": Path(
        "docs/phase32_domain_boundary_aware_physical_consistency_findings.md"
    ),
    "phase32_design": Path("docs/phase32_domain_boundary_aware_design.md"),
    "phase32_guardrail_metrics": Path(
        "analysis/phase32_domain_boundary_aware_design/guardrail_metrics.csv"
    ),
    "phase32_stop_go_criteria": Path(
        "analysis/phase32_domain_boundary_aware_design/stop_go_criteria.csv"
    ),
    "phase32_design_summary": Path(
        "analysis/phase32_domain_boundary_aware_design/design_summary.json"
    ),
    "phase31_masked_findings": Path(
        "analysis/phase31_physics_input_recovery_readiness/masked_physical_error_findings.md"
    ),
    "phase31_delta_csv": Path(
        "analysis/phase31_physics_input_recovery_readiness/"
        "masked_physical_error_delta_phase29_vs_phase27.csv"
    ),
    "phase31_masked_summary": Path(
        "analysis/phase31_physics_input_recovery_readiness/"
        "masked_physical_error_summary.json"
    ),
}

PILOT_OPTION_COLUMNS = (
    "option_id",
    "option_name",
    "target_failure_mode",
    "target_region",
    "evidence_strength",
    "specificity",
    "risk_level",
    "required_guardrails",
    "unmet_requirements",
    "readiness",
    "recommended_status",
)

READINESS_COLUMNS = (
    "criterion_id",
    "criterion",
    "status",
    "met",
    "evidence_source",
    "notes",
)

REQUIRED_GUARDRAIL_GROUPS = {
    "standard",
    "valid_domain",
    "boundary_ring",
    "high_impervious_valid",
    "manhole_nonzero_valid",
    "dry_threshold",
    "level_boundary",
}

DESIGN_ONLY_GUARDRAILS = {
    "does_not_train": True,
    "does_not_modify_model_architecture": True,
    "does_not_modify_losses": True,
    "does_not_modify_training_configs": True,
    "does_not_run_seed123_or_seed202": True,
    "does_not_perform_sweeps": True,
    "does_not_claim_phase29_success": True,
    "does_not_claim_strict_conservation": True,
    "does_not_claim_full_mass_conservation": True,
    "does_not_claim_swe_pinn": True,
    "does_not_claim_full_hydrodynamic_closure": True,
    "keeps_claims_level4_plus_proxy": True,
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Review Phase 33 seed42 pilot readiness under the Phase 32 guardrail "
            "framework. Diagnostic-only: does not train, modify model architecture, "
            "modify losses, modify training configs, run seed123/seed202, or perform sweeps."
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
        raise FileNotFoundError("Missing required Phase 33 inputs: " + ", ".join(missing))
    return resolved


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def read_text_inputs(paths: dict[str, Path]) -> dict[str, str]:
    return {
        name: path.read_text(encoding="utf-8")
        for name, path in paths.items()
        if path.suffix.lower() in {".md", ".txt"}
    }


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_csv(path: Path, fieldnames: tuple[str, ...], rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def metric_lookup(delta_rows: list[dict[str, str]]) -> dict[tuple[str, str], dict[str, str]]:
    return {
        (row.get("region", ""), row.get("metric", "")): row
        for row in delta_rows
        if row.get("region") and row.get("metric")
    }


def fmt_float(value: str | None) -> str:
    try:
        return f"{float(value):.6g}"
    except (TypeError, ValueError):
        return "" if value is None else value


def metric_note(
    lookup: dict[tuple[str, str], dict[str, str]],
    region: str,
    metric: str,
) -> str:
    row = lookup.get((region, metric))
    if not row:
        return "Phase 31/32 qualitative evidence only."
    return (
        f"Phase 27={fmt_float(row.get('phase27'))}; "
        f"Phase 29={fmt_float(row.get('phase29'))}; "
        f"delta={fmt_float(row.get('delta'))}; "
        f"improved={row.get('improved', '')}"
    )


def group_is_defined(guardrail_rows: list[dict[str, str]], group: str) -> bool:
    return any(
        row.get("guardrail_group") == group
        and row.get("required_before_training", "").lower() == "yes"
        for row in guardrail_rows
    )


def status_is_unmet(status: str) -> bool:
    lowered = status.lower()
    return lowered.startswith("not_met") or "not_met" in lowered


def status_is_partial(status: str) -> bool:
    lowered = status.lower()
    return lowered.startswith("partially_met") or "thresholds_not_fixed" in lowered


def build_readiness_criteria(
    stop_go_rows: list[dict[str, str]],
    guardrail_rows: list[dict[str, str]],
    texts: dict[str, str],
) -> list[dict[str, str]]:
    stop_go_by_id = {row["criterion_id"]: row for row in stop_go_rows}

    sg02 = stop_go_by_id["SG02"]
    sg03 = stop_go_by_id["SG03"]
    sg04 = stop_go_by_id["SG04"]
    sg05 = stop_go_by_id["SG05"]
    sg06 = stop_go_by_id["SG06"]
    sg07 = stop_go_by_id["SG07"]
    sg10 = stop_go_by_id["SG10"]
    sg11 = stop_go_by_id["SG11"]

    phase33_text = texts["phase33_plan"]
    phase32_text = texts["phase32_design"] + "\n" + texts["phase32_findings"]

    rows = [
        {
            "criterion_id": "RC01",
            "criterion": "diagnosed_failure_mode_defined",
            "status": sg02["status_now"],
            "met": "no",
            "evidence_source": sg02["evidence_source"],
            "notes": "Candidate diagnosed failure modes exist, but no single future objective is selected.",
        },
        {
            "criterion_id": "RC02",
            "criterion": "target_region_fixed",
            "status": sg03["status_now"],
            "met": "partial",
            "evidence_source": sg03["evidence_source"],
            "notes": "Recovered masks exist, but the selected pilot target region is not fixed.",
        },
        {
            "criterion_id": "RC03",
            "criterion": "baseline_comparisons_fixed",
            "status": sg05["status_now"],
            "met": "partial",
            "evidence_source": sg05["evidence_source"],
            "notes": "Phase 27 and Phase 29 masked baselines are available; full Phase 25/27/29 acceptance and rejection comparisons are not written.",
        },
        {
            "criterion_id": "RC04",
            "criterion": "acceptance_thresholds_fixed",
            "status": sg06["status_now"],
            "met": "no",
            "evidence_source": sg06["evidence_source"],
            "notes": "Acceptance thresholds remain undeclared, so training is not authorized.",
        },
        {
            "criterion_id": "RC05",
            "criterion": "rejection_thresholds_fixed",
            "status": sg06["status_now"],
            "met": "no",
            "evidence_source": sg06["evidence_source"],
            "notes": "Rejection thresholds remain undeclared, including hard rejection for repeating the Phase 29 trade-off.",
        },
        {
            "criterion_id": "RC06",
            "criterion": "standard_guardrails_defined",
            "status": "met" if group_is_defined(guardrail_rows, "standard") else sg04["status_now"],
            "met": "yes" if group_is_defined(guardrail_rows, "standard") else "no",
            "evidence_source": "analysis/phase32_domain_boundary_aware_design/guardrail_metrics.csv",
            "notes": "Standard guardrail metric group is defined; numeric thresholds are still separate readiness blockers.",
        },
        {
            "criterion_id": "RC07",
            "criterion": "valid_domain_guardrails_defined",
            "status": "met" if group_is_defined(guardrail_rows, "valid_domain") else sg04["status_now"],
            "met": "yes" if group_is_defined(guardrail_rows, "valid_domain") else "no",
            "evidence_source": "analysis/phase32_domain_boundary_aware_design/guardrail_metrics.csv",
            "notes": "Valid-domain masked guardrails are defined at Level 4+ proxy scope.",
        },
        {
            "criterion_id": "RC08",
            "criterion": "boundary_ring_guardrails_defined",
            "status": "met" if group_is_defined(guardrail_rows, "boundary_ring") else sg04["status_now"],
            "met": "yes" if group_is_defined(guardrail_rows, "boundary_ring") else "no",
            "evidence_source": "analysis/phase32_domain_boundary_aware_design/guardrail_metrics.csv",
            "notes": "Boundary-ring guardrails are defined without claiming boundary flux closure.",
        },
        {
            "criterion_id": "RC09",
            "criterion": "high_impervious_guardrails_defined",
            "status": "met"
            if group_is_defined(guardrail_rows, "high_impervious_valid")
            else sg04["status_now"],
            "met": "yes" if group_is_defined(guardrail_rows, "high_impervious_valid") else "no",
            "evidence_source": "analysis/phase32_domain_boundary_aware_design/guardrail_metrics.csv",
            "notes": "High-impervious guardrails are defined as static-proxy diagnostics.",
        },
        {
            "criterion_id": "RC10",
            "criterion": "manhole_guardrails_defined",
            "status": "met"
            if group_is_defined(guardrail_rows, "manhole_nonzero_valid")
            else sg04["status_now"],
            "met": "yes" if group_is_defined(guardrail_rows, "manhole_nonzero_valid") else "no",
            "evidence_source": "analysis/phase32_domain_boundary_aware_design/guardrail_metrics.csv",
            "notes": "Manhole-region guardrails are defined as sparse-indicator proxy diagnostics.",
        },
        {
            "criterion_id": "RC11",
            "criterion": "dry_threshold_guardrails_defined",
            "status": "met" if group_is_defined(guardrail_rows, "dry_threshold") else sg04["status_now"],
            "met": "yes" if group_is_defined(guardrail_rows, "dry_threshold") else "no",
            "evidence_source": "analysis/phase32_domain_boundary_aware_design/guardrail_metrics.csv",
            "notes": "Dry-threshold guardrails are defined, but exact threshold acceptance/rejection values remain unset.",
        },
        {
            "criterion_id": "RC12",
            "criterion": "level_boundary_guardrails_defined",
            "status": sg11["status_now"],
            "met": "yes",
            "evidence_source": sg11["evidence_source"],
            "notes": "The reviewed materials preserve the Level 4+ / Level 5 boundary.",
        },
        {
            "criterion_id": "RC13",
            "criterion": "avoids_phase27_underresponse_only_failure",
            "status": "met_as_design_guardrail_not_yet_tested",
            "met": "yes",
            "evidence_source": "docs/phase33_seed42_pilot_readiness_review_plan.md",
            "notes": "The option set targets false-dry, false-wet, and dry-threshold failure modes rather than underresponse only.",
        },
        {
            "criterion_id": "RC14",
            "criterion": "avoids_phase29_tolerance_band_tradeoff",
            "status": sg07["status_now"],
            "met": "yes",
            "evidence_source": sg07["evidence_source"],
            "notes": "The review rejects optimizing volume proxy alone because Phase 29 worsened RMSE, MAE, false-dry, false-wet, false-dry volume-loss, and false-wet volume-excess.",
        },
        {
            "criterion_id": "RC15",
            "criterion": "level4_plus_scope_preserved",
            "status": sg10["status_now"],
            "met": "yes"
            if "Level 4+" in phase33_text and "Level 4+" in phase32_text
            else "partial",
            "evidence_source": sg10["evidence_source"],
            "notes": "Conclusions are limited to Level 4+ masked physical proxy diagnostics.",
        },
    ]
    return rows


def criteria_met(criteria_rows: list[dict[str, str]], criterion: str) -> bool:
    row = next(row for row in criteria_rows if row["criterion"] == criterion)
    return row["met"] == "yes"


def build_pilot_options(
    lookup: dict[tuple[str, str], dict[str, str]],
    criteria_rows: list[dict[str, str]],
) -> list[dict[str, str]]:
    thresholds_unmet = [
        "acceptance_thresholds_fixed",
        "rejection_thresholds_fixed",
        "full baseline acceptance/rejection comparisons",
    ]
    full_guardrails = ";".join(sorted(REQUIRED_GUARDRAIL_GROUPS))

    return [
        {
            "option_id": "A",
            "option_name": "boundary_ring_false_dry_guardrail",
            "target_failure_mode": "boundary-ring false-dry degradation",
            "target_region": "boundary_ring",
            "evidence_strength": "medium",
            "specificity": "high",
            "risk_level": "high",
            "required_guardrails": full_guardrails,
            "unmet_requirements": ";".join(thresholds_unmet),
            "readiness": "partial",
            "recommended_status": (
                "candidate_guardrail_only; not training-ready because thresholds and "
                "baseline acceptance/rejection criteria are not fixed; "
                + metric_note(lookup, "boundary_ring", "false_dry_rate")
            ),
        },
        {
            "option_id": "B",
            "option_name": "manhole_nonzero_false_dry_guardrail",
            "target_failure_mode": "highest Phase 29 false-dry rate",
            "target_region": "manhole_nonzero_valid",
            "evidence_strength": "high",
            "specificity": "high",
            "risk_level": "medium",
            "required_guardrails": full_guardrails,
            "unmet_requirements": ";".join(thresholds_unmet),
            "readiness": "partial",
            "recommended_status": (
                "most_promising_diagnostic_target; not training-ready because thresholds "
                "and baseline acceptance/rejection criteria are not fixed; "
                + metric_note(lookup, "manhole_nonzero_valid", "false_dry_rate")
            ),
        },
        {
            "option_id": "C",
            "option_name": "high_impervious_false_wet_guardrail",
            "target_failure_mode": "highest Phase 29 false-wet rate",
            "target_region": "high_impervious_valid",
            "evidence_strength": "high",
            "specificity": "high",
            "risk_level": "medium",
            "required_guardrails": full_guardrails,
            "unmet_requirements": ";".join(thresholds_unmet),
            "readiness": "partial",
            "recommended_status": (
                "promising_secondary_candidate; not training-ready because thresholds "
                "and baseline acceptance/rejection criteria are not fixed; "
                + metric_note(lookup, "high_impervious_valid", "false_wet_rate")
            ),
        },
        {
            "option_id": "D",
            "option_name": "dry_threshold_accumulation_guard",
            "target_failure_mode": "dry/near-threshold low-depth accumulation and false-wet expansion",
            "target_region": "dry_or_threshold_valid_domain",
            "evidence_strength": "medium",
            "specificity": "medium",
            "risk_level": "high",
            "required_guardrails": full_guardrails,
            "unmet_requirements": ";".join(thresholds_unmet + ["exact dry-threshold subset definition"]),
            "readiness": "partial",
            "recommended_status": (
                "candidate_guardrail_only; not training-ready because threshold-sensitive "
                "trade-offs require stricter predeclared acceptance and rejection criteria"
            ),
        },
        {
            "option_id": "E",
            "option_name": "no_pilot_yet",
            "target_failure_mode": "none",
            "target_region": "none",
            "evidence_strength": "high",
            "specificity": "medium",
            "risk_level": "low",
            "required_guardrails": full_guardrails,
            "unmet_requirements": "pilot objective selection;acceptance_thresholds_fixed;rejection_thresholds_fixed",
            "readiness": "ready",
            "recommended_status": "ready_as_diagnostic_hold; safest current status if no objective is selected",
        },
    ]


def all_stop_go_met(stop_go_rows: list[dict[str, str]]) -> bool:
    for row in stop_go_rows:
        status = row.get("status_now", "")
        if status_is_unmet(status) or status_is_partial(status):
            return False
        if "thresholds_not_fixed" in status.lower() or "no_future_objective_selected" in status.lower():
            return False
    return True


def decide(
    criteria_rows: list[dict[str, str]],
    option_rows: list[dict[str, str]],
    stop_go_rows: list[dict[str, str]],
) -> tuple[str, str, bool]:
    thresholds_fixed = criteria_met(criteria_rows, "acceptance_thresholds_fixed") and criteria_met(
        criteria_rows, "rejection_thresholds_fixed"
    )
    baselines_fixed = criteria_met(criteria_rows, "baseline_comparisons_fixed")
    objective_fixed = criteria_met(criteria_rows, "diagnosed_failure_mode_defined")
    target_fixed = criteria_met(criteria_rows, "target_region_fixed")
    training_authorized = False

    promising_options = [
        row
        for row in option_rows
        if row["option_name"]
        in {
            "manhole_nonzero_false_dry_guardrail",
            "high_impervious_false_wet_guardrail",
            "boundary_ring_false_dry_guardrail",
        }
    ]
    recommended_option = "manhole_nonzero_false_dry_guardrail"

    if all_stop_go_met(stop_go_rows) and thresholds_fixed and baselines_fixed and objective_fixed and target_fixed:
        return "narrow_seed42_pilot_allowed_next", recommended_option, True

    if promising_options and not (thresholds_fixed and baselines_fixed):
        return "pilot_design_ready_but_training_not_started", recommended_option, training_authorized

    return "pilot_not_ready", "no_pilot_yet", training_authorized


def relative_sources(input_paths: dict[str, Path]) -> dict[str, str]:
    return {
        name: str(path.relative_to(REPO_ROOT)).replace("\\", "/")
        for name, path in input_paths.items()
    }


def write_summary_json(
    path: Path,
    input_paths: dict[str, Path],
    texts: dict[str, str],
    phase32_summary: dict[str, Any],
    guardrail_rows: list[dict[str, str]],
    stop_go_rows: list[dict[str, str]],
    delta_rows: list[dict[str, str]],
    criteria_rows: list[dict[str, str]],
    option_rows: list[dict[str, str]],
    decision: str,
    recommended_option: str,
    training_authorized: bool,
) -> dict[str, Any]:
    unmet_criteria = [
        row["criterion"] for row in criteria_rows if row["met"] in {"no", "partial"}
    ]
    summary: dict[str, Any] = {
        "phase": 33,
        "script": "scripts/review_phase33_seed42_pilot_readiness.py",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "purpose": "diagnostic-only seed42 pilot readiness review",
        "input_sources": relative_sources(input_paths),
        "source_text_checks": {
            name: {
                "contains_level4_plus": "Level 4+" in text,
                "contains_no_training": "No training" in text or "not train" in text,
                "contains_no_strict_conservation": "strict conservation" in text,
                "contains_no_swe_pinn": "SWE/PINN" in text,
            }
            for name, text in texts.items()
        },
        "phase32_prior_decision": phase32_summary.get("current_decision"),
        "phase32_guardrail_metrics_read": len(guardrail_rows),
        "phase32_stop_go_criteria_read": len(stop_go_rows),
        "phase31_delta_rows_read": len(delta_rows),
        "pilot_options_evaluated": len(option_rows),
        "readiness_criteria_evaluated": len(criteria_rows),
        "recommended_option": recommended_option,
        "final_decision": decision,
        "training_authorized": training_authorized,
        "design_only_guardrails": DESIGN_ONLY_GUARDRAILS,
        "unmet_or_partial_readiness_criteria": unmet_criteria,
        "critical_blockers": [
            "acceptance_thresholds_fixed",
            "rejection_thresholds_fixed",
            "full Phase 25/27/29 baseline acceptance/rejection comparisons",
            "single pilot objective and target region not formally selected",
        ],
        "phase29_interpretation": {
            "valid_domain_relative_volume_bias_proxy_improved": True,
            "valid_domain_rmse_worsened": True,
            "valid_domain_mae_worsened": True,
            "valid_domain_false_dry_worsened": True,
            "valid_domain_false_wet_worsened": True,
            "valid_domain_false_dry_volume_loss_worsened": True,
            "valid_domain_false_wet_volume_excess_worsened": True,
            "conclusion": "No future pilot should optimize volume proxy alone.",
        },
        "level_boundary": (
            "All conclusions remain Level 4+ proxy diagnostics. This review does not "
            "claim strict conservation, full mass conservation, SWE/PINN, or full "
            "hydrodynamic closure."
        ),
    }
    path.write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    return summary


def write_markdown_summary(
    path: Path,
    input_paths: dict[str, Path],
    option_rows: list[dict[str, str]],
    criteria_rows: list[dict[str, str]],
    decision: str,
    recommended_option: str,
    training_authorized: bool,
) -> None:
    source_paths = relative_sources(input_paths)
    option_lines = [
        (
            f"| {row['option_id']} | `{row['option_name']}` | {row['evidence_strength']} | "
            f"{row['specificity']} | {row['risk_level']} | {row['readiness']} |"
        )
        for row in option_rows
    ]
    criteria_lines = [
        f"| `{row['criterion']}` | {row['met']} | {row['status']} |"
        for row in criteria_rows
    ]
    recommended_text = (
        "`manhole_nonzero_false_dry_guardrail` is the most promising diagnostic target "
        "because `manhole_nonzero_valid` has the highest Phase 29 false-dry rate. It is "
        "not training-ready."
        if recommended_option == "manhole_nonzero_false_dry_guardrail"
        else f"`{recommended_option}`"
    )

    lines = [
        "# Phase 33 Seed42 Pilot Readiness Summary",
        "",
        "## 1. Executive Summary",
        "",
        (
            "Phase 33 reviewed five pilot options under the Phase 32 guardrail framework. "
            "The review is diagnostic-only and does not train, modify losses, modify "
            "training configs, or modify model code."
        ),
        "",
        f"Current decision: `{decision}`.",
        "",
        f"Training authorized: `{str(training_authorized).lower()}`.",
        "",
        "The strongest candidate is a manhole-nonzero false-dry diagnostic target, but "
        "acceptance and rejection thresholds are not fixed, and full baseline "
        "acceptance/rejection criteria are not written. Training is therefore not authorized.",
        "",
        "## 2. Inputs Reviewed",
        "",
    ]
    lines.extend(f"- `{path}`" for path in source_paths.values())
    lines.extend(
        [
            "",
            "## 3. Pilot Option Comparison",
            "",
            "| Option | Name | Evidence | Specificity | Risk | Readiness |",
            "| --- | --- | --- | --- | --- | --- |",
            *option_lines,
            "",
            "## 4. Readiness Criteria Status",
            "",
            "| Criterion | Met | Status |",
            "| --- | --- | --- |",
            *criteria_lines,
            "",
            "## 5. Recommended Option, If Any",
            "",
            recommended_text,
            "",
            "No pilot is authorized from this recommendation. It is an objective-selection "
            "diagnostic only.",
            "",
            "## 6. Current Decision",
            "",
            f"`{decision}`",
            "",
            "## 7. Why Training Is Not Authorized",
            "",
            "- Acceptance thresholds are not fixed.",
            "- Rejection thresholds are not fixed.",
            "- Full Phase 25, Phase 27, and Phase 29 baseline acceptance/rejection criteria are not written.",
            "- No single option satisfies diagnosed failure mode, fixed target region, full guardrails, and thresholds.",
            "- Phase 29 improved the valid-domain relative volume-bias proxy but worsened RMSE, MAE, false-dry, false-wet, false-dry volume-loss, and false-wet volume-excess; volume proxy alone is not acceptable.",
            "",
            "## 8. Level Boundary",
            "",
            (
                "All conclusions remain Level 4+ proxy diagnostics. This review does not "
                "claim Phase 29 success, strict conservation, full mass conservation, SWE/PINN, "
                "or full hydrodynamic closure."
            ),
            "",
            "## 9. Next Required Actions Before Any Future Pilot",
            "",
            "- Select one diagnosed failure mode and one fixed target region.",
            "- Write numeric acceptance thresholds for all standard and masked guardrails.",
            "- Write numeric rejection thresholds that reject the Phase 29 trade-off pattern.",
            "- Fix Phase 25, Phase 27, and Phase 29 baseline comparison tables.",
            "- Keep the pilot seed42-only unless a separate stop/go review justifies expansion.",
            "- Preserve Level 4+ proxy-only claim language.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    args = parse_args()
    input_paths = require_inputs()
    texts = read_text_inputs(input_paths)

    guardrail_rows = read_csv_rows(input_paths["phase32_guardrail_metrics"])
    stop_go_rows = read_csv_rows(input_paths["phase32_stop_go_criteria"])
    delta_rows = read_csv_rows(input_paths["phase31_delta_csv"])
    phase32_summary = read_json(input_paths["phase32_design_summary"])
    _phase31_summary = read_json(input_paths["phase31_masked_summary"])

    lookup = metric_lookup(delta_rows)
    criteria_rows = build_readiness_criteria(stop_go_rows, guardrail_rows, texts)
    option_rows = build_pilot_options(lookup, criteria_rows)
    decision, recommended_option, training_authorized = decide(
        criteria_rows, option_rows, stop_go_rows
    )

    output_dir = repo_path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    write_csv(output_dir / "pilot_option_scores.csv", PILOT_OPTION_COLUMNS, option_rows)
    write_csv(
        output_dir / "readiness_criteria_status.csv",
        READINESS_COLUMNS,
        criteria_rows,
    )
    summary = write_summary_json(
        output_dir / "phase33_readiness_summary.json",
        input_paths,
        texts,
        phase32_summary,
        guardrail_rows,
        stop_go_rows,
        delta_rows,
        criteria_rows,
        option_rows,
        decision,
        recommended_option,
        training_authorized,
    )
    write_markdown_summary(
        output_dir / "phase33_readiness_summary.md",
        input_paths,
        option_rows,
        criteria_rows,
        decision,
        recommended_option,
        training_authorized,
    )

    print(f"pilot options evaluated: {summary['pilot_options_evaluated']}")
    print(f"readiness criteria evaluated: {summary['readiness_criteria_evaluated']}")
    print(f"recommended option: {summary['recommended_option']}")
    print(f"final decision: {summary['final_decision']}")
    print(f"training authorized: {str(summary['training_authorized']).lower()}")


if __name__ == "__main__":
    main()
