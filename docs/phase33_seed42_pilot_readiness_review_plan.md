\# Phase 33 Seed42 Pilot Readiness Review Plan



\## 1. Background



Phase 32 completed a plan-first, design/diagnostic-only Level 4+ domain-/boundary-aware physical consistency design.



Phase 32 formalized:



\- a Level 4+ proxy scope;

\- domain-/boundary-aware region roles;

\- 20 guardrail metrics;

\- 12 stop/go criteria;

\- the decision `design\_ready\_no\_training\_yet`.



Phase 32 did not train, modify loss functions, modify configs, run seed123/seed202, or perform sweeps.



The current question is whether the project is ready to define a narrow seed42 pilot objective, not whether it should immediately train.



\## 2. Purpose



The purpose of Phase 33 is to review pilot readiness under the Phase 32 guardrail framework.



Phase 33 should answer:



1\. Is there a sufficiently sharp failure mode for a future seed42 pilot?

2\. Is the target region fixed?

3\. Are baseline comparisons fixed?

4\. Are acceptance and rejection thresholds defined?

5\. Are all guardrail groups satisfied before training?

6\. Would a future pilot avoid the Phase 27 underresponse-only failure?

7\. Would a future pilot avoid the Phase 29 tolerance-band trade-off?

8\. Does the proposed scope remain Level 4+ proxy-only?



Phase 33 is a readiness review and objective-selection phase.



\## 3. What Phase 33 Is Not



Phase 33 is not:



\- a training phase;

\- a new loss implementation phase;

\- a config creation phase;

\- a seed123 or seed202 expansion phase;

\- a sweep phase;

\- a model architecture change;

\- a strict conservation implementation;

\- a SWE/PINN implementation;

\- a full hydrodynamic closure attempt.



Phase 33 must not modify:



\- `utils/physics\_losses.py`;

\- training configs;

\- model architecture;

\- trainer code.



\## 4. Inputs



Phase 33 should use existing Phase 31 and Phase 32 evidence:



\### Phase 31 evidence



\- `docs/phase31\_physics\_input\_recovery\_readiness\_findings.md`

\- `analysis/phase31\_physics\_input\_recovery\_readiness/masked\_physical\_error\_findings.md`

\- `analysis/phase31\_physics\_input\_recovery\_readiness/masked\_physical\_error\_delta\_phase29\_vs\_phase27.csv`



\### Phase 32 evidence



\- `docs/phase32\_domain\_boundary\_aware\_physical\_consistency\_plan.md`

\- `docs/phase32\_domain\_boundary\_aware\_design.md`

\- `analysis/phase32\_domain\_boundary\_aware\_design/guardrail\_metrics.csv`

\- `analysis/phase32\_domain\_boundary\_aware\_design/stop\_go\_criteria.csv`

\- `analysis/phase32\_domain\_boundary\_aware\_design/design\_summary.json`

\- `analysis/phase32\_domain\_boundary\_aware\_design/phase32\_guardrail\_summary.md`

\- `docs/phase32\_domain\_boundary\_aware\_physical\_consistency\_findings.md`



\## 5. Evidence To Review



Phase 33 should review the following critical evidence.



\### 5.1 Phase 29 masked diagnostic trade-off



Phase 29 improved valid-domain relative volume-bias proxy compared with Phase 27:



\- Phase 27: `0.0169359`

\- Phase 29: `0.0115344`



However, Phase 29 worsened:



\- valid-domain RMSE: `0.0460827 -> 0.0480984`

\- valid-domain MAE: `0.0183693 -> 0.0190492`

\- false-dry rate: `0.0689175 -> 0.0739891`

\- false-wet rate: `0.0181923 -> 0.0194308`

\- false-dry volume-loss proxy: `3575.36 -> 4027.38`

\- false-wet volume-excess proxy: `5263.67 -> 5690.27`



This means a future pilot cannot simply optimize volume-bias proxy.



\### 5.2 Region-specific failure modes



Phase 31 identified:



\- `manhole\_nonzero\_valid` has the highest Phase 29 false-dry rate: `0.131298`

\- `high\_impervious\_valid` has the highest Phase 29 false-wet rate: `0.0239894`

\- boundary-ring false-dry worsened from Phase 27 to Phase 29



These are candidate target regions or guardrail regions.



\### 5.3 Phase 32 guardrail framework



Phase 32 formalized 20 guardrail metrics and 12 stop/go criteria.



Guardrail groups:



\- `standard`

\- `valid\_domain`

\- `boundary\_ring`

\- `high\_impervious\_valid`

\- `manhole\_nonzero\_valid`

\- `dry\_threshold`

\- `level\_boundary`



Current Phase 32 decision:



`design\_ready\_no\_training\_yet`



\## 6. Pilot Readiness Criteria



Phase 33 should evaluate the following readiness criteria.



\### Criterion 1: Diagnosed failure mode



A future pilot must target one diagnosed failure mode, not a broad multi-objective improvement.



Possible candidate failure modes:



\- boundary-ring false-dry;

\- manhole-nonzero false-dry;

\- high-impervious false-wet;

\- dry-threshold low-depth accumulation;

\- valid-domain volume-bias proxy under guardrails.



\### Criterion 2: Fixed target region



The target mask must be fixed before training.



Possible masks:



\- `valid\_domain`

\- `boundary\_ring`

\- `high\_impervious\_valid`

\- `manhole\_nonzero\_valid`

\- dry/near-threshold subset inside valid domain



\### Criterion 3: Fixed baseline comparison



Baseline comparisons must be fixed before training.



Required baselines should include:



\- Phase 25 seed42;

\- Phase 27 seed42;

