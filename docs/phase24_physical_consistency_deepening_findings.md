# Phase 24 Physical Consistency Deepening and Process Diagnostics Findings



## 1. Phase Objective



Phase 24 deepened the project from reliability-aware warning case demonstration toward process-level physical consistency diagnosis.



The purpose of this phase was not to improve the model by retraining, architecture modification, or parameter tuning. Instead, Phase 24 examined whether the existing Phase 10 recommended surrogate outputs behave consistently with physically plausible flood-process behavior.



The main diagnostic focus was:



- rainfall-volume response consistency

- peak-depth preservation and underprediction

- wet-area contraction

- wet-area connectivity and fragmentation

- temporal process behavior

- linkage between physical-consistency metrics and Phase 15/16 warning-risk labels

- physical interpretation of the Phase 23 representative cases



## 2. Inputs Reused



Phase 24 reused existing artifacts from previous phases.



The main sources were:



- Phase 10 forecast map artifacts under `runs/phase10_margin_aware_boundary_band_seed*_40e/evaluation_test`

- Phase 15 reliability-screening outputs

- Phase 16 warning-rule outputs

- Phase 23 selected case information



The script discovered and loaded:



- 57 existing map artifacts

- 114 scenario-level records

- 1368 timestep-level records

- 3 Phase 23 selected cases



No new model predictions were generated.



## 3. Generated Outputs



The main analysis script added in this phase is:



- `scripts/analyze_phase24_physical_consistency.py`



The generated output directory is:



- `analysis/phase24_physical_consistency/`



The main output files are:



- `analysis/phase24_physical_consistency/summary.json`

- `analysis/phase24_physical_consistency/scenario_physical_consistency_metrics.csv`

- `analysis/phase24_physical_consistency/volume_response_metrics.csv`

- `analysis/phase24_physical_consistency/peak_depth_consistency.csv`

- `analysis/phase24_physical_consistency/wet_connectivity_metrics.csv`

- `analysis/phase24_physical_consistency/temporal_consistency_metrics.csv`

- `analysis/phase24_physical_consistency/physics_risk_linkage.csv`

- `analysis/phase24_physical_consistency/topographic_consistency.csv`



The generated figures are:



- `analysis/phase24_physical_consistency/figures/volume_bias_by_warning_level.png`

- `analysis/phase24_physical_consistency/figures/peak_underprediction_by_warning_level.png`

- `analysis/phase24_physical_consistency/figures/physics_consistency_vs_risk_score.png`

- `analysis/phase24_physical_consistency/figures/wet_connectivity_fragmentation.png`

- `analysis/phase24_physical_consistency/figures/temporal_volume_bias_examples.png`

- `analysis/phase24_physical_consistency/figures/phase23_case_physical_failure_profiles.png`



## 4. Main Diagnostic Result



The central finding is that high-risk cases are not only statistically worse. They are also physically less consistent.



The warning-level progression shows a clear physical degradation pattern:



- false-dry behavior becomes stronger

- wet-area contraction becomes stronger

- peak-depth underprediction becomes much stronger

- wet-area connectivity loss becomes more severe

- relative volume bias becomes more negative



This provides a process-level explanation for the Phase 15/16/23 warning-risk categories.



## 5. Physical-Consistency Linkage With Risk Score



The strongest physical-consistency linkages with risk score are:



- false-dry rate: correlation with risk_score = 0.913

- wet-area contraction: correlation with risk_score = 0.862

- peak-depth underprediction: correlation with risk_score = 0.856

- connectivity loss indicator: correlation with risk_score = 0.539



These results indicate that the existing risk score is physically interpretable. It is strongly associated with missed inundation, shrinking predicted wet extent, attenuated local peak depths, and degraded wet-region connectivity.



## 6. Warning-Level Physical Failure Pattern



The warning-level group means show a clear progression from reliable to caution to high-risk.



### False-dry rate



- reliable: 0.125

- caution: 0.268

- high-risk: 0.444



The false-dry rate increases monotonically with warning severity. This means that high-risk cases are much more likely to miss truly wet cells.



### Wet-area contraction



- reliable: 0.046

- caution: 0.135

- high-risk: 0.383



Wet-area contraction is much stronger in high-risk cases. This confirms that high-risk predictions tend to shrink the inundated extent relative to the target field.



### Peak-depth underprediction



- reliable: 0.024 m

- caution: 0.241 m

- high-risk: 1.381 m



Peak-depth underprediction increases sharply in high-risk cases. This is consistent with previous Phase 13 and Phase 23 findings that high-intensity location2 cases show attenuated local maxima and severe underprediction of flood severity.



### Connectivity loss indicator



- reliable: 0.197

- caution: 0.240

- high-risk: 1.000



Connectivity loss is strongest in the high-risk group. This suggests that high-risk predictions do not only underpredict water depth; they also distort the spatial structure of inundation by weakening or fragmenting connected wet regions.



### Relative volume bias



- reliable: -0.040

- caution: -0.145

