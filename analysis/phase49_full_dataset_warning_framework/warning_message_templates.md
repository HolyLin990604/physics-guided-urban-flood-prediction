# Phase 49 Warning Message Templates

Global disclaimer: warning labels are conservative diagnostic screening labels. They are not calibrated probabilities, event likelihoods, final production guarantees, SWE/PINN validation claims, strict conservation claims, or hydrodynamic closure claims.

## reliable_scenario_message

Warning category: Reliable

Recommended action: Normal use with standard monitoring.

Interpretation: Phase 48 diagnostics did not identify major reliability or physical proxy concerns for `{scenario}` at `{location}` under the evaluated Phase 47 baseline.

Limitations: This is a conservative diagnostic label, not a calibrated probability or final production guarantee.

## caution_scenario_message

Warning category: Caution

Recommended action: Use with caution and review diagnostics.

Interpretation: One or more diagnostics indicate degraded reliability or a potential warning failure mode for `{scenario}` at `{location}`. Review drivers: `{failure_drivers}`.

Limitations: This label supports review and contextual interpretation. It is not a calibrated probability and does not prove model failure.

## high_risk_scenario_message

Warning category: High-risk

Recommended action: Review before relying on the prediction, or supplement with additional evidence.

Interpretation: Conservative diagnostics indicate elevated risk of warning failure or physical proxy inconsistency for `{scenario}` at `{location}`. Review drivers: `{failure_drivers}`.

Limitations: This screening label is intentionally sensitive. It does not by itself prove poor overall model skill or establish event probability.
