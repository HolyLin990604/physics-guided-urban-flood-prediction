# Phase 49 Full-Dataset Warning Framework Summary

Selected decision: `phase49_warning_framework_completed_with_conservative_labels`.

Phase 49 converted fixed Phase 48 full-dataset reliability and physical proxy diagnostics into a conservative warning framework for the Phase 47 128x128 full-dataset baseline. No training, seed sweep, hyperparameter sweep, loss redesign, model modification, SWE residual, or PINN component was run or introduced.

## Scenario Counts

- Input files found: `true`
- Scenario count: `48`
- Reliable: `1`
- Caution: `12`
- High-risk: `35`
- High-risk review cases: `35`

## Interpretation

Phase 49 preserves Phase 48 warning labels as conservative diagnostic screening labels; they are not calibrated probabilities, event likelihoods, or final production guarantees. High-risk is intentionally sensitive and does not by itself prove poor overall model skill. Phase 49 does not claim Level 5 support, strict conservation, full mass conservation, hydrodynamic closure, or final production readiness.

## Failure-Driver Rules

Failure drivers use Phase 48 summary thresholds where available. The key thresholds are:

- RMSE driver threshold: `0.011004068821235263`
- Wet/dry IoU driver threshold: `0.8860657485849278`
- False-dry driver threshold: `0.10486495261130992`
- False-wet driver threshold: `0.00442259846859298`
- Volume-bias proxy driver threshold: `0.025945133712967482`
- Peak-depth underprediction proxy driver threshold: `> 0`

Next recommended action: Use Phase 49 outputs for conservative case reporting and diagnostic screening, with manual review for high-risk cases and no probability interpretation.
