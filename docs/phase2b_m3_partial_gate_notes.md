\# Phase 2B Milestone 3 Partial Gate Notes



\## Goal



Test whether selective residual rainfall-conditioned gating is more robust than global residual gating.



\## Motivation



M2 showed that simply weakening the gate with a global residual path did not solve the cross-seed instability problem.



The M3 hypothesis is:



\- the issue is not only gate strength

\- the issue may be that too many bottleneck channels are being modulated at once

\- selective modulation may be more robust than global modulation



\## Implementation



A new rainfall conditioning mode was added:



\- `temporal\_gate\_residual\_partial`



Key design choices:



\- keep existing `temporal\_gate` unchanged

\- keep existing `temporal\_gate\_residual` unchanged

\- add explicit `conditioned\_fraction`

\- apply residual rainfall-conditioned modulation only to a fixed subset of bottleneck channels

\- leave the remaining channels unchanged



\## Sanity Check



Sanity check passed for:



\- disabled-path compatibility

\- residual mode forward pass

\- partial mode forward pass

\- `residual\_alpha = 0.0` identity / no-op behavior

\- `conditioned\_fraction = 0.0` identity / no-op behavior



Command:

```bash
python scripts/sanity_check_phase2b_temporal_gate.py
```

## Pilot Configs

Pilot configs were created for:

- `seed42`
- `seed202`

with:

- `hidden_channels = 16`
- `residual_alpha = 0.10`
- `conditioned_fraction = 0.25`
- `conditioned_fraction = 0.50`

## Test Results

### seed202

#### f025

- RMSE = 0.04056802137117637
- MAE = 0.01605622362541525
- wet/dry IoU = 0.7957316542926588
- rollout stability = 0.9906371863264787

#### f050

- RMSE = 0.039487342987405624
- MAE = 0.015739386509123602
- wet/dry IoU = 0.7955405931723746
- rollout stability = 0.9908571902074312

Interpretation:

- `f050` is slightly better than `f025` on RMSE, MAE, and stability
- wet/dry IoU is essentially unchanged
- both partial-gate variants improve clearly over the previous M2 residual-gate result
- M3 improves the old Phase 2B behavior on the `seed202` risk case, but still does not surpass Phase 2A

### seed42

#### f025

- RMSE = 0.03521115528909784
- MAE = 0.013695237030716319
- wet/dry IoU = 0.8305582623732718
- rollout stability = 0.9913632367786608

#### f050

- RMSE = 0.03798978040485006
- MAE = 0.014650357053860238
- wet/dry IoU = 0.8144126001157259
- rollout stability = 0.9911644741108543

Interpretation:

- `f025` is clearly better than `f050` on the `seed42` favorable case
- `f050` weakens the strong-case advantage too much
- `f025` is the more balanced choice across seeds

## Current Conclusion

M3 is substantially more successful than M2.

The key conclusion is:

- selective partial gating is a valid and promising Phase 2B direction
- the current best-balanced M3 candidate is:

`temporal_gate_residual_partial`  
`hidden_channels = 16`  
`residual_alpha = 0.10`  
`conditioned_fraction = 0.25`

Additional interpretation:

- `conditioned_fraction = 0.50` helps slightly on the `seed202` risk case
- but it hurts the `seed42` favorable case
- therefore `f025` is currently preferred as the best-balanced M3 setting

## Position Relative to Current Mainline

At the current stage:

- **Primary candidate: Phase 2A 40e**
- **Strong alternative: original Phase 2B h16 40e**

M3 does not yet replace the primary candidate.

However, M3 `f025` is the first new Phase 2B direction that behaves reasonably on both the risk case and the favorable case, and is therefore worth preserving as the current best next-step architecture direction.