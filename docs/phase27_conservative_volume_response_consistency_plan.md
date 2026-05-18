\# Phase 27 Conservative Volume-Response Consistency Refinement Plan



\## 1. Background



Phase 26 completed the Strong Physics Constraint Feasibility Audit and Conservation-Proxy Diagnostics.



The Phase 26 conclusion was conservative and important:



\- Level 4 conservation-oriented diagnostics are partially supported.

\- Level 4 conservation-aware loss design remains unclear but is potentially feasible if designed conservatively.

\- Level 5 full SWE/PINN residual constraints are not supported by the currently available repository evidence.



Phase 26 also showed that Phase 25 target-wet recall consistency improves aggregate water-volume response relative to the Phase 10 recommended baseline. However, Phase 25 is not a strict timestep-wise conservation solution.



Therefore, Phase 27 should not jump to full SWE/PINN or strict mass-conservation enforcement. Instead, Phase 27 should design and test a conservative Level 4 volume-response consistency refinement that stays within the available data support.



\## 2. Purpose



The purpose of Phase 27 is to move one step beyond Phase 25 target-wet recall consistency by adding a lightweight, conservative volume-response consistency objective.



The goal is not to enforce full hydrodynamic conservation.



The goal is to reduce systematic aggregate volume under-response while preserving the improvements already achieved by Phase 25.



\## 3. Scientific Motivation



Phase 24 identified physically meaningful failure modes in high-risk cases:



\- false-dry behavior;

\- wet-area contraction;

\- peak-depth underprediction;

\- connectivity loss;

\- volume under-response.



Phase 25 converted one diagnosed failure mode into a targeted loss:



\- `target\_wet\_recall\_consistency`



Phase 25 improved false-dry behavior, wet-area contraction, aggregate volume response, and standard prediction metrics across three seeds.



Phase 26 then confirmed that Phase 25 improves aggregate water-volume response and reduces under-response, but does not provide strict timestep-wise conservation.



Phase 27 is motivated by the following question:



Can a conservative volume-response consistency term further reduce systematic under-response without causing excessive false-wet expansion or degrading standard prediction metrics?



\## 4. What Phase 27 Is Not



Phase 27 must not be misinterpreted as any of the following:



\- not a full SWE/PINN model;

\- not a strict mass-conservation model;

\- not a full continuity-equation residual;

\- not a hydrodynamic flux-consistency model;

\- not a Phase 10 boundary-weight retuning stage;

\- not a Phase 25 weight sweep;

\- not an uncontrolled stacking of physics losses;

\- not an attempt to optimize only RMSE or MAE.



Phase 27 is a conservative Level 4 physical-consistency refinement based on available depth-field outputs and training targets.



\## 5. Working Hypothesis



The working hypothesis is:



A small, underresponse-focused volume-response consistency loss can reduce systematic volume underestimation and preserve Phase 25 wet-region improvements, but it may increase false-wet behavior if weighted too strongly.



Therefore, Phase 27 should begin with a narrow, low-risk pilot rather than a broad sweep.



\## 6. Proposed Loss Concept



The planned loss is tentatively named:



\- `volume\_response\_consistency`



or more specifically:



\- `underresponse\_volume\_consistency`



The loss should operate on predicted and target flood-depth tensors during training.



The basic idea is:



\- compute non-negative predicted depth;

\- compute non-negative target depth;

\- aggregate the predicted and target depth over spatial dimensions;

\- penalize only the case where predicted volume response is lower than target volume response;

\- normalize by target volume plus a small epsilon;

\- apply the loss only where target volume is meaningful.



This makes the loss conservative: it targets under-response without directly encouraging uncontrolled overprediction.



\## 7. Candidate Mathematical Form



Let:



\- `pred` be the predicted water-depth tensor;

\- `target` be the target water-depth tensor;

\- `eps` be a numerical stability constant.



Use non-negative depths:



\- `pred\_pos = max(pred, 0)`

\- `target\_pos = max(target, 0)`



Aggregate over spatial dimensions:



\- `V\_pred = sum(pred\_pos)`

\- `V\_target = sum(target\_pos)`



Define under-response:



\- `U = max(V\_target - V\_pred, 0)`



Define normalized under-response loss:



\- `L\_volume = mean(U / (V\_target + eps))`



Optionally, apply the loss only when `V\_target` is larger than a minimum active-volume threshold.



This should be treated as a volume-response proxy, not physical volume in cubic meters, unless `dx` and `dy` are explicitly available.



\## 8. Initial Configuration



The initial pilot should be conservative.



Suggested configuration:



\- `enabled = true`

\- `weight = 0.005`

\- `eps = 1e-6`

\- `underresponse\_only = true`

\- `min\_target\_volume = 1e-6`

\- `normalize = true`



The weight should start lower than the Phase 25 target-wet recall weight because Phase 26 showed false-wet trade-offs already exist.



A second candidate weight, if needed later, may be `0.01`, but Phase 27 should not begin with a broad weight sweep.



\## 9. Relationship to Existing Losses



Phase 27 should build on the Phase 25 configuration rather than replacing it.



The intended loss stack is:



\- standard data loss;

\- existing Phase 10 boundary-band wet/dry consistency;

\- Phase 25 `target\_wet\_recall\_consistency`;

\- Phase 27 conservative `volume\_response\_consistency`.



The fixed Phase 10 settings should remain:



\- `boundary\_band\_pixels = 1`

