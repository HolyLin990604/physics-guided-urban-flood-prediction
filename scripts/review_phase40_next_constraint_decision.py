from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = Path("analysis/phase40_failed_pilot_design_review")

INPUTS = {
    "phase40_plan": Path(
        "docs/phase40_failed_pilot_design_review_next_constraint_plan.md"
    ),
    "phase39_findings": Path(
        "docs/phase39_failed_pilot_tradeoff_diagnosis_findings.md"
    ),
    "phase39_summary_json": Path(
        "analysis/phase39_failed_pilot_tradeoff_diagnosis/"
        "phase39_tradeoff_diagnosis_summary.json"
    ),
    "phase39_summary_md": Path(
        "analysis/phase39_failed_pilot_tradeoff_diagnosis/"
        "phase39_tradeoff_diagnosis_summary.md"
    ),
    "failed_acceptance_components": Path(
        "analysis/phase39_failed_pilot_tradeoff_diagnosis/"
        "failed_acceptance_components.csv"
    ),
    "triggered_rejection_rules": Path(
        "analysis/phase39_failed_pilot_tradeoff_diagnosis/"
        "triggered_rejection_rules.csv"
    ),
    "phase38_vs_baselines_metric_comparison": Path(
        "analysis/phase39_failed_pilot_tradeoff_diagnosis/"
        "phase38_vs_baselines_metric_comparison.csv"
    ),
    "region_tradeoff_summary": Path(
        "analysis/phase39_failed_pilot_tradeoff_diagnosis/"
        "region_tradeoff_summary.csv"
    ),
    "phase38_decision_json": Path(
        "analysis/phase38_seed42_pilot_training_guardrail_evaluation/"
        "phase38_guardrail_decision.json"
    ),
    "phase38_decision_md": Path(
        "analysis/phase38_seed42_pilot_training_guardrail_evaluation/"
        "phase38_guardrail_decision.md"
    ),
}

OPTION_IDS = (
    "redesign_level4_proxy_constraint_plan_first",
    "pause_loss_redesign_move_to_swe_data_readiness",
    "consolidate_negative_result_no_new_training",
    "decision_deferred_pending_more_evidence",
)

OPTION_LABELS = {
    "redesign_level4_proxy_constraint_plan_first": "Redesign Level 4+ proxy constraint plan-first",
    "pause_loss_redesign_move_to_swe_data_readiness": "Pause proxy-loss redesign and move to SWE data readiness",
    "consolidate_negative_result_no_new_training": "Consolidate negative result with no new training",
    "decision_deferred_pending_more_evidence": "Defer decision pending more evidence",
}

CRITERIA = (
    "respects_phase38_rejection",
    "avoids_seed_expansion",
    "avoids_sweep",
    "avoids_posthoc_rescue",
    "addresses_phase29_like_tradeoff",
    "reduces_risk_of_narrow_proxy_error_transfer",
    "advances_toward_level5",
    "requires_new_data",
    "requires_training_now",
    "preserves_level4_plus_scope",
    "scientific_value",
    "implementation_risk",
    "recommended_priority",
)

SWE_READINESS_DATA_NEEDS = (
    "velocity_or_flux_fields",
    "dx_dy_grid_spacing",
    "dt_time_step",
    "boundary_conditions",
    "source_sink_terms",
    "pump_gate_operations",
    "hydrodynamic_state_variables",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Phase 40 diagnostic/design-review decision script. This script reads "
            "existing Phase 38 and Phase 39 artifacts only. It does not train, "
            "rerun seed42, run seed123/seed202, sweep, modify losses/configs/model "
            "architecture, continue Phase 29, or rescue Phase 38."
        )
    )
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    return parser.parse_args()


def repo_path(path: Path) -> Path:
    return path if path.is_absolute() else REPO_ROOT / path


