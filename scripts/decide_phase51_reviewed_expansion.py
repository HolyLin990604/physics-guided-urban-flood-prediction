from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = Path("analysis/phase51_reviewed_expansion_decision")

INPUTS = {
    "phase51_plan": Path("docs/phase51_reviewed_expansion_decision_plan.md"),
    "phase50_synthesis": Path(
        "analysis/phase50_framework_consolidation/phase50_framework_synthesis.json"
    ),
    "phase50_next_steps": Path(
        "analysis/phase50_framework_consolidation/phase50_recommended_next_steps.csv"
    ),
    "phase47_training_summary": Path(
        "analysis/phase47_controlled_downsample_baseline/"
        "phase47_training_summary.json"
    ),
    "phase48_reliability_summary": Path(
        "analysis/phase48_full_dataset_reliability_physical_proxy/"
        "phase48_reliability_summary.json"
    ),
    "phase49_warning_summary": Path(
        "analysis/phase49_full_dataset_warning_framework/"
        "warning_framework_summary.json"
    ),
}

SELECTED_DECISION = "phase51_authorize_128x128_seed42_longer_run"
DEFER_DECISION = "phase51_defer_expansion"
AUTHORIZED_NEXT_PHASE = "phase52_controlled_128x128_seed42_longer_run_baseline"

OPTION_COLUMNS = [
    "option_id",
    "option_name",
    "description",
    "scientific_value",
    "implementation_risk",
    "compute_cost",
    "continuity_with_phase47",
    "diagnostic_alignment",
    "claim_boundary_safety",
    "recommendation",
    "rationale",
]

