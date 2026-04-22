from __future__ import annotations

import argparse
import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]

METRICS = ("val_rmse", "val_mae", "val_wet_dry_iou", "val_rollout_stability", "val_loss")
LOWER_IS_BETTER = {"val_rmse", "val_mae", "val_loss"}
HIGHER_IS_BETTER = {"val_wet_dry_iou", "val_rollout_stability"}
REQUIRED_SEEDS = ("seed202", "seed123", "seed42")


@dataclass(frozen=True)
class MetricValue:
    value: float | None
    source_file: str
    source_kind: str


def resolve_repo_path(path: str | Path) -> Path:
    path = Path(path)
    if path.is_absolute():
        return path
    return REPO_ROOT / path


def display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return str(path)


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_final_history_record(run_root: Path) -> tuple[dict[str, Any] | None, Path | None]:
    history_path = run_root / "history.json"
    if not history_path.exists():
        return None, None
    history = load_json(history_path)
    if not isinstance(history, list) or not history:
        raise ValueError(f"{display_path(history_path)} must contain a non-empty JSON list.")
    if not isinstance(history[-1], dict):
        raise ValueError(f"Final history entry in {display_path(history_path)} must be a JSON object.")
    return history[-1], history_path


def find_evaluation_metrics(run_root: Path) -> tuple[dict[str, Any] | None, Path | None]:
    for metrics_path in sorted(run_root.glob("evaluation_*/metrics.json")):
        metrics = load_json(metrics_path)
        if not isinstance(metrics, dict):
            raise ValueError(f"{display_path(metrics_path)} must contain a JSON object.")
        return metrics, metrics_path
    return None, None


def read_metric_values(run_root: Path) -> dict[str, MetricValue]:
    history_record, history_path = load_final_history_record(run_root)
    evaluation_metrics, evaluation_path = find_evaluation_metrics(run_root)
    values: dict[str, MetricValue] = {}

    for metric in METRICS:
        if history_record is not None and metric in history_record:
            values[metric] = MetricValue(
                value=float(history_record[metric]),
                source_file=display_path(history_path),
                source_kind="history_final_validation",
            )
            continue

        eval_key = metric.removeprefix("val_")
        if evaluation_metrics is not None and eval_key in evaluation_metrics:
            values[metric] = MetricValue(
                value=float(evaluation_metrics[eval_key]),
                source_file=display_path(evaluation_path),
                source_kind="evaluation_metrics_fallback",
            )
            continue

        values[metric] = MetricValue(value=None, source_file="MISSING", source_kind="missing")

    return values


def metric_delta(static_value: float | None, adaptive_value: float | None) -> float | None:
    if static_value is None or adaptive_value is None:
        return None
    return adaptive_value - static_value


def direction_for_metric(metric: str, delta: float | None) -> str:
    if delta is None:
        return "missing"
    if delta == 0.0:
        return "tie"
    if metric in LOWER_IS_BETTER:
        return "adapt010_better" if delta < 0.0 else "static_better"
    if metric in HIGHER_IS_BETTER:
        return "adapt010_better" if delta > 0.0 else "static_better"
    return "not_applicable"


def combined_direction(metric_names: tuple[str, ...], row: dict[str, Any]) -> str:
    directions = [row[f"{metric}_direction"] for metric in metric_names]
    if any(direction == "missing" for direction in directions):
        return "missing"
    unique = set(directions)
    if len(unique) == 1:
        return directions[0]
    return "mixed"


