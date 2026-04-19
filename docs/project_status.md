\# Project Status



\## Current Stage



The project has completed:



\- Phase 1: baseline + output-space physics-guided losses

\- Phase 2: rainfall-conditioning architecture exploration

\- Phase 3: structured refinement exploration

\- Phase 4: final contender comparison



The project is currently in:



\- \*\*Phase 5: Mainline Consolidation and Release Prep\*\*



\## Current Mainline Conclusion



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



\## Final Contender Comparison Outcome



The final contender comparison between:



\- \*\*M3 f025\*\*

\- \*\*Phase 3.3 af025\*\*



supports the following conclusion:



\- \*\*M3 f025 remains the current overall best-balanced architecture\*\*

\- \*\*Phase 3.3 af025 is the strongest structured refinement discovered so far\*\*



Interpretation:



\- Phase 3.3 af025 performs better on the difficult case (`seed202`)

\- M3 f025 remains stronger on the favorable case (`seed42`)

\- therefore, Phase 3.3 af025 does not yet replace M3 as the project mainline



\## Repository Status



\### Main branch



`main` is now intended to serve as:



\- the stable project homepage

\- the current project summary

\- the main entry point for external readers



\### Archive branches



Important archive branches include:



\- `phase2b-m3-partial-gate`

\- `phase3-structured-selective-modulation`

\- `phase3-2-structured-response-split`

\- `phase3-3-protected-response-split`

\- `phase4-final-comparison`



These branches preserve stage-specific experimental history.



\## Current Documentation Status



Main documentation now includes:



\- `docs/experiment\_index.md`

\- `docs/phase3\_summary.md`

\- `docs/phase4\_final\_comparison.md`

\- `docs/project\_status.md`

\- `docs/phase5\_consolidation\_plan.md`



\## Remaining Consolidation Tasks



The following tasks still remain in Phase 5:



1\. sync a concise Phase 4 final-comparison conclusion back into `main` README

2\. check whether final comparison figures should be lightly referenced from `main`

3\. review minor repository cleanup items

4\. decide what to do with the untracked file:

&#x20;  - `configs/train\_phase2b\_temporal\_gate\_h16.json`



\## Next Recommended Direction



No immediate new architecture exploration is recommended.



The correct short-term priority is:



\- finalize mainline consolidation

\- stabilize repository presentation

\- preserve current conclusions cleanly



After that, a future research stage can be opened around a more focused question, such as:



\- how to combine the favorable-case stability of M3 with the difficult-case advantage of Phase 3.3

\- or how to conditionally activate stronger structured modulation only when needed

