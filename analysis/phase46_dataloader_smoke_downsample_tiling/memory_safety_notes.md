# Phase 46 Memory Safety Notes

- The smoke script used `numpy.load(..., mmap_mode="r")` for flood, rainfall, and static `.npy` access.
- Flood reads were bounded to the first `2` temporal frames per representative sample.
- Full flood sequences were not materialized in memory.
- No transformed training samples or downsampled datasets were written to disk.
- Downsample checks used small in-memory slices only and wrote compact CSV metadata.
- Tile checks extracted deterministic patches in memory only and did not write tiles to disk.
- No training, model forward pass, optimizer, loss computation, seed run, or sweep was executed.
- Variable full flood lengths 360 and 480 must be handled by future fixed-window sampling.
- Variable rainfall lengths 180 and 360 must be handled by future alignment rules.
- Phase 46 supports Level 4+ dataloader readiness evidence only; Level 5 support remains false.