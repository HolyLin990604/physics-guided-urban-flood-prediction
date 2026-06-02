from __future__ import annotations

import argparse
import ast
import csv
import json
import random
import sys
import time
import tracemalloc
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import torch
import torch.nn.functional as functional
from torch.utils.data import DataLoader, Dataset

from models.unet_tcn import UNetTCNForecaster
from trainers.train import build_loss, train_one_epoch
from trainers.validate import validate_one_epoch


EXPECTED_OUTPUT_DIR = Path("runs/phase47_full_downsample128_baseline_seed42_10e")
EXPECTED_ANALYSIS_DIR = Path("analysis/phase47_controlled_downsample_baseline")
EXPECTED_SCENARIO_INDEX = Path("analysis/phase45_full_dataset_indexing/scenario_index.csv")
EXPECTED_STATIC_INDEX = Path("analysis/phase45_full_dataset_indexing/static_geodata_index.csv")
EXPECTED_TRAINING_COMMAND = (
    "python scripts/train_phase47_full_downsample_baseline.py "
    "--config configs/train_phase47_full_downsample128_seed42_10e.json"
)

REQUIRED_CONFIG_VALUES = {
    "phase": 47,
    "seed": 42,
    "resolution": 128,
    "dataset_root": "E:/BaiduNetdiskDownload/urbanflood24/urbanflood24",
    "scenario_index_path": str(EXPECTED_SCENARIO_INDEX).replace("\\", "/"),
    "static_index_path": str(EXPECTED_STATIC_INDEX).replace("\\", "/"),
    "output_dir": str(EXPECTED_OUTPUT_DIR).replace("\\", "/"),
    "analysis_dir": str(EXPECTED_ANALYSIS_DIR).replace("\\", "/"),
    "no_swe_pinn": True,
    "level5_supported": False,
    "training_scope": "controlled_128_downsample_seed42_pilot",
}

REQUIRED_SCENARIO_COLUMNS = (
    "split",
    "location",
    "scenario",
    "scenario_type",
    "flood_path",
    "rainfall_path",
    "flood_shape",
    "rainfall_shape",
    "rainfall_length",
    "static_dem_path",
    "static_impervious_path",
    "static_manhole_path",
)

REQUIRED_STATIC_COLUMNS = (
    "split",
    "location",
    "absolute_dem_path",
    "impervious_path",
    "manhole_path",
    "static_coverage_status",
)

PROHIBITED_CONFIG_KEYS = {
    "seed123",
    "seed202",
    "seed_sweep",
    "seeds",
    "sweep",
    "hyperparameter_sweep",
    "resolution_sweep",
    "resolutions",
    "tile_training",
    "multiscale_training",
    "full_500_training",
    "pinn",
    "swe_residual",
    "level5_claim",
}


@dataclass(frozen=True)
class WindowRef:
    row_index: int
    start_idx: int


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run the bounded Phase 47 controlled 128x128 UrbanFlood24 full-dataset "
            "downsample baseline pilot."
        )
    )
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate config, indexes, dataloader, and one model forward pass without training or writing run outputs.",
    )
    return parser.parse_args()


def repo_path(path: str | Path) -> Path:
    candidate = Path(path).expanduser()
    return candidate if candidate.is_absolute() else REPO_ROOT / candidate


def rel_text(path: str | Path) -> str:
    return str(Path(path)).replace("\\", "/")


def path_text(path: str | Path) -> str:
    return str(Path(path).resolve()).replace("\\", "/")


def bool_text(value: bool) -> str:
    return str(bool(value)).lower()


def load_json(path: Path) -> dict[str, Any]:
    resolved = repo_path(path)
    return json.loads(resolved.read_text(encoding="utf-8"))


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)


def flatten_keys(value: Any, prefix: str = "") -> set[str]:
    keys: set[str] = set()
    if isinstance(value, dict):
        for key, item in value.items():
            key_text = str(key)
            keys.add(key_text)
            nested_prefix = f"{prefix}.{key_text}" if prefix else key_text
            keys.update(flatten_keys(item, nested_prefix))
    elif isinstance(value, list):
        for item in value:
            keys.update(flatten_keys(item, prefix))
    return keys


