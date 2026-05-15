# Phase 25 Target-Wet Recall Consistency Implementation Note



## 1. Purpose



This note documents the first Phase 25 physics-consistency guided refinement implementation.



Phase 24 showed that high-risk scenarios are physically less consistent than reliable scenarios, especially through stronger false-dry behavior, wet-area contraction, peak-depth underprediction, connectivity loss, and volume under-response.



The first Phase 25 code intervention therefore targets the strongest Phase 24 failure signals:



- false-dry reduction

- wet-area contraction reduction



The implemented refinement is a configurable depth-field-compatible physics loss named `target_wet_recall_consistency`.



## 2. Files Changed



The implementation changed only:



- `utils/physics_losses.py`

- `configs/train_phase25_target_wet_recall_seed123_40e.json`



No model architecture file was modified.



No existing Phase 10 config was modified.



No existing Phase 10 output was modified.



## 3. Loss Definition



The new loss is enabled through the following config block:



&#x20;   "target_wet_recall_consistency": {

&#x20;     "enabled": true,

&#x20;     "weight": 0.02,

&#x20;     "threshold": 0.05,

&#x20;     "temperature": 0.02,

&#x20;     "eps": 1e-6

&#x20;   }



The implemented logic is:



&#x20;   target_wet = target > threshold

&#x20;   pred_wet_prob = sigmoid((prediction - threshold) / max(temperature, eps))

&#x20;   loss = sum(((1 - pred_wet_prob) ** 2) * target_wet) / clamp(sum(target_wet), min=eps)



The loss encourages predicted wet probability inside target-wet cells.



This directly targets missed wet cells, false-dry behavior, and wet-area contraction.



## 4. Physical Meaning



The physical meaning is:



- if the target field indicates inundation, the prediction should not collapse that cell into a dry or near-dry state

- the model should preserve target wet regions more reliably

- the model should reduce systematic shrinkage of inundated extent



This is a depth-field-compatible physical-consistency refinement. It does not require velocity, flux, boundary flow, or full shallow-water-equation residual information.



## 5. Relationship to Phase 24



Phase 24 found the following correlations with `risk_score`:



- false_dry_rate: 0.913

- wet_area_contraction: 0.862

- peak_depth_underprediction: 0.856

- connectivity_loss_indicator: 0.539



Because false-dry and wet-area contraction had the strongest physical-risk linkages, the first Phase 25 intervention focuses on target-wet recall.



This intervention is intentionally narrow and does not attempt to solve all physical-consistency issues at once.



## 6. Configuration



The first pilot config is:



- `configs/train_phase25_target_wet_recall_seed123_40e.json`



It was copied from:



- `configs/train_phase10_margin_aware_boundary_band_seed123_40e.json`



Only the following changes were made:



1. `output.root` was changed to `runs/phase25_target_wet_recall_seed123_40e`

2. the new `physics_losses.target_wet_recall_consistency` block was added



The following Phase 10 settings remain unchanged:



- `boundary_band_pixels = 1`

- `boundary_weight = 2.0`



## 7. Smoke Tests



The implementation passed the following smoke tests:



- syntax check for `utils/physics_losses.py`

- import check for `PhysicsLossController`

- config JSON load and key assertions

- synthetic tensor test for enabled loss

- synthetic tensor test for absent or disabled loss behavior

- finite loss and finite gradient check

- no-target-wet edge case with finite loss and gradients and zero target-wet recall loss

- config diff constraint check against Phase 10 seed123 config



## 8. Explicit Non-Actions



The following actions were not performed:



- no model retraining

- no evaluation

- no new predictions

- no architecture modification

- no Phase 10 config edits

- no Phase 10 output edits

- no boundary_weight tuning

- no boundary_band_pixels tuning

- no parameter sweep

- no traffic-impact modeling



## 9. Next Step



The next step is a single-seed pilot training run using:



- `configs/train_phase25_target_wet_recall_seed123_40e.json`



The pilot should be compared against the existing Phase 10 seed123 baseline:



- `runs/phase10_margin_aware_boundary_band_seed123_40e`



The key evaluation question is not only whether RMSE improves.



The key question is whether the new loss reduces physically meaningful failure modes, especially:



- false_dry_rate

- wet_area_contraction

- peak_depth_underprediction

- connectivity_loss_indicator

- relative_volume_bias



The candidate should not be promoted unless it improves or preserves these physical-consistency indicators without unacceptable degradation in standard predictive metrics.

