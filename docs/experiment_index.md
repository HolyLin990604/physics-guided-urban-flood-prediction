\# Experiment Index



\## Purpose



This document provides a compact index of the main experiment stages, their goals, and the most important documentation outputs.



It is intended to help navigate the project history without relying only on branch names.



\## Current Main Conclusions



\### Current best-balanced architecture



\- `temporal\_gate\_residual\_partial`

\- `hidden\_channels = 16`

\- `residual\_alpha = 0.10`

\- `conditioned\_fraction = 0.25`



This is the current \*\*M3 f025\*\* mainline.



\### Strongest structured refinement



\- `temporal\_gate\_residual\_response\_split\_protected`

\- `hidden\_channels = 16`

\- `residual\_alpha = 0.10`

\- `conditioned\_fraction = 0.25`

\- `active\_fraction\_within\_response = 0.25`



This is the current \*\*Phase 3.3 af025\*\* structured refinement winner.



\## Phase Index



\### Phase 1



\*\*Goal\*\*

\- Establish the baseline U-Net + TCN forecasting setup

\- Add lightweight output-space physics-guided losses



\*\*Key ideas\*\*

\- non-negativity loss

\- wet/dry consistency loss



\*\*Role in project\*\*

\- established the initial physics-guided baseline



\*\*Key materials\*\*

\- README overview on `main`

\- early baseline/phase1 qualitative figures in `assets/images/`



\---



\### Phase 2



\*\*Goal\*\*

\- Explore rainfall-conditioning architectures

\- identify the best-balanced mainline direction



\*\*Key ideas\*\*

\- residual gate variants

\- partial gate variants

\- multi-seed validation

\- qualitative comparison of candidate directions



\*\*Role in project\*\*

\- identified the current best-balanced architecture: \*\*M3 f025\*\*



\*\*Key documents\*\*

\- `docs/phase2\_40e\_multiseed\_summary.md`

\- `docs/phase2\_40e\_multiseed\_test\_summary.md`

\- `docs/phase2\_qualitative\_comparison\_notes.md`

\- `docs/phase2b\_m3\_partial\_gate\_notes.md`

\- `docs/phase2b\_m3\_vs\_phase2a\_three\_seed\_summary.md`



\*\*Important archive branch\*\*

\- `phase2b-m3-partial-gate`



\---



\### Phase 3.1



\*\*Goal\*\*

\- test whether a learnable channel selector could improve over fixed partial gating



\*\*Key idea\*\*

\- `temporal\_gate\_residual\_learned\_selective`



\*\*Role in project\*\*

\- showed that freer learned channel selection was not the main solution



\*\*Key document\*\*

\- `docs/phase3\_1\_learned\_selective\_notes.md`



\*\*Important archive branch\*\*

\- `phase3-structured-selective-modulation`



\---



\### Phase 3.2



\*\*Goal\*\*

\- introduce explicit memory/response separation in the bottleneck channels



\*\*Key idea\*\*

\- `temporal\_gate\_residual\_response\_split`



\*\*Role in project\*\*

\- showed that structured memory/response separation is meaningful

\- but full response-block modulation was too aggressive



\*\*Key document\*\*

\- `docs/phase3\_2\_response\_split\_notes.md`



\*\*Important archive branch\*\*

\- `phase3-2-structured-response-split`



\---



\### Phase 3.3



\*\*Goal\*\*

\- protect the response split by introducing anchor response channels and active response channels



\*\*Key idea\*\*

\- `temporal\_gate\_residual\_response\_split\_protected`



\*\*Role in project\*\*

\- established the strongest structured refinement direction

\- identified `af025` as the best Phase 3 balance point



\*\*Key documents\*\*

\- `docs/phase3\_3\_protected\_response\_split\_notes.md`

\- `docs/phase3\_summary.md`



\*\*Important archive branch\*\*

\- `phase3-3-protected-response-split`



\---



\### Phase 4



\*\*Goal\*\*

\- compare the two final contenders directly:

&#x20; - M3 f025

&#x20; - Phase 3.3 af025



\*\*Role in project\*\*

\- finalized the project-level conclusion

\- confirmed that:

&#x20; - M3 f025 remains overall best-balanced

&#x20; - Phase 3.3 af025 is the strongest structured refinement



\*\*Key documents\*\*

\- `docs/phase4\_final\_comparison\_plan.md`

\- `docs/phase4\_final\_comparison.md`



\*\*Key figures\*\*

\- `assets/images/final/m3\_vs\_phase33\_af025\_seed202\_maps.png`

\- `assets/images/final/m3\_vs\_phase33\_af025\_seed202\_timeseries.png`

\- `assets/images/final/m3\_vs\_phase33\_af025\_seed42\_maps.png`

\- `assets/images/final/m3\_vs\_phase33\_af025\_seed42\_timeseries.png`



\*\*Important archive branch\*\*

\- `phase4-final-comparison`



\---



\## Recommended Reading Order



If someone wants to understand the project quickly, the most efficient reading order is:



1\. `README.md`

2\. `docs/project\_status.md`

3\. `docs/phase4\_final\_comparison.md`

4\. `docs/phase3\_summary.md`

5\. Phase-specific archive notes if deeper detail is needed



\## Current Project-Level Position



The repository should currently be interpreted as follows:



\- `main` = stable project homepage and current project overview

\- Phase archive branches = stage-specific experiment records

\- M3 f025 = current mainline reference

\- Phase 3.3 af025 = strongest structured refinement reference