def validate_phase47_config(config: dict[str, Any]) -> None:
    for key, expected in REQUIRED_CONFIG_VALUES.items():
        actual = config.get(key)
        if isinstance(expected, str):
            actual = rel_text(actual)
        if actual != expected:
            raise ValueError(f"Phase 47 config requires {key}={expected!r}, got {actual!r}.")

    if int(config.get("epochs", 0)) > 10:
        raise ValueError(f"Phase 47 pilot epochs must be <= 10, got {config.get('epochs')}.")
    if int(config["resolution"]) != 128:
        raise ValueError("Phase 47 implementation is bounded to 128x128 only.")
    if int(config["seed"]) != 42:
        raise ValueError("Phase 47 implementation is bounded to seed42 only.")

    present_prohibited = sorted(PROHIBITED_CONFIG_KEYS & flatten_keys(config))
    if present_prohibited:
        raise ValueError(f"Prohibited Phase 47 config keys present: {present_prohibited}.")

    dataset_cfg = config.get("dataset", {})
    if int(dataset_cfg.get("input_steps", 0)) <= 0 or int(dataset_cfg.get("pred_steps", 0)) <= 0:
        raise ValueError("input_steps and pred_steps must be positive.")
    if int(dataset_cfg.get("max_windows_per_scenario", 0)) <= 0:
        raise ValueError("max_windows_per_scenario must be positive and bounded.")
    if dataset_cfg.get("rainfall_alignment") != "proportional_bin_mean_known_forcing":
        raise ValueError("Phase 47 rainfall alignment must be proportional_bin_mean_known_forcing.")


def parse_shape(value: Any) -> tuple[int, ...] | None:
    try:
        parsed = ast.literal_eval(str(value))
    except (SyntaxError, ValueError):
        return None
    if not isinstance(parsed, tuple):
        return None
    try:
        return tuple(int(item) for item in parsed)
    except (TypeError, ValueError):
        return None


