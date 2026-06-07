# Phase 50 Framework Summary Figures Plan

## Executive Summary

This step plans no-training, README-facing visualization support for the completed Phase 50 framework consolidation. It will convert existing Phase 43-50 CSV, JSON, and Markdown evidence into a compact set of reader-facing PNG figures.

The planned work is reporting support only. It is not a new experiment phase, does not generate new model evidence, and does not authorize Phase 51 training or any other expansion. The figures must preserve the current Level 4+ claim boundary and present the warning framework as conservative diagnostic screening rather than calibrated probability output.

The planned script is:

```text
scripts/plot_phase50_framework_summary_figures.py
```

## Motivation

Phase 50 completed no-training framework consolidation and paper-ready full-dataset evidence synthesis across Phases 43-49. The GitHub README records that result, but its representative visual material still relies mainly on older Phase 24/25 figures.

The Phase 43-50 route now contains the project's current full-dataset evidence chain:

```text
dataset inspection
-> replanning
-> indexing
-> dataloader feasibility
-> controlled 128x128 baseline
-> reliability diagnostics
-> warning framework
-> evidence synthesis
```

Most of this evidence is currently stored in CSV, JSON, and Markdown artifacts. Summary figures are needed to make the sequence, metrics, warning distribution, and claim boundaries understandable at README and paper-outline reading speed without changing the underlying evidence.

## Inputs

The plotting script should read only existing Phase 47-50 result artifacts:

```text
analysis/phase50_framework_consolidation/phase50_evidence_chain_table.csv
analysis/phase50_framework_consolidation/phase50_key_metrics_summary.csv
analysis/phase50_framework_consolidation/phase50_claim_boundary_table.csv
analysis/phase50_framework_consolidation/phase50_recommended_next_steps.csv
analysis/phase50_framework_consolidation/phase50_framework_synthesis.json
analysis/phase49_full_dataset_warning_framework/warning_framework_summary.json
analysis/phase48_full_dataset_reliability_physical_proxy/phase48_reliability_summary.json
analysis/phase47_controlled_downsample_baseline/phase47_training_summary.json
```

CSV and JSON fields should be the source of truth where the same value appears in multiple files. The script should validate required fields and fail clearly if a required artifact or value is missing. It should not infer stronger claims from metric values or warning counts.

## Planned Figures

### `phase50_evidence_chain_overview.png`

Show the Phase 43-50 evidence chain as a left-to-right or top-to-bottom staged workflow:

```text
Phase 43: dataset inspection
Phase 44: replanning
Phase 45: indexing
Phase 46: dataloader feasibility
Phase 47: controlled 128x128 baseline
Phase 48: reliability diagnostics
Phase 49: warning framework
Phase 50: evidence synthesis
```

Each stage should use concise reader-facing wording. The figure should distinguish evidence generation, no-training diagnostics, and synthesis without implying that every phase involved training.

### `phase50_key_metrics_summary.png`

Show the key Phase 47 controlled-baseline and Phase 48 diagnostic metrics in clearly separated groups.

Phase 47 controlled baseline:

| Metric | Value |
| --- | ---: |
| Best test RMSE | `0.01109213042097205` |
| Test MAE | `0.00525291082279485` |
| Test wet/dry IoU | `0.8255524213115374` |

Phase 48 full-dataset diagnostics:

| Metric | Value |
| --- | ---: |
| Mean RMSE | `0.012037189189155709` |
| Mean MAE | `0.005252910632811514` |
| Mean wet/dry IoU | `0.863043953275997` |
| Mean false-dry rate | `0.0911363765964386` |
| Mean false-wet rate | `0.003937674554837349` |
| Mean absolute relative volume-bias proxy | `0.021456503649973275` |

Because these metrics have different meanings and scales, the figure should avoid a single misleading shared-axis comparison. A grouped metric-card, normalized display, or small-multiple layout is preferred. The volume value must remain labeled as a proxy.

### `phase50_warning_level_counts.png`

Show the Phase 48/49 scenario warning-level counts:

| Warning level | Count |
| --- | ---: |
| `reliable` | `1` |
| `caution` | `12` |
| `high-risk` | `35` |

The figure should state that the total is `48` scenarios and that these are conservative diagnostic screening labels, not calibrated probabilities. The presentation must not imply that warning-level frequency is a probability distribution or an operational forecast calibration result.

### `phase50_claim_boundary_matrix.png`

Show a clear supported-versus-not-supported claim matrix.

Supported:

