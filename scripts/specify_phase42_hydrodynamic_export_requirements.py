from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = Path("analysis/phase42_hydrodynamic_export_requirements")

DECISION_CANDIDATES = (
    "export_contract_ready_for_dataset_inspection",
    "export_contract_ready_for_icm_mike_request",
    "export_contract_incomplete_needs_review",
)

SELECTED_DECISION = "export_contract_ready_for_dataset_inspection"

GUARDRAILS = (
    "no training",
    "no seed runs",
    "no sweeps",
    "no loss modification",
    "no config modification",
    "no model architecture modification",
    "no SWE residual implementation",
    "no PINN implementation",
    "no strict conservation claim",
    "no full mass conservation claim",
    "no hydrodynamic closure claim",
    "no Level 5 support claim",
)

FIELD_COLUMNS = (
    "field_name",
    "physical_meaning",
    "required_for_level5",
    "required_for_continuity_residual",
    "required_for_momentum_residual",
    "required_for_mass_balance_diagnostic",
    "acceptable_variable_names",
    "expected_units",
    "expected_shape",
    "expected_time_axis",
    "expected_grid_alignment",
    "source_model_examples",
    "export_priority",
    "can_be_missing_for_level4_proxy",
    "missing_consequence",
    "notes",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Phase 42 no-training hydrodynamic export requirement specification. "
            "Writes data-contract CSV/JSON/Markdown artifacts only; does not train, "
            "edit losses/configs/models, or implement SWE/PINN residuals."
        )
    )
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    return parser.parse_args()


def repo_path(path: Path) -> Path:
    return path if path.is_absolute() else REPO_ROOT / path


def bool_text(value: bool) -> str:
    return str(value).lower()