def display_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT)).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, Any]], columns: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def require_inputs() -> dict[str, Path]:
    paths = {name: repo_path(path) for name, path in INPUTS.items()}
    missing = [display_path(path) for path in paths.values() if not path.exists()]
    if missing:
        raise FileNotFoundError("Missing required Phase 40 input(s): " + ", ".join(missing))
    return paths


def collect_evidence(paths: dict[str, Path]) -> dict[str, Any]:
    phase38 = read_json(paths["phase38_decision_json"])
    phase39 = read_json(paths["phase39_summary_json"])
    failed_acceptance = read_csv_rows(paths["failed_acceptance_components"])
    triggered_rules = read_csv_rows(paths["triggered_rejection_rules"])
    comparison = read_csv_rows(paths["phase38_vs_baselines_metric_comparison"])
    region_rows = read_csv_rows(paths["region_tradeoff_summary"])
    plan_text = read_text(paths["phase40_plan"])
    findings_text = read_text(paths["phase39_findings"])
    phase39_md = read_text(paths["phase39_summary_md"])
    phase38_md = read_text(paths["phase38_decision_md"])

    triggered_ids = {
        row.get("rejection_id", "")
        for row in triggered_rules
        if row.get("status") == "triggered"
    }
    failed_ids = {
        row.get("acceptance_id", "")
        for row in failed_acceptance
        if row.get("status") == "fail"
    }
    region_tradeoff_regions = {
        row.get("region", "")
        for row in region_rows
        if row.get("supports_localized_target_improvement_vs_broader_degradation")
        == "yes"
    }
    target_improved = any(
        row.get("tradeoff_flag") == "target_metric_improved_vs_phase27_and_phase29"
        for row in comparison
    )

    contradiction_reasons: list[str] = []
    if phase38.get("final_decision") != "seed42_pilot_rejected":
        contradiction_reasons.append(
            f"Phase38 JSON final_decision is {phase38.get('final_decision')!r}."
        )
    if phase39.get("final_decision") != "seed42_pilot_rejected":
        contradiction_reasons.append(
            f"Phase39 JSON final_decision is {phase39.get('final_decision')!r}."
        )
    if "RT01" not in triggered_ids:
        contradiction_reasons.append("RT01 phase29_tradeoff_pattern is not triggered.")
    if not {"AT02", "AT03", "AT04", "AT06", "AT07", "AT08", "AT09", "AT10"}.issubset(
        failed_ids
    ):
        contradiction_reasons.append(
            "Expected broad failed acceptance components are incomplete."
        )

    combined_text = "\n".join([plan_text, findings_text, phase39_md, phase38_md]).lower()
    wording_checks = {
        "contains_seed42_pilot_rejected": "seed42_pilot_rejected" in combined_text,
        "contains_no_training_guardrail": "no training" in combined_text
        or "does not train" in combined_text,
        "contains_no_swe_claim_boundary": "swe/pinn" in combined_text
        and "hydrodynamic closure" in combined_text,
        "contains_level4_plus": "level 4+" in combined_text,
    }

    return {
        "phase38": phase38,
        "phase39": phase39,
        "failed_acceptance": failed_acceptance,
        "triggered_rules": triggered_rules,
        "comparison": comparison,
        "region_rows": region_rows,
        "triggered_ids": sorted(triggered_ids),
        "failed_ids": sorted(failed_ids),
        "region_tradeoff_regions": sorted(region_tradeoff_regions),
        "target_improved": target_improved,
        "contradiction_reasons": contradiction_reasons,
        "wording_checks": wording_checks,
    }


