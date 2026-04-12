from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

import numpy as np

from datasets.rainfall_alignment import (
    SUPPORTED_ALIGNMENT_MODES,
    align_rainfall_sequence,
    summarize_alignment_change,
)


EXPECTED_STATIC_FILES: Tuple[str, ...] = (
    "absolute_DEM.npy",
    "impervious.npy",
    "manhole.npy",
)


DEFAULT_CONFIG: Dict[str, Any] = {
    "dataset_root": r"data\urbanflood24_lite",
    "split": "train",
    "input_steps": 12,
    "pred_steps": 12,
    "stride": 6,
    "alignment_mode": "mass_preserving",
    "debug": False,
    "cache_arrays": False,
    "include_partial_windows": False,
    "return_numpy": True,
    "locations": None,
    "events": None,
}


class DatasetStructureError(RuntimeError):
    """Raised when the dataset directory does not match the expected layout."""


@dataclass(frozen=True)
class EventRecord:
    split: str
    location: str
    event: str
    flood_path: Path
    rainfall_path: Path
    static_paths: Tuple[Path, ...]
    flood_steps: int
    rainfall_steps: int
    grid_shape: Tuple[int, int]


@dataclass(frozen=True)
class SampleIndex:
    event_idx: int
    start_idx: int


def load_dataset_config(config_path: str | Path | None = None) -> Dict[str, Any]:
    config = dict(DEFAULT_CONFIG)
    if config_path is None:
        return config

    path = Path(config_path).expanduser().resolve()
    _ensure_exists(path, "dataset config file")
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Failed to parse JSON config at {path}: {exc}") from exc

    if not isinstance(loaded, dict):
        raise ValueError(f"Expected a JSON object in {path}, got {type(loaded).__name__}.")

    unknown_keys = sorted(set(loaded) - set(DEFAULT_CONFIG))
    if unknown_keys:
        raise ValueError(
            f"Unknown config keys in {path}: {unknown_keys}. "
            f"Allowed keys are {sorted(DEFAULT_CONFIG)}."
        )

    config.update(loaded)
    return config


def _ensure_exists(path: Path, kind: str) -> None:
    if not path.exists():
        raise DatasetStructureError(f"Missing {kind}: {path}")


def _load_npy(path: Path, *, expected_ndim: Optional[int] = None) -> np.ndarray:
    try:
        array = np.load(path)
    except Exception as exc:  # pragma: no cover - delegated to numpy
        raise RuntimeError(f"Failed to load numpy file at {path}: {exc}") from exc

    if expected_ndim is not None and array.ndim != expected_ndim:
        raise ValueError(
            f"Expected {path.name} at {path} to have {expected_ndim} dims, "
            f"but found shape {array.shape}."
        )
    return array.astype(np.float32, copy=False)


