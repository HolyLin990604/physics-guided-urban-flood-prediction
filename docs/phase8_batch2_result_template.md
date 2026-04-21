# Phase 8 Batch 2 Result Template

## Experiment Purpose

TBD

State the specific Batch 2 question addressed by this comparison. Keep the purpose tied to trade-off and robustness positioning for `adapt010`.

## Compared Runs

| role | seed | config / run id | epoch count | result source |
|---|---|---|---:|---|
| static Phase 3.3 `af025` control | TBD | TBD | TBD | TBD |
| `adapt010` candidate | TBD | TBD | TBD | TBD |

## Seed Role

| seed | role | interpretation note |
|---|---|---|
| `seed202` | difficult-case reference | TBD |
| `seed123` | repeatability reference | TBD |
| `seed42` | favorable-case guardrail reference | TBD |
| other | explicitly justified comparison | TBD |

Use only the rows that apply. If another seed is used, state why it is needed for Batch 2.

## Key Metrics Table

| config | val_rmse | val_mae | val_wet_dry_iou | val_rollout_stability | val_loss |
|---|---:|---:|---:|---:|---:|
| static Phase 3.3 `af025` | TBD | TBD | TBD | TBD | TBD |
| `adapt010` | TBD | TBD | TBD | TBD | TBD |
| delta: `adapt010 - af025` | TBD | TBD | TBD | TBD | TBD |

## Compact Per-Seed Comparison Versus Static `af025`

| seed | seed role | RMSE/MAE reading | IoU reading | stability reading | overall Batch 2 reading |
|---|---|---|---|---|---|
| `seed202` | difficult-case | TBD | TBD | TBD | TBD |
| `seed123` | repeatability | TBD | TBD | TBD | TBD |
| `seed42` | favorable-case guardrail | TBD | TBD | TBD | TBD |
| other | TBD | TBD | TBD | TBD | TBD |

## Qualitative / Process Interpretation

Artifacts used:

- TBD

Interpretation:

- spatial behavior: TBD
- process / time-series behavior: TBD
- visible mismatch or improvement pattern: TBD

If no qualitative artifacts are used, state that explicitly.

## Trade-Off Interpretation

RMSE/MAE behavior:

- TBD

Wet/dry IoU behavior:

- TBD

Rollout stability behavior:

- TBD

Overall trade-off reading:

- TBD

## Guardrail Check

Favorable-case guardrail status:

- TBD

Does `adapt010` show unacceptable favorable-case regression relative to static `af025`?

- TBD

## Decision Note

Batch 2 decision for this comparison:

- TBD

Use one of the following forms where appropriate:

- continue focused `adapt010` development
- keep `adapt010` active but limited
- pause adaptive expansion pending clearer evidence

## Final Positioning Summary For `adapt010`

TBD

State the final Batch 2 positioning without broad claims:

- where `adapt010` is stronger: TBD
- where evidence is mixed: TBD
- whether gains are mainly RMSE/MAE-oriented, IoU-oriented, or mixed: TBD
- whether difficult-case and favorable-case behavior remain compatible: TBD
- whether `adapt010` remains stable and interpretable enough for continued focused development: TBD