\- `boundary\_weight = 2.0`



The Phase 25 target-wet recall settings should remain unchanged initially:



\- `weight = 0.02`

\- `threshold = 0.05`

\- `temperature = 0.02`

\- `eps = 1e-6`



Phase 27 should not tune these existing settings unless there is strong evidence of instability.



\## 10. Pilot Design



The first Phase 27 pilot should be narrow.



Recommended first pilot:



\- base configuration: Phase 25 target-wet recall

\- add conservative volume-response consistency

\- use `weight = 0.005`

\- use the same three project seeds if full validation becomes justified

\- start with one diagnostic seed if compute time is limited



Recommended first diagnostic seed:



\- `seed42` if the goal is favorable-case guardrail checking;

\- `seed123` if the goal is stress-testing the original wet/dry trade-off seed.



A reasonable order is:



1\. implement the loss and config support;

2\. create one pilot config;

3\. train one seed for 40 epochs only if implementation checks pass;

4\. evaluate using standard test metrics;

5\. run Phase 25-style aligned physical comparison;

6\. run Phase 26-style conservation-proxy comparison;

7\. decide whether three-seed confirmation is justified.



\## 11. Evaluation Metrics



Phase 27 should be evaluated using both standard metrics and physical-consistency diagnostics.



Standard metrics:



\- RMSE;

\- MAE;

\- wet/dry IoU;

\- rollout stability;

\- step RMSE standard deviation.



Physical-consistency metrics:



\- aggregate absolute relative volume bias;

\- timestep-wise absolute relative volume bias;

\- false-dry rate;

\- false-dry volume loss;

\- false-wet rate;

\- false-wet volume excess;

\- wet-area contraction;

\- peak-depth underprediction;

\- connectivity-loss indicator, if available;

\- Phase 26 conservation-proxy deltas.



\## 12. Success Criteria



A Phase 27 pilot should be considered promising only if it satisfies the following conditions relative to Phase 25:



1\. aggregate absolute relative volume bias improves or remains clearly better than Phase 10;

2\. false-dry volume loss does not regress substantially;

3\. wet-area contraction does not regress substantially;

4\. RMSE and MAE do not degrade materially;

5\. wet/dry IoU does not show a major decline;

6\. false-wet rate and false-wet volume excess do not increase beyond an acceptable trade-off;

7\. peak-depth underprediction does not worsen substantially.



The most important guardrail is avoiding a solution that simply increases predicted wet area everywhere.



\## 13. Failure Criteria



A Phase 27 pilot should be rejected or revised if it shows:



\- large false-wet increase;

\- obvious over-expansion of wet areas;

\- RMSE or MAE degradation;

\- wet/dry IoU degradation;

\- loss of the Phase 25 false-dry improvement;

\- unstable training;

\- improved aggregate volume response only because of physically implausible overprediction.



\## 14. Planned Code Changes



Possible files to modify:



\- `utils/physics\_losses.py`

\- training loss assembly code, if needed;

\- configuration files under `configs/`;

\- evaluation or comparison scripts only if required.



Possible new config:



\- `configs/train\_phase27\_volume\_response\_seed42\_40e.json`

\- or `configs/train\_phase27\_volume\_response\_seed123\_40e.json`



Possible new analysis outputs:



\- `analysis/phase27\_conservative\_volume\_response\_consistency/`



Possible new comparison script only if existing scripts cannot be reused:



\- `scripts/compare\_phase27\_volume\_response.py`



However, Phase 27 should reuse existing Phase 25 and Phase 26 comparison machinery where possible.



\## 15. Planned Artifacts



Expected Phase 27 artifacts may include:



\- `docs/phase27\_conservative\_volume\_response\_consistency\_plan.md`

\- updated `utils/physics\_losses.py`

\- one or more Phase 27 config files;

\- Phase 27 run outputs under `runs/`;

\- comparison outputs under `analysis/phase27\_conservative\_volume\_response\_consistency/`;

\- `docs/phase27\_conservative\_volume\_response\_consistency\_findings.md`



\## 16. Guardrails



Phase 27 must follow these guardrails:



1\. Do not return to Phase 10 boundary-weight tuning.

2\. Do not sweep Phase 25 target-wet recall weight.

3\. Do not claim full SWE/PINN residual constraints.

4\. Do not claim strict timestep-wise conservation.

5\. Do not claim physical volume in cubic meters unless `dx` and `dy` are available.

6\. Do not start broad parameter sweeps.

7\. Do not optimize only RMSE/MAE.

8\. Do not allow volume-response loss to create uncontrolled false-wet expansion.

9\. Do not proceed to three-seed confirmation until a one-seed pilot is technically and scientifically justified.



\## 17. Expected Phase 27 Outcome



The expected best-case outcome is:



A conservative volume-response consistency term further reduces aggregate volume under-response while preserving the Phase 25 improvements in false-dry behavior, wet-area contraction, and standard prediction metrics.



The expected risk is:



The model may increase false-wet rate or wet-area over-expansion if the volume-response term is too strong.



Therefore, Phase 27 should be framed as a cautious Level 4 refinement rather than a final strong-physics solution.



\## 18. Immediate Next Step



After this plan is committed, the next step is to inspect the existing loss implementation and configuration structure, especially:



\- `utils/physics\_losses.py`

\- existing Phase 25 configuration files;

\- training loss assembly code.



Only after confirming the implementation path should Codex implement the `volume\_response\_consistency` loss.