def read_csv_rows(path: Path, required_columns: tuple[str, ...], label: str) -> list[dict[str, str]]:
    if not path.exists():
        raise FileNotFoundError(f"Missing {label}: {path}")
    with path.open("r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        rows = [dict(row) for row in reader]
        columns = set(reader.fieldnames or [])
    missing = sorted(set(required_columns) - columns)
    if missing:
        raise ValueError(f"{label} is missing required columns: {missing}")
    return rows


def validate_indexes(config: dict[str, Any]) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    scenario_rows = read_csv_rows(
        repo_path(config["scenario_index_path"]),
        REQUIRED_SCENARIO_COLUMNS,
        "Phase 45 scenario index",
    )
    static_rows = read_csv_rows(
        repo_path(config["static_index_path"]),
        REQUIRED_STATIC_COLUMNS,
        "Phase 45 static geodata index",
    )
    split_counts = Counter(row["split"] for row in scenario_rows)
    if split_counts.get("train", 0) != 120 or split_counts.get("test", 0) != 48:
        raise ValueError(f"Expected Phase 45 split counts train=120/test=48, got {dict(split_counts)}.")
    if len(scenario_rows) != 168:
        raise ValueError(f"Expected 168 indexed scenarios, got {len(scenario_rows)}.")
    if len(static_rows) != 6:
        raise ValueError(f"Expected 6 static geodata rows, got {len(static_rows)}.")
    return scenario_rows, static_rows


def validate_row_shapes(rows: list[dict[str, str]]) -> None:
    for row in rows:
        flood_shape = parse_shape(row.get("flood_shape"))
        rainfall_shape = parse_shape(row.get("rainfall_shape"))
        if flood_shape not in {(360, 1, 500, 500), (480, 1, 500, 500)}:
            raise ValueError(f"Unsupported flood shape for {row['split']}/{row['scenario']}: {flood_shape}")
        if rainfall_shape not in {(180,), (360,)}:
            raise ValueError(f"Unsupported rainfall shape for {row['split']}/{row['scenario']}: {rainfall_shape}")


def align_rainfall_to_flood_steps(rainfall: np.ndarray, flood_steps: int) -> np.ndarray:
    rainfall = np.asarray(rainfall, dtype=np.float32).reshape(-1)
    if rainfall.size not in {180, 360}:
        raise ValueError(f"Unsupported rainfall length {rainfall.size}; expected 180 or 360.")
    if flood_steps not in {360, 480}:
        raise ValueError(f"Unsupported flood length {flood_steps}; expected 360 or 480.")

    aligned = np.zeros((flood_steps,), dtype=np.float32)
    for step in range(flood_steps):
        left = step * rainfall.size / flood_steps
        right = (step + 1) * rainfall.size / flood_steps
        start = int(np.floor(left))
        stop = int(np.ceil(right))
        segment = rainfall[max(start, 0) : min(stop, rainfall.size)]
        if segment.size:
            aligned[step] = float(segment.mean())
        else:
            midpoint = (left + right) * 0.5
            aligned[step] = float(np.interp(midpoint, np.arange(rainfall.size), rainfall))
    return aligned


def downsample_tensor(array: np.ndarray, resolution: int, *, is_static: bool) -> torch.Tensor:
    tensor = torch.from_numpy(np.array(array, dtype=np.float32, copy=True))
    if is_static:
        tensor = tensor.unsqueeze(0)
    with torch.no_grad():
        resized = functional.interpolate(
            tensor,
            size=(resolution, resolution),
            mode="bilinear",
            align_corners=False,
        )
    if is_static:
        resized = resized.squeeze(0)
    return resized.contiguous()


class Phase47IndexedDownsampleDataset(Dataset):
    """
    Script-local adapter plumbing for Phase 45 indexed UrbanFlood24 full data.

    It lazily opens `.npy` arrays with mmap, creates fixed windows, downsamples
    flood/static tensors to 128x128 in memory, and returns the existing model's
    expected batch keys. Future rainfall is used as known forcing for this
    supervised baseline and is recorded in the config.
    """

    def __init__(
        self,
        rows: list[dict[str, str]],
        *,
        split: str,
        input_steps: int,
        pred_steps: int,
        stride: int,
        max_windows_per_scenario: int,
        resolution: int,
    ) -> None:
        self.rows = [row for row in rows if row["split"] == split]
        self.split = split
        self.input_steps = int(input_steps)
        self.pred_steps = int(pred_steps)
        self.stride = int(stride)
        self.max_windows_per_scenario = int(max_windows_per_scenario)
        self.resolution = int(resolution)
        self._static_cache: dict[tuple[str, str, str], torch.Tensor] = {}
        self.windows = self._build_windows()
        if not self.windows:
            raise ValueError(f"No Phase 47 windows created for split {split}.")

    def __len__(self) -> int:
        return len(self.windows)

    def __getitem__(self, idx: int) -> dict[str, Any]:
        ref = self.windows[idx]
        row = self.rows[ref.row_index]
        total_steps = self.input_steps + self.pred_steps
        end_idx = ref.start_idx + total_steps

        flood = np.load(Path(row["flood_path"]), mmap_mode="r")
        rainfall = np.load(Path(row["rainfall_path"]), mmap_mode="r")
        flood_window = np.asarray(flood[ref.start_idx:end_idx], dtype=np.float32)
        if flood_window.shape != (total_steps, 1, 500, 500):
            raise ValueError(f"Unexpected flood window shape {flood_window.shape} for {row['scenario']}.")

        flood_downsampled = downsample_tensor(flood_window, self.resolution, is_static=False)
        aligned_rainfall = align_rainfall_to_flood_steps(np.asarray(rainfall), int(flood.shape[0]))
        rainfall_window = aligned_rainfall[ref.start_idx:end_idx]
        if rainfall_window.shape != (total_steps,):
            raise ValueError(f"Unexpected rainfall window shape {rainfall_window.shape} for {row['scenario']}.")

        static_maps = self._load_static_maps(row)
        past_flood = flood_downsampled[: self.input_steps]
        future_flood = flood_downsampled[self.input_steps :]
        past_rainfall = torch.from_numpy(rainfall_window[: self.input_steps, None].astype(np.float32, copy=True))
        future_rainfall = torch.from_numpy(rainfall_window[self.input_steps :, None].astype(np.float32, copy=True))

        return {
            "past_flood": past_flood,
            "past_rainfall": past_rainfall,
            "future_rainfall": future_rainfall,
            "static_maps": static_maps,
            "future_flood": future_flood,
            "metadata": {
                "split": row["split"],
                "location": row["location"],
                "scenario": row["scenario"],
                "scenario_type": row["scenario_type"],
                "start_idx": ref.start_idx,
                "input_steps": self.input_steps,
                "pred_steps": self.pred_steps,
                "resolution": self.resolution,
            },
        }

    def describe(self) -> dict[str, Any]:
        return {
            "split": self.split,
            "scenario_count": len(self.rows),
            "sample_count": len(self.windows),
            "input_steps": self.input_steps,
            "pred_steps": self.pred_steps,
            "stride": self.stride,
            "max_windows_per_scenario": self.max_windows_per_scenario,
            "resolution": self.resolution,
            "flood_shape_counts": dict(Counter(row["flood_shape"] for row in self.rows)),
            "rainfall_length_counts": dict(Counter(row["rainfall_length"] for row in self.rows)),
        }

    @staticmethod
    def collate(samples: list[dict[str, Any]]) -> dict[str, Any]:
        tensor_keys = ("past_flood", "past_rainfall", "future_rainfall", "static_maps", "future_flood")
        batch = {key: torch.stack([sample[key] for sample in samples], dim=0) for key in tensor_keys}
        batch["metadata"] = [sample["metadata"] for sample in samples]
        return batch

    def _build_windows(self) -> list[WindowRef]:
        windows: list[WindowRef] = []
        total_steps = self.input_steps + self.pred_steps
        for row_index, row in enumerate(self.rows):
            flood_shape = parse_shape(row["flood_shape"])
            if flood_shape is None:
                continue
            flood_steps = flood_shape[0]
            last_start = flood_steps - total_steps
            if last_start < 0:
                continue
            candidates = list(range(0, last_start + 1, self.stride))
            if len(candidates) > self.max_windows_per_scenario:
                positions = np.linspace(0, len(candidates) - 1, self.max_windows_per_scenario)
                selected = [candidates[int(round(position))] for position in positions]
            else:
                selected = candidates
            for start_idx in dict.fromkeys(selected):
                windows.append(WindowRef(row_index=row_index, start_idx=int(start_idx)))
        return windows

    def _load_static_maps(self, row: dict[str, str]) -> torch.Tensor:
        key = (row["static_dem_path"], row["static_impervious_path"], row["static_manhole_path"])
        cached = self._static_cache.get(key)
        if cached is not None:
            return cached

        static_stack = np.stack(
            [
                np.asarray(np.load(Path(row["static_dem_path"]), mmap_mode="r"), dtype=np.float32),
                np.asarray(np.load(Path(row["static_impervious_path"]), mmap_mode="r"), dtype=np.float32),
                np.asarray(np.load(Path(row["static_manhole_path"]), mmap_mode="r"), dtype=np.float32),
            ],
            axis=0,
        )
        if static_stack.shape != (3, 500, 500):
            raise ValueError(f"Unexpected static stack shape {static_stack.shape} for {row['split']}/{row['location']}.")
        downsampled = downsample_tensor(static_stack, self.resolution, is_static=True)
        self._static_cache[key] = downsampled
        return downsampled


def build_model(config: dict[str, Any]) -> UNetTCNForecaster:
    model_cfg = config["model"]
    return UNetTCNForecaster(
        flood_channels=model_cfg["flood_channels"],
        static_channels=model_cfg["static_channels"],
        rainfall_channels=model_cfg["rainfall_channels"],
        out_channels=model_cfg["out_channels"],
        base_channels=model_cfg["base_channels"],
        encoder_levels=model_cfg["encoder_levels"],
        temporal_hidden_channels=model_cfg["temporal_hidden_channels"],
        temporal_layers=model_cfg["temporal_layers"],
        temporal_kernel_size=model_cfg["temporal_kernel_size"],
        dropout=model_cfg["dropout"],
        skip_fusion_mode=model_cfg.get("skip_fusion_mode", "temporal_mean"),
    )


def build_datasets(config: dict[str, Any], scenario_rows: list[dict[str, str]]) -> tuple[Dataset, Dataset]:
    dataset_cfg = config["dataset"]
    common = {
        "input_steps": int(dataset_cfg["input_steps"]),
        "pred_steps": int(dataset_cfg["pred_steps"]),
        "stride": int(dataset_cfg["sampling_stride"]),
        "max_windows_per_scenario": int(dataset_cfg["max_windows_per_scenario"]),
        "resolution": int(config["resolution"]),
    }
    train_dataset = Phase47IndexedDownsampleDataset(
        scenario_rows,
        split=dataset_cfg["train_split"],
        **common,
    )
    test_dataset = Phase47IndexedDownsampleDataset(
        scenario_rows,
        split=dataset_cfg["test_split"],
        **common,
    )
    return train_dataset, test_dataset


def make_loader(dataset: Dataset, *, batch_size: int, shuffle: bool, config: dict[str, Any]) -> DataLoader:
    generator = torch.Generator()
    generator.manual_seed(int(config["seed"]))
    return DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=shuffle,
        num_workers=int(config["runtime"]["num_workers"]),
        pin_memory=torch.cuda.is_available(),
        collate_fn=Phase47IndexedDownsampleDataset.collate,
        generator=generator if shuffle else None,
    )


