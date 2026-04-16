\# M3 vs Phase 2A Three-Seed Summary



\## Goal



Compare the current best M3 candidate against Phase 2A across three seeds.



\## Models Under Comparison



\### Phase 2A



\- loss-only physics-guided baseline

\- current primary candidate after the earlier Phase 2 formal comparison stage



\### M3 candidate



\- `temporal\_gate\_residual\_partial`

\- `hidden\_channels = 16`

\- `residual\_alpha = 0.10`

\- `conditioned\_fraction = 0.25`



\## Seed-wise Comparison



\### seed42



| Model | RMSE | MAE | wet/dry IoU | rollout stability |

|---|---:|---:|---:|---:|

| Phase 2A | 0.03625 | 0.01447 | 0.81357 | 0.99154 |

| M3 f025 | 0.03521115528909784 | 0.013695237030716319 | 0.8305582623732718 | 0.9913632367786608 |



Interpretation:



\- M3 f025 is better than Phase 2A on RMSE

\- M3 f025 is better than Phase 2A on MAE

\- M3 f025 is clearly better than Phase 2A on wet/dry IoU

\- rollout stability is very close, with Phase 2A slightly higher



Overall reading for `seed42`:



\- M3 f025 outperforms Phase 2A on the favorable case



\### seed202



| Model | RMSE | MAE | wet/dry IoU | rollout stability |

|---|---:|---:|---:|---:|

| Phase 2A | 0.03830 | 0.01516 | 0.81970 | 0.99100 |

| M3 f025 | 0.04056802137117637 | 0.01605622362541525 | 0.7957316542926588 | 0.9906371863264787 |



Interpretation:



\- Phase 2A is better than M3 f025 on RMSE

\- Phase 2A is better than M3 f025 on MAE

\- Phase 2A is better than M3 f025 on wet/dry IoU

\- rollout stability is slightly better for Phase 2A



Overall reading for `seed202`:



\- M3 f025 improves substantially over the previous M2 direction

\- however, it still does not surpass Phase 2A on the risk case



\### seed123



| Model | RMSE | MAE | wet/dry IoU | rollout stability |

|---|---:|---:|---:|---:|

| Phase 2A | 0.03528 | 0.01394 | 0.83318 | 0.99048 |

| M3 f025 | 0.0348767723496023 | 0.014442356401368192 | 0.8356670078478361 | 0.9905538778556021 |



Interpretation:



\- M3 f025 is slightly better than Phase 2A on RMSE

\- Phase 2A is slightly better than M3 f025 on MAE

\- M3 f025 is slightly better than Phase 2A on wet/dry IoU

\- rollout stability is slightly better for M3 f025



Overall reading for `seed123`:



\- this seed is very competitive between the two models

\- M3 f025 is at least on the same performance tier as Phase 2A



\## Three-Seed Reading



Across the three seeds, the current picture is:



\- `seed42` favors M3 f025

\- `seed202` favors Phase 2A

\- `seed123` is very close, but slightly favorable to M3 f025 on RMSE, wet/dry IoU, and stability



This means:



\- M3 f025 is not a weak or unstable exploratory variant

\- M3 f025 now has meaningful support from three seeds

\- M3 f025 is clearly stronger than the earlier M2 residual-gate direction

\- M3 f025 is also more convincing than the original M3 `f050` setting from a cross-seed balance perspective



\## What M3 Improves



Relative to earlier Phase 2B directions, M3 f025 shows:



\- better cross-seed balance

\- a more credible selective-modulation mechanism

\- stronger wet/dry spatial overlap than Phase 2A on some favorable cases

\- initial evidence that partial gating is more robust than broader gating



\## What M3 Still Does Not Prove



M3 f025 does not yet justify replacing Phase 2A as the primary candidate.



Reasons:



\- `seed202` still clearly favors Phase 2A

\- the current evidence supports M3 as a strong next-step architecture direction, not yet as a definitive new mainline winner

\- a broader multi-seed or qualitative-comparison-based judgment would still be needed before promoting M3 above the current primary candidate



\## Provisional Conclusion



At the current stage:



\- \*\*Phase 2A remains the primary candidate\*\*

\- \*\*M3 f025 is now the strongest new Phase 2B-derived direction discovered so far\*\*



The current best M3 candidate is:



`temporal\_gate\_residual\_partial`  

`hidden\_channels = 16`  

`residual\_alpha = 0.10`  

`conditioned\_fraction = 0.25`



Its status should now be described as:



\- stronger than M2

\- supported by three seeds

\- competitive with Phase 2A on multiple seeds

\- worth preserving as the current best next-step architecture direction



\## Recommended Next Step



The next step is not another broad parameter sweep.



The next step should be one of the following:



1\. perform a compact qualitative comparison between Phase 2A and M3 f025 on representative seeds

2\. or begin the next-stage design discussion based on the current conclusion that selective partial gating is a credible architecture direction

