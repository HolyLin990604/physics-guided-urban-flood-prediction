\# Phase 27 Seed42 Conservative Volume-Response Pilot Findings



\## 1. Purpose



Phase 27 tested a conservative Level 4 volume-response consistency refinement on top of the Phase 25 target-wet recall configuration.



The goal was not to implement full SWE/PINN constraints or strict mass conservation. The goal was to test whether a lightweight underresponse-only `volume\_response\_consistency` loss could further reduce systematic aggregate volume under-response while preserving the improvements achieved by Phase 25.



This document summarizes the first narrow seed42 pilot.



\## 2. Phase 27 Intervention



Phase 27 added a new config-gated loss term:



`volume\_response\_consistency`



The loss was implemented in:



`utils/physics\_losses.py`



It was added after `target\_wet\_recall\_consistency` and before `rainfall\_depth\_consistency`.



The pilot config was:



`configs/train\_phase27\_volume\_response\_seed42\_40e.json`



The config was cloned from the Phase 25 seed42 configuration and kept the following settings unchanged:



\- Phase 10 boundary-band settings:

&#x20; - `boundary\_band\_pixels = 1`

&#x20; - `boundary\_weight = 2.0`

\- Phase 25 target-wet recall settings:

&#x20; - `target\_wet\_recall\_consistency.weight = 0.02`

&#x20; - `threshold = 0.05`

&#x20; - `temperature = 0.02`

&#x20; - `eps = 1e-6`



The new Phase 27 volume-response block used:



\- `enabled = true`

\- `weight = 0.005`

\- `underresponse\_only = true`

\- `normalize = true`

\- `min\_target\_volume = 1e-6`

\- `reduction = mean`



\## 3. Training and Test Setup



The Phase 27 pilot was trained for seed42 using:



`configs/train\_phase27\_volume\_response\_seed42\_40e.json`



The output directory was:



`runs/phase27\_volume\_response\_seed42\_40e`



After training, test evaluation was performed using the standard evaluation script.



The Phase 27 seed42 test metrics were:



\- RMSE = `0.0423809813`

\- MAE = `0.0172847716`

\- wet/dry IoU = `0.8128013736`

\- rollout stability = `0.9901222963`

\- step RMSE std = `0.0100226047`



\## 4. Standard Metric Comparison Against Phase 25



The Phase 25 seed42 test metrics were:



\- RMSE = `0.0447470026`

\- MAE = `0.0179394448`

\- wet/dry IoU = `0.8038777207`

\- rollout stability = `0.9895041993`

\- step RMSE std = `0.0106537426`



Phase27 minus Phase25 deltas were:



\- RMSE = `-0.00236602`

\- MAE = `-0.000654673`

\- wet/dry IoU = `+0.00892365`

\- rollout stability = `+0.000618097`

\- step RMSE std = `-0.000631138`



Therefore, Phase 27 seed42 passed the standard-metric guardrail. All listed standard test metrics moved in the preferred direction.



\## 5. Physical and Conservation-Proxy Comparison



The Phase 27 seed42 diagnostic comparison was performed by:



`scripts/compare\_phase27\_volume\_response\_seed42.py`



Outputs were written under:



`analysis/phase27\_conservative\_volume\_response\_consistency/`



The comparison used 38 matched evaluation-test map files and 456 paired step records.



\### 5.1 Positive Indicators



Compared with Phase 25 seed42, Phase 27 improved several under-response-related indicators:



\- false-dry volume loss decreased by `-1.77546`

\- wet-area contraction decreased by `-0.00626303`

\- peak-depth underprediction decreased by `-0.011376`

\- false-wet rate decreased by `-0.000387357`

\- false-wet volume excess decreased by `-0.403664`

\- RMSE and MAE also improved in the paired diagnostic comparison



This means the Phase 27 pilot did not produce the most concerning failure mode of uncontrolled false-wet expansion.



\### 5.2 Failed Primary Volume-Response Objective



However, the primary Phase 27 objective was not achieved.



Aggregate absolute relative volume bias worsened:



\- Phase 25 = `0.00296825`

\- Phase 27 = `0.0246616`

\- Delta = `+0.0216934`



Mean-step absolute relative volume bias also worsened:



\- Phase 25 = `0.240179`

\- Phase 27 = `0.257274`

\- Delta = `+0.0170953`



This means the new loss did not improve the intended volume-response consistency metric.



The run-level aggregate relative volume bias moved from a near-zero value under Phase 25 to a larger positive value under Phase 27. This suggests that the pilot shifted the model toward aggregate over-response rather than further correcting under-response.



\## 6. Interpretation



Phase 27 seed42 is a mixed pilot.



It is positive in the sense that:



\- standard test metrics improved;

\- false-dry volume loss improved;

\- wet-area contraction improved;

\- peak-depth preservation improved;

\- false-wet trade-offs did not increase.



However, it is not a confirmed conservative volume-response improvement because:



\- aggregate absolute relative volume bias worsened;

\- timestep-wise absolute relative volume bias worsened;

\- the primary volume-response objective was not achieved.



Therefore, the pilot should not be interpreted as a successful strong-physics or conservation-constrained refinement.



\## 7. Scientific Conclusion



The strongest defensible conclusion is:



Phase 27 seed42 passed standard-metric guardrails and improved several under-response-related physical indicators, but failed the primary conservative volume-response objective.



The result should be classified as:



`mixed seed42 pilot`



or:



`standard-metric positive, volume-response objective not confirmed`



It should not be described as:



\- full mass conservation;

\- SWE/PINN;

\- strict timestep-wise conservation;

\- confirmed volume-response consistency improvement;

\- ready for three-seed confirmation.



\## 8. Decision



The recommended decision is:



`remain\_seed42\_positive\_only`



Phase 27 should not immediately proceed to seed123 and seed202 confirmation.



A broader multi-seed run would only be justified if the volume-response loss design is revised or if a clearer target metric is selected.



\## 9. Implications for Future Work



The Phase 27 result is useful because it shows that a simple underresponse-only volume-response loss does not necessarily improve test-time aggregate volume consistency.



Possible explanations include:



\- the Phase 25 seed42 aggregate volume bias was already close to zero;

\- the added loss may shift the model toward over-response;

\- training-time batch-level volume loss may not align perfectly with test-time aggregate volume diagnostics;

\- the loss may improve local under-response proxies without improving total volume calibration.



Future refinement should be more cautious and should avoid simply increasing the loss weight.



Potential next directions include:



\- revise the loss to target deviation from zero volume bias rather than only under-response;

\- apply volume-response consistency only to selected high-underresponse cases;

\- introduce a margin or tolerance band around near-zero aggregate volume bias;

\- analyze whether volume over-response is localized in high-depth or already-wet cells;

\- avoid broad sweeps until the failure mechanism is better understood.



\## 10. Guardrails



No further Phase 27 work should claim:



\- strict mass conservation;

\- full SWE/PINN constraints;

\- hydrodynamic flux consistency;

\- universal physical consistency;

\- confirmed multi-seed improvement.



No immediate seed123 or seed202 training is recommended from the current result.



\## 11. Final Statement



Phase 27 seed42 is informative but not conclusive.



It improves standard prediction metrics and several physically meaningful under-response proxies, but it does not achieve the primary conservative volume-response consistency goal.



The current result should be documented and used to revise the loss-design strategy before any multi-seed confirmation.

