\# Phase 4 Final Comparison Plan



\## Background

Phase 2 established M3 f025 as the current best-balanced mainline.

Phase 3 established Phase 3.3 af025 as the strongest structured refinement, but it did not fully replace M3.



\## Why Phase 4

The project no longer needs another round of local parameter search in Phase 3.

The next priority is to consolidate final evidence for the two strongest contenders.



\## Final Contenders

\### Contender A: M3 f025

\- temporal\_gate\_residual\_partial

\- hidden\_channels = 16

\- residual\_alpha = 0.10

\- conditioned\_fraction = 0.25



\### Contender B: Phase 3.3 af025

\- temporal\_gate\_residual\_response\_split\_protected

\- hidden\_channels = 16

\- residual\_alpha = 0.10

\- conditioned\_fraction = 0.25

\- active\_fraction\_within\_response = 0.25



\## Phase 4 Goal

Generate direct final comparisons between the two contenders without changing model structure or training logic.



\## Deliverables

\- assets/images/final/m3\_vs\_phase33\_af025\_seed202\_maps.png

\- assets/images/final/m3\_vs\_phase33\_af025\_seed202\_timeseries.png

\- assets/images/final/m3\_vs\_phase33\_af025\_seed42\_maps.png

\- assets/images/final/m3\_vs\_phase33\_af025\_seed42\_timeseries.png

\- docs/phase4\_final\_comparison.md



\## Comparison Focus

\### difficult case

\- seed202



\### favorable case

\- seed42



\## Success Criteria

\- Direct qualitative comparison is available for both seed202 and seed42

\- Quantitative and qualitative evidence support the final project-level conclusion

\- README can later be updated using these final figures

