\# Phase 3 Summary



\## Phase 3 Objective



Phase 3 was designed to test whether the current effective M3 direction could be upgraded into a more structured, more interpretable architecture without losing performance balance.



\## Starting Point



Current reference entering Phase 3:



`temporal\_gate\_residual\_partial`  

`hidden\_channels = 16`  

`residual\_alpha = 0.10`  

`conditioned\_fraction = 0.25`



This remained the best-balanced architecture at the end of Phase 2.



\## Phase 3.1



\### Idea

Replace the fixed partial-gate channel selection with a learnable selector.



\### Result

\- difficult-case improvement signal existed

\- but favorable-case balance was not preserved



\### Conclusion

A freer learned selector was not the main answer.



\## Phase 3.2



\### Idea

Explicitly split bottleneck channels into:

\- memory channels

\- response channels



Only the response channels were rainfall-gated.



\### Result

\- strong improvement on the difficult case

\- but too much favorable-case damage



\### Conclusion

Memory/response functional separation is meaningful, but full response-block modulation is too aggressive.



\## Phase 3.3



\### Idea

Protect the response block by splitting it into:

\- anchor response channels

\- active response channels



Only active response channels were directly rainfall-gated.



\### Result

\- this was the correct direction

\- smaller active modulation gave better balance

\- `active\_fraction\_within\_response = 0.25` was better than `0.50`



\### Conclusion

Protected response split is the strongest structured refinement discovered in Phase 3.



\## Final Phase 3 Outcome



\### Best Phase 3 variant



`temporal\_gate\_residual\_response\_split\_protected`  

`hidden\_channels = 16`  

`residual\_alpha = 0.10`  

`conditioned\_fraction = 0.25`  

`active\_fraction\_within\_response = 0.25`



\### Overall best-balanced architecture after Phase 3



Still remains:



`temporal\_gate\_residual\_partial`  

`hidden\_channels = 16`  

`residual\_alpha = 0.10`  

`conditioned\_fraction = 0.25`



\## Final Interpretation



Phase 3 did not replace M3 f025 as the global best-balanced architecture.



However, Phase 3 successfully established the strongest structured refinement direction discovered so far:



\- protected response split

\- conservative active modulation

\- clearer functional interpretation than earlier exploratory variants



\## Project Decision After Phase 3



\- Phase 3 can be treated as complete

\- M3 f025 remains the current best-balanced mainline

\- Phase 3.3 / af025 is preserved as the strongest structured refinement direction

\- the next step should be repository cleanup and GitHub presentation improvement

