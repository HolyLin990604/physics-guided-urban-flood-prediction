from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = Path("analysis/phase54_reviewed_seed_replication_decision")

INPUTS = {
    "phase54_plan": Path(
        "docs/phase54_reviewed_seed_replication_decision_plan.md"
    ),
    "phase52_training_summary": Path(
        "analysis/phase52_controlled_128x128_seed42_longer_run/"
        "phase52_training_summary.json"
    ),
    "phase53_diagnostics_summary": Path(
        "analysis/phase53_phase52_diagnostics_review/"
        "phase53_diagnostics_summary.json"
    ),
    "phase53_diagnostic_comparison": Path(
        "analysis/phase53_phase52_diagnostics_review/"
        "phase52_vs_phase48_diagnostic_comparison.csv"
    ),
    "phase53_warning_levels": Path(
        "analysis/phase53_phase52_diagnostics_review/"
        "reliability_warning_levels.csv"
    ),
    "phase52_findings": Path(
        "docs/phase52_controlled_128x128_seed42_longer_run_findings.md"
    ),
    "phase53_findings": Path(
        "docs/phase53_phase52_diagnostics_review_findings.md"
    ),
}

SELECTED_DECISION = "phase54_authorize_controlled_128x128_seed_replication"
DEFER_DECISION = "phase54_defer_expansion_insufficient_evidence"
AUTHORIZED_NEXT_PHASE = "phase55_controlled_128x128_seed_replication"