def format_value(value: Any) -> str:
    if value is None:
        return "NA"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def build_rows(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    comparisons = manifest.get("comparisons")
    if not isinstance(comparisons, list):
        raise ValueError("Manifest must contain a 'comparisons' list.")

    seeds = [item.get("seed") for item in comparisons if isinstance(item, dict)]
    if tuple(seeds) != REQUIRED_SEEDS:
        raise ValueError(f"Manifest comparisons must contain exactly {', '.join(REQUIRED_SEEDS)} in order.")

    rows: list[dict[str, Any]] = []
    for item in comparisons:
        static_root = resolve_repo_path(item["static_af025_run_root"])
        adaptive_root = resolve_repo_path(item["adapt010_run_root"])
        if not static_root.exists():
            raise FileNotFoundError(f"Static run root not found: {display_path(static_root)}")
        if not adaptive_root.exists():
            raise FileNotFoundError(f"Adaptive run root not found: {display_path(adaptive_root)}")

        static_values = read_metric_values(static_root)
        adaptive_values = read_metric_values(adaptive_root)
        row: dict[str, Any] = {
            "seed": item["seed"],
            "seed_role": item["seed_role"],
            "static_af025_run_root": display_path(static_root),
            "adapt010_run_root": display_path(adaptive_root),
        }

        for metric in METRICS:
            static_metric = static_values[metric]
            adaptive_metric = adaptive_values[metric]
            delta = metric_delta(static_metric.value, adaptive_metric.value)
            row[f"static_{metric}"] = static_metric.value
            row[f"adapt010_{metric}"] = adaptive_metric.value
            row[f"{metric}_delta"] = delta
            row[f"{metric}_direction"] = direction_for_metric(metric, delta)
            row[f"static_{metric}_source_file"] = static_metric.source_file
            row[f"static_{metric}_source_kind"] = static_metric.source_kind
            row[f"adapt010_{metric}_source_file"] = adaptive_metric.source_file
            row[f"adapt010_{metric}_source_kind"] = adaptive_metric.source_kind

        row["rmse_mae_loss_direction"] = combined_direction(("val_rmse", "val_mae", "val_loss"), row)
        row["wet_dry_iou_direction"] = row["val_wet_dry_iou_direction"]
        row["rollout_stability_direction"] = row["val_rollout_stability_direction"]
        rows.append(row)

    return rows


def write_csv(rows: list[dict[str, Any]], output_path: Path) -> None:
    base_fields = [
        "seed",
        "seed_role",
        "static_af025_run_root",
        "adapt010_run_root",
        "rmse_mae_loss_direction",
        "wet_dry_iou_direction",
        "rollout_stability_direction",
    ]
    metric_fields: list[str] = []
    for metric in METRICS:
        metric_fields.extend(
            [
                f"static_{metric}",
                f"adapt010_{metric}",
                f"{metric}_delta",
                f"{metric}_direction",
                f"static_{metric}_source_file",
                f"static_{metric}_source_kind",
                f"adapt010_{metric}_source_file",
                f"adapt010_{metric}_source_kind",
            ]
        )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=base_fields + metric_fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: format_value(row.get(field)) for field in writer.fieldnames})


def write_markdown(rows: list[dict[str, Any]], output_path: Path) -> None:
    lines = [
        "# Phase 9 af025 vs adapt010 Summary",
        "",
        "Source priority: final validation metrics from `history.json`; `evaluation_*/metrics.json` is used only when a final validation field is unavailable.",
        "",
        "| seed | role | RMSE/MAE/loss | wet/dry IoU | rollout stability |",
        "|---|---|---|---|---|",
    ]
    for row in rows:
        lines.append(
            "| {seed} | {role} | {error_dir} | {iou_dir} | {rollout_dir} |".format(
                seed=row["seed"],
                role=row["seed_role"],
                error_dir=row["rmse_mae_loss_direction"],
                iou_dir=row["wet_dry_iou_direction"],
                rollout_dir=row["rollout_stability_direction"],
            )
        )

    lines.extend(["", "## Metric Values", ""])
    for row in rows:
        lines.extend(
            [
                f"### {row['seed']}: {row['seed_role']}",
                "",
                f"- static run: `{row['static_af025_run_root']}`",
                f"- adapt010 run: `{row['adapt010_run_root']}`",
                "",
                "| metric | static af025 | adapt010 | delta | direction | static source | adapt010 source |",
                "|---|---:|---:|---:|---|---|---|",
            ]
        )
        for metric in METRICS:
            lines.append(
                "| {metric} | {static_value} | {adaptive_value} | {delta} | {direction} | `{static_source}` | `{adaptive_source}` |".format(
                    metric=metric,
                    static_value=format_value(row[f"static_{metric}"]),
                    adaptive_value=format_value(row[f"adapt010_{metric}"]),
                    delta=format_value(row[f"{metric}_delta"]),
                    direction=row[f"{metric}_direction"],
                    static_source=row[f"static_{metric}_source_file"],
                    adaptive_source=row[f"adapt010_{metric}_source_file"],
                )
            )
        lines.append("")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a read-only Phase 9 static af025 vs adapt010 comparison report."
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=Path("analysis/manifests/phase9_af025_vs_adapt010_runs.json"),
        help="JSON manifest mapping seed comparisons to existing run roots.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("analysis/phase9_af025_vs_adapt010"),
        help="Directory where the CSV and Markdown summaries will be written.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    manifest_path = resolve_repo_path(args.manifest)
    output_dir = resolve_repo_path(args.output_dir)
    manifest = load_json(manifest_path)
    if not isinstance(manifest, dict):
        raise ValueError("Manifest root must be a JSON object.")

    rows = build_rows(manifest)
    csv_path = output_dir / "phase9_af025_vs_adapt010_summary.csv"
    markdown_path = output_dir / "phase9_af025_vs_adapt010_summary.md"
    write_csv(rows, csv_path)
    write_markdown(rows, markdown_path)

    print(f"Wrote CSV: {display_path(csv_path)}")
    print(f"Wrote Markdown: {display_path(markdown_path)}")


if __name__ == "__main__":
    main()