def option_rows() -> list[dict[str, Any]]:
    return [
        {
            "option_id": "A",
            "option_name": OPTION_LABELS["redesign_level4_proxy_constraint_plan_first"],
            "decision_candidate": "redesign_level4_proxy_constraint_plan_first",
            "description": (
                "Plan a redesigned Level 4+ proxy constraint before any implementation, "
                "with domain-balanced, boundary-aware, false-dry/false-wet paired checks."
            ),
            "addresses_phase38_phase39_tradeoff": "yes_if_plan_addresses_all_failed_regions",
            "avoids_narrow_region_error_transfer": "partial_until_redesign_reviewed",
            "requires_future_training": "possible_later_not_authorized_now",
            "requires_loss_change": "possible_later_not_authorized_now",
            "requires_config_change": "possible_later_not_authorized_now",
            "allowed_in_phase40": "review_only",
            "notes": (
                "Viable only as a plan-first direction; no weight increase, loss edit, "
                "config edit, architecture edit, seed expansion, sweep, or Phase38 rescue."
            ),
        },
        {
            "option_id": "B",
            "option_name": OPTION_LABELS["pause_loss_redesign_move_to_swe_data_readiness"],
            "decision_candidate": "pause_loss_redesign_move_to_swe_data_readiness",
            "description": (
                "Pause proxy-loss redesign and audit data readiness for future residual-style "
                "physical constraints without claiming SWE/PINN behavior."
            ),
            "addresses_phase38_phase39_tradeoff": "yes",
            "avoids_narrow_region_error_transfer": "yes",
            "requires_future_training": "no_for_next_readiness_phase",
            "requires_loss_change": "no",
            "requires_config_change": "no",
            "allowed_in_phase40": "review_only",
            "notes": (
                "Conservative pivot to data-readiness evidence after repeated proxy-loss "
                "trade-off limitations."
            ),
        },
        {
            "option_id": "C",
            "option_name": OPTION_LABELS["consolidate_negative_result_no_new_training"],
            "decision_candidate": "consolidate_negative_result_no_new_training",
            "description": (
                "Document Phase 38-39 as a useful negative result and avoid a new constraint."
            ),
            "addresses_phase38_phase39_tradeoff": "yes_as_documentation",
            "avoids_narrow_region_error_transfer": "yes_by_not_adding_constraint",
            "requires_future_training": "no",
            "requires_loss_change": "no",
            "requires_config_change": "no",
            "allowed_in_phase40": "review_only",
            "notes": (
                "Scientifically valid if no immediate new direction is justified, but it "
                "does not advance the project toward richer physical evidence."
            ),
        },
        {
            "option_id": "D",
            "option_name": OPTION_LABELS["decision_deferred_pending_more_evidence"],
            "decision_candidate": "decision_deferred_pending_more_evidence",
            "description": (
                "Defer the next-direction decision if required evidence is missing or "
                "contradictory."
            ),
            "addresses_phase38_phase39_tradeoff": "partial",
            "avoids_narrow_region_error_transfer": "partial",
            "requires_future_training": "no",
            "requires_loss_change": "no",
            "requires_config_change": "no",
            "allowed_in_phase40": "fallback_only",
            "notes": "Used only for missing or contradictory required evidence.",
        },
    ]


