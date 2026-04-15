import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# 固定比较对象：同一样本、同一步
step = 11

baseline_path = Path(r"runs\phase2_loss_only_40e_seed42\evaluation_test\test_batch_0000\forecast_maps.npz")
phase1_path = Path(r"runs\phase2b_temporal_gate_h16_40e_seed42\evaluation_test\test_batch_0000\forecast_maps.npz")
out_path = Path(r"runs\comparison_maps_seed42_test_batch0000.png")

b = np.load(baseline_path)
p = np.load(phase1_path)

target = b["target"][0, step, 0]
baseline_pred = b["prediction"][0, step, 0]
phase1_pred = p["prediction"][0, step, 0]
baseline_err = np.abs(baseline_pred - target)
phase1_err = np.abs(phase1_pred - target)

# 统一色标：前三张共用一个，后两张误差图共用一个
main_vmin = min(target.min(), baseline_pred.min(), phase1_pred.min())
main_vmax = max(target.max(), baseline_pred.max(), phase1_pred.max())

err_vmin = 0.0
err_vmax = max(baseline_err.max(), phase1_err.max())

fig, axes = plt.subplots(1, 5, figsize=(20, 4))

# 前三张：统一主色标
for ax, img, title in zip(
    axes[:3],
    [target, baseline_pred, phase1_pred],
    ["Target", "Phase 2A", "Phase 2B h16"]
):
    im = ax.imshow(img, cmap="viridis", vmin=main_vmin, vmax=main_vmax)
    ax.set_title(title)
    ax.axis("off")
    plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)

# 后两张：统一误差色标
for ax, img, title in zip(
    axes[3:],
    [baseline_err, phase1_err],
    ["Phase 2A Error", "Phase 2B h16 Error"]
):
    im = ax.imshow(img, cmap="viridis", vmin=err_vmin, vmax=err_vmax)
    ax.set_title(title)
    ax.axis("off")
    plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)

plt.suptitle(f"Spatial comparison: Phase 2A vs Phase 2B h16 (seed42, test batch 0000, step {step})")
plt.tight_layout()
plt.savefig(out_path, dpi=300, bbox_inches="tight")
print(f"Saved to: {out_path}")
plt.show()