from __future__ import annotations

import argparse
import csv
import json
import math
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable


REPO_ROOT = Path(__file__).resolve().parents[1]
BASE_DIR = Path("analysis/phase25_target_wet_recall_comparison")
DEFAULT_PHASE10_DIR = BASE_DIR / "phase10_seed123_physical"
DEFAULT_PHASE25_DIR = BASE_DIR / "phase25_seed123_physical"
DEFAULT_OUTPUT_DIR = BASE_DIR / "aligned_comparison"
DEFAULT_PHASE10_RUN_TOKEN = "phase10_margin_aware_boundary_band_seed123_40e"
DEFAULT_PHASE25_RUN_TOKEN = "phase25_target_wet_recall_seed123_40e"

SCENARIO_FILE = "scenario_physical_consistency_metrics.csv"
OPTIONAL_FILES = (
    "volume_response_metrics.csv",
    "peak_depth_consistency.csv",
    "wet_connectivity_metrics.csv",
    "temporal_consistency_metrics.csv",
)

KEY_CANDIDATES = (
    ("scenario_identity",),
    ("scenario_key",),
    ("seed", "location", "event", "start_idx"),
    ("location", "event", "start_idx"),
    ("seed", "batch_index", "sample_index", "location", "event", "start_idx"),
    ("batch_index", "sample_index", "location", "event", "start_idx"),
    ("phase24_case_key",),
)

METRICS = (
    "rmse",
    "mae",
    "relative_volume_bias",
    "wet_area_contraction",
    "peak_depth_underprediction",
    "false_dry_rate",
    "false_wet_rate",
    "connectivity_loss_indicator",
    "largest_component_ratio_change",
)

LOWER_IS_BETTER = {
    "rmse",
    "mae",
    "wet_area_contraction",
    "peak_depth_underprediction",
    "false_dry_rate",
    "false_wet_rate",
    "connectivity_loss_indicator",
}

STANDARD_METRICS = {
    "phase10_seed123_baseline": {
        "rmse": 0.061625179099409205,
        "mae": 0.02252520179670108,
        "wet_dry_iou": 0.7068078314003191,
        "rollout_stability": 0.982880363338872,
        "step_rmse_std": 0.017476716078817844,
    },
    "phase25_seed123": {
        "rmse": 0.05673027646384741,
        "mae": 0.02153666278249339,
        "wet_dry_iou": 0.780236404193075,
        "rollout_stability": 0.9832738888891119,
        "step_rmse_std": 0.017054059983868348,
    },
}


def resolve_repo_path(path: Path) -> Path:
    return path if path.is_absolute() else REPO_ROOT / path


