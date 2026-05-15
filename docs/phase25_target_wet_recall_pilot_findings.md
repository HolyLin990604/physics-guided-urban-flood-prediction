# Phase 25 Target-Wet Recall Pilot Findings



## 1. Phase Objective



Phase 25 moves the project from physical-consistency diagnosis to targeted physics-consistency guided surrogate refinement.



Phase 24 showed that high-risk cases are not only statistically worse, but physically less consistent. The strongest physical-risk linkages were associated with false-dry behavior, wet-area contraction, peak-depth underprediction, and connectivity loss.



The first Phase 25 intervention was therefore designed as a narrow, depth-field-compatible refinement targeting target-wet recall.



The purpose of this pilot was not to replace the current Phase 10 mainline immediately. The purpose was to test whether a small, interpretable physical-consistency loss can reduce the dominant false-dry and wet-area contraction failure modes without damaging standard predictive performance.



## 2. Implemented Refinement



The implemented Phase 25 loss is:



- target_wet_recall_consistency



The loss encourages predicted wet probability inside target-wet cells.



The implemented logic is:



    target_wet = target > threshold

    pred_wet_prob = sigmoid((prediction - threshold) / max(temperature, eps))

    loss = sum(((1 - pred_wet_prob) ** 2) * target_wet) / clamp(sum(target_wet), min=eps)



The first pilot configuration is:



- configs/train_phase25_target_wet_recall_seed123_40e.json



It was copied from:



- configs/train_phase10_margin_aware_boundary_band_seed123_40e.json



Only the following changes were made:



1. output.root was changed to runs/phase25_target_wet_recall_seed123_40e

2. physics_losses.target_wet_recall_consistency was added



The current Phase 10 boundary-band setting remained fixed:



- boundary_band_pixels = 1

- boundary_weight = 2.0



## 3. Explicit Non-Actions



This pilot did not perform the following actions:



- no model architecture modification

- no Phase 10 boundary_weight tuning

- no boundary_band_pixels tuning

- no Phase 10 config modification

- no uncontrolled hyperparameter sweep

- no full SWE/PINN residual

- no traffic-impact modeling

- no replacement of the current Phase 10 recommendation



This pilot adds one optional, config-gated, depth-field-compatible physical-consistency loss.



## 4. Training Run



The Phase 25 seed123 pilot was trained for 40 epochs using:



- configs/train_phase25_target_wet_recall_seed123_40e.json



The run directory is:



- runs/phase25_target_wet_recall_seed123_40e



The training process completed successfully.



The new target-wet recall loss was active during training, as shown by the logged metrics:



- train_target_wet_recall_consistency

- train_target_wet_recall_consistency_weighted

- val_target_wet_recall_consistency

- val_target_wet_recall_consistency_weighted



The validation target-wet recall consistency loss decreased strongly during training, indicating that the model learned the intended target-wet recall behavior.



At epoch 40, the key validation metrics were:



- val_rmse = 0.060679

- val_mae = 0.024091

- val_wet_dry_iou = 0.754339

- val_loss = 0.031009

- val_target_wet_recall_consistency = 0.066259

- val_physics_total = 0.017598



The 40-epoch training curve showed stable convergence and no obvious training collapse.



## 5. Standard Test Comparison



The Phase 25 seed123 pilot was evaluated on the test set and compared against the existing Phase 10 seed123 baseline.



### Phase 10 seed123 baseline



- RMSE = 0.061625

- MAE = 0.022525

- wet/dry IoU = 0.706808

- rollout stability = 0.982880

- step RMSE std = 0.017477



### Phase 25 target-wet recall seed123



- RMSE = 0.056730

- MAE = 0.021537

- wet/dry IoU = 0.780236

- rollout stability = 0.983274

- step RMSE std = 0.017054



### Standard metric deltas



Phase25 - Phase10:



- RMSE = -0.004895

- MAE = -0.000989

- wet/dry IoU = +0.073429

- rollout stability = +0.000394

- step RMSE std = -0.000423



The pilot passed the standard metric guardrail.



The new loss did not degrade standard predictive performance. Instead, it improved RMSE, MAE, wet/dry IoU, rollout stability, and step RMSE standard deviation for seed123.



## 6. Need for Aligned Physical Comparison



The first direct physical diagnostic comparison had unequal row counts:



- Phase 10 diagnostic rows = 114

- Phase 25 diagnostic rows = 152



Therefore, the raw warning-level means were useful for directional screening but not sufficient for a strict conclusion.



A separate aligned comparison was implemented to compare only common seed123 cases.



The aligned comparison script is:



- scripts/compare_phase25_target_wet_recall_aligned.py



The aligned comparison output directory is:



- analysis/phase25_target_wet_recall_comparison/aligned_comparison



The aligned comparison used:



- common aligned rows = 38

- alignment key = scenario_key

- run_name was not used as an alignment key



Run name was used only as a subset filter because the diagnostic CSVs aggregate multiple runs.



## 7. Aligned Physical-Consistency Comparison



The aligned common-case comparison showed that Phase 25 improved the intended physical-consistency targets.



