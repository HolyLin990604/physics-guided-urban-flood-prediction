# Phase 38 Seed42 Pilot Training and Guardrail Evaluation Plan

## 1. Background

- Phase 37 completed seed42 training authorization review.
- 18 / 18 required checks passed.
- `decision = seed42_training_authorized_next_phase`.
- `training_authorized_next_phase = true`.
- Phase 37 itself did not train.
- The only reviewed config is `configs/train_phase36_manhole_false_dry_guardrail_seed42_40e.json`.

## 2. Purpose

Phase 38 will run the single authorized seed42 pilot, evaluate it, and check it against Phase 34 AT01-AT14 and RT01-RT09.

## 3. Authorized Training Command

```bash
python scripts/train_model.py --config configs/train_phase36_manhole_false_dry_guardrail_seed42_40e.json
```

No other config is authorized.

## 4. Required Evaluation Step

After training, run test evaluation using the project evaluation script and the trained best checkpoint if needed.

## 5. Required Guardrail Check

After evaluation, run:

```bash
python scripts/check_phase36_pilot_guardrails.py
```

The result must be compared against Phase 34 AT01-AT14 and RT01-RT09. Any RT01-RT09 trigger rejects the result.

## 6. Decision Types

Use only:

- `seed42_pilot_accepted`
- `seed42_pilot_rejected`
- `seed42_pilot_mixed_requires_review`
- `training_or_evaluation_failed`

## 7. Allowed Actions

- Run the reviewed seed42 config only.
- Evaluate test split.
- Run Phase 36 guardrail checker.
- Write findings.

## 8. Prohibited Actions

- No seed123.
- No seed202.
- No multi-seed expansion.
- No sweeps.
- No Phase 29 continuation.
- No post-hoc loss/config changes to rescue the run.
- No strict conservation claims.
- No full mass conservation claims.
- No SWE/PINN claims.
- No hydrodynamic closure claims.
- No Level 5 claims.

## 9. Required Outputs

- `runs/phase36_manhole_false_dry_guardrail_seed42_40e/`
- Test evaluation outputs.
- Guardrail checker outputs.
- `docs/phase38_seed42_pilot_training_guardrail_evaluation_findings.md`
- Optional `analysis/phase38_seed42_pilot_training_guardrail_evaluation/` summary files if needed.

## 10. Success Criteria

Phase 38 succeeds if it runs only the authorized seed42 config, evaluates the result, runs the guardrail checker, and reports accept/reject/mixed using predeclared rules.

## 11. Immediate Next Step

After this plan is committed, run:

```bash
python scripts/train_model.py --config configs/train_phase36_manhole_false_dry_guardrail_seed42_40e.json
```
