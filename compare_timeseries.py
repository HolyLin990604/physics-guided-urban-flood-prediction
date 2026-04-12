import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

r0, r1, c0, c1 = 40, 88, 40, 88

baseline_path = Path(r"runs\baseline_20epoch\visualizations\epoch_019\val_batch_0000\forecast_maps.npz")
phase1_path = Path(r"runs\stage2b_phase1_20epoch\visualizations\epoch_019\val_batch_0000\forecast_maps.npz")
out_path = Path(r"runs\comparison_timeseries_epoch19_regionavg.png")

b = np.load(baseline_path)
p = np.load(phase1_path)

target = b["target"][0, :, 0, r0:r1, c0:c1].mean(axis=(1, 2))
baseline = b["prediction"][0, :, 0, r0:r1, c0:c1].mean(axis=(1, 2))
phase1 = p["prediction"][0, :, 0, r0:r1, c0:c1].mean(axis=(1, 2))

steps = np.arange(1, len(target) + 1)

plt.figure(figsize=(8, 5))
plt.plot(steps, target, marker="o", label="Target")
plt.plot(steps, baseline, marker="s", label="Baseline")
plt.plot(steps, phase1, marker="^", label="Phase 1")
plt.xlabel("Forecast step")
plt.ylabel("Region-averaged water depth")
plt.title("Region-averaged process comparison")
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(out_path, dpi=300, bbox_inches="tight")
print(f"Saved to: {out_path}")
plt.show()