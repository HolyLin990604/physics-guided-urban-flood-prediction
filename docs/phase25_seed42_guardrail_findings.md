# Phase 25 Seed42 Target-Wet Recall Guardrail Findings



## 1. Purpose



This document summarizes the Phase 25 seed42 guardrail validation for the target-wet recall consistency refinement.



The Phase 25 target-wet recall loss was first tested on seed123 and showed strong positive pilot behavior. The purpose of the seed42 run was not to tune the loss or start a sweep. The purpose was to test whether the same configuration remains stable and beneficial under another seed.



## 2. Configuration



The seed42 Phase 25 configuration is:



- configs/train_phase25_target_wet_recall_seed42_40e.json



It was copied from:



- configs/train_phase10_margin_aware_boundary_band_seed42_40e.json



Only the following changes were made:



1. output.root was changed to runs/phase25_target_wet_recall_seed42_40e

2. physics_losses.target_wet_recall_consistency was added



The target-wet recall block remained unchanged from the seed123 pilot:



- enabled = true

- weight = 0.02

- threshold = 0.05

- temperature = 0.02

- eps = 1e-6



The Phase 10 boundary-band setting remained fixed:



- boundary_band_pixels = 1

- boundary_weight = 2.0



## 3. Explicit Non-Actions



This guardrail validation did not perform the following actions:



- no model architecture modification

- no Phase 10 boundary_weight tuning

- no boundary_band_pixels tuning

- no new loss-weight sweep

- no full SWE/PINN residual

- no traffic-impact modeling

- no replacement of the current Phase 10 recommendation



## 4. Training Behavior



The seed42 Phase 25 run completed 40 epochs successfully.



The training process showed stable convergence. The new target-wet recall consistency term was active during training, as indicated by the logged metrics:



- train_target_wet_recall_consistency

- train_target_wet_recall_consistency_weighted

- val_target_wet_recall_consistency

- val_target_wet_recall_consistency_weighted



At epoch 40, the key validation metrics were:



- val_rmse = 0.049198

- val_mae = 0.017605

- val_wet_dry_iou = 0.760256

- val_loss = 0.021585

- val_target_wet_recall_consistency = 0.082652

- val_physics_total = 0.012919



The seed42 training run did not show collapse or obvious instability.



## 5. Standard Test Comparison



The Phase 25 seed42 run was evaluated against the existing Phase 10 seed42 baseline.



### Phase 10 seed42 baseline



- RMSE = 0.058588

- MAE = 0.021415

- wet/dry IoU = 0.682114

- rollout stability = 0.987815

- step RMSE std = 0.012386



### Phase 25 target-wet recall seed42



- RMSE = 0.044747

- MAE = 0.017939

- wet/dry IoU = 0.803878

- rollout stability = 0.989504

- step RMSE std = 0.010654



### Standard metric deltas



Phase25 - Phase10:



- RMSE = -0.013841

- MAE = -0.003476

- wet/dry IoU = +0.121764

- rollout stability = +0.001689

- step RMSE std = -0.001733



The seed42 run clearly passed the standard test guardrail.



Compared with the Phase 10 seed42 baseline, Phase 25 improved RMSE, MAE, wet/dry IoU, rollout stability, and step RMSE standard deviation.



## 6. Need for Aligned Physical Comparison



The Phase 24-style physical diagnostic row counts were not directly aligned:



- Phase 10 seed42 diagnostic rows = 114

- Phase 25 seed42 diagnostic rows = 152



Therefore, as in the seed123 pilot, a common-case aligned comparison was required.



The aligned comparison was generated using:



- scripts/compare_phase25_target_wet_recall_aligned.py



The seed42 aligned output directory is:



- analysis/phase25_target_wet_recall_comparison/aligned_comparison_seed42



The aligned comparison used:



- common aligned rows = 38

- alignment key = scenario_key

- Phase10-only rows = 0

- Phase25-only rows = 0



The run name was not used as an alignment key. It was only used as a subset filter because the diagnostic CSVs aggregate multiple runs.



## 7. Aligned Physical-Consistency Comparison



The aligned common-case comparison showed that Phase 25 improved the intended physical-consistency targets on seed42.



Overall Phase25 - Phase10 deltas were:



