# Project Status

## Current Conclusion

The repository should currently be interpreted as follows:

- `M3 f025` remains the overall best-balanced mainline reference
- Phase 3.3 `af025` remains the strongest static structured refinement
- Phase 6 `adapt025` is closed as a negative/neutral result
- Phase 7 `adapt010` is now the current adaptive candidate

## Meaning Of Each Reference

### Mainline reference

`M3 f025` remains the default project reference because it still provides the strongest overall balance across robustness, stability, and project-level confidence.

### Strongest static structured refinement

Phase 3.3 `af025` remains the strongest static structured refinement discovered so far. It is still the correct static control when evaluating whether adaptive follow-ups add value.

### Closed adaptive result

Phase 6 `adapt025` established that the adaptive scalar mechanism is technically stable and trainable, but it did not remain superior to the static Phase 3.3 `af025` control after full training. It should therefore be treated as a documented negative/neutral result rather than an active candidate.

### Current adaptive candidate

Phase 7 `adapt010` is the current adaptive candidate. It improved the decisive difficult-case `seed202 / 40e` result over both the static `af025` control and the earlier Phase 6 `adapt025` run, and it also passed the favorable-case `seed42 / 5e` guardrail check.

## Practical Reading Guide

When reading the repository:

- use `M3 f025` as the overall project mainline reference
- use Phase 3.3 `af025` as the static structured refinement reference
- treat Phase 6 `adapt025` as archived evidence that a larger adaptive range was too aggressive
- treat Phase 7 `adapt010` as the active adaptive direction for future targeted follow-up work

## Key Documents

- `docs/phase3_summary.md`
- `docs/phase3_3_protected_response_split_notes.md`
- `docs/phase6_pilot_a_results.md`
- `docs/phase7_adapt010_results.md`
