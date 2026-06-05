# Phase 50 Paper-Ready Contribution Outline

## Suggested Paper Contribution Title

A Conservative Full-Dataset Proxy Modeling and Diagnostic Warning Framework for UrbanFlood24 Flood Prediction

## Core Research Contribution

This work contributes a paper-ready Level 4+ framework that consolidates full-dataset inspection, indexing, memory-safe data loading, controlled downsample baseline modeling, reliability diagnostics, physical proxy diagnostics, and conservative warning labels for UrbanFlood24 flood prediction.

## Dataset and Evidence Chain Paragraph

The evidence chain begins with UrbanFlood24 full-dataset inspection covering 354 files, 186 directories, and 54 sampled arrays. It then indexes 168 scenarios, including 120 train scenarios and 48 test scenarios, with six static-index rows and documented flood-shape and rainfall-length distributions. These steps support a full-dataset Level 4+ proxy modeling route while keeping Level 5 unsupported.

## Method/Framework Paragraph

The framework uses a no-training feasibility stage to verify scenario and static indexes, representative samples, 128x128 and 256x256 downsample paths, tiling checks, batch smoke checks, and memory-safe loading. A single controlled 128x128 seed42 10-epoch baseline then provides bounded proxy-modeling evidence without modifying the model, loss, or configuration family beyond the authorized baseline protocol.

## Results Paragraph

The controlled 128x128 baseline used 960 training samples and 384 test samples, achieving best test RMSE 0.01109213042097205, test MAE 0.00525291082279485, test wet/dry IoU 0.8255524213115374, and test rollout stability 0.998722607580324. These results support baseline viability, not seed robustness or production readiness.

## Reliability/Warning Framework Paragraph

No-training diagnostics evaluated 48 scenarios and 384 windows, with mean RMSE 0.012037189189155709, mean MAE 0.005252910632811514, mean wet/dry IoU 0.863043953275997, mean false-dry rate 0.0911363765964386, mean false-wet rate 0.003937674554837349, and mean absolute relative volume-bias proxy 0.021456503649973275. The warning framework assigns 1 reliable, 12 caution, and 35 high-risk labels. These warning labels are conservative diagnostic screening labels, not calibrated probabilities.

## Limitations Paragraph

The current evidence does not support Level 5, SWE residual or PINN claims, strict conservation, full mass conservation, hydrodynamic closure, calibrated probability warning labels, or final production readiness. The controlled baseline is a single seed42 10-epoch run at 128x128 resolution, so broader training claims require reviewed expansion.

## Next-Step Paragraph

The recommended next step is a Phase 51 reviewed expansion decision. Conservative options include reviewing a longer 128x128 seed42 run, considering seed replication only after review, allowing a 256x256 pilot only after explicit authorization, reporting warning-framework cases, and using this outline for manuscript development under the stated claim boundaries.