def display_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Compare Phase 25 target-wet recall diagnostics against the Phase 10 seed123 baseline "
            "on common aligned cases only. This script reads existing CSVs; it does not retrain or "
            "generate predictions."
        )
    )
    parser.add_argument("--phase10-dir", type=Path, default=DEFAULT_PHASE10_DIR)
    parser.add_argument("--phase25-dir", type=Path, default=DEFAULT_PHASE25_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--phase10-run-token", default=DEFAULT_PHASE10_RUN_TOKEN)
    parser.add_argument("--phase25-run-token", default=DEFAULT_PHASE25_RUN_TOKEN)
    return parser.parse_args()


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            return []
        return [dict(row) for row in reader]


def write_csv_rows(path: Path, rows: list[dict[str, Any]], fieldnames: list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if fieldnames is None:
        fieldnames = []
        for row in rows:
            for key in row:
                if key not in fieldnames:
                    fieldnames.append(key)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, sort_keys=True)
        handle.write("\n")


def to_float(value: Any) -> float:
    if value in ("", None):
        return math.nan
    try:
        number = float(value)
    except (TypeError, ValueError):
        return math.nan
    return number if math.isfinite(number) else math.nan


def clean_number(value: float) -> float | None:
    return value if math.isfinite(value) else None


def mean(values: Iterable[float]) -> float | None:
    finite = [value for value in values if math.isfinite(value)]
    if not finite:
        return None
    return sum(finite) / len(finite)


def key_for(row: dict[str, Any], key_cols: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(str(row.get(col, "")) for col in key_cols)


def rows_have_columns(rows: list[dict[str, Any]], columns: tuple[str, ...]) -> bool:
    if not rows:
        return False
    fields = set(rows[0])
    return all(col in fields for col in columns)


def is_unique_key(rows: list[dict[str, Any]], key_cols: tuple[str, ...]) -> bool:
    keys = [key_for(row, key_cols) for row in rows]
    return len(keys) == len(set(keys))


def choose_alignment_key(phase10_rows: list[dict[str, Any]], phase25_rows: list[dict[str, Any]]) -> tuple[str, ...]:
    for candidate in KEY_CANDIDATES:
        if (
            rows_have_columns(phase10_rows, candidate)
            and rows_have_columns(phase25_rows, candidate)
            and is_unique_key(phase10_rows, candidate)
            and is_unique_key(phase25_rows, candidate)
        ):
            return candidate
    raise ValueError("No stable unique alignment key found. Refusing to align by run_name.")


def row_matches_run_token(row: dict[str, str], run_token: str) -> bool:
    haystack = " ".join(str(row.get(col, "")) for col in ("run_name", "run_root", "maps_path", "summary_path"))
    return run_token in haystack


def filter_rows(rows: list[dict[str, str]], run_token: str) -> list[dict[str, str]]:
    filtered = [row for row in rows if row_matches_run_token(row, run_token)]
    if not filtered:
        raise ValueError(f"No rows matched run token: {run_token}")
    return filtered


def load_enriched_rows(input_dir: Path, run_token: str) -> tuple[list[dict[str, str]], int]:
    scenario_path = input_dir / SCENARIO_FILE
    raw_rows = read_csv_rows(scenario_path)
    if not raw_rows:
        raise FileNotFoundError(f"No rows found in required input: {display_path(scenario_path)}")
    rows = filter_rows(raw_rows, run_token)

    provisional_key = choose_alignment_key(rows, rows)
    row_by_key = {key_for(row, provisional_key): row for row in rows}
    for file_name in OPTIONAL_FILES:
        optional_path = input_dir / file_name
        optional_rows = filter_rows(read_csv_rows(optional_path), run_token) if optional_path.exists() else []
        if not optional_rows or not rows_have_columns(optional_rows, provisional_key):
            continue
        for optional_row in optional_rows:
            target = row_by_key.get(key_for(optional_row, provisional_key))
            if target is None:
                continue
            for col, value in optional_row.items():
                if col not in target or target[col] == "":
                    target[col] = value
    return rows, len(raw_rows)


def standard_metric_deltas() -> dict[str, dict[str, float]]:
    phase10 = STANDARD_METRICS["phase10_seed123_baseline"]
    phase25 = STANDARD_METRICS["phase25_seed123"]
    deltas = {}
    for metric in phase10:
        deltas[metric] = {
            "phase10": phase10[metric],
            "phase25": phase25[metric],
            "delta_phase25_minus_phase10": phase25[metric] - phase10[metric],
        }
    return deltas


def improvement_flag(metric: str, delta: float | None) -> bool | None:
    if delta is None:
        return None
    if metric in LOWER_IS_BETTER:
        return delta < 0
    return None


def summarize_metric(rows: list[dict[str, Any]], metric: str) -> dict[str, Any]:
    phase10_values = [to_float(row.get(f"phase10_{metric}")) for row in rows]
    phase25_values = [to_float(row.get(f"phase25_{metric}")) for row in rows]
    delta_values = [to_float(row.get(f"delta_{metric}")) for row in rows]
    delta_mean = mean(delta_values)
    return {
        "metric": metric,
        "n": sum(1 for value in delta_values if math.isfinite(value)),
        "phase10_mean": mean(phase10_values),
        "phase25_mean": mean(phase25_values),
        "delta_mean_phase25_minus_phase10": delta_mean,
        "lower_is_better": metric in LOWER_IS_BETTER,
        "phase25_improved": improvement_flag(metric, delta_mean),
    }


def summarize_by_warning_level(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[str(row.get("warning_level", "unlabeled") or "unlabeled")].append(row)

    output_rows: list[dict[str, Any]] = []
    for warning_level in sorted(grouped):
        group_rows = grouped[warning_level]
        out: dict[str, Any] = {"warning_level": warning_level, "n": len(group_rows)}
        for metric in METRICS:
            summary = summarize_metric(group_rows, metric)
            out[f"phase10_{metric}_mean"] = summary["phase10_mean"]
            out[f"phase25_{metric}_mean"] = summary["phase25_mean"]
            out[f"delta_{metric}_mean"] = summary["delta_mean_phase25_minus_phase10"]
            out[f"phase25_improved_{metric}"] = summary["phase25_improved"]
        output_rows.append(out)
    return output_rows


def build_aligned_rows(
    phase10_rows: list[dict[str, str]],
    phase25_rows: list[dict[str, str]],
    key_cols: tuple[str, ...],
    phase10_raw_rows: int,
    phase25_raw_rows: int,
) -> tuple[list[dict[str, Any]], dict[str, int]]:
    phase10_by_key = {key_for(row, key_cols): row for row in phase10_rows}
    phase25_by_key = {key_for(row, key_cols): row for row in phase25_rows}
    phase10_keys = set(phase10_by_key)
    phase25_keys = set(phase25_by_key)
    common_keys = sorted(phase10_keys & phase25_keys)

    aligned_rows: list[dict[str, Any]] = []
    for key in common_keys:
        phase10 = phase10_by_key[key]
        phase25 = phase25_by_key[key]
        row: dict[str, Any] = {col: phase10.get(col, phase25.get(col, "")) for col in key_cols}
        row["warning_level"] = phase10.get("warning_level") or phase25.get("warning_level") or "unlabeled"
        row["phase25_warning_level"] = phase25.get("warning_level", "")
        row["risk_score"] = phase10.get("risk_score") or phase25.get("risk_score", "")
        row["risk_category"] = phase10.get("risk_category") or phase25.get("risk_category", "")
        for metric in METRICS:
            phase10_value = to_float(phase10.get(metric))
            phase25_value = to_float(phase25.get(metric))
            delta = phase25_value - phase10_value if math.isfinite(phase10_value) and math.isfinite(phase25_value) else math.nan
            row[f"phase10_{metric}"] = clean_number(phase10_value)
            row[f"phase25_{metric}"] = clean_number(phase25_value)
            row[f"delta_{metric}"] = clean_number(delta)
            row[f"phase25_improved_{metric}"] = improvement_flag(metric, clean_number(delta))
        aligned_rows.append(row)

    counts = {
        "phase10_rows": phase10_raw_rows,
        "phase25_rows": phase25_raw_rows,
        "phase10_filtered_rows": len(phase10_rows),
        "phase25_filtered_rows": len(phase25_rows),
        "common_rows": len(common_keys),
        "phase10_only_rows": len(phase10_keys - phase25_keys),
        "phase25_only_rows": len(phase25_keys - phase10_keys),
    }
    return aligned_rows, counts


def main() -> None:
    args = parse_args()
    phase10_dir = resolve_repo_path(args.phase10_dir)
    phase25_dir = resolve_repo_path(args.phase25_dir)
    output_dir = resolve_repo_path(args.output_dir)

    phase10_rows, phase10_raw_rows = load_enriched_rows(phase10_dir, args.phase10_run_token)
    phase25_rows, phase25_raw_rows = load_enriched_rows(phase25_dir, args.phase25_run_token)
    key_cols = choose_alignment_key(phase10_rows, phase25_rows)
    aligned_rows, row_counts = build_aligned_rows(
        phase10_rows, phase25_rows, key_cols, phase10_raw_rows, phase25_raw_rows
    )

    metric_summary = [summarize_metric(aligned_rows, metric) for metric in METRICS]
    warning_summary = summarize_by_warning_level(aligned_rows)
    standard = {
        "phase10_seed123_baseline": STANDARD_METRICS["phase10_seed123_baseline"],
        "phase25_seed123": STANDARD_METRICS["phase25_seed123"],
        "delta_phase25_minus_phase10": standard_metric_deltas(),
    }

    output_dir.mkdir(parents=True, exist_ok=True)
    write_csv_rows(output_dir / "aligned_case_metrics.csv", aligned_rows)
    write_csv_rows(output_dir / "aligned_metric_delta_summary.csv", metric_summary)
    write_csv_rows(output_dir / "aligned_summary_by_warning_level.csv", warning_summary)
    write_json(output_dir / "phase10_vs_phase25_standard_metrics.json", standard)

    metric_summary_by_name = {row["metric"]: row for row in metric_summary}
    summary = {
        "alignment": {
            "key_columns": list(key_cols),
            "key_selection_policy": "First available unique stable key set from scenario_identity, scenario_key, stable scenario/sample columns, then phase24_case_key. run_name is never used as an alignment key.",
            "phase10_subset_filter": {
                "run_token": args.phase10_run_token,
                "note": "Used only to select the Phase 10 seed123 diagnostic subset from the aggregate CSV before alignment.",
            },
            "phase25_subset_filter": {
                "run_token": args.phase25_run_token,
                "note": "Used only to select the Phase 25 seed123 diagnostic subset from the aggregate CSV before alignment.",
            },
            **row_counts,
        },
        "inputs": {
            "phase10_scenario_metrics": display_path(phase10_dir / SCENARIO_FILE),
            "phase25_scenario_metrics": display_path(phase25_dir / SCENARIO_FILE),
            "optional_files_considered": list(OPTIONAL_FILES),
        },
        "outputs": {
            "aligned_case_metrics": display_path(output_dir / "aligned_case_metrics.csv"),
            "aligned_summary_by_warning_level": display_path(output_dir / "aligned_summary_by_warning_level.csv"),
            "aligned_metric_delta_summary": display_path(output_dir / "aligned_metric_delta_summary.csv"),
            "phase10_vs_phase25_standard_metrics": display_path(output_dir / "phase10_vs_phase25_standard_metrics.json"),
        },
        "standard_metric_deltas": standard["delta_phase25_minus_phase10"],
        "physical_metric_delta_summary": metric_summary_by_name,
        "warning_level_summary": warning_summary,
        "phase25_improves_false_dry_rate": metric_summary_by_name["false_dry_rate"]["phase25_improved"],
        "phase25_improves_wet_area_contraction": metric_summary_by_name["wet_area_contraction"]["phase25_improved"],
    }
    write_json(output_dir / "aligned_comparison_summary.json", summary)

    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
