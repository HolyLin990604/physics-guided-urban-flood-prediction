\# Phase 2 40-Epoch Multi-Seed Test Summary



\## Scope



This note summarizes the test-set comparison between:



\- Phase 2A (loss-only baseline)

\- Phase 2B h16 (rainfall-conditioned temporal gate)



using three seeds: 42, 123, and 202.



\## Test Summary Table


| Seed | Model | Test RMSE | Test MAE | Test wet/dry IoU | Test rollout stability | Test step RMSE std |
| ---- | ----- | --------: | -------: | ---------------: | ---------------------: | -----------------: |
| 42 | Phase 2A | 0.03625 | 0.01447 | 0.81357 | 0.99154 | 0.00858 |
| 42 | Phase 2B h16 | 0.03561 | 0.01357 | 0.82678 | 0.99169 | 0.00844 |
| 123 | Phase 2A | 0.03528 | 0.01394 | 0.83318 | 0.99048 | 0.00966 |
| 123 | Phase 2B h16 | 0.03492 | 0.01422 | 0.82763 | 0.99086 | 0.00927 |
| 202 | Phase 2A | 0.03830 | 0.01516 | 0.81970 | 0.99100 | 0.00914 |
| 202 | Phase 2B h16 | 0.03968 | 0.01598 | 0.78627 | 0.99103 | 0.00911 |


\## Main Observation



The three-seed test comparison shows that:



\- seed 42 favors Phase 2B h16

\- seed 123 is mixed

\- seed 202 favors Phase 2A



At the current stage, Phase 2A remains the more stable primary candidate, while Phase 2B h16 is retained as a strong alternative.



\## Recommended Next Step



The next step is not more training. The next step is:



1\. build a paired qualitative comparison for seed 42 and seed 202

2\. compare inundation maps

3\. compare region-average time series

4\. then decide whether README should be updated

