\# Phase 32 Domain-/Boundary-Aware Physical Consistency Design Plan



\## 1. Background



Phase 31 moved the project from a Level 4 conservation-proxy / physical-consistency-guided surrogate position to a stronger Level 4+ structured physical proxy diagnostics position.



Phase 31 recovered and verified several physical inputs and diagnostic supports:



\- raw flood, rainfall, and static arrays are available;

\- `absolute\_DEM.npy`, `impervious.npy`, and `manhole.npy` are available;

\- static maps are shape-compatible with 128 x 128 flood maps;

\- train/test geodata are consistent;

\- `DEM = 100` likely represents a high / invalid / no-data candidate;

\- `absolute\_DEM < 99` supports valid-domain mask construction;

\- valid-domain, invalid/high, boundary-ring, and interior masks can be constructed;

\- sample-to-location mapping for forecast maps can be recovered from adjacent `summary.json` metadata;

\- masked physical error diagnostics are fully supported.



However, Phase 31 also confirmed that Level 5 strong physics remains unsupported because the repository still lacks:



\- aligned velocity or flux fields;

\- boundary inflow/outflow fields;

\- source/sink, drainage, or operation fields;

\- explicit `dx/dy`;

\- explicit physical `dt`;

\- complete hydrodynamic state variables.



Therefore, Phase 32 should not attempt full SWE/PINN, strict mass conservation, or full hydrodynamic closure. Instead, it should design a Level 4+ domain-/boundary-aware physical consistency strategy based on the recovered masks and masked error diagnostics.



\## 2. Purpose



The purpose of Phase 32 is to design the next physically informed refinement strategy using the Phase 31 recovered masks and masked diagnostics.



Phase 32 should answer:



1\. Which physical regions should guide future diagnostics or losses?

2\. Which masks are reliable enough for Level 4+ structured proxy constraints?

3\. Which Phase 29 failure modes should be avoided?

4\. Whether the next step should be diagnostic-only, loss-design-only, or a narrow pilot.

5\. What stop/go criteria must be satisfied before any training is justified.



Phase 32 is a design phase first. It should not immediately train a model or modify losses without a documented design decision.



\## 3. What Phase 32 Is Not



Phase 32 is not:



\- a direct training phase;

\- a Phase 29 continuation;

\- a tolerance-band weight sweep;

\- a seed123 / seed202 expansion;

\- a full SWE/PINN implementation;

\- a strict conservation implementation;

\- a hydrodynamic closure attempt;

\- a model architecture search.



Phase 32 should not begin by modifying `utils/physics\_losses.py` or adding a new config. It should first define the design logic, target regions, diagnostics, guardrails, and stop/go criteria.



\## 4. Evidence From Phase 31



Phase 31 produced four important diagnostic results.



\### 4.1 Static-map readiness



The project now has shape-compatible static maps:



\- `absolute\_DEM.npy`

\- `impervious.npy`

\- `manhole.npy`



These maps are 128 x 128 and consistent across train/test geodata.



\### 4.2 Domain and boundary masks



Phase 31 supports:



\- `valid\_domain\_mask = absolute\_DEM < 99`

\- `invalid\_or\_high\_mask = absolute\_DEM >= 99`

\- `boundary\_ring\_mask`

\- `interior\_mask`

\- `high\_impervious\_valid`

\- `manhole\_nonzero\_valid`



Train/test masks are `consistent\_equal`.



\### 4.3 Masked physical error diagnostics



Phase 31 recovered sample-to-location mapping from adjacent:



`evaluation\_test/test\_batch\_\*/summary.json`



using:



`metadata.location`



This enabled masked diagnostics over Phase 25, Phase 27, and Phase 29.



\### 4.4 Phase 29 masked-diagnostic interpretation



Phase 29 improved valid-domain masked relative volume-bias proxy relative to Phase 27:



\- Phase 27: `0.0169359`

\- Phase 29: `0.0115344`



However, Phase 29 worsened most other valid-domain masked metrics:



\- RMSE worsened from `0.0460827` to `0.0480984`

\- MAE worsened from `0.0183693` to `0.0190492`

\- false-dry rate worsened from `0.0689175` to `0.0739891`

\- false-wet rate worsened from `0.0181923` to `0.0194308`

\- false-dry volume-loss proxy worsened from `3575.36` to `4027.38`

\- false-wet volume-excess proxy worsened from `5263.67` to `5690.27`



Region-specific Phase 29 concerns:



\- `manhole\_nonzero\_valid` has the highest Phase 29 false-dry rate: `0.131298`

\- `high\_impervious\_valid` has the highest Phase 29 false-wet rate: `0.0239894`



Therefore, Phase 32 should not simply extend the Phase 29 tolerance-band idea. It must explicitly guard against false-dry, false-wet, and region-specific degradation.



