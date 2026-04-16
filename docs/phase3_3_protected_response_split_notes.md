\# Phase 3.3 Protected Response Split Notes



\## Goal



Refine the Phase 3.2 response-split idea by making the response side more conservative.



The main question is:



\- can we preserve the difficult-case benefit of explicit memory/response separation

\- while reducing the favorable-case damage introduced by full response-block modulation



\## Motivation



Phase 3.2 showed a strong positive result on `seed202`, but it degraded the favorable-case balance on `seed42`.



This suggested that the main issue was not the memory/response split itself, but the fact that the entire response block was still being directly modulated.



Therefore, Phase 3.3 introduced a protected response split.



\## Implemented Mode



A new rainfall conditioning mode was added:



\- `temporal\_gate\_residual\_response\_split\_protected`



Key design choices:



\- preserve all previous modes unchanged

\- preserve the Phase 3.2 memory/response structure

\- split the response block itself into:

&#x20; - anchor response channels

&#x20; - active response channels

\- only the active response channels receive rainfall-conditioned residual gating

\- memory channels and anchor response channels remain untouched



\## Sanity Check



Sanity check passed for the protected response-split mode.



Command:



```bash

python scripts/sanity\_check\_phase2b\_temporal\_gate.py

```



Key sanity-check values:



\- `protected\_response\_split\_mode\_output\_shape = \[2, 12, 1, 32, 32]`

\- `protected\_response\_split\_mode\_finite = true`

\- `protected\_response\_split\_response\_channels = 64`

\- `protected\_response\_split\_memory\_channels = 64`

\- `protected\_response\_split\_anchor\_response\_channels = 32`

\- `protected\_response\_split\_active\_response\_channels = 32`

\- `protected\_response\_split\_residual\_alpha\_zero\_is\_identity = true`

\- `protected\_response\_split\_full\_active\_max\_abs\_diff\_vs\_phase32 = 0.0`



Interpretation:



\- the protected mode is shape-safe

\- it remains finite

\- it preserves no-op behavior when `residual\_alpha = 0.0`

\- when fully active, it reduces exactly to the Phase 3.2 response-split path



\## Tested Variants



\### Variant A



\- `active\_fraction\_within\_response = 0.50`



\### Variant B



\- `active\_fraction\_within\_response = 0.25`



Common settings:



\- `hidden\_channels = 16`

\- `residual\_alpha = 0.10`

\- `conditioned\_fraction = 0.25`



\## Test Results



\### Reference: current M3 f025



\#### seed202



\- RMSE = 0.04056802137117637

\- MAE = 0.01605622362541525

\- wet/dry IoU = 0.7957316542926588

\- rollout stability = 0.9906371863264787



\#### seed42



\- RMSE = 0.03521115528909784

\- MAE = 0.013695237030716319

\- wet/dry IoU = 0.8305582623732718

\- rollout stability = 0.9913632367786608



\---



\### Phase 3.3 / af050



\#### seed202



\- RMSE = 0.03874241364629645

\- MAE = 0.015434139016035357

\- wet/dry IoU = 0.8063646335350839

\- rollout stability = 0.9910438782290408



\#### seed42



\- RMSE = 0.03937520145585662

\- MAE = 0.015328815304919294

\- wet/dry IoU = 0.7902859386644865

\- rollout stability = 0.9911636459200006



Interpretation:



\- `af050` preserves clear difficult-case gains on `seed202`

\- `af050` improves over Phase 3.2 on `seed42`

\- but `af050` still remains clearly weaker than M3 f025 on the favorable case



\---



\### Phase 3.3 / af025



\#### seed202



\- RMSE = 0.039513754021180306

\- MAE = 0.01580669652474554

\- wet/dry IoU = 0.8013222374414143

\- rollout stability = 0.9913082624736586



\#### seed42



\- RMSE = 0.038860898759020004

\- MAE = 0.014597773649974874

\- wet/dry IoU = 0.8003254783780951

\- rollout stability = 0.9915911335694162



Interpretation:



\- `af025` is slightly more conservative than `af050`

\- `af025` gives up a small amount of difficult-case strength on `seed202`

\- `af025` improves clearly over `af050` on `seed42`

\- within Phase 3.3, `af025` is the better balance point



\## Cross-Variant Reading



Comparing `af050` and `af025`:



\- `seed202` prefers `af050`

\- `seed42` clearly prefers `af025`



However, the `seed202` difference is modest, while the `seed42` recovery under `af025` is more meaningful.



Therefore:



\- within Phase 3.3, `af025` is the better balanced setting



\## Phase 3 Final Reading



Across the full Phase 3 exploration:



\- Phase 3.1 showed that a freer learned selector is not the main answer

\- Phase 3.2 showed that explicit memory/response functional separation is highly meaningful

\- Phase 3.3 showed that this structure must be protected and more conservative

\- within Phase 3.3, smaller active modulation is better



This yields a clear final structure-level conclusion:



\- protected response split is the correct Phase 3 direction

\- but the current best Phase 3 variant still does not fully surpass M3 f025



\## Current Conclusion



\### Best Phase 3 variant



`temporal\_gate\_residual\_response\_split\_protected`  

`hidden\_channels = 16`  

`residual\_alpha = 0.10`  

`conditioned\_fraction = 0.25`  

`active\_fraction\_within\_response = 0.25`



\### Overall project-level best-balanced architecture



Still remains:



`temporal\_gate\_residual\_partial`  

`hidden\_channels = 16`  

`residual\_alpha = 0.10`  

`conditioned\_fraction = 0.25`



\## Practical Interpretation



Phase 3 is successful as a research stage because it clarified the structural direction:



\- free learned channel selection is not the main solution

\- structured memory/response separation is meaningful

\- protected and conservative response modulation is better than broader response modulation



However, Phase 3 did not yet produce a new global best-balanced architecture that surpasses M3 f025.



\## Final Recommendation



Phase 3 can now be considered complete.



The correct next action is:



1\. archive Phase 3 as a completed structured-exploration stage

2\. keep M3 f025 as the current best-balanced architecture

3\. treat Phase 3.3 / af025 as the strongest structured refinement direction discovered so far

4\. move next to project cleanup, documentation consolidation, and GitHub mainline presentation

