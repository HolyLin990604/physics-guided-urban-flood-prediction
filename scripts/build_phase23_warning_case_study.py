from __future__ import annotations

import argparse
import csv
import json
import math
import warnings
from collections import Counter
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PHASE15_DIR = Path("analysis/phase15_reliability_screening")
DEFAULT_PHASE16_DIR = Path("analysis/phase16_warning_rules")
DEFAULT_OUTPUT_DIR = Path("analysis/phase23_warning_case_study")

CASE_ROLES = ("reliable", "caution", "high-risk")
WARNING_LEVEL_COLS = ("warning_level", "risk_category", "reliability_level", "category")
SCENARIO_ID_COLS = ("scenario_key", "scenario_id", "case_id")
RISK_SCORE_COLS = ("risk_score", "scenario_risk_score", "score")
FALSE_DRY_COLS = ("false_dry_rate", "false_dry_fraction", "false_dry_cell_fraction")
BOUNDARY_RISK_COLS = ("boundary_false_dry_rate", "boundary_fraction", "boundary_component")
RMSE_COLS = ("rmse", "root_mean_square_error")
ACTION_COLS = ("warning_action", "action", "recommended_action")
USE_NOTE_COLS = ("use_note", "applicability_note", "pixel_warning_note")

PHASE15_INPUTS = {
    "scenario_risk_scores": "scenario_risk_scores.csv",
    "pixel_risk_summary": "pixel_risk_summary.csv",
    "high_risk_cases": "high_risk_cases.csv",
    "summary": "summary.json",
}
PHASE16_INPUTS = {
    "scenario_warning_summary": "scenario_warning_summary.csv",
    "pixel_warning_summary": "pixel_warning_summary.csv",
    "high_risk_warning_cases": "high_risk_warning_cases.csv",
    "warning_rules": "warning_rules.json",
    "summary": "summary.json",
}

INTERPRETATION_NOTE = (
    "This Phase 23 prototype reuses existing Phase 15 reliability-screening outputs and "
    "Phase 16 warning-rule outputs. It does not retrain models, tune Phase 10 settings, "
    "or generate new predictions."
)


