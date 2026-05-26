\# Phase 36 Manhole False-Dry Guardrail Code / Smoke-Test Implementation Plan



\## 1. Background



Phase 35 completed the implementation plan for a possible future `manhole\_nonzero\_false\_dry\_guardrail` pilot.



The current candidate is:



\- candidate: `manhole\_nonzero\_false\_dry\_guardrail`

\- target region: `manhole\_nonzero\_valid`

\- target metric: `false\_dry\_rate`

\- AT01 threshold: `0.1172229713`

\- training\_authorized: `false`



Phase 36 is the first code/smoke-test implementation phase after Phase 35. It may implement code required for a future pilot, but it must not run training.



\## 2. Purpose



The purpose of Phase 36 is to implement and smoke-test the minimum code components needed for a future `manhole\_nonzero\_false\_dry\_guardrail` seed42 pilot.



Phase 36 should implement:



1\. a config-gated Level 4+ proxy loss term;

2\. a seed42 pilot config draft;

3\. a guardrail checker that reads Phase 34 thresholds;

4\. no-training smoke tests to verify that the loss, config, and guardrail checker work.



\## 3. What Phase 36 Is Not



Phase 36 is not:



\- a training phase;

\- a seed42 40-epoch run;

\- a seed123 or seed202 expansion;

\- a sweep phase;

\- a Phase 29 continuation;

\- a strict conservation implementation;

\- a SWE/PINN implementation;

\- a hydrodynamic closure implementation.



Phase 36 must not run model training.



\## 4. Proposed Code Components



\### 4.1 Loss implementation



Implement a config-gated loss term in:



`utils/physics\_losses.py`



Tentative name:



`manhole\_nonzero\_false\_dry\_guardrail`



The loss should:



\- activate only when explicitly enabled in config;

\- use `manhole` static map as the mask source;

\- optionally combine with valid-domain masking if available;

\- apply only where the target is wet and the prediction is dry or insufficiently wet;

\- penalize false-dry behavior in `manhole\_nonzero\_valid`;

\- remain a Level 4+ static-map-aware proxy loss, not a hydrodynamic closure term.



The loss must be gentle and auxiliary.



\### 4.2 Config draft



Create a seed42-only config draft:



`configs/train\_phase36\_manhole\_false\_dry\_guardrail\_seed42\_40e.json`



This config should be based on the most defensible prior seed42 baseline, likely Phase 25 or Phase 27 depending on existing config availability and consistency.



The config should include:



\- Phase 10 boundary-band settings preserved;

\- Phase 25 target-wet-recall setting preserved if used as baseline;

\- new `manhole\_nonzero\_false\_dry\_guardrail` block added but conservatively weighted;

\- output root clearly named:

&#x20; `runs/phase36\_manhole\_false\_dry\_guardrail\_seed42\_40e`



Important: creating the config does not authorize training.



\### 4.3 Guardrail checker



Create:



`scripts/check\_phase36\_pilot\_guardrails.py`



The checker should read:



\- `analysis/phase34\_pilot\_thresholds/acceptance\_thresholds.csv`

\- `analysis/phase34\_pilot\_thresholds/rejection\_thresholds.csv`

\- `analysis/phase34\_pilot\_thresholds/baseline\_metric\_table.csv`



It should be able to check a future Phase 36 result against:



\- AT01-AT14

\- RT01-RT09



For Phase 36, the checker may run in dry-run mode if no Phase 36 trained output exists.



\### 4.4 Smoke tests



Phase 36 should perform smoke tests only:



\- Python syntax check;

\- JSON config load check;

\- `PhysicsLossController` smoke test with dummy tensors;

\- verify loss appears in returned loss dictionary only when enabled;

\- verify weighted value is finite;

\- verify guardrail checker can read Phase 34 thresholds;

\- verify checker reports no training result available rather than failing.



\## 5. Required Outputs



Expected files:



\- `docs/phase36\_manhole\_false\_dry\_guardrail\_code\_smoke\_plan.md`

\- `utils/physics\_losses.py`

\- `configs/train\_phase36\_manhole\_false\_dry\_guardrail\_seed42\_40e.json`

\- `scripts/check\_phase36\_pilot\_guardrails.py`

\- `analysis/phase36\_manhole\_false\_dry\_guardrail\_code\_smoke/smoke\_test\_summary.json`

\- `analysis/phase36\_manhole\_false\_dry\_guardrail\_code\_smoke/smoke\_test\_summary.md`



\## 6. Acceptance Criteria for Phase 36



Phase 36 succeeds if:



1\. the new loss is config-gated;

2\. the loss is disabled by default unless configured;

3\. dummy-tensor smoke test passes;

4\. the config loads successfully;

5\. the guardrail checker reads Phase 34 thresholds;

6\. the guardrail checker can run in no-result dry-run mode;

7\. no training is executed;

8\. no seed123/seed202 is touched;

9\. no sweep is performed.



\## 7. Guardrails



Phase 36 must follow these guardrails:



\- do not train;

\- do not run seed42 40e;

\- do not run seed123;

\- do not run seed202;

\- do not perform sweeps;

\- do not continue Phase 29;

\- do not claim pilot success;

\- do not claim strict conservation;

\- do not claim full mass conservation;

\- do not claim SWE/PINN;

\- do not claim hydrodynamic closure;

\- keep all claims at Level 4+ proxy scope.



\## 8. Current Decision Boundary



Phase 36 may end with:



`code\_smoke\_ready\_training\_still\_blocked`



or:



`code\_smoke\_failed\_training\_blocked`



Phase 36 must not end with:



`training\_authorized`



Training can only be considered in a later phase after the code smoke test and guardrail checker are reviewed.



\## 9. Immediate Next Step



After this plan is committed, implement the minimal code changes:



1\. update `utils/physics\_losses.py`;

2\. add the seed42 config draft;

3\. add the guardrail checker script;

4\. run no-training smoke tests;

5\. write Phase 36 smoke-test outputs.

