from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = Path("analysis/phase37_seed42_training_authorization")

TRAINING_COMMAND_UNDER_REVIEW = (
    "python scripts/train_model.py --config "
    "configs/train_phase36_manhole_false_dry_guardrail_seed42_40e.json"
)

INPUTS = {
    "phase37_plan": Path("docs/phase37_seed42_training_authorization_review_plan.md"),
    "acceptance_thresholds": Path(
        "analysis/phase34_pilot_thresholds/acceptance_thresholds.csv"
    ),
    "rejection_thresholds": Path(
        "analysis/phase34_pilot_thresholds/rejection_thresholds.csv"
    ),
    "baseline_metrics": Path(
        "analysis/phase34_pilot_thresholds/baseline_metric_table.csv"
    ),
    "smoke_summary": Path(
        "analysis/phase36_manhole_false_dry_guardrail_code_smoke/"
        "smoke_test_summary.json"
    ),
    "guardrail_dry_run": Path(
        "analysis/phase36_manhole_false_dry_guardrail_code_smoke/"
        "guardrail_checker_dry_run.json"
    ),
    "phase36_config": Path(
        "configs/train_phase36_manhole_false_dry_guardrail_seed42_40e.json"
    ),
    "phase36_findings": Path(
        "docs/phase36_manhole_false_dry_guardrail_code_smoke_findings.md"
    ),
}

CHECKLIST_COLUMNS = (
    "check_id",
    "check_name",
    "status",
    "evidence",
    "required_for_authorization",
    "blocker_if_failed",
    "notes",
)

EXPECTED_ACCEPTANCE_IDS = {f"AT{i:02d}" for i in range(1, 15)}
EXPECTED_REJECTION_IDS = {f"RT{i:02d}" for i in range(1, 10)}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Diagnostic-only Phase 37 review of whether the Phase 36 seed42 "
            "config may be authorized for training in a later phase. This script "
            "does not train, run seed42, run seed123/seed202, perform sweeps, "
            "continue Phase 29, or modify losses/configs/model architecture."
        )
    )
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    return parser.parse_args()


def repo_path(path: Path) -> Path:
    return path if path.is_absolute() else REPO_ROOT / path


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT)).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


def read_json(path: Path) -> dict[str, Any] | None:
    try:
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
    except (OSError, json.JSONDecodeError):
        return None
    return data if isinstance(data, dict) else None


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    try:
        with path.open("r", encoding="utf-8", newline="") as handle:
            return list(csv.DictReader(handle))
    except OSError:
        return []


def bool_status(value: bool | None) -> str:
    if value is True:
        return "pass"
    if value is False:
        return "fail"
    return "incomplete"


def checklist_row(
    check_id: str,
    check_name: str,
    status: str,
    evidence: str,
    notes: str,
    required: bool = True,
    blocker: bool = True,
) -> dict[str, str]:
    return {
        "check_id": check_id,
        "check_name": check_name,
        "status": status,
        "evidence": evidence,
        "required_for_authorization": str(required).lower(),
        "blocker_if_failed": str(blocker).lower(),
        "notes": notes,
    }


def contains_all(text: str, needles: tuple[str, ...]) -> bool:
    lowered = text.lower()
    return all(needle.lower() in lowered for needle in needles)


def normalized_text(*parts: str) -> str:
    joined = "\n".join(parts).lower()
    return joined.replace("_", " ").replace("-", " ")


def csv_ids(rows: list[dict[str, str]], field: str) -> set[str]:
    return {row.get(field, "").strip() for row in rows if row.get(field, "").strip()}


def baseline_has_seed42_references(rows: list[dict[str, str]]) -> bool:
    required_columns = {"phase25_seed42", "phase27_seed42", "phase29_seed42"}
    if not rows or not required_columns.issubset(rows[0].keys()):
        return False
    return all(
        row.get("phase25_seed42", "").strip()
        and row.get("phase27_seed42", "").strip()
        and row.get("phase29_seed42", "").strip()
        for row in rows
    )


