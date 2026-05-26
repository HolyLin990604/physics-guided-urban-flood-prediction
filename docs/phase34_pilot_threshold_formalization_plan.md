\# Phase 34 Seed42 Pilot Acceptance/Rejection Threshold Formalization Plan



\## 1. Background



Phase 33 completed a diagnostic-only seed42 pilot readiness review under the Phase 32 guardrail framework.



Phase 33 result:



\- pilot options evaluated: 5

\- readiness criteria evaluated: 15

\- recommended future candidate: `manhole\_nonzero\_false\_dry\_guardrail`

\- current decision: `pilot\_design\_ready\_but\_training\_not\_started`

\- training authorized: `false`



The recommended future candidate is `manhole\_nonzero\_false\_dry\_guardrail` because `manhole\_nonzero\_valid` had the highest Phase 29 false-dry rate among the reviewed masked diagnostic regions.



However, Phase 33 did not authorize training because the following items remain incomplete:



\- numeric acceptance thresholds are not fixed;

\- numeric rejection thresholds are not fixed;

\- full Phase 25 / Phase 27 / Phase 29 baseline acceptance/rejection criteria are not written;

\- a single future pilot objective and target region are not formally locked as a training design.



Therefore, Phase 34 should formalize acceptance/rejection thresholds before any future pilot implementation.



\## 2. Purpose



The purpose of Phase 34 is to convert Phase 33 readiness blockers into explicit threshold rules.



Phase 34 should define:



1\. fixed baseline comparisons;

2\. numeric acceptance thresholds;

3\. numeric rejection thresholds;

4\. pilot failure patterns;

5\. pilot success requirements;

6\. stop/go rules for any future seed42 pilot.



Phase 34 is still not a training phase. It is a threshold-formalization and pre-training decision phase.



\## 3. What Phase 34 Is Not



Phase 34 is not:



\- a training phase;

\- a new loss implementation phase;

\- a config creation phase;

\- a seed42 run;

\- a seed123 or seed202 expansion;

\- a sweep phase;

\- a Phase 29 continuation;

\- a strict mass-conservation implementation;

\- a SWE/PINN implementation;

\- a hydrodynamic closure attempt.



Phase 34 must not modify:



\- `utils/physics\_losses.py`;

\- training configs;

\- model architecture;

\- trainer code.



\## 4. Inputs



Phase 34 should use existing evidence from Phases 25, 27, 29, 31, 32, and 33.



\### Baseline runs



Required seed42 baseline references:



\- Phase 25 seed42: `runs/phase25\_target\_wet\_recall\_seed42\_40e`

\- Phase 27 seed42: `runs/phase27\_volume\_response\_seed42\_40e`

\- Phase 29 seed42: `runs/phase29\_tolerance\_band\_volume\_seed42\_40e`



\### Phase 31 masked diagnostics



Use:



\- `analysis/phase31\_physics\_input\_recovery\_readiness/masked\_physical\_error\_by\_phase.csv`

\- `analysis/phase31\_physics\_input\_recovery\_readiness/masked\_physical\_error\_by\_region.csv`

\- `analysis/phase31\_physics\_input\_recovery\_readiness/masked\_physical\_error\_delta\_phase29\_vs\_phase27.csv`

\- `analysis/phase31\_physics\_input\_recovery\_readiness/masked\_physical\_error\_summary.json`

\- `analysis/phase31\_physics\_input\_recovery\_readiness/masked\_physical\_error\_findings.md`



\### Phase 32 guardrails



Use:



\- `analysis/phase32\_domain\_boundary\_aware\_design/guardrail\_metrics.csv`

\- `analysis/phase32\_domain\_boundary\_aware\_design/stop\_go\_criteria.csv`

\- `analysis/phase32\_domain\_boundary\_aware\_design/design\_summary.json`

\- `analysis/phase32\_domain\_boundary\_aware\_design/phase32\_guardrail\_summary.md`



\### Phase 33 readiness review



Use:



\- `analysis/phase33\_seed42\_pilot\_readiness/pilot\_option\_scores.csv`

\- `analysis/phase33\_seed42\_pilot\_readiness/readiness\_criteria\_status.csv`