\## 5. Core Design Question



The central Phase 32 question is:



Can we design a Level 4+ domain-/boundary-aware physical consistency strategy that targets physically meaningful regions while avoiding the trade-offs observed in Phase 27 and Phase 29?



This strategy should be based on:



\- valid-domain-only diagnostics;

\- boundary-ring wet/dry reliability;

\- high-impervious false-wet control;

\- manhole-proximal false-dry diagnostics;

\- dry-threshold guarded proxy refinement;

\- explicit stop/go rules before training.



\## 6. Candidate Design Directions



Phase 32 should compare the following possible directions.



\### Direction A: Diagnostic-only extension



Use Phase 31 masks to produce richer diagnostics without modifying training.



Possible outputs:



\- per-location masked diagnostics;

\- per-scenario masked diagnostics;

\- boundary-ring false-dry rankings;

\- high-impervious false-wet rankings;

\- manhole-proximal false-dry rankings;

\- valid-domain/interior/boundary-ring error maps.



This is the lowest-risk option.



\### Direction B: Domain-mask-aware consistency design



Design future losses or diagnostics that only apply to valid-domain cells:



`valid\_domain = absolute\_DEM < 99`



This avoids treating invalid/high/no-data regions as physical target domains.



Potential target:



\- valid-domain depth consistency;

\- valid-domain wet/dry consistency;

\- valid-domain volume-proxy diagnostics.



Risk:



\- may still reproduce Phase 27/29 volume trade-offs if not paired with false-dry and false-wet guardrails.



\### Direction C: Boundary-ring-aware wet/dry design



Use `boundary\_ring\_mask` to explicitly monitor or constrain wet/dry classification near domain boundaries.



Potential target:



\- reduce boundary-ring false-dry;

\- reduce boundary-ring peak-depth underprediction;

\- avoid creating boundary-ring false-wet expansion.



Risk:



\- boundary cells may be physically ambiguous without real boundary flux information.



\### Direction D: High-impervious false-wet control



Phase 31 found that `high\_impervious\_valid` has the highest Phase 29 false-wet rate.



Potential target:



\- monitor high-impervious false-wet expansion;

\- design a false-wet guardrail for high-impervious cells;

\- avoid over-expansion caused by volume-response style losses.



Risk:



\- imperviousness is a runoff proxy, not a direct hydraulic state variable.



\### Direction E: Manhole-proximal false-dry diagnostics



Phase 31 found that `manhole\_nonzero\_valid` has the highest Phase 29 false-dry rate.



Potential target:



\- diagnose false-dry behavior near sparse drainage/manhole indicators;

\- test whether drainage-proxy areas are systematically underpredicted;

\- define a manhole-region false-dry guardrail.



Risk:



\- manhole maps are sparse indicators, not full drainage-capacity fields.



\### Direction F: Dry-threshold guarded proxy refinement



Phase 28 showed that dry\_or\_threshold low-depth accumulation caused Phase 27 volume-response failure. Phase 29 partly repaired volume bias but worsened other masked errors.



A future design could explicitly guard dry/near-threshold cells.



Potential target:



\- prevent low-depth accumulation in dry\_or\_threshold regions;

\- avoid worsening false-wet and false-dry errors;

\- combine volume-bias proxy with wet/dry guardrails.



Risk:



\- still proxy-based and not strict conservation.



\## 7. Preferred Phase 32 Strategy



The preferred Phase 32 strategy should be conservative:



1\. Do not train immediately.

2\. First define a domain-/boundary-aware physical consistency design.

3\. Use Phase 31 masked diagnostics to choose target regions.

4\. Define guardrail metrics before any new loss is proposed.

5\. Only then decide whether a narrow seed42 pilot is justified.



The likely preferred technical route is:



\*\*Phase 32A: Diagnostic Design and Guardrail Specification\*\*



followed only later, if justified, by:



\*\*Phase 32B: Narrow seed42 pilot\*\*



Phase 32A should be completed before any code change to loss functions.



\## 8. Proposed Phase 32A Outputs



Phase 32A should produce:



\- `docs/phase32\_domain\_boundary\_aware\_physical\_consistency\_plan.md`

\- `docs/phase32\_domain\_boundary\_aware\_design.md`

\- optional diagnostic summary:

&#x20; - `analysis/phase32\_domain\_boundary\_aware\_design/design\_summary.json`

&#x20; - `analysis/phase32\_domain\_boundary\_aware\_design/guardrail\_metrics.csv`



If a diagnostic script is needed, it should be read-only and should not train.



Possible script:



\- `scripts/design\_phase32\_domain\_boundary\_guardrails.py`



\## 9. Proposed Guardrail Metrics