def field_rows() -> list[dict[str, Any]]:
    rows = [
        {
            "field_name": "water_depth_h",
            "physical_meaning": "2D water depth above terrain or bed elevation for each exported hydrodynamic state.",
            "required_for_level5": True,
            "required_for_continuity_residual": True,
            "required_for_momentum_residual": True,
            "required_for_mass_balance_diagnostic": True,
            "acceptable_variable_names": "h; depth; water_depth; flood_depth; flood; water_level_minus_bed",
            "expected_units": "m or documented convertible depth unit",
            "expected_shape": "dynamic raster h(t,y,x) or mesh/cell field with remapping metadata",
            "expected_time_axis": "explicit timestamps or timestep indices aligned to rainfall, velocity/flux, boundary, and source/sink fields",
            "expected_grid_alignment": "same grid as target flood arrays, or documented conservative remap from source mesh/cells",
            "source_model_examples": "InfoWorks ICM 2D depth; MIKE+ 2D water depth; UrbanFlood24 full depth/flood arrays",
            "export_priority": "P0",
            "can_be_missing_for_level4_proxy": False,
            "missing_consequence": "Blocks even depth-based target verification and blocks future SWE residual consideration.",
            "notes": "Depth alone is insufficient for Level 5 but is a core state variable.",
        },
        {
            "field_name": "velocity_u_v",
            "physical_meaning": "Horizontal velocity components in grid x and y directions.",
            "required_for_level5": True,
            "required_for_continuity_residual": False,
            "required_for_momentum_residual": True,
            "required_for_mass_balance_diagnostic": False,
            "acceptable_variable_names": "u; v; velocity_x; velocity_y; vel_x; vel_y; Vx; Vy",
            "expected_units": "m/s with documented axis and sign convention",
            "expected_shape": "u(t,y,x) and v(t,y,x), or mesh/cell components with remapping metadata",
            "expected_time_axis": "same hydrodynamic output times as h, or documented interpolation relationship",
            "expected_grid_alignment": "aligned to h; state whether cell-centered, node-centered, face-centered, or mesh-based",
            "source_model_examples": "InfoWorks ICM velocity vector exports; MIKE+ velocity components",
            "export_priority": "P0",
            "can_be_missing_for_level4_proxy": True,
            "missing_consequence": "Blocks momentum residuals and full hydrodynamic state closure; depth-only work remains Level 4 proxy.",
            "notes": "Flux qx/qy may substitute for some continuity-style reviews but does not remove the need for transport fields.",
        },
        {
            "field_name": "flux_qx_qy",
            "physical_meaning": "Specific discharge, flow per unit width, or discharge/flux components across the grid.",
            "required_for_level5": True,
            "required_for_continuity_residual": True,
            "required_for_momentum_residual": True,
            "required_for_mass_balance_diagnostic": True,
            "acceptable_variable_names": "qx; qy; flux_x; flux_y; discharge_x; discharge_y; flow_x; flow_y; momentum_x; momentum_y",
            "expected_units": "m2/s, m3/s, discharge per width, or documented equivalent with conversion notes",
            "expected_shape": "qx(t,y,x) and qy(t,y,x), face fields, link fields, or mesh fields with geometry metadata",
            "expected_time_axis": "aligned to h time axis and output cadence",
            "expected_grid_alignment": "aligned to h or mapped to cell faces/centers with orientation and sign convention",
            "source_model_examples": "InfoWorks ICM flow/discharge exports; MIKE+ flux/discharge results",
            "export_priority": "P0",
            "can_be_missing_for_level4_proxy": True,
            "missing_consequence": "Blocks continuity residual and mass-balance closure unless velocity plus depth and geometry can form flux.",
            "notes": "If both u/v and qx/qy exist, export both with conversion relationship.",
        },
        {
            "field_name": "dx_dy_grid_spacing",
            "physical_meaning": "Physical spacing or mesh geometry needed for spatial derivatives and cell areas.",
            "required_for_level5": True,
            "required_for_continuity_residual": True,
            "required_for_momentum_residual": True,
            "required_for_mass_balance_diagnostic": True,
            "acceptable_variable_names": "dx; dy; cell_size; grid_spacing; resolution; pixel_size; mesh_geometry; cell_area",
            "expected_units": "m or projected-coordinate units convertible to m",
            "expected_shape": "scalar dx/dy for uniform raster, per-cell arrays, or mesh geometry tables",
            "expected_time_axis": "static unless the source grid changes; versioned with scenario/export metadata",
            "expected_grid_alignment": "must define x/y orientation, origin, row/column order, and any mesh-to-raster mapping",
            "source_model_examples": "ICM 2D mesh/cell geometry; MIKE+ mesh geometry; UrbanFlood24 grid metadata",
            "export_priority": "P0",
            "can_be_missing_for_level4_proxy": True,
            "missing_consequence": "Blocks physical derivatives, volume conversion, and residual scaling.",
            "notes": "Matching array shape is not enough; physical spacing and units must be explicit.",
        },
        {
            "field_name": "dt_time_step",
            "physical_meaning": "Physical timestep or output interval between hydrodynamic states.",
            "required_for_level5": True,
            "required_for_continuity_residual": True,
            "required_for_momentum_residual": True,
            "required_for_mass_balance_diagnostic": True,
            "acceptable_variable_names": "dt; timestep; time_step; output_interval; temporal_resolution; cadence",
            "expected_units": "seconds, minutes, hours, or documented convertible temporal unit",
            "expected_shape": "scalar for regular cadence, or vector dt(t) for irregular output",
            "expected_time_axis": "explicit timestamps, timestep indices, start/end time, and cadence for all dynamic fields",
            "expected_grid_alignment": "not spatial, but must align every dynamic field and scenario horizon",
            "source_model_examples": "ICM result timestep; MIKE+ output timestep; UrbanFlood24 temporal metadata",
            "export_priority": "P0",
            "can_be_missing_for_level4_proxy": True,
            "missing_consequence": "Blocks temporal derivatives and physical source/rainfall rate conversion.",
            "notes": "File ordering alone is not acceptable evidence of physical dt.",
        },
        {
            "field_name": "DEM_or_bed_elevation",
            "physical_meaning": "Terrain, bed, or ground elevation used to compute water surface and slope terms.",
            "required_for_level5": True,
            "required_for_continuity_residual": False,
            "required_for_momentum_residual": True,
            "required_for_mass_balance_diagnostic": False,
            "acceptable_variable_names": "DEM; dem; bed_elevation; terrain; ground_elevation; z; zb; static_elevation",
            "expected_units": "m with vertical datum or documented convertible elevation unit",
            "expected_shape": "static raster z(y,x), per-cell mesh field, or aligned static map",
            "expected_time_axis": "static for each scenario unless terrain changes are modeled",
            "expected_grid_alignment": "same grid as h or remapped with documented interpolation/rasterization",
            "source_model_examples": "ICM ground model; MIKE+ bathymetry/terrain; UrbanFlood24 static maps",
            "export_priority": "P0",
            "can_be_missing_for_level4_proxy": True,
            "missing_consequence": "Blocks bed-slope and momentum residual terms and weakens terrain-aware diagnostics.",
            "notes": "Record vertical datum, nodata, and whether values are bed, ground, or DEM proxies.",
        },
        {
            "field_name": "rainfall_source",
            "physical_meaning": "Precipitation forcing supplied to the hydrodynamic model or dataset scenario.",
            "required_for_level5": True,
            "required_for_continuity_residual": True,
            "required_for_momentum_residual": False,
            "required_for_mass_balance_diagnostic": True,
            "acceptable_variable_names": "rainfall; rain; precipitation; precip; rainfall_rate; rain_intensity",
            "expected_units": "mm/interval, mm/h, m/s, or documented forcing convention",
            "expected_shape": "rain(t,y,x), rain(t), rain(event,t), or source polygons with remapping metadata",
            "expected_time_axis": "interval start/end times aligned to h and dt",
            "expected_grid_alignment": "aligned to h grid, or documented spatial distribution/remapping from gauges or polygons",
            "source_model_examples": "ICM rainfall hyetographs/spatial rainfall; MIKE+ rainfall boundary/source; UrbanFlood24 rainfall.npy",
            "export_priority": "P0",
            "can_be_missing_for_level4_proxy": False,
            "missing_consequence": "Blocks continuity source term and mass-balance forcing review.",
            "notes": "Distinguish instantaneous rates from accumulated interval depths.",
        },
        {
            "field_name": "boundary_conditions",
            "physical_meaning": "Open, wall, inflow, outflow, stage, water-level, rating-curve, or control boundary definitions and values.",
            "required_for_level5": True,
            "required_for_continuity_residual": True,
            "required_for_momentum_residual": True,
            "required_for_mass_balance_diagnostic": True,
            "acceptable_variable_names": "boundary; inflow; outflow; stage; water_level; open_boundary; rating_curve; upstream; downstream",
            "expected_units": "stage/depth in m, discharge in m3/s, velocity in m/s, flux in m2/s, or typed boundary metadata",
            "expected_shape": "boundary table plus time series; boundary raster/mask; face/link/node values over time",
            "expected_time_axis": "time-varying values aligned to h if dynamic; fixed values marked explicitly",
            "expected_grid_alignment": "boundary locations mapped to cells, faces, links, nodes, or masks on the h grid",
            "source_model_examples": "ICM 2D/1D boundary definitions; MIKE+ boundary conditions",
            "export_priority": "P0",
            "can_be_missing_for_level4_proxy": True,
            "missing_consequence": "Blocks treatment of open boundaries and can invalidate residual or mass-balance interpretation.",
            "notes": "Boundary values must not be silently inferred from interior cells.",
        },
        {
            "field_name": "source_sink_terms",
            "physical_meaning": "Non-rainfall source/sink terms such as infiltration, drainage, sewer exchange, lateral inflow, evaporation, abstraction, or storage exchange.",
            "required_for_level5": True,
            "required_for_continuity_residual": True,
            "required_for_momentum_residual": False,
            "required_for_mass_balance_diagnostic": True,
            "acceptable_variable_names": "source; sink; infiltration; drainage; sewer; outfall; inlet; lateral_flow; evaporation; abstraction",
            "expected_units": "m/s, mm/interval, m3/s, cell-normalized discharge, or documented model convention",
            "expected_shape": "time-varying raster, point/link table, source polygon table, or documented zero/closure metadata",
            "expected_time_axis": "aligned to h, rainfall, and boundary time axis",
            "expected_grid_alignment": "mapped to cells, faces, links, nodes, or source polygons with sign convention",
            "source_model_examples": "ICM sewer/drainage/outfall exchange; MIKE+ source/sink and network exchange outputs",
            "export_priority": "P0",
            "can_be_missing_for_level4_proxy": True,
            "missing_consequence": "Blocks complete continuity closure and full mass-balance claims.",
            "notes": "Missing terms may be treated as zero only with explicit source-model documentation.",
        },
        {
            "field_name": "pump_gate_operations",
            "physical_meaning": "Controlled infrastructure states, openings, rule states, and flows.",
            "required_for_level5": True,
            "required_for_continuity_residual": True,
            "required_for_momentum_residual": True,
            "required_for_mass_balance_diagnostic": True,
            "acceptable_variable_names": "pump; gate; sluice; valve; control; operation; opening; pump_flow; gate_flow",
            "expected_units": "state/category, opening fraction, m, m3/s, or documented control schedule units",
            "expected_shape": "operation time series by asset plus mapped asset location or affected links/cells",
            "expected_time_axis": "aligned to scenario time axis and source/sink or boundary series",
            "expected_grid_alignment": "asset locations mapped to nodes, links, cells, faces, or boundary/source terms",
            "source_model_examples": "ICM pump/gate controls; MIKE+ structures and control rules",
            "export_priority": "P1",
            "can_be_missing_for_level4_proxy": True,
            "missing_consequence": "Blocks closure wherever controlled assets affect flows; absence must be documented if not represented.",
            "notes": "Required when the source hydrodynamic model contains controlled infrastructure.",
        },
        {
            "field_name": "valid_domain_mask",
            "physical_meaning": "Cells or elements where hydrodynamic states are valid and residual/diagnostic evaluation may be considered.",
            "required_for_level5": True,
            "required_for_continuity_residual": True,
            "required_for_momentum_residual": True,
            "required_for_mass_balance_diagnostic": True,
            "acceptable_variable_names": "valid_domain; domain_mask; valid_mask; wettable_area; active_cell_mask",
            "expected_units": "boolean, integer, or categorical encoding with documented meaning",
            "expected_shape": "mask(y,x), mask(t,y,x) if active domain changes, or mesh/cell mask",
            "expected_time_axis": "static or dynamic status explicitly documented",
            "expected_grid_alignment": "same grid/elements as h and all diagnostic fields",
            "source_model_examples": "ICM active 2D zone; MIKE+ computational domain; UrbanFlood24 valid-domain mask if provided",
            "export_priority": "P0",
            "can_be_missing_for_level4_proxy": True,
            "missing_consequence": "Blocks reliable masking of nodata/outside-domain cells.",
            "notes": "Nodata values are not a substitute for explicit mask semantics.",
        },
        {
            "field_name": "boundary_mask",
            "physical_meaning": "Cells, faces, links, nodes, or elements that lie on physical or computational boundaries.",
            "required_for_level5": True,
            "required_for_continuity_residual": True,
            "required_for_momentum_residual": True,
            "required_for_mass_balance_diagnostic": True,
            "acceptable_variable_names": "boundary_mask; open_boundary_mask; wall_mask; boundary_ring; edge_mask",
            "expected_units": "boolean, integer, or categorical encoding by boundary type",
            "expected_shape": "mask(y,x), face mask, link/node table, or mesh boundary element table",
            "expected_time_axis": "static unless boundary types or active boundaries change by scenario/time",
            "expected_grid_alignment": "aligned to h plus boundary-condition locations and values",
            "source_model_examples": "ICM boundary polygons/links; MIKE+ boundary definitions; repository boundary-ring masks",
            "export_priority": "P0",
            "can_be_missing_for_level4_proxy": True,
            "missing_consequence": "Blocks boundary-aware residual handling and boundary mass-balance accounting.",
            "notes": "Boundary mask and boundary values are both required for future residual feasibility review.",
        },
        {
            "field_name": "coordinate_reference_or_grid_metadata",
            "physical_meaning": "CRS, projection, origin, orientation, axis order, grid indexing, and mapping metadata.",
            "required_for_level5": True,
            "required_for_continuity_residual": True,
            "required_for_momentum_residual": True,
            "required_for_mass_balance_diagnostic": True,
            "acceptable_variable_names": "crs; epsg; projection; transform; affine; origin; x_coords; y_coords; mesh_nodes; mesh_elements",
            "expected_units": "CRS identifier plus projected coordinate units, or full local-coordinate definition",
            "expected_shape": "metadata object, affine transform, coordinate vectors, or mesh geometry tables",
            "expected_time_axis": "static per scenario/export unless moving mesh is used",
            "expected_grid_alignment": "defines relation between source hydrodynamic export and repository flood/rain/static arrays",
            "source_model_examples": "ICM GIS export metadata; MIKE+ projection/mesh metadata; UrbanFlood24 grid metadata",
            "export_priority": "P0",
            "can_be_missing_for_level4_proxy": True,
            "missing_consequence": "Blocks defensible spatial alignment and physical derivative interpretation.",
            "notes": "Array dimensions alone do not prove physical alignment.",
        },
        {
            "field_name": "units_and_scaling",
            "physical_meaning": "Units, scaling factors, nodata conventions, sign conventions, and conversion rules.",
            "required_for_level5": True,
            "required_for_continuity_residual": True,
            "required_for_momentum_residual": True,
            "required_for_mass_balance_diagnostic": True,
            "acceptable_variable_names": "units; scale; scaling; nodata; fill_value; sign_convention; conversion",
            "expected_units": "metadata for each exported variable",
            "expected_shape": "metadata table keyed by variable/file/field",
            "expected_time_axis": "versioned with export; time-varying units are not acceptable without explicit conversion",
            "expected_grid_alignment": "applies consistently across aligned fields and remapped products",
            "source_model_examples": "ICM result unit metadata; MIKE+ result metadata; dataset README/data dictionary",
            "export_priority": "P0",
            "can_be_missing_for_level4_proxy": False,
            "missing_consequence": "Blocks physical interpretation and any residual or conservation-style claim.",
            "notes": "Every dynamic and static field must have unit and scaling evidence.",
        },
        {
            "field_name": "scenario_metadata",
            "physical_meaning": "Scenario/event identifiers, model version, run settings, export timestamp, return period, duration, and location.",
            "required_for_level5": True,
            "required_for_continuity_residual": False,
            "required_for_momentum_residual": False,
            "required_for_mass_balance_diagnostic": True,
            "acceptable_variable_names": "scenario; event_id; location; return_period; duration; model_version; run_id; export_time",
            "expected_units": "metadata identifiers and documented parameter units where applicable",
            "expected_shape": "metadata table keyed by scenario/event/file group",
            "expected_time_axis": "links all dynamic fields belonging to the same event and horizon",
            "expected_grid_alignment": "links each scenario to the grid/mesh, static maps, rainfall, boundaries, and source/sink exports",
            "source_model_examples": "ICM run metadata; MIKE+ scenario metadata; UrbanFlood24 event/location metadata",
            "export_priority": "P1",
            "can_be_missing_for_level4_proxy": True,
            "missing_consequence": "Blocks reproducibility and can mix incompatible event fields.",
            "notes": "Needed to prevent accidental cross-scenario alignment.",
        },
        {
            "field_name": "time_axis_metadata",
            "physical_meaning": "Timestamp, timestep index, cadence, timezone/reference convention, spin-up, warm-up, and horizon metadata.",
            "required_for_level5": True,
            "required_for_continuity_residual": True,
            "required_for_momentum_residual": True,
            "required_for_mass_balance_diagnostic": True,
            "acceptable_variable_names": "time; timestamp; timestep; step; time_index; start_time; end_time; warmup; spinup",
            "expected_units": "ISO timestamps, seconds since reference, minutes since event start, or documented equivalent",
            "expected_shape": "time vector or metadata table for every dynamic field",
            "expected_time_axis": "single reconciled axis for h, u/v or qx/qy, rainfall, boundaries, sources/sinks, and controls",
            "expected_grid_alignment": "not spatial, but must map each time slice to the correct scenario/grid fields",
            "source_model_examples": "ICM result timestamps; MIKE+ result timestamps; UrbanFlood24 sequence metadata",
            "export_priority": "P0",
            "can_be_missing_for_level4_proxy": True,
            "missing_consequence": "Blocks temporal derivatives and dynamic forcing alignment.",
            "notes": "Must document irregular intervals, missing timesteps, spin-up, and warm-up handling.",
        },
    ]
    return [{key: bool_text(value) if isinstance(value, bool) else value for key, value in row.items()} for row in rows]