class UrbanFlood24LiteProcessDataset:
    """
    Process-prediction adapter for UrbanFlood24 Lite.

    The adapter keeps flood and rainfall as separate modalities:
    - past_flood: [input_steps, 1, H, W]
    - past_rainfall: [input_steps, 1]
    - future_rainfall: [pred_steps, 1]
    - static_maps: [3, H, W]
    - future_flood: [pred_steps, 1, H, W]

    Scientific note:
    Rainfall-to-flood alignment is not given explicitly by the raw files, so every
    alignment mode below is a modeling assumption. `mass_preserving` best preserves
    cumulative rainfall if the coarse rainfall samples are interpreted as per-step
    rainfall amounts. `piecewise_constant`, `linear`, and `repeat_if_integer_ratio`
    are reasonable intensity-style resampling assumptions, but they do not generally
    preserve the original cumulative total after resampling.
    """

    def __init__(
        self,
        root_dir: str | Path,
        *,
        split: str = "train",
        input_steps: int = 12,
        pred_steps: int = 12,
        stride: int = 1,
        locations: Optional[Sequence[str]] = None,
        events: Optional[Sequence[str]] = None,
        alignment_mode: str = "mass_preserving",
        debug: bool = False,
        cache_arrays: bool = False,
        include_partial_windows: bool = False,
        return_numpy: bool = True,
    ) -> None:
        self.root_dir = Path(root_dir).expanduser().resolve()
        self.split = split
        self.input_steps = int(input_steps)
        self.pred_steps = int(pred_steps)
        self.stride = int(stride)
        self.locations = set(locations) if locations else None
        self.events = set(events) if events else None
        self.alignment_mode = alignment_mode
        self.debug = debug
        self.cache_arrays = cache_arrays
        self.include_partial_windows = include_partial_windows
        self.return_numpy = return_numpy

        if self.input_steps <= 0:
            raise ValueError(f"input_steps must be positive, got {self.input_steps}.")
        if self.pred_steps <= 0:
            raise ValueError(f"pred_steps must be positive, got {self.pred_steps}.")
        if self.stride <= 0:
            raise ValueError(f"stride must be positive, got {self.stride}.")
        if self.alignment_mode not in SUPPORTED_ALIGNMENT_MODES:
            raise ValueError(
                f"Unsupported alignment_mode '{self.alignment_mode}'. "
                f"Expected one of {SUPPORTED_ALIGNMENT_MODES}."
            )

        self._split_dir = self.root_dir / self.split
        _ensure_exists(self.root_dir, "dataset root")
        _ensure_exists(self._split_dir, "split directory")
        _ensure_exists(self._split_dir / "flood", "flood directory")
        _ensure_exists(self._split_dir / "geodata", "geodata directory")

        self._event_records = self._discover_events()
        if not self._event_records:
            raise DatasetStructureError(
                f"No events found under split '{self.split}' in {self.root_dir}."
            )

        self._array_cache: Dict[Path, np.ndarray] = {}
        self._sample_index: List[SampleIndex] = self._build_sample_index()
        if not self._sample_index:
            raise ValueError(
                "No valid process-prediction windows were created. "
                f"Check input_steps={self.input_steps}, pred_steps={self.pred_steps}, "
                f"stride={self.stride}, and the available flood sequence lengths."
            )

    @classmethod
    def from_config(
        cls,
        config_path: str | Path,
        *,
        split: Optional[str] = None,
        debug: Optional[bool] = None,
    ) -> "UrbanFlood24LiteProcessDataset":
        config = load_dataset_config(config_path)
        if split is not None:
            config["split"] = split
        if debug is not None:
            config["debug"] = debug
        return cls(
            root_dir=config["dataset_root"],
            split=config["split"],
            input_steps=config["input_steps"],
            pred_steps=config["pred_steps"],
            stride=config["stride"],
            locations=config["locations"],
            events=config["events"],
            alignment_mode=config["alignment_mode"],
            debug=config["debug"],
            cache_arrays=config["cache_arrays"],
            include_partial_windows=config["include_partial_windows"],
            return_numpy=config["return_numpy"],
        )

    def __len__(self) -> int:
        return len(self._sample_index)

    def __getitem__(self, idx: int) -> Dict[str, Any]:
        sample_ref = self._sample_index[idx]
        event_record = self._event_records[sample_ref.event_idx]

        flood = self._get_array(event_record.flood_path, expected_ndim=3)
        rainfall = self._get_array(event_record.rainfall_path, expected_ndim=1)
        static_stack = self._load_static_stack(event_record.static_paths, event_record.grid_shape)
        aligned_rainfall = align_rainfall_sequence(
            rainfall,
            target_steps=flood.shape[0],
            mode=self.alignment_mode,
        )
        alignment_summary = summarize_alignment_change(rainfall, aligned_rainfall)

        total_steps = self.input_steps + self.pred_steps
        start_idx = sample_ref.start_idx
        end_idx = start_idx + total_steps

        if end_idx > flood.shape[0]:
            raise IndexError(
                f"Requested window [{start_idx}, {end_idx}) exceeds flood length "
                f"{flood.shape[0]} for event {event_record.event}."
            )

        flood_window = flood[start_idx:end_idx]
        rainfall_window = aligned_rainfall[start_idx:end_idx]
        past_flood = flood_window[: self.input_steps, None, :, :]
        future_flood = flood_window[self.input_steps :, None, :, :]
        past_rainfall = rainfall_window[: self.input_steps, None]
        future_rainfall = rainfall_window[self.input_steps :, None]

        sample: Dict[str, Any] = {
            "past_flood": past_flood.astype(np.float32, copy=False),
            "past_rainfall": past_rainfall.astype(np.float32, copy=False),
            "future_rainfall": future_rainfall.astype(np.float32, copy=False),
            "static_maps": static_stack.astype(np.float32, copy=False),
            "future_flood": future_flood.astype(np.float32, copy=False),
            "metadata": {
                "split": event_record.split,
                "location": event_record.location,
                "event": event_record.event,
                "start_idx": start_idx,
                "input_steps": self.input_steps,
                "pred_steps": self.pred_steps,
                "alignment_mode": self.alignment_mode,
            },
        }

        if self.debug:
            sample["debug"] = {
                "flood_path": str(event_record.flood_path),
                "rainfall_path": str(event_record.rainfall_path),
                "static_paths": [str(path) for path in event_record.static_paths],
                "raw_flood_shape": tuple(flood.shape),
                "raw_rainfall_shape": tuple(rainfall.shape),
                "aligned_rainfall_shape": tuple(aligned_rainfall.shape),
                "grid_shape": event_record.grid_shape,
                "alignment_mode": self.alignment_mode,
                "alignment_summary": alignment_summary,
            }

        if not self.return_numpy:
            sample = self._maybe_convert_to_torch(sample)
        return sample

    def describe(self) -> Dict[str, Any]:
        flood_lengths = sorted({record.flood_steps for record in self._event_records})
        rainfall_lengths = sorted({record.rainfall_steps for record in self._event_records})
        locations = sorted({record.location for record in self._event_records})
        return {
            "root_dir": str(self.root_dir),
            "split": self.split,
            "num_events": len(self._event_records),
            "num_samples": len(self),
            "locations": locations,
            "flood_lengths": flood_lengths,
            "rainfall_lengths": rainfall_lengths,
            "alignment_mode": self.alignment_mode,
            "supported_alignment_modes": list(SUPPORTED_ALIGNMENT_MODES),
            "input_steps": self.input_steps,
            "pred_steps": self.pred_steps,
            "stride": self.stride,
        }

    def iter_events(self) -> Iterable[EventRecord]:
        return iter(self._event_records)

    def get_sample_event_key(self, idx: int) -> str:
        sample_ref = self._sample_index[idx]
        record = self._event_records[sample_ref.event_idx]
        return f"{record.split}/{record.location}/{record.event}"

    @staticmethod
    def collate_numpy(samples: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
        if not samples:
            raise ValueError("Cannot collate an empty sample list.")

        keys_to_stack = (
            "past_flood",
            "past_rainfall",
            "future_rainfall",
            "static_maps",
            "future_flood",
        )
        batch = {key: np.stack([sample[key] for sample in samples], axis=0) for key in keys_to_stack}
        batch["metadata"] = [sample["metadata"] for sample in samples]
        if "debug" in samples[0]:
            batch["debug"] = [sample["debug"] for sample in samples]
        return batch

    def _discover_events(self) -> List[EventRecord]:
        flood_root = self._split_dir / "flood"
        geodata_root = self._split_dir / "geodata"
        records: List[EventRecord] = []

        for location_dir in sorted(path for path in flood_root.iterdir() if path.is_dir()):
            location = location_dir.name
            if self.locations and location not in self.locations:
                continue

            static_paths = tuple(geodata_root / location / name for name in EXPECTED_STATIC_FILES)
            for static_path in static_paths:
                _ensure_exists(static_path, "static geodata file")

            static_grid_shape = self._validate_static_grid(static_paths)

            for event_dir in sorted(path for path in location_dir.iterdir() if path.is_dir()):
                event = event_dir.name
                if self.events and event not in self.events:
                    continue

                flood_path = event_dir / "flood.npy"
                rainfall_path = event_dir / "rainfall.npy"
                _ensure_exists(flood_path, "flood sequence")
                _ensure_exists(rainfall_path, "rainfall sequence")

                flood = _load_npy(flood_path, expected_ndim=3)
                rainfall = _load_npy(rainfall_path, expected_ndim=1)

                if flood.shape[0] < self.input_steps + self.pred_steps and not self.include_partial_windows:
                    continue
                if flood.shape[1:] != static_grid_shape:
                    raise ValueError(
                        f"Flood grid shape {flood.shape[1:]} for {flood_path} does not match "
                        f"static grid shape {static_grid_shape} for location {location}."
                    )
                if rainfall.shape[0] <= 0:
                    raise ValueError(f"Rainfall file {rainfall_path} is empty.")

                records.append(
                    EventRecord(
                        split=self.split,
                        location=location,
                        event=event,
                        flood_path=flood_path,
                        rainfall_path=rainfall_path,
                        static_paths=static_paths,
                        flood_steps=int(flood.shape[0]),
                        rainfall_steps=int(rainfall.shape[0]),
                        grid_shape=tuple(int(v) for v in static_grid_shape),
                    )
                )
        return records

    def _build_sample_index(self) -> List[SampleIndex]:
        sample_index: List[SampleIndex] = []
        total_steps = self.input_steps + self.pred_steps

        for event_idx, record in enumerate(self._event_records):
            last_start = record.flood_steps - total_steps
            if last_start < 0:
                if self.include_partial_windows:
                    sample_index.append(SampleIndex(event_idx=event_idx, start_idx=0))
                continue
            for start_idx in range(0, last_start + 1, self.stride):
                sample_index.append(SampleIndex(event_idx=event_idx, start_idx=start_idx))
        return sample_index

    def _get_array(self, path: Path, *, expected_ndim: Optional[int] = None) -> np.ndarray:
        if self.cache_arrays and path in self._array_cache:
            array = self._array_cache[path]
        else:
            array = _load_npy(path, expected_ndim=expected_ndim)
            if self.cache_arrays:
                self._array_cache[path] = array

        if expected_ndim is not None and array.ndim != expected_ndim:
            raise ValueError(
                f"Expected cached array at {path} to have {expected_ndim} dims, got {array.shape}."
            )
        return array

    def _validate_static_grid(self, static_paths: Sequence[Path]) -> Tuple[int, int]:
        arrays = [_load_npy(path, expected_ndim=2) for path in static_paths]
        shapes = {array.shape for array in arrays}
        if len(shapes) != 1:
            raise ValueError(
                "Static geodata arrays do not share a consistent grid shape for "
                f"{static_paths[0].parent}: {sorted(shapes)}"
            )
        shape = next(iter(shapes))
        return int(shape[0]), int(shape[1])

    def _load_static_stack(
        self,
        static_paths: Sequence[Path],
        expected_shape: Tuple[int, int],
    ) -> np.ndarray:
        static_arrays = []
        for path in static_paths:
            array = self._get_array(path, expected_ndim=2)
            if tuple(array.shape) != tuple(expected_shape):
                raise ValueError(
                    f"Static map {path} has shape {array.shape}, expected {expected_shape}."
                )
            static_arrays.append(array)
        return np.stack(static_arrays, axis=0)

    def _maybe_convert_to_torch(self, sample: Dict[str, Any]) -> Dict[str, Any]:
        try:
            import torch
        except ImportError as exc:
            raise RuntimeError(
                "return_numpy=False requires PyTorch, but 'torch' is not installed."
            ) from exc

        converted: Dict[str, Any] = {}
        for key, value in sample.items():
            if isinstance(value, np.ndarray):
                converted[key] = torch.from_numpy(value)
            else:
                converted[key] = value
        return converted