\- `analysis/phase33\_seed42\_pilot\_readiness/phase33\_readiness\_summary.json`

\- `analysis/phase33\_seed42\_pilot\_readiness/phase33\_readiness\_summary.md`

\- `docs/phase33\_seed42\_pilot\_readiness\_review\_findings.md`



\## 5. Baseline Metrics To Fix



Phase 34 should fix baseline values for at least these categories.



\### Standard metrics



From existing `evaluation\_test/metrics.json` files:



\- RMSE

\- MAE

\- wet/dry IoU

\- rollout stability

\- step RMSE standard deviation



\### Valid-domain masked metrics



From Phase 31 masked diagnostics:



\- valid-domain RMSE

\- valid-domain MAE

\- valid-domain false-dry rate

\- valid-domain false-wet rate

\- valid-domain false-dry volume-loss proxy

\- valid-domain false-wet volume-excess proxy

\- valid-domain relative volume-bias proxy

\- valid-domain absolute relative volume-bias proxy



\### Manhole-nonzero target metrics



Since Phase 33 recommended `manhole\_nonzero\_false\_dry\_guardrail`, Phase 34 should fix:



\- manhole-nonzero false-dry rate

\- manhole-nonzero false-dry volume-loss proxy

\- manhole-nonzero peak-depth underprediction

\- manhole-nonzero RMSE

\- manhole-nonzero MAE



\### Guardrail regions



Also fix baseline values for:



\- boundary-ring false-dry rate

\- boundary-ring false-wet rate

\- high-impervious false-wet rate

\- dry-threshold / dry-or-threshold accumulation proxy if available



\## 6. Required Acceptance Logic



A future pilot must not be accepted only because it improves one target metric.



A future pilot can only be accepted if it satisfies all required guardrails.



Minimum acceptance logic:



1\. It must improve or maintain the selected target failure metric.

2\. It must not worsen standard RMSE beyond a predeclared tolerance.

3\. It must not worsen standard MAE beyond a predeclared tolerance.

4\. It must not reduce wet/dry IoU beyond a predeclared tolerance.

5\. It must not worsen valid-domain RMSE / MAE beyond predeclared tolerance.

6\. It must not worsen valid-domain false-dry rate.

7\. It must not worsen valid-domain false-wet rate.

8\. It must not worsen false-dry volume-loss proxy.

9\. It must not worsen false-wet volume-excess proxy.

10\. It must not repeat the Phase 29 trade-off pattern.



\## 7. Required Rejection Logic



Phase 34 must define hard rejection rules.



A future pilot should be rejected if any of the following occurs:



1\. It improves volume-bias proxy while worsening RMSE, MAE, false-dry, and false-wet metrics.

2\. It repeats the Phase 29 trade-off pattern.

3\. It worsens `manhole\_nonzero\_valid` false-dry rate while claiming to target manhole false-dry.

4\. It worsens `high\_impervious\_valid` false-wet rate substantially.

5\. It worsens boundary-ring false-dry substantially.

6\. It improves only one proxy metric while degrading multiple physical error proxies.

7\. It violates Level 4+ proxy claim boundaries.

8\. It requires Level 5 variables that are not available.

9\. It depends on seed123/seed202 before seed42 is accepted.

10\. It requires a sweep to be interpretable.



\## 8. Candidate Future Pilot Target



The only candidate allowed to be formalized in Phase 34 is:



`manhole\_nonzero\_false\_dry\_guardrail`



Reason:



\- Phase 33 identified it as the strongest future candidate.

\- It targets a specific observed masked failure mode.

\- `manhole\_nonzero\_valid` had the highest Phase 29 false-dry rate.



Phase 34 should not authorize training yet. It should only formalize thresholds for a possible later pilot.



\## 9. Threshold Philosophy



Thresholds should be conservative and predeclared.



Possible threshold types:



\### No-worse-than-baseline threshold



A metric must not be worse than the chosen baseline.



\### Tolerance-based threshold



A metric may worsen only within a small predeclared tolerance.



\### Improvement-required threshold



The target metric must improve by at least a minimum amount.



\### Trade-off rejection threshold



