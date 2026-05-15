# Phase 25 Three-Seed Target-Wet Recall Synthesis Findings



## 1. Purpose



This document synthesizes the three-seed Phase 25 target-wet recall consistency refinement results.



Phase 25 was designed after Phase 24 physical-consistency diagnosis showed that high-risk cases were not only statistically worse, but also physically less consistent. The dominant physical failure modes were:



- false-dry behavior

- wet-area contraction

- relative volume under-response

- peak-depth underprediction

- wet-connectivity degradation



The first Phase 25 intervention added a narrow, depth-field-compatible loss:



- target_wet_recall_consistency



The goal was not to implement a full shallow-water-equation residual or a PINN formulation. The goal was to test whether a small, interpretable, config-gated physical-consistency term could reduce missed wet cells and wet-area contraction without damaging standard predictive performance.



## 2. Implemented Refinement



The target-wet recall consistency loss encourages predicted wet probability inside target-wet cells.



The implemented logic is:



    target_wet = target > threshold

    pred_wet_prob = sigmoid((prediction - threshold) / max(temperature, eps))

    loss = sum(((1 - pred_wet_prob) ** 2) * target_wet) / clamp(sum(target_wet), min=eps)



The configuration block was:



    target_wet_recall_consistency:

      enabled: true

      weight: 0.02

      threshold: 0.05

      temperature: 0.02

      eps: 1e-6



The same target-wet recall setting was tested on:



- seed123

- seed42

- seed202



The Phase 10 boundary-band setting remained fixed in all Phase 25 runs:



- boundary_band_pixels = 1

- boundary_weight = 2.0



No additional tuning was performed between seeds.



## 3. Explicit Non-Actions



Phase 25 did not perform the following actions:



- no model architecture modification

- no Phase 10 boundary_weight tuning

- no boundary_band_pixels tuning

- no uncontrolled hyperparameter sweep

- no full SWE/PINN residual

- no traffic-impact modeling

- no replacement of the Phase 10 baseline before evidence was collected



The Phase 25 intervention was intentionally narrow and targeted.



## 4. Completed Runs and Outputs



The completed Phase 25 target-wet recall configs are:



- configs/train_phase25_target_wet_recall_seed123_40e.json

- configs/train_phase25_target_wet_recall_seed42_40e.json

- configs/train_phase25_target_wet_recall_seed202_40e.json



The corresponding run directories are:



- runs/phase25_target_wet_recall_seed123_40e

- runs/phase25_target_wet_recall_seed42_40e

- runs/phase25_target_wet_recall_seed202_40e



The aligned comparison outputs are stored under:



- analysis/phase25_target_wet_recall_comparison/aligned_comparison

- analysis/phase25_target_wet_recall_comparison/aligned_comparison_seed42

- analysis/phase25_target_wet_recall_comparison/aligned_comparison_seed202



The physical diagnostic outputs are stored under:



- analysis/phase25_target_wet_recall_comparison/phase10_seed123_physical

- analysis/phase25_target_wet_recall_comparison/phase25_seed123_physical

- analysis/phase25_target_wet_recall_comparison/phase10_seed42_physical

- analysis/phase25_target_wet_recall_comparison/phase25_seed42_physical

- analysis/phase25_target_wet_recall_comparison/phase10_seed202_physical

- analysis/phase25_target_wet_recall_comparison/phase25_seed202_physical



## 5. Standard Test Metric Summary



Across all three seeds, Phase 25 improved the standard test metrics relative to the Phase 10 seed-matched baseline.



### Seed123



Phase25 - Phase10:



- RMSE = -0.004895

- MAE = -0.000989

- wet/dry IoU = +0.073429

- rollout stability = +0.000394

- step RMSE std = -0.000423



### Seed42



Phase25 - Phase10:



- RMSE = -0.013841

- MAE = -0.003476

- wet/dry IoU = +0.121764

- rollout stability = +0.001689

- step RMSE std = -0.001733



### Seed202



Phase25 - Phase10:



- RMSE = -0.002434

- MAE = -0.000092

- wet/dry IoU = +0.034817

- rollout stability = +0.001022

- step RMSE std = -0.001058



## 6. Three-Seed Standard Metric Interpretation



The standard test results show consistent improvement across all three seeds.



The mean Phase25 - Phase10 standard test deltas across the three seeds were approximately:



- RMSE = -0.007057

- MAE = -0.001519

- wet/dry IoU = +0.076670

- rollout stability = +0.001035

- step RMSE std = -0.001071



This means Phase 25 did not trade standard accuracy for physical-consistency behavior.



Instead, the target-wet recall loss improved:



- depth prediction accuracy

- absolute error

- wet/dry classification

- rollout stability

- timestep-wise stability



This is important because the first concern for any new physics-consistency loss is whether it harms ordinary predictive performance. Across the three tested seeds, no such standard-metric guardrail failure was observed.



## 7. Aligned Physical-Consistency Comparison



The first physical diagnostic outputs had unequal raw row counts:



