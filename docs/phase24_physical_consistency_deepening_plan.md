# Phase 24 Physical Consistency Deepening and Process Diagnostics Plan



## 1. Objective



Phase 24 moves the project from reliability-aware warning case demonstration toward deeper physical-consistency diagnosis.



The objective is not to retrain the model immediately. Instead, Phase 24 aims to systematically diagnose whether the existing Phase 10 recommended surrogate model produces flood-depth predictions that are physically reasonable in terms of rainfall-volume response, peak-depth behavior, topographic control, wet-area connectivity, temporal process evolution, and linkage with warning-risk categories.



This phase prepares the evidence base for a later physics-consistency guided model refinement phase.



## 2. Research Position



The current project has already established the following chain:



- Phase 10: margin-aware physics-guided prediction model

- Phase 12: reliability and applicability diagnosis

- Phase 13: representative failure-case visualization

- Phase 14: confidence and disagreement proxy diagnostics

- Phase 15: reliability screening and spatial risk mapping

- Phase 16: warning-rule and applicability-boundary guidance

- Phase 17: reliability-aware warning framework synthesis

- Phase 18-22: manuscript-oriented consolidation

- Phase 23: reliability-aware warning case-study prototype



Phase 24 does not replace the reliability-aware warning framework. It deepens the physical explanation behind it.



The core question is:



- where does the surrogate model violate or weaken physically plausible flood-process behavior?

- do these physical-consistency issues explain reliable, caution, and high-risk warning categories?

- which physical-consistency constraints should be prioritized in a later model-refinement phase?



## 3. What Phase 24 Should Do



Phase 24 should diagnose the physical consistency of existing model outputs.



It should reuse existing prediction artifacts, evaluation outputs, Phase 15 risk-screening outputs, Phase 16 warning outputs, and available static layers where possible.



The planned diagnostic modules are:



1. rainfall-volume response consistency

2. peak-depth consistency and underprediction diagnosis

3. topographic-control consistency

4. wet-area connectivity and fragmentation diagnosis

5. temporal process consistency

6. physical-consistency linkage with Phase 15/16 risk and warning labels



Phase 24 should generate interpretable physical-consistency metrics, tables, figures, and findings.



## 4. What Phase 24 Should Not Do



Phase 24 must not perform the following actions:



1. no model retraining

2. no architecture modification

3. no new prediction generation

4. no Phase 10 boundary-weight sweep

5. no boundary_band_pixels tuning

6. no boundary_weight tuning

7. no new loss-function deployment

8. no metric-chasing experiment

9. no manuscript literature-review expansion

10. no traffic-impact modeling yet



The current recommended Phase 10 setting remains:



- boundary_band_pixels = 1

- boundary_weight = 2.0



The boundary_weight = 1.5 setting remains only a conservative rollback option.



## 5. Physical-Consistency Questions



### 5.1 Rainfall-volume response consistency



This diagnostic asks whether predicted inundation volume responds reasonably to rainfall intensity and scenario severity.



Example questions:



- does predicted inundation volume increase when rainfall intensity or severity increases?

- does the model systematically under-respond in high-intensity scenarios?

- do high-risk cases show stronger volume under-response than reliable cases?

- does predicted wet area contract relative to target wet area in physically important scenarios?



Candidate metrics:



- target inundation volume

- predicted inundation volume

- volume bias

- relative volume bias

- target wet area

- predicted wet area

- wet-area contraction

- rainfall-severity group statistics



### 5.2 Peak-depth consistency



This diagnostic asks whether local peak depths are preserved.



Example questions:



- where does the model underestimate local maximum water depth?

- are high-intensity and high-risk scenarios associated with stronger peak-depth underprediction?

- do moderate-to-deep target depths show systematic attenuation?

- is the peak-depth error consistent with Phase 12 and Phase 13 findings?



Candidate metrics:



- target maximum depth

- predicted maximum depth

- peak-depth bias

- peak-depth underprediction

- depth-bin error summary

- warning-level grouped peak-depth bias



### 5.3 Topographic-control consistency



This diagnostic asks whether errors are consistent with terrain-controlled flood behavior.



Example questions:



- are low-lying cells more likely to be false-dry?

- does the model create implausible wet predictions on relatively high terrain?

- do errors concentrate near sharp topographic transitions?

- is high-risk behavior related to DEM-controlled accumulation zones?



Candidate metrics:



- DEM-stratified error

- low-elevation false-dry rate

- high-elevation false-wet rate

- error by DEM quantile

- depth error versus DEM relationship

- terrain-transition-zone error summary



### 5.4 Wet-area connectivity and fragmentation



This diagnostic asks whether predicted wet areas preserve physically plausible connectivity.



Example questions:



- does the model fragment continuous target inundation regions?

- does it create false-dry holes within target wet areas?

- do high-risk cases show more wet-region fragmentation?

- is boundary false-dry risk associated with connectivity loss?



Candidate metrics:



- number of target wet connected components

- number of predicted wet connected components

- connected-component difference

- largest wet-component area ratio

- false-dry hole indicator

- fragmentation index

- boundary-zone connectivity error



### 5.5 Temporal process consistency



This diagnostic asks whether multi-step predictions evolve plausibly over time.



Example questions:



