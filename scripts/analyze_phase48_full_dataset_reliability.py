from __future__ import annotations

import csv
import json
import math
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import torch


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from train_phase47_full_downsample_baseline import (  # noqa: E402
    build_datasets,
    build_model,
    load_json,
    make_loader,
    path_text,
    rel_text,
    set_seed,
    validate_indexes,
    validate_phase47_config,
    validate_row_shapes,
)


CONFIG_PATH = Path("configs/train_phase47_full_downsample128_seed42_10e.json")
PHASE47_ANALYSIS_DIR = Path("analysis/phase47_controlled_downsample_baseline")
PHASE47_OUTPUT_DIR = Path("runs/phase47_full_downsample128_baseline_seed42_10e")
PHASE48_OUTPUT_DIR = Path("analysis/phase48_full_dataset_reliability_physical_proxy")

REQUIRED_PHASE47_ARTIFACTS = (
    PHASE47_ANALYSIS_DIR / "metrics.csv",
    PHASE47_ANALYSIS_DIR / "metrics.json",
    PHASE47_ANALYSIS_DIR / "phase47_training_summary.json",
)

DECISION_READY = "phase48_diagnostics_ready_for_warning_framework_extension"
DECISION_MISSING = "phase48_diagnostics_completed_with_missing_prediction_artifacts"
DECISION_BLOCKED = "phase48_diagnostics_blocked_by_checkpoint_or_artifact_issue"
DECISION_REQUIRES_EVAL = "phase48_diagnostics_requires_evaluation_pass"

EPS = 1.0e-8


@dataclass
class MetricAccumulator:
    sample_ids: set[str] = field(default_factory=set)
    sse: float = 0.0
    sae: float = 0.0
    count: int = 0
    intersection: int = 0
    union: int = 0
    false_dry: int = 0
    false_wet: int = 0
    target_wet: int = 0
    target_dry: int = 0
    pred_wet: int = 0
    target_sum: float = 0.0
    pred_sum: float = 0.0
    max_target: float = 0.0
    max_pred: float = 0.0

    def update(
        self,
        *,
        sample_id: str,
        pred: torch.Tensor,
        target: torch.Tensor,
        pred_wet: torch.Tensor,
        target_wet: torch.Tensor,
    ) -> None:
        diff = pred - target
        self.sample_ids.add(sample_id)
        self.sse += float(torch.sum(diff * diff).item())
        self.sae += float(torch.sum(torch.abs(diff)).item())
        self.count += int(diff.numel())

        intersection = pred_wet & target_wet
        union = pred_wet | target_wet
        false_dry = target_wet & ~pred_wet
        false_wet = pred_wet & ~target_wet
        target_dry = ~target_wet

        self.intersection += int(intersection.sum().item())
        self.union += int(union.sum().item())
        self.false_dry += int(false_dry.sum().item())
        self.false_wet += int(false_wet.sum().item())
        self.target_wet += int(target_wet.sum().item())
        self.target_dry += int(target_dry.sum().item())
        self.pred_wet += int(pred_wet.sum().item())

        self.target_sum += float(target.sum().item())
        self.pred_sum += float(pred.sum().item())
        self.max_target = max(self.max_target, float(target.max().item()))
        self.max_pred = max(self.max_pred, float(pred.max().item()))

    def as_metrics(self) -> dict[str, float | int]:
        rmse = math.sqrt(self.sse / self.count) if self.count else 0.0
        mae = self.sae / self.count if self.count else 0.0
        iou = self.intersection / self.union if self.union else 1.0
        false_dry_rate = self.false_dry / self.target_wet if self.target_wet else 0.0
        false_wet_rate = self.false_wet / self.target_dry if self.target_dry else 0.0
        target_wet_fraction = self.target_wet / self.count if self.count else 0.0
        pred_wet_fraction = self.pred_wet / self.count if self.count else 0.0
        mean_target_depth = self.target_sum / self.count if self.count else 0.0
        mean_pred_depth = self.pred_sum / self.count if self.count else 0.0
        volume_bias = self.pred_sum - self.target_sum
        relative_volume_bias = volume_bias / max(abs(self.target_sum), EPS)
        peak_under = max(0.0, self.max_target - self.max_pred)
        return {
            "sample_count": len(self.sample_ids),
            "rmse": rmse,
            "mae": mae,
            "wet_dry_iou": iou,
            "false_dry_rate": false_dry_rate,
            "false_wet_rate": false_wet_rate,
            "target_wet_fraction": target_wet_fraction,
            "pred_wet_fraction": pred_wet_fraction,
            "mean_target_depth": mean_target_depth,
            "mean_pred_depth": mean_pred_depth,
            "max_target_depth": self.max_target,
            "max_pred_depth": self.max_pred,
            "absolute_volume_bias_proxy": abs(volume_bias),
            "relative_volume_bias_proxy": relative_volume_bias,
            "absolute_relative_volume_bias_proxy": abs(relative_volume_bias),
            "peak_depth_underprediction_proxy": peak_under,
        }


