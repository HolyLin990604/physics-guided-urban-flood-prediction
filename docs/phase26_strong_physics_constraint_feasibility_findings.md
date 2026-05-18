\# Phase 26 Strong Physics Constraint Feasibility Findings



\## 1. Purpose



Phase 26 was designed to determine whether the current `physics-guided-urban-flood-prediction` project can credibly move from targeted physical-consistency refinement toward stronger physics constraints.



The central question was:



Can the current data and model outputs support conservation-oriented or full SWE/PINN-style strong physics constraints?



This phase was diagnostic only. It did not train new models, modify model architecture, change loss functions, tune Phase 10 parameters, or sweep Phase 25 weights.



\## 2. Current Phase 26 Artifacts



Phase 26 has produced the following committed artifacts:



\- `docs/phase26\_strong\_physics\_constraint\_feasibility\_plan.md`

\- `scripts/audit\_phase26\_physics\_inputs.py`

\- `analysis/phase26\_strong\_physics\_constraint\_feasibility/physics\_input\_audit.json`

\- `analysis/phase26\_strong\_physics\_constraint\_feasibility/physics\_input\_audit.md`

\- `scripts/analyze\_phase26\_conservation\_residual.py`

\- `analysis/phase26\_strong\_physics\_constraint\_feasibility/conservation\_residual\_by\_step.csv`

\- `analysis/phase26\_strong\_physics\_constraint\_feasibility/conservation\_residual\_by\_run.csv`

\- `analysis/phase26\_strong\_physics\_constraint\_feasibility/conservation\_residual\_by\_seed.csv`

\- `analysis/phase26\_strong\_physics\_constraint\_feasibility/conservation\_residual\_phase\_delta.csv`

\- `analysis/phase26\_strong\_physics\_constraint\_feasibility/summary.json`

\- `analysis/phase26\_strong\_physics\_constraint\_feasibility/conservation\_residual\_summary.md`



The analysis compared the Phase 10 recommended margin-aware baseline against the Phase 25 `target\_wet\_recall` refinement.



The compared run pairs were:



\- seed123: `phase10\_margin\_aware\_boundary\_band\_seed123\_40e` vs `phase25\_target\_wet\_recall\_seed123\_40e`

\- seed42: `phase10\_margin\_aware\_boundary\_band\_seed42\_40e` vs `phase25\_target\_wet\_recall\_seed42\_40e`

\- seed202: `phase10\_margin\_aware\_boundary\_band\_seed202\_40e` vs `phase25\_target\_wet\_recall\_seed202\_40e`



\## 3. Physics Input Audit Findings



The Phase 26 input audit found that repository-local `.npy` files were not available in the scanned repository directories.



However, `forecast\_maps.npz` files under `runs/` were available and usable for diagnostic analysis.



The audit inspected representative `forecast\_maps.npz` archives and found:



\- representative flood spatial shape: `\[128, 128]`

\- prediction/target keys available: `prediction`, `target`, `error`

\- Phase 10 evaluation-test prediction/target arrays: supported

\- Phase 25 evaluation-test prediction/target arrays: supported

\- prediction/target shape compatibility: supported

\- Phase 25 target-wet recall runs for seed123, seed42, and seed202: found



The audit also correctly distinguished the Phase 10 recommended baseline from rollback candidates:



\- Phase 10 recommended baseline: `boundary\_weight = 2.0`, also referred to as w20

\- Phase 10 rollback or non-default candidate: `boundary\_weight = 1.5`, also referred to as w15



Therefore, subsequent Phase 26 diagnostics used the recommended Phase 10 w20 baseline, not the w15 rollback setting.



\## 4. Strong Physics Feasibility Classification



The Phase 26 audit produced the following feasibility classification.



\### 4.1 Level 4 Conservation-Oriented Diagnostics



Classification: partially supported.



Reason:



Paired Phase 10 and Phase 25 prediction/target map artifacts are available from evaluation-test outputs. These support aggregate volume-response and conservation-proxy diagnostics.



The current forecast maps allow calculation of:



\- predicted total water-volume proxy

\- target total water-volume proxy

\- aggregate relative volume bias

\- false-dry volume loss

\- false-wet volume excess

\- wet-area contraction

\- peak-depth underprediction

\- RMSE and MAE



However, this remains a proxy-level analysis because strict conservation residuals require physical grid spacing, timestep duration, boundary fluxes, and source/sink terms.



\### 4.2 Level 4 Conservation-Aware Loss Design



Classification: unclear.



Reason:



