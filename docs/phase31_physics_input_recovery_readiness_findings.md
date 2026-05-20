# Phase 31 Physics Input Recovery and Strong-Constraint Readiness Findings

## 1. Executive Summary

Phase 31 completed a diagnostic-only physics input recovery and strong-constraint readiness audit. It moved beyond the Phase 30 boundary synthesis by recovering and verifying additional physical inputs rather than continuing Phase 27 or Phase 29 loss tuning.

The main finding is conservative but technically useful:

**The project can now support Level 4+ structured physical proxy diagnostics, but it still cannot support Level 5 strong physics, strict mass conservation, SWE/PINN claims, or full hydrodynamic closure.**

Raw flood, rainfall, and static arrays are available. Shape-compatible static maps are available for `absolute_DEM.npy`, `impervious.npy`, and `manhole.npy`. These maps are 128 x 128, align with the representative flood-map shape, and are consistent between train and test geodata. Candidate valid-domain, invalid/high, boundary-ring, and interior masks can be constructed from the recovered static maps.

The recovered inputs are enough for domain-aware, boundary-aware, impervious-region, and manhole-region masked diagnostics. They are not enough for strict physical conservation or SWE residuals because aligned velocity/flux fields, explicit boundary source/sink variables, explicit `dx/dy`, explicit `dt`, and complete hydrodynamic state variables remain unavailable.

## 2. What Phase 31 Adds Beyond Phase 30

Phase 30 established the defensible boundary as a Level 4 conservation-proxy / physical-consistency-guided surrogate. It concluded that the project could support physical-consistency diagnosis and conservation-proxy evaluation, but not strict mass conservation, full SWE/PINN residuals, or hydrodynamic closure.

Phase 31 adds four concrete diagnostic advances:

1. It confirms that raw `flood.npy`, `rainfall.npy`, and static map arrays are locally available.
2. It verifies that shape-compatible static maps exist for DEM, imperviousness, and manhole indicators.
3. It constructs valid-domain, invalid/high, boundary-ring, and interior masks from static-map evidence.
4. It applies those masks to existing Phase 25, Phase 27, and Phase 29 prediction/target flood-depth rasters to produce Level 4+ masked physical error diagnostics.

This is an upgrade from unmasked depth-raster proxy evaluation to structured proxy diagnostics that use recovered physical context. It is not an upgrade to Level 5 strong physics.

## 3. Physics Input Inventory Findings

The Phase 31 physics input inventory found:

- Preliminary readiness classification: `Level 4+ possible`
- Level 5 status: `unsupported`
- Representative flood spatial shape: `[128, 128]`
- Raw flood/rain/static availability: flood=`True`, rainfall=`True`, static=`True`
- DEM/static elevation compatibility: `true`
- `dt` status: `inferred_ratio_only`
- `dx/dy` status: `candidate_mentions_only`

The inventory found 36 `flood.npy` files, 36 `rainfall.npy` files, and 18 static array files. Representative existing `forecast_maps.npz` outputs contain compatible `prediction`, `target`, and `error` arrays with 128 x 128 spatial shape.

The inventory supports recovery of useful static and temporal context, but only partially. Flood and rainfall sequence lengths provide timestep ratio evidence, not explicit physical timestep duration. Spatial resolution evidence remains limited to candidate mentions, not explicit usable `dx` and `dy` values.

Missing inputs remain:

- aligned velocity, flux, or discharge fields;
- aligned boundary inflow/outflow fields or complete boundary-condition metadata;
- source/sink, infiltration, drainage, or operation terms as aligned physical fields;
- explicit `dx/dy`;
- explicit physical `dt`.

## 4. Static Map Readiness

The static map inspection confirms that recovered geodata can support Level 4+ static-map-aware diagnostics.

Key findings:

- Static maps inspected: `18 / 18`
- Shape-compatible with 128 x 128 flood maps: `True`
- Train/test geodata consistency: `consistent_allclose`
- DEM valid-domain candidate: `supported_dem_lt_99`
- Level 4+ static-map-aware readiness: `supported`
- Level 5 status: `unsupported`

