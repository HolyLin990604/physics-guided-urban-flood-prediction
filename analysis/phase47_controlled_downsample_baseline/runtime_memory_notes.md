# Phase 47 Runtime And Memory Notes

- Run scope: controlled 128x128 full-dataset downsample baseline, seed42 only.
- Dataset access: `numpy.load(..., mmap_mode="r")` for flood, rainfall, and static arrays.
- Downsampling: in-memory bilinear interpolation to 128x128 per batch/sample.
- Transformed training datasets written to disk: false.
- Future rainfall usage: known forcing, aligned by proportional bin mean over flood steps.
- SWE residuals and PINN components used: false.
- Batch size: `2`.
- Eval batch size: `2`.
- Runtime seconds: `1728.620`.
- Tracemalloc peak MB: `51.473`.
- CUDA max allocated MB: `943.691`.
- CUDA max reserved MB: `1246.000`.