The existing outputs support diagnostic evidence for a possible future conservative volume-response loss. However, the repository scan did not expose all raw training-time inputs and metadata required for a fully specified conservation-aware loss.



In particular, `dx`, `dy`, explicit `dt`, boundary fluxes, pump/gate operations, and source/sink terms are missing or unclear.



Therefore, a future Phase 27 loss should be conservative in scope. It should not claim strict mass conservation unless the missing information is resolved.



\### 4.3 Level 5 Full SWE/PINN Residual Constraints



Classification: not supported.



Reason:



The current repository evidence does not support full shallow-water-equation or PINN-style residual constraints.



Missing or unclear information includes:



\- velocity fields

\- discharge or flux fields

\- boundary inflow and outflow conditions

\- pump and gate operation records

\- explicit `dx` and `dy`

\- explicit `dt`

\- source/sink, infiltration, or drainage terms

\- shape-compatible DEM or static elevation layer

\- valid computational-domain mask

\- boundary mask



Therefore, Phase 26 should not claim full SWE/PINN capability.



\## 5. Conservation Residual Proxy Diagnostics



The Phase 26 conservation residual proxy analysis processed:



\- map files: 114

\- step records: 2736



The analysis compared Phase 10 w20 baseline outputs with Phase 25 target-wet recall outputs using `evaluation\_test/test\_batch\_\*/forecast\_maps.npz`.



The wet/dry threshold was fixed at `0.05 m`.



The analysis computed:



\- target volume proxy

\- prediction volume proxy

\- relative volume bias

\- aggregate absolute relative volume bias

\- timestep-wise absolute relative volume bias

\- false-dry rate

\- false-wet rate

\- false-dry volume loss

\- false-wet volume excess

\- wet-area contraction

\- peak-depth underprediction

\- RMSE

\- MAE



\## 6. Main Quantitative Findings



\### 6.1 Aggregate Volume Response



Phase 25 improved aggregate absolute relative volume bias across all three seeds.



Phase25 minus Phase10 deltas were:



\- seed123: `-0.064695`

\- seed42: `-0.114739`

\- seed202: `-0.0405758`



This indicates that Phase 25 substantially reduced the aggregate volume-response underestimation observed in Phase 10.



At the phase level:



\- Phase 10 aggregate relative volume bias: `-0.0873309`

\- Phase 25 aggregate relative volume bias: `-0.0120155`



This shows that Phase 25 moved the aggregate predicted water-volume proxy much closer to the target water-volume proxy.



\### 6.2 False-Dry Volume Loss



Phase 25 reduced false-dry volume loss across all three seeds.



Phase25 minus Phase10 deltas were:



\- seed123: `-26.4163`

\- seed42: `-32.2189`

\- seed202: `-13.3703`



This is important because false-dry errors are physically meaningful under-response errors: the target is wet, but the model predicts dry or near-dry cells.



\### 6.3 Wet-Area Contraction



Phase 25 reduced wet-area contraction across all three seeds.



Phase25 minus Phase10 deltas were:



\- seed123: `-0.0848763`

\- seed42: `-0.104508`

\- seed202: `-0.0519941`



This confirms that the target-wet recall refinement reduced the tendency of the model to shrink the predicted inundated area.



\### 6.4 Peak-Depth Preservation



Phase 25 improved peak-depth preservation across all three seeds.



Phase25 minus Phase10 deltas in peak-depth underprediction were:



\- seed123: `-0.00745827`

\- seed42: `-0.0757306`

\- seed202: `-0.00395138`



This suggests that Phase 25 helped reduce local peak-depth underprediction, although the improvement was much stronger for seed42 than for seed123 or seed202.



\### 6.5 Standard Prediction Metrics



Phase 25 also improved standard prediction metrics across all three seeds.



RMSE deltas were:



\- seed123: `-0.00475925`

\- seed42: `-0.013858`

\- seed202: `-0.00217833`



MAE deltas were:



\- seed123: `-0.000988539`

\- seed42: `-0.00347597`

\- seed202: `-0.0000916891`



This confirms that the physical-consistency improvement did not come at the expense of standard predictive accuracy.



\### 6.6 False-Wet Trade-Off



Phase 25 increased false-wet rate and false-wet volume excess slightly.



False-wet-rate deltas were:



\- seed123: `0.00498559`

\- seed42: `0.00234719`

\- seed202: `0.00415345`



False-wet volume excess also increased.



Therefore, Phase 25 should be interpreted as reducing under-response and false-dry behavior while introducing a small false-wet trade-off.



\## 7. Aggregate vs Timestep-Wise Volume Bias



