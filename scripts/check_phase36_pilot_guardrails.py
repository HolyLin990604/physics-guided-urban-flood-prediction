from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_THRESHOLD_DIR = Path("analysis/phase34_pilot_thresholds")
DEFAULT_OUTPUT_DIR = Path("analysis/phase36_manhole_false_dry_guardrail_code_smoke")
DEFAULT_RUN_ROOT = Path("runs/phase36_manhole_false_dry_guardrail_seed42_40e")

ACCEPTANCE_FILE = "acceptance_thresholds.csv"
REJECTION_FILE = "rejection_thresholds.csv"
BASELINE_FILE = "baseline_metric_table.csv"


def repo_path(path: str | Path) -> Path:
    path = Path(path)
    if path.is_absolute():
        return path
    return REPO_ROOT / path


def display_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise FileNotFoundError(f"Missing required Phase 34 threshold input: {display_path(path)}")
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def load_threshold_inputs(threshold_dir: Path) -> dict[str, Any]:
    acceptance_path = threshold_dir / ACCEPTANCE_FILE
    rejection_path = threshold_dir / REJECTION_FILE
    baseline_path = threshold_dir / BASELINE_FILE
    acceptance_rows = read_csv_rows(acceptance_path)
    rejection_rows = read_csv_rows(rejection_path)
    baseline_rows = read_csv_rows(baseline_path)
    return {
        "paths": {
            "acceptance_thresholds": display_path(acceptance_path),
            "rejection_thresholds": display_path(rejection_path),
            "baseline_metric_table": display_path(baseline_path),
        },
        "acceptance_rows": acceptance_rows,
        "rejection_rows": rejection_rows,
        "baseline_rows": baseline_rows,
    }


def summarize_thresholds(inputs: dict[str, Any]) -> dict[str, Any]:
    acceptance_ids = [row.get("threshold_id", "") for row in inputs["acceptance_rows"]]
    rejection_ids = [row.get("rejection_id", "") for row in inputs["rejection_rows"]]
    return {
        "acceptance_threshold_count": len(inputs["acceptance_rows"]),
        "rejection_threshold_count": len(inputs["rejection_rows"]),
        "baseline_metric_count": len(inputs["baseline_rows"]),
        "acceptance_ids": acceptance_ids,
        "rejection_ids": rejection_ids,
        "expected_acceptance_ids": [f"AT{idx:02d}" for idx in range(1, 15)],
        "expected_rejection_ids": [f"RT{idx:02d}" for idx in range(1, 10)],
        "acceptance_structure_ready": acceptance_ids == [f"AT{idx:02d}" for idx in range(1, 15)],
        "rejection_structure_ready": rejection_ids == [f"RT{idx:02d}" for idx in range(1, 10)],
    }


def build_future_check_plan(inputs: dict[str, Any]) -> dict[str, list[dict[str, str]]]:
    acceptance_plan = [
        {
            "threshold_id": row.get("threshold_id", ""),
            "metric_group": row.get("metric_group", ""),
            "metric_name": row.get("metric_name", ""),
            "region": row.get("region", ""),
            "status": "pending_training_result",
        }
        for row in inputs["acceptance_rows"]
    ]
    rejection_plan = [
        {
            "rejection_id": row.get("rejection_id", ""),
            "rejection_rule": row.get("rejection_rule", ""),
            "trigger_metric_name": row.get("trigger_metric_name", ""),
            "trigger_region": row.get("trigger_region", ""),
            "status": "pending_training_result",
        }
        for row in inputs["rejection_rows"]
    ]
    return {"acceptance_checks": acceptance_plan, "rejection_checks": rejection_plan}


def run_guardrail_check(threshold_dir: Path, run_root: Path) -> dict[str, Any]:
    inputs = load_threshold_inputs(threshold_dir)
    threshold_summary = summarize_thresholds(inputs)
    metrics_path = run_root / "evaluation_test" / "metrics.json"
    training_result_available = metrics_path.exists()

    result: dict[str, Any] = {
        "phase": 36,
        "candidate": "manhole_nonzero_false_dry_guardrail",
        "claim_scope": "Level 4+ static-map-aware proxy diagnostics only",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "training_authorized": False,
        "training_result_available": training_result_available,
        "run_root": display_path(run_root),
        "expected_metrics_path": display_path(metrics_path),
        "threshold_inputs": inputs["paths"],
        "threshold_summary": threshold_summary,
        "future_check_plan": build_future_check_plan(inputs),
    }

    if not training_result_available:
        result.update(
            {
                "decision": "no_training_result_guardrail_check_dry_run",
                "status": "dry_run_passed",
                "notes": [
                    "No Phase 36 training result was found, as expected for code-smoke scope.",
                    "AT01-AT14 and RT01-RT09 are loaded and staged for a future result check.",
                    "This checker does not authorize training.",
                ],
            }
        )
        return result

    result.update(
        {
            "decision": "training_result_check_not_implemented_in_phase36",
            "status": "blocked_by_phase36_scope",
            "notes": [
                "A Phase 36 result path exists, but Phase 36 is a no-training smoke phase.",
                "Full candidate metric extraction and AT01-AT14 / RT01-RT09 evaluation should be implemented only after training is authorized.",
            ],
        }
    )
    return result


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_markdown(path: Path, payload: dict[str, Any]) -> None:
    lines = [
        "# Phase 36 Pilot Guardrail Checker Dry Run",
        "",
        f"- candidate: `{payload['candidate']}`",
        f"- claim_scope: `{payload['claim_scope']}`",
        f"- training_authorized: `{str(payload['training_authorized']).lower()}`",
        f"- training_result_available: `{str(payload['training_result_available']).lower()}`",
        f"- decision: `{payload['decision']}`",
        f"- status: `{payload['status']}`",
        "",
        "## Phase 34 Inputs",
        "",
    ]
    for key, value in payload["threshold_inputs"].items():
        lines.append(f"- {key}: `{value}`")
    summary = payload["threshold_summary"]
    lines.extend(
        [
            "",
            "## Threshold Structure",
            "",
            f"- acceptance_threshold_count: `{summary['acceptance_threshold_count']}`",
            f"- rejection_threshold_count: `{summary['rejection_threshold_count']}`",
            f"- baseline_metric_count: `{summary['baseline_metric_count']}`",
            f"- acceptance_structure_ready: `{str(summary['acceptance_structure_ready']).lower()}`",
            f"- rejection_structure_ready: `{str(summary['rejection_structure_ready']).lower()}`",
            "",
            "## Notes",
            "",
        ]
    )
    lines.extend(f"- {note}" for note in payload["notes"])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check Phase 36 pilot guardrails without authorizing training.")
    parser.add_argument("--threshold-dir", type=Path, default=DEFAULT_THRESHOLD_DIR)
    parser.add_argument("--run-root", type=Path, default=DEFAULT_RUN_ROOT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    threshold_dir = repo_path(args.threshold_dir)
    run_root = repo_path(args.run_root)
    output_dir = repo_path(args.output_dir)

    payload = run_guardrail_check(threshold_dir, run_root)
    write_json(output_dir / "guardrail_checker_dry_run.json", payload)
    write_markdown(output_dir / "guardrail_checker_dry_run.md", payload)

    print(f"training_result_available={str(payload['training_result_available']).lower()}")
    print(f"training_authorized={str(payload['training_authorized']).lower()}")
    print(f"decision={payload['decision']}")


if __name__ == "__main__":
    main()
