from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = Path("analysis/phase50_framework_consolidation")

SELECTED_DECISION = "phase50_framework_synthesis_ready_for_paper_outline"
PHASES_SYNTHESIZED = "43-49"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Synthesize the no-training Phase 50 UrbanFlood24 full-dataset Level 4+ "
            "evidence chain from Phases 43-49 into paper-ready framework artifacts."
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


def write_csv_rows(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def phase_evidence_rows() -> list[dict[str, str]]:
    return [
        {
            "phase": "43",
            "phase_name": "UrbanFlood24 full dataset inspection",
            "evidence_type": "dataset inventory and readiness inspection",
            "key_artifacts": "analysis/phase43_urbanflood24_full_dataset_inspection",
            "key_result": (
                "total_files=354; total_dirs=186; sampled_arrays_count=54; "
                "level4_plus_supported=true; level5_supported=false"
            ),
            "decision": "full_dataset_readiness_uncertain_needs_metadata",
            "claim_supported": "Full-dataset Level 4+ route is plausible with metadata/indexing follow-up.",
            "claim_not_supported": "Level 5 readiness, hydrodynamic closure, strict conservation.",
            "role_in_framework": "Establishes dataset availability and conservative upper claim boundary.",
        },
        {
            "phase": "44",
            "phase_name": "UrbanFlood24 full Level 4+ replanning",
            "evidence_type": "claim governance and route selection",
            "key_artifacts": "docs/phase44_full_level4_plus_replanning",
            "key_result": "Short-term Level 5/SWE/PINN claims frozen; route redirected to full-dataset proxy modeling.",
            "decision": "level4_plus_proxy_route_selected",
            "claim_supported": "Conservative Level 4+ proxy modeling, diagnostics, and warning extension.",
            "claim_not_supported": "Near-term Level 5, SWE residual, PINN, or production hydrodynamic claims.",
            "role_in_framework": "Defines the allowed scientific route and prevents claim escalation.",
        },
        {
            "phase": "45",
            "phase_name": "Full dataset indexing and lightweight adapter preparation",
            "evidence_type": "indexing and shape audit",
            "key_artifacts": "analysis/phase45_full_dataset_indexing",
            "key_result": (
                "scenario_count_total=168; train=120; test=48; static_index_rows=6; warning_count=0; "
                "flood_shapes=(360,1,500,500):153,(480,1,500,500):15; rainfall_lengths=180:108,360:60"
            ),
            "decision": "indexing_ready_for_dataloader_smoke",
            "claim_supported": "Indexed full-dataset scenario structure suitable for dataloader feasibility checks.",
            "claim_not_supported": "Training sufficiency, calibrated warnings, Level 5 evidence.",
            "role_in_framework": "Turns raw dataset inspection into reproducible scenario/static indexes.",
        },
        {
            "phase": "46",
            "phase_name": "No-training dataloader smoke, downsample, and tiling feasibility",
            "evidence_type": "no-training dataloader feasibility",
            "key_artifacts": "analysis/phase46_full_dataloader_smoke",
            "key_result": (
                "scenario_index_loaded=true; static_index_loaded=true; representative_samples_count=11; "
                "downsample_128_passed=true; downsample_256_passed=true; tile_checks_passed=true; "
                "batch_smoke_passed=true; memory_safe=true"
            ),
            "decision": "dataloader_smoke_ready_for_downsample_baseline",
            "claim_supported": "Memory-safe full-dataset dataloader path for controlled downsample baseline.",
            "claim_not_supported": "Model performance, training generalization, Level 5.",
            "role_in_framework": "Validates the data access path before any controlled baseline run.",
        },
        {
            "phase": "47",
            "phase_name": "Controlled 128x128 full-dataset downsample seed42 10e baseline",
            "evidence_type": "controlled baseline training result",
            "key_artifacts": "analysis/phase47_controlled_downsample_baseline; runs/phase47_full_downsample128_baseline_seed42_10e",
            "key_result": (
                "seed=42; resolution=128; epochs=10; train_samples=960; test_samples=384; "
                "best_test_rmse=0.01109213042097205; test_mae=0.00525291082279485; "
                "test_wet_dry_iou=0.8255524213115374; test_rollout_stability=0.998722607580324"
            ),
            "decision": "phase47_controlled_128_downsample_seed42_pilot_completed",
            "claim_supported": "Controlled 128x128 full-dataset baseline viability.",
            "claim_not_supported": "Seed-robust conclusion, Level 5, SWE/PINN, strict conservation.",
            "role_in_framework": "Provides the first bounded full-dataset proxy modeling baseline.",
        },
        {
            "phase": "48",
            "phase_name": "No-training full-dataset reliability and physical proxy diagnostics",
            "evidence_type": "post hoc reliability and physical proxy diagnostics",
            "key_artifacts": "analysis/phase48_full_dataset_reliability_physical_proxy",
            "key_result": (
                "evaluated_scenarios=48; evaluated_windows=384; mean_rmse=0.012037189189155709; "
                "mean_mae=0.005252910632811514; mean_wet_dry_iou=0.863043953275997; "
                "mean_false_dry_rate=0.0911363765964386; mean_false_wet_rate=0.003937674554837349; "
                "mean_absolute_relative_volume_bias_proxy=0.021456503649973275; "
                "warning_level_counts=reliable:1,caution:12,high-risk:35"
            ),
            "decision": "phase48_diagnostics_ready_for_warning_framework_extension",
            "claim_supported": "Reliability and physical proxy diagnostic screening for the baseline.",
            "claim_not_supported": "Calibrated probabilities, full mass conservation, hydrodynamic closure.",
            "role_in_framework": "Quantifies operational risk signals without adding training or physics claims.",
        },
        {
            "phase": "49",
            "phase_name": "No-training full-dataset warning framework extension",
            "evidence_type": "diagnostic warning framework",
            "key_artifacts": "analysis/phase49_full_dataset_warning_framework",
            "key_result": (
                "scenario_count=48; warning_level_counts=reliable:1,caution:12,high-risk:35; "
                "high_risk_case_count=35; warning_labels_are_probabilities=false"
            ),
            "decision": "phase49_warning_framework_completed_with_conservative_labels",
            "claim_supported": "Conservative diagnostic warning labels and action mapping.",
            "claim_not_supported": "Calibrated probability warning labels or final production readiness.",
            "role_in_framework": "Converts diagnostics into a cautious use/review framework for reporting.",
        },
    ]


def key_metric_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = [
        {"source_phase": "43", "metric_group": "dataset_inventory", "metric": "total_files", "value": 354, "interpretation": "UrbanFlood24 full dataset file inventory."},
        {"source_phase": "43", "metric_group": "dataset_inventory", "metric": "total_dirs", "value": 186, "interpretation": "UrbanFlood24 full dataset directory inventory."},
        {"source_phase": "43", "metric_group": "dataset_inventory", "metric": "sampled_arrays_count", "value": 54, "interpretation": "Sampled array inspection count."},
        {"source_phase": "43", "metric_group": "dataset_inventory", "metric": "level4_plus_supported", "value": True, "interpretation": "Conservative Level 4+ route can proceed."},
        {"source_phase": "43", "metric_group": "dataset_inventory", "metric": "level5_supported", "value": False, "interpretation": "Level 5 is not supported."},
        {"source_phase": "45", "metric_group": "indexing", "metric": "scenario_count_total", "value": 168, "interpretation": "Indexed full dataset scenarios."},
        {"source_phase": "45", "metric_group": "indexing", "metric": "train_scenarios", "value": 120, "interpretation": "Indexed training scenarios."},
        {"source_phase": "45", "metric_group": "indexing", "metric": "test_scenarios", "value": 48, "interpretation": "Indexed test scenarios."},
        {"source_phase": "45", "metric_group": "indexing", "metric": "static_index_rows", "value": 6, "interpretation": "Static map index rows."},
        {"source_phase": "45", "metric_group": "indexing", "metric": "warning_count", "value": 0, "interpretation": "No pre-existing warning labels in indexing phase."},
        {"source_phase": "45", "metric_group": "shape_distribution", "metric": "flood_shape_(360,1,500,500)", "value": 153, "interpretation": "Flood tensor shape count."},
        {"source_phase": "45", "metric_group": "shape_distribution", "metric": "flood_shape_(480,1,500,500)", "value": 15, "interpretation": "Flood tensor shape count."},
        {"source_phase": "45", "metric_group": "shape_distribution", "metric": "rainfall_length_180", "value": 108, "interpretation": "Rainfall sequence length count."},
        {"source_phase": "45", "metric_group": "shape_distribution", "metric": "rainfall_length_360", "value": 60, "interpretation": "Rainfall sequence length count."},
        {"source_phase": "46", "metric_group": "dataloader_feasibility", "metric": "scenario_index_loaded", "value": True, "interpretation": "Scenario index was readable."},
        {"source_phase": "46", "metric_group": "dataloader_feasibility", "metric": "static_index_loaded", "value": True, "interpretation": "Static index was readable."},
        {"source_phase": "46", "metric_group": "dataloader_feasibility", "metric": "representative_samples_count", "value": 11, "interpretation": "Representative smoke samples checked."},
        {"source_phase": "46", "metric_group": "dataloader_feasibility", "metric": "downsample_128_passed", "value": True, "interpretation": "128x128 downsample path passed."},
        {"source_phase": "46", "metric_group": "dataloader_feasibility", "metric": "downsample_256_passed", "value": True, "interpretation": "256x256 downsample path passed as feasibility only."},
        {"source_phase": "46", "metric_group": "dataloader_feasibility", "metric": "tile_checks_passed", "value": True, "interpretation": "Tile checks passed."},
        {"source_phase": "46", "metric_group": "dataloader_feasibility", "metric": "batch_smoke_passed", "value": True, "interpretation": "Batch smoke check passed."},
        {"source_phase": "46", "metric_group": "dataloader_feasibility", "metric": "memory_safe", "value": True, "interpretation": "Feasibility checks were memory safe."},
        {"source_phase": "47", "metric_group": "controlled_baseline", "metric": "seed", "value": 42, "interpretation": "Single controlled baseline seed."},
        {"source_phase": "47", "metric_group": "controlled_baseline", "metric": "resolution", "value": 128, "interpretation": "Downsample resolution."},
        {"source_phase": "47", "metric_group": "controlled_baseline", "metric": "epochs", "value": 10, "interpretation": "Controlled short baseline duration."},
        {"source_phase": "47", "metric_group": "controlled_baseline", "metric": "train_samples", "value": 960, "interpretation": "Training samples used by the baseline."},
        {"source_phase": "47", "metric_group": "controlled_baseline", "metric": "test_samples", "value": 384, "interpretation": "Test samples used by the baseline."},
        {"source_phase": "47", "metric_group": "controlled_baseline", "metric": "best_test_rmse", "value": 0.01109213042097205, "interpretation": "Best test RMSE from the controlled baseline."},
        {"source_phase": "47", "metric_group": "controlled_baseline", "metric": "test_mae", "value": 0.00525291082279485, "interpretation": "Test MAE from the controlled baseline."},
        {"source_phase": "47", "metric_group": "controlled_baseline", "metric": "test_wet_dry_iou", "value": 0.8255524213115374, "interpretation": "Wet/dry IoU from the controlled baseline."},
        {"source_phase": "47", "metric_group": "controlled_baseline", "metric": "test_rollout_stability", "value": 0.998722607580324, "interpretation": "Rollout stability from the controlled baseline."},
        {"source_phase": "47", "metric_group": "controlled_baseline", "metric": "no_swe_pinn", "value": True, "interpretation": "No SWE/PINN components were used."},
        {"source_phase": "47", "metric_group": "controlled_baseline", "metric": "level5_supported", "value": False, "interpretation": "Level 5 remains unsupported."},
        {"source_phase": "48", "metric_group": "diagnostics", "metric": "evaluated_scenarios", "value": 48, "interpretation": "Test scenarios evaluated by diagnostics."},
        {"source_phase": "48", "metric_group": "diagnostics", "metric": "evaluated_windows", "value": 384, "interpretation": "Evaluation windows checked."},
        {"source_phase": "48", "metric_group": "diagnostics", "metric": "mean_rmse", "value": 0.012037189189155709, "interpretation": "Mean diagnostic RMSE."},
        {"source_phase": "48", "metric_group": "diagnostics", "metric": "mean_mae", "value": 0.005252910632811514, "interpretation": "Mean diagnostic MAE."},
        {"source_phase": "48", "metric_group": "diagnostics", "metric": "mean_wet_dry_iou", "value": 0.863043953275997, "interpretation": "Mean diagnostic wet/dry IoU."},
        {"source_phase": "48", "metric_group": "diagnostics", "metric": "mean_false_dry_rate", "value": 0.0911363765964386, "interpretation": "Mean diagnostic false-dry rate."},
        {"source_phase": "48", "metric_group": "diagnostics", "metric": "mean_false_wet_rate", "value": 0.003937674554837349, "interpretation": "Mean diagnostic false-wet rate."},
        {"source_phase": "48", "metric_group": "diagnostics", "metric": "mean_absolute_relative_volume_bias_proxy", "value": 0.021456503649973275, "interpretation": "Mean physical proxy volume-bias diagnostic."},
        {"source_phase": "48", "metric_group": "diagnostics", "metric": "warning_level_reliable", "value": 1, "interpretation": "Reliable diagnostic screening labels."},
        {"source_phase": "48", "metric_group": "diagnostics", "metric": "warning_level_caution", "value": 12, "interpretation": "Caution diagnostic screening labels."},
        {"source_phase": "48", "metric_group": "diagnostics", "metric": "warning_level_high-risk", "value": 35, "interpretation": "High-risk diagnostic screening labels."},
        {"source_phase": "49", "metric_group": "warning_framework", "metric": "scenario_count", "value": 48, "interpretation": "Scenarios covered by warning framework."},
        {"source_phase": "49", "metric_group": "warning_framework", "metric": "warning_level_reliable", "value": 1, "interpretation": "Reliable warning labels."},
        {"source_phase": "49", "metric_group": "warning_framework", "metric": "warning_level_caution", "value": 12, "interpretation": "Caution warning labels."},
        {"source_phase": "49", "metric_group": "warning_framework", "metric": "warning_level_high-risk", "value": 35, "interpretation": "High-risk warning labels."},
        {"source_phase": "49", "metric_group": "warning_framework", "metric": "high_risk_case_count", "value": 35, "interpretation": "Cases requiring review or supplemental evidence."},
        {"source_phase": "49", "metric_group": "warning_framework", "metric": "warning_labels_are_probabilities", "value": False, "interpretation": "Warning labels are not calibrated probabilities."},
    ]
    for row in rows:
        if isinstance(row["value"], bool):
            row["value"] = bool_text(row["value"])
    return rows


def claim_boundary_rows() -> list[dict[str, str]]:
    return [
        {"claim_status": "supported", "claim": "Level 4+ full-dataset proxy modeling route", "evidence_basis": "Phases 43-49 establish dataset inspection, indexing, dataloader feasibility, controlled 128x128 baseline, diagnostics, and warning extension.", "boundary_or_caveat": "A proxy modeling route is supported; this is not Level 5 or production hydrodynamic validation."},
        {"claim_status": "supported", "claim": "128x128 full-dataset controlled baseline viability", "evidence_basis": "Phase 47 seed42 10e baseline completed with test RMSE, MAE, wet/dry IoU, and rollout stability metrics.", "boundary_or_caveat": "Single-seed short-run evidence only; longer run or replication requires review."},
        {"claim_status": "supported", "claim": "Reliability and physical proxy diagnostics", "evidence_basis": "Phase 48 evaluated 48 scenarios and 384 windows with error, wet/dry, false dry/wet, and volume-bias proxy metrics.", "boundary_or_caveat": "Diagnostics are post hoc screening metrics, not strict conservation or hydrodynamic closure."},
        {"claim_status": "supported", "claim": "Conservative warning framework extension", "evidence_basis": "Phase 49 mapped Phase 48 labels into reliable/caution/high-risk action categories.", "boundary_or_caveat": "Labels are conservative diagnostic screening labels, not calibrated probabilities."},
        {"claim_status": "not_supported", "claim": "Level 5", "evidence_basis": "Phase 43 and Phase 47 explicitly keep level5_supported=false; Phase 44 froze short-term Level 5 claims.", "boundary_or_caveat": "Do not claim Level 5."},
        {"claim_status": "not_supported", "claim": "SWE residual/PINN", "evidence_basis": "Phase 44 froze SWE/PINN claims and Phase 47 records no_swe_pinn=true.", "boundary_or_caveat": "Do not implement or claim SWE residuals or PINN in Phase 50."},
        {"claim_status": "not_supported", "claim": "Strict conservation", "evidence_basis": "Evidence uses proxy diagnostics only and does not solve or enforce conservation laws.", "boundary_or_caveat": "Do not claim strict conservation."},
        {"claim_status": "not_supported", "claim": "Full mass conservation", "evidence_basis": "Phase 48 reports a volume-bias proxy, not a closed mass balance audit.", "boundary_or_caveat": "Do not claim full mass conservation."},
        {"claim_status": "not_supported", "claim": "Hydrodynamic closure", "evidence_basis": "No hydrodynamic governing-equation closure was implemented or validated in Phases 43-50.", "boundary_or_caveat": "Do not claim hydrodynamic closure."},
        {"claim_status": "not_supported", "claim": "Calibrated probability warning labels", "evidence_basis": "Phases 48 and 49 state warning labels are conservative diagnostic screening labels.", "boundary_or_caveat": "Do not interpret warning labels as probabilities or event likelihoods."},
        {"claim_status": "not_supported", "claim": "Final production readiness", "evidence_basis": "The chain is paper-ready synthesis and reviewed-expansion preparation, not deployment validation.", "boundary_or_caveat": "Do not claim final production readiness."},
    ]


def next_step_rows() -> list[dict[str, str]]:
    return [
        {
            "priority": "1",
            "next_step": "Phase 51 reviewed expansion decision",
            "allowed": "allowed",
            "rationale": "A review gate should decide whether evidence justifies any controlled expansion.",
            "guardrails": "No uncontrolled training; preserve Level 4+ boundary; require explicit decision record.",
        },
        {
            "priority": "2",
            "next_step": "128x128 seed42 longer run review",
            "allowed": "allowed_after_review",
            "rationale": "The single 10e baseline supports viability but not duration sensitivity.",
            "guardrails": "Review diagnostics first; keep same model/loss/config family unless separately authorized; no Level 5 claims.",
        },
        {
            "priority": "3",
            "next_step": "128x128 seed replication only after review",
            "allowed": "allowed_after_review",
            "rationale": "Replication can test seed robustness after the Phase 47/48/49 evidence is reviewed.",
            "guardrails": "No sweep expansion; predefine seeds and stopping rules; report failures and warning labels conservatively.",
        },
        {
            "priority": "4",
            "next_step": "256x256 pilot only after explicit authorization",
            "allowed": "not_allowed_without_explicit_authorization",
            "rationale": "Phase 46 showed feasibility only; no 256x256 training evidence exists.",
            "guardrails": "Require written authorization, resource check, and bounded pilot protocol before any run.",
        },
        {
            "priority": "5",
            "next_step": "Warning-framework case reporting",
            "allowed": "allowed",
            "rationale": "High-risk and caution cases should be summarized for paper and review use.",
            "guardrails": "State labels are conservative diagnostic screening labels, not probabilities; include diagnostic drivers.",
        },
        {
            "priority": "6",
            "next_step": "Paper-ready manuscript outline",
            "allowed": "allowed",
            "rationale": "The evidence chain supports a framework contribution outline under conservative claims.",
            "guardrails": "Avoid Level 5, SWE/PINN, conservation, hydrodynamic closure, calibrated probability, and production-readiness claims.",
        },
    ]


def framework_synthesis_payload(output_files: list[str]) -> dict[str, Any]:
    return {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "phase": 50,
        "selected_decision": SELECTED_DECISION,
        "decision_candidates": [
            "phase50_framework_synthesis_ready_for_paper_outline",
            "phase50_framework_synthesis_ready_for_reviewed_expansion_decision",
            "phase50_framework_synthesis_incomplete_missing_phase_artifacts",
            "phase50_framework_synthesis_deferred",
        ],
        "phases_synthesized": PHASES_SYNTHESIZED,
        "level4_plus_route_supported": True,
        "level5_supported": False,
        "no_training": True,
        "no_new_seeds": True,
        "no_sweeps": True,
        "no_model_loss_config_changes": True,
        "no_swe_pinn": True,
        "strict_conservation_supported": False,
        "full_mass_conservation_supported": False,
        "hydrodynamic_closure_supported": False,
        "warning_labels_are_probabilities": False,
        "evidence_chain_summary": [
            "Phase 43 inspected the UrbanFlood24 full dataset and supported only a conservative Level 4+ route.",
            "Phase 44 froze short-term Level 5/SWE/PINN claims and redirected the work to full-dataset proxy modeling.",
            "Phase 45 indexed 168 scenarios with 120 train and 48 test scenarios.",
            "Phase 46 confirmed memory-safe dataloader, downsample, tiling, and batch-smoke feasibility without training.",
            "Phase 47 completed one controlled 128x128 seed42 10e baseline with bounded test metrics.",
            "Phase 48 added no-training reliability and physical proxy diagnostics across 48 scenarios and 384 windows.",
            "Phase 49 converted diagnostics into conservative warning labels and action categories.",
        ],
        "claim_boundary_summary": (
            "The chain supports a paper-ready Level 4+ full-dataset proxy modeling and diagnostic-warning framework. "
            "It does not support Level 5, SWE residual/PINN claims, strict conservation, full mass conservation, "
            "hydrodynamic closure, calibrated probability warning labels, or final production readiness."
        ),
        "recommended_next_action": "Use the Phase 50 synthesis for a paper-ready contribution outline and proceed only to a reviewed Phase 51 expansion decision.",
        "outputs_written": output_files,
    }


def build_framework_markdown(payload: dict[str, Any]) -> str:
    summary = "\n".join(f"- {item}" for item in payload["evidence_chain_summary"])
    return (
        "# Phase 50 Framework Synthesis\n\n"
        f"Selected decision: `{payload['selected_decision']}`\n\n"
        f"Phases synthesized: `{payload['phases_synthesized']}`\n\n"
        "## Guardrail Status\n\n"
        f"- Level 4+ route supported: `{bool_text(payload['level4_plus_route_supported'])}`\n"
        f"- Level 5 supported: `{bool_text(payload['level5_supported'])}`\n"
        f"- No training in Phase 50: `{bool_text(payload['no_training'])}`\n"
        f"- No SWE/PINN in Phase 50: `{bool_text(payload['no_swe_pinn'])}`\n"
        f"- Warning labels are probabilities: `{bool_text(payload['warning_labels_are_probabilities'])}`\n\n"
        "## Concise Evidence Chain\n\n"
        f"{summary}\n\n"
        "## Claim Boundary Summary\n\n"
        f"{payload['claim_boundary_summary']}\n\n"
        "## Recommended Next Action\n\n"
        f"{payload['recommended_next_action']}\n"
    )


def build_paper_outline() -> str:
    return (
        "# Phase 50 Paper-Ready Contribution Outline\n\n"
        "## Suggested Paper Contribution Title\n\n"
        "A Conservative Full-Dataset Proxy Modeling and Diagnostic Warning Framework for UrbanFlood24 Flood Prediction\n\n"
        "## Core Research Contribution\n\n"
        "This work contributes a paper-ready Level 4+ framework that consolidates full-dataset inspection, indexing, "
        "memory-safe data loading, controlled downsample baseline modeling, reliability diagnostics, physical proxy "
        "diagnostics, and conservative warning labels for UrbanFlood24 flood prediction.\n\n"
        "## Dataset and Evidence Chain Paragraph\n\n"
        "The evidence chain begins with UrbanFlood24 full-dataset inspection covering 354 files, 186 directories, "
        "and 54 sampled arrays. It then indexes 168 scenarios, including 120 train scenarios and 48 test scenarios, "
        "with six static-index rows and documented flood-shape and rainfall-length distributions. These steps support "
        "a full-dataset Level 4+ proxy modeling route while keeping Level 5 unsupported.\n\n"
        "## Method/Framework Paragraph\n\n"
        "The framework uses a no-training feasibility stage to verify scenario and static indexes, representative "
        "samples, 128x128 and 256x256 downsample paths, tiling checks, batch smoke checks, and memory-safe loading. "
        "A single controlled 128x128 seed42 10-epoch baseline then provides bounded proxy-modeling evidence without "
        "modifying the model, loss, or configuration family beyond the authorized baseline protocol.\n\n"
        "## Results Paragraph\n\n"
        "The controlled 128x128 baseline used 960 training samples and 384 test samples, achieving best test "
        "RMSE 0.01109213042097205, test MAE 0.00525291082279485, test wet/dry IoU 0.8255524213115374, and test "
        "rollout stability 0.998722607580324. These results support baseline viability, not seed robustness or "
        "production readiness.\n\n"
        "## Reliability/Warning Framework Paragraph\n\n"
        "No-training diagnostics evaluated 48 scenarios and 384 windows, with mean RMSE 0.012037189189155709, "
        "mean MAE 0.005252910632811514, mean wet/dry IoU 0.863043953275997, mean false-dry rate "
        "0.0911363765964386, mean false-wet rate 0.003937674554837349, and mean absolute relative volume-bias "
        "proxy 0.021456503649973275. The warning framework assigns 1 reliable, 12 caution, and 35 high-risk labels. "
        "These warning labels are conservative diagnostic screening labels, not calibrated probabilities.\n\n"
        "## Limitations Paragraph\n\n"
        "The current evidence does not support Level 5, SWE residual or PINN claims, strict conservation, full mass "
        "conservation, hydrodynamic closure, calibrated probability warning labels, or final production readiness. "
        "The controlled baseline is a single seed42 10-epoch run at 128x128 resolution, so broader training claims "
        "require reviewed expansion.\n\n"
        "## Next-Step Paragraph\n\n"
        "The recommended next step is a Phase 51 reviewed expansion decision. Conservative options include reviewing "
        "a longer 128x128 seed42 run, considering seed replication only after review, allowing a 256x256 pilot only "
        "after explicit authorization, reporting warning-framework cases, and using this outline for manuscript "
        "development under the stated claim boundaries.\n"
    )


def synthesize(output_dir: Path) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)

    evidence_path = output_dir / "phase50_evidence_chain_table.csv"
    metrics_path = output_dir / "phase50_key_metrics_summary.csv"
    claims_path = output_dir / "phase50_claim_boundary_table.csv"
    steps_path = output_dir / "phase50_recommended_next_steps.csv"
    json_path = output_dir / "phase50_framework_synthesis.json"
    md_path = output_dir / "phase50_framework_synthesis.md"
    outline_path = output_dir / "phase50_paper_ready_contribution_outline.md"

    write_csv_rows(
        evidence_path,
        phase_evidence_rows(),
        [
            "phase",
            "phase_name",
            "evidence_type",
            "key_artifacts",
            "key_result",
            "decision",
            "claim_supported",
            "claim_not_supported",
            "role_in_framework",
        ],
    )
    write_csv_rows(
        metrics_path,
        key_metric_rows(),
        ["source_phase", "metric_group", "metric", "value", "interpretation"],
    )
    write_csv_rows(
        claims_path,
        claim_boundary_rows(),
        ["claim_status", "claim", "evidence_basis", "boundary_or_caveat"],
    )
    write_csv_rows(
        steps_path,
        next_step_rows(),
        ["priority", "next_step", "allowed", "rationale", "guardrails"],
    )

    output_files = [
        display_path(evidence_path),
        display_path(metrics_path),
        display_path(claims_path),
        display_path(steps_path),
        display_path(json_path),
        display_path(md_path),
        display_path(outline_path),
    ]
    payload = framework_synthesis_payload(output_files)
    write_json(json_path, payload)
    md_path.write_text(build_framework_markdown(payload), encoding="utf-8")
    outline_path.write_text(build_paper_outline(), encoding="utf-8")
    return payload


def main() -> None:
    args = parse_args()
    output_dir = repo_path(args.output_dir)
    payload = synthesize(output_dir)

    print(f"phases_synthesized: {payload['phases_synthesized']}")
    print(f"selected_decision: {payload['selected_decision']}")
    print(f"level4_plus_route_supported: {bool_text(payload['level4_plus_route_supported'])}")
    print(f"level5_supported: {bool_text(payload['level5_supported'])}")
    print(f"no_training: {bool_text(payload['no_training'])}")
    print(f"warning_labels_are_probabilities: {bool_text(payload['warning_labels_are_probabilities'])}")
    print("outputs_written:")
    for output in payload["outputs_written"]:
        print(f"- {output}")


if __name__ == "__main__":
    main()