- Phase 10 diagnostics generally produced 114 scenario rows

- Phase 25 diagnostics generally produced 152 scenario rows



Therefore, raw warning-level means were not used as final evidence.



For each seed, a common-case aligned comparison was performed.



Each aligned comparison used:



- common aligned rows = 38

- alignment key = scenario_key

- run_name was not used as an alignment key



Run name was used only as a subset filter to separate the aggregated diagnostic CSVs before alignment.



## 8. Seed123 Aligned Physical Results



Seed123 overall Phase25 - Phase10 aligned deltas:



- RMSE = -0.004910

- MAE = -0.000977

- relative_volume_bias = +0.094689

- wet_area_contraction = -0.081389

- peak_depth_underprediction = +0.002614

- false_dry_rate = -0.113020

- false_wet_rate = +0.005015

- connectivity_loss_indicator = +0.078947

- largest_component_ratio_change = -0.008463



Seed123 interpretation:



- false_dry_rate improved

- wet_area_contraction improved

- relative_volume_bias became less negative

- RMSE and MAE improved

- peak_depth_underprediction was essentially neutral but slightly worse

- connectivity_loss_indicator worsened



Seed123 was therefore classified as a strong positive pilot candidate, but not a complete physical-consistency solution.



## 9. Seed42 Aligned Physical Results



Seed42 overall Phase25 - Phase10 aligned deltas:



- RMSE = -0.014146

- MAE = -0.004074

- relative_volume_bias = +0.157211

- wet_area_contraction = -0.106194

- peak_depth_underprediction = -0.037269

- false_dry_rate = -0.152555

- false_wet_rate = +0.002350

- connectivity_loss_indicator = +0.157895

- largest_component_ratio_change = -0.005106



Seed42 interpretation:



- false_dry_rate improved strongly

- wet_area_contraction improved strongly

- relative_volume_bias became less negative

- peak_depth_underprediction improved

- RMSE and MAE improved strongly

- connectivity_loss_indicator worsened



Seed42 confirmed that the seed123 result was not a one-seed artifact.



## 10. Seed202 Aligned Physical Results



Seed202 overall Phase25 - Phase10 aligned deltas:



- RMSE = -0.002675

- MAE = -0.000603

- relative_volume_bias = +0.063380

- wet_area_contraction = -0.049730

- peak_depth_underprediction = -0.010232

- false_dry_rate = -0.068388

- false_wet_rate = +0.004168

- connectivity_loss_indicator = 0.000000

- largest_component_ratio_change = +0.007845



Seed202 interpretation:



- false_dry_rate improved

- wet_area_contraction improved

- relative_volume_bias became less negative

- peak_depth_underprediction improved

- RMSE and MAE improved

- connectivity_loss_indicator was neutral overall

- false_wet_rate increased slightly



Seed202 confirmed that the target-wet recall benefit persisted in the third seed.



## 11. Three-Seed Physical Metric Synthesis



Across seed123, seed42, and seed202, the aligned comparisons showed consistent improvement in the two intended physical-consistency targets:



- false_dry_rate decreased in all three seeds

- wet_area_contraction decreased in all three seeds



The mean aligned deltas across the three seeds were approximately:



- false_dry_rate = -0.111321

- wet_area_contraction = -0.079104

- relative_volume_bias = +0.105093

- peak_depth_underprediction = -0.014962

- RMSE = -0.007244

- MAE = -0.001885

- false_wet_rate = +0.003844

- connectivity_loss_indicator = +0.078947



The strongest and most stable improvements were:



- false-dry reduction

- wet-area contraction reduction

- volume under-response mitigation

- standard RMSE and MAE improvement



The less stable or non-primary effects were:



- false_wet_rate increased slightly in all seeds

- connectivity_loss_indicator was not consistently improved

- peak_depth_underprediction improved in seed42 and seed202 but was nearly neutral/slightly worse in seed123



## 12. Warning-Level Interpretation



The warning-level aligned comparisons showed that the high-risk cases benefited strongly.



### Seed123 high-risk cases



n = 4



Phase25 - Phase10:



- false_dry_rate = -0.202895

- wet_area_contraction = -0.246607

- RMSE = -0.005808



### Seed42 high-risk cases



n = 5



Phase25 - Phase10:



- false_dry_rate = -0.261612

- wet_area_contraction = -0.289823

- RMSE = -0.014619

- MAE = -0.004548



### Seed202 high-risk cases



n = 4



Phase25 - Phase10:



- false_dry_rate = -0.124321

- wet_area_contraction = -0.158422

- peak_depth_underprediction = -0.075531

- connectivity_loss_indicator = -0.250000

- RMSE = -0.004355

- MAE = -0.000929



The high-risk results are important because Phase 24 identified high-risk cases as physically less consistent and dominated by missed wet extent, wet-area contraction, volume under-response, and local peak-depth underprediction.



The Phase 25 target-wet recall loss consistently reduced the missed-wet and wet-area contraction components in these difficult cases.



