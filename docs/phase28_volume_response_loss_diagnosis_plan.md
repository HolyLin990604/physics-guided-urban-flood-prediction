\# Phase 28 Volume-Response Loss Failure Diagnosis and Redesign Plan



\## 1. Background



Phase 27 tested a conservative Level 4 `volume\_response\_consistency` loss on seed42. The pilot was built on the Phase 25 target-wet recall configuration and kept the Phase 10 boundary-band settings unchanged.



The Phase 27 seed42 pilot improved all standard test metrics relative to Phase 25 seed42:



\- RMSE improved from `0.0447470026` to `0.0423809813`

\- MAE improved from `0.0179394448` to `0.0172847716`

\- wet/dry IoU improved from `0.8038777207` to `0.8128013736`

\- rollout stability improved from `0.9895041993` to `0.9901222963`

\- step RMSE std improved from `0.0106537426` to `0.0100226047`



It also improved several under-response-related physical proxies:



\- false-dry volume loss decreased by `-1.77546`

\- wet-area contraction decreased by `-0.00626303`

\- peak-depth underprediction decreased by `-0.011376`

\- false-wet rate decreased by `-0.000387357`

\- false-wet volume excess decreased by `-0.403664`



However, the primary Phase 27 volume-response objective was not achieved:



\- aggregate absolute relative volume bias worsened by `+0.0216934`

\- mean-step absolute relative volume bias worsened by `+0.0170953`

\- run-level aggregate relative volume bias shifted from Phase 25 `+0.00296825` to Phase 27 `+0.0246616`



Therefore, Phase 27 was classified as:



`mixed seed42 pilot`



or:



`standard-metric positive, volume-response objective not confirmed`



The Phase 27 decision was:



`remain\_seed42\_positive\_only`



No seed123/seed202 confirmation or Phase 27 weight sweep should be performed before diagnosing the failure mechanism.



\## 2. Purpose



The purpose of Phase 28 is to diagnose why the underresponse-only volume-response loss improved several local under-response indicators but failed to improve the primary volume-response consistency objective.



Phase 28 should answer:



Why did Phase 27 improve standard metrics and several physical proxies, but worsen aggregate and timestep-wise absolute relative volume bias?



\## 3. Core Scientific Question



The central question is:



Did Phase 27 worsen volume-response consistency because of:



1\. already-wet cells becoming too deep;

2\. localized peak-depth overcompensation;

3\. a small number of timesteps dominating aggregate volume bias;

4\. high-depth cells contributing excessive positive volume;

5\. low-depth wet-region expansion;

6\. mismatch between training-time batch-level volume loss and test-time aggregate volume diagnostics;

7\. the underresponse-only loss being unsuitable when Phase 25 already has near-zero aggregate volume bias?



\## 4. What Phase 28 Is Not



Phase 28 is not:



\- a new training phase;

\- a Phase 27 weight sweep;

\- seed123/seed202 confirmation;

\- a return to Phase 10 boundary-weight tuning;

\- a full SWE/PINN implementation;

\- a strict mass-conservation phase;

\- a claim of full hydrodynamic physical consistency.



Phase 28 is a diagnostic and redesign phase.



\## 5. Diagnostic Objectives



\### Objective 1: Decompose volume-bias worsening



Determine whether the Phase 27 aggregate volume-bias increase comes from:



\- broad over-response across many timesteps;

\- a few high-error timesteps;

\- already-wet cells becoming deeper;

\- false-wet area expansion;

\- peak-depth overcompensation;

\- or scenario-specific behavior.



\### Objective 2: Separate wet-area and wet-depth effects



Phase 27 did not increase false-wet rate or false-wet volume excess. Therefore, the aggregate volume-bias worsening may not be caused by simple wet-area expansion.



Phase 28 should decompose volume changes into:



\- target-wet/pred-wet overlap volume;

\- false-dry volume loss;

\- false-wet volume excess;

\- already-wet cell depth amplification;

\- peak-depth contribution.



\### Objective 3: Analyze timestep-wise behavior



Phase 28 should identify whether the volume-bias worsening occurs:



\- uniformly across timesteps;

\- mainly during peak inundation;

\- mainly during recession;

\- or only in a few extreme steps.



\### Objective 4: Determine whether underresponse-only loss is unsuitable



Phase 25 seed42 aggregate relative volume bias was already close to zero:



`+0.00296825`



This means an underresponse-only loss may be poorly matched to seed42 because there was little aggregate under-response left to correct.



