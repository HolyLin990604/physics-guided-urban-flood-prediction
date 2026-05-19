\# Phase 29 Seed42 Tolerance-Band Volume Consistency Findings



\## 1. Purpose



Phase 29 tested a tolerance-band volume consistency redesign after the Phase 28 diagnosis showed that the Phase 27 underresponse-only volume loss should not be directly expanded.



The goal was not to implement strict mass conservation, SWE/PINN residual constraints, or full hydrodynamic closure.



The goal was narrower:



\- reduce the Phase 27 aggregate volume over-response;

\- reduce dry\_or\_threshold low-depth volume accumulation;

\- preserve the Phase 25/27 gains in standard metrics and under-response-related physical proxies;

\- determine whether the tolerance-band formulation is suitable for multi-seed confirmation.



\## 2. Background



Phase 27 introduced an underresponse-only `volume\_response\_consistency` loss. It improved standard test metrics and several physical proxies on seed42, but it failed the primary volume-response objective.



Phase 28 diagnosed why Phase 27 failed. The main finding was that the Phase 27 volume-bias worsening was dominated by dry\_or\_threshold target-depth-bin volume accumulation, not by threshold-level false-wet expansion or already-wet amplification.



Key Phase 28 evidence:



\- Phase 27 delta volume bias total: `+6974.12`

\- Phase 25 relative volume bias: `+0.00296825`

\- Phase 27 relative volume bias: `+0.0246616`

\- false-wet volume excess delta: `-184.071`

\- already-wet amplification: `+1396.20`

\- dry\_or\_threshold contribution: `+5362.82`, about `76.9%` of total delta volume bias



Therefore, Phase 29 redesigned the volume-response loss as a tolerance-band formulation.



\## 3. Phase 29 Intervention



Phase 29 added a new config-gated loss term:



`tolerance\_band\_volume\_consistency`



The loss was implemented in:



`utils/physics\_losses.py`



It was added without removing the previous Phase 27 `volume\_response\_consistency` loss, so Phase 27 remains reproducible.



The Phase 29 seed42 pilot config was:



`configs/train\_phase29\_tolerance\_band\_volume\_seed42\_40e.json`



The output directory was:



`runs/phase29\_tolerance\_band\_volume\_seed42\_40e`



The Phase 29 config kept the Phase 10 and Phase 25 settings unchanged:



\- `boundary\_band\_pixels = 1`

\- `boundary\_weight = 2.0`

\- `target\_wet\_recall\_consistency.weight = 0.02`

\- `target\_wet\_recall\_consistency.threshold = 0.05`

\- `target\_wet\_recall\_consistency.temperature = 0.02`



The new tolerance-band volume block used:



\- `enabled = true`

\- `weight = 0.005`

\- `tolerance = 0.02`

\- `under\_weight = 1.0`

\- `over\_weight = 0.5`

\- `eps = 1e-6`

\- `min\_target\_volume = 1e-6`

\- `reduction = mean`



The old Phase 27 `volume\_response\_consistency` was not enabled in the Phase 29 config.



\## 4. Training and Test Metrics



Phase 29 seed42 was trained for 40 epochs and evaluated on the test split.



The Phase 29 seed42 test metrics were:



\- RMSE = `0.0443854521`

\- MAE = `0.0178462429`

\- wet/dry IoU = `0.8016409529`

\- rollout stability = `0.9895110601`

\- step RMSE std = `0.0106412431`



For comparison, Phase 25 seed42 test metrics were:



\- RMSE = `0.0447470026`

\- MAE = `0.0179394448`

\- wet/dry IoU = `0.8038777207`

\- rollout stability = `0.9895041993`

\- step RMSE std = `0.0106537426`



Phase 27 seed42 test metrics were:



\- RMSE = `0.0423809813`

\- MAE = `0.0172847716`

\- wet/dry IoU = `0.8128013736`

\- rollout stability = `0.9901222963`

\- step RMSE std = `0.0100226047`



\## 5. Standard Metric Interpretation



Relative to Phase 25, Phase 29 was mixed but close:



\- RMSE improved slightly: `-0.000361551`

\- MAE improved slightly: `-0.0000932019`

\- wet/dry IoU declined slightly: `-0.00223677`

\- rollout stability was nearly unchanged: `+0.00000686`

\- step RMSE std improved slightly: `-0.0000124994`



Relative to Phase 27, Phase 29 was weaker on all listed standard metrics:



\- RMSE worsened by `+0.00200447`

\- MAE worsened by `+0.000561471`

\- wet/dry IoU decreased by `-0.0111604`

\- rollout stability decreased by `-0.000611236`

\- step RMSE std worsened by `+0.000618638`



Therefore, Phase 29 does not preserve the full standard-metric advantage of Phase 27.



\## 6. Volume-Response Diagnostic Comparison



A three-way diagnostic comparison was performed using:



`scripts/compare\_phase29\_tolerance\_band\_volume\_seed42.py`



The compared runs were:



\- Phase 25: `runs/phase25\_target\_wet\_recall\_seed42\_40e`

\- Phase 27: `runs/phase27\_volume\_response\_seed42\_40e`

