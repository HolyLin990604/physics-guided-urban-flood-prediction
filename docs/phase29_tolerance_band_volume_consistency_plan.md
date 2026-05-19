\# Phase 29 Tolerance-Band Volume Consistency Redesign Plan



\## 1. Background



Phase 27 tested a conservative `volume\_response\_consistency` loss with an underresponse-only formulation.



The Phase 27 seed42 pilot produced a mixed result:



\- standard test metrics improved relative to Phase 25 seed42;

\- false-dry volume loss decreased;

\- wet-area contraction decreased;

\- peak-depth underprediction decreased;

\- false-wet rate and false-wet volume excess did not increase;

\- however, the primary volume-response objective was not confirmed.



The key Phase 27 failure was:



\- aggregate absolute relative volume bias worsened by `+0.0216934`;

\- mean-step absolute relative volume bias worsened by `+0.0170953`;

\- run-level aggregate relative volume bias shifted from Phase 25 `+0.00296825` to Phase 27 `+0.0246616`.



Phase 28 then diagnosed why this happened.



The Phase 28 conclusion was that Phase 27's volume-response worsening was not mainly caused by threshold-level false-wet expansion and was not primarily caused by already-wet depth amplification.



Instead, the dominant source was dry-or-threshold target-depth-bin volume accumulation.



Key Phase 28 evidence:



\- delta volume bias total = `+6974.12`;

\- Phase 25 relative volume bias = `+0.00296825`;

\- Phase 27 relative volume bias = `+0.0246616`;

\- false-wet volume excess delta = `-184.071`;

\- already-wet amplification = `+1396.20`;

\- dry\_or\_threshold contribution = `+5362.82`, about `76.9%` of total delta volume bias.



Therefore, direct expansion of the Phase 27 underresponse-only loss is not justified.



\## 2. Purpose



The purpose of Phase 29 is to redesign the volume-response loss based on the Phase 28 failure diagnosis.



Phase 29 should not continue the Phase 27 underresponse-only formulation directly.



Instead, Phase 29 should design a tolerance-band volume consistency loss that avoids pushing already near-balanced cases into over-response.



\## 3. Scientific Motivation



Phase 25 had already brought seed42 aggregate relative volume bias close to zero:



`+0.00296825`



When the Phase 27 underresponse-only loss was added, the model was further encouraged to increase predicted volume where prediction volume was below target volume at training time.



However, because the evaluation case was already near-balanced at aggregate scale, this one-sided correction likely pushed the model into over-response, especially through low-depth or near-threshold mass accumulation in dry\_or\_threshold cells.



A better volume-response loss should therefore:



\- avoid penalizing near-zero signed volume bias;

\- avoid forcing near-balanced cases to increase predicted volume;

\- penalize only when relative volume bias falls outside a tolerance band;

\- distinguish under-response and over-response;

\- continue monitoring dry\_or\_threshold-bin accumulation.



\## 4. What Phase 29 Is Not



Phase 29 is not:



\- a full SWE/PINN implementation;

\- a strict mass-conservation model;

\- a full hydrodynamic residual;

\- a Phase 27 weight sweep;

\- a seed123/seed202 confirmation of Phase 27;

\- a return to Phase 10 boundary-weight tuning;

\- a claim of full physical consistency;

\- an attempt to optimize only RMSE or MAE.



Phase 29 is a loss-design refinement stage based on Phase 28 diagnostic evidence.



\## 5. Core Design Question



The central question is:



Can a tolerance-band volume consistency loss reduce meaningful volume-response error without pushing near-balanced cases into over-response or accumulating sub-threshold dry-bin water mass?



\## 6. Proposed Loss Concept



The new loss should be tentatively named:



`tolerance\_band\_volume\_consistency`



The core idea is to compute signed relative volume bias:



`relative\_bias = (V\_pred - V\_target) / (V\_target + eps)`



Then apply no penalty if the absolute relative bias is within a tolerance band:



`abs(relative\_bias) <= tolerance`



Only when the relative bias exceeds the tolerance band should the loss activate.



A simple conceptual form is:



`excess\_bias = max(abs(relative\_bias) - tolerance, 0)`



Then the loss can penalize `excess\_bias`.



\## 7. Asymmetric Penalty Option



Because historical model failure modes include under-response, the loss may use asymmetric weights:



\- stronger penalty for under-response;

\- weaker penalty for over-response;

\- no penalty inside the tolerance band.



For example:



\- if `relative\_bias < -tolerance`, apply `under\_weight`;

\- if `relative\_bias > tolerance`, apply `over\_weight`;

\- otherwise apply zero.



This avoids the Phase 27 problem where an underresponse-only loss keeps pushing already balanced cases upward.



\## 8. Dry-Or-Threshold Guardrail



Phase 28 showed that dry\_or\_threshold cells contributed about 76.9% of the Phase 27 delta volume bias.



Therefore, Phase 29 should include explicit monitoring of dry\_or\_threshold-bin volume accumulation.



The first implementation does not necessarily need a dry-bin penalty, but evaluation must report:



\- dry\_or\_threshold predicted-volume contribution;

\- Phase29 minus Phase25 dry\_or\_threshold volume change;

\- false-wet rate;

\- false-wet volume excess;

\- aggregate relative volume bias;

\- mean-step absolute relative volume bias.



If Phase 29 reduces aggregate bias only by creating new dry-bin artifacts, it should be rejected.



\## 9. Candidate Configuration



The initial Phase 29 pilot should be conservative.



Candidate settings:



\- `enabled = true`

\- `weight = 0.005`

\- `tolerance = 0.02`

