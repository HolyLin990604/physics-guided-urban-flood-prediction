\# Phase 12 Reliability / Applicability Diagnosis Plan



\## Objective



Phase 12 moves the project from model refinement to reliability and applicability diagnosis.



The purpose is not to improve the model by changing architecture, tuning loss weights, or opening another parameter sweep. The purpose is to diagnose where the current Phase 10 recommended model is reliable, where it fails, and how its errors vary across time steps, water-depth ranges, wet/dry boundary regions, and rainfall/scenario conditions.



The broader research goal remains to build a trustworthy, interpretable, physically consistent deep-learning surrogate for urban flood process prediction that can support rapid warning. Phase 12 contributes to that goal by turning model trustworthiness into measurable reliability profiles rather than a vague qualitative claim.



\## Current Mainline Starting Point



Phase 10 and Phase 11 have been completed and merged into `main`.



The current recommended Phase 10 setting is:



\- `boundary\_band\_pixels = 1`

\- `boundary\_weight = 2.0`



This setting has passed test-facing confirmation across three key seeds:



\- `seed123`: original mixed wet/dry IoU problem seed

\- `seed42`: favorable-case guardrail seed

\- `seed202`: difficult-case confirmation seed



`boundary\_weight = 1.5` remains only a conservative rollback setting.



No additional Phase 10 boundary-weight sweep is justified.



\## Phase 12 Scope



Phase 12 should diagnose the current recommended model. It should not change the model itself.



In scope:



\- timestep-wise error diagnosis

\- depth-bin error diagnosis

\- wet/dry boundary-distance error diagnosis

\- rainfall-condition or scenario-level reliability diagnosis

\- failure-case ranking

\- summary JSON / CSV / table outputs

\- diagnostic figures where useful

\- concise findings document based on actual results



Out of scope:



\- changing the U-Net + TCN architecture

\- changing rainfall-conditioned temporal gate design

\- tuning `boundary\_weight`

\- tuning `boundary\_band\_pixels`

\- adding new physical losses

\- opening a new model-family search

\- using validation-only evidence for final conclusions



\## Primary Diagnostic Objects



The first diagnostic target should be the Phase 10 recommended setting.



Target runs:



\- `runs/phase10\_margin\_aware\_boundary\_band\_seed123\_40e`

\- `runs/phase10\_margin\_aware\_boundary\_band\_seed42\_40e`

\- `runs/phase10\_margin\_aware\_boundary\_band\_seed202\_40e`



The diagnosis should focus on test-facing results. Existing `evaluation\_test` outputs should be reused when available. If deeper per-pixel or per-timestep predictions are needed, the analysis scripts may rerun evaluation using existing project utilities, but should not retrain models.



\## Diagnostic Questions



\### 1. Timestep-wise reliability



Questions:



\- Does error grow with forecast horizon?

\- Are later timesteps less reliable than earlier timesteps?

\- Is rollout stability consistent across seeds?

\- Are there specific timesteps where wet/dry IoU drops sharply?



Expected outputs:



\- `analysis/phase12\_reliability/timestep\_metrics.csv`

\- timestep-wise RMSE / MAE / wet-dry IoU table

\- optional timestep-wise figure



\### 2. Depth-bin reliability



Questions:



\- Is the model more reliable in dry, shallow, moderate, or deeper water regions?

\- Are shallow-water and near-threshold cells the dominant error source?

\- Does the model underpredict or overpredict deeper inundation areas?



Suggested target-depth bins:



\- dry / near dry: `target <= 0.05`

\- shallow: `0.05 < target <= 0.15`

\- moderate: `0.15 < target <= 0.30`

\- deep: `target > 0.30`



Expected outputs:



\- `analysis/phase12\_reliability/depth\_bin\_metrics.csv`

\- per-bin MAE / RMSE / bias / cell count



\### 3. Wet/dry boundary-distance reliability



Questions:



\- Are errors concentrated near target wet/dry boundaries?

\- How much error remains inside the 0–1 pixel boundary band?

\- Does error decrease away from the boundary?

\- Does Phase 10 improve the area that it was designed to address?



Suggested boundary-distance bands:



\- boundary band: `0–1 px`

\- near boundary: `1–3 px`

\- interior / far field: `>3 px`



Expected outputs:



\- `analysis/phase12\_reliability/boundary\_distance\_metrics.csv`

\- boundary-distance RMSE / MAE / bias / wet-dry classification error



\### 4. Rainfall-condition or scenario-level reliability



Questions:



\- Which test batches or scenarios produce the largest error?

\- Do heavier or more dynamic rainfall cases produce larger errors?

\- Are failure cases associated with stronger rainfall input, larger target inundation area, or sharper wet/dry boundaries?



Expected outputs:



\- `analysis/phase12\_reliability/scenario\_metrics.csv`

\- `analysis/phase12\_reliability/failure\_cases.csv`

\- ranked failure-case list



\### 5. Cross-seed reliability summary



Questions:



\- Are reliability patterns consistent across `seed123`, `seed42`, and `seed202`?

\- Does one seed remain systematically harder?

\- Are failures seed-specific or shared across the Phase 10 recommended model?



Expected outputs:



\- `analysis/phase12\_reliability/summary.json`

\- `analysis/phase12\_reliability/summary.md`

\- cross-seed summary table



\## Suggested First Script



The first Codex-generated script should be:



\- `scripts/analyze\_phase12\_reliability.py`



The script should create:



\- `analysis/phase12\_reliability/summary.json`

\- `analysis/phase12\_reliability/timestep\_metrics.csv`

\- `analysis/phase12\_reliability/depth\_bin\_metrics.csv`

\- `analysis/phase12\_reliability/boundary\_distance\_metrics.csv`

\- `analysis/phase12\_reliability/scenario\_metrics.csv`

\- `analysis/phase12\_reliability/failure\_cases.csv`



Optional figures may be saved under:



\- `analysis/phase12\_reliability/figures/`



\## Implementation Rules For Codex



Codex should follow these rules:



1\. Do not modify model architecture.

2\. Do not modify training code unless strictly necessary for reading outputs.

3\. Do not modify Phase 10 loss implementation.

4\. Do not open any new sweep.

5\. Reuse existing configs, datasets, checkpoints, and evaluation utilities where possible.

6\. Prefer test-facing analysis.

7\. Do not invent conclusions before metrics are generated.

8\. Write scripts that are reproducible from the repository root.

9\. Save outputs under `analysis/phase12\_reliability/`.

10\. Keep the first implementation focused and readable.



\## Expected Phase 12 Deliverables



Minimum deliverables:



\- `docs/phase12\_reliability\_applicability\_plan.md`

\- `scripts/analyze\_phase12\_reliability.py`

\- `analysis/phase12\_reliability/summary.json`

\- `analysis/phase12\_reliability/\*.csv`

\- `docs/phase12\_reliability\_applicability\_findings.md`



Optional deliverables:



\- diagnostic figures

\- representative failure-case visual summaries

\- README update after Phase 12 results are stable



\## Decision Criteria



Phase 12 should be considered successful if it can answer:



\- where the Phase 10 recommended model is reliable

\- where it is less reliable

\- whether errors concentrate near wet/dry boundaries

\- whether errors grow over forecast horizon

\- whether specific water-depth ranges dominate the error

\- whether specific scenarios or seeds remain difficult

\- what reliability boundaries should be reported before moving to the next research stage



\## Next Step



After this plan is committed, Codex can be used to implement the first new Phase 12 diagnostic script.



The first coding task should be to create `scripts/analyze\_phase12\_reliability.py` and generate the initial reliability outputs under `analysis/phase12\_reliability/`.