## 13. Main Scientific Interpretation



The Phase 25 target-wet recall consistency loss directly addresses a physically meaningful failure mode:



- target-wet cells should not be predicted as dry or near-dry



The three-seed results show that this design is effective.



The improvement is not merely a statistical artifact because the aligned physical metrics show consistent reductions in:



- false_dry_rate

- wet_area_contraction



At the same time, the standard test metrics also improve.



This means the new loss improves both:



- predictive accuracy

- physically interpretable wet-region preservation



The result supports the value of targeted, diagnosis-driven physical-consistency refinement.



## 14. Relationship to Phase 24



Phase 24 diagnosed that high-risk cases were physically less consistent, with stronger:



- false-dry behavior

- wet-area contraction

- peak-depth underprediction

- connectivity loss

- volume under-response



Phase 25 took this diagnosis and implemented a narrow intervention aimed at the most actionable depth-field-compatible components:



- false-dry reduction

- wet-area contraction reduction



The three-seed evidence confirms that the intervention successfully reduces these two components.



Therefore, Phase 25 represents a transition from:



- physical-consistency diagnosis



to:



- physical-consistency guided model refinement



This is a meaningful step toward a trustworthy, interpretable, physically consistent urban flood surrogate.



## 15. Remaining Limitations



Phase 25 should not be overclaimed.



The target-wet recall loss does not solve all physical-consistency problems.



The main remaining limitations are:



1. Connectivity is not consistently improved.



The connectivity_loss_indicator worsened in seed123 and seed42, and was neutral overall in seed202. Therefore, Phase 25 should not be described as a connectivity-preserving loss.



2. False-wet rate increases slightly.



The false_wet_rate increased slightly in all three aligned comparisons. This is expected because improving wet recall can introduce more false wet predictions. The magnitude is small, but it should be monitored.



3. Peak-depth preservation is only partially improved.



Peak-depth underprediction improved in seed42 and seed202 but was near-neutral/slightly worse in seed123. Therefore, peak-depth preservation may require a separate targeted refinement.



4. Topographic consistency remains unavailable.



Topographic consistency was still skipped because no shape-compatible DEM/static elevation layer was found.



5. The intervention remains depth-field-compatible rather than full hydrodynamic.



The current loss does not use velocity, flux, boundary flow, pump-gate operation, or source-sink terms. It should not be described as a full shallow-water-equation residual.



## 16. Current Phase 25 Judgment



The correct current judgment is:



- Phase 25 target-wet recall is a three-seed positive candidate with consistent target-wet recall benefit.



It can also be described as:



- a credible targeted refinement over the Phase 10 baseline for reducing false-dry behavior and wet-area contraction.



It should not be described as:



- a complete physical-consistency solution

- a full hydrodynamic constraint

- a final replacement of all future physical refinement needs



The current Phase 10 recommended setting remains the baseline reference:



- boundary_band_pixels = 1

- boundary_weight = 2.0



The Phase 25 target-wet recall setting is now a strong candidate refinement that should be documented and considered for mainline promotion after project-level synchronization.



## 17. Mainline Recommendation Status



Based on the three-seed evidence, Phase 25 target-wet recall is stronger than a pilot-only result.



It has passed:



- seed123 standard metric test and aligned physical comparison

- seed42 standard metric test and aligned physical comparison

- seed202 standard metric test and aligned physical comparison



The evidence supports promoting it from pilot candidate to strong three-seed candidate.



However, before formally calling it the new recommended mainline, the project should complete:



1. Phase 25 project-level documentation synchronization

2. README/project_status/experiment_index updates

3. clear statement of remaining limitations

4. final branch clean check

5. merge into main only after documentation is coherent



## 18. Next Step



The next step is not additional tuning.



The next step should be Phase 25 consolidation:



1. commit this three-seed synthesis findings document

2. update README.md

3. update docs/project_status.md

4. update docs/experiment_index.md

5. optionally show representative Phase 25 comparison figures in README

6. avoid committing runs/checkpoints

7. merge Phase 25 into main only after the documentation is synchronized and the branch is clean



No further loss-weight sweep is justified at this point.



Future work after Phase 25 may consider a separate connectivity-aware or peak-depth-preservation refinement, but that should be treated as a later targeted stage rather than expanding Phase 25 into an uncontrolled sweep.



## 19. Conclusion



Phase 25 successfully converts the Phase 24 physical-consistency diagnosis into a targeted model refinement.



Across seed123, seed42, and seed202, the target-wet recall consistency loss consistently improves false-dry behavior and wet-area contraction while also improving standard test metrics.



The strongest conclusion is:



- Phase 25 target-wet recall is a strong three-seed positive candidate for improving wet-region preservation and reducing missed inundation.



The appropriate boundary is:



- it is not a complete physical-consistency solution and does not consistently solve wet-connectivity preservation.



This result moves the project closer to the long-term goal of a trustworthy, interpretable, physically consistent, and operationally useful deep-learning surrogate for rapid urban flood warning.