OPTION_COLUMNS = [
    "option_id",
    "option_name",
    "description",
    "scientific_value",
    "reproducibility_value",
    "implementation_risk",
    "compute_cost",
    "continuity_with_phase52",
    "diagnostic_support_from_phase53",
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

EXPECTED_PHASE52_METRICS = {
    "test_rmse": 0.005160715272116552,
    "test_mae": 0.002410597107882495,
    "test_wet_dry_iou": 0.9130120601863988,
    "test_rollout_stability": 0.9992842044060429,
    "test_step_rmse_std": 0.0007178322914948391,
    "test_loss": 0.0002713639403471764,
}

DEFERRED_OPTIONS = [
    "phase54_authorize_single_seed123_pilot",
    "phase54_defer_replication_for_256x256",
    "phase54_defer_training_for_reporting",
    "phase54_defer_expansion_insufficient_evidence",
    "256x256_training",
    "tile_training",
    "multiscale_training",
    "full_500x500_training",
    "seed_sweep_beyond_seed123_and_seed202",
    "hyperparameter_sweep",
    "architecture_sweep",
    "loss_redesign",
    "training_beyond_40_epochs_per_seed",
    "swe_residual_implementation",
    "pinn_implementation",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Synthesize the no-training Phase 54 reviewed seed-replication "
            "decision from completed Phase 52 training evidence and Phase 53 "
            "diagnostic evidence. This script writes decision artifacts only."
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
            "Missing required Phase 54 input(s): " + ", ".join(missing)
        )
    return paths


def values_match(actual: Any, expected: float, tolerance: float = 1e-12) -> bool:
    return isinstance(actual, (int, float)) and abs(actual - expected) <= tolerance


def collect_evidence(paths: dict[str, Path]) -> dict[str, Any]:
    phase52 = read_json(paths["phase52_training_summary"])
    phase53 = read_json(paths["phase53_diagnostics_summary"])
    comparison_rows = read_csv_rows(paths["phase53_diagnostic_comparison"])
    warning_rows = read_csv_rows(paths["phase53_warning_levels"])
    plan_text = paths["phase54_plan"].read_text(encoding="utf-8")
    phase52_findings = paths["phase52_findings"].read_text(encoding="utf-8")
    phase53_findings = paths["phase53_findings"].read_text(encoding="utf-8")

    best_metrics = phase52.get("best_epoch_metrics", {})
    phase48_counts = Counter(
        row.get("phase48_warning_level", "") for row in comparison_rows
    )
    phase53_counts = Counter(
        row.get("phase53_warning_level", "") for row in warning_rows
    )
    diagnostic_rows = (
        phase53.get("evaluated_windows", 0) * 12
        if isinstance(phase53.get("evaluated_windows"), int)
        else None
    )

    checks: list[tuple[bool, str]] = [
        (phase52.get("seed") == 42, "Phase 52 seed is not 42."),
        (phase52.get("resolution") == 128, "Phase 52 resolution is not 128."),
        (
            phase52.get("epochs_completed") == 40,
            "Phase 52 did not complete 40 epochs.",
        ),
        (
            phase52.get("epochs_configured") == 40,
            "Phase 52 configured epoch cap is not 40.",
        ),
        (phase52.get("train_samples") == 960, "Phase 52 train samples are not 960."),
        (phase52.get("test_samples") == 384, "Phase 52 test samples are not 384."),
        (phase52.get("best_epoch") == 40, "Phase 52 best epoch is not 40."),
        (
            phase52.get("level5_supported") is False,
            "Phase 52 does not explicitly keep Level 5 unsupported.",
        ),
        (
            phase52.get("no_swe_pinn") is True,
            "Phase 52 does not preserve the no-SWE/PINN boundary.",
        ),
        (
            phase53.get("diagnostics_executed") is True,
            "Phase 53 diagnostics are not recorded as executed.",
        ),
        (
            phase53.get("evaluated_scenarios") == 48,
            "Phase 53 evaluated scenario count is not 48.",
        ),
        (
            phase53.get("evaluated_windows") == 384,
            "Phase 53 evaluated window count is not 384.",
        ),
        (
            phase53.get("matched_diagnostic_comparison", {}).get(
                "matched_scenarios"
            )
            == 48,
            "Phase 53 matched comparison count is not 48.",
        ),
        (
            len(comparison_rows) == 48,
            "Phase 53 diagnostic comparison CSV does not contain 48 rows.",
        ),
        (
            len(warning_rows) == 48,
            "Phase 53 warning-level CSV does not contain 48 rows.",
        ),
        (
            diagnostic_rows == 4608,
            "Phase 53 diagnostic row count cannot be reconciled to 4,608.",
        ),
        (
            dict(phase48_counts) == {
                "reliable": 1,
                "caution": 12,
                "high-risk": 35,
            },
            "Phase 48/49 warning counts in the matched CSV are inconsistent.",
        ),
        (
            dict(phase53_counts) == {
                "reliable": 38,
                "caution": 3,
                "high-risk": 7,
            },
            "Phase 53 warning counts in the warning-level CSV are inconsistent.",
        ),
        (
            phase53.get("phase48_reference_warning_level_counts")
            == {"reliable": 1, "caution": 12, "high-risk": 35},
            "Phase 53 summary has unexpected Phase 48/49 warning counts.",
        ),
        (
            phase53.get("phase52_warning_level_counts")
            == {"reliable": 38, "caution": 3, "high-risk": 7},
            "Phase 53 summary has unexpected Phase 52/53 warning counts.",
        ),
        (
            phase53.get("no_training") is True,
            "Phase 53 is not explicitly recorded as no-training.",
        ),
        (
            phase53.get("level5_supported") is False,
            "Phase 53 does not explicitly keep Level 5 unsupported.",
        ),
        (
            phase53.get("no_swe_pinn") is True,
            "Phase 53 does not preserve the no-SWE/PINN boundary.",
        ),
        (
            phase53.get("warning_labels_are_probabilities") is False,
            "Phase 53 warning labels are not explicitly non-probabilistic.",
        ),
        (
            SELECTED_DECISION in plan_text,
            "Phase 54 plan does not name the expected conservative decision.",
        ),
        (
            "does not establish seed robustness" in plan_text,
            "Phase 54 plan does not preserve the seed-robustness boundary.",
        ),
        (
            "does not establish seed robustness" in phase52_findings.lower(),
            "Phase 52 findings do not preserve the seed-robustness boundary.",
        ),
        (
            "does not demonstrate seed robustness" in phase53_findings.lower(),
            "Phase 53 findings do not preserve the seed-robustness boundary.",
        ),
    ]
    for metric, expected in EXPECTED_PHASE52_METRICS.items():
        checks.append(
            (
                values_match(best_metrics.get(metric), expected),
                f"Phase 52 best-epoch {metric} is inconsistent.",
            )
        )

    inconsistencies = [message for passed, message in checks if not passed]
    return {
        "phase52": phase52,
        "phase53": phase53,
        "comparison_rows": comparison_rows,
        "warning_rows": warning_rows,
        "diagnostic_rows": diagnostic_rows,
        "phase48_warning_counts": dict(phase48_counts),
        "phase53_warning_counts": dict(phase53_counts),
        "inconsistencies": inconsistencies,
    }


def option_rows() -> list[dict[str, str]]:
    return [
        {
            "option_id": "A",
            "option_name": "Controlled seed123 and seed202 replication",
            "description": (
                "Authorize a separate Phase 55 for exactly seed123 and seed202 "
                "under the fixed Phase 52 128x128, 40-epoch protocol."
            ),
            "scientific_value": "high",
            "reproducibility_value": "highest_direct_three_seed_comparison",
            "implementation_risk": "low_to_moderate_controlled_reuse",
            "compute_cost": "moderate_two_bounded_runs_plus_diagnostics",
            "continuity_with_phase52": "highest_only_seed_changes",
            "diagnostic_support_from_phase53": "strong_with_seven_high_risk_cases_retained",
            "claim_boundary_safety": "high_if_bounded_to_tested_three_seed_scope",
            "recommendation": "authorize_next_phase",
            "rationale": (
                "Directly addresses the unresolved seed-sensitivity question while "
                "holding the established training and diagnostic protocol fixed."
            ),
        },
        {
            "option_id": "B",
            "option_name": "Seed123-only pilot",
            "description": (
                "Authorize seed123 only and require another decision before seed202."
            ),
            "scientific_value": "moderate",
            "reproducibility_value": "partial_two_seed_evidence_only",
            "implementation_risk": "low",
            "compute_cost": "lower_initial_cost_but_additional_review_cycle",
            "continuity_with_phase52": "high_only_seed_changes",
            "diagnostic_support_from_phase53": "sufficient_but_unnecessarily_staged",
            "claim_boundary_safety": "high",
            "recommendation": "not_preferred",
            "rationale": (
                "It reduces immediate compute but delays the predefined three-seed "
                "comparison even though the fixed protocol and diagnostics are ready."
            ),
        },
        {
            "option_id": "C",
            "option_name": "Defer replication and authorize 256x256",
            "description": (
                "Change resolution before evaluating seed sensitivity at 128x128."
            ),
            "scientific_value": "medium_but_confounded",
            "reproducibility_value": "low_for_current_seed_question",
            "implementation_risk": "high_new_resolution_and_resource_profile",
            "compute_cost": "high",
            "continuity_with_phase52": "low_changes_resolution",
            "diagnostic_support_from_phase53": "does_not_support_resolution_expansion",
            "claim_boundary_safety": "medium",
            "recommendation": "defer",
            "rationale": (
                "A resolution change would confound attribution before the established "
                "128x128 protocol has bounded replication evidence."
            ),
        },
        {
            "option_id": "D",
            "option_name": "Defer training for reporting or manuscript work",
            "description": (
                "Continue reporting, visualization, and manuscript work without "
                "new training."
            ),
            "scientific_value": "moderate_for_reporting",
            "reproducibility_value": "none_for_seed_sensitivity",
            "implementation_risk": "low",
            "compute_cost": "low",
            "continuity_with_phase52": "high_reporting_only",
            "diagnostic_support_from_phase53": "high_for_bounded_reporting",
            "claim_boundary_safety": "highest_if_limitations_remain_explicit",
            "recommendation": "allowed_parallel_work_not_selected",
            "rationale": (
                "Useful non-training work, but it leaves the principal seed-robustness "
                "gap unresolved."
            ),
        },
        {
            "option_id": "E",
            "option_name": "Defer all expansion because evidence is insufficient",
            "description": (
                "Authorize no training when required evidence is missing, contradictory, "
                "or inadequate for controlled replication."
            ),
            "scientific_value": "low_unless_evidence_checks_fail",
            "reproducibility_value": "none",
            "implementation_risk": "low_operational_high_stagnation",
            "compute_cost": "none",
            "continuity_with_phase52": "none",
            "diagnostic_support_from_phase53": "fallback_for_failed_review_only",
            "claim_boundary_safety": "highest",
            "recommendation": "fail_closed_fallback",
            "rationale": (
                "Required if evidence validation fails; the reviewed Phase 52/53 "
                "artifacts otherwise support the bounded Option A design."
            ),
        },
    ]


def risk_rows() -> list[dict[str, str]]:
    return [
        {
            "risk_item": "seed-specific performance degradation",
            "affected_options": "A;B",
            "risk_level": "high",
            "mitigation": (
                "Retain best and final checkpoints, complete each authorized run, "
                "and compare all retained metrics directly across seeds 42, 123, and 202."
            ),
            "decision_impact": (
                "Expected replication risk; requires review and cannot be hidden by "
                "substituting another seed."
            ),
        },
        {
            "risk_item": "seed-specific warning-diagnostic degradation",
            "affected_options": "A;B",
            "risk_level": "high",
            "mitigation": (
                "Require the retained reliability, physical-proxy, and warning "
                "diagnostics for both new seeds before judging replication."
            ),
            "decision_impact": (
                "Training completion alone is insufficient for Phase 55 success."
            ),
        },
        {
            "risk_item": "compute/runtime expansion",
            "affected_options": "A;B;C",
            "risk_level": "moderate",
            "mitigation": (
                "Limit Phase 55 to exactly two runs, cap each at 40 epochs, and use "
                "resource-aware scheduling without changing the protocol."
            ),
            "decision_impact": "Supports bounded Option A but prohibits broader sweeps.",
        },
        {
            "risk_item": "accidental protocol drift",
            "affected_options": "A;B;C",
            "risk_level": "high",
            "mitigation": (
                "Diff each seed config against Phase 52 and freeze split, sample counts, "
                "architecture, loss, optimizer/scheduler basis, batch-size basis, "
                "rainfall alignment, downsampling, wet threshold, and metrics."
            ),
            "decision_impact": (
                "Any non-seed drift invalidates controlled replication and requires stop."
            ),
        },
        {
            "risk_item": "output-directory overwrite",
            "affected_options": "A;B;C",
            "risk_level": "high",
            "mitigation": (
                "Use separate seed123 and seed202 run directories plus a separate "
                "Phase 55 analysis directory; never overwrite Phase 52 or the other seed."
            ),
            "decision_impact": "Non-overwriting outputs are mandatory.",
        },
        {
            "risk_item": (
                "overclaiming seed robustness before all runs and diagnostics are complete"
            ),
            "affected_options": "A;B",
            "risk_level": "high",
            "mitigation": (
                "Keep seed_robustness_demonstrated=false in Phase 54 and require a "
                "completed three-seed review before any bounded reproducibility statement."
            ),
            "decision_impact": "Authorization is not a robustness result.",
        },
        {
            "risk_item": (
                "interpreting successful replication as Level 5 or production readiness"
            ),
            "affected_options": "A;B;C;D",
            "risk_level": "high",
            "mitigation": (
                "Preserve Level 4+ wording and prohibit Level 5, SWE/PINN, strict or "
                "full conservation, hydrodynamic closure, calibrated-probability "
                "warning, and production-readiness claims."
            ),
            "decision_impact": "Applies non-negotiable claim guardrails.",
        },
    ]


def build_decision(
    paths: dict[str, Path], evidence: dict[str, Any]
) -> dict[str, Any]:
    evidence_ok = not evidence["inconsistencies"]
    selected = SELECTED_DECISION if evidence_ok else DEFER_DECISION
    authorized_seeds = [123, 202] if evidence_ok else []

    return {
        "phase": 54,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "script": "scripts/decide_phase54_seed_replication.py",
        "selected_decision": selected,
        "authorized_next_phase": AUTHORIZED_NEXT_PHASE if evidence_ok else None,
        "authorized_seeds": authorized_seeds,
        "reference_seed": 42,
        "resolution": 128,
        "maximum_epochs_per_seed": 40,
        "required_train_samples": 960,
        "required_test_samples": 384,
        "protocol_must_match_phase52": True,
        "post_training_diagnostics_required": True,
        "deferred_options": DEFERRED_OPTIONS,
        "no_training_in_phase54": True,
        "seed_robustness_demonstrated": False,
        "level4_plus_route_supported": evidence_ok,
        "level5_supported": False,
        "no_swe_pinn": True,
        "warning_labels_are_probabilities": False,
        "no_uncontrolled_expansion": True,
        "next_recommended_action": (
            "Implement Phase 55 as exactly two separate controlled 128x128 runs "
            "for seed123 and seed202, each capped at 40 epochs under the unchanged "
            "Phase 52 protocol, followed by direct three-seed reliability, "
            "physical-proxy, and warning-diagnostic comparison."
            if evidence_ok
            else "Resolve the listed evidence inconsistencies before authorizing training."
        ),
        "authorized_phase55_scope": {
            "seeds": authorized_seeds,
            "reference_seed": 42,
            "resolution": 128,
            "maximum_epochs_per_seed": 40,
            "same_phase52_scenario_split": True,
            "train_samples": 960,
            "test_samples": 384,
            "same_model_architecture": True,
            "same_loss": True,
            "same_optimizer_and_scheduler_basis": True,
            "same_batch_size_basis": True,
            "same_rainfall_alignment": True,
            "same_downsampling": True,
            "same_wet_threshold_and_metrics": True,
            "separate_config_per_seed": True,
            "separate_run_directory_per_seed": True,
            "retain_best_and_final_checkpoints_locally": True,
            "direct_three_seed_comparison_required": True,
            "reliability_physical_proxy_warning_diagnostics_required": True,
            "suggested_run_directories": [
                "runs/phase55_full_downsample128_seed123_40e/",
                "runs/phase55_full_downsample128_seed202_40e/",
            ],
            "suggested_analysis_directory": (
                "analysis/phase55_controlled_128x128_seed_replication/"
            ),
        },
        "evidence_review_passed": evidence_ok,
        "evidence_inconsistencies": evidence["inconsistencies"],
        "evidence_summary": {
            "phase52_seed": evidence["phase52"].get("seed"),
            "phase52_best_epoch": evidence["phase52"].get("best_epoch"),
            "phase52_test_rmse": evidence["phase52"].get(
                "best_epoch_metrics", {}
            ).get("test_rmse"),
            "phase53_diagnostics_executed": evidence["phase53"].get(
                "diagnostics_executed"
            ),
            "phase53_evaluated_scenarios": evidence["phase53"].get(
                "evaluated_scenarios"
            ),
            "phase53_evaluated_windows": evidence["phase53"].get(
                "evaluated_windows"
            ),
            "phase53_diagnostic_rows": evidence["diagnostic_rows"],
            "phase53_matched_comparison_rows": len(evidence["comparison_rows"]),
            "phase48_phase49_warning_counts": evidence[
                "phase48_warning_counts"
            ],
            "phase53_warning_counts": evidence["phase53_warning_counts"],
        },
        "input_sources": {
            name: display_path(path) for name, path in paths.items()
        },
        "claim_guardrails": {
            "strict_conservation_supported": False,
            "full_mass_conservation_supported": False,
            "hydrodynamic_closure_supported": False,
            "calibrated_probability_warning_supported": False,
            "production_readiness_supported": False,
        },
    }


def write_markdown(path: Path, decision: dict[str, Any]) -> None:
    evidence = decision["evidence_summary"]
    deferred = "\n".join(f"- `{item}`" for item in decision["deferred_options"])
    inconsistencies = decision["evidence_inconsistencies"]
    inconsistency_section = ""
    if inconsistencies:
        bullets = "\n".join(f"- {item}" for item in inconsistencies)
        inconsistency_section = f"\n## Evidence Inconsistencies\n\n{bullets}\n"

    text = f"""# Phase 54 Reviewed Seed-Replication Decision

Phase 54 is decision synthesis only. It performs no training, creates no
checkpoint, and generates no new model-performance evidence.

## Evidence Reviewed

- Phase 52 completed seed42 at 128x128 for 40 epochs using 960 train and 384 test windows.
- The Phase 52 best epoch was {evidence['phase52_best_epoch']} with test RMSE `{evidence['phase52_test_rmse']}`.
- Phase 53 executed no-training diagnostics over {evidence['phase53_evaluated_scenarios']} scenarios, {evidence['phase53_evaluated_windows']} windows, and {evidence['phase53_diagnostic_rows']:,} diagnostic rows.
- The matched Phase 52-versus-Phase 48 comparison contains {evidence['phase53_matched_comparison_rows']} scenarios.
- Warning counts improved from reliable/caution/high-risk = `1/12/35` to `38/3/7`.
- Seven high-risk scenarios and case-level peak, timing, and volume-proxy degradations remain.

## Candidate Options

- **A:** Authorize controlled seed123 and seed202 replication.
- **B:** Authorize seed123 only as a pilot.
- **C:** Defer replication and authorize 256x256.
- **D:** Defer training for reporting or manuscript work.
- **E:** Defer all expansion because evidence is insufficient.

## Selected Decision

`{decision['selected_decision']}`

- Authorized next phase: `{decision['authorized_next_phase']}`
- Authorized seeds: `{decision['authorized_seeds']}`
- Reference seed: `{decision['reference_seed']}`
- No training in Phase 54: `{bool_text(decision['no_training_in_phase54'])}`
- Seed robustness demonstrated: `{bool_text(decision['seed_robustness_demonstrated'])}`
- Level 4+ route supported: `{bool_text(decision['level4_plus_route_supported'])}`
- Level 5 supported: `{bool_text(decision['level5_supported'])}`

## Why Bounded Two-Seed Replication Is Authorized

Phase 52 materially improved all retained aggregate metrics under a completed
and controlled 40-epoch seed42 protocol. Phase 53 showed that the improvement
extends across matched reliability, wet/dry, physical-proxy, and warning
diagnostics. The protocol and diagnostic basis are therefore sufficiently
defined to test the main unresolved limitation: sensitivity to training seed.

Authorizing exactly seed123 and seed202 changes only the seed and creates a
direct, bounded three-seed comparison. Authorization does not demonstrate seed
robustness; that conclusion remains false until both runs and all required
diagnostics are complete and reviewed.

## Why a Seed123-Only Pilot Is Not Preferred

A seed123-only pilot lowers immediate compute but yields only a partial
two-seed comparison and adds another decision cycle before seed202. Because the
Phase 52 protocol and Phase 53 diagnostics are already established, the extra
staging does not materially reduce conceptual risk. Resource constraints must
be managed inside the two-run cap rather than by weakening the replication
design.

## Why 256x256 Remains Deferred

Moving to 256x256 would change resolution and resource behavior before seed
sensitivity at 128x128 is understood. That would confound attribution and would
not answer whether the favorable Phase 52 result is reproducible. Resolution
expansion requires a later reviewed decision after Phase 55 evidence is complete.

## Authorized Phase 55 Protocol

- Train exactly seed123 and seed202; seed42 remains reference only.
- Use 128x128 resolution and a maximum of 40 epochs per seed.
- Preserve the Phase 52 scenario split, 960 train windows, and 384 test windows.
- Preserve the model architecture, loss, optimizer and scheduler basis, batch-size basis, rainfall alignment, downsampling, wet threshold, and metrics.
- Use a separate config and run directory for each seed.
- Retain best and final checkpoints locally.
- Compare seed42, seed123, and seed202 directly.
- Run reliability, physical-proxy, and warning diagnostics after training.

Suggested run directories:

```text
runs/phase55_full_downsample128_seed123_40e/
runs/phase55_full_downsample128_seed202_40e/
```

Suggested analysis directory:

```text
analysis/phase55_controlled_128x128_seed_replication/
```

## Stop and Failure Boundaries

- Stop a run if the fixed split, sample counts, model, loss, optimizer/scheduler basis, masks, wet threshold, metrics, or other non-seed protocol fields drift from Phase 52.
- Stop rather than overwrite Phase 52 or another Phase 55 seed directory.
- Do not exceed 40 epochs per seed.
- Classify non-finite required metrics, unreadable checkpoints, resource exhaustion, or repeated controlled-execution failure explicitly.
- Do not replace a failed authorized seed with another seed.
- Treat Phase 55 as incomplete if either authorized seed lacks valid training artifacts or required diagnostics.
- Do not make a seed-reproducibility conclusion until all three seeds are reviewed.

## Deferred Paths

{deferred}

Reporting and manuscript work may continue as non-training activity, but it
does not resolve seed sensitivity.

## Claim Guardrails

- Do not claim seed robustness from Phase 54 authorization or one additional run.
- Limit any later reproducibility statement to the tested three seeds and fixed 128x128 protocol.
- Do not claim Level 5, SWE/PINN behavior, strict conservation, full mass conservation, or hydrodynamic closure.
- Warning labels remain rule-based diagnostics, not calibrated probabilities.
- Do not claim production readiness.
- Do not authorize 256x256, tile, multiscale, full 500x500, sweep, redesign, or other uncontrolled expansion.

## Next Action

{decision['next_recommended_action']}
{inconsistency_section}"""
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
        output_dir / "phase54_seed_replication_option_matrix.csv",
        option_rows(),
        OPTION_COLUMNS,
    )
    write_csv(
        output_dir / "phase54_seed_replication_risk_assessment.csv",
        risk_rows(),
        RISK_COLUMNS,
    )
    write_json(
        output_dir / "phase54_selected_decision.json",
        decision,
    )
    write_markdown(
        output_dir / "phase54_selected_decision.md",
        decision,
    )

    print(f"selected_decision={decision['selected_decision']}")
    print(f"authorized_next_phase={decision['authorized_next_phase']}")
    print(f"authorized_seeds={decision['authorized_seeds']}")
    print(
        "maximum_epochs_per_seed="
        f"{decision['maximum_epochs_per_seed']}"
    )
    print(
        "no_training_in_phase54="
        f"{bool_text(decision['no_training_in_phase54'])}"
    )
    print(
        "seed_robustness_demonstrated="
        f"{bool_text(decision['seed_robustness_demonstrated'])}"
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