The shape-compatible static maps are:

- `absolute_DEM.npy`
- `impervious.npy`
- `manhole.npy`

For all three locations, static maps are 128 x 128. The train/test geodata are numerically consistent for the same location and channel.

The DEM maps contain values at or near `100.0`, which appear to be high, invalid, or no-data candidates. The inspection supports `absolute_DEM < 99` as a candidate valid-domain mask, with location valid ratios:

| Location | Valid ratio |
| --- | ---: |
| `location1` | 0.8190307617 |
| `location2` | 0.9536743164 |
| `location3` | 0.8607177734 |

Impervious and manhole maps are usable as static proxy descriptors. They support region-aware diagnostics, not hydrodynamic closure.

## 5. Domain and Boundary Mask Readiness

The domain/boundary mask construction step confirms that masks can be derived consistently from the recovered static maps.

Key findings:

- Locations processed: `3`
- All masks shape-compatible with 128 x 128 flood maps: `True`
- Valid-domain mask status: `supported_dem_lt_99`
- Boundary-ring mask status: `supported`
- Interior mask status: `supported`
- Train/test mask consistency: `consistent_equal`
- Level 4+ domain/boundary-aware readiness: `supported`
- Level 5 status: `unsupported`

The supported masks are:

- valid-domain mask from `absolute_DEM < 99`;
- invalid/high mask from DEM high/no-data candidate cells;
- boundary-ring mask from valid cells adjacent to invalid/high cells or the image border;
- interior mask from valid cells outside the boundary ring;
- high-impervious valid-region mask;
- manhole-nonzero valid-region mask.

These masks are suitable for masked depth-raster diagnostics. They do not establish true physical boundaries with measured inflow/outflow fluxes.

## 6. Masked Physical Error Diagnostics

Phase 31 recovered sample-to-location mapping for existing forecast maps from adjacent `evaluation_test/test_batch_*/summary.json` files using `metadata.location`. This was necessary because `forecast_maps.npz` stores arrays but not the location label directly.

Masked diagnostics are fully supported for the available forecast-map outputs.

Regions processed:

- `valid_domain`
- `interior`
- `boundary_ring`
- `high_impervious_valid`
- `manhole_nonzero_valid`
- `invalid_or_high`

The masked diagnostic classification is:

- Level 4+ masked diagnostic status: `supported`
- Level 5 status: `unsupported`

The `invalid_or_high` region is diagnostic-only and should not be treated as a physical target domain.

## 7. Interpretation of Phase 29 Under Masked Diagnostics

The masked diagnostics do not support a Phase 29 success claim.

For valid-domain masked diagnostics, Phase 29 improves the relative volume-bias proxy compared with Phase 27, but worsens most other masked error metrics:

| Metric | Phase 27 | Phase 29 | Interpretation |
| --- | ---: | ---: | --- |
| RMSE | 0.0460827 | 0.0480984 | worsened |
| MAE | 0.0183693 | 0.0190492 | worsened |
| false-dry rate | 0.0689175 | 0.0739891 | worsened |
| false-wet rate | 0.0181923 | 0.0194308 | worsened |
| false-dry volume-loss proxy | 3575.36 | 4027.38 | worsened |
| false-wet volume-excess proxy | 5263.67 | 5690.27 | worsened |
| relative volume-bias proxy | 0.0169359 | 0.0115344 | improved |

The correct interpretation is that Phase 29 reduces the valid-domain masked volume-bias proxy relative to Phase 27, but this comes with broader degradation in masked RMSE, MAE, false-dry behavior, false-wet behavior, and volume-loss/excess proxy terms.

Region-specific Phase 29 observations:

- `manhole_nonzero_valid` has the highest Phase 29 false-dry rate: `0.131298`
- `high_impervious_valid` has the highest Phase 29 false-wet rate: `0.0239894`

These results suggest useful diagnostic targets for future design, but they do not justify continuing Phase 29 training, seed expansion, or success language.

