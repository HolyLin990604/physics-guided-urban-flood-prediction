\# Phase 30 Strong Physics Boundary Synthesis Plan



\## 1. Background



The project has progressed from rapid urban flood-depth prediction toward reliability-aware and physically interpretable flood-warning support.



Recent phases have focused on physical consistency and strong-physics feasibility:



\- Phase 24 diagnosed physical consistency failure modes, including false-dry behavior, wet-area contraction, peak-depth underprediction, connectivity loss, and volume under-response.

\- Phase 25 introduced target-wet recall consistency and improved false-dry behavior and wet-region preservation across three seeds.

\- Phase 26 audited strong-physics feasibility and found that Level 4 conservation-proxy diagnostics are partially supported, while Level 5 full SWE/PINN residual constraints are not supported by the current repository evidence.

\- Phase 27 tested an underresponse-only volume-response loss. It improved standard metrics and several local under-response proxies on seed42, but failed the primary volume-response objective.

\- Phase 28 diagnosed why Phase 27 failed and found that the worsening was dominated by dry\_or\_threshold low-depth / near-threshold volume accumulation.

\- Phase 29 tested tolerance-band volume consistency. It partially repaired the Phase 27 volume-bias and dry\_or\_threshold accumulation problem, but the trade-off was unacceptable.



Therefore, the project should now pause further volume-response loss expansion and synthesize the current strong-physics boundary.



\## 2. Purpose



The purpose of Phase 30 is to summarize what the project has and has not achieved regarding strong physical constraints.



Phase 30 should clarify:



1\. What level of physical consistency has been reached.

2\. What evidence supports that conclusion.

3\. Why the current model should not be described as strict mass-conservative, full hydrodynamic, SWE/PINN, or fully physics-constrained.

4\. Why Phase 27 and Phase 29 should not be expanded directly.

5\. What additional data and modeling information would be required for stronger physical constraints.

6\. What research directions remain scientifically justified.



\## 3. Phase 30 Position



Phase 30 is a synthesis and decision phase.



It is not:



\- a training phase;

\- a new loss-design phase;

\- a seed expansion phase;

\- a tolerance or weight sweep;

\- a model architecture phase;

\- a full SWE/PINN implementation;

\- a strict mass-conservation phase.



Phase 30 should not generate new model predictions or modify training code.



\## 4. Core Scientific Question



The central question is:



Given the evidence from Phases 24-29, what is the strongest defensible claim about the project's current physical consistency level?



The expected answer is likely:



The current model has advanced to a reliability-aware, physical-consistency-guided surrogate with Level 4 conservation-proxy diagnostics and targeted physical failure-mode analysis, but it has not reached Level 5 full physics, strict mass conservation, or SWE/PINN residual consistency.



\## 5. Evidence Chain To Synthesize



\### Phase 24: Physical Consistency Deepening



Phase 24 showed that high-risk cases were not only statistically worse but also physically less consistent.



Important findings included:



\- stronger false-dry behavior;

\- wet-area contraction;

\- peak-depth underprediction;

\- wet-connectivity loss;

\- volume under-response;

\- strong linkage between risk score and physical failure proxies.



Phase 24 established the need for physically interpretable diagnostics beyond RMSE/MAE.



\### Phase 25: Target-Wet Recall Refinement



Phase 25 introduced a targeted physical-consistency refinement focused on wet-region recall.



It improved standard metrics and under-response proxies across seed123, seed42, and seed202.



Important improvements included:



\- reduced false-dry behavior;

\- reduced wet-area contraction;

\- improved peak-depth preservation;

\- improved aggregate volume-response proxies.



However, Phase 25 was not a full hydrodynamic consistency solution and did not implement mass conservation or SWE residuals.



\### Phase 26: Strong Physics Feasibility Audit



Phase 26 audited what level of strong physics could be supported by the current repository evidence.



The conclusion was:



\- Level 4 conservation-proxy diagnostics: partially supported;

\- Level 4 conservation-aware loss design: uncertain;

\- Level 5 full SWE/PINN residual constraints: not supported.



Missing or unclear requirements included:



\- velocity or flux fields;

\- boundary inflow/outflow;

\- pump/gate operations;

\- dx/dy spatial resolution;

\- source/sink or drainage terms;

\- shape-compatible DEM/static elevation;

\- complete hydrodynamic state variables.



Phase 26 established the boundary between feasible proxy diagnostics and unsupported full-physics claims.



\### Phase 27: Underresponse-Only Volume Response Pilot



Phase 27 tested a conservative volume-response consistency loss on seed42.



Positive findings:



\- standard metrics improved relative to Phase 25 seed42;

\- false-dry volume loss decreased;

\- wet-area contraction decreased;

\- peak-depth underprediction decreased;

\- false-wet rate and false-wet volume excess did not increase.



Negative finding:



\- aggregate absolute relative volume bias worsened;

\- mean-step absolute relative volume bias worsened;

\- run-level aggregate relative volume bias moved from Phase 25 near-zero bias toward over-response.



Conclusion:



Phase 27 was a mixed seed42 pilot and should not be expanded directly.



\### Phase 28: Volume-Response Failure Diagnosis