def build_criteria_values(evidence_ok: bool) -> dict[str, dict[str, str]]:
    values = {
        "redesign_level4_proxy_constraint_plan_first": {
            "respects_phase38_rejection": "yes",
            "avoids_seed_expansion": "yes",
            "avoids_sweep": "yes",
            "avoids_posthoc_rescue": "yes",
            "addresses_phase29_like_tradeoff": "yes",
            "reduces_risk_of_narrow_proxy_error_transfer": "partial",
            "advances_toward_level5": "no_directly_level4_plus_only",
            "requires_new_data": "no_immediate",
            "requires_training_now": "no",
            "preserves_level4_plus_scope": "yes",
            "scientific_value": "medium",
            "implementation_risk": "medium",
            "recommended_priority": "medium_low",
        },
        "pause_loss_redesign_move_to_swe_data_readiness": {
            "respects_phase38_rejection": "yes",
            "avoids_seed_expansion": "yes",
            "avoids_sweep": "yes",
            "avoids_posthoc_rescue": "yes",
            "addresses_phase29_like_tradeoff": "yes",
            "reduces_risk_of_narrow_proxy_error_transfer": "yes",
            "advances_toward_level5": "yes_data_readiness_only",
            "requires_new_data": "yes_audit_availability",
            "requires_training_now": "no",
            "preserves_level4_plus_scope": "yes_no_swe_claim",
            "scientific_value": "high",
            "implementation_risk": "low_medium",
            "recommended_priority": "high",
        },
        "consolidate_negative_result_no_new_training": {
            "respects_phase38_rejection": "yes",
            "avoids_seed_expansion": "yes",
            "avoids_sweep": "yes",
            "avoids_posthoc_rescue": "yes",
            "addresses_phase29_like_tradeoff": "yes_as_negative_evidence",
            "reduces_risk_of_narrow_proxy_error_transfer": "yes_by_stopping",
            "advances_toward_level5": "no",
            "requires_new_data": "no",
            "requires_training_now": "no",
            "preserves_level4_plus_scope": "yes",
            "scientific_value": "medium_high",
            "implementation_risk": "low",
            "recommended_priority": "medium",
        },
        "decision_deferred_pending_more_evidence": {
            "respects_phase38_rejection": "yes_if_deferred",
            "avoids_seed_expansion": "yes",
            "avoids_sweep": "yes",
            "avoids_posthoc_rescue": "yes",
            "addresses_phase29_like_tradeoff": "partial",
            "reduces_risk_of_narrow_proxy_error_transfer": "partial",
            "advances_toward_level5": "no",
            "requires_new_data": "unknown",
            "requires_training_now": "no",
            "preserves_level4_plus_scope": "yes",
            "scientific_value": "low_unless_inputs_contradict",
            "implementation_risk": "low",
            "recommended_priority": "low",
        },
    }
    if not evidence_ok:
        values["decision_deferred_pending_more_evidence"]["recommended_priority"] = "high"
        values["decision_deferred_pending_more_evidence"][
            "scientific_value"
        ] = "high_fail_closed"
    return values


def criterion_source_and_note(criterion: str) -> tuple[str, str]:
    sources = {
        "respects_phase38_rejection": (
            "phase38_guardrail_decision.json; phase39_tradeoff_diagnosis_summary.json",
            "Phase38 remains seed42_pilot_rejected.",
        ),
        "avoids_seed_expansion": (
            "Phase40 plan; Phase39 guardrails",
            "seed123 and seed202 remain unauthorized.",
        ),
        "avoids_sweep": (
            "Phase40 plan; Phase39 guardrails",
            "Sweeps remain unauthorized.",
        ),
        "avoids_posthoc_rescue": (
            "Phase40 plan; triggered rejection rules",
            "The Phase38 result cannot be relabeled, rescued, or accepted post hoc.",
        ),
        "addresses_phase29_like_tradeoff": (
            "triggered_rejection_rules.csv",
            "RT01 identifies a Phase29-like trade-off pattern.",
        ),
        "reduces_risk_of_narrow_proxy_error_transfer": (
            "failed_acceptance_components.csv; region_tradeoff_summary.csv",
            "The narrow target proxy improved while valid-domain, boundary, high-impervious, and standard checks failed.",
        ),
        "advances_toward_level5": (
            "Phase40 plan",
            "Only data-readiness work can move toward future residual constraints, without claiming Level 5 support.",
        ),
        "requires_new_data": (
            "Phase40 plan",
            "SWE-readiness means checking availability, not implementing residuals.",
        ),
        "requires_training_now": (
            "Phase40 guardrails",
            "All acceptable Phase40 decisions block immediate training.",
        ),
        "preserves_level4_plus_scope": (
            "Phase38/39/40 claim-boundary text",
            "No strict conservation, full mass conservation, SWE/PINN, hydrodynamic closure, or Level 5 claim is allowed.",
        ),
        "scientific_value": (
            "Phase39 diagnosis",
            "Scientific value is highest when the next step uses the negative evidence to reduce repeated proxy trade-off risk.",
        ),
        "implementation_risk": (
            "Phase40 option review",
            "Risk is lower when the next phase is audit/documentation rather than implementation.",
        ),
        "recommended_priority": (
            "computed decision matrix",
            "Priority reflects conservative decision policy and available evidence.",
        ),
    }
    return sources[criterion]