\- Phase 29: `runs/phase29\_tolerance\_band\_volume\_seed42\_40e`



Outputs were written under:



`analysis/phase29\_tolerance\_band\_volume\_consistency/`



The diagnostic processed:



\- 57 map files

\- 1368 step records



\## 7. Positive Phase 29 Findings



Phase 29 partially repaired the Phase 27 volume-response failure mode.



Compared with Phase 27, aggregate absolute relative volume bias improved:



\- Phase 27: `0.0246616`

\- Phase 29: `0.019464`

\- Delta: `-0.00519769`



Mean-step absolute relative volume bias also improved:



\- Phase 27: `0.257274`

\- Phase 29: `0.230447`

\- Delta: `-0.0268275`



The dry\_or\_threshold target-depth-bin predicted-volume contribution decreased:



\- Phase 27: `0.137662`

\- Phase 29: `0.131428`



This confirms that the Phase 28 diagnosis was useful. The tolerance-band formulation partially reduced the dry/threshold-bin volume accumulation that caused the Phase 27 volume-response failure.



\## 8. Negative Phase 29 Findings



Despite the partial volume-response repair, Phase 29 introduced substantial trade-offs relative to Phase 27.



False-dry volume loss worsened:



\- Phase 27: `5409.72`

\- Phase 29: `5964.83`

\- Delta: `+555.113`



False-wet volume excess worsened:



\- Phase 27: `7750.32`

\- Phase 29: `8289.77`

\- Delta: `+539.44`



False-dry rate worsened:



\- Phase 27: `0.0689175`

\- Phase 29: `0.0739891`

\- Delta: `+0.00507161`



False-wet rate worsened:



\- Phase 27: `0.01585`

\- Phase 29: `0.0169892`

\- Delta: `+0.00113924`



Peak-depth underprediction worsened:



\- Phase 27: `0.128045`

\- Phase 29: `0.134593`

\- Delta: `+0.0065482`



Phase 29 also remained far from the Phase 25 near-zero aggregate volume bias:



\- Phase 25 aggregate relative volume bias: `0.00296825`

\- Phase 29 aggregate relative volume bias: `0.019464`



Therefore, Phase 29 did not recover the near-balanced aggregate volume behavior of Phase 25.



\## 9. Scientific Interpretation



Phase 29 confirms that tolerance-band volume consistency is directionally relevant.



It partially reduces the Phase 27 aggregate volume over-response and dry\_or\_threshold volume accumulation.



However, the current configuration is not acceptable as a confirmed improvement because it sacrifices too much of the Phase 27 advantage in:



\- standard metrics;

\- false-dry reduction;

\- false-wet control;

\- peak-depth preservation.



The result should therefore be interpreted as a mixed tolerance-band pilot rather than a successful refinement.



\## 10. Decision



The recommended decision is:



`remain\_seed42\_only\_pending\_revision`



Phase 29 should not proceed to seed123 or seed202 confirmation.



The current result does not justify:



\- multi-seed confirmation;

\- tolerance/weight sweep;

\- strict conservation claims;

\- full mass-conservation claims;

\- SWE/PINN claims;

\- declaring tolerance-band volume consistency successful.



\## 11. Implications for Future Work



Phase 29 provides useful evidence for future loss redesign.



The tolerance-band concept partially addresses the dry\_or\_threshold volume accumulation identified in Phase 28, but the current implementation and configuration are not sufficient.



Possible future directions include:



\- revising the tolerance value only after a new plan;

\- testing a weaker tolerance-band weight only after a new plan;

\- adding an explicit dry\_or\_threshold-bin guardrail;

\- using a selective loss applied only to high-underresponse cases;

\- combining tolerance-band volume consistency with safeguards against false-dry and false-wet regression;

\- pausing volume-response loss development if trade-offs remain unacceptable.



No next experiment should begin without a new plan.



\## 12. Guardrails



The following guardrails remain active:



1\. Do not run seed123 or seed202 based on the current Phase 29 result.

2\. Do not perform a tolerance or weight sweep without a new plan.

3\. Do not claim strict timestep-wise conservation.

4\. Do not claim full mass conservation.

5\. Do not claim SWE/PINN residual consistency.

6\. Do not describe depth-raster volume proxies as physical volume unless dx/dy are available.

7\. Do not treat Phase 29 as a successful strong-physics result.

8\. Do not optimize only standard metrics.

9\. Do not ignore dry\_or\_threshold volume accumulation.

10\. Do not ignore the regression in false-dry and false-wet indicators.



\## 13. Final Conclusion



Phase 29 seed42 is a mixed tolerance-band pilot.



It partially repairs the Phase 27 volume-bias and dry/threshold-bin accumulation problem, but the current trade-off is not acceptable for multi-seed confirmation.



The strongest defensible conclusion is:



Phase 29 validates the relevance of tolerance-band volume consistency as a redesign direction, but the tested seed42 configuration remains unresolved because it improves volume-response proxies relative to Phase 27 while sacrificing standard metrics and key physical-error proxies.



The current status should remain:



`seed42 only, pending revision`

