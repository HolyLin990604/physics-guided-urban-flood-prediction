from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List

import numpy as np


EXPECTED_STATIC_FILES = ("absolute_DEM.npy", "impervious.npy", "manhole.npy")


def inspect_split(root: Path, split: str) -> Dict[str, object]:
    split_dir = root / split
    flood_root = split_dir / "flood"
    geodata_root = split_dir / "geodata"

    summary: Dict[str, object] = {
        "split": split,
        "locations": [],
        "events_per_location": {},
        "flood_shapes": Counter(),
        "rainfall_shapes": Counter(),
        "static_shapes": Counter(),
        "sample_events": [],
    }

    for location_dir in sorted(path for path in flood_root.iterdir() if path.is_dir()):
        location = location_dir.name
        summary["locations"].append(location)
        events: List[str] = []

        for static_name in EXPECTED_STATIC_FILES:
            static_path = geodata_root / location / static_name
            static_arr = np.load(static_path)
            summary["static_shapes"][(location, static_name, tuple(static_arr.shape))] += 1

        for event_dir in sorted(path for path in location_dir.iterdir() if path.is_dir()):
            events.append(event_dir.name)
            flood = np.load(event_dir / "flood.npy")
            rainfall = np.load(event_dir / "rainfall.npy")
            summary["flood_shapes"][(location, tuple(flood.shape))] += 1
            summary["rainfall_shapes"][(location, tuple(rainfall.shape))] += 1

            if len(summary["sample_events"]) < 6:
                summary["sample_events"].append(
                    {
                        "location": location,
                        "event": event_dir.name,
                        "flood_shape": tuple(flood.shape),
                        "rainfall_shape": tuple(rainfall.shape),
                        "flood_min": float(flood.min()),
                        "flood_max": float(flood.max()),
                        "rainfall_min": float(rainfall.min()),
                        "rainfall_max": float(rainfall.max()),
                    }
                )

        summary["events_per_location"][location] = events

    return summary


def print_summary(summary: Dict[str, object]) -> None:
    print(f"Split: {summary['split']}")
    print(f"Locations: {', '.join(summary['locations'])}")
    print("Events per location:")
    for location, events in summary["events_per_location"].items():
        print(f"  - {location}: {len(events)} events")
        print(f"    {', '.join(events)}")

    print("Flood shapes:")
    for (location, shape), count in sorted(summary["flood_shapes"].items()):
        print(f"  - {location}: {shape} x{count}")

    print("Rainfall shapes:")
    for (location, shape), count in sorted(summary["rainfall_shapes"].items()):
        print(f"  - {location}: {shape} x{count}")

    print("Static geodata shapes:")
    for (location, name, shape), count in sorted(summary["static_shapes"].items()):
        print(f"  - {location}: {name} -> {shape} x{count}")

    print("Sample events:")
    for sample in summary["sample_events"]:
        print(
            "  - "
            f"{sample['location']}/{sample['event']}: "
            f"flood={sample['flood_shape']} "
            f"rainfall={sample['rainfall_shape']} "
            f"flood_range=[{sample['flood_min']:.4f}, {sample['flood_max']:.4f}] "
            f"rainfall_range=[{sample['rainfall_min']:.4f}, {sample['rainfall_max']:.4f}]"
        )


def print_temporal_note(root: Path) -> None:
    ratios = defaultdict(int)
    for split in ("train", "test"):
        flood_root = root / split / "flood"
        for location_dir in sorted(path for path in flood_root.iterdir() if path.is_dir()):
            for event_dir in sorted(path for path in location_dir.iterdir() if path.is_dir()):
                flood = np.load(event_dir / "flood.npy")
                rainfall = np.load(event_dir / "rainfall.npy")
                ratios[(int(flood.shape[0]), int(rainfall.shape[0]))] += 1

    print("Temporal alignment note:")
    print("  - Flood and rainfall raw lengths do not match, so rainfall-to-flood alignment is a modeling assumption.")
    for (flood_len, rainfall_len), count in sorted(ratios.items()):
        print(f"  - observed pair flood={flood_len}, rainfall={rainfall_len} x{count}")
    print("  - Available adapter modes: piecewise_constant, linear, mass_preserving, repeat_if_integer_ratio.")
    print("  - `mass_preserving` best preserves cumulative rainfall when raw rainfall is interpreted as amount per coarse time bin.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Inspect UrbanFlood24 Lite structure and shapes.")
    parser.add_argument(
        "--root",
        type=Path,
        default=Path("data/urbanflood24_lite"),
        help="Dataset root directory.",
    )
    args = parser.parse_args()

    root = args.root.expanduser().resolve()
    print(f"Inspecting dataset root: {root}")
    for split in ("train", "test"):
        print_summary(inspect_split(root, split))
        print()
    print_temporal_note(root)


if __name__ == "__main__":
    main()