\- Phase 29 seed42.



If a future pilot is proposed, it must be compared against these baselines before any seed expansion.



\### Criterion 4: Acceptance thresholds



Acceptance thresholds must be written before training.



They should include:



\- standard metrics;

\- valid-domain masked metrics;

\- boundary-ring metrics;

\- high-impervious metrics;

\- manhole-nonzero metrics;

\- dry-threshold metrics;

\- claim-boundary guardrails.



\### Criterion 5: Rejection thresholds



Rejection thresholds must be written before training.



A pilot should be rejected if it repeats Phase 29 behavior:



\- improves volume-bias proxy but worsens RMSE, MAE, false-dry, false-wet, or peak-depth proxies.



\### Criterion 6: Level boundary



Any pilot must remain Level 4+ proxy-framed.



It must not claim:



\- strict conservation;

\- full mass conservation;

\- SWE/PINN;

\- full hydrodynamic closure;

\- Level 5 strong physics.



\## 7. Candidate Pilot Objective Options



Phase 33 should compare candidate pilot objectives, without implementing them.



\### Option A: Boundary-ring false-dry guardrail pilot



Target:



\- boundary-ring false-dry.



Potential benefit:



\- directly addresses boundary-sensitive wet/dry degradation.



Risk:



\- boundary behavior is physically ambiguous without real boundary fluxes.



\### Option B: Manhole-region false-dry diagnostic pilot



Target:



\- `manhole\_nonzero\_valid` false-dry.



Potential benefit:



\- targets the highest Phase 29 false-dry region.



Risk:



\- manhole map is a sparse indicator, not a drainage-capacity field.



\### Option C: High-impervious false-wet guardrail pilot



Target:



\- `high\_impervious\_valid` false-wet.



Potential benefit:



\- targets the highest Phase 29 false-wet region.



Risk:



\- imperviousness is a static runoff proxy, not a direct hydraulic state.



\### Option D: Dry-threshold accumulation guard pilot



Target:



\- dry/near-threshold low-depth accumulation.



Potential benefit:



\- directly addresses Phase 28 failure diagnosis.



Risk:



\- may repeat threshold-sensitive trade-offs if not heavily guarded.



\### Option E: No pilot yet



Target:



\- none.



Potential benefit:



\- avoids premature training when acceptance/rejection thresholds are incomplete.



Risk:



\- technical progress pauses until pilot conditions are clearer.



\## 8. Expected Script



Phase 33 may create a diagnostic/readiness script:



`scripts/review\_phase33\_seed42\_pilot\_readiness.py`



This script should not train or modify model/loss/config code.



It should read:



\- Phase 32 guardrail metrics;

\- Phase 32 stop/go criteria;

\- Phase 31 masked diagnostics;

\- Phase 32 design summary.



It should output:



\- `analysis/phase33\_seed42\_pilot\_readiness/pilot\_option\_scores.csv`

\- `analysis/phase33\_seed42\_pilot\_readiness/readiness\_criteria\_status.csv`

\- `analysis/phase33\_seed42\_pilot\_readiness/phase33\_readiness\_summary.json`

\- `analysis/phase33\_seed42\_pilot\_readiness/phase33\_readiness\_summary.md`



\## 9. Expected Review Outputs



Phase 33 should produce:



\- `docs/phase33\_seed42\_pilot\_readiness\_review\_plan.md`

\- optional script: `scripts/review\_phase33\_seed42\_pilot\_readiness.py`

\- `analysis/phase33\_seed42\_pilot\_readiness/` outputs

\- `docs/phase33\_seed42\_pilot\_readiness\_review\_findings.md`



\## 10. Expected Decision Types



Phase 33 should end with one of these decisions.



\### Decision A: `pilot\_not\_ready`



Use this if failure mode, thresholds, baselines, or guardrails remain insufficient.



\### Decision B: `pilot\_design\_ready\_but\_training\_not\_started`



Use this if one pilot target is clear, but training should still wait for final review.



\### Decision C: `narrow\_seed42\_pilot\_allowed\_next`



Use this only if all stop/go criteria are satisfied.



This decision should be rare and must still not run training inside Phase 33.



\## 11. Likely Expected Decision



Based on Phase 32, the likely current decision is:



`pilot\_not\_ready` or `pilot\_design\_ready\_but\_training\_not\_started`



because acceptance/rejection thresholds are not fully fixed and the pilot objective has not yet been selected.



Phase 33 should not force a pilot decision if evidence is insufficient.



\## 12. Guardrails



Phase 33 must follow these guardrails:



1\. Do not train.

2\. Do not modify losses.

3\. Do not modify configs.

4\. Do not modify model architecture.

5\. Do not run seed123 or seed202.

6\. Do not perform sweeps.

7\. Do not claim Phase 29 success.

8\. Do not claim strict conservation.

9\. Do not claim full mass conservation.

10\. Do not claim SWE/PINN.

11\. Do not claim full hydrodynamic closure.

12\. Keep all conclusions at Level 4+ proxy scope.

13\. Do not authorize training unless all stop/go criteria are explicitly satisfied.



\## 13. Success Criteria



Phase 33 succeeds if it:



\- evaluates all candidate pilot objective options;

\- identifies whether a pilot target is sharp enough;

\- records which readiness criteria are met or unmet;

\- prevents premature training;

\- gives a clear decision;

\- preserves the Level 4+ / Level 5 boundary;

\- defines what would be required before any future seed42 pilot.



\## 14. Immediate Next Step



After committing this plan, implement the diagnostic-only readiness review script:



`scripts/review\_phase33\_seed42\_pilot\_readiness.py`



No training or loss modification should occur.

