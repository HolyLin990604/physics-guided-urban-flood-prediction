\# Phase 31 Physics Input Recovery and Strong-Constraint Readiness Audit Plan



\## 1. Background



Phase 30 concluded that the current project has reached a Level 4 conservation-proxy / physical-consistency-guided surrogate position.



The project can currently support:



\- reliability-aware warning support;

\- physical-consistency diagnosis;

\- conservation-proxy evaluation;

\- failure-mode interpretation;

\- applicability-boundary communication.



However, the project cannot yet support:



\- strict mass conservation;

\- full hydrodynamic closure;

\- SWE/PINN residual consistency;

\- Level 5 strong physics.



The main reason is that the current repository evidence does not clearly expose the full physical state, forcing, boundary, and grid information needed for stronger physics constraints.



Therefore, Phase 31 should not continue Phase 27/29 volume-response loss tuning. Instead, it should audit whether more physical inputs can be recovered from the local dataset, repository artifacts, metadata, static maps, and existing evaluation outputs.



\## 2. Purpose



The purpose of Phase 31 is to perform a physics-input recovery and strong-constraint readiness audit.



The central question is:



Can the current repository and local UrbanFlood24 Lite data support stronger structured physical constraints beyond Level 4 proxy diagnostics?



Phase 31 should answer whether the project can move toward:



\- Level 4+ structured proxy constraints;

\- masked / domain-aware physical consistency;

\- topography-aware consistency;

\- boundary-aware diagnostics;

\- rainfall-time-aligned consistency;



or whether it must remain at Level 4 conservation-proxy diagnostics because key inputs are still missing.



\## 3. What Phase 31 Is Not



Phase 31 is not:



\- a model training phase;

\- a new loss-design phase;

\- a seed expansion phase;

\- a Phase 27 or Phase 29 continuation;

\- a tolerance or weight sweep;

\- a full SWE/PINN implementation;

\- a strict mass-conservation phase;

\- a model architecture modification phase.



Phase 31 should not train models, modify loss functions, modify configs, or run seed123/seed202.



\## 4. Key Questions



Phase 31 should answer:



1\. Are raw `flood.npy`, `rainfall.npy`, and static map arrays available locally?

2\. Is there a shape-compatible DEM/static elevation layer aligned with 128 × 128 flood maps?

3\. Can static map channels be identified as DEM, imperviousness, manhole density, or other physical descriptors?

4\. Can `dt` be inferred from flood/rainfall sequence alignment?

5\. Can `dx` and `dy` be recovered from metadata, coordinate information, grid extent, or dataset documentation?

6\. Can a valid-domain mask be constructed from flood/static data?

7\. Can a boundary mask be constructed from the valid-domain mask or flood-domain extent?

8\. Are velocity, flux, discharge, boundary inflow/outflow, pump/gate operations, drainage, infiltration, or source/sink terms available?

9\. Can the current project support Level 4+ structured physical constraints?

10\. Does the evidence continue to rule out Level 5 SWE/PINN constraints?



\## 5. Input Sources To Inspect



Phase 31 should inspect:



\- repository-local files;

\- config files;

\- dataset adapter code;

\- static map loading code;

\- existing `runs/\*\*/evaluation\_test/\*\*/forecast\_maps.npz`;

\- existing `analysis/phase26\_strong\_physics\_constraint\_feasibility/`;

\- existing Phase 24-30 documents;

\- local dataset path if referenced in configs;

\- UrbanFlood24 Lite directory if available from config paths.



Potential relevant paths include:



\- `configs/`

\- `data/`

\- `datasets/`

\- `utils/`

\- `scripts/`

\- `runs/`

\- `analysis/phase26\_strong\_physics\_constraint\_feasibility/`

\- local UrbanFlood24 Lite data directory referenced by training configs



\## 6. Planned Scripts



Phase 31 may create diagnostic-only scripts:



\- `scripts/audit\_phase31\_dataset\_physics\_inputs.py`

\- `scripts/inspect\_phase31\_static\_maps.py`

\- `scripts/build\_phase31\_domain\_boundary\_masks.py`

\- `scripts/summarize\_phase31\_physics\_readiness.py`



These scripts should be read-only except for writing outputs under:



`analysis/phase31\_physics\_input\_recovery\_readiness/`



\## 7. Expected Outputs



Expected output directory:



`analysis/phase31\_physics\_input\_recovery\_readiness/`



Expected outputs:



\- `physics\_input\_inventory.json`

\- `physics\_input\_inventory.md`

\- `static\_map\_channel\_summary.csv`

\- `static\_map\_shape\_compatibility.csv`

\- `domain\_boundary\_mask\_summary.csv`

\- `time\_alignment\_summary.csv`

\- `strong\_constraint\_readiness\_summary.json`