Before any new loss or training, Phase 32 should define guardrail metrics.



Minimum guardrails:



\### Standard metrics



\- RMSE must not worsen substantially.

\- MAE must not worsen substantially.

\- wet/dry IoU must not decline substantially.

\- rollout stability must not degrade.



\### Valid-domain metrics



\- valid-domain RMSE

\- valid-domain MAE

\- valid-domain false-dry rate

\- valid-domain false-wet rate

\- valid-domain relative volume-bias proxy



\### Boundary-ring metrics



\- boundary-ring false-dry rate

\- boundary-ring false-wet rate

\- boundary-ring peak-depth underprediction

\- boundary-ring absolute relative volume-bias proxy



\### High-impervious metrics



\- high-impervious false-wet rate

\- high-impervious false-wet volume-excess proxy

\- high-impervious RMSE / MAE



\### Manhole-region metrics



\- manhole-nonzero false-dry rate

\- manhole-nonzero false-dry volume-loss proxy

\- manhole-nonzero peak-depth underprediction



\### Dry-threshold metrics



\- dry\_or\_threshold predicted-volume contribution

\- false-wet expansion near dry threshold

\- low-depth accumulation proxy



\## 10. Stop/Go Rules Before Training



Any future training pilot should require explicit stop/go criteria.



A future seed42 pilot may be justified only if the design satisfies:



1\. It targets a clearly diagnosed failure mode.

2\. It has a specific region/mask target.

3\. It has explicit false-dry and false-wet guardrails.

4\. It does not repeat the Phase 27 underresponse-only failure.

5\. It does not repeat the Phase 29 tolerance-band trade-off.

6\. It defines standard metric acceptance thresholds.

7\. It remains Level 4+ proxy framed.

8\. It does not claim SWE/PINN or strict conservation.



If these are not satisfied, the project should remain diagnostic-only.



\## 11. Potential Future Loss Concepts



Phase 32 should only discuss future loss concepts at design level.



Possible concepts:



\### Concept 1: Valid-domain-only guarded consistency



Apply proxy consistency only inside valid-domain cells.



\### Concept 2: Boundary-ring wet/dry guardrail



Apply a monitoring or auxiliary guardrail to boundary-ring false-dry / false-wet behavior.



\### Concept 3: High-impervious false-wet penalty



Prevent spurious false-wet expansion in high-impervious valid-domain cells.



\### Concept 4: Manhole-region false-dry monitor



Monitor or gently penalize false-dry behavior in manhole-nonzero valid-domain cells.



\### Concept 5: Dry-threshold accumulation guard



Prevent near-threshold dry-region accumulation from dominating volume-response proxy behavior.



These are only candidate concepts. Phase 32 should not implement them before the design is finalized.



\## 12. Expected Decision Types



Phase 32 should end with one of the following decisions:



\### Decision A: Diagnostic-only continuation



The safest conclusion is to keep using the recovered masks for diagnostics and not train.



\### Decision B: Design ready, no training yet



A domain-/boundary-aware design is ready, but training should wait for further review.



\### Decision C: Narrow seed42 pilot justified



A narrow seed42 pilot is justified only if guardrails are explicit and the objective is sharply defined.



\### Decision D: Additional data required



The next technical step requires additional physical data, metadata, or hydrodynamic outputs.



\## 13. Level Boundary



Phase 32 must preserve the Level 4+ / Level 5 boundary.



Supported:



\- static-map-aware diagnostics;

\- domain-aware diagnostics;

\- boundary-aware diagnostics;

\- masked physical proxy metrics;

\- region-specific failure-mode analysis.



Unsupported:



\- strict mass conservation;

\- full mass conservation;

\- SWE/PINN;

\- hydrodynamic closure;

\- flux-based residuals;

\- boundary-condition closure.



\## 14. Guardrails



Phase 32 must follow these guardrails:



1\. Do not train before the design is finalized.

2\. Do not modify losses before the design is finalized.

3\. Do not run seed123 or seed202.

4\. Do not perform sweeps.

5\. Do not claim Phase 29 success.

6\. Do not claim strict conservation.

7\. Do not claim full mass conservation.

8\. Do not claim SWE/PINN.

9\. Do not claim full hydrodynamic closure.

10\. Do not treat invalid/high DEM cells as physical target domain.

11\. Do not treat impervious or manhole maps as full hydraulic boundary/source-sink fields.

12\. Keep all claims at Level 4+ proxy level.



\## 15. Immediate Next Step



After this plan is committed, Phase 32 should create:



`docs/phase32\_domain\_boundary\_aware\_design.md`



This document should formalize:



\- candidate target regions;

\- guardrail metrics;

\- stop/go thresholds;

\- whether a narrow pilot is justified;

\- what not to do next.



No training should occur before this design document is complete.