def dry_run(config: dict[str, Any], train_dataset: Dataset, test_dataset: Dataset) -> None:
    loader = make_loader(
        train_dataset,
        batch_size=int(config["optimization"]["batch_size"]),
        shuffle=False,
        config=config,
    )
    batch = next(iter(loader))
    model = build_model(config)
    with torch.no_grad():
        prediction = model(
            batch["past_flood"].float(),
            batch["past_rainfall"].float(),
            batch["future_rainfall"].float(),
            batch["static_maps"].float(),
        )
    if prediction.shape != batch["future_flood"].shape:
        raise ValueError(
            f"Dry-run prediction shape {tuple(prediction.shape)} != target shape {tuple(batch['future_flood'].shape)}."
        )
    print("dry_run=true")
    print(f"train_dataset={json.dumps(train_dataset.describe(), sort_keys=True)}")
    print(f"test_dataset={json.dumps(test_dataset.describe(), sort_keys=True)}")
    print(f"batch_past_flood_shape={tuple(batch['past_flood'].shape)}")
    print(f"batch_static_maps_shape={tuple(batch['static_maps'].shape)}")
    print(f"batch_future_flood_shape={tuple(batch['future_flood'].shape)}")
    print(f"prediction_shape={tuple(prediction.shape)}")
    print(f"expected_training_command={EXPECTED_TRAINING_COMMAND}")