\- `phase31\_physics\_readiness\_findings.md`



Optional outputs:



\- example valid-domain mask figure;

\- example boundary mask figure;

\- static map channel preview figure.



Figures should only be generated if useful and if the scripts can do so without introducing new dependencies or unclear assumptions.



\## 8. Readiness Levels



Phase 31 should classify the project into one of the following readiness levels.



\### Level 4: Conservation-Proxy Diagnostics Only



Supported when only predicted and target flood-depth rasters are available.



Allowed:



\- aggregate volume-response proxy;

\- timestep-wise volume-response proxy;

\- false-dry / false-wet proxy diagnostics;

\- depth-bin proxy analysis.



Not allowed:



\- strict mass conservation;

\- flux-based continuity;

\- SWE/PINN residuals.



\### Level 4+: Structured Physical Proxy Constraints



Possible if some aligned physical inputs can be recovered, such as:



\- DEM/static elevation;

\- valid-domain mask;

\- boundary mask;

\- explicit dt;

\- clear static-map semantics;

\- rainfall-time alignment.



Allowed examples:



\- domain-mask-aware consistency;

\- topography-aware plausibility diagnostics;

\- boundary-aware wet/dry diagnostics;

\- rainfall-response consistency within valid domain;

\- dry-threshold guarded proxy constraints.



Still not allowed:



\- full mass conservation;

\- full SWE/PINN;

\- hydrodynamic closure.



\### Level 5: Full SWE/PINN Residual Constraints



Only possible if the project has:



\- water depth;

\- velocity or flux fields;

\- boundary inflow/outflow;

\- source/sink terms;

\- pump/gate operations if relevant;

\- dx/dy;

\- dt;

\- DEM/topography;

\- valid-domain and boundary masks;

\- consistent hydrodynamic metadata.



Phase 26 previously found Level 5 unsupported. Phase 31 should verify whether this remains true.



\## 9. Success Criteria



Phase 31 succeeds if it produces a clear, evidence-based answer to:



\- what physical inputs are available;

\- what physical inputs are missing;

\- whether DEM/static elevation is shape-compatible;

\- whether domain/boundary masks can be constructed;

\- whether dt/dx/dy can be inferred;

\- whether stronger Level 4+ constraints are feasible;

\- whether Level 5 SWE/PINN remains unsupported;

\- what the next technical stage should be.



\## 10. Guardrails



Phase 31 must follow these guardrails:



1\. Do not train models.

2\. Do not modify model architecture.

3\. Do not modify loss functions.

4\. Do not modify training configs.

5\. Do not run seed123 or seed202.

6\. Do not perform any tolerance or weight sweep.

7\. Do not claim strict mass conservation.

8\. Do not claim full SWE/PINN capability.

9\. Do not claim full hydrodynamic closure.

10\. Do not infer missing physical variables without evidence.

11\. Do not treat depth-raster volume proxies as true physical volume unless dx/dy are available.

12\. Do not create new strong-physics loss before readiness is audited.



\## 11. Expected Decision Types



Possible Phase 31 final decisions include:



\### Decision A: Level 4 Only



The project remains limited to conservation-proxy diagnostics because key physical inputs remain unavailable.



\### Decision B: Level 4+ Feasible



The project can support structured physical proxy constraints using recovered DEM/static maps, domain masks, boundary masks, and time alignment.



\### Decision C: Level 5 Still Unsupported



Full SWE/PINN remains unsupported due to missing velocity/flux, boundary, source/sink, dx/dy, or hydrodynamic state variables.



\### Decision D: Data Recovery Required



The project cannot proceed technically until external dataset documentation or raw hydrodynamic model outputs are added.



\## 12. Likely Next Stage After Phase 31



If Phase 31 finds Level 4+ feasible, the likely next stage is:



Phase 32 — Domain-/Topography-Aware Physical Consistency Design



Possible directions:



\- domain-mask-aware depth and wet/dry consistency;

\- boundary-aware wet/dry diagnostics;

\- topography-aware ponding plausibility;

\- rainfall-response consistency with valid-domain masking;

\- dry-threshold guarded volume proxy with explicit mask safeguards.



If Phase 31 confirms Level 4 only, the next stage should not be new training. It should instead clarify data requirements or prepare manuscript/project narrative.



\## 13. Immediate Next Step



After this plan is committed, implement the first diagnostic script:



`scripts/audit\_phase31\_dataset\_physics\_inputs.py`



This script should inventory repository and dataset-level physical inputs and write:



\- `analysis/phase31\_physics\_input\_recovery\_readiness/physics\_input\_inventory.json`

\- `analysis/phase31\_physics\_input\_recovery\_readiness/physics\_input\_inventory.md`



No training or model modification should occur.