@dataclass
class PeakAccumulator:
    best_target: float = -math.inf
    pred_at_best_target: float = 0.0
    target_peak_global_step: int | None = None
    best_pred: float = -math.inf
    pred_peak_global_step: int | None = None

    def update(self, *, target_peak: float, pred_peak: float, global_step: int) -> None:
        if target_peak > self.best_target:
            self.best_target = target_peak
            self.pred_at_best_target = pred_peak
            self.target_peak_global_step = global_step
        if pred_peak > self.best_pred:
            self.best_pred = pred_peak
            self.pred_peak_global_step = global_step

    def as_metrics(self) -> dict[str, float | int | None]:
        target = 0.0 if self.best_target == -math.inf else self.best_target
        pred = 0.0 if self.best_pred == -math.inf else self.best_pred
        timing_error = None
        if self.target_peak_global_step is not None and self.pred_peak_global_step is not None:
            timing_error = abs(self.pred_peak_global_step - self.target_peak_global_step)
        return {
            "peak_target_depth": target,
            "peak_pred_depth": pred,
            "peak_depth_underprediction_proxy": max(0.0, target - pred),
            "peak_timing_error_proxy": timing_error,
            "target_peak_global_step": self.target_peak_global_step,
            "pred_peak_global_step": self.pred_peak_global_step,
        }


def repo_path(path: str | Path) -> Path:
    candidate = Path(path).expanduser()
    return candidate if candidate.is_absolute() else REPO_ROOT / candidate


def bool_text(value: bool) -> str:
    return str(bool(value)).lower()


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fieldnames})


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def validate_phase48_config(config: dict[str, Any]) -> None:
    validate_phase47_config(config)
    required = {
        "resolution": 128,
        "seed": 42,
        "no_swe_pinn": True,
        "level5_supported": False,
        "output_dir": rel_text(PHASE47_OUTPUT_DIR),
    }
    for key, expected in required.items():
        actual = config.get(key)
        if key == "output_dir":
            actual = rel_text(actual)
        if actual != expected:
            raise ValueError(f"Phase 48 requires config {key}={expected!r}, got {actual!r}.")


def find_checkpoint(checkpoints_dir: Path) -> Path | None:
    if not checkpoints_dir.exists():
        return None
    best_candidates = sorted(checkpoints_dir.glob("*best*.pt"), key=lambda path: path.stat().st_mtime, reverse=True)
    if best_candidates:
        return best_candidates[0]
    all_candidates = sorted(checkpoints_dir.glob("*.pt"), key=lambda path: path.stat().st_mtime, reverse=True)
    return all_candidates[0] if all_candidates else None


def base_readiness(
    *,
    config_valid: bool,
    checkpoint_path: Path | None,
    artifact_status: dict[str, bool],
    selected_decision: str,
    diagnostics_executed: bool,
    notes: list[str],
) -> dict[str, Any]:
    return {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "phase": 48,
        "config_path": path_text(repo_path(CONFIG_PATH)),
        "config_valid": config_valid,
        "checkpoint_found": checkpoint_path is not None,
        "checkpoint_path": path_text(checkpoint_path) if checkpoint_path else None,
        "phase47_artifacts": artifact_status,
        "diagnostics_executed": diagnostics_executed,
        "evaluated_split": "test",
        "selected_decision": selected_decision,
        "no_training": True,
        "no_swe_pinn": True,
        "level5_supported": False,
        "notes": notes,
    }