Phase 28 should evaluate whether future loss design should use:



\- tolerance-band volume loss;

\- signed-volume-bias loss;

\- balanced under/over-response penalty;

\- selective high-underresponse-only loss;

\- or scenario-conditioned volume correction.



\## 6. Planned Diagnostic Script



Possible script:



`scripts/diagnose\_phase28\_volume\_response\_failure.py`



Expected input runs:



\- Phase 25 baseline:

&#x20; `runs/phase25\_target\_wet\_recall\_seed42\_40e`

\- Phase 27 pilot:

&#x20; `runs/phase27\_volume\_response\_seed42\_40e`



Expected output directory:



`analysis/phase28\_volume\_response\_loss\_diagnosis/`



Expected outputs:



\- `volume\_bias\_decomposition\_by\_step.csv`

\- `volume\_bias\_decomposition\_summary.csv`

\- `volume\_bias\_timestep\_ranking.csv`

\- `volume\_bias\_depth\_bin\_decomposition.csv`

\- `phase28\_volume\_response\_failure\_summary.json`

\- `phase28\_volume\_response\_failure\_findings.md`



\## 7. Candidate Diagnostics



Phase 28 should compute:



\- per-step volume bias;

\- per-step relative volume bias;

\- absolute relative volume bias;

\- positive volume excess;

\- negative volume deficit;

\- overlap wet-cell volume difference;

\- false-dry volume loss;

\- false-wet volume excess;

\- target-wet overlap depth difference;

\- peak-cell contribution;

\- high-depth-bin contribution;

\- timestep ranking by Phase27 minus Phase25 volume-bias worsening.



\## 8. Loss Redesign Candidates



Phase 28 should not immediately implement a new loss, but it may recommend one of the following redesign directions.



\### Candidate A: Tolerance-band volume consistency



Do not penalize small volume bias near zero.



Only penalize if relative volume bias exceeds a tolerance band, such as:



\- `abs(relative\_volume\_bias) > 0.02`

\- or a tuned conservative threshold.



\### Candidate B: Balanced signed volume consistency



Instead of underresponse-only loss, penalize both under-response and over-response, but with asymmetric weights.



Example:



\- under-response penalty weight higher;

\- over-response penalty weight lower;

\- no penalty inside a tolerance band.



\### Candidate C: High-underresponse-only selective loss



Apply volume-response loss only to batches or timesteps where target volume is high and predicted volume is clearly lower.



This avoids pushing already near-balanced cases into over-response.



\### Candidate D: Depth-bin-aware correction



Apply correction only where underprediction occurs in target-wet moderate/deep cells, rather than globally increasing volume.



\### Candidate E: Keep Phase 27 as a negative/mixed pilot



If diagnostics show no stable loss-design path, Phase 27 should remain a documented mixed pilot and no further training should be performed.



\## 9. Success Criteria for Phase 28



Phase 28 succeeds if it can clearly explain:



\- why Phase 27 worsened volume bias;

\- whether the worsening comes from over-response in already-wet cells or from false-wet expansion;

\- whether only a small number of timesteps dominate the volume-bias worsening;

\- whether underresponse-only loss is fundamentally mismatched to Phase 25 seed42;

\- what loss redesign, if any, is scientifically justified.



\## 10. Guardrails



Phase 28 must follow these guardrails:



1\. Do not train a new model.

2\. Do not run seed123 or seed202.

3\. Do not sweep Phase 27 weights.

4\. Do not modify model architecture.

5\. Do not claim strict conservation.

6\. Do not claim SWE/PINN.

7\. Do not claim full mass conservation.

8\. Do not continue Phase 27 until the failure mechanism is diagnosed.

9\. Do not optimize only standard metrics.

10\. Do not treat volume-response improvement as confirmed.



\## 11. Expected Outcome



The expected outcome is a diagnosis of the Phase 27 seed42 mixed result.



Possible final decisions include:



\- revise loss design using a tolerance-band volume consistency term;

\- revise loss design using a signed/balanced volume-bias term;

\- restrict volume-response correction to high-underresponse cases;

\- keep Phase 27 as an informative mixed pilot and pause volume-response training;

\- or design a new Phase 29 only after the Phase 28 diagnosis justifies it.



\## 12. Immediate Next Step



After this plan is committed, the next step is to implement a diagnostic-only script:



`scripts/diagnose\_phase28\_volume\_response\_failure.py`



This script should compare Phase 25 and Phase 27 seed42 evaluation-test forecast maps and decompose where the volume-bias worsening came from.