\- `under\_weight = 1.0`

\- `over\_weight = 0.5`

\- `eps = 1e-6`

\- `min\_target\_volume = 1e-6`

\- `reduction = mean`



The tolerance value should be treated as a pilot choice, not a final tuned value.



No broad tolerance sweep should be started in Phase 29.



\## 10. Relationship to Existing Losses



Phase 29 should build on Phase 25, not on expanding Phase 27 blindly.



The intended stack is:



\- standard data loss;

\- Phase 10 boundary-band wet/dry consistency;

\- Phase 25 target-wet recall consistency;

\- Phase 29 tolerance-band volume consistency.



The fixed Phase 10 settings remain:



\- `boundary\_band\_pixels = 1`

\- `boundary\_weight = 2.0`



The Phase 25 target-wet recall settings remain:



\- `weight = 0.02`

\- `threshold = 0.05`

\- `temperature = 0.02`

\- `eps = 1e-6`



The Phase 27 underresponse-only loss should not be used as the active loss in the Phase 29 pilot.



\## 11. Pilot Strategy



Phase 29 should begin with a single seed42 pilot only if the implementation passes code and smoke-test checks.



The initial plan should be:



1\. implement config-gated tolerance-band volume consistency;

2\. keep old Phase 27 loss available if already committed, but do not enable it in the Phase 29 config;

3\. create one Phase 29 seed42 config;

4\. run smoke test only;

5\. only then decide whether to train seed42 for 40 epochs;

6\. after training, compare Phase 29 against both Phase 25 and Phase 27 seed42.



No seed123 or seed202 should be run until the seed42 diagnostic result is clearly positive on the primary volume-response objective.



\## 12. Evaluation Metrics



Phase 29 evaluation should include standard metrics:



\- RMSE;

\- MAE;

\- wet/dry IoU;

\- rollout stability;

\- step RMSE std.



It must also include physical and volume-response metrics:



\- aggregate relative volume bias;

\- aggregate absolute relative volume bias;

\- mean-step relative volume bias;

\- mean-step absolute relative volume bias;

\- false-dry volume loss;

\- false-wet volume excess;

\- wet-area contraction;

\- peak-depth underprediction;

\- dry\_or\_threshold volume contribution;

\- depth-bin volume decomposition.



\## 13. Success Criteria



Phase 29 seed42 should be considered promising only if it satisfies:



1\. aggregate absolute relative volume bias improves relative to Phase 27 and preferably remains close to or better than Phase 25;

2\. mean-step absolute relative volume bias does not worsen materially;

3\. dry\_or\_threshold volume accumulation is reduced relative to Phase 27;

4\. false-dry volume loss does not regress substantially;

5\. wet-area contraction does not regress substantially;

6\. false-wet rate and false-wet volume excess do not increase materially;

7\. RMSE and MAE do not degrade materially;

8\. wet/dry IoU does not collapse.



\## 14. Failure Criteria



Phase 29 should be rejected or redesigned if:



\- aggregate volume bias worsens further;

\- dry\_or\_threshold-bin volume accumulation persists or increases;

\- false-wet rate increases substantially;

\- wet/dry IoU collapses;

\- RMSE or MAE degrade materially;

\- improvements occur only through implausible wet-area expansion;

\- the model again fails the primary volume-response objective.



\## 15. Planned Code Changes



Possible implementation path:



\- update `utils/physics\_losses.py`;

\- add a new config-gated term named `tolerance\_band\_volume\_consistency`;

\- create `configs/train\_phase29\_tolerance\_band\_volume\_seed42\_40e.json`;

\- avoid modifying trainers unless strictly necessary.



The existing `PhysicsLossController` structure should allow adding the new loss without changing the training loop.



\## 16. Planned Diagnostics



If training is performed later, Phase 29 should add or reuse comparison diagnostics under:



`analysis/phase29\_tolerance\_band\_volume\_consistency/`



Possible output files:



\- `phase29\_seed42\_by\_step.csv`

\- `phase29\_seed42\_by\_run.csv`

\- `phase29\_seed42\_delta\_vs\_phase25.csv`

\- `phase29\_seed42\_delta\_vs\_phase27.csv`

\- `phase29\_seed42\_depth\_bin\_decomposition.csv`

\- `phase29\_seed42\_summary.json`

\- `phase29\_seed42\_summary.md`



\## 17. Guardrails



Phase 29 must follow these guardrails:



1\. Do not claim strict mass conservation.

2\. Do not claim full SWE/PINN.

3\. Do not claim hydrodynamic closure.

4\. Do not run seed123 or seed202 before seed42 succeeds.

5\. Do not perform broad sweeps.

6\. Do not continue underresponse-only Phase 27 directly.

7\. Do not optimize standard metrics alone.

8\. Do not ignore dry\_or\_threshold-bin volume accumulation.

9\. Do not describe volume proxy as physical volume unless dx/dy are available.

10\. Do not claim success unless the primary volume-response objective improves.



\## 18. Expected Outcome



The expected best-case outcome is a better-designed Level 4 volume-response loss that avoids the Phase 27 over-response failure mode while preserving the standard-metric and under-response-proxy improvements.



The expected risk is that tolerance-band volume consistency may be too weak to influence training or may still interact with wet/dry losses in unexpected ways.



Therefore, Phase 29 should proceed cautiously.



\## 19. Immediate Next Step



After this plan is committed, inspect the current `utils/physics\_losses.py` and Phase 27 implementation. Then ask Codex to implement only the config-gated tolerance-band loss and one seed42 pilot config.



No training should start before the implementation is reviewed and smoke-tested.

