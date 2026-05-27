\# Phase 37 Seed42 Training Authorization Review Plan



\## 1. Background



Phase 36 completed the code/smoke-test implementation for the `manhole\_nonzero\_false\_dry\_guardrail` candidate.



Phase 36 implemented:



\- config-gated `manhole\_nonzero\_false\_dry\_guardrail` support in `utils/physics\_losses.py`;

\- seed42 config draft: `configs/train\_phase36\_manhole\_false\_dry\_guardrail\_seed42\_40e.json`;

\- guardrail checker: `scripts/check\_phase36\_pilot\_guardrails.py`;

\- smoke-test outputs under `analysis/phase36\_manhole\_false\_dry\_guardrail\_code\_smoke/`.



Phase 36 smoke-test result:



\- `config\_loaded = true`

\- `loss\_smoke\_passed = true`

\- `guardrail\_checker\_dry\_run\_passed = true`

\- `training\_authorized = false`

\- `training\_executed = false`

\- `seed42\_run\_executed = false`

\- `seed123\_seed202\_executed = false`

\- `decision = code\_smoke\_ready\_training\_still\_blocked`



Phase 37 is therefore required to review whether the Phase 36 seed42 config may be executed in a later training phase.



\## 2. Purpose



The purpose of Phase 37 is to perform an explicit seed42 training authorization review.



Phase 37 should answer:



Can the project authorize a single seed42 training run using:



`configs/train\_phase36\_manhole\_false\_dry\_guardrail\_seed42\_40e.json`



under the Phase 34 acceptance and rejection thresholds?



Phase 37 itself should not run training. It should only determine whether a later phase may train.



\## 3. What Phase 37 Is Not



Phase 37 is not:



\- a training phase;

\- a seed42 execution phase;

\- a seed123 or seed202 expansion;

\- a sweep phase;

\- a loss redesign phase;

\- a config redesign phase;

\- a Phase 29 continuation;

\- a strict conservation implementation;

\- a SWE/PINN implementation;

\- a hydrodynamic closure attempt.



Phase 37 must not execute:



`python scripts/train\_model.py --config configs/train\_phase36\_manhole\_false\_dry\_guardrail\_seed42\_40e.json`



unless a future phase is explicitly created for training.



\## 4. Inputs



Phase 37 should review the following artifacts.



\### Phase 34 threshold artifacts



\- `analysis/phase34\_pilot\_thresholds/baseline\_metric\_table.csv`

\- `analysis/phase34\_pilot\_thresholds/acceptance\_thresholds.csv`

\- `analysis/phase34\_pilot\_thresholds/rejection\_thresholds.csv`

\- `analysis/phase34\_pilot\_thresholds/threshold\_readiness\_status.csv`

\- `analysis/phase34\_pilot\_thresholds/phase34\_threshold\_summary.json`

\- `analysis/phase34\_pilot\_thresholds/phase34\_threshold\_summary.md`



\### Phase 35 pilot plan



\- `docs/phase35\_manhole\_false\_dry\_guardrail\_pilot\_plan.md`



\### Phase 36 code/smoke artifacts



\- `docs/phase36\_manhole\_false\_dry\_guardrail\_code\_smoke\_plan.md`

\- `docs/phase36\_manhole\_false\_dry\_guardrail\_code\_smoke\_findings.md`

\- `utils/physics\_losses.py`

\- `configs/train\_phase36\_manhole\_false\_dry\_guardrail\_seed42\_40e.json`

\- `scripts/check\_phase36\_pilot\_guardrails.py`

\- `analysis/phase36\_manhole\_false\_dry\_guardrail\_code\_smoke/smoke\_test\_summary.json`

\- `analysis/phase36\_manhole\_false\_dry\_guardrail\_code\_smoke/smoke\_test\_summary.md`

\- `analysis/phase36\_manhole\_false\_dry\_guardrail\_code\_smoke/guardrail\_checker\_dry\_run.json`

\- `analysis/phase36\_manhole\_false\_dry\_guardrail\_code\_smoke/guardrail\_checker\_dry\_run.md`



\## 5. Authorization Review Questions



Phase 37 should check:



1\. Does the Phase 36 config exist?

2\. Can the Phase 36 config be loaded?

3\. Does the config point to a clearly named output directory?

4\. Is the new loss config-gated?

5\. Did the loss smoke test pass?

6\. Did the guardrail checker dry-run pass?

7\. Are Phase 34 acceptance thresholds available?

8\. Are Phase 34 rejection thresholds available?

9\. Are Phase 25 / Phase 27 / Phase 29 baseline metrics fixed?

10\. Is training restricted to seed42 only?

11\. Are seed123 and seed202 explicitly blocked?

12\. Are sweeps explicitly blocked?

13\. Is Phase 29 continuation explicitly blocked?