Overall Phase25 - Phase10 deltas were:



- RMSE = -0.004910

- MAE = -0.000977

- relative_volume_bias = +0.094689

- wet_area_contraction = -0.081389

- peak_depth_underprediction = +0.002614

- false_dry_rate = -0.113020

- false_wet_rate = +0.005015

- connectivity_loss_indicator = +0.078947

- largest_component_ratio_change = -0.008463



The main intended improvements were achieved:



- false_dry_rate decreased

- wet_area_contraction decreased

- relative_volume_bias became less negative

- RMSE and MAE decreased



This means the target-wet recall loss successfully addressed the Phase 24 diagnosis of missed wet cells and wet-area contraction in the aligned seed123 pilot comparison.



## 8. Warning-Level Aligned Results



The aligned comparison also showed that the improvement was strongest in the more difficult warning categories.



### Reliable cases



n = 25



Phase25 - Phase10:



- false_dry_rate = -0.077387

- wet_area_contraction = -0.041093

- RMSE = -0.005055



Reliable cases improved, but the improvement was moderate because the baseline was already relatively stable in these cases.



### Caution cases



n = 9



Phase25 - Phase10:



- false_dry_rate = -0.172053

- wet_area_contraction = -0.119893

- RMSE = -0.004106



Caution cases showed stronger improvement than reliable cases, especially in false-dry reduction and wet-area contraction reduction.



### High-risk cases



n = 4



Phase25 - Phase10:



- false_dry_rate = -0.202895

- wet_area_contraction = -0.246607

- RMSE = -0.005808



High-risk cases showed the strongest physical-consistency improvement.



This is important because Phase 24 identified high-risk cases as physically less consistent, especially through missed wet extent, wet-area contraction, and volume under-response.



## 9. Interpretation



The Phase 25 target-wet recall loss directly improved the two most important intended physical failure modes:



- false-dry behavior

- wet-area contraction



It also improved standard predictive metrics, including RMSE, MAE, and wet/dry IoU.



The pilot result therefore supports the interpretation that target-wet recall consistency is a meaningful depth-field-compatible physical refinement.



The improvement is not merely a metric artifact. It aligns with the Phase 24 physical-consistency diagnosis.



## 10. Guardrail Observations



The result is strongly positive, but not complete.



The pilot did not clearly improve all physical-consistency indicators.



### Peak-depth underprediction



Overall delta:



- peak_depth_underprediction = +0.002614



This is effectively near-neutral but slightly worse in the aligned comparison.



This is acceptable for the first Phase 25 intervention because the target-wet recall loss was not designed to explicitly preserve local peak depths.



### Connectivity loss



Overall delta:



- connectivity_loss_indicator = +0.078947



This suggests that the current loss improves wet recall and wet-area extent but does not solve wet-connectivity preservation.



This result is important for later refinement. A future Phase 25 extension or Phase 26-style intervention may need a separate connectivity-aware or structure-aware term.



### False-wet rate



Overall delta:



- false_wet_rate = +0.005015



This slight increase is also expected. Improving wet recall can sometimes increase false-wet behavior. The magnitude is small, but it should be monitored in future seeds.



## 11. Current Phase 25 Judgment



The Phase 25 seed123 target-wet recall pilot should be classified as:



- strong positive pilot candidate



It should not yet be classified as:



- new recommended mainline



Reason:



- only seed123 has been tested

- seed42 and seed202 guardrails are still required

- connectivity loss did not improve

- peak-depth underprediction was not meaningfully improved

- the current intervention specifically addresses target-wet recall, not all physical-consistency dimensions



The correct interpretation is:



- Phase 25 target-wet recall is a promising targeted refinement

- it directly improves false-dry and wet-area contraction behavior

- it preserves and improves standard test metrics on seed123

- it requires cross-seed guardrail validation before any mainline recommendation



## 12. Next Step



The next step should not be a broad sweep.



The next step should be guardrail validation on additional seeds.



Recommended next runs:



1. create Phase 25 target-wet recall config for seed42

2. train seed42 with the same settings

3. evaluate seed42 on test

4. run aligned Phase 10 vs Phase 25 physical comparison for seed42

5. repeat for seed202 only if seed42 does not reveal a serious guardrail failure



The Phase 25 target-wet recall setting should remain unchanged for these guardrail runs:



- target_wet_recall_consistency.weight = 0.02

- threshold = 0.05

- temperature = 0.02

- boundary_band_pixels = 1

- boundary_weight = 2.0



No new loss weight tuning should be started until seed42 and seed202 guardrails are understood.



## 13. Phase 25 Pilot Conclusion



The Phase 25 seed123 pilot provides strong initial evidence that a small, depth-field-compatible target-wet recall loss can improve both standard prediction metrics and key physical-consistency failure modes.



Most importantly, it reduces false-dry behavior and wet-area contraction, with the strongest improvement appearing in high-risk cases.



This result supports continuing Phase 25 with controlled cross-seed guardrail validation.



However, this pilot should remain a candidate result rather than a new mainline recommendation until additional seeds confirm that the improvement is robust and does not introduce new failure modes.