- Level 4+ full-dataset proxy modeling route
- controlled `128x128` baseline
- reliability diagnostics
- physical proxy diagnostics
- conservative warning framework
- paper-ready evidence synthesis

Not supported:

- Level 5
- SWE/PINN
- strict conservation
- full mass conservation
- hydrodynamic closure
- calibrated probability labels
- final production readiness
- uncontrolled training expansion

The visual hierarchy should make unsupported claims at least as prominent as supported claims. It must not use ambiguous intermediate labels that weaken the current claim boundary.

### Optional: `phase50_reviewed_next_steps_matrix.png`

If included, show conservative Phase 51 candidate options and their review status:

- `128x128` seed42 longer-run review
- `128x128` seed replication after review
- `256x256` pilot after explicit authorization
- warning-framework case reporting
- manuscript development

The matrix should distinguish currently allowed reporting work from training options that require review or explicit authorization. It must not present any candidate training option as approved merely because it appears in the figure.

## Expected Output Directory

All generated figures should be written to:

```text
analysis/phase50_framework_consolidation/figures/
```

Expected required outputs:

```text
phase50_evidence_chain_overview.png
phase50_key_metrics_summary.png
phase50_warning_level_counts.png
phase50_claim_boundary_matrix.png
```

Optional output:

```text
phase50_reviewed_next_steps_matrix.png
```

The script should create the figure directory if it does not exist. Outputs should use consistent dimensions, typography, colors, margins, and export resolution suitable for GitHub README display and paper-outline reuse.

## README Update Plan

After the figures are generated and visually reviewed, add a new section immediately after the existing Phase 50 paragraph in `README.md`:

```markdown
Representative Phase 50 figures:

![Phase 50 evidence chain overview](analysis/phase50_framework_consolidation/figures/phase50_evidence_chain_overview.png)

![Phase 50 key metrics summary](analysis/phase50_framework_consolidation/figures/phase50_key_metrics_summary.png)

![Phase 50 warning level counts](analysis/phase50_framework_consolidation/figures/phase50_warning_level_counts.png)

![Phase 50 claim boundary matrix](analysis/phase50_framework_consolidation/figures/phase50_claim_boundary_matrix.png)
```

Link the optional reviewed-next-steps matrix only if it is generated, reviewed, and clearly preserves the Phase 51 authorization boundary. The existing Phase 24/25 figures should remain unless a separate documentation review decides otherwise.

## Guardrails

- No training.
- No new seed runs.
- No sweeps.
- No `256x256`, tile, multiscale, or full-`500` training.
- No model, loss, or config edits.
- No SWE residual.
- No PINN.
- No Level 5 support claim.
- No strict conservation claim.
- No full mass conservation claim.
- No hydrodynamic closure claim.
- No calibrated probability claim.
- No final production-readiness claim.
- No uncontrolled training expansion authorization.
- Do not alter or recompute source experiment metrics.
- Do not represent diagnostic warning labels as probabilities.
- Do not present physical proxy diagnostics as physics closure.
- Do not treat the optional next-steps figure as an experiment authorization record.

The plotting script may read existing result artifacts and write visualization files only. It must not invoke training entry points or modify model, loss, dataset, or experiment configuration code.

## Success Criteria

This visualization support step is successful when:

- the four required PNG figures are generated from the listed existing artifacts;
- all displayed metrics and counts match their source CSV/JSON values;
- the Phase 43-50 evidence sequence is complete and readable;
- the claim matrix clearly separates supported Level 4+ evidence from unsupported Level 5 and production claims;
- warning labels are explicitly described as conservative diagnostic screening labels, not probabilities;
- the figures are legible in the GitHub README at normal display width;
- visual styling is consistent across the figure set;
- the README receives a Representative Phase 50 figures section after the Phase 50 paragraph;
- no training, experiment expansion, model change, or new performance claim occurs.

The optional next-steps matrix is successful only if it clearly separates reporting options from reviewed or explicitly authorized training candidates.

## Final Conclusion

This step should improve README-facing and paper-facing visualization for the completed Phase 50 framework consolidation. It should make the Phase 43-50 evidence chain, key metrics, warning distribution, and claim boundaries visible before the Phase 51 reviewed expansion decision.

The work remains a no-training presentation layer over existing evidence. It does not change the current conclusion: the full-dataset Level 4+ proxy modeling and conservative warning-framework route is supported, while Level 5, SWE/PINN, strict or full mass conservation, hydrodynamic closure, calibrated probability labels, final production readiness, and uncontrolled training expansion remain unsupported.
