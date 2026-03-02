# valorstruct-dwg-service

DWG interpretation microservice for ValorStruct MVP.

## Endpoints

### `POST /interpret`
Upload a `.dwg` and receive a basic line-based part extraction.

### `POST /peb/preliminary-design`
Runs a **preliminary** conceptual sizing pass for a portal-frame pre-engineered steel building (PEB).

### `POST /peb/boq-summary`
Generates a conceptual steel BOQ with component-wise quantities, trial dimensions, and total steel weight.

### `POST /peb/staad-std`
Generates a starter STAAD.Pro `.std` model text for one representative portal frame with AISC code-check directives.

### `POST /peb/solidworks-members`
Generates a CSV cut-list template for SolidWorks member modeling workflows.

> ⚠️ These PEB endpoints are for conceptual estimation only and do **not** replace detailed code-based design, connection design, and licensed engineering sign-off.

## Example `POST /peb/boq-summary` payload

```json
{
  "width_m": 88.0,
  "length_m": 237.0,
  "eave_height_m": 5.0,
  "ridge_height_m": 7.4,
  "frame_spacing_m": 7.8,
  "side_bay_left_m": 28.85,
  "center_bay_m": 31.10,
  "side_bay_right_m": 28.85,
  "roof_dead_load_kn_m2": 0.10,
  "roof_live_load_kn_m2": 0.58,
  "roof_collateral_load_kn_m2": 0.10,
  "basic_wind_speed_kmh": 180.0,
  "wind_exposure": "C",
  "fy_main_kn_cm2": 34.5,
  "allowable_soil_bearing_kn_m2": 200.0,
  "column_depth_mm": 500,
  "column_flange_width_mm": 250,
  "column_plate_thickness_mm": 12,
  "rafter_depth_mm": 450,
  "rafter_flange_width_mm": 220,
  "rafter_plate_thickness_mm": 10
}
```

Returns component-level BOQ entries for columns, rafters, purlins, girts, eave struts, bracing, base plates, anchor bolt count, cladding areas, and conceptual costing breakdown.