def unit_shape_time_rows(fields: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "field_name": row["field_name"],
            "expected_units": row["expected_units"],
            "expected_shape": row["expected_shape"],
            "expected_time_axis": row["expected_time_axis"],
            "expected_grid_alignment": row["expected_grid_alignment"],
            "metadata_required": "units; shape; axis order; nodata; source file/table; scenario id; conversion notes",
            "conversion_notes": (
                "Convert to SI-compatible units before any future residual feasibility review; "
                "record original source units and sign conventions."
            ),
        }
        for row in fields
    ]


def minimum_contract_rows() -> list[dict[str, Any]]:
    items = [
        ("MC01", "water_depth_h", "aligned h(t,y,x)", "Depth or documented equivalent must be aligned to the target grid/time axis."),
        ("MC02", "velocity_u_v_or_flux_qx_qy", "either u/v or qx/qy aligned to h", "At least one transport representation must align to h with units and sign convention."),
        ("MC03", "dx_dy_grid_spacing", "dx/dy with physical units", "Physical grid spacing, cell areas, or mesh geometry must be explicit."),
        ("MC04", "dt_time_step", "dt with physical units", "Regular or irregular timestep duration must be explicit and aligned to all dynamic fields."),
        ("MC05", "DEM_or_bed_elevation", "DEM or bed elevation aligned to h", "Terrain/bed elevation must align to the hydrodynamic state grid or include remapping metadata."),
        ("MC06", "rainfall_source", "rainfall source aligned to h time axis", "Rainfall rates or interval accumulations must be aligned to h and dt."),
        ("MC07", "boundary_conditions", "boundary mask and boundary values / boundary conditions", "Boundary locations, types, values, units, and time series must be documented."),
        ("MC08", "source_sink_terms", "complete source/sink documentation", "All non-rain source/sink terms must be exported or explicitly closed by documentation."),
        ("MC09", "valid_domain_mask", "valid-domain mask", "A mask must identify cells/elements where states and diagnostics are valid."),
        ("MC10", "scenario_metadata_and_units", "scenario metadata and units", "Scenario/event metadata plus units/scaling/sign/nodata conventions must be complete."),
    ]
    rows = []
    for item_id, category, requirement, evidence in items:
        rows.append(
            {
                "contract_item": item_id,
                "field_category": category,
                "minimum_requirement": requirement,
                "required_evidence": evidence,
                "allowed_absence_condition": "none for minimum contract unless source documentation proves a physically valid closure",
                "level5_blocking_if_absent": "true",
                "interpretation": "Required before any future SWE residual prototype can be considered; this does not authorize implementation.",
            }
        )
    return rows