def collect_review() -> tuple[list[dict[str, str]], dict[str, Any]]:
    paths = {name: repo_path(path) for name, path in INPUTS.items()}

    plan_text = read_text(paths["phase37_plan"])
    findings_text = read_text(paths["phase36_findings"])
    combined_text = normalized_text(plan_text, findings_text)

    config_exists = paths["phase36_config"].exists()
    config = read_json(paths["phase36_config"]) if config_exists else None
    config_loads = config is not None

    output_root = ""
    runtime_seed: Any = None
    if config:
        output = config.get("output", {})
        runtime = config.get("runtime", {})
        output_root = output.get("root", "") if isinstance(output, dict) else ""
        runtime_seed = runtime.get("seed") if isinstance(runtime, dict) else None

    output_root_named = (
        isinstance(output_root, str)
        and "phase36_manhole_false_dry_guardrail_seed42_40e" in output_root
    )

    smoke = read_json(paths["smoke_summary"])
    dry_run = read_json(paths["guardrail_dry_run"])

    loss_smoke_passed = (
        smoke.get("loss_smoke_status", {}).get("passed") is True if smoke else None
    )
    guardrail_checker_dry_run_passed = (
        dry_run.get("status") == "dry_run_passed"
        and dry_run.get("training_authorized") is False
        and dry_run.get("training_result_available") is False
        if dry_run
        else None
    )

    acceptance_rows = read_csv_rows(paths["acceptance_thresholds"])
    rejection_rows = read_csv_rows(paths["rejection_thresholds"])
    baseline_rows = read_csv_rows(paths["baseline_metrics"])

    acceptance_ids = csv_ids(acceptance_rows, "threshold_id")
    rejection_ids = csv_ids(rejection_rows, "rejection_id")
    acceptance_thresholds_available = EXPECTED_ACCEPTANCE_IDS.issubset(acceptance_ids)
    rejection_thresholds_available = EXPECTED_REJECTION_IDS.issubset(rejection_ids)
    baseline_metrics_available = baseline_has_seed42_references(baseline_rows)

    seed42_only = runtime_seed == 42 and contains_all(
        combined_text, ("single seed42", "seed42 only")
    )
    seed123_seed202_blocked = contains_all(combined_text, ("seed123", "seed202", "blocked"))
    sweeps_blocked = "sweep" in combined_text and "blocked" in combined_text
    phase29_continuation_blocked = contains_all(
        combined_text, ("phase 29 continuation", "blocked")
    )
    level4_plus_scope_preserved = (
        "level 4+" in combined_text
        and "strict conservation" in combined_text
        and "hydrodynamic closure" in combined_text
    )
    post_training_guardrail_check_required = (
        "post training" in combined_text
        and "guardrail" in combined_text
        and "rt01" in combined_text
        and "rt09" in combined_text
    )
    plan_text_unescaped = plan_text.replace("\\_", "_")
    training_command_documented = TRAINING_COMMAND_UNDER_REVIEW in plan_text_unescaped

    training_executed = False
    seed42_run_executed = False
    seed123_seed202_executed = False
    sweep_executed = False
    if smoke:
        training_executed = bool(smoke.get("training_executed", False))
        seed42_run_executed = bool(smoke.get("seed42_run_executed", False))
        seed123_seed202_executed = bool(smoke.get("seed123_seed202_executed", False))
        sweep_executed = bool(smoke.get("sweep_executed", False))

    phase37_training_not_executed = (
        not training_executed
        and not seed42_run_executed
        and not seed123_seed202_executed
        and not sweep_executed
    )

    checks = [
        checklist_row(
            "phase36_config_exists",
            "Phase 36 seed42 config exists",
            bool_status(config_exists),
            display_path(paths["phase36_config"]),
            "Required seed42 config artifact is present.",
        ),
        checklist_row(
            "phase36_config_loads",
            "Phase 36 seed42 config loads as JSON",
            bool_status(config_loads),
            display_path(paths["phase36_config"]),
            "JSON parsing must succeed before a later phase can run the reviewed config.",
        ),
        checklist_row(
            "phase36_output_root_is_named",
            "Phase 36 config output root is clearly named",
            bool_status(output_root_named if config_loads else None),
            output_root or "missing output.root",
            "Output root must name the reviewed Phase 36 seed42 40e run.",
        ),
        checklist_row(
            "loss_smoke_passed",
            "Phase 36 loss smoke test passed",
            bool_status(loss_smoke_passed),
            display_path(paths["smoke_summary"]),
            "Phase 37 relies on the no-training Phase 36 smoke evidence.",
        ),
        checklist_row(
            "guardrail_checker_dry_run_passed",
            "Phase 36 guardrail checker dry-run passed",
            bool_status(guardrail_checker_dry_run_passed),
            display_path(paths["guardrail_dry_run"]),
            "Dry-run must stage checks without claiming a training result.",
        ),
        checklist_row(
            "acceptance_thresholds_available",
            "Phase 34 acceptance thresholds are available",
            bool_status(acceptance_thresholds_available),
            f"{display_path(paths['acceptance_thresholds'])}; ids={sorted(acceptance_ids)}",
            "AT01-AT14 must be available before training can be reviewed.",
        ),
        checklist_row(
            "rejection_thresholds_available",
            "Phase 34 rejection thresholds are available",
            bool_status(rejection_thresholds_available),
            f"{display_path(paths['rejection_thresholds'])}; ids={sorted(rejection_ids)}",
            "RT01-RT09 must be available before training can be reviewed.",
        ),
        checklist_row(
            "baseline_metrics_available",
            "Phase 34 baseline metrics are available",
            bool_status(baseline_metrics_available),
            f"{display_path(paths['baseline_metrics'])}; rows={len(baseline_rows)}",
            "Baseline table must contain Phase 25, Phase 27, and Phase 29 seed42 references.",
        ),
        checklist_row(
            "AT01_available",
            "AT01 target threshold is available",
            bool_status("AT01" in acceptance_ids),
            "AT01 in acceptance_thresholds.csv",
            "AT01 is the targeted manhole-nonzero false-dry acceptance check.",
        ),
        checklist_row(
            "RT01_available",
            "RT01 hard rejection threshold is available",
            bool_status("RT01" in rejection_ids),
            "RT01 in rejection_thresholds.csv",
            "RT01 blocks the Phase 29 trade-off pattern.",
        ),
        checklist_row(
            "seed42_only_scope",
            "Scope remains seed42-only",
            bool_status(seed42_only),
            f"runtime.seed={runtime_seed}; Phase 37 plan/finding text reviewed",
            "Next phase authorization, if granted, is limited to the reviewed seed42 config.",
        ),
        checklist_row(
            "seed123_seed202_blocked",
            "seed123 and seed202 remain blocked",
            bool_status(seed123_seed202_blocked and not seed123_seed202_executed),
            "Phase 37 plan/finding text and Phase 36 smoke execution flags reviewed",
            "No seed123 or seed202 expansion may occur before seed42 passes.",
        ),
        checklist_row(
            "sweeps_blocked",
            "Sweeps remain blocked",
            bool_status(sweeps_blocked and not sweep_executed),
            "Phase 37 plan/finding text and Phase 36 smoke execution flags reviewed",
            "No sweeps may occur before the reviewed seed42 config passes.",
        ),
        checklist_row(
            "phase29_continuation_blocked",
            "Phase 29 continuation remains blocked",
            bool_status(phase29_continuation_blocked),
            "Phase 37 plan/finding text reviewed",
            "This authorization review must not continue Phase 29.",
        ),
        checklist_row(
            "level4_plus_scope_preserved",
            "Level 4+ proxy scope is preserved",
            bool_status(level4_plus_scope_preserved),
            "Phase 37 plan/finding text reviewed",
            "No strict conservation, full mass conservation, SWE/PINN, or hydrodynamic closure claims are made.",
        ),
        checklist_row(
            "post_training_guardrail_check_required",
            "Post-training guardrail check is required",
            bool_status(post_training_guardrail_check_required),
            "Phase 37 plan reviewed",
            "A later trained result must run evaluation and the Phase 36 guardrail checker.",
        ),
        checklist_row(
            "training_command_documented_but_not_executed",
            "Training command is documented but not executed",
            bool_status(training_command_documented and phase37_training_not_executed),
            TRAINING_COMMAND_UNDER_REVIEW,
            "Phase 37 may document the command under review but must not execute it.",
        ),
        checklist_row(
            "training_not_executed_in_phase37",
            "Training was not executed in Phase 37",
            bool_status(phase37_training_not_executed),
            (
                f"training_executed={training_executed}; "
                f"seed42_run_executed={seed42_run_executed}; "
                f"seed123_seed202_executed={seed123_seed202_executed}; "
                f"sweep_executed={sweep_executed}"
            ),
            "This diagnostic-only script must not train.",
        ),
    ]

    required_checks = [row for row in checks if row["required_for_authorization"] == "true"]
    required_checks_passed = sum(row["status"] == "pass" for row in required_checks)
    total_required_checks = len(required_checks)

    if any(row["status"] == "incomplete" for row in required_checks):
        decision = "authorization_review_incomplete"
    elif any(row["status"] == "fail" for row in required_checks):
        decision = "training_not_authorized"
    else:
        decision = "seed42_training_authorized_next_phase"

    training_authorized_next_phase = decision == "seed42_training_authorized_next_phase"

    summary = {
        "phase": 37,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "claim_scope": "Level 4+ proxy diagnostics only",
        "config_exists": config_exists,
        "config_loads": config_loads,
        "loss_smoke_passed": loss_smoke_passed is True,
        "guardrail_checker_dry_run_passed": guardrail_checker_dry_run_passed is True,
        "acceptance_thresholds_available": acceptance_thresholds_available,
        "rejection_thresholds_available": rejection_thresholds_available,
        "baseline_metrics_available": baseline_metrics_available,
        "seed42_only": seed42_only,
        "seed123_seed202_blocked": seed123_seed202_blocked and not seed123_seed202_executed,
        "sweeps_blocked": sweeps_blocked and not sweep_executed,
        "phase29_continuation_blocked": phase29_continuation_blocked,
        "level4_plus_scope_preserved": level4_plus_scope_preserved,
        "post_training_guardrail_check_required": post_training_guardrail_check_required,
        "training_command_under_review": TRAINING_COMMAND_UNDER_REVIEW,
        "training_executed": training_executed,
        "seed42_run_executed": seed42_run_executed,
        "seed123_seed202_executed": seed123_seed202_executed,
        "sweep_executed": sweep_executed,
        "required_checks_passed": required_checks_passed,
        "total_required_checks": total_required_checks,
        "decision": decision,
        "training_authorized_next_phase": training_authorized_next_phase,
        "authorization_scope": (
            "Authorization, if true, is for the next phase only. Phase 37 itself "
            "does not train."
        ),
        "next_phase_requirements_if_authorized": [
            "Run only the reviewed seed42 config.",
            "Run evaluation on the trained result.",
            "Run scripts/check_phase36_pilot_guardrails.py after evaluation.",
            "Reject the result if any RT01-RT09 trigger fires.",
            "Do not run seed123, seed202, or sweeps before seed42 passes.",
            "Preserve Level 4+ proxy wording.",
        ],
        "inputs": {name: display_path(path) for name, path in paths.items()},
    }
    return checks, summary