- RMSE = -0.014146

- MAE = -0.004074

- relative_volume_bias = +0.157211

- wet_area_contraction = -0.106194

- peak_depth_underprediction = -0.037269

- false_dry_rate = -0.152555

- false_wet_rate = +0.002350

- connectivity_loss_indicator = +0.157895

- largest_component_ratio_change = -0.005106



The main intended improvements were achieved:



- false_dry_rate decreased

- wet_area_contraction decreased

- relative_volume_bias became less negative

- peak_depth_underprediction decreased

- RMSE and MAE decreased



This confirms that the target-wet recall loss improved the core Phase 24 physical failure modes on seed42, especially false-dry behavior and wet-area contraction.



## 8. Warning-Level Aligned Results



The seed42 aligned comparison showed that the improvement was strongest in caution and high-risk cases.



### Reliable cases



n = 23



Phase25 - Phase10:



- false_dry_rate = -0.092404

- wet_area_contraction = -0.046514

- RMSE = -0.014182

- MAE = -0.004374



### Caution cases



n = 10



Phase25 - Phase10:



- false_dry_rate = -0.236374

- wet_area_contraction = -0.151644

- RMSE = -0.013826

- MAE = -0.003146



### High-risk cases



n = 5



Phase25 - Phase10:



- false_dry_rate = -0.261612

- wet_area_contraction = -0.289823

- RMSE = -0.014619

- MAE = -0.004548



The high-risk group showed the strongest physical-consistency improvement. This is important because Phase 24 identified high-risk cases as physically less consistent and dominated by false-dry behavior, wet-area contraction, and volume under-response.



## 9. Interpretation



Seed42 confirms that the Phase 25 target-wet recall loss is not a one-seed artifact.



The result is stronger than a simple no-harm guardrail. It shows clear improvements in:



- standard test accuracy

- wet/dry classification

- false-dry reduction

- wet-area contraction reduction

- relative volume response

- peak-depth underprediction



The seed42 result therefore supports upgrading Phase 25 from a seed123-only promising pilot to a two-seed positive candidate with guardrail support.



## 10. Remaining Boundary



The main remaining caution is wet-connectivity preservation.



The aligned comparison shows:



- connectivity_loss_indicator = +0.157895



This means that the target-wet recall loss improves wet recall and wet-area extent, but it does not solve wet-region structural connectivity. The result remains consistent with the seed123 finding: target-wet recall is effective for missed wet cells and wet-area contraction, but connectivity requires a separate future design.



False-wet behavior also increased slightly:



- false_wet_rate = +0.002350



This is small, but it should continue to be monitored because improving wet recall can increase false-wet tendency.



## 11. Current Phase 25 Judgment



After seed123 and seed42, the current Phase 25 judgment is:



- two-seed positive candidate with guardrail support



It should not yet be classified as:



- final recommended mainline



Reason:



- seed202 confirmation is still required

- connectivity loss has not improved

- the current intervention targets target-wet recall, not all physical-consistency dimensions

- no broader multi-seed synthesis has been written yet



## 12. Next Step



The next step should be seed202 confirmation using the same target-wet recall configuration.



The seed202 configuration should be created by copying:



- configs/train_phase10_margin_aware_boundary_band_seed202_40e.json



to:



- configs/train_phase25_target_wet_recall_seed202_40e.json



Only the following changes should be made:



1. output.root should be changed to runs/phase25_target_wet_recall_seed202_40e

2. physics_losses.target_wet_recall_consistency should be added



The following should remain unchanged:



- seed = 202

- epochs = 40

- boundary_band_pixels = 1

- boundary_weight = 2.0

- target_wet_recall_consistency.weight = 0.02

- threshold = 0.05

- temperature = 0.02



No new tuning should be performed before seed202 is evaluated.



## 13. Conclusion



The Phase 25 seed42 guardrail result is strongly positive.



It confirms that the target-wet recall consistency refinement improves both standard predictive metrics and the intended physical-consistency failure modes in a second seed.



Most importantly, it again reduces false-dry behavior and wet-area contraction, with the strongest improvements appearing in high-risk cases.



This supports continuing Phase 25 to seed202 final confirmation before making any mainline recommendation.

