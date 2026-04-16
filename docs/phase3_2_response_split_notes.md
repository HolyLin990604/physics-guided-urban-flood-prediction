\# Phase 3.2 Response Split Notes



\## Goal



Test whether the current M3 partial-gate idea can be upgraded into a more structured architecture by explicitly splitting bottleneck channels into:



\- a preserved memory block

\- a rainfall-responsive modulation block



The key motivation is to move beyond free learned channel selection and instead introduce a more interpretable functional split.



\## Motivation



Phase 3.1 showed that a learned channel selector can help on a difficult case (`seed202`), but it did not preserve the favorable-case balance on `seed42`.



This suggested that the next step should not be a freer selector.



Instead, the next step should be a more constrained and more structured design:



\- preserve one part of the bottleneck as stable memory

\- apply rainfall-conditioned residual modulation only to the explicitly designated response part



\## Implemented Mode



A new rainfall conditioning mode was added:



\- `temporal\_gate\_residual\_response\_split`



Key design choices:



\- keep all previous modes unchanged:

&#x20; - `temporal\_gate`

&#x20; - `temporal\_gate\_residual`

&#x20; - `temporal\_gate\_residual\_partial`

&#x20; - `temporal\_gate\_residual\_learned\_selective`

\- use `conditioned\_fraction` to define the response-block size

\- split bottleneck channels into:

&#x20; - memory channels

&#x20; - response channels

\- preserve the memory channels without direct rainfall gating

\- apply the residual rainfall gate only to the response channels

\- keep initialization exactly aligned with current M3 partial behavior at sanity-check level



\## Sanity Check



Sanity check passed for the response-split mode.



Command:



```bash

python scripts/sanity\_check\_phase2b\_temporal\_gate.py

```



Key sanity-check values:



\- `response\_split\_mode\_output\_shape = \[2, 12, 1, 32, 32]`

\- `response\_split\_mode\_finite = true`

\- `response\_split\_response\_channels = 64`

\- `response\_split\_memory\_channels = 64`

\- `response\_split\_residual\_alpha\_zero\_max\_abs\_diff = 0.0`

\- `response\_split\_residual\_alpha\_zero\_is\_identity = true`

\- `response\_split\_init\_max\_abs\_diff\_vs\_partial = 0.0`



Interpretation:



\- the response-split path is shape-safe

\- it remains finite

\- it preserves identity behavior when `residual\_alpha = 0.0`

\- it matches current M3 partial behavior exactly at initialization



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



\#### Phase 3.2 response-split



\- RMSE = 0.03877004628118716

\- MAE = 0.01543275830581

\- wet/dry IoU = 0.811147109458321

\- rollout stability = 0.9908450026261179



Interpretation:



\- Phase 3.2 improves RMSE

\- Phase 3.2 improves MAE

\- Phase 3.2 improves wet/dry IoU

\- Phase 3.2 improves rollout stability



Overall reading for `seed202`:



\- response-split gives a strong and clearly meaningful improvement on the difficult case

\- this is a stronger positive signal than Phase 3.1

\- explicit memory/response separation appears genuinely helpful for the risk case



\### seed42



\#### Current M3 f025 reference



\- RMSE = 0.03521115528909784

\- MAE = 0.013695237030716319

\- wet/dry IoU = 0.8305582623732718

\- rollout stability = 0.9913632367786608



\#### Phase 3.2 response-split



\- RMSE = 0.0402357308684211

\- MAE = 0.015512033561734776

\- wet/dry IoU = 0.7871554650758442

\- rollout stability = 0.9916081648123892



Interpretation:



\- Phase 3.2 is worse than M3 f025 on RMSE

\- Phase 3.2 is worse than M3 f025 on MAE

\- Phase 3.2 is worse than M3 f025 on wet/dry IoU

\- rollout stability is only slightly higher



Overall reading for `seed42`:



\- response-split does not preserve the favorable-case advantage of M3 f025

\- the current implementation helps the difficult case but sacrifices too much strong-case performance



\## Cross-Seed Reading



Putting the two checked seeds together:



\- `seed202` strongly favors Phase 3.2 response-split

\- `seed42` clearly favors current M3 f025



This means:



\- the response-split idea is not only valid, but highly informative

\- however, the current implementation is not yet better than M3 f025 in cross-seed balance

\- the current behavior is best interpreted as a strong difficult-case-oriented direction rather than a new overall best architecture



\## Comparison to Phase 3.1



Relative to Phase 3.1 learned-selective:



\- Phase 3.2 provides a stronger positive signal on `seed202`

\- Phase 3.2 gives a clearer structural interpretation

\- Phase 3.2 still fails to preserve the favorable-case balance on `seed42`



Therefore:



\- Phase 3.2 is more valuable than Phase 3.1 as a research signal

\- but Phase 3.2 still does not replace current M3 f025 as the best-balanced direction



\## Current Conclusion



Phase 3.2 is a useful and important exploratory result, but it does not replace the current M3 best setting.



The most stable current conclusion is:



\- \*\*current best-balanced architecture direction remains M3 f025\*\*

\- \*\*Phase 3.2 response-split should be preserved as the strongest current difficult-case improvement direction\*\*



Current best M3 setting remains:



`temporal\_gate\_residual\_partial`  

`hidden\_channels = 16`  

`residual\_alpha = 0.10`  

`conditioned\_fraction = 0.25`



\## Practical Interpretation



The current Phase 3.2 result suggests:



\- explicit memory/response functional separation is meaningful

\- structural partitioning helps difficult cases more clearly than free learned selection

\- however, the current response-split implementation still over-trades favorable-case balance



Therefore, Phase 3.2 should be treated as:



\- a stronger directional signal than Phase 3.1

\- but not yet the new preferred model variant



\## Recommended Next Step



The immediate next step should not be broad expansion.



The correct current position is:



1\. preserve M3 f025 as the current best-balanced architecture direction

2\. archive Phase 3.2 as the strongest difficult-case-oriented structural refinement discovered so far

3\. only move to a next Phase 3 substage if the new design explicitly aims to preserve favorable-case behavior while retaining the response-split benefit on difficult cases