def write_checklist(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=CHECKLIST_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def write_summary_md(path: Path, summary: dict[str, Any], checks: list[dict[str, str]]) -> None:
    authorized = summary["training_authorized_next_phase"]
    lines = [
        "# Phase 37 Seed42 Training Authorization Review",
        "",
        "## Decision",
        "",
        f"- `decision`: `{summary['decision']}`",
        f"- `training_authorized_next_phase`: `{str(authorized).lower()}`",
        f"- `training_executed`: `{str(summary['training_executed']).lower()}`",
        f"- `seed42_run_executed`: `{str(summary['seed42_run_executed']).lower()}`",
        f"- `seed123_seed202_executed`: `{str(summary['seed123_seed202_executed']).lower()}`",
        "",
        "Phase 37 is diagnostic-only. It documents the command under review but does not execute it:",
        "",
        f"`{summary['training_command_under_review']}`",
        "",
        "## Authorization Scope",
        "",
        "- Authorization is for the next phase only.",
        "- Phase 37 itself does not train.",
        "- The next phase must run only the reviewed seed42 config.",
        "- The next phase must run evaluation and then the Phase 36 guardrail checker.",
        "- Any RT01-RT09 trigger rejects the result.",
        "- No seed123, seed202, or sweeps may run before seed42 passes.",
        "- Claims remain Level 4+ proxy scoped.",
        "",
        "## Checklist",
        "",
        "| check_id | status | required | blocker_if_failed |",
        "|---|---:|---:|---:|",
    ]
    for row in checks:
        lines.append(
            "| "
            + " | ".join(
                [
                    row["check_id"],
                    row["status"],
                    row["required_for_authorization"],
                    row["blocker_if_failed"],
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Guardrails Preserved",
            "",
            "- No training was executed.",
            "- seed42 was not run in Phase 37.",
            "- seed123 and seed202 were not run.",
            "- Sweeps were not performed.",
            "- Phase 29 was not continued.",
            "- Losses, configs, and model architecture were not modified by this script.",
            "- No pilot success, strict conservation, full mass conservation, SWE/PINN, or hydrodynamic closure claim is made.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    output_dir = repo_path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    checks, summary = collect_review()

    write_checklist(output_dir / "authorization_checklist.csv", checks)
    with (output_dir / "training_authorization_summary.json").open(
        "w", encoding="utf-8"
    ) as handle:
        json.dump(summary, handle, indent=2, sort_keys=True)
        handle.write("\n")
    write_summary_md(output_dir / "training_authorization_summary.md", summary, checks)

    print(f"config_exists={str(summary['config_exists']).lower()}")
    print(f"config_loads={str(summary['config_loads']).lower()}")
    print(f"required_checks_passed={summary['required_checks_passed']}")
    print(f"total_required_checks={summary['total_required_checks']}")
    print(f"decision={summary['decision']}")
    print(f"training_executed={str(summary['training_executed']).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
