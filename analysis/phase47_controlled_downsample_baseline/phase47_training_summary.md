# Phase 47 Controlled Downsample Baseline Training Summary

- selected_decision: `phase47_controlled_128_downsample_seed42_pilot_completed`
- phase: `47`
- seed: `42`
- resolution: `128`
- epochs: `10`
- train_samples: `960`
- test_samples: `384`
- best_test_rmse: `0.01109213042097205`
- no_swe_pinn: `true`
- level5_supported: `false`
- training_command: `python scripts/train_phase47_full_downsample_baseline.py --config configs/train_phase47_full_downsample128_seed42_10e.json`

This run used the existing U-Net + TCN supervised model family with script-local adapter plumbing for Phase 45 indexed full-dataset input compatibility.