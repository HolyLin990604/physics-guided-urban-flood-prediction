from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from datasets.urbanflood24_lite_adapter import UrbanFlood24LiteProcessDataset, load_dataset_config


def summarize_sample(sample: dict) -> dict:
    result = {}
    for key, value in sample.items():
        if hasattr(value, "shape"):
            result[key] = {
                "shape": list(value.shape),
                "dtype": str(value.dtype),
            }
        else:
            result[key] = value
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Debug the UrbanFlood24 Lite dataset adapter.")
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("configs/urbanflood24_lite_adapter.json"),
        help="JSON config file for the dataset adapter.",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=None,
        help="Dataset root directory.",
    )
    parser.add_argument("--split", default=None, choices=("train", "test"))
    parser.add_argument("--input-steps", type=int, default=None)
    parser.add_argument("--pred-steps", type=int, default=None)
    parser.add_argument("--stride", type=int, default=None)
    parser.add_argument("--alignment-mode", default=None)
    parser.add_argument("--samples", type=int, default=2, help="Number of samples to print.")
    parser.add_argument("--debug", action="store_true", help="Enable adapter debug metadata.")
    args = parser.parse_args()

    config = load_dataset_config(args.config)
    if args.root is not None:
        config["dataset_root"] = str(args.root)
    if args.split is not None:
        config["split"] = args.split
    if args.input_steps is not None:
        config["input_steps"] = args.input_steps
    if args.pred_steps is not None:
        config["pred_steps"] = args.pred_steps
    if args.stride is not None:
        config["stride"] = args.stride
    if args.alignment_mode is not None:
        config["alignment_mode"] = args.alignment_mode
    if args.debug:
        config["debug"] = True

    dataset = UrbanFlood24LiteProcessDataset(
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
        return_numpy=True,
    )

    print("Dataset summary:")
    print(json.dumps(dataset.describe(), indent=2))
    print()

    num_samples = min(args.samples, len(dataset))
    picked_samples = []
    for idx in range(num_samples):
        sample = dataset[idx]
        picked_samples.append(sample)
        print(f"Sample {idx}:")
        print(json.dumps(summarize_sample(sample), indent=2))
        print()

    if picked_samples:
        batch = UrbanFlood24LiteProcessDataset.collate_numpy(picked_samples)
        print("Batched shapes:")
        batched_summary = summarize_sample(batch)
        print(json.dumps(batched_summary, indent=2))


if __name__ == "__main__":
    main()