def build_criteria_matrix(evidence_ok: bool) -> list[dict[str, Any]]:
    values = build_criteria_values(evidence_ok)
    rows: list[dict[str, Any]] = []
    for idx, criterion in enumerate(CRITERIA, start=1):
        source, note = criterion_source_and_note(criterion)
        rows.append(
            {
                "criterion_id": f"DC{idx:02d}",
                "criterion": criterion,
                "option_a_redesign_level4_proxy": values[
                    "redesign_level4_proxy_constraint_plan_first"
                ][criterion],
                "option_b_swe_data_readiness": values[
                    "pause_loss_redesign_move_to_swe_data_readiness"
                ][criterion],
                "option_c_consolidate_negative_result": values[
                    "consolidate_negative_result_no_new_training"
                ][criterion],
                "option_d_decision_deferred": values[
                    "decision_deferred_pending_more_evidence"
                ][criterion],
                "evidence_source": source,
                "review_note": note,
            }
        )
    return rows


def score_options(evidence_ok: bool) -> dict[str, int]:
    if not evidence_ok:
        return {
            "redesign_level4_proxy_constraint_plan_first": 0,
            "pause_loss_redesign_move_to_swe_data_readiness": 0,
            "consolidate_negative_result_no_new_training": 0,
            "decision_deferred_pending_more_evidence": 100,
        }
    return {
        "redesign_level4_proxy_constraint_plan_first": 60,
        "pause_loss_redesign_move_to_swe_data_readiness": 88,
        "consolidate_negative_result_no_new_training": 76,
        "decision_deferred_pending_more_evidence": 35,
    }


def decide(evidence: dict[str, Any]) -> tuple[str, dict[str, int], list[str]]:
    evidence_ok = not evidence["contradiction_reasons"]
    scores = score_options(evidence_ok)
    selected = max(scores, key=scores.get)
    rationale = [
        "Phase38 remains seed42_pilot_rejected.",
        "Phase39 diagnosed a Phase29-like trade-off pattern through RT01.",
        (
            "The manhole_nonzero_false_dry_guardrail improved a narrow target proxy "
            "but failed broader valid-domain, regional guardrail, and standard checks."
        ),
        (
            "Immediate seed expansion, sweeps, and Phase38 rescue are blocked because "
            "they would reinterpret a rejected pilot rather than address the diagnosed mechanism."
        ),
    ]
    if selected == "pause_loss_redesign_move_to_swe_data_readiness":
        rationale.append(
            "The highest-priority conservative direction is a no-training data-readiness "
            "audit for future residual-style physical constraints."
        )
    if evidence["contradiction_reasons"]:
        rationale.append(
            "Required evidence was missing or contradictory, so the decision fails closed."
        )
    return selected, scores, rationale