14\. Is the claim scope restricted to Level 4+ proxy diagnostics?

15\. Is post-training guardrail checking mandatory?



\## 6. Required Authorization Conditions



A future seed42 training run may be authorized only if all of the following are satisfied:



1\. Phase 36 config exists and loads.

2\. Phase 36 loss smoke test passed.

3\. Phase 36 guardrail checker dry-run passed.

4\. Phase 34 AT01–AT14 are available.

5\. Phase 34 RT01–RT09 are available.

6\. Phase 34 baseline table contains Phase 25 / Phase 27 / Phase 29 seed42 references.

7\. The pilot remains seed42-only.

8\. seed123 and seed202 are blocked.

9\. sweeps are blocked.

10\. Phase 29 continuation is blocked.

11\. The training result must be evaluated using Phase 34 guardrail checker.

12\. Any result triggering RT01–RT09 must be rejected.

13\. All claims remain Level 4+ proxy scoped.



\## 7. Expected Script



Phase 37 should implement a diagnostic-only authorization review script:



`scripts/review\_phase37\_seed42\_training\_authorization.py`



This script must not train.



It should read:



\- Phase 34 threshold files;

\- Phase 36 smoke-test summary;

\- Phase 36 guardrail checker dry-run summary;

\- Phase 36 config draft;

\- Phase 36 findings.



It should output:



\- `analysis/phase37\_seed42\_training\_authorization/authorization\_checklist.csv`

\- `analysis/phase37\_seed42\_training\_authorization/training\_authorization\_summary.json`

\- `analysis/phase37\_seed42\_training\_authorization/training\_authorization\_summary.md`



\## 8. Expected Output Fields



The authorization summary should include:



\- `config\_exists`

\- `config\_loads`

\- `loss\_smoke\_passed`

\- `guardrail\_checker\_dry\_run\_passed`

\- `acceptance\_thresholds\_available`

\- `rejection\_thresholds\_available`

\- `baseline\_metrics\_available`

\- `seed42\_only`

\- `seed123\_seed202\_blocked`

\- `sweeps\_blocked`

\- `phase29\_continuation\_blocked`

\- `level4\_plus\_scope\_preserved`

\- `post\_training\_guardrail\_check\_required`

\- `training\_authorized\_next\_phase`



\## 9. Possible Decisions



Phase 37 may end with one of these decisions.



\### Decision A: `training\_not\_authorized`



Use if required inputs are missing or guardrail structures are incomplete.



\### Decision B: `seed42\_training\_authorized\_next\_phase`



Use only if the review confirms that a single seed42 run may be executed in the next phase.



This does not mean Phase 37 itself trains.



\### Decision C: `authorization\_review\_incomplete`



Use if evidence is insufficient or contradictory.



\## 10. Expected Decision



Given Phase 36 smoke results, the likely expected decision is:



`seed42\_training\_authorized\_next\_phase`



if all checks pass.



However, Phase 37 must remain conservative and should only authorize the next phase if all required conditions are satisfied.



\## 11. Training Command Under Review



The command under review is:



`python scripts/train\_model.py --config configs/train\_phase36\_manhole\_false\_dry\_guardrail\_seed42\_40e.json`



Phase 37 should document this command but must not execute it.



\## 12. Post-Training Requirements If Authorized



If Phase 37 authorizes a future seed42 run, the next phase must:



1\. run only the reviewed seed42 config;

2\. evaluate on test split;

3\. run `scripts/check\_phase36\_pilot\_guardrails.py` after evaluation;

4\. compare against Phase 34 thresholds;

5\. reject the result if any RT01–RT09 condition is triggered;

6\. avoid seed123 / seed202 until seed42 passes;

7\. avoid sweeps;

8\. preserve Level 4+ proxy wording.



\## 13. Guardrails



Phase 37 must follow these guardrails:



\- do not train;

\- do not run seed42;

\- do not run seed123;

\- do not run seed202;

\- do not perform sweeps;

\- do not continue Phase 29;

\- do not modify losses;

\- do not modify configs;

\- do not modify architecture;

\- do not claim pilot success;

\- do not claim strict conservation;

\- do not claim full mass conservation;

\- do not claim SWE/PINN;

\- do not claim hydrodynamic closure;

\- keep all claims at Level 4+ proxy scope.



\## 14. Success Criteria



Phase 37 succeeds if it:



\- reviews all required artifacts;

\- creates an explicit authorization checklist;

\- states whether a future seed42 training run is authorized;

\- preserves all Phase 34 rejection rules;

\- keeps training out of Phase 37 itself;

\- defines exact next-step requirements if training is authorized.



\## 15. Immediate Next Step



After committing this plan, implement:



`scripts/review\_phase37\_seed42\_training\_authorization.py`



This script should perform the authorization review and generate the checklist and summary. It must not execute training.