Phase 28 diagnosed why Phase 27 failed the primary volume-response objective.



Key finding:



The worsening was not mainly caused by threshold-level false-wet expansion and was not primarily caused by already-wet amplification.



The dominant source was dry\_or\_threshold target-depth-bin low-depth / near-threshold volume accumulation.



This supported stopping direct expansion of the Phase 27 underresponse-only loss.



\### Phase 29: Tolerance-Band Volume Consistency Pilot



Phase 29 tested a tolerance-band redesign on seed42.



Positive findings relative to Phase 27:



\- aggregate absolute relative volume bias improved;

\- mean-step absolute relative volume bias improved;

\- dry\_or\_threshold contribution decreased.



Negative findings relative to Phase 27:



\- all listed standard metrics worsened;

\- false-dry volume loss worsened;

\- false-wet volume excess worsened;

\- peak-depth underprediction worsened;

\- aggregate bias remained far from Phase 25 near-zero bias.



Conclusion:



Phase 29 partially repaired the Phase 27 volume-response failure mode but produced unacceptable trade-offs. It should remain seed42-only pending revision.



\## 6. Boundary Statement To Develop



Phase 30 should develop a clear boundary statement:



The current project supports physical-consistency diagnosis, reliability screening, warning-rule guidance, and Level 4 conservation-proxy analysis, but it does not yet support strict physical conservation or full hydrodynamic residual enforcement.



The model should be described as:



\- physics-guided;

\- reliability-aware;

\- physically diagnosed;

\- conservation-proxy evaluated;

\- warning-oriented;

\- applicability-boundary aware.



The model should not be described as:



\- strictly mass-conservative;

\- full physics-constrained;

\- SWE/PINN-based;

\- hydrodynamically closed;

\- guaranteed physically consistent;

\- universally reliable.



\## 7. Data Requirements For Stronger Physics



Phase 30 should list what would be needed to move beyond Level 4 proxy diagnostics toward stronger physical constraints.



Potential requirements include:



\- aligned water depth and velocity fields;

\- flux or discharge fields;

\- boundary inflow and outflow conditions;

\- pump/gate operation time series;

\- drainage and source/sink terms;

\- infiltration or runoff generation terms;

\- explicit dx/dy grid spacing;

\- explicit dt;

\- shape-compatible DEM/static elevation;

\- valid-domain and boundary masks;

\- hydrodynamic solver metadata;

\- scenario-level forcing and boundary metadata.



Without these, full SWE/PINN residual constraints should not be claimed.



\## 8. Decisions To Make



Phase 30 should decide:



1\. Whether Phase 27/29 volume-response losses should remain documented mixed pilots.

2\. Whether seed123/seed202 expansion should remain blocked.

3\. Whether additional loss redesign should pause until a new plan is justified.

4\. Whether the next stage should be manuscript/research-narrative consolidation rather than new training.

5\. Whether the project should state a clear strong-physics boundary in README and manuscript text.



\## 9. Expected Outputs



Main outputs:



\- `docs/phase30\_strong\_physics\_boundary\_synthesis\_plan.md`

\- `docs/phase30\_strong\_physics\_boundary\_synthesis.md`



Optional outputs:



\- `analysis/phase30\_strong\_physics\_boundary/strong\_physics\_phase24\_29\_summary.csv`

\- `analysis/phase30\_strong\_physics\_boundary/strong\_physics\_boundary\_summary.json`



The optional structured outputs are only needed if they help summarize the evidence cleanly. No model training should be performed.



\## 10. Guardrails



Phase 30 must follow these guardrails:



1\. Do not train a model.

2\. Do not modify model architecture.

3\. Do not modify loss functions.

4\. Do not modify training configs.

5\. Do not run seed123 or seed202.

6\. Do not perform tolerance or weight sweeps.

7\. Do not claim strict mass conservation.

8\. Do not claim full SWE/PINN capability.

9\. Do not claim full hydrodynamic closure.

10\. Do not overstate Phase 27 or Phase 29 as successful.

11\. Do not optimize only RMSE/MAE.

12\. Do not ignore the trade-offs identified in Phase 27 and Phase 29.



\## 11. Success Criteria



Phase 30 succeeds if it produces a defensible synthesis that:



\- explains the Phase 24-29 evidence chain;

\- defines the current strong-physics boundary;

\- clarifies what is supported and what is not supported;

\- prevents overclaiming;

\- provides a clear next-step decision;

\- identifies what data would be needed for stronger physics;

\- gives the project a coherent physical-consistency narrative.



\## 12. Likely Next Stage After Phase 30



The preferred next stage after Phase 30 is not another immediate training phase.



A likely next stage is:



Phase 31 — Strong-Physics Feasibility and Loss-Design Narrative for Manuscript / README



This would translate the Phase 24-30 evidence into a research narrative explaining:



\- why physical consistency matters;

\- how reliability diagnosis exposed failure modes;

\- why simple physical loss terms are insufficient;

\- what current data can and cannot support;

\- what is needed for stronger physics in future work.



A technical loss redesign stage should only resume after the Phase 30 boundary synthesis justifies it.

