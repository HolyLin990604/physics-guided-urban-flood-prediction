AGENTS.md



Repository purpose

This repository is a research prototype for physics-guided urban flood prediction.



Current stable baseline

Backbone: UNet + TCN

Stable physics guidance:

non-negativity loss

wet/dry consistency loss



Development rules

Do not overwrite or break the current baseline pipeline.

Preserve backward compatibility with existing training scripts and configs.

All new physics modules must be optional and configurable.

Keep code changes modular and minimally invasive.

Do not hardcode new local absolute paths.

Update README when training or evaluation workflow changes.



Preferred upgrade path

*1*Stronger physics losses

*2Ablationfriendly* experiment configs

*3Architecturelevel* physicsaware modules

*4Only* later explore shallowwaterinspired residual constraints



Done means

New code compiles/runs in the existing project structure

Existing configs remain usable

New feature has a config switch

README explains how to enable the feature

A minimal sanity check is provided

