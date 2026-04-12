# Physics-Guided Urban Flood Process Prediction

A research prototype for physics-guided urban flood process prediction based on a U-Net + TCN framework.

## Overview

This repository implements a spatiotemporal urban flood forecasting prototype using the UrbanFlood24 Lite dataset.  
The baseline model is built on a U-Net + TCN architecture for multi-step flood process prediction.

On top of the baseline, a Phase 1 physics-guided model is implemented by adding two output-space regularization terms:

- Non-negativity loss
- Wet/dry consistency loss

These physics-guided losses are imposed on the predicted future flood depth field at the output layer, while the backbone architecture remains unchanged.

## Current Mainline

The current stable mainline is:

Phase 1 = Baseline + non-negativity loss + wet/dry consistency loss

In our current experiments, Phase 1 consistently outperforms the pure baseline under the same 20-epoch setting.

## Dataset

This project uses the UrbanFlood24 Lite dataset.

Expected dataset directory:

```text
data/
└─ urbanflood24_lite/
   ├─ train/
   └─ test/
```

The dataset contains:

 Dynamic flood depth sequences (`flood.npy`)
 Rainfall forcing sequences (`rainfall.npy`)
 Static geospatial factors:

   `absolute_DEM.npy`
   `impervious.npy`
   `manhole.npy`

## Task Definition

The task is multi-step flood process prediction.

Inputs:

Past flood sequence
Past rainfall sequence
Future rainfall sequence
Static maps

Output:

Future flood depth sequence

In the current setup, the model uses:

 `input_steps = 12`
 `pred_steps = 12`

## Method

### Baseline

 Backbone: U-Net + TCN
 Pure data-driven flood process prediction

### Phase 1 Physics Guidance

The Phase 1 model keeps the same backbone as the baseline, but adds two physics-guided loss terms on the predicted future flood depth field:

`L_total = L_data + λ1  L_nonneg + λ2  L_wd`

where:

 `L_data` = data fidelity loss
 `L_nonneg` = non-negativity loss
 `L_wd` = wet/dry consistency loss

These constraints are applied at the output layer, rather than inside the encoder, decoder, or temporal module.

## Repository Structure

```text
configs/
datasets/
models/
scripts/
trainers/
utils/
compare_maps.py
compare_timeseries.py
README.md
```

## Environment

Recommended environment:

```bash
conda create -n flood python=3.8 -y
conda activate flood
pip install -r requirements.txt
```

## Training

Train the baseline model:

```bash
python scripts/train_model.py --config configs/train_baseline.json
```

Train the Phase 1 model:

```bash
python scripts/train_model.py --config configs/train_stage2b_phase1.json
```

## Evaluation and Visualization

Example scripts:

```bash
python compare_maps.py
python compare_timeseries.py
```

## Current Results

Under the same 20-epoch setting, the current validated results are:

| Model    | Val RMSE | Val MAE | Val wet/dry IoU | Val rollout stability |
| -------- | -------: | ------: | --------------: | --------------------: |
| Baseline |   0.0774 |  0.0236 |          0.4281 |                0.9919 |
| Phase 1  |   0.0541 |  0.0185 |          0.6167 |                0.9915 |

These results indicate that lightweight output-space physics guidance can improve both flood depth prediction accuracy and wet-region boundary recovery without degrading rollout stability.

## Current Limitations

This repository is a research prototype, not a production-ready engineering system.

Current limitations include:

 Results are currently validated on UrbanFlood24 Lite
 More repeated experiments with different random seeds are still needed
 More external baselines can be added
 More advanced physics terms have not yet shown stable gains

## Future Work

Planned extensions include:

 Test-set evaluation
 Multi-seed experiments
 Stronger baselines
 More advanced hydrodynamic knowledge embedding
 Cross-scenario generalization analysis

## License

MIT License.