def build_summary(
    paths: dict[str, Path],
    evidence: dict[str, Any],
    selected: str,
    scores: dict[str, int],
    rationale: list[str],
) -> dict[str, Any]:
    return {
        "phase": 40,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "script": "scripts/review_phase40_next_constraint_decision.py",
        "phase38_decision": "seed42_pilot_rejected",
        "phase38_recorded_final_decision": evidence["phase38"].get("final_decision"),
        "phase39_interpretation": (
            "Phase29-like trade-off: narrow manhole_nonzero false-dry proxy "
            "improved while broader valid-domain, regional guardrail, and standard "
            "checks failed."
        ),
        "phase39_recorded_decision": evidence["phase39"].get("phase39_decision"),
        "final_decision_candidate": selected,
        "training_authorized": False,
        "seed42_rerun_authorized": False,
        "seed123_authorized": False,
        "seed202_authorized": False,
        "sweep_authorized": False,
        "phase29_continuation_authorized": False,
        "phase38_rescue_authorized": False,
        "pilot_success_claim_authorized": False,
        "loss_edit_authorized": False,
        "config_edit_authorized": False,
        "model_architecture_edit_authorized": False,
        "strict_conservation_claim_authorized": False,
        "full_mass_conservation_claim_authorized": False,
        "swe_claim_authorized": False,
        "hydrodynamic_closure_claim_authorized": False,
        "level5_claim_authorized": False,
        "required_next_phase": (
            "phase41_swe_data_readiness_audit"
            if selected == "pause_loss_redesign_move_to_swe_data_readiness"
            else "phase41_next_constraint_planning_or_consolidation"
        ),
        "next_recommended_phase": (
            "SWE data-readiness audit only: check velocity/flux, dx/dy, dt, "
            "boundary/source-sink, pump/gate operations, and hydrodynamic state "
            "variable availability without SWE/PINN or Level 5 claims."
        ),
        "decision_rationale": rationale,
        "option_scores": scores,
        "options_evaluated": len(OPTION_IDS),
        "criteria_rows": len(CRITERIA),
        "failed_acceptance_count": len(evidence["failed_acceptance"]),
        "triggered_rejection_count": len(evidence["triggered_rules"]),
        "triggered_rejection_ids": evidence["triggered_ids"],
        "failed_acceptance_ids": evidence["failed_ids"],
        "region_tradeoff_regions": evidence["region_tradeoff_regions"],
        "target_proxy_improved": evidence["target_improved"],
        "swe_readiness_data_needs": list(SWE_READINESS_DATA_NEEDS),
        "evidence_contradictions": evidence["contradiction_reasons"],
        "wording_checks": evidence["wording_checks"],
        "input_sources": {name: display_path(path) for name, path in paths.items()},
        "level_boundary": (
            "Phase40 remains Level 4+ diagnostic/design review. It makes no strict "
            "conservation, full mass conservation, SWE/PINN, hydrodynamic closure, "
            "Level 5 support, or pilot success claim."
        ),
    }