def priority_rows(fields: list[dict[str, Any]]) -> list[dict[str, Any]]:
    recommended_source = {
        "water_depth_h": "UrbanFlood24 full dataset or ICM/MIKE+ 2D depth export",
        "velocity_u_v": "ICM/MIKE+ velocity exports; UrbanFlood24 full if available",
        "flux_qx_qy": "ICM/MIKE+ flux/discharge exports; UrbanFlood24 full if available",
        "dx_dy_grid_spacing": "Source grid/mesh metadata and dataset documentation",
        "dt_time_step": "Source result metadata and dataset documentation",
        "DEM_or_bed_elevation": "Source terrain/bed export and UrbanFlood24 static maps",
        "rainfall_source": "Dataset rainfall arrays or source-model rainfall forcing",
        "boundary_conditions": "ICM/MIKE+ boundary definitions and time series",
        "source_sink_terms": "ICM/MIKE+ source/sink and network exchange exports",
        "pump_gate_operations": "ICM/MIKE+ structures/control exports",
        "valid_domain_mask": "Source model computational domain or repository/domain masks",
        "boundary_mask": "Source boundary elements or derived boundary mask with documented method",
        "coordinate_reference_or_grid_metadata": "Source GIS/projection/mesh metadata",
        "units_and_scaling": "Source result metadata, README, or data dictionary",
        "scenario_metadata": "Source run/scenario metadata",
        "time_axis_metadata": "Source result timestamps and dataset sequence metadata",
    }
    rows = []
    for row in fields:
        field_name = row["field_name"]
        priority = row["export_priority"]
        rows.append(
            {
                "priority": priority,
                "field_name": field_name,
                "reason": row["missing_consequence"],
                "recommended_source": recommended_source[field_name],
                "inspection_or_request_action": (
                    "Inspect downloaded UrbanFlood24 full files first; request equivalent ICM/MIKE+ export if absent."
                    if priority == "P0"
                    else "Request or document during external model export review."
                ),
                "notes": row["notes"],
            }
        )
    return rows