A pattern of improvement in one proxy metric plus degradation in multiple error metrics triggers rejection.



Phase 34 should avoid arbitrary overfitting. If exact numeric thresholds are difficult to justify, it should write conservative provisional thresholds and label them as pre-pilot thresholds requiring final review.



\## 10. Expected Script



Phase 34 should implement a diagnostic-only threshold formalization script:



`scripts/formalize\_phase34\_pilot\_thresholds.py`



The script should not train or modify model/loss/config code.



It should output:



\- `analysis/phase34\_pilot\_thresholds/baseline\_metric\_table.csv`

\- `analysis/phase34\_pilot\_thresholds/acceptance\_thresholds.csv`

\- `analysis/phase34\_pilot\_thresholds/rejection\_thresholds.csv`

\- `analysis/phase34\_pilot\_thresholds/threshold\_readiness\_status.csv`

\- `analysis/phase34\_pilot\_thresholds/phase34\_threshold\_summary.json`

\- `analysis/phase34\_pilot\_thresholds/phase34\_threshold\_summary.md`



\## 11. Expected Threshold Tables



\### `baseline\_metric\_table.csv`



Columns:



\- metric\_group

\- metric\_name

\- region

\- phase25\_seed42

\- phase27\_seed42

\- phase29\_seed42

\- preferred\_direction

\- reference\_baseline

\- notes



\### `acceptance\_thresholds.csv`



Columns:



\- threshold\_id

\- metric\_group

\- metric\_name

\- region

\- baseline\_reference

\- acceptance\_rule

\- numeric\_threshold

\- threshold\_type

\- required\_for\_pilot\_acceptance

\- rationale



\### `rejection\_thresholds.csv`



Columns:



\- rejection\_id

\- rejection\_rule

\- trigger\_metric\_group

\- trigger\_metric\_name

\- trigger\_region

\- trigger\_condition

\- required\_for\_pilot\_rejection

\- rationale



\### `threshold\_readiness\_status.csv`



Columns:



\- criterion

\- status

\- evidence

\- blocker

\- next\_required\_action



\## 12. Decision Types



Phase 34 should end with one of these decisions.



\### Decision A: `thresholds\_not\_ready`



Use if numeric thresholds cannot be defensibly fixed.



\### Decision B: `thresholds\_formalized\_training\_still\_blocked`



Use if thresholds are formalized but the project still needs a final pilot implementation plan.



\### Decision C: `pilot\_implementation\_plan\_allowed\_next`



Use if thresholds are formalized and the next phase may write a pilot implementation plan.



This still does not mean training is allowed in Phase 34.



\## 13. Expected Decision



The likely expected decision is:



`thresholds\_formalized\_training\_still\_blocked`



or:



`pilot\_implementation\_plan\_allowed\_next`



depending on whether the threshold rules are complete enough.



Training should remain unauthorized in Phase 34.



\## 14. Guardrails



Phase 34 must follow these guardrails:



1\. Do not train.

2\. Do not modify losses.

3\. Do not modify configs.

4\. Do not modify model architecture.

5\. Do not run seed42.

6\. Do not run seed123 or seed202.

7\. Do not perform sweeps.

8\. Do not continue Phase 29.

9\. Do not claim Phase 29 success.

10\. Do not claim strict conservation.

11\. Do not claim full mass conservation.

12\. Do not claim SWE/PINN.

13\. Do not claim hydrodynamic closure.

14\. Keep all conclusions at Level 4+ proxy scope.

15\. Do not authorize training directly from Phase 34.



\## 15. Success Criteria



Phase 34 succeeds if it:



\- fixes baseline metrics for Phase 25 / Phase 27 / Phase 29 seed42;

\- defines acceptance thresholds;

\- defines rejection thresholds;

\- explicitly rejects the Phase 29 trade-off pattern;

\- preserves Level 4+ proxy framing;

\- blocks immediate training;

\- states whether the next phase may write a pilot implementation plan.



\## 16. Immediate Next Step



After committing this plan, implement:



`scripts/formalize\_phase34\_pilot\_thresholds.py`



This script should generate threshold tables and a summary. It must not train or modify model, loss, or config code.

