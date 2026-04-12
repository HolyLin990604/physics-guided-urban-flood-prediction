from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Iterable

import numpy as np


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from datasets.rainfall_alignment import SUPPORTED_ALIGNMENT_MODES, align_rainfall_sequence, summarize_alignment_change


def format_values(values: np.ndarray, limit: int) -> str:
    clipped = values[:limit]
    return ", ".join(f"{float(v):.4f}" for v in clipped)


def load_event_arrays(root: Path, split: str, location: str, event: str) -> tuple[np.ndarray, np.ndarray]:
    event_dir = root / split / "flood" / location / event
    rainfall = np.load(event_dir / "rainfall.npy").astype(np.float32, copy=False)
    flood = np.load(event_dir / "flood.npy").astype(np.float32, copy=False)
    return rainfall, flood


def print_mode_report(raw_rainfall: np.ndarray, target_steps: int, modes: Iterable[str], preview_steps: int) -> None:
    raw_sum = float(raw_rainfall.sum())
    print(f"Raw rainfall steps={raw_rainfall.shape[0]} sum={raw_sum:.6f}")
    print(f"Target flood steps={target_steps}")
    print(f"Raw rainfall preview: {format_values(raw_rainfall, preview_steps)}")
    print()

    for mode in modes:
        print(f"Mode: {mode}")
        try:
            aligned = align_rainfall_sequence(raw_rainfall, target_steps=target_steps, mode=mode)
            summary = summarize_alignment_change(raw_rainfall, aligned)
            print(f"  aligned_steps={summary['aligned_steps']}")
            print(f"  aligned_sum={summary['aligned_sum']:.6f}")
            print(f"  sum_difference={summary['sum_difference']:.6f}")
            print(f"  sum_ratio={summary['sum_ratio']:.6f}")
            print(f"  aligned preview: {format_values(aligned, preview_steps)}")
            print(f"  cumulative preview: {format_values(np.cumsum(aligned), preview_steps)}")
        except ValueError as exc:
            print(f"  not applicable: {exc}")
        print()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compare rainfall alignment modes for a real UrbanFlood24 Lite event."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path("data/urbanflood24_lite"),
        help="Dataset root directory.",
    )
    parser.add_argument("--split", default="train", choices=("train", "test"))
    parser.add_argument("--location", default="location2")
    parser.add_argument("--event", default="r300y_p0.4_d3h")
    parser.add_argument("--preview-steps", type=int, default=12)
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print a machine-readable JSON summary after the human-readable report.",
    )
    args = parser.parse_args()

    root = args.root.expanduser().resolve()
    raw_rainfall, flood = load_event_arrays(root, args.split, args.location, args.event)
    target_steps = int(flood.shape[0])

    print(f"Event: {args.split}/{args.location}/{args.event}")
    print_mode_report(raw_rainfall, target_steps, SUPPORTED_ALIGNMENT_MODES, args.preview_steps)

    if args.json:
        payload = {
            "split": args.split,
            "location": args.location,
            "event": args.event,
            "raw_rainfall_steps": int(raw_rainfall.shape[0]),
            "flood_steps": target_steps,
            "modes": {},
        }
        for mode in SUPPORTED_ALIGNMENT_MODES:
            try:
                aligned = align_rainfall_sequence(raw_rainfall, target_steps=target_steps, mode=mode)
                payload["modes"][mode] = {
                    "summary": summarize_alignment_change(raw_rainfall, aligned),
                    "aligned_preview": aligned[: args.preview_steps].tolist(),
                    "cumulative_preview": np.cumsum(aligned)[: args.preview_steps].tolist(),
                }
            except ValueError as exc:
                payload["modes"][mode] = {"error": str(exc)}
        print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
