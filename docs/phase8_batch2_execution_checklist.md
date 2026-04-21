# Phase 8 Batch 2 Execution Checklist

## Objective Reminder

Phase 8 Batch 2 has one objective:

**Trade-off and robustness positioning for `adapt010`.**

The execution goal is to determine where `adapt010` is stronger than static Phase 3.3 `af025`, where it is mixed, and whether it remains stable enough for continued focused development.

## Allowed Scope

- use `adapt010` as the only adaptive candidate under review
- compare against static Phase 3.3 `af025`
- focus on `seed202`, `seed123`, and `seed42`
- use full `40e` comparisons where matching runs already exist or are explicitly produced
- collect quantitative metrics and concise qualitative/process notes
- produce one compact per-seed comparison table and one final positioning note

## Prohibited Scope

- do not introduce Phase 9
- do not run a parameter sweep
- do not reopen `adapt025`
- do not add architecture ideas
- do not modify model code, training code, evaluation logic, or configs
- do not claim `adapt010` is the new overall mainline

## Pre-Run Verification

Before deciding to run anything:

- confirm the available static Phase 3.3 `af025` result for each seed under review
- confirm the available `adapt010` result for each seed under review
- confirm whether each available comparison is full `40e`
- confirm that metric names match the current validation record:
  - `val_rmse`
  - `val_mae`
  - `val_wet_dry_iou`
  - `val_rollout_stability`
  - `val_loss`
- check whether paired qualitative or process artifacts already exist for the seed
- record missing evidence explicitly instead of filling gaps with assumptions

## New Experiment Decision

First decide whether Batch 2 can be completed from existing evidence.

Run no new experiment if:

- each required seed has a usable `adapt010` versus static `af025` comparison
- the available metrics are sufficient to separate RMSE/MAE behavior from IoU behavior
- the guardrail and repeatability questions can be answered from existing results

Run a new experiment only if:

- one specific comparison is missing or unusable
- that comparison is required to answer the Batch 2 trade-off question
- the motivation can be stated before the run

At most one new explicitly motivated comparison is allowed in Batch 2. It must be a comparison, not a sweep.

## Evidence To Collect Per Seed

For each seed, collect:

- seed role:
  - `seed202`: difficult-case reference
  - `seed123`: repeatability reference
  - `seed42`: favorable-case guardrail reference
  - other: explicitly justify use
- static Phase 3.3 `af025` run identifier or source
- `adapt010` run identifier or source
- epoch count for each run
- final validation metrics
- qualitative/process artifacts used, if any
- short interpretation of RMSE/MAE behavior
- short interpretation of wet/dry IoU behavior
- short interpretation of rollout stability
- note on whether the seed supports, weakens, or complicates the `adapt010` position

## Required Comparison Against Static `af025`

Every Batch 2 result should compare `adapt010` against static Phase 3.3 `af025` on:

- `val_rmse`
- `val_mae`
- `val_wet_dry_iou`
- `val_rollout_stability`
- `val_loss`

Do not treat an `adapt010` result as meaningful without the corresponding static `af025` reference.

## Artifacts And Notes To Save

Save or record:

- one compact per-seed comparison table versus static `af025`
- source paths or run identifiers for compared results
- any figure or process artifact paths used for interpretation
- a short trade-off note for each seed
- a final positioning note / decision note for `adapt010`

Keep notes factual. Do not add inferred results that are not supported by metrics or artifacts.

## Completion Criteria

Batch 2 is complete when:

- all available required seed comparisons have been recorded
- any missing evidence is explicitly marked as missing
- no more than one new comparison has been run, if any
- RMSE/MAE behavior and wet/dry IoU behavior are interpreted separately
- favorable-case guardrail behavior is stated
- repeatability evidence is stated
- the final `adapt010` positioning note is written

The completion output should be a narrow trade-off decision, not a new phase plan.