def write_markdown(path: Path, summary: dict[str, Any], matrix: list[dict[str, Any]]) -> None:
    lines = [
        "# Phase 40 Next Constraint Decision",
        "",
        "This is a diagnostic/design-review artifact only. It does not train, rerun seed42, run seed123 or seed202, sweep, modify losses, modify configs, modify model architecture, continue Phase 29, or rescue Phase 38.",
        "",
        "## Final Phase38 Status",
        "",
        f"- Phase38 recorded final decision: `{summary['phase38_recorded_final_decision']}`",
        "- Phase40 preserves this as `seed42_pilot_rejected`.",
        "- No pilot success claim is made.",
        "",
        "## Phase39 Diagnosis",
        "",
        "- Phase39 diagnosed a Phase29-like trade-off pattern.",
        "- `manhole_nonzero_false_dry_guardrail` improved a narrow target proxy but failed broader valid-domain, regional guardrail, and standard checks.",
        f"- Failed acceptance components: `{summary['failed_acceptance_count']}`.",
        f"- Triggered rejection rules: `{', '.join(summary['triggered_rejection_ids'])}`.",
        "",
        "## Option Comparison",
        "",
        "| Option | Score | Priority | Summary |",
        "| --- | ---: | --- | --- |",
    ]
    option_priority = {
        row["criterion"]: row
        for row in matrix
        if row["criterion"] == "recommended_priority"
    }["recommended_priority"]
    priority_by_option = {
        "redesign_level4_proxy_constraint_plan_first": option_priority[
            "option_a_redesign_level4_proxy"
        ],
        "pause_loss_redesign_move_to_swe_data_readiness": option_priority[
            "option_b_swe_data_readiness"
        ],
        "consolidate_negative_result_no_new_training": option_priority[
            "option_c_consolidate_negative_result"
        ],
        "decision_deferred_pending_more_evidence": option_priority[
            "option_d_decision_deferred"
        ],
    }
    summaries = {
        "redesign_level4_proxy_constraint_plan_first": (
            "Possible only as a future plan-first redesign that explicitly avoids narrow-region error transfer."
        ),
        "pause_loss_redesign_move_to_swe_data_readiness": (
            "Conservative no-training pivot to audit data needed for future residual-style constraints."
        ),
        "consolidate_negative_result_no_new_training": (
            "Valid negative-result consolidation with no new constraint or training."
        ),
        "decision_deferred_pending_more_evidence": (
            "Fail-closed fallback if required evidence is missing or contradictory."
        ),
    }
    for option in OPTION_IDS:
        lines.append(
            f"| `{option}` | {summary['option_scores'][option]} | "
            f"{priority_by_option[option]} | {summaries[option]} |"
        )

    lines.extend(
        [
            "",
            "## Selected Decision",
            "",
            f"`{summary['final_decision_candidate']}`",
            "",
            "Rationale:",
        ]
    )
    lines.extend(f"- {item}" for item in summary["decision_rationale"])
    lines.extend(
        [
            "",
            "## Why Direct Training Is Blocked",
            "",
            "- Phase38 is rejected under predeclared guardrails.",
            "- Phase39 found the failure mechanism is not solved by the narrow target proxy.",
            "- Phase40 is review-only and authorizes no training, no loss edit, no config edit, and no architecture edit.",
            "",
            "## Why Seed Expansion, Sweep, and Rescue Are Blocked",
            "",
            "- `seed123` and `seed202` would expand a rejected pilot rather than address the diagnosed trade-off.",
            "- Sweeps would search around a rejected proxy design and risk post-hoc rescue.",
            "- Phase38 cannot be relabeled as successful or mixed-positive after failed acceptance checks and triggered rejection rules.",
            "",
            "## Recommended Next Phase",
            "",
            f"`{summary['required_next_phase']}`",
            "",
            "The next phase should audit availability of:",
        ]
    )
    lines.extend(f"- `{item}`" for item in summary["swe_readiness_data_needs"])
    lines.extend(
        [
            "",
            "This audit must not implement SWE residuals, train a model, or claim SWE/PINN behavior.",
            "",
            "## Level Boundary",
            "",
            summary["level_boundary"],
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    paths = require_inputs()
    evidence = collect_evidence(paths)
    selected, scores, rationale = decide(evidence)
    matrix = build_criteria_matrix(not evidence["contradiction_reasons"])
    options = option_rows()
    summary = build_summary(paths, evidence, selected, scores, rationale)

    output_dir = repo_path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    write_csv(
        output_dir / "next_constraint_options.csv",
        options,
        [
            "option_id",
            "option_name",
            "decision_candidate",
            "description",
            "addresses_phase38_phase39_tradeoff",
            "avoids_narrow_region_error_transfer",
            "requires_future_training",
            "requires_loss_change",
            "requires_config_change",
            "allowed_in_phase40",
            "notes",
        ],
    )
    write_csv(
        output_dir / "decision_criteria_matrix.csv",
        matrix,
        [
            "criterion_id",
            "criterion",
            "option_a_redesign_level4_proxy",
            "option_b_swe_data_readiness",
            "option_c_consolidate_negative_result",
            "option_d_decision_deferred",
            "evidence_source",
            "review_note",
        ],
    )
    write_json(output_dir / "phase40_next_constraint_decision.json", summary)
    write_markdown(output_dir / "phase40_next_constraint_decision.md", summary, matrix)

    print(f"options_evaluated={summary['options_evaluated']}")
    print(f"criteria_rows={summary['criteria_rows']}")
    print(f"selected_decision={summary['final_decision_candidate']}")
    print(f"training_authorized={str(summary['training_authorized']).lower()}")
    print(f"next_recommended_phase={summary['required_next_phase']}")


if __name__ == "__main__":
    main()