RISK_COLUMNS = [
    "risk_item",
    "affected_options",
    "risk_level",
    "mitigation",
    "decision_impact",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Synthesize the no-training Phase 51 reviewed expansion decision from "
            "Phase 47-50 evidence. This script writes decision artifacts only and "
            "does not train, run seeds, change resolution, sweep, or modify the "
            "model, loss, configuration, or architecture."
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
        return str(path.resolve()).replace("\\", "/")


def bool_text(value: bool) -> str:
    return str(bool(value)).lower()


def read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Expected a JSON object: {display_path(path)}")
    return data


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(
    path: Path, rows: list[dict[str, Any]], columns: list[str]
) -> None:
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
    missing = [display_path(path) for path in paths.values() if not path.is_file()]
    if missing:
        raise FileNotFoundError(
            "Missing required Phase 51 input(s): " + ", ".join(missing)
        )
    return paths


def collect_evidence(paths: dict[str, Path]) -> dict[str, Any]:
    phase50 = read_json(paths["phase50_synthesis"])
    phase47 = read_json(paths["phase47_training_summary"])
    phase48 = read_json(paths["phase48_reliability_summary"])
    phase49 = read_json(paths["phase49_warning_summary"])
    next_steps = read_csv_rows(paths["phase50_next_steps"])
    plan_text = paths["phase51_plan"].read_text(encoding="utf-8")

    inconsistencies: list[str] = []

    expected_values = [
        (
            phase47.get("seed") == 42,
            "Phase 47 seed is not 42.",
        ),
        (
            phase47.get("resolution") == 128,
            "Phase 47 resolution is not 128.",
        ),
        (
            phase47.get("epochs") == 10,
            "Phase 47 epoch count is not the reviewed 10-epoch pilot.",
        ),
        (
            phase47.get("train_dataset", {}).get("sample_count") == 960,
            "Phase 47 train sample count is not 960.",
        ),
        (
            phase47.get("test_dataset", {}).get("sample_count") == 384,
            "Phase 47 test sample count is not 384.",
        ),
        (
            phase47.get("level5_supported") is False,
            "Phase 47 does not explicitly keep Level 5 unsupported.",
        ),
        (
            phase47.get("no_swe_pinn") is True,
            "Phase 47 does not explicitly preserve the no-SWE/PINN boundary.",
        ),
        (
            phase48.get("no_training") is True,
            "Phase 48 is not recorded as no-training.",
        ),
        (
            phase48.get("evaluated_scenarios") == 48,
            "Phase 48 evaluated scenario count is not 48.",
        ),
        (
            phase48.get("evaluated_windows") == 384,
            "Phase 48 evaluated window count is not 384.",
        ),
        (
            phase48.get("level5_supported") is False,
            "Phase 48 does not explicitly keep Level 5 unsupported.",
        ),
        (
            phase48.get("no_swe_pinn") is True,
            "Phase 48 does not explicitly preserve the no-SWE/PINN boundary.",
        ),
        (
            phase49.get("no_training") is True,
            "Phase 49 is not recorded as no-training.",
        ),
        (
            phase49.get("warning_labels_are_probabilities") is False,
            "Phase 49 warning labels are not explicitly non-probabilistic.",
        ),
        (
            phase49.get("level5_supported") is False,
            "Phase 49 does not explicitly keep Level 5 unsupported.",
        ),
        (
            phase49.get("no_swe_pinn") is True,
            "Phase 49 does not explicitly preserve the no-SWE/PINN boundary.",
        ),
        (
            phase50.get("level4_plus_route_supported") is True,
            "Phase 50 does not support the Level 4+ route.",
        ),
        (
            phase50.get("level5_supported") is False,
            "Phase 50 does not explicitly keep Level 5 unsupported.",
        ),
        (
            phase50.get("no_swe_pinn") is True,
            "Phase 50 does not explicitly preserve the no-SWE/PINN boundary.",
        ),
        (
            phase50.get("no_training") is True,
            "Phase 50 is not recorded as no-training.",
        ),
        (
            phase48.get("warning_level_counts")
            == phase49.get("warning_level_counts"),
            "Phase 48 and Phase 49 warning counts disagree.",
        ),
        (
            any(
                row.get("next_step") == "128x128 seed42 longer run review"
                and row.get("allowed") == "allowed_after_review"
                for row in next_steps
            ),
            "Phase 50 next steps do not allow a reviewed seed42 longer-run decision.",
        ),
        (
            SELECTED_DECISION in plan_text,
            "Phase 51 plan does not name the expected conservative decision.",
        ),
    ]
    inconsistencies.extend(message for passed, message in expected_values if not passed)

    return {
        "phase47": phase47,
        "phase48": phase48,
        "phase49": phase49,
        "phase50": phase50,
        "phase50_next_steps": next_steps,
        "inconsistencies": inconsistencies,
    }


def option_rows() -> list[dict[str, str]]:
    return [
        {
            "option_id": "A",
            "option_name": "128x128 seed42 longer run",
            "description": (
                "Authorize a separate Phase 52 bounded 128x128 seed42 longer run, "
                "recommended at 40 epochs, with the Phase 47 route otherwise fixed."
            ),
            "scientific_value": "high",
            "implementation_risk": "low",
            "compute_cost": "moderate_bounded",
            "continuity_with_phase47": "highest_same_seed_resolution_and_route",
            "diagnostic_alignment": "high_requires_phase48_phase49_reassessment",
            "claim_boundary_safety": "high_preserves_level4_plus",
            "recommendation": "authorize_next_phase",
            "rationale": (
                "Tests the unresolved training-horizon question while changing only "
                "the bounded epoch horizon; it is the lowest-risk training expansion."
            ),
        },
        {
            "option_id": "B",
            "option_name": "128x128 seed replication",
            "description": (
                "Run seed123 and seed202 at 128x128 after defining an adequate "
                "reviewed training horizon."
            ),
            "scientific_value": "high_after_longer_run_review",
            "implementation_risk": "moderate",
            "compute_cost": "moderate_to_high_multiple_runs",
            "continuity_with_phase47": "medium_changes_seed",
            "diagnostic_alignment": "high_but_multiplies_review_scope",
            "claim_boundary_safety": "high_if_predefined_and_bounded",
            "recommendation": "defer",
            "rationale": (
                "Replicating the 10-epoch pilot now would estimate variability around "
                "a training horizon that has not yet been reviewed as adequate."
            ),
        },
        {
            "option_id": "C",
            "option_name": "256x256 pilot",
            "description": (
                "Run a bounded higher-resolution pilot after the established "
                "128x128 route is reviewed under a longer horizon."
            ),
            "scientific_value": "medium_high",
            "implementation_risk": "moderate_to_high",
            "compute_cost": "high",
            "continuity_with_phase47": "low_changes_resolution_and_resource_profile",
            "diagnostic_alignment": "possible_but_requires_new_baseline_review",
            "claim_boundary_safety": "medium_if_strictly_bounded",
            "recommendation": "defer",
            "rationale": (
                "Phase 46 established 256x256 data-path feasibility, not training "
                "stability; changing resolution would confound the horizon review."
            ),
        },
        {
            "option_id": "D",
            "option_name": "Warning-framework case reporting / manuscript path",
            "description": (
                "Expand representative case reporting and manuscript interpretation "
                "without generating new training evidence."
            ),
            "scientific_value": "medium_high",
            "implementation_risk": "low",
            "compute_cost": "low",
            "continuity_with_phase47": "high_reporting_only",
            "diagnostic_alignment": "highest_direct_use_of_phase48_phase49",
            "claim_boundary_safety": "highest_if_labels_remain_non_probabilistic",
            "recommendation": "retain_not_next_training_step",
            "rationale": (
                "Useful for reporting and can proceed separately, but it does not "
                "resolve whether the Phase 47 route improves, plateaus, or degrades."
            ),
        },
        {
            "option_id": "E",
            "option_name": "Defer expansion",
            "description": (
                "Authorize neither training nor reporting expansion until reviewed "
                "evidence is complete and internally consistent."
            ),
            "scientific_value": "low_unless_evidence_is_inconsistent",
            "implementation_risk": "low_operational_high_stagnation",
            "compute_cost": "none",
            "continuity_with_phase47": "none",
            "diagnostic_alignment": "neutral",
            "claim_boundary_safety": "highest",
            "recommendation": "fallback_only",
            "rationale": (
                "Fail-closed fallback for missing or contradictory evidence; otherwise "
                "it leaves the main training-horizon question unanswered."
            ),
        },
    ]


def risk_rows() -> list[dict[str, str]]:
    return [
        {
            "risk_item": "longer_run_overfit_or_plateau",
            "affected_options": "A",
            "risk_level": "moderate",
            "mitigation": (
                "Fix the epoch cap at 40; retain best and final checkpoints; compare "
                "training curves and best/final metrics directly with Phase 47."
            ),
            "decision_impact": (
                "Manageable in Phase 52 and does not justify changing seed or resolution first."
            ),
        },
        {
            "risk_item": "aggregate_metrics_hide_warning_failure_modes",
            "affected_options": "A;B;C",
            "risk_level": "high",
            "mitigation": (
                "Repeat Phase 48 reliability/physical proxy diagnostics and Phase 49 "
                "warning review before considering further expansion."
            ),
            "decision_impact": "Makes diagnostic reassessment mandatory for Phase 52.",
        },
        {
            "risk_item": "seed_replication_before_protocol_review",
            "affected_options": "B",
            "risk_level": "moderate",
            "mitigation": (
                "Review the seed42 longer-run protocol first, then predefine replication "
                "seeds, stopping rules, and comparisons in a later phase."
            ),
            "decision_impact": "Defers seed123 and seed202.",
        },
        {
            "risk_item": "resolution_change_confounds_horizon_effect",
            "affected_options": "C",
            "risk_level": "high",
            "mitigation": (
                "Hold resolution at 128x128 until longer-run stability is reviewed; "
                "require a separate resource and protocol authorization for 256x256."
            ),
            "decision_impact": "Defers the 256x256 pilot.",
        },
        {
            "risk_item": "case_reporting_does_not_add_training_evidence",
            "affected_options": "D",
            "risk_level": "low",
            "mitigation": (
                "Retain case reporting as a parallel manuscript path while Phase 52 "
                "addresses the controlled training-horizon question."
            ),
            "decision_impact": "Keeps D useful but not the next training step.",
        },
        {
            "risk_item": "claim_escalation_from_improved_metrics",
            "affected_options": "A;B;C;D",
            "risk_level": "high",
            "mitigation": (
                "Preserve Level 4+ wording; prohibit Level 5, SWE/PINN, strict/full mass "
                "conservation, hydrodynamic closure, calibrated warning probability, "
                "and production-readiness claims."
            ),
            "decision_impact": "Applies non-negotiable claim guardrails.",
        },
        {
            "risk_item": "uncontrolled_scope_or_artifact_overwrite",
            "affected_options": "A;B;C",
            "risk_level": "high",
            "mitigation": (
                "Use a separate Phase 52 config, script, output directory, checkpoint "
                "policy, resource limit, stop criteria, and direct Phase 47 comparison."
            ),
            "decision_impact": (
                "Authorizes only a separately reviewed bounded Phase 52 implementation."
            ),
        },
    ]


def build_decision(
    paths: dict[str, Path], evidence: dict[str, Any]
) -> dict[str, Any]:
    evidence_ok = not evidence["inconsistencies"]
    selected = SELECTED_DECISION if evidence_ok else DEFER_DECISION
    authorized_phase = AUTHORIZED_NEXT_PHASE if evidence_ok else None
    authorized_scope = (
        {
            "phase51_training_authorized": False,
            "future_phase_only": True,
            "resolution": 128,
            "seed": 42,
            "reference_epochs": 10,
            "target_epochs": 40,
            "model_loss_config_architecture_unchanged": True,
            "train_test_split_unchanged": True,
            "separate_non_overwriting_output_required": True,
            "phase47_comparison_required": True,
            "phase48_phase49_diagnostic_review_required": True,
        }
        if evidence_ok
        else {
            "phase51_training_authorized": False,
            "future_phase_only": False,
            "reason": "Required evidence is missing or inconsistent.",
        }
    )

    return {
        "phase": 51,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "script": "scripts/decide_phase51_reviewed_expansion.py",
        "selected_decision": selected,
        "authorized_next_phase": authorized_phase,
        "authorized_training_scope": authorized_scope,
        "deferred_options": [
            "phase51_authorize_128x128_seed_replication",
            "phase51_authorize_256x256_pilot",
            "phase51_defer_training_for_case_reporting_as_next_training_step",
            "tile_training",
            "multiscale_training",
            "full_500x500_training",
            "hyperparameter_or_architecture_sweeps",
            "new_loss_design",
            "swe_residual_implementation",
            "pinn_implementation",
        ],
        "no_training_in_phase51": True,
        "level4_plus_route_supported": evidence_ok,
        "level5_supported": False,
        "no_swe_pinn": True,
        "no_uncontrolled_expansion": True,
        "next_recommended_action": (
            "Create Phase 52 as a controlled 128x128 seed42 40-epoch longer-run "
            "baseline with unchanged model/loss/config architecture, non-overwriting "
            "outputs, direct Phase 47 comparison, and Phase 48/49 diagnostic review."
            if evidence_ok
            else "Resolve the listed evidence inconsistencies before authorizing expansion."
        ),
        "evidence_review_passed": evidence_ok,
        "evidence_inconsistencies": evidence["inconsistencies"],
        "input_sources": {name: display_path(path) for name, path in paths.items()},
        "claim_guardrails": {
            "strict_conservation_supported": False,
            "full_mass_conservation_supported": False,
            "hydrodynamic_closure_supported": False,
            "warning_labels_are_probabilities": False,
            "production_readiness_supported": False,
        },
    }


def write_markdown(path: Path, decision: dict[str, Any]) -> None:
    selected = decision["selected_decision"]
    deferred = "\n".join(f"- `{item}`" for item in decision["deferred_options"])
    inconsistencies = decision["evidence_inconsistencies"]
    inconsistency_section = ""
    if inconsistencies:
        bullets = "\n".join(f"- {item}" for item in inconsistencies)
        inconsistency_section = (
            "\n## Evidence Inconsistencies\n\n"
            f"{bullets}\n"
        )

    text = (
        "# Phase 51 Reviewed Expansion Decision\n\n"
        "Phase 51 is decision synthesis only. It performs no training and creates "
        "no model checkpoint or new performance result.\n\n"
        "## Selected Decision\n\n"
        f"`{selected}`\n\n"
        f"- Authorized next phase: `{decision['authorized_next_phase']}`\n"
        f"- No training in Phase 51: `{bool_text(decision['no_training_in_phase51'])}`\n"
        f"- Level 4+ route supported: `{bool_text(decision['level4_plus_route_supported'])}`\n"
        f"- Level 5 supported: `{bool_text(decision['level5_supported'])}`\n"
        f"- No SWE/PINN: `{bool_text(decision['no_swe_pinn'])}`\n"
        f"- No uncontrolled expansion: `{bool_text(decision['no_uncontrolled_expansion'])}`\n\n"
        "## Why Option A Is Authorized\n\n"
        "Phase 47 is the only route with completed training evidence: one controlled "
        "128x128 seed42 10-epoch pilot. A bounded longer seed42 run changes only the "
        "training horizon and directly tests whether the established route improves, "
        "plateaus, overfits, or degrades. It is lower risk than changing seed, "
        "resolution, model, loss, or architecture.\n\n"
        "Authorization applies only to a separate Phase 52 controlled baseline, "
        "recommended at 40 epochs. Phase 51 does not run seed42.\n\n"
        "## Why Options B and C Are Deferred\n\n"
        "Seed123 and seed202 are deferred because replicating an unreviewed short-horizon "
        "protocol would multiply compute before the baseline duration is established. "
        "The 256x256 pilot is deferred because Phase 46 proved data-path feasibility, "
        "not training stability, and a resolution change would confound the training-horizon review.\n\n"
        "## Why Option D Remains Useful\n\n"
        "Warning-framework case reporting and manuscript development remain valid "
        "low-risk work. They directly use Phase 48/49 diagnostics, but they are not "
        "the next training step because they do not resolve longer-run baseline behavior. "
        "Warning labels must remain conservative screening labels, not calibrated probabilities.\n\n"
        "## Deferred Options\n\n"
        f"{deferred}\n\n"
        "## Guardrails\n\n"
        "- Do not train in Phase 51.\n"
        "- Do not run seed42, seed123, or seed202 in Phase 51.\n"
        "- Do not run 256x256, tile, multiscale, or full 500x500 training.\n"
        "- Do not run sweeps or modify model, loss, config, or architecture.\n"
        "- Do not implement SWE residuals or PINN components.\n"
        "- Do not claim Level 5, strict conservation, full mass conservation, or hydrodynamic closure.\n"
        "- Do not claim calibrated probability warning labels or production readiness.\n"
        "- Do not authorize uncontrolled training expansion.\n"
        "- Require separate outputs, bounded resources, checkpoint retention, stop criteria, and direct Phase 47 comparison in Phase 52.\n\n"
        "## Next Phase\n\n"
        "The next phase should be **Phase 52 controlled 128x128 seed42 longer-run "
        "baseline**, with a recommended 40-epoch cap and unchanged Level 4+ claim boundary.\n"
        f"{inconsistency_section}"
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def main() -> int:
    args = parse_args()
    paths = require_inputs()
    evidence = collect_evidence(paths)
    decision = build_decision(paths, evidence)

    output_dir = repo_path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    write_csv(
        output_dir / "phase51_expansion_option_matrix.csv",
        option_rows(),
        OPTION_COLUMNS,
    )
    write_csv(
        output_dir / "phase51_risk_assessment.csv",
        risk_rows(),
        RISK_COLUMNS,
    )
    write_json(
        output_dir / "phase51_selected_decision.json",
        decision,
    )
    write_markdown(
        output_dir / "phase51_selected_decision.md",
        decision,
    )

    print(f"selected_decision={decision['selected_decision']}")
    print(f"authorized_next_phase={decision['authorized_next_phase']}")
    print(
        "no_training_in_phase51="
        f"{bool_text(decision['no_training_in_phase51'])}"
    )
    print(f"level5_supported={bool_text(decision['level5_supported'])}")
    print(f"no_swe_pinn={bool_text(decision['no_swe_pinn'])}")
    print(
        "no_uncontrolled_expansion="
        f"{bool_text(decision['no_uncontrolled_expansion'])}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