def display_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def resolve_repo_path(path: Path) -> Path:
    return path if path.is_absolute() else REPO_ROOT / path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build Phase 23 reliability-aware warning case-study prototype from existing Phase 15/16 outputs."
    )
    parser.add_argument("--phase15-dir", type=Path, default=DEFAULT_PHASE15_DIR)
    parser.add_argument("--phase16-dir", type=Path, default=DEFAULT_PHASE16_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    return parser.parse_args()


def read_json_if_exists(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, data: dict[str, Any]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, sort_keys=True)
        handle.write("\n")


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            return []
        return [dict(row) for row in reader]


def write_csv_rows(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def input_paths(base_dir: Path, mapping: dict[str, str]) -> dict[str, Path]:
    return {key: base_dir / name for key, name in mapping.items()}


def first_existing_col(row: dict[str, Any], candidates: tuple[str, ...]) -> str | None:
    lower_lookup = {key.lower(): key for key in row}
    for candidate in candidates:
        if candidate in row:
            return candidate
        if candidate.lower() in lower_lookup:
            return lower_lookup[candidate.lower()]
    return None


def get_value(row: dict[str, Any], candidates: tuple[str, ...], default: str = "") -> str:
    col = first_existing_col(row, candidates)
    if col is None:
        return default
    value = row.get(col, default)
    return default if value is None else str(value)


def to_float_value(value: Any, default: float = 0.0) -> float:
    if value in ("", None):
        return default
    try:
        number = float(value)
    except (TypeError, ValueError):
        return default
    return default if math.isnan(number) or math.isinf(number) else number


def to_float(row: dict[str, Any], candidates: tuple[str, ...], default: float = 0.0) -> float:
    col = first_existing_col(row, candidates)
    return default if col is None else to_float_value(row.get(col), default)


def to_int_value(value: Any, default: int = 0) -> int:
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return default


def normalize_level(value: str) -> str:
    cleaned = value.strip().lower().replace("_", "-")
    aliases = {
        "high risk": "high-risk",
        "highrisk": "high-risk",
        "safe": "reliable",
        "low-risk": "reliable",
        "low risk": "reliable",
        "medium-risk": "caution",
        "moderate": "caution",
    }
    return aliases.get(cleaned, cleaned)


def scenario_identity(row: dict[str, Any]) -> str:
    explicit = get_value(row, SCENARIO_ID_COLS)
    if explicit:
        return explicit
    parts = [
        str(row.get("location", "")),
        str(row.get("event", "")),
        str(row.get("start_idx", "")),
    ]
    if any(parts):
        return "|".join(parts)
    return "|".join(
        str(row.get(field, ""))
        for field in ("seed", "run_name", "batch_index", "sample_index")
        if str(row.get(field, ""))
    )


def row_stable_key(row: dict[str, Any]) -> tuple[str, ...]:
    return (
        str(row.get("seed", "")),
        str(row.get("run_name", "")),
        str(row.get("location", "")),
        str(row.get("event", "")),
        str(row.get("start_idx", "")),
        str(row.get("batch_index", "")),
        str(row.get("sample_index", "")),
        scenario_identity(row),
    )


def component_fields(rows: list[dict[str, Any]]) -> list[str]:
    if not rows:
        return []
    fields = set().union(*(row.keys() for row in rows))
    preferred = [
        "false_dry_component",
        "wet_fraction_contraction_component",
        "peak_underprediction_component",
        "underprediction_bias_component",
        "boundary_component",
        "high_intensity_location2_component",
        "cross_seed_disagreement_component",
        "low_margin_component",
    ]
    chosen = [field for field in preferred if field in fields]
    chosen.extend(sorted(field for field in fields if field.endswith("_component") and field not in chosen))
    return chosen


def dominant_components(row: dict[str, Any], fields: list[str], limit: int = 3) -> list[tuple[str, float]]:
    values = [(field, to_float_value(row.get(field), 0.0)) for field in fields]
    values = [(field, value) for field, value in values if value > 0]
    values.sort(key=lambda item: (-item[1], item[0]))
    return values[:limit]


def format_component_name(name: str) -> str:
    suffix = "_component"
    if name.endswith(suffix):
        name = name[: -len(suffix)]
    return name.replace("_", " ")


def select_cases(rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    by_level: dict[str, list[dict[str, Any]]] = {role: [] for role in CASE_ROLES}
    for row in rows:
        level = normalize_level(get_value(row, WARNING_LEVEL_COLS))
        if level in by_level:
            by_level[level].append(row)

    selection_notes: dict[str, Any] = {
        "logic": {
            "reliable": "lowest available risk score, then lowest false-dry/boundary risk and RMSE",
            "caution": "risk score closest to the caution midpoint when available, then stable identity",
            "high-risk": "prefer location2+r300y/Phase-13-like cases, then highest risk evidence",
        },
        "available_counts": {level: len(rows_for_level) for level, rows_for_level in by_level.items()},
        "missing_levels": [],
    }

    selected: list[dict[str, Any]] = []
    used_keys: set[tuple[str, ...]] = set()

    reliable_rows = by_level["reliable"]
    if reliable_rows:
        reliable = sorted(
            reliable_rows,
            key=lambda row: (
                to_float(row, RISK_SCORE_COLS, 0.0),
                to_float(row, FALSE_DRY_COLS, 0.0),
                to_float(row, BOUNDARY_RISK_COLS, 0.0),
                to_float(row, RMSE_COLS, 0.0),
                row_stable_key(row),
            ),
        )[0]
        selected.append(reliable)
        used_keys.add(row_stable_key(reliable))
    else:
        selection_notes["missing_levels"].append("reliable")

    caution_rows = by_level["caution"]
    if caution_rows:
        risk_values = [to_float(row, RISK_SCORE_COLS, 0.0) for row in caution_rows]
        target = 3.75 if any(value > 0 for value in risk_values) else 0.0
        caution = sorted(
            caution_rows,
            key=lambda row: (
                abs(to_float(row, RISK_SCORE_COLS, 0.0) - target),
                to_float(row, FALSE_DRY_COLS, 0.0),
                to_float(row, BOUNDARY_RISK_COLS, 0.0),
                row_stable_key(row),
            ),
        )[0]
        selected.append(caution)
        used_keys.add(row_stable_key(caution))
    else:
        selection_notes["missing_levels"].append("caution")

    high_risk_rows = by_level["high-risk"]
    if high_risk_rows:
        def high_risk_priority(row: dict[str, Any]) -> tuple[int, int, float, float, tuple[str, ...]]:
            location = str(row.get("location", "")).lower()
            event = str(row.get("event", "")).lower()
            scenario = scenario_identity(row).lower()
            reason = str(row.get("high_intensity_reason", "")).lower()
            location2_r300y = int("location2" in f"{location}|{scenario}" and "r300y" in f"{event}|{scenario}")
            phase13_like = int(location2_r300y or "location2_r300y" in reason)
            return (
                -phase13_like,
                -location2_r300y,
                -to_float(row, RISK_SCORE_COLS, 0.0),
                -to_float(row, FALSE_DRY_COLS, 0.0),
                row_stable_key(row),
            )

        high_risk = sorted(high_risk_rows, key=high_risk_priority)[0]
        selected.append(high_risk)
        used_keys.add(row_stable_key(high_risk))
    else:
        selection_notes["missing_levels"].append("high-risk")

    if len(selected) < 3:
        fallback_rows = sorted(rows, key=lambda row: (-to_float(row, RISK_SCORE_COLS, 0.0), row_stable_key(row)))
        for row in fallback_rows:
            if len(selected) >= 3:
                break
            key = row_stable_key(row)
            if key not in used_keys:
                selected.append(row)
                used_keys.add(key)

    return selected[:3], selection_notes


def warning_action(row: dict[str, Any], level: str) -> str:
    existing = get_value(row, ACTION_COLS)
    if existing:
        return existing
    return {
        "reliable": "use as rapid prediction reference",
        "caution": "use with targeted review",
        "high-risk": "do not use alone for warning decisions",
    }.get(level, "use with documented reliability review")


def applicability_note(row: dict[str, Any], level: str) -> str:
    existing = get_value(row, USE_NOTE_COLS)
    if existing:
        return existing
    if level == "reliable":
        return "This case lies within the stronger applicability range indicated by the available screening outputs."
    if level == "caution":
        return "This case should be interpreted near an applicability boundary, with targeted review of spatial risk signals."
    if level == "high-risk":
        return "This case lies near or outside the current reliable operating envelope of the surrogate model."
    return "Applicability should be interpreted from the available Phase 15/16 screening fields."


def reliability_interpretation(row: dict[str, Any], level: str) -> str:
    risk = to_float(row, RISK_SCORE_COLS, 0.0)
    false_dry = to_float(row, FALSE_DRY_COLS, 0.0)
    contraction = to_float(row, ("wet_fraction_contraction",), 0.0)
    peak_under = to_float(row, ("peak_underprediction",), 0.0)
    if level == "reliable":
        return (
            f"Phase 15/16 screening labels this case reliable with risk score {risk:.3g}; "
            "the available missed-inundation and boundary indicators are comparatively low."
        )
    if level == "caution":
        return (
            f"Phase 15/16 screening labels this case caution with risk score {risk:.3g}; "
            "the prediction may be useful as a rapid reference after targeted review."
        )
    if level == "high-risk":
        return (
            f"Phase 15/16 screening labels this case high-risk with risk score {risk:.3g}, "
            f"false-dry rate {false_dry:.3g}, wet-fraction contraction {contraction:.3g}, "
            f"and peak underprediction {peak_under:.3g} m."
        )
    return "Reliability interpretation is limited because the warning level is unavailable or unrecognized."


def build_selected_case_rows(selected: list[dict[str, Any]], component_cols: list[str]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in selected:
        level = normalize_level(get_value(row, WARNING_LEVEL_COLS))
        role = level if level in CASE_ROLES else "fallback"
        components = dominant_components(row, component_cols)
        component_text = "; ".join(f"{format_component_name(name)}={value:.3g}" for name, value in components)
        if not component_text:
            component_text = "No positive component fields were available."
        rows.append(
            {
                "case_role": role,
                "scenario_identity": scenario_identity(row),
                "warning_level": level,
                "seed": row.get("seed", ""),
                "run_name": row.get("run_name", ""),
                "location": row.get("location", ""),
                "event": row.get("event", ""),
                "start_idx": row.get("start_idx", ""),
                "batch_index": row.get("batch_index", ""),
                "sample_index": row.get("sample_index", ""),
                "maps_path": row.get("maps_path", ""),
                "risk_score": to_float(row, RISK_SCORE_COLS, 0.0),
                "false_dry_rate": to_float(row, FALSE_DRY_COLS, 0.0),
                "boundary_false_dry_rate": to_float(row, BOUNDARY_RISK_COLS, 0.0),
                "wet_fraction_contraction": to_float(row, ("wet_fraction_contraction",), 0.0),
                "peak_underprediction": to_float(row, ("peak_underprediction",), 0.0),
                "rmse": to_float(row, RMSE_COLS, 0.0),
                "dominant_risk_components": component_text,
                "model_reliability_interpretation": reliability_interpretation(row, level),
                "suggested_warning_action": warning_action(row, level),
                "applicability_boundary_note": applicability_note(row, level),
                "selection_basis": selection_basis(role),
            }
        )
    return rows


def selection_basis(role: str) -> str:
    if role == "reliable":
        return "Selected as the lowest-risk reliable-labeled case using risk score, false-dry, boundary, RMSE, and stable identity tie-breaks."
    if role == "caution":
        return "Selected as a representative caution-labeled case closest to the caution risk midpoint with stable tie-breaks."
    if role == "high-risk":
        return "Selected as a high-risk case, prioritizing Phase-13-like location2+r300y evidence and then stronger risk evidence."
    return "Selected as a deterministic fallback because fewer than three requested warning levels were available."


def save_warning_level_overview(path: Path, selected_rows: list[dict[str, Any]], all_rows: list[dict[str, Any]]) -> None:
    counts = Counter(normalize_level(get_value(row, WARNING_LEVEL_COLS)) for row in all_rows)
    labels = list(CASE_ROLES)
    values = [counts.get(label, 0) for label in labels]
    colors = ["#3b7f5c", "#c8922d", "#b84a4a"]
    fig, ax = plt.subplots(figsize=(8, 4.8))
    bars = ax.bar(labels, values, color=colors)
    ax.set_title("Phase 23 Selected Cases Within Phase 16 Warning Levels")
    ax.set_ylabel("Scenario count")
    ax.bar_label(bars, padding=3)
    selected_levels = Counter(row["warning_level"] for row in selected_rows)
    for idx, label in enumerate(labels):
        if selected_levels.get(label, 0):
            ax.scatter(idx, values[idx] + max(values) * 0.04 + 0.5, marker="v", s=90, color="#222222", zorder=3)
            ax.text(idx, values[idx] + max(values) * 0.08 + 1.0, "selected", ha="center", fontsize=9)
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)


def save_risk_component_comparison(path: Path, selected_rows: list[dict[str, Any]], source_rows: list[dict[str, Any]], component_cols: list[str]) -> bool:
    if not component_cols:
        return False
    selected_source = list(source_rows)
    if not selected_source:
        return False
    active_cols = [
        field
        for field in component_cols
        if any(to_float_value(row.get(field), 0.0) > 0 for row in selected_source)
    ][:8]
    if not active_cols:
        return False
    roles = [row["case_role"] for row in selected_rows]
    x = np.arange(len(active_cols), dtype=np.float64)
    width = 0.24
    fig, ax = plt.subplots(figsize=(11, 5.4))
    colors = {"reliable": "#3b7f5c", "caution": "#c8922d", "high-risk": "#b84a4a"}
    for offset, row in enumerate(selected_source):
        role = roles[offset] if offset < len(roles) else f"case{offset + 1}"
        values = [to_float_value(row.get(field), 0.0) for field in active_cols]
        ax.bar(x + (offset - 1) * width, values, width=width, label=role, color=colors.get(role, "#58799a"))
    ax.set_title("Selected Case Risk-Component Comparison")
    ax.set_ylabel("Component contribution")
    ax.set_xticks(x)
    ax.set_xticklabels([format_component_name(field) for field in active_cols], rotation=30, ha="right")
    ax.legend()
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)
    return True


def pixel_warning_grid(pixel_rows: list[dict[str, str]]) -> np.ndarray | None:
    if not pixel_rows:
        return None
    if "row" not in pixel_rows[0] or "col" not in pixel_rows[0]:
        return None
    max_row = max(to_int_value(row.get("row"), -1) for row in pixel_rows)
    max_col = max(to_int_value(row.get("col"), -1) for row in pixel_rows)
    if max_row < 0 or max_col < 0:
        return None
    grid = np.zeros((max_row + 1, max_col + 1), dtype=np.float64)
    for row in pixel_rows:
        r = to_int_value(row.get("row"), -1)
        c = to_int_value(row.get("col"), -1)
        if r < 0 or c < 0:
            continue
        level = normalize_level(str(row.get("pixel_warning_level", "")))
        if level == "high-risk":
            value = 2.0
        elif level == "caution":
            value = 1.0
        else:
            value = 0.0
        grid[r, c] = value
    return grid


def load_case_arrays(row: dict[str, Any]) -> tuple[np.ndarray, np.ndarray, np.ndarray] | None:
    maps_value = str(row.get("maps_path", ""))
    if not maps_value:
        return None
    maps_path = resolve_repo_path(Path(maps_value))
    if not maps_path.exists():
        return None
    try:
        with np.load(maps_path) as arrays:
            files = set(arrays.files)
            pred_key = "prediction" if "prediction" in files else next((key for key in arrays.files if "pred" in key.lower()), None)
            target_key = "target" if "target" in files else next((key for key in arrays.files if "target" in key.lower()), None)
            if pred_key is None or target_key is None:
                return None
            prediction = np.asarray(arrays[pred_key], dtype=np.float64)
            target = np.asarray(arrays[target_key], dtype=np.float64)
            error = np.asarray(arrays["error"], dtype=np.float64) if "error" in files else np.abs(prediction - target)
    except Exception as exc:  # pragma: no cover - defensive around local artifacts.
        warnings.warn(f"Could not load map arrays from {display_path(maps_path)}: {exc}", stacklevel=2)
        return None
    if prediction.shape != target.shape:
        return None
    sample_idx = to_int_value(row.get("sample_index"), 0)
    if prediction.ndim == 5:
        sample_idx = min(max(sample_idx, 0), prediction.shape[0] - 1)
        target_sample = target[sample_idx, :, 0, :, :]
        pred_sample = prediction[sample_idx, :, 0, :, :]
        err_sample = error[sample_idx, :, 0, :, :]
    elif prediction.ndim == 4:
        sample_idx = min(max(sample_idx, 0), prediction.shape[0] - 1)
        target_sample = target[sample_idx]
        pred_sample = prediction[sample_idx]
        err_sample = error[sample_idx]
    elif prediction.ndim == 3:
        target_sample = target
        pred_sample = prediction
        err_sample = error
    elif prediction.ndim == 2:
        target_sample = target[None, :, :]
        pred_sample = prediction[None, :, :]
        err_sample = error[None, :, :]
    else:
        return None
    peak_step = int(np.nanargmax(np.nanmax(target_sample, axis=(1, 2)))) if target_sample.ndim == 3 else 0
    return target_sample[peak_step], pred_sample[peak_step], np.abs(err_sample[peak_step])


def save_case_map_figure(path: Path, row: dict[str, Any], warning_grid: np.ndarray | None) -> bool:
    arrays = load_case_arrays(row)
    if arrays is None:
        return False
    target, prediction, error = arrays
    panels = [("Target depth", target), ("Predicted depth", prediction), ("Absolute error", error)]
    if warning_grid is not None and warning_grid.shape == target.shape:
        panels.append(("Phase 16 pixel warning", warning_grid))
    fig, axes = plt.subplots(1, len(panels), figsize=(4.4 * len(panels), 4.2))
    if len(panels) == 1:
        axes = [axes]
    depth_max = max(float(np.nanmax(target)), float(np.nanmax(prediction)), 1e-6)
    for ax, (title, data) in zip(axes, panels):
        if title == "Phase 16 pixel warning":
            cmap = matplotlib.colors.ListedColormap(["#3b7f5c", "#c8922d", "#b84a4a"])
            image = ax.imshow(data, cmap=cmap, vmin=-0.5, vmax=2.5, origin="upper")
            cbar = fig.colorbar(image, ax=ax, fraction=0.046, pad=0.04, ticks=[0, 1, 2])
            cbar.ax.set_yticklabels(["reliable", "caution", "high-risk"])
        else:
            vmax = depth_max if title != "Absolute error" else max(float(np.nanmax(error)), 1e-6)
            image = ax.imshow(data, cmap="viridis", vmin=0.0, vmax=vmax, origin="upper")
            fig.colorbar(image, ax=ax, fraction=0.046, pad=0.04)
        ax.set_title(title)
        ax.set_xticks([])
        ax.set_yticks([])
    fig.suptitle(f"{row['case_role']} case: {row['scenario_identity']}", y=1.02)
    fig.tight_layout()
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)
    return True


def write_report(
    path: Path,
    selected_rows: list[dict[str, Any]],
    figures: list[str],
    map_status: dict[str, Any],
    missing_inputs: list[str],
) -> None:
    lines = [
        "# Phase 23 Reliability-Aware Warning Case Study",
        "",
        INTERPRETATION_NOTE,
        "",
        "## Selected Cases",
        "",
    ]
    for row in selected_rows:
        lines.extend(
            [
                f"### {row['case_role'].title()} Case",
                "",
                f"- Scenario identity: {row['scenario_identity']}",
                f"- Warning level: {row['warning_level']}",
                f"- Dominant risk components: {row['dominant_risk_components']}",
                f"- Model reliability interpretation: {row['model_reliability_interpretation']}",
                f"- Suggested warning action: {row['suggested_warning_action']}",
                f"- Applicability boundary note: {row['applicability_boundary_note']}",
                f"- Selection basis: {row['selection_basis']}",
                "",
            ]
        )
    lines.extend(["## Figures", ""])
    for figure in figures:
        lines.append(f"- {figure}")
    if not figures:
        lines.append("- No figures were generated.")
    lines.extend(["", "## Map-Level Visualization Status", ""])
    if map_status.get("generated"):
        lines.append(
            "Case map figures were generated from existing forecast map `.npz` files referenced by Phase 15/16 rows. "
            "The pixel-warning panel, when present, uses the existing Phase 16 pixel warning summary grid."
        )
    else:
        lines.append(
            "Map-level visualizations were not generated because source arrays could not be located safely from the selected case rows."
        )
    for note in map_status.get("notes", []):
        lines.append(f"- {note}")
    lines.extend(["", "## Missing Inputs And Limitations", ""])
    if missing_inputs:
        for missing in missing_inputs:
            lines.append(f"- Missing input: {missing}")
    else:
        lines.append("- All expected Phase 15 and Phase 16 input files were found.")
    lines.extend(
        [
            "- Warning labels are deterministic screening labels, not calibrated probabilities.",
            "- No model retraining, architecture changes, Phase 10 parameter tuning, or new predictions were performed.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    args = parse_args()
    phase15_dir = resolve_repo_path(args.phase15_dir)
    phase16_dir = resolve_repo_path(args.phase16_dir)
    output_dir = resolve_repo_path(args.output_dir)
    figures_dir = output_dir / "figures"
    output_dir.mkdir(parents=True, exist_ok=True)
    figures_dir.mkdir(parents=True, exist_ok=True)

    phase15_paths = input_paths(phase15_dir, PHASE15_INPUTS)
    phase16_paths = input_paths(phase16_dir, PHASE16_INPUTS)
    all_input_paths = {f"phase15_{key}": path for key, path in phase15_paths.items()}
    all_input_paths.update({f"phase16_{key}": path for key, path in phase16_paths.items()})
    missing_inputs = [display_path(path) for path in all_input_paths.values() if not path.exists()]

    scenario_rows = read_csv_rows(phase16_paths["scenario_warning_summary"])
    scenario_source = phase16_paths["scenario_warning_summary"]
    if not scenario_rows:
        scenario_rows = read_csv_rows(phase15_paths["scenario_risk_scores"])
        scenario_source = phase15_paths["scenario_risk_scores"]
    if not scenario_rows:
        raise FileNotFoundError(
            "Phase 23 needs scenario-level Phase 16 warning rows or Phase 15 risk rows; neither was readable."
        )

    pixel_warning_rows = read_csv_rows(phase16_paths["pixel_warning_summary"])
    phase15_summary = read_json_if_exists(phase15_paths["summary"])
    phase16_summary = read_json_if_exists(phase16_paths["summary"])
    warning_rules = read_json_if_exists(phase16_paths["warning_rules"])

    component_cols = component_fields(scenario_rows)
    selected_source_rows, selection_notes = select_cases(scenario_rows)
    selected_rows = build_selected_case_rows(selected_source_rows, component_cols)

    selected_fieldnames = [
        "case_role",
        "scenario_identity",
        "warning_level",
        "seed",
        "run_name",
        "location",
        "event",
        "start_idx",
        "batch_index",
        "sample_index",
        "maps_path",
        "risk_score",
        "false_dry_rate",
        "boundary_false_dry_rate",
        "wet_fraction_contraction",
        "peak_underprediction",
        "rmse",
        "dominant_risk_components",
        "model_reliability_interpretation",
        "suggested_warning_action",
        "applicability_boundary_note",
        "selection_basis",
    ]
    write_csv_rows(output_dir / "selected_cases.csv", selected_rows, selected_fieldnames)

    generated_figures: list[Path] = []
    overview_path = figures_dir / "case_warning_level_overview.png"
    save_warning_level_overview(overview_path, selected_rows, scenario_rows)
    generated_figures.append(overview_path)

    component_path = figures_dir / "case_risk_component_comparison.png"
    if save_risk_component_comparison(component_path, selected_rows, selected_source_rows, component_cols):
        generated_figures.append(component_path)

    map_status: dict[str, Any] = {"generated": False, "notes": []}
    warning_grid = pixel_warning_grid(pixel_warning_rows)
    if warning_grid is None:
        map_status["notes"].append("Phase 16 pixel warning grid was unavailable or missing row/col coordinates.")

    for row in selected_rows:
        figure_name = f"{row['case_role'].replace('-', '_')}_case_maps.png"
        figure_path = figures_dir / figure_name
        if save_case_map_figure(figure_path, row, warning_grid):
            generated_figures.append(figure_path)
            map_status["generated"] = True
            map_status["notes"].append(f"Generated {display_path(figure_path)} from {row.get('maps_path', '')}.")
        else:
            map_status["notes"].append(
                f"Map figure for {row['case_role']} case was skipped because source arrays were unavailable or unreadable."
            )

    figure_paths = [display_path(path) for path in generated_figures]
    write_report(output_dir / "case_warning_report.md", selected_rows, figure_paths, map_status, missing_inputs)

    constraints = {
        "trained_model": False,
        "generated_new_predictions": False,
        "evaluated_model_from_checkpoint": False,
        "modified_model_architecture": False,
        "modified_phase10_loss": False,
        "tuned_boundary_weight": False,
        "tuned_boundary_band_pixels": False,
        "opened_new_sweep": False,
        "performed_metric_chasing_experiment": False,
        "performed_manuscript_literature_review": False,
    }
    summary = {
        "phase": "Phase 23 Reliability-Aware Warning Case Study",
        "interpretation_note": INTERPRETATION_NOTE,
        "inputs": {
            "phase15_dir": display_path(phase15_dir),
            "phase16_dir": display_path(phase16_dir),
            "scenario_source": display_path(scenario_source),
            "expected_inputs": {key: display_path(path) for key, path in all_input_paths.items()},
            "missing_inputs": missing_inputs,
            "phase15_summary_loaded": phase15_summary is not None,
            "phase16_summary_loaded": phase16_summary is not None,
            "warning_rules_loaded": warning_rules is not None,
        },
        "constraints": constraints,
        "row_counts": {
            "scenario_rows_used": len(scenario_rows),
            "pixel_warning_rows": len(pixel_warning_rows),
            "selected_cases": len(selected_rows),
        },
        "selection": {
            "required_case_roles": list(CASE_ROLES),
            "selected_case_roles": [row["case_role"] for row in selected_rows],
            "selection_notes": selection_notes,
            "selected_cases": selected_rows,
        },
        "figures": {
            "generated": figure_paths,
            "map_level_visualizations_generated": bool(map_status.get("generated")),
            "map_level_status": map_status,
        },
        "outputs": {
            "summary_json": display_path(output_dir / "summary.json"),
            "selected_cases_csv": display_path(output_dir / "selected_cases.csv"),
            "case_warning_report_md": display_path(output_dir / "case_warning_report.md"),
            "figures_dir": display_path(figures_dir),
        },
        "limitations": [
            "Warning levels are deterministic screening and warning-rule labels, not calibrated probabilities.",
            "Case map figures reuse existing .npz forecast artifacts referenced by the selected rows; no new predictions are generated.",
            "The pixel-warning panel summarizes Phase 16 repeated pixel-warning signals and is not a newly generated case-specific uncertainty field.",
        ],
    }
    write_json(output_dir / "summary.json", summary)

    print(f"Wrote Phase 23 warning case-study outputs to {display_path(output_dir)}")
    print("Selected cases:")
    for row in selected_rows:
        print(f"- {row['case_role']}: {row['scenario_identity']} ({row['warning_level']})")
    print(f"Generated figures: {len(generated_figures)}")
    if missing_inputs:
        print("Missing expected inputs: " + ", ".join(missing_inputs))


if __name__ == "__main__":
    main()