- does predicted inundation volume evolve smoothly through the forecast horizon?

- does the model underpredict the growth phase or the peak phase?

- are there unrealistic abrupt jumps or collapses in wet area?

- do high-risk scenarios show stronger temporal inconsistency?



Candidate metrics:



- timestep-wise volume bias

- timestep-wise wet-area bias

- timestep-wise peak-depth bias

- temporal smoothness index

- target-predicted peak timing difference

- growth-phase under-response indicator



### 5.6 Physical-consistency linkage with warning risk



This diagnostic links physical-consistency metrics with existing Phase 15/16 risk labels.



Example questions:



- do high-risk cases show systematically worse physical-consistency metrics?

- which physical-consistency metrics best explain risk_score?

- is false-dry risk associated with wet-connectivity loss?

- is peak underprediction associated with volume under-response?

- can physical-consistency diagnostics strengthen the interpretability of warning labels?



Candidate outputs:



- physical metrics grouped by warning level

- correlation between physical metrics and risk_score

- high-risk physical failure profiles

- reliable versus high-risk contrast table

- physical-consistency explanation for Phase 23 selected cases



## 6. Expected Input Sources



Phase 24 should reuse existing files where possible.



Expected sources include:



- Phase 10 evaluation map artifacts under `runs/phase10_margin_aware_boundary_band_*`

- Phase 15 scenario risk scores under `analysis/phase15_reliability_screening/`

- Phase 16 scenario warning summaries under `analysis/phase16_warning_rules/`

- Phase 23 selected case information under `analysis/phase23_warning_case_study/`

- available static map layers, including DEM if present in the dataset or run artifacts

- available rainfall arrays or rainfall metadata if present in scenario metadata or run artifacts



The script should be robust. If a specific input is unavailable, it should skip that diagnostic component and record the limitation clearly in `summary.json` and the findings document.



## 7. Planned Script



The main analysis script should be:



- `scripts/analyze_phase24_physical_consistency.py`



The script should create:



- `analysis/phase24_physical_consistency/`



Expected outputs include:



- `analysis/phase24_physical_consistency/summary.json`

- `analysis/phase24_physical_consistency/scenario_physical_consistency_metrics.csv`

- `analysis/phase24_physical_consistency/volume_response_metrics.csv`

- `analysis/phase24_physical_consistency/peak_depth_consistency.csv`

- `analysis/phase24_physical_consistency/topographic_consistency.csv`

- `analysis/phase24_physical_consistency/wet_connectivity_metrics.csv`

- `analysis/phase24_physical_consistency/temporal_consistency_metrics.csv`

- `analysis/phase24_physical_consistency/physics_risk_linkage.csv`

- `analysis/phase24_physical_consistency/figures/`



Recommended figures include:



- `rainfall_volume_response.png`

- `volume_bias_by_warning_level.png`

- `peak_underprediction_by_warning_level.png`

- `topographic_error_pattern.png`

- `wet_connectivity_fragmentation.png`

- `temporal_volume_bias_examples.png`

- `physics_consistency_vs_risk_score.png`

- `phase23_case_physical_failure_profiles.png`



The exact output names may be adjusted depending on available fields and artifacts.



## 8. Expected Findings Document



After the analysis script is implemented and run, Phase 24 should add:



- `docs/phase24_physical_consistency_deepening_findings.md`



The findings document should summarize:



1. which physical-consistency diagnostics were available

2. which diagnostics were skipped due to missing inputs

3. whether high-risk cases show stronger physical inconsistency

4. whether peak-depth underprediction and wet-area contraction explain previous failure modes

5. whether topography and wet-connectivity metrics explain false-dry behavior

6. what physical constraints should be prioritized in a later refinement phase



## 9. Expected Research Meaning



Phase 24 should move the project from reliability-aware warning demonstration toward process-level physical interpretability.



The intended contribution is:



- rapid flood-depth prediction

- reliability-aware warning interpretation

- physical-consistency diagnosis

- process-based explanation of warning risk

- evidence for future physics-consistency guided model refinement



Phase 24 should help answer not only whether a prediction is reliable, but why it is or is not physically reliable.



## 10. Acceptance Criteria



Phase 24 can be considered complete if the following conditions are satisfied:



1. the plan document is committed

2. `scripts/analyze_phase24_physical_consistency.py` is implemented

3. `analysis/phase24_physical_consistency/` is generated

4. available physical-consistency metrics are exported as CSV and JSON

5. figures are generated for available diagnostics

6. unavailable diagnostics are clearly documented

7. physical-consistency metrics are linked to Phase 15/16 warning or risk categories

8. Phase 23 selected cases are interpreted from a physical-consistency perspective

9. `docs/phase24_physical_consistency_deepening_findings.md` is written

10. README, project_status, and experiment_index are synchronized

11. no retraining, architecture modification, new prediction generation, or Phase 10 parameter tuning is performed



## 11. Immediate Next Steps



After saving this plan:



1. inspect the plan

2. commit the plan

3. ask Codex to implement `scripts/analyze_phase24_physical_consistency.py`

4. run the script

5. inspect generated outputs and figures

6. write Phase 24 findings

7. update README, project_status, and experiment_index

8. merge Phase 24 into main if outputs are satisfactory

