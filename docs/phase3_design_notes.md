\# Phase 3 Design Notes



\## Stage Transition



The project has now completed the main Phase 2 comparison stage and an initial follow-up architecture exploration stage.



The current status is:



\- \*\*Primary candidate:\*\* Phase 2A (40 epochs)

\- \*\*Best next-step architecture direction:\*\* M3 `temporal\_gate\_residual\_partial`

\- current best M3 setting:

&#x20; - `hidden\_channels = 16`

&#x20; - `residual\_alpha = 0.10`

&#x20; - `conditioned\_fraction = 0.25`



This transition means the project should no longer focus on broad exploratory tuning of many small gate variants.



Phase 3 should begin from a different question:



\- not only whether a modified architecture can improve metrics

\- but whether the improved architecture can be made more structured, more interpretable, and more credible



\## Why Phase 3 Starts Now



Phase 2 and the M2/M3 follow-up work have already answered several important questions.



\### What has been established



1\. \*\*Phase 2A remains a strong and stable baseline\*\*

&#x20;  - it is still the current primary candidate



2\. \*\*M2 was not sufficient\*\*

&#x20;  - simply weakening the residual gate globally did not solve the cross-seed issue



3\. \*\*M3 was a meaningful improvement\*\*

&#x20;  - selective partial gating performed clearly better than M2

&#x20;  - `f025` emerged as the best-balanced setting

&#x20;  - this conclusion is now supported by multiple seeds



4\. \*\*The key architectural signal is now clearer\*\*

&#x20;  - the issue is not only gate strength

&#x20;  - the issue is also how many channels are modulated and how that modulation is organized



\### What is no longer worth doing



Phase 3 should not continue with:



\- broad parameter sweeps over many gate strengths

\- repeated small variations of the same global-vs-partial gate idea

\- unconstrained exploratory trial-and-error without a clearer structural hypothesis



\## Main Phase 3 Question



Phase 3 should answer the following higher-level question:



> Can the currently effective selective-modulation idea be upgraded into a more structured and more credible architecture direction?



In other words:



\- Phase 2 mainly asked whether a new structure could help

\- Phase 3 should ask why that structure helps and how to make it more meaningful



\## Phase 3 Goal



The goal of Phase 3 is:



\- to move from an \*\*effective architecture variant\*\*

\- toward a \*\*more structured and physically credible architecture direction\*\*



This does \*\*not\*\* mean switching immediately to a full physics-constrained framework.



Instead, it means beginning with a minimal next step:



\- keep the successful selective-modulation idea

\- make the selective behavior less arbitrary

\- give the modulation structure a clearer architectural meaning



\## Core Interpretation from Phase 2 / M3



The current M3 result suggests the following interpretation:



\- modulating all bottleneck channels is too broad

\- modulating a smaller subset of channels is more robust

\- therefore, selective modulation is a valid design principle



However, the current M3 implementation is still only a first approximation:



\- the conditioned channels are chosen as a fixed block of channels

\- this is operationally useful

\- but it is still not very interpretable



So the next step is not to abandon M3.



The next step is to \*\*make selective modulation more structured\*\*.



\## Phase 3.1 Proposal



\### Working name



\*\*Phase 3.1: Structured Selective Modulation\*\*



\### Central hypothesis



The next improvement should not come from changing gate strength again.



The next improvement should come from giving the selective gate a more meaningful internal structure.



\### Basic idea



Current M3 uses:



\- a fixed subset of bottleneck channels

\- residual rainfall-conditioned modulation

\- a manually chosen conditioned fraction



Phase 3.1 should test whether the same selective-modulation idea becomes more robust if the selective behavior is given a more explicit internal organization.



\## Phase 3.1 Design Principle



A good Phase 3.1 design should satisfy all of the following:



1\. \*\*Preserve current M3 strengths\*\*

&#x20;  - keep backward compatibility with the current successful M3 direction

&#x20;  - do not discard the selective partial-gate idea



2\. \*\*Increase structural meaning\*\*

&#x20;  - the conditioned portion should not feel like an arbitrary last-k-channel rule only

&#x20;  - the architecture should express a clearer reason for why some channels are modulated and others are not



3\. \*\*Stay conservative\*\*

&#x20;  - Phase 3.1 should still be a minimal extension

&#x20;  - it should not become a large uncontrolled redesign



4\. \*\*Remain comparable\*\*

&#x20;  - comparisons should remain anchored to:

&#x20;    - Phase 2A

&#x20;    - M3 `f025`



\## Concrete Phase 3.1 Starting Direction



The first Phase 3.1 direction should be:



> replace purely fixed channel-block selective gating with a more structured selective-modulation mechanism



This can still remain lightweight and conservative.



The important point is conceptual:



\- M3 proved that \*\*partial modulation\*\* helps

\- Phase 3.1 should test whether \*\*structured partial modulation\*\* is better than naive partial modulation



\## Recommended Scope for Phase 3.1



Phase 3.1 should be intentionally narrow.



\### What should change



\- only the internal organization of the selective-modulation mechanism

\- only one new architectural idea at a time

\- only one compact pilot at first



\### What should not change



\- do not change the whole training framework

\- do not change `train\_model.py`

\- do not change `evaluate\_model.py`

\- do not introduce many new loss terms at once

\- do not launch a large hyperparameter sweep immediately



\## Phase 3 Baselines



All Phase 3 work should be evaluated against exactly two main references:



\### Baseline 1

\*\*Phase 2A\*\*



This remains the current primary candidate.



\### Baseline 2

\*\*M3 f025\*\*



This is the current best next-step architecture direction.



These two models should define the reference frame for all Phase 3 judgments.



\## Phase 3 Success Criteria



A Phase 3.1 direction should only be considered successful if it satisfies at least one of the following without clearly damaging the others:



\- improves cross-seed balance relative to M3 f025

\- improves favorable-case performance without losing too much on difficult seeds

\- improves difficult-seed behavior without collapsing favorable cases

\- provides a clearer and more interpretable structure than the current M3 design



A Phase 3.1 direction should \*\*not\*\* be judged only by a single-seed metric improvement.



\## Current Research Position



At the present stage, the project position is:



\- Phase 2A remains the safest current mainline result

\- M3 f025 is the strongest new Phase 2B-derived direction discovered so far

\- the project is now ready to move from “does this variant help?” toward “can this helpful variant become a more credible architecture direction?”



This is the reason Phase 3 begins now.



\## Immediate Next Step



Before writing Phase 3 code, the workflow should be:



1\. finalize this design note

2\. define one narrow Phase 3.1 implementation hypothesis

3\. open a new code branch for Phase 3.1

4\. let Codex implement only the minimal required changes

5\. run one compact pilot before considering any broader expansion



\## Practical Project Decision



Therefore, the correct current workflow is:



\- \*\*now:\*\* finalize Phase 3 design notes

\- \*\*next:\*\* define the exact Phase 3.1 minimal hypothesis

\- \*\*then:\*\* open a new branch for Phase 3.1 code implementation

\- \*\*then:\*\* use Codex for the constrained implementation work



\## Provisional Phase 3 Conclusion



Phase 3 should be understood as:



> the stage that upgrades a metric-effective selective-gating idea into a more structured and more credible architecture direction.



The immediate task is not broad experimentation.



The immediate task is to design the first minimal structured-selective-modulation hypothesis clearly enough that it can be implemented cleanly and tested against:



\- Phase 2A

\- M3 f025