def urbanflood24_checklist_rows() -> list[dict[str, Any]]:
    items = [
        ("UF24-01", "file tree scan", "List full dataset files, folders, extensions, sizes, and scenario grouping without training."),
        ("UF24-02", "search for velocity / flux / qx / qy / u / v / discharge", "Search names, metadata, tables, and arrays for transport-state variables."),
        ("UF24-03", "search for dx/dy/dt metadata", "Find explicit physical grid spacing and timestep cadence with units."),
        ("UF24-04", "search for boundary / inflow / outflow / stage / water_level", "Identify boundary definitions, locations, and time-varying values."),
        ("UF24-05", "search for pump/gate/source/sink metadata", "Identify controlled structures and non-rain source/sink terms or documented absences."),
        ("UF24-06", "verify flood.npy/rainfall.npy/static maps shape", "Record shape, dtype, axis order, and scenario linkage for known arrays."),
        ("UF24-07", "verify 500x500 or other full-resolution shapes if present", "Record whether full-resolution arrays differ from lite 128x128 products."),
        ("UF24-08", "verify 1-minute or other time interval metadata if present", "Record cadence, output interval, timestamps, spin-up, and warm-up handling."),
        ("UF24-09", "record whether full dataset is still depth/rainfall/static-only", "State if full export lacks velocity/flux, boundary, and source/sink fields."),
        ("UF24-10", "record whether Level 5 variables are actually present", "Record present/absent/uncertain for each minimum contract item without claiming Level 5 support."),
    ]
    return [
        {
            "check_id": check_id,
            "check_item": item,
            "inspection_requirement": requirement,
            "expected_evidence": "file path(s), metadata excerpt summary, shape/unit/time/grid evidence, and present/absent/uncertain status",
            "training_allowed": "false",
            "level5_claim_allowed": "false",
            "notes": "Checklist item only; no dataset inspection is performed by Phase 42.",
        }
        for check_id, item, requirement in items
    ]