def write_summary_md(path: Path, summary: dict[str, Any]) -> None:
    thresholds = summary.get("warning_thresholds", {})
    lines = [
        "# Phase 48 Full-Dataset Reliability And Physical Proxy Diagnostics",
        "",
        f"- selected_decision: `{summary['selected_decision']}`",
        f"- checkpoint_found: `{bool_text(summary['checkpoint_found'])}`",
        f"- checkpoint_path: `{summary.get('checkpoint_path')}`",
        f"- diagnostics_executed: `{bool_text(summary['diagnostics_executed'])}`",
        f"- evaluated_split: `{summary['evaluated_split']}`",
        f"- evaluated_scenarios: `{summary['evaluated_scenarios']}`",
        f"- evaluated_windows: `{summary['evaluated_windows']}`",
        f"- mean_rmse: `{summary.get('mean_rmse')}`",
        f"- mean_mae: `{summary.get('mean_mae')}`",
        f"- mean_wet_dry_iou: `{summary.get('mean_wet_dry_iou')}`",
        f"- mean_false_dry_rate: `{summary.get('mean_false_dry_rate')}`",
        f"- mean_false_wet_rate: `{summary.get('mean_false_wet_rate')}`",
        f"- mean_absolute_relative_volume_bias_proxy: `{summary.get('mean_absolute_relative_volume_bias_proxy')}`",
        f"- warning_level_counts: `{summary.get('warning_level_counts')}`",
        f"- no_training: `{bool_text(summary['no_training'])}`",
        f"- no_swe_pinn: `{bool_text(summary['no_swe_pinn'])}`",
        f"- level5_supported: `{bool_text(summary['level5_supported'])}`",
        "",
        "## Warning Thresholds",
        "",
        (
            "Scenario labels are conservative distribution-derived screening labels, not calibrated "
            "probabilities. A scenario is `reliable` only when RMSE is at or below the lower-tercile "
            "threshold, wet/dry IoU is at or above the upper-tercile threshold, and false-dry, "
            "false-wet, and absolute relative volume-bias proxies are not above their upper-tercile "
            "thresholds. A scenario is `high-risk` when any upper-quartile error proxy is triggered "
            "or wet/dry IoU is at or below its lower-quartile threshold. Remaining scenarios are "
            "`caution`."
        ),
        "",
        f"- rmse_reliable_max: `{thresholds.get('rmse_reliable_max')}`",
        f"- wet_dry_iou_reliable_min: `{thresholds.get('wet_dry_iou_reliable_min')}`",
        f"- rmse_high_risk_min: `{thresholds.get('rmse_high_risk_min')}`",
        f"- wet_dry_iou_high_risk_max: `{thresholds.get('wet_dry_iou_high_risk_max')}`",
        "",
        "## Scope Notes",
        "",
        "These diagnostics are Level 4+ reliability and physical proxy diagnostics only. They do not implement SWE residuals, PINN components, strict conservation, full mass conservation, hydrodynamic closure, Level 5 support, or any training.",
        "",
        f"Next recommended action: {summary['next_recommended_action']}",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def blocked_outputs(reason: str, *, config_valid: bool = False, checkpoint_path: Path | None = None) -> None:
    output_dir = repo_path(PHASE48_OUTPUT_DIR)
    output_dir.mkdir(parents=True, exist_ok=True)
    artifact_status = {rel_text(path): repo_path(path).exists() for path in REQUIRED_PHASE47_ARTIFACTS}
    readiness = base_readiness(
        config_valid=config_valid,
        checkpoint_path=checkpoint_path,
        artifact_status=artifact_status,
        selected_decision=DECISION_BLOCKED,
        diagnostics_executed=False,
        notes=[reason],
    )
    summary = {
        **readiness,
        "evaluated_scenarios": 0,
        "evaluated_windows": 0,
        "mean_rmse": None,
        "mean_mae": None,
        "mean_wet_dry_iou": None,
        "mean_false_dry_rate": None,
        "mean_false_wet_rate": None,
        "mean_absolute_relative_volume_bias_proxy": None,
        "warning_level_counts": {},
        "worst_scenarios_by_rmse": [],
        "worst_scenarios_by_false_dry": [],
        "worst_scenarios_by_volume_bias": [],
        "next_recommended_action": "Resolve checkpoint or required Phase 47 artifact availability, then rerun Phase 48 diagnostics.",
    }
    write_json(output_dir / "phase48_diagnostic_readiness.json", readiness)
    write_json(output_dir / "phase48_reliability_summary.json", summary)
    write_summary_md(output_dir / "phase48_reliability_summary.md", summary)
    print_terminal_summary(summary)


def quantile(values: list[float], q: float) -> float:
    if not values:
        return 0.0
    return float(np.quantile(np.asarray(values, dtype=np.float64), q))


def attach_warning_levels(scenario_rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, float]]:
    rmse_values = [float(row["rmse"]) for row in scenario_rows]
    iou_values = [float(row["wet_dry_iou"]) for row in scenario_rows]
    false_dry_values = [float(row["false_dry_rate"]) for row in scenario_rows]
    false_wet_values = [float(row["false_wet_rate"]) for row in scenario_rows]
    volume_values = [float(row["absolute_relative_volume_bias_proxy"]) for row in scenario_rows]
    thresholds = {
        "rmse_reliable_max": quantile(rmse_values, 1.0 / 3.0),
        "wet_dry_iou_reliable_min": quantile(iou_values, 2.0 / 3.0),
        "false_dry_reliable_max": quantile(false_dry_values, 2.0 / 3.0),
        "false_wet_reliable_max": quantile(false_wet_values, 2.0 / 3.0),
        "absolute_relative_volume_bias_reliable_max": quantile(volume_values, 2.0 / 3.0),
        "rmse_high_risk_min": quantile(rmse_values, 0.75),
        "wet_dry_iou_high_risk_max": quantile(iou_values, 0.25),
        "false_dry_high_risk_min": quantile(false_dry_values, 0.75),
        "false_wet_high_risk_min": quantile(false_wet_values, 0.75),
        "absolute_relative_volume_bias_high_risk_min": quantile(volume_values, 0.75),
    }

    labeled_rows: list[dict[str, Any]] = []
    for row in scenario_rows:
        rmse = float(row["rmse"])
        iou = float(row["wet_dry_iou"])
        false_dry = float(row["false_dry_rate"])
        false_wet = float(row["false_wet_rate"])
        volume = float(row["absolute_relative_volume_bias_proxy"])
        reliable = (
            rmse <= thresholds["rmse_reliable_max"]
            and iou >= thresholds["wet_dry_iou_reliable_min"]
            and false_dry <= thresholds["false_dry_reliable_max"]
            and false_wet <= thresholds["false_wet_reliable_max"]
            and volume <= thresholds["absolute_relative_volume_bias_reliable_max"]
        )
        high_risk = (
            rmse >= thresholds["rmse_high_risk_min"]
            or iou <= thresholds["wet_dry_iou_high_risk_max"]
            or false_dry >= thresholds["false_dry_high_risk_min"]
            or false_wet >= thresholds["false_wet_high_risk_min"]
            or volume >= thresholds["absolute_relative_volume_bias_high_risk_min"]
        )
        if reliable:
            level = "reliable"
        elif high_risk:
            level = "high-risk"
        else:
            level = "caution"
        labeled = dict(row)
        labeled["warning_level"] = level
        labeled_rows.append(labeled)
    return labeled_rows, thresholds


