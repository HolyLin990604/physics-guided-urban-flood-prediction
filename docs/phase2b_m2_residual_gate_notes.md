\# Phase 2B Milestone 2 Residual Gate Notes



\## Goal



Test whether a more conservative residual rainfall-conditioned gate can improve the cross-seed robustness of Phase 2B.



\## Implementation



A new rainfall conditioning mode was added:



\* `temporal\_gate\_residual`



Key design choices:



\* keep existing `temporal\_gate` unchanged

\* add explicit `residual\_alpha`

\* require `residual\_alpha` explicitly for residual mode

\* keep backward compatibility for old configs



\## Sanity Check



Sanity check passed for:



\* disabled-path compatibility

\* residual mode forward pass

\* `residual\_alpha = 0.0` identity / no-op behavior



Command:



```bash

python scripts/sanity\_check\_phase2b\_temporal\_gate.py --base-config configs/train\_phase2\_loss\_only\_debug.json

```



\## Pilot Configs



Pilot configs were created for:



\* `seed42`

\* `seed202`



with:



\* `hidden\_channels = 16`

\* `residual\_alpha = 0.10`, `0.15`, `0.20`



\## First Tested Version



The first tested version was:



\* `temporal\_gate\_residual`

\* `hidden\_channels = 16`

\* `residual\_alpha = 0.10`



## Current Result

### seed202

Test result for `temporal_gate_residual (h16, alpha=0.10)`:

- RMSE = 0.04248711751087716
- MAE = 0.01679978622613769
- wet/dry IoU = 0.7754691996072468
- rollout stability = 0.9906553751543948

Interpretation:

- did not improve over the previous Phase 2B h16 baseline
- remained clearly worse than Phase 2A on the test set

### seed42

Test result for `temporal_gate_residual (h16, alpha=0.10)`:

- RMSE = 0.037440244598608265
- MAE = 0.015006645533599351
- wet/dry IoU = 0.8165401565401178
- rollout stability = 0.991424908763484

Interpretation:

- did not preserve the original Phase 2B h16 advantage on the test set
- therefore did not justify promotion of the residual gate variant



\## Current Conclusion



At the current stage, `temporal\_gate\_residual (h16, alpha=0.10)` is a meaningful exploratory branch, but it is not promoted to the current main candidate set.



The current main conclusion remains:



\* \*\*Primary candidate: Phase 2A 40e\*\*

\* \*\*Strong alternative: Phase 2B h16 40e\*\*