## 8. Current Readiness Classification

The current readiness classification is:

**Level 4+ structured physical proxy diagnostics supported.**

The current unsupported classification remains:

**Level 5 strong physics unsupported.**

Phase 31 provides stronger structure than Phase 30 because diagnostics can now be conditioned on valid domains, boundary rings, impervious regions, and manhole-nonzero regions. However, these are still proxy diagnostics over depth rasters and static masks.

## 9. What Level 4+ Now Supports

Phase 31 supports the following Level 4+ capabilities:

- domain-mask-aware depth error diagnostics;
- boundary-ring-aware wet/dry diagnostics;
- valid-domain-only volume-bias proxy diagnostics;
- invalid/high-region contrast diagnostics;
- high-impervious-region false-wet and error diagnostics;
- manhole-nonzero-region false-dry and error diagnostics;
- train/test-consistent static-map-aware analysis;
- sample-to-location-aware forecast-map diagnostics.

These capabilities are appropriate for physical consistency interpretation, failure-mode localization, and conservative design planning.

## 10. Why Level 5 Still Remains Unsupported

Level 5 remains unsupported because Phase 31 did not recover the required hydrodynamic variables and metadata for strong physics closure.

Still missing or insufficient:

- aligned velocity or flux fields;
- discharge fields;
- boundary inflow/outflow variables;
- source/sink terms such as drainage, infiltration, pump, gate, or sewer operation fields;
- explicit `dx` and `dy`;
- explicit physical `dt`;
- full hydrodynamic state variables needed for continuity or SWE residuals.

The recovered DEM, impervious, manhole, domain, and boundary-ring masks are valuable static context. They do not allow computation of full mass conservation, closed boundary fluxes, or shallow-water-equation residuals.

## 11. Recommended Next Technical Direction

If continuing technically, the next phase should be:

**Phase 32 - Domain-/Boundary-Aware Physical Consistency Design**

Possible Phase 32 directions:

- domain-mask-aware depth consistency diagnostics;
- boundary-ring-aware wet/dry diagnostics;
- high-impervious-region false-wet control;
- manhole-proximal false-dry diagnostics;
- dry-threshold guarded proxy refinement;
- diagnostic design that remains explicitly Level 4+ unless missing hydrodynamic variables are added.

Phase 32 should be a design and diagnostic-planning phase before immediate training. It should define objectives, metrics, masks, failure-mode criteria, and stop/go rules before any new loss or training run is proposed.

No SWE/PINN or strict-conservation work should be attempted unless the missing hydrodynamic variables and grid metadata are added.

## 12. Guardrails

The following guardrails remain active:

- Do not claim strict mass conservation.
- Do not claim full mass conservation.
- Do not claim SWE/PINN capability.
- Do not claim full hydrodynamic closure.
- Do not claim Level 5 strong physics.
- Do not claim Phase 29 success.
- Keep all Phase 31 results as Level 4+ proxy diagnostics.
- Do not recommend `seed123` or `seed202` training from Phase 29.
- Do not recommend immediate training before a Phase 32 plan.

Depth-raster volume sums should remain described as proxies unless explicit spatial resolution and hydrodynamic closure information are available.

## 13. Final Conclusion

Phase 31 confirms that the project has advanced beyond the Phase 30 Level 4 boundary by recovering shape-compatible static physical context and constructing consistent domain/boundary masks. The project can now support Level 4+ masked, static-map-aware, domain-aware, and boundary-aware physical proxy diagnostics.

At the same time, Phase 31 does not change the strongest physics boundary. Level 5 remains unsupported because the repository still lacks the aligned hydrodynamic state, velocity/flux, boundary/source-sink, `dx/dy`, and explicit `dt` information required for strict conservation, full SWE residuals, PINN claims, or hydrodynamic closure.

The next defensible technical step is Phase 32: domain-/boundary-aware physical consistency design, with conservative Level 4+ proxy framing and explicit guardrails before any further training.