def grouped_summary(scenario_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in scenario_rows:
        groups[(str(row["location"]), str(row["scenario_type"]))].append(row)

    output: list[dict[str, Any]] = []
    for (location, scenario_type), rows in sorted(groups.items()):
        output.append(
            {
                "location": location,
                "scenario_type": scenario_type,
                "scenario_count": len(rows),
                "mean_rmse": float(np.mean([float(row["rmse"]) for row in rows])),
                "mean_mae": float(np.mean([float(row["mae"]) for row in rows])),
                "mean_wet_dry_iou": float(np.mean([float(row["wet_dry_iou"]) for row in rows])),
                "mean_false_dry_rate": float(np.mean([float(row["false_dry_rate"]) for row in rows])),
                "mean_false_wet_rate": float(np.mean([float(row["false_wet_rate"]) for row in rows])),
                "mean_absolute_relative_volume_bias_proxy": float(
                    np.mean([float(row["absolute_relative_volume_bias_proxy"]) for row in rows])
                ),
            }
        )
    return output


def row_key(metadata: dict[str, Any]) -> tuple[str, str, str, str]:
    return (
        str(metadata["split"]),
        str(metadata["location"]),
        str(metadata["scenario"]),
        str(metadata["scenario_type"]),
    )


def run_diagnostics(config: dict[str, Any], checkpoint_path: Path) -> dict[str, Any]:
    scenario_rows, _static_rows = validate_indexes(config)
    validate_row_shapes(scenario_rows)
    _train_dataset, test_dataset = build_datasets(config, scenario_rows)

    device = torch.device(config["runtime"]["device"] if torch.cuda.is_available() else "cpu")
    loader = make_loader(
        test_dataset,
        batch_size=int(config["optimization"]["eval_batch_size"]),
        shuffle=False,
        config=config,
    )
    model = build_model(config).to(device)
    checkpoint = torch.load(checkpoint_path, map_location=device)
    state_dict = checkpoint.get("model_state", checkpoint)
    model.load_state_dict(state_dict)
    model.eval()

    wet_threshold = float(config["metrics"]["wet_threshold"])
    scenario_acc: dict[tuple[str, str, str, str], MetricAccumulator] = defaultdict(MetricAccumulator)
    step_acc: dict[int, MetricAccumulator] = defaultdict(MetricAccumulator)
    peak_acc: dict[tuple[str, str, str, str], PeakAccumulator] = defaultdict(PeakAccumulator)

    with torch.no_grad():
        for batch in loader:
            past_flood = batch["past_flood"].float().to(device)
            past_rainfall = batch["past_rainfall"].float().to(device)
            future_rainfall = batch["future_rainfall"].float().to(device)
            static_maps = batch["static_maps"].float().to(device)
            target = batch["future_flood"].float().to(device)
            pred = model(past_flood, past_rainfall, future_rainfall, static_maps)
            if pred.shape != target.shape:
                raise ValueError(f"Prediction shape {tuple(pred.shape)} != target shape {tuple(target.shape)}.")

            pred_wet = pred >= wet_threshold
            target_wet = target >= wet_threshold
            for sample_index, metadata in enumerate(batch["metadata"]):
                key = row_key(metadata)
                start_idx = int(metadata["start_idx"])
                sample_id = f"{key[1]}/{key[2]}/start{start_idx}"
                scenario_acc[key].update(
                    sample_id=sample_id,
                    pred=pred[sample_index],
                    target=target[sample_index],
                    pred_wet=pred_wet[sample_index],
                    target_wet=target_wet[sample_index],
                )
                for step in range(pred.shape[1]):
                    global_step = start_idx + int(metadata["input_steps"]) + step
                    step_sample_id = f"{sample_id}/step{step}"
                    step_acc[step].update(
                        sample_id=step_sample_id,
                        pred=pred[sample_index, step],
                        target=target[sample_index, step],
                        pred_wet=pred_wet[sample_index, step],
                        target_wet=target_wet[sample_index, step],
                    )
                    peak_acc[key].update(
                        target_peak=float(target[sample_index, step].max().item()),
                        pred_peak=float(pred[sample_index, step].max().item()),
                        global_step=global_step,
                    )

    scenario_metric_rows: list[dict[str, Any]] = []
    for key, acc in sorted(scenario_acc.items()):
        split, location, scenario, scenario_type = key
        scenario_metric_rows.append(
            {
                "split": split,
                "location": location,
                "scenario": scenario,
                "scenario_type": scenario_type,
                **acc.as_metrics(),
            }
        )

    scenario_metric_rows, warning_thresholds = attach_warning_levels(scenario_metric_rows)

    step_metric_rows = []
    for step, acc in sorted(step_acc.items()):
        metrics = acc.as_metrics()
        step_metric_rows.append(
            {
                "window_step": step,
                "sample_count": metrics["sample_count"],
                "rmse": metrics["rmse"],
                "mae": metrics["mae"],
                "wet_dry_iou": metrics["wet_dry_iou"],
                "false_dry_rate": metrics["false_dry_rate"],
                "false_wet_rate": metrics["false_wet_rate"],
                "mean_target_depth": metrics["mean_target_depth"],
                "mean_pred_depth": metrics["mean_pred_depth"],
                "volume_bias_proxy": metrics["relative_volume_bias_proxy"],
            }
        )

    wet_dry_rows = [
        {
            "split": row["split"],
            "location": row["location"],
            "scenario": row["scenario"],
            "scenario_type": row["scenario_type"],
            "false_dry_rate": row["false_dry_rate"],
            "false_wet_rate": row["false_wet_rate"],
            "wet_dry_iou": row["wet_dry_iou"],
        }
        for row in scenario_metric_rows
    ]

    peak_rows = []
    for key, acc in sorted(peak_acc.items()):
        split, location, scenario, scenario_type = key
        peak_rows.append(
            {
                "split": split,
                "location": location,
                "scenario": scenario,
                "scenario_type": scenario_type,
                **acc.as_metrics(),
            }
        )

    volume_rows = [
        {
            "split": row["split"],
            "location": row["location"],
            "scenario": row["scenario"],
            "scenario_type": row["scenario_type"],
            "sum_target_depth": scenario_acc[
                (row["split"], row["location"], row["scenario"], row["scenario_type"])
            ].target_sum,
            "sum_pred_depth": scenario_acc[
                (row["split"], row["location"], row["scenario"], row["scenario_type"])
            ].pred_sum,
            "volume_bias_proxy": row["relative_volume_bias_proxy"],
            "relative_volume_bias_proxy": row["relative_volume_bias_proxy"],
            "absolute_relative_volume_bias_proxy": row["absolute_relative_volume_bias_proxy"],
        }
        for row in scenario_metric_rows
    ]
    location_rows = grouped_summary(scenario_metric_rows)
    warning_rows = [
        {
            "split": row["split"],
            "location": row["location"],
            "scenario": row["scenario"],
            "scenario_type": row["scenario_type"],
            "rmse": row["rmse"],
            "wet_dry_iou": row["wet_dry_iou"],
            "false_dry_rate": row["false_dry_rate"],
            "false_wet_rate": row["false_wet_rate"],
            "absolute_relative_volume_bias_proxy": row["absolute_relative_volume_bias_proxy"],
            "warning_level": row["warning_level"],
        }
        for row in scenario_metric_rows
    ]

    output_dir = repo_path(PHASE48_OUTPUT_DIR)
    scenario_fields = [
        "split",
        "location",
        "scenario",
        "scenario_type",
        "sample_count",
        "rmse",
        "mae",
        "wet_dry_iou",
        "false_dry_rate",
        "false_wet_rate",
        "target_wet_fraction",
        "pred_wet_fraction",
        "mean_target_depth",
        "mean_pred_depth",
        "max_target_depth",
        "max_pred_depth",
        "absolute_volume_bias_proxy",
        "relative_volume_bias_proxy",
        "absolute_relative_volume_bias_proxy",
        "peak_depth_underprediction_proxy",
        "warning_level",
    ]
    write_csv(output_dir / "scenario_reliability_metrics.csv", scenario_metric_rows, scenario_fields)
    write_csv(
        output_dir / "step_reliability_metrics.csv",
        step_metric_rows,
        [
            "window_step",
            "sample_count",
            "rmse",
            "mae",
            "wet_dry_iou",
            "false_dry_rate",
            "false_wet_rate",
            "mean_target_depth",
            "mean_pred_depth",
            "volume_bias_proxy",
        ],
    )
    write_csv(
        output_dir / "wet_dry_error_metrics.csv",
        wet_dry_rows,
        ["split", "location", "scenario", "scenario_type", "false_dry_rate", "false_wet_rate", "wet_dry_iou"],
    )
    write_csv(
        output_dir / "peak_depth_timing_metrics.csv",
        peak_rows,
        [
            "split",
            "location",
            "scenario",
            "scenario_type",
            "peak_target_depth",
            "peak_pred_depth",
            "peak_depth_underprediction_proxy",
            "peak_timing_error_proxy",
            "target_peak_global_step",
            "pred_peak_global_step",
        ],
    )
    write_csv(
        output_dir / "volume_response_proxy_metrics.csv",
        volume_rows,
        [
            "split",
            "location",
            "scenario",
            "scenario_type",
            "sum_target_depth",
            "sum_pred_depth",
            "volume_bias_proxy",
            "relative_volume_bias_proxy",
            "absolute_relative_volume_bias_proxy",
        ],
    )
    write_csv(
        output_dir / "location_type_summary.csv",
        location_rows,
        [
            "location",
            "scenario_type",
            "scenario_count",
            "mean_rmse",
            "mean_mae",
            "mean_wet_dry_iou",
            "mean_false_dry_rate",
            "mean_false_wet_rate",
            "mean_absolute_relative_volume_bias_proxy",
        ],
    )
    write_csv(
        output_dir / "reliability_warning_levels.csv",
        warning_rows,
        [
            "split",
            "location",
            "scenario",
            "scenario_type",
            "rmse",
            "wet_dry_iou",
            "false_dry_rate",
            "false_wet_rate",
            "absolute_relative_volume_bias_proxy",
            "warning_level",
        ],
    )

    warning_counts = dict(Counter(row["warning_level"] for row in scenario_metric_rows))
    mean = lambda key: float(np.mean([float(row[key]) for row in scenario_metric_rows])) if scenario_metric_rows else None
    summary = {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "phase": 48,
        "checkpoint_found": True,
        "checkpoint_path": path_text(checkpoint_path),
        "diagnostics_executed": True,
        "evaluated_split": "test",
        "evaluated_scenarios": len(scenario_metric_rows),
        "evaluated_windows": len(test_dataset),
        "selected_decision": DECISION_READY,
        "mean_rmse": mean("rmse"),
        "mean_mae": mean("mae"),
        "mean_wet_dry_iou": mean("wet_dry_iou"),
        "mean_false_dry_rate": mean("false_dry_rate"),
        "mean_false_wet_rate": mean("false_wet_rate"),
        "mean_absolute_relative_volume_bias_proxy": mean("absolute_relative_volume_bias_proxy"),
        "warning_level_counts": warning_counts,
        "warning_thresholds": warning_thresholds,
        "worst_scenarios_by_rmse": sorted(
            scenario_metric_rows, key=lambda row: float(row["rmse"]), reverse=True
        )[:5],
        "worst_scenarios_by_false_dry": sorted(
            scenario_metric_rows, key=lambda row: float(row["false_dry_rate"]), reverse=True
        )[:5],
        "worst_scenarios_by_volume_bias": sorted(
            scenario_metric_rows,
            key=lambda row: float(row["absolute_relative_volume_bias_proxy"]),
            reverse=True,
        )[:5],
        "no_training": True,
        "no_swe_pinn": True,
        "level5_supported": False,
        "next_recommended_action": "Extend the warning framework using Phase 48 scenario labels as conservative diagnostics, not calibrated probabilities.",
        "outputs": {
            "phase48_diagnostic_readiness_json": path_text(output_dir / "phase48_diagnostic_readiness.json"),
            "scenario_reliability_metrics_csv": path_text(output_dir / "scenario_reliability_metrics.csv"),
            "step_reliability_metrics_csv": path_text(output_dir / "step_reliability_metrics.csv"),
            "wet_dry_error_metrics_csv": path_text(output_dir / "wet_dry_error_metrics.csv"),
            "peak_depth_timing_metrics_csv": path_text(output_dir / "peak_depth_timing_metrics.csv"),
            "volume_response_proxy_metrics_csv": path_text(output_dir / "volume_response_proxy_metrics.csv"),
            "location_type_summary_csv": path_text(output_dir / "location_type_summary.csv"),
            "reliability_warning_levels_csv": path_text(output_dir / "reliability_warning_levels.csv"),
            "phase48_reliability_summary_json": path_text(output_dir / "phase48_reliability_summary.json"),
            "phase48_reliability_summary_md": path_text(output_dir / "phase48_reliability_summary.md"),
        },
    }
    return summary


def print_terminal_summary(summary: dict[str, Any]) -> None:
    print(f"checkpoint_found={bool_text(summary.get('checkpoint_found', False))}")
    print(f"diagnostics_executed={bool_text(summary.get('diagnostics_executed', False))}")
    print(f"evaluated_scenarios={summary.get('evaluated_scenarios', 0)}")
    print(f"evaluated_windows={summary.get('evaluated_windows', 0)}")
    print(f"selected_decision={summary.get('selected_decision')}")
    print(f"mean_rmse={summary.get('mean_rmse')}")
    print(f"mean_mae={summary.get('mean_mae')}")
    print(f"mean_wet_dry_iou={summary.get('mean_wet_dry_iou')}")
    print(f"warning_level_counts={summary.get('warning_level_counts', {})}")
    print(f"no_training={bool_text(summary.get('no_training', True))}")


def main() -> None:
    output_dir = repo_path(PHASE48_OUTPUT_DIR)
    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        config = load_json(CONFIG_PATH)
        validate_phase48_config(config)
    except Exception as exc:
        blocked_outputs(f"Config validation failed: {exc}", config_valid=False)
        return

    artifact_status = {rel_text(path): repo_path(path).exists() for path in REQUIRED_PHASE47_ARTIFACTS}
    if not all(artifact_status.values()):
        missing = [path for path, exists in artifact_status.items() if not exists]
        blocked_outputs(f"Missing required Phase 47 artifacts: {missing}", config_valid=True)
        return

    checkpoint_path = find_checkpoint(repo_path(PHASE47_OUTPUT_DIR) / "checkpoints")
    if checkpoint_path is None:
        blocked_outputs("No Phase 47 checkpoint found under the expected checkpoints directory.", config_valid=True)
        return

    set_seed(int(config["seed"]))
    readiness = base_readiness(
        config_valid=True,
        checkpoint_path=checkpoint_path,
        artifact_status=artifact_status,
        selected_decision=DECISION_REQUIRES_EVAL,
        diagnostics_executed=False,
        notes=["Checkpoint and required Phase 47 artifacts found; evaluation pass pending."],
    )
    write_json(output_dir / "phase48_diagnostic_readiness.json", readiness)

    try:
        summary = run_diagnostics(config, checkpoint_path)
    except FileNotFoundError as exc:
        summary = {
            **readiness,
            "selected_decision": DECISION_MISSING,
            "evaluated_scenarios": 0,
            "evaluated_windows": 0,
            "mean_rmse": None,
            "mean_mae": None,
            "mean_wet_dry_iou": None,
            "mean_false_dry_rate": None,
            "mean_false_wet_rate": None,
            "mean_absolute_relative_volume_bias_proxy": None,
            "warning_level_counts": {},
            "worst_scenarios_by_rmse": [],
            "worst_scenarios_by_false_dry": [],
            "worst_scenarios_by_volume_bias": [],
            "next_recommended_action": f"Restore missing read-only dataset or prediction artifact and rerun diagnostics: {exc}",
        }
    except Exception as exc:
        blocked_outputs(f"Diagnostic evaluation failed: {exc}", config_valid=True, checkpoint_path=checkpoint_path)
        return

    readiness.update(
        {
            "diagnostics_executed": bool(summary["diagnostics_executed"]),
            "selected_decision": summary["selected_decision"],
            "notes": [
                "No-training Phase 48 diagnostic pass completed on the Phase 45 test split."
                if summary["diagnostics_executed"]
                else "No-training Phase 48 diagnostic pass could not execute because a required read-only dataset or prediction artifact was missing."
            ],
        }
    )
    write_json(output_dir / "phase48_diagnostic_readiness.json", readiness)
    write_json(output_dir / "phase48_reliability_summary.json", summary)
    write_summary_md(output_dir / "phase48_reliability_summary.md", summary)
    print_terminal_summary(summary)


if __name__ == "__main__":
    main()