def icm_mike_checklist_rows() -> list[dict[str, Any]]:
    items = [
        ("EXT-01", "2D water depth", "Export depth or water level plus bed elevation needed to recover depth."),
        ("EXT-02", "2D velocity vector or flux/discharge components", "Export u/v and/or qx/qy with axis, sign, centering, and units."),
        ("EXT-03", "timestep duration", "Export simulation timestep and output timestep metadata."),
        ("EXT-04", "cell size / grid spacing / mesh geometry", "Export raster cell size or full mesh nodes/elements/cell areas."),
        ("EXT-05", "terrain / bed elevation", "Export DEM, bed elevation, ground model, vertical datum, and nodata values."),
        ("EXT-06", "boundary inflow/outflow/water-level series", "Export boundary type, location, values, units, and time series."),
        ("EXT-07", "rainfall source series", "Export rainfall forcing as rates or interval depths plus spatial allocation."),
        ("EXT-08", "sewer/drainage/outfall/source-sink exchange", "Export all represented lateral, drainage, sewer, outfall, infiltration, and loss terms."),
        ("EXT-09", "pump/gate operation states and flows", "Export control states, schedules, openings, and realized flows."),
        ("EXT-10", "coordinate reference system", "Export CRS/EPSG, projection units, origin, orientation, and vertical datum."),
        ("EXT-11", "scenario/event metadata", "Export scenario name, event ID, model version, run settings, and export timestamp."),
        ("EXT-12", "export units and scaling", "Export units, scaling, nodata, sign conventions, and conversion notes for every field."),
        ("EXT-13", "alignment rules to current flood/rain/static arrays", "Document how source mesh/grid fields map to repository arrays and event horizons."),
    ]
    return [
        {
            "request_id": request_id,
            "export_requirement": requirement,
            "details": details,
            "required_for_minimum_contract": "true",
            "acceptable_source_models": "InfoWorks ICM; MIKE+; UrbanFlood24 full dataset; equivalent hydrodynamic source",
            "blocking_if_absent": "true",
            "notes": "Required for future SWE residual feasibility review; does not authorize implementation.",
        }
        for request_id, requirement, details in items
    ]