def write_metrics_csv(path: Path, history: list[dict[str, float]]) -> None:
    if not history:
        return
    fieldnames = list(history[0].keys())
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in history:
            writer.writerow(row)


def memory_snapshot(device: torch.device, start_time: float) -> dict[str, Any]:
    current, peak = tracemalloc.get_traced_memory()
    snapshot: dict[str, Any] = {
        "runtime_seconds": time.perf_counter() - start_time,
        "tracemalloc_current_mb": current / (1024 * 1024),
        "tracemalloc_peak_mb": peak / (1024 * 1024),
    }
    if device.type == "cuda":
        snapshot["cuda_max_allocated_mb"] = torch.cuda.max_memory_allocated(device) / (1024 * 1024)
        snapshot["cuda_max_reserved_mb"] = torch.cuda.max_memory_reserved(device) / (1024 * 1024)
    return snapshot


def write_runtime_memory_notes(path: Path, config: dict[str, Any], memory: dict[str, Any]) -> None:
    lines = [
        "# Phase 47 Runtime And Memory Notes",
        "",
        "- Run scope: controlled 128x128 full-dataset downsample baseline, seed42 only.",
        "- Dataset access: `numpy.load(..., mmap_mode=\"r\")` for flood, rainfall, and static arrays.",
        "- Downsampling: in-memory bilinear interpolation to 128x128 per batch/sample.",
        "- Transformed training datasets written to disk: false.",
        "- Future rainfall usage: known forcing, aligned by proportional bin mean over flood steps.",
        "- SWE residuals and PINN components used: false.",
        f"- Batch size: `{config['optimization']['batch_size']}`.",
        f"- Eval batch size: `{config['optimization']['eval_batch_size']}`.",
        f"- Runtime seconds: `{memory['runtime_seconds']:.3f}`.",
        f"- Tracemalloc peak MB: `{memory['tracemalloc_peak_mb']:.3f}`.",
    ]
    if "cuda_max_allocated_mb" in memory:
        lines.append(f"- CUDA max allocated MB: `{memory['cuda_max_allocated_mb']:.3f}`.")
        lines.append(f"- CUDA max reserved MB: `{memory['cuda_max_reserved_mb']:.3f}`.")
    path.write_text("\n".join(lines), encoding="utf-8")


