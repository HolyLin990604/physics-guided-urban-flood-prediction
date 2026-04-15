import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

r0, r1, c0, c1 = 40, 88, 40, 88

baseline_path = Path(r"runs\phase2_loss_only_40e_seed202\evaluation_test\test_batch_0000\forecast_maps.npz")
phase1_path = Path(r"runs\phase2b_temporal_gate_h16_40e_seed202\evaluation_test\test_batch_0000\forecast_maps.npz")
out_path = Path(r"runs\comparison_timeseries_seed202_test_batch0000.png")

b = np.load(baseline_path)
p = np.load(phase1_path)

target = b["target"][0, :, 0, r0:r1, c0:c1].mean(axis=(1, 2))
baseline = b["prediction"][0, :, 0, r0:r1, c0:c1].mean(axis=(1, 2))
phase1 = p["prediction"][0, :, 0, r0:r1, c0:c1].mean(axis=(1, 2))

steps = np.arange(1, len(target) + 1)

plt.figure(figsize=(8, 5))
plt.plot(steps, target, marker="o", label="Target")
plt.plot(steps, baseline, marker="s", label="Phase 2A")
plt.plot(steps, phase1, marker="^",label="Phase 2B h16")
plt.xlabel("Forecast step")
plt.ylabel("Region-averaged water depth")
plt.title("Region-averaged process comparison: Phase 2A vs Phase 2B h16 (seed202, test batch 0000)")
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(out_path, dpi=300, bbox_inches="tight")
print(f"Saved to: {out_path}")
plt.show()