A key Phase 26 finding is that aggregate volume-response improvement and timestep-wise conservation behavior must be distinguished.



The aggregate metric is computed from total predicted volume and total target volume over the full paired evaluation seed or set.



The timestep-wise metric is computed as the mean of timestep-level absolute relative volume bias.



Phase 25 strongly improves aggregate absolute relative volume bias across all three seeds.



However, timestep-wise absolute relative volume bias is mixed:



\- seed42 improves

\- seed123 shows a very small increase

\- seed202 shows a very small increase



Therefore, the conservative conclusion is:



Phase 25 improves aggregate water-volume response and reduces under-response, but it is not a strict timestep-wise conservation solution.



This distinction is important. Phase 25 should not be described as enforcing strict water conservation or solving continuity residuals.



\## 8. Relationship to Phase 25



Phase 25 was not a complete strong-physics solution, but it was a necessary bridge toward stronger physics constraints.



Phase 24 diagnosed physically meaningful failure modes, including:



\- false-dry behavior

\- wet-area contraction

\- peak-depth underprediction

\- volume under-response

\- connectivity loss



Phase 25 converted one diagnosed failure mode into a targeted loss:



\- `target\_wet\_recall\_consistency`



Phase 26 shows that this targeted loss did more than improve pixel-level classification. It also improved aggregate volume-response behavior and reduced false-dry volume loss.



Therefore, Phase 25 can be interpreted as a successful targeted physical-consistency refinement and a valid precursor to stronger conservation-oriented constraints.



\## 9. Scientific Interpretation



The main scientific interpretation is:



Phase 25 reduces systematic under-response in predicted flood-depth fields.



The evidence is not limited to RMSE or IoU. It includes physically meaningful conservation-proxy indicators:



\- lower aggregate absolute relative volume bias

\- lower false-dry volume loss

\- lower wet-area contraction

\- improved peak-depth preservation



This suggests that the model became more physically plausible in terms of water-volume response.



However, the evidence remains diagnostic and proxy-based. It does not prove full mass conservation, full continuity satisfaction, or SWE/PINN residual consistency.



\## 10. Limitations



Phase 26 has several important limitations.



First, the analysis uses water-depth forecast maps only. It does not use velocity, discharge, flux, or boundary-flow data.



Second, aggregate volume is computed as a raster-sum proxy rather than a physically dimensioned volume using known `dx` and `dy`.



Third, explicit timestep length `dt` is missing or unclear.



Fourth, source/sink terms such as drainage, infiltration, pump operation, and gate operation are not available.



Fifth, no shape-compatible DEM/static elevation layer was found in the scanned repository files.



Sixth, the analysis does not compute full shallow-water-equation residuals.



Seventh, Phase 25 improves aggregate water-volume response but does not guarantee timestep-wise conservation.



\## 11. Phase 26 Conclusion



Phase 26 supports the following conclusion:



The current project can credibly support Level 4 conservation-proxy diagnostics. It does not currently support Level 5 full SWE/PINN residual constraints.



Phase 25 is directionally stronger than the Phase 10 recommended baseline on the main conservation-proxy diagnostics, especially:



\- aggregate water-volume response

\- false-dry volume loss

\- wet-area contraction

\- peak-depth preservation

\- RMSE

\- MAE



However, Phase 25 remains a targeted physical-consistency refinement rather than a strict conservation-constrained model.



The strongest defensible statement is:



Phase 25 improves aggregate water-volume response and reduces under-response, but it is not a strict timestep-wise conservation solution.



\## 12. Implications for Phase 27



Phase 27 should not jump directly to full SWE/PINN training.



A reasonable next step would be a conservative volume-response consistency design, if new training is justified.



Possible Phase 27 direction:



\- design a lightweight volume-response consistency loss

\- penalize systematic aggregate volume under-response

\- preserve the Phase 25 false-dry improvements

\- monitor false-wet trade-offs

\- avoid uncontrolled stacking of loss terms

\- avoid claiming strict conservation without `dt`, `dx`, `dy`, boundary fluxes, and source/sink terms



A possible Phase 27 theme is:



Conservative Volume-Response Consistency Refinement.



The purpose would be to move one step beyond target-wet recall while staying within what the available data can actually support.



\## 13. Recommended Next Step



Before starting Phase 27, the project should first finalize Phase 26 by:



\- committing this findings document

\- synchronizing `README.md`

\- synchronizing `docs/project\_status.md`

\- synchronizing `docs/experiment\_index.md`



Only after Phase 26 is fully documented should a Phase 27 training or loss-design stage be considered.