def write_summary_md(path: Path, summary: dict[str, Any]) -> None:
    lines = [
        "# Phase 47 Controlled Downsample Baseline Training Summary",
        "",
        f"- selected_decision: `{summary['selected_decision']}`",
        f"- phase: `{summary['phase']}`",
        f"- seed: `{summary['seed']}`",
        f"- resolution: `{summary['resolution']}`",
        f"- epochs: `{summary['epochs']}`",
        f"- train_samples: `{summary['train_dataset']['sample_count']}`",
        f"- test_samples: `{summary['test_dataset']['sample_count']}`",
        f"- best_test_rmse: `{summary.get('best_test_rmse')}`",
        f"- no_swe_pinn: `{bool_text(summary['no_swe_pinn'])}`",
        f"- level5_supported: `{bool_text(summary['level5_supported'])}`",
        f"- training_command: `{EXPECTED_TRAINING_COMMAND}`",
        "",
        "This run used the existing U-Net + TCN supervised model family with script-local adapter plumbing for Phase 45 indexed full-dataset input compatibility.",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def run_training(config: dict[str, Any], train_dataset: Dataset, test_dataset: Dataset) -> None:
    output_dir = repo_path(config["output_dir"])
    analysis_dir = repo_path(config["analysis_dir"])
    checkpoints_dir = output_dir / "checkpoints"
    output_dir.mkdir(parents=True, exist_ok=True)
    analysis_dir.mkdir(parents=True, exist_ok=True)
    checkpoints_dir.mkdir(parents=True, exist_ok=True)

    (output_dir / "training_config_snapshot.json").write_text(
        json.dumps(config, indent=2, sort_keys=True),
        encoding="utf-8",
    )

    device = torch.device(config["runtime"]["device"] if torch.cuda.is_available() else "cpu")
    if device.type == "cuda":
        torch.cuda.reset_peak_memory_stats(device)

    train_loader = make_loader(
        train_dataset,
        batch_size=int(config["optimization"]["batch_size"]),
        shuffle=True,
        config=config,
    )
    test_loader = make_loader(
        test_dataset,
        batch_size=int(config["optimization"]["eval_batch_size"]),
        shuffle=False,
        config=config,
    )

    model = build_model(config).to(device)
    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=float(config["optimization"]["lr"]),
        weight_decay=float(config["optimization"]["weight_decay"]),
    )
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=int(config["epochs"]))
    criterion = build_loss(config["optimization"]["loss"])
    scaler = torch.cuda.amp.GradScaler(enabled=device.type == "cuda" and bool(config["runtime"]["use_amp"]))

    history: list[dict[str, float]] = []
    best_metric: float | None = None
    start_time = time.perf_counter()
    tracemalloc.start()

    for epoch in range(1, int(config["epochs"]) + 1):
        train_metrics = train_one_epoch(
            model,
            train_loader,
            optimizer,
            device,
            criterion,
            wet_threshold=float(config["metrics"]["wet_threshold"]),
            scaler=scaler,
            grad_clip_norm=float(config["optimization"]["grad_clip_norm"]),
            use_amp=bool(config["runtime"]["use_amp"]),
            physics_controller=None,
        )
        test_metrics = validate_one_epoch(
            model,
            test_loader,
            device,
            criterion,
            wet_threshold=float(config["metrics"]["wet_threshold"]),
            physics_controller=None,
        )
        scheduler.step()
        record = {
            "epoch": epoch,
            **{f"train_{key}": value for key, value in train_metrics.items()},
            **{f"test_{key}": value for key, value in test_metrics.items()},
        }
        history.append(record)
        print(json.dumps(record, indent=2, sort_keys=True))

        current_metric = float(test_metrics["rmse"])
        if best_metric is None or current_metric < best_metric:
            best_metric = current_metric
            torch.save(
                {
                    "epoch": epoch,
                    "model_state": model.state_dict(),
                    "optimizer_state": optimizer.state_dict(),
                    "scheduler_state": scheduler.state_dict(),
                    "config": config,
                    "best_test_rmse": best_metric,
                },
                checkpoints_dir / "best.pt",
            )

    memory = memory_snapshot(device, start_time)
    tracemalloc.stop()
    metrics_json = {"history": history, "best_test_rmse": best_metric}
    (output_dir / "metrics.json").write_text(json.dumps(metrics_json, indent=2, sort_keys=True), encoding="utf-8")
    write_metrics_csv(output_dir / "metrics.csv", history)
    write_runtime_memory_notes(output_dir / "runtime_memory_notes.md", config, memory)

    summary = {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "selected_decision": "phase47_controlled_128_downsample_seed42_pilot_completed",
        "phase": config["phase"],
        "seed": config["seed"],
        "resolution": config["resolution"],
        "epochs": config["epochs"],
        "training_scope": config["training_scope"],
        "no_swe_pinn": config["no_swe_pinn"],
        "level5_supported": config["level5_supported"],
        "train_dataset": train_dataset.describe(),
        "test_dataset": test_dataset.describe(),
        "best_test_rmse": best_metric,
        "memory": memory,
        "outputs": {
            "training_config_snapshot_json": path_text(output_dir / "training_config_snapshot.json"),
            "metrics_json": path_text(output_dir / "metrics.json"),
            "metrics_csv": path_text(output_dir / "metrics.csv"),
            "runtime_memory_notes_md": path_text(output_dir / "runtime_memory_notes.md"),
            "phase47_training_summary_json": path_text(analysis_dir / "phase47_training_summary.json"),
            "phase47_training_summary_md": path_text(analysis_dir / "phase47_training_summary.md"),
        },
    }
    (analysis_dir / "phase47_training_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    write_summary_md(analysis_dir / "phase47_training_summary.md", summary)


def main() -> None:
    args = parse_args()
    config = load_json(args.config)
    validate_phase47_config(config)
    set_seed(int(config["seed"]))
    scenario_rows, _static_rows = validate_indexes(config)
    validate_row_shapes(scenario_rows)
    train_dataset, test_dataset = build_datasets(config, scenario_rows)

    if args.dry_run:
        dry_run(config, train_dataset, test_dataset)
        return

    run_training(config, train_dataset, test_dataset)


if __name__ == "__main__":
    main()
