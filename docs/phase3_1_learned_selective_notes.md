\# Phase 3.1 Learned Selective Notes



\## Goal



Test whether the current M3 partial-gate idea can be upgraded into a more structured selective-modulation mechanism by replacing the fixed channel-block selection rule with a learnable channel-wise selector.



\## Motivation



M3 showed that selective partial modulation is more robust than broader gating.



However, the current M3 implementation still uses a fixed channel-block rule:



\- a fixed subset of bottleneck channels is modulated

\- the conditioned fraction is manually specified

\- the selected channels are structurally simple but not very interpretable



Phase 3.1 was introduced to test a more structured alternative:



\- keep the successful residual rainfall-conditioned gate idea

\- keep the same conservative modulation budget

\- replace the fixed partial mask with a learnable channel-wise selector



\## Implemented Mode



A new rainfall conditioning mode was added:



\- `temporal\_gate\_residual\_learned\_selective`



Key design choices:



\- keep existing modes unchanged:

&#x20; - `temporal\_gate`

&#x20; - `temporal\_gate\_residual`

&#x20; - `temporal\_gate\_residual\_partial`

\- add a lightweight learnable channel-wise selector

\- preserve the residual rainfall-conditioned gate pathway from M3

\- initialize the selector from the current `conditioned\_fraction` prior

\- keep initialization very close to current M3 partial behavior



\## Sanity Check



Sanity check passed for the learned-selective mode.



Verified items include:



\- output shape unchanged

\- forward pass finite

\- `residual\_alpha = 0.0` remains identity / no-op

\- initialization stays very close to the current M3 partial-gate path



Command:



```bash

python scripts/sanity\_check\_phase2b\_temporal\_gate.py

```



Key sanity-check values:



\- `learned\_selective\_mode\_output\_shape = \[2, 12, 1, 32, 32]`

\- `learned\_selective\_mode\_finite = true`

\- `learned\_selective\_residual\_alpha\_zero\_max\_abs\_diff = 0.0`

\- `learned\_selective\_residual\_alpha\_zero\_is\_identity = true`

\- `learned\_selective\_init\_max\_abs\_diff\_vs\_partial = 1.1682510375976562e-05`

\- `learned\_selective\_selector\_prior\_max\_abs\_diff = 0.00033535013790242374`



\## Pilot Config



A minimal pilot config was created first for:



\- `seed202`



with:



\- `hidden\_channels = 16`

\- `residual\_alpha = 0.10`

\- `conditioned\_fraction = 0.25`



A second follow-up check was then run for:



\- `seed42`



using the same setting.



\## Test Results



\### seed202



\#### Current M3 f025 reference



\- RMSE = 0.04056802137117637

\- MAE = 0.01605622362541525

\- wet/dry IoU = 0.7957316542926588

\- rollout stability = 0.9906371863264787



\#### Phase 3.1 learned-selective



\- RMSE = 0.039599172378841196

\- MAE = 0.0156574871293024

\- wet/dry IoU = 0.7954359681982743

\- rollout stability = 0.9909981457810653



Interpretation:



\- Phase 3.1 improves RMSE

\- Phase 3.1 improves MAE

\- Phase 3.1 improves rollout stability

\- wet/dry IoU is slightly lower but essentially on the same level



Overall reading for `seed202`:



\- learned-selective provides a real but modest improvement on the difficult case

\- this is a meaningful positive signal

\- however, the gain is incremental rather than transformative



\### seed42



\#### Current M3 f025 reference



\- RMSE = 0.03521115528909784

\- MAE = 0.013695237030716319

\- wet/dry IoU = 0.8305582623732718

\- rollout stability = 0.9913632367786608



\#### Phase 3.1 learned-selective



\- RMSE = 0.03626077367286933

\- MAE = 0.013907563235414656

\- wet/dry IoU = 0.8187811625631232

\- rollout stability = 0.9913672773461593



Interpretation:



\- Phase 3.1 is worse than M3 f025 on RMSE

\- Phase 3.1 is worse than M3 f025 on MAE

\- Phase 3.1 is worse than M3 f025 on wet/dry IoU

\- rollout stability is essentially unchanged



Overall reading for `seed42`:



\- learned-selective does not preserve the current M3 advantage on the favorable case

\- the current implementation appears to trade away too much of the strong-case behavior



\## Cross-Seed Reading



Putting the two checked seeds together:



\- `seed202` favors Phase 3.1 learned-selective

\- `seed42` favors current M3 f025



This means:



\- the learned-selective idea is not invalid

\- but the current implementation is not yet better than M3 f025 in cross-seed balance

\- the current behavior is closer to a targeted difficult-case refinement than a new overall best architecture



\## Current Conclusion



Phase 3.1 is a useful exploratory result, but it does not replace the current M3 best setting.



The most stable current conclusion is:



\- \*\*current best next-step architecture direction remains M3 f025\*\*

\- \*\*Phase 3.1 learned-selective should be preserved as a promising but not yet dominant refinement idea\*\*



Current best M3 setting remains:



`temporal\_gate\_residual\_partial`  

`hidden\_channels = 16`  

`residual\_alpha = 0.10`  

`conditioned\_fraction = 0.25`



\## Practical Interpretation



The current Phase 3.1 result suggests:



\- learnable channel selection may help on difficult cases

\- but the current selector design does not yet maintain the favorable-case balance achieved by M3 f025

\- therefore, the learned-selective idea should be treated as a directional clue, not yet as the new preferred model variant



\## Recommended Next Step



The immediate next step should not be a broad expansion of Phase 3.1.



Instead, the correct current position is:



1\. preserve M3 f025 as the current best-balanced architecture direction

2\. archive Phase 3.1 as a targeted refinement attempt

3\. only revisit learned-selective modulation later if a more structured or better-regularized selector design is proposed