def write_csv(path: Path, rows: list[dict[str, Any]], columns: tuple[str, ...] | list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fieldnames = list(columns or rows[0].keys())
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_markdown(path: Path, summary: dict[str, Any], fields: list[dict[str, Any]], contract: list[dict[str, Any]]) -> None:
    lines = [
        "# Phase 42 Hydrodynamic Export Requirement Specification",
        "",
        "Phase 42 is a no-training specification only. It creates the data contract required before future Level 5 SWE-oriented work can be considered.",
        "",
        "It does not claim Level 5 support. It does not implement SWE residuals. It does not implement PINN components. It does not authorize training.",
        "",
        "## Decision",
        "",
        f"- Selected decision: `{summary['selected_decision']}`",
        f"- Training authorized: `{str(summary['training_authorized']).lower()}`",
        f"- Level 5 supported: `{str(summary['level5_supported']).lower()}`",
        f"- SWE residual implementation authorized: `{str(summary['swe_residual_implementation_authorized']).lower()}`",
        f"- External export needed: `{str(summary['external_export_needed']).lower()}`",
        "",
        "## What This Contract Clarifies",
        "",
        "This contract clarifies what must be exported or recovered before SWE/PINN work can be considered: aligned depth, velocity or flux, physical dx/dy, physical dt, DEM or bed elevation, rainfall, boundary conditions, complete source/sink terms, valid-domain masks, units, scenario metadata, and time-axis metadata.",
        "",
        "## Required Hydrodynamic Field Categories",
        "",
        "| Field | Priority | Required for Level 5 | Missing consequence |",
        "| --- | --- | --- | --- |",
    ]
    for row in fields:
        lines.append(
            f"| `{row['field_name']}` | `{row['export_priority']}` | `{row['required_for_level5']}` | {row['missing_consequence']} |"
        )

    lines.extend(
        [
            "",
            "## Minimum SWE Residual Data Contract",
            "",
            "| Item | Category | Minimum requirement |",
            "| --- | --- | --- |",
        ]
    )
    for row in contract:
        lines.append(
            f"| `{row['contract_item']}` | `{row['field_category']}` | {row['minimum_requirement']} |"
        )

    lines.extend(
        [
            "",
            "## Guardrails",
            "",
        ]
    )
    lines.extend(f"- {guardrail}" for guardrail in summary["guardrails"])
    lines.extend(
        [
            "",
            "No strict conservation, full mass conservation, hydrodynamic closure, SWE/PINN support, or Level 5 support claim is made.",
            "",
            "## Next Recommended Action",
            "",
            summary["next_recommended_action"],
            "",
            "Inspect the UrbanFlood24 full dataset if available and/or request/export the required fields from InfoWorks ICM, MIKE+, or an equivalent hydrodynamic source.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def build_summary(
    fields: list[dict[str, Any]],
    contract: list[dict[str, Any]],
    urbanflood24_checks: list[dict[str, Any]],
    icm_mike_checks: list[dict[str, Any]],
) -> dict[str, Any]:
    required_outputs = [
        "required_hydrodynamic_fields.csv",
        "field_unit_shape_time_requirements.csv",
        "swe_residual_minimum_data_contract.csv",
        "export_priority_table.csv",
        "urbanflood24_full_inspection_checklist.csv",
        "icm_mike_export_checklist.csv",
        "phase42_export_requirement_summary.json",
        "phase42_export_requirement_summary.md",
    ]
    complete = (
        len(fields) == 16
        and len(contract) == 10
        and len(urbanflood24_checks) == 10
        and len(icm_mike_checks) == 13
        and SELECTED_DECISION in DECISION_CANDIDATES
    )
    selected = SELECTED_DECISION if complete else "export_contract_incomplete_needs_review"
    return {
        "phase": 42,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "script": "scripts/specify_phase42_hydrodynamic_export_requirements.py",
        "phase41_readiness_decision": "readiness_uncertain_requires_external_data_export",
        "phase41_level5_supported": False,
        "phase41_external_hydrodynamic_model_export_needed": True,
        "phase41_level4_proxy_supported": True,
        "training_authorized": False,
        "seed_runs_authorized": False,
        "sweeps_authorized": False,
        "loss_config_model_edits_authorized": False,
        "level5_supported": False,
        "swe_residual_implementation_authorized": False,
        "pinn_implementation_authorized": False,
        "strict_conservation_claim_authorized": False,
        "full_mass_conservation_claim_authorized": False,
        "hydrodynamic_closure_claim_authorized": False,
        "external_export_needed": True,
        "decision_candidates": list(DECISION_CANDIDATES),
        "selected_decision": selected,
        "required_fields_count": len(fields),
        "minimum_contract_items": len(contract),
        "urbanflood24_checklist_items": len(urbanflood24_checks),
        "icm_mike_checklist_items": len(icm_mike_checks),
        "required_outputs": required_outputs,
        "guardrails": list(GUARDRAILS),
        "summary": (
            "Phase 42 is a no-training export requirement specification. It translates the Phase 41 "
            "data-readiness gap into a formal contract for future hydrodynamic exports from "
            "UrbanFlood24 full data, InfoWorks ICM, MIKE+, or equivalent sources. It does not "
            "claim Level 5 support and does not implement SWE/PINN residuals."
        ),
        "next_recommended_action": (
            "Inspect UrbanFlood24 full dataset if available and/or request/export fields from "
            "InfoWorks ICM, MIKE+, or an equivalent hydrodynamic source."
        ),
        "contract_complete": complete,
    }


def main() -> int:
    args = parse_args()
    output_dir = repo_path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    fields = field_rows()
    unit_rows = unit_shape_time_rows(fields)
    contract = minimum_contract_rows()
    priority = priority_rows(fields)
    urbanflood24_checks = urbanflood24_checklist_rows()
    icm_mike_checks = icm_mike_checklist_rows()
    summary = build_summary(fields, contract, urbanflood24_checks, icm_mike_checks)

    write_csv(output_dir / "required_hydrodynamic_fields.csv", fields, FIELD_COLUMNS)
    write_csv(output_dir / "field_unit_shape_time_requirements.csv", unit_rows)
    write_csv(output_dir / "swe_residual_minimum_data_contract.csv", contract)
    write_csv(output_dir / "export_priority_table.csv", priority)
    write_csv(output_dir / "urbanflood24_full_inspection_checklist.csv", urbanflood24_checks)
    write_csv(output_dir / "icm_mike_export_checklist.csv", icm_mike_checks)
    write_json(output_dir / "phase42_export_requirement_summary.json", summary)
    write_markdown(output_dir / "phase42_export_requirement_summary.md", summary, fields, contract)

    print(f"required_fields_count={summary['required_fields_count']}")
    print(f"minimum_contract_items={summary['minimum_contract_items']}")
    print(f"urbanflood24_checklist_items={summary['urbanflood24_checklist_items']}")
    print(f"icm_mike_checklist_items={summary['icm_mike_checklist_items']}")
    print(f"selected_decision={summary['selected_decision']}")
    print(f"training_authorized={str(summary['training_authorized']).lower()}")
    print(f"next_recommended_action={summary['next_recommended_action']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