- high-risk: -0.448



The increasingly negative relative volume bias indicates that high-risk cases show stronger volume under-response. The model tends to produce less inundation volume than the target in more severe warning conditions.



## 7. Interpretation of Phase 23 Representative Cases



Phase 24 provides a physical-consistency explanation for the three Phase 23 representative cases.



The reliable case remains within a stronger applicability range because its physical-consistency errors are relatively small.



The caution case represents an intermediate state. It shows stronger missed-inundation and peak-depth attenuation than reliable cases, but it is not as physically degraded as the high-risk group.



The high-risk case is physically problematic because it combines several failure mechanisms:



- strong false-dry behavior

- strong wet-area contraction

- strong peak-depth underprediction

- stronger connectivity loss

- strong volume under-response



This confirms that the Phase 23 high-risk label is not just a screening label. It corresponds to identifiable physical-process inconsistency.



## 8. Topographic Diagnostic Status



The topographic-consistency diagnostic was skipped.



The reason is:



- no shape-compatible DEM or static elevation layer was found



The expected shape was:



- 128 x 128



The script recorded this limitation in both:



- `analysis/phase24_physical_consistency/summary.json`

- `analysis/phase24_physical_consistency/topographic_consistency.csv`



This is an important boundary of the current Phase 24 result. The project can currently diagnose volume response, peak-depth behavior, wet/dry behavior, temporal behavior, and connectivity structure. However, it cannot yet fully diagnose DEM-controlled error patterns without a compatible static elevation layer.



## 9. Relation to Previous Phases



Phase 24 strengthens the interpretation of previous results.



Phase 12 identified reliability and applicability boundaries.



Phase 13 showed that top failure cases are concentrated in high-intensity location2 scenarios and are dominated by underprediction and false-dry behavior.



Phase 14 showed that confidence and disagreement proxies can provide risk signals.



Phase 15 converted these signals into reliability screening and spatial risk mapping.



Phase 16 converted screening labels into warning-rule guidance.



Phase 23 demonstrated representative warning cases.



Phase 24 now explains these warning risks from a physical-consistency perspective.



The resulting chain is:



- high-risk warning label

- stronger false-dry behavior

- stronger wet-area contraction

- stronger peak-depth underprediction

- stronger connectivity loss

- stronger volume under-response



This makes the reliability-aware warning framework more physically interpretable.



## 10. Implications for Phase 25



Phase 24 suggests that the next model-refinement phase should not blindly add a complete shallow-water-equation residual.



The current data and artifacts support more targeted physics-consistency refinement first.



The most promising Phase 25 constraint directions are:



- false-dry reduction

- wet-area contraction penalty

- peak-depth preservation

- wet-connectivity preservation

- volume-response consistency



Candidate Phase 25 refinement ideas include:



- stronger false-dry penalty in physically important wet regions

- wet-area contraction-aware loss

- peak-depth preservation or high-depth weighted loss

- connectivity-aware wet-region consistency regularization

- temporal volume-response consistency loss



A full SWE/PINN-style residual may be considered later only if velocity, flux, boundary, DEM, and source-sink information become available in a consistent form.



## 11. Technical Boundaries



Phase 24 is a diagnostic phase, not a model-training phase.



The following actions were not performed:



- no model retraining

- no architecture modification

- no new prediction generation

- no Phase 10 boundary_weight tuning

- no boundary_band_pixels tuning

- no new loss-function deployment

- no new parameter sweep

- no metric-chasing experiment

- no traffic-impact modeling



The current recommended Phase 10 setting remains:



- boundary_band_pixels = 1

- boundary_weight = 2.0



The boundary_weight = 1.5 setting remains only a conservative rollback option.



## 12. Limitations



The current physical-consistency diagnosis is limited by available artifacts.



The main limitations are:



- no compatible DEM/static elevation layer was found for topographic diagnostics

- connectivity metrics are based on wet/dry thresholded structures and should be interpreted as structural indicators rather than full hydrodynamic connectivity

- volume-response metrics are based on predicted and target depth fields rather than full water-balance closure with boundary fluxes

- no explicit velocity or discharge field is available

- no full shallow-water-equation residual was computed

- warning labels remain deterministic screening labels, not calibrated probabilities



These limitations do not invalidate the Phase 24 result, but they define the boundary of what can be claimed.



## 13. Phase 24 Conclusion



Phase 24 successfully deepens the reliability-aware warning framework by adding process-level physical-consistency diagnosis.



The main conclusion is that high-risk scenarios are physically less consistent than reliable scenarios. They show stronger false-dry behavior, stronger wet-area contraction, stronger peak-depth underprediction, stronger connectivity loss, and stronger volume under-response.



This result moves the project closer to the long-term goal of a trustworthy, interpretable, physically consistent deep-learning surrogate framework for rapid urban flood warning.



Phase 24 also provides a clear basis for a later Phase 25 model-refinement phase focused on targeted physical-consistency constraints rather than blind metric chasing.

