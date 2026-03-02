from math import atan, ceil, degrees, sqrt
from fastapi import FastAPI, UploadFile
from pydantic import BaseModel, Field
import ezdxf

app = FastAPI()

STEEL_DENSITY_KG_M3 = 7850.0


@app.post("/interpret")
async def interpret_dwg(file: UploadFile):
    contents = await file.read()
    with open("temp.dwg", "wb") as f:
        f.write(contents)

    doc = ezdxf.readfile("temp.dwg")
    msp = doc.modelspace()

    parts = []
    for e in msp.query("LINE"):
        length = e.dxf.start.distance(e.dxf.end)
        parts.append({
            "type": "beam",
            "length_mm": round(length, 2),
            "section": "UNKNOWN"
        })

    return {"parts": parts}


class PEBInput(BaseModel):
    width_m: float = 88.0
    length_m: float = 237.0
    eave_height_m: float = 5.0
    ridge_height_m: float = 7.4
    frame_spacing_m: float = 7.8
    roof_dead_load_kn_m2: float = 0.10
    roof_live_load_kn_m2: float = 0.58
    roof_collateral_load_kn_m2: float = 0.10
    basic_wind_speed_kmh: float = 180.0
    wind_exposure: str = "C"
    fy_main_kn_cm2: float = Field(34.5, description="Yield stress for built-up primary frame steel")
    allowable_soil_bearing_kn_m2: float = 200.0


class PEBBOQInput(PEBInput):
    side_bay_left_m: float = 28.85
    center_bay_m: float = 31.10
    side_bay_right_m: float = 28.85
    purlin_spacing_m: float = 1.5
    girt_spacing_m: float = 1.8
    x_braced_bays_each_side: int = 4

    # Trial dimensions / unit weights for quantity takeoff
    column_depth_mm: float = 500.0
    column_flange_width_mm: float = 250.0
    column_plate_thickness_mm: float = 12.0
    rafter_depth_mm: float = 450.0
    rafter_flange_width_mm: float = 220.0
    rafter_plate_thickness_mm: float = 10.0
    purlin_unit_weight_kg_m: float = 8.5
    girt_unit_weight_kg_m: float = 7.5
    eave_strut_unit_weight_kg_m: float = 10.0
    bracing_unit_weight_kg_m: float = 5.5
    base_plate_side_mm: float = 500.0
    base_plate_thickness_mm: float = 25.0
    anchor_bolt_dia_mm: float = 24.0
    anchor_bolts_per_column: int = 4
    steel_rate_usd_per_kg: float = 1.15
    connection_misc_percent: float = 7.5


def _preliminary_design(data: PEBInput):
    half_span = data.width_m / 2.0
    rise = data.ridge_height_m - data.eave_height_m
    roof_slope = rise / half_span
    roof_angle_deg = degrees(atan(roof_slope))

    n_frames = ceil(data.length_m / data.frame_spacing_m) + 1

    gravity_load_kn_m2 = (
        data.roof_dead_load_kn_m2 +
        data.roof_live_load_kn_m2 +
        data.roof_collateral_load_kn_m2
    )

    frame_tributary_area_m2 = data.width_m * data.frame_spacing_m
    total_gravity_per_frame_kn = gravity_load_kn_m2 * frame_tributary_area_m2

    col_vertical_reaction_kn = total_gravity_per_frame_kn / 2.0

    v_ms = data.basic_wind_speed_kmh / 3.6
    q_kn_m2 = 0.613 * (v_ms ** 2) / 1000.0

    exposure_multiplier = {
        "B": 0.85,
        "C": 1.0,
        "D": 1.15,
    }.get(data.wind_exposure.upper(), 1.0)

    design_wind_pressure_kn_m2 = q_kn_m2 * exposure_multiplier

    wall_area_per_frame_m2 = data.eave_height_m * data.frame_spacing_m
    lateral_force_per_frame_kn = design_wind_pressure_kn_m2 * wall_area_per_frame_m2

    base_shear_each_col_kn = lateral_force_per_frame_kn / 2.0
    base_moment_each_col_knm = base_shear_each_col_kn * (data.eave_height_m / 2.0)

    fy_kn_m2 = data.fy_main_kn_cm2 * 10000.0
    allowable_axial_kn_m2 = 0.6 * fy_kn_m2
    req_col_area_m2 = col_vertical_reaction_kn / allowable_axial_kn_m2
    req_col_area_cm2 = req_col_area_m2 * 10000.0

    required_plate_area_m2 = col_vertical_reaction_kn / (0.6 * data.allowable_soil_bearing_kn_m2)
    plate_side_m = required_plate_area_m2 ** 0.5

    footing_area_m2 = col_vertical_reaction_kn / data.allowable_soil_bearing_kn_m2
    footing_side_m = footing_area_m2 ** 0.5

    lever_arm_m = max(0.3, plate_side_m * 0.8)
    anchor_tension_group_kn = base_moment_each_col_knm / lever_arm_m

    return {
        "geometry": {
            "roof_slope_ratio": round(roof_slope, 4),
            "roof_angle_deg_approx": round(roof_angle_deg, 3),
            "number_of_frames": n_frames,
        },
        "loads": {
            "gravity_load_kn_m2": round(gravity_load_kn_m2, 3),
            "total_gravity_per_frame_kn": round(total_gravity_per_frame_kn, 2),
            "wind_pressure_kn_m2": round(design_wind_pressure_kn_m2, 3),
            "lateral_force_per_frame_kn": round(lateral_force_per_frame_kn, 2),
        },
        "preliminary_demands": {
            "column_vertical_reaction_kn": round(col_vertical_reaction_kn, 2),
            "column_base_shear_kn": round(base_shear_each_col_kn, 2),
            "column_base_moment_knm": round(base_moment_each_col_knm, 2),
        },
        "trial_sizes": {
            "required_column_area_cm2": round(req_col_area_cm2, 2),
            "base_plate_square_side_mm": round(plate_side_m * 1000.0),
            "isolated_footing_square_side_mm": round(footing_side_m * 1000.0),
            "anchor_tension_group_kn": round(anchor_tension_group_kn, 2),
        },
    }


@app.post("/peb/preliminary-design")
def preliminary_peb_design(data: PEBInput):
    result = _preliminary_design(data)
    result["warning"] = "Preliminary concept design only. Perform full 3D analysis and code checks before construction."
    result["material_reference"] = {
        "main_frame_fy_kn_cm2": data.fy_main_kn_cm2,
        "wind_exposure": data.wind_exposure.upper(),
    }
    return result


@app.post("/peb/boq-summary")
def peb_boq_summary(data: PEBBOQInput):
    """
    Produces a conceptual BOQ and total steel weight for a PEB using trial dimensions.
    """
    prelim = _preliminary_design(data)
    n_frames = prelim["geometry"]["number_of_frames"]
    n_columns = 2 * n_frames

    roof_half_len = sqrt((data.width_m / 2.0) ** 2 + (data.ridge_height_m - data.eave_height_m) ** 2)
    total_rafter_length_m = n_frames * 2.0 * roof_half_len
    total_column_length_m = n_columns * data.eave_height_m

    col_area_m2 = (
        2.0 * (data.column_depth_mm / 1000.0) * (data.column_plate_thickness_mm / 1000.0)
        + 2.0 * (data.column_flange_width_mm / 1000.0) * (data.column_plate_thickness_mm / 1000.0)
    )
    rafter_area_m2 = (
        2.0 * (data.rafter_depth_mm / 1000.0) * (data.rafter_plate_thickness_mm / 1000.0)
        + 2.0 * (data.rafter_flange_width_mm / 1000.0) * (data.rafter_plate_thickness_mm / 1000.0)
    )

    col_unit_wt = col_area_m2 * STEEL_DENSITY_KG_M3
    rafter_unit_wt = rafter_area_m2 * STEEL_DENSITY_KG_M3

    purlin_lines = ceil(roof_half_len / data.purlin_spacing_m) * 2
    total_purlin_length_m = purlin_lines * data.length_m

    girt_rows = ceil(data.eave_height_m / data.girt_spacing_m)
    side_wall_girts_m = 2 * girt_rows * data.length_m
    end_wall_girts_m = 2 * girt_rows * data.width_m
    total_girt_length_m = side_wall_girts_m + end_wall_girts_m

    total_eave_strut_length_m = 2 * data.length_m

    bracing_bays_total = data.x_braced_bays_each_side * 2
    bracing_length_per_bay_m = 2 * sqrt(data.frame_spacing_m ** 2 + data.eave_height_m ** 2)
    total_bracing_length_m = bracing_bays_total * bracing_length_per_bay_m

    base_plate_volume_m3_each = (
        (data.base_plate_side_mm / 1000.0) ** 2 * (data.base_plate_thickness_mm / 1000.0)
    )
    base_plate_weight_kg_each = base_plate_volume_m3_each * STEEL_DENSITY_KG_M3

    components = [
        {
            "item": "Built-up columns",
            "section": f"I built-up {int(data.column_depth_mm)}x{int(data.column_flange_width_mm)}x{int(data.column_plate_thickness_mm)} mm",
            "quantity": n_columns,
            "unit": "nos",
            "total_length_m": round(total_column_length_m, 2),
            "unit_weight_kg_m": round(col_unit_wt, 2),
            "total_weight_kg": round(total_column_length_m * col_unit_wt, 1),
        },
        {
            "item": "Built-up rafters",
            "section": f"I built-up {int(data.rafter_depth_mm)}x{int(data.rafter_flange_width_mm)}x{int(data.rafter_plate_thickness_mm)} mm",
            "quantity": n_frames * 2,
            "unit": "nos",
            "total_length_m": round(total_rafter_length_m, 2),
            "unit_weight_kg_m": round(rafter_unit_wt, 2),
            "total_weight_kg": round(total_rafter_length_m * rafter_unit_wt, 1),
        },
        {
            "item": "Roof purlins (Z/C)",
            "section": "Cold-formed Z/C",
            "quantity": purlin_lines,
            "unit": "lines",
            "total_length_m": round(total_purlin_length_m, 2),
            "unit_weight_kg_m": data.purlin_unit_weight_kg_m,
            "total_weight_kg": round(total_purlin_length_m * data.purlin_unit_weight_kg_m, 1),
        },
        {
            "item": "Wall girts",
            "section": "Cold-formed Z/C",
            "quantity": girt_rows,
            "unit": "rows/face",
            "total_length_m": round(total_girt_length_m, 2),
            "unit_weight_kg_m": data.girt_unit_weight_kg_m,
            "total_weight_kg": round(total_girt_length_m * data.girt_unit_weight_kg_m, 1),
        },
        {
            "item": "Eave struts",
            "section": "Cold-formed",
            "quantity": 2,
            "unit": "lines",
            "total_length_m": round(total_eave_strut_length_m, 2),
            "unit_weight_kg_m": data.eave_strut_unit_weight_kg_m,
            "total_weight_kg": round(total_eave_strut_length_m * data.eave_strut_unit_weight_kg_m, 1),
        },
        {
            "item": "Vertical X-bracing",
            "section": "Rods/cables",
            "quantity": bracing_bays_total,
            "unit": "bays",
            "total_length_m": round(total_bracing_length_m, 2),
            "unit_weight_kg_m": data.bracing_unit_weight_kg_m,
            "total_weight_kg": round(total_bracing_length_m * data.bracing_unit_weight_kg_m, 1),
        },
        {
            "item": "Base plates",
            "section": f"{int(data.base_plate_side_mm)}x{int(data.base_plate_side_mm)}x{int(data.base_plate_thickness_mm)} mm",
            "quantity": n_columns,
            "unit": "nos",
            "total_length_m": 0,
            "unit_weight_kg_m": 0,
            "total_weight_kg": round(n_columns * base_plate_weight_kg_each, 1),
        },
    ]

    total_steel_weight_kg = sum(item["total_weight_kg"] for item in components)
    primary_steel_weight_kg = components[0]["total_weight_kg"] + components[1]["total_weight_kg"]
    secondary_steel_weight_kg = sum(item["total_weight_kg"] for item in components[2:6])
    base_plate_weight_kg = components[6]["total_weight_kg"]

    material_cost_usd = total_steel_weight_kg * data.steel_rate_usd_per_kg
    connection_misc_usd = material_cost_usd * (data.connection_misc_percent / 100.0)
    total_cost_usd = material_cost_usd + connection_misc_usd

    roof_area_m2 = data.length_m * roof_half_len * 2.0
    wall_area_m2 = 2.0 * data.length_m * data.eave_height_m + 2.0 * data.width_m * data.eave_height_m

    return {
        "warning": "Conceptual BOQ only. Final steel takeoff requires detailed fabrication drawings and connection design.",
        "design_basis": {
            "code": "AISC (concept-level assumptions)",
            "note": "Final member checks require full load combinations and stability checks in a dedicated structural solver.",
        },
        "geometry": {
            "width_m": data.width_m,
            "length_m": data.length_m,
            "eave_height_m": data.eave_height_m,
            "ridge_height_m": data.ridge_height_m,
            "transverse_bays_m": [data.side_bay_left_m, data.center_bay_m, data.side_bay_right_m],
            "number_of_frames": n_frames,
        },
        "preliminary_design": prelim,
        "boq": {
            "components": components,
            "weight_breakdown_kg": {
                "primary_steel": round(primary_steel_weight_kg, 1),
                "secondary_steel": round(secondary_steel_weight_kg, 1),
                "base_plates": round(base_plate_weight_kg, 1),
            },
            "total_steel_weight_kg": round(total_steel_weight_kg, 1),
            "total_steel_weight_ton": round(total_steel_weight_kg / 1000.0, 3),
            "costing": {
                "steel_rate_usd_per_kg": data.steel_rate_usd_per_kg,
                "material_cost_usd": round(material_cost_usd, 2),
                "connection_misc_percent": data.connection_misc_percent,
                "connection_misc_usd": round(connection_misc_usd, 2),
                "estimated_total_usd": round(total_cost_usd, 2),
            },
            "anchor_bolts": {
                "diameter_mm": data.anchor_bolt_dia_mm,
                "count_nos": n_columns * data.anchor_bolts_per_column,
            },
            "cladding_areas_m2": {
                "roof": round(roof_area_m2, 2),
                "walls": round(wall_area_m2, 2),
                "total": round(roof_area_m2 + wall_area_m2, 2),
            },
        },
        "member_details": {
            "columns": {
                "count": n_columns,
                "trial_section": components[0]["section"],
                "height_m_each": data.eave_height_m,
            },
            "rafters": {
                "count": n_frames * 2,
                "trial_section": components[1]["section"],
                "slope_length_m_each": round(roof_half_len, 3),
            },
            "purlins": {
                "line_count": purlin_lines,
                "spacing_m": data.purlin_spacing_m,
            },
            "girts": {
                "rows_each_face": girt_rows,
                "spacing_m": data.girt_spacing_m,
            },
        },
    }


@app.post("/peb/staad-std")
def generate_staad_std(data: PEBBOQInput):
    """
    Generates a starter STAAD.Pro STD text block for one representative AISC portal frame.
    """
    rise = data.ridge_height_m - data.eave_height_m
    half = data.width_m / 2.0
    std_text = f"""STAAD SPACE
START JOB INFORMATION
ENGINEER DATE 2026-01-01
END JOB INFORMATION
INPUT WIDTH 79
UNIT METER KN
JOINT COORDINATES
1 0 0 0;
2 {half:.3f} {rise:.3f} 0;
3 {data.width_m:.3f} 0 0;
MEMBER INCIDENCES
1 1 2;
2 2 3;
DEFINE MATERIAL START
ISOTROPIC STEEL
E 2.05e8
POISSON 0.3
DENSITY 76.8195
ALPHA 1.2e-5
DAMP 0.03
END DEFINE MATERIAL
MEMBER PROPERTY AMERICAN
1 TABLE ST W{int(data.rafter_depth_mm/25.4)}X{max(10,int(data.rafter_flange_width_mm/10))}
2 TABLE ST W{int(data.rafter_depth_mm/25.4)}X{max(10,int(data.rafter_flange_width_mm/10))}
CONSTANTS
MATERIAL STEEL ALL
SUPPORTS
1 PINNED
3 PINNED
LOAD 1 DEAD + COLLATERAL
MEMBER LOAD
1 UNI GY -{(data.roof_dead_load_kn_m2 + data.roof_collateral_load_kn_m2) * data.frame_spacing_m / 2:.3f}
2 UNI GY -{(data.roof_dead_load_kn_m2 + data.roof_collateral_load_kn_m2) * data.frame_spacing_m / 2:.3f}
LOAD 2 ROOF LIVE
MEMBER LOAD
1 UNI GY -{data.roof_live_load_kn_m2 * data.frame_spacing_m / 2:.3f}
2 UNI GY -{data.roof_live_load_kn_m2 * data.frame_spacing_m / 2:.3f}
PERFORM ANALYSIS
PARAMETER 1
CODE AISC UNIFIED 2016
CHECK CODE ALL
FINISH
"""
    return {
        "warning": "Starter STAAD input only; add full frame lines, bracing, combinations, and exact sections before final checking.",
        "file_name": "peb_portal_frame_concept.std",
        "std_text": std_text,
    }


@app.post("/peb/solidworks-members")
def generate_solidworks_members(data: PEBBOQInput):
    """
    Returns a CSV-style cut-list template importable into SolidWorks workflows.
    """
    prelim = _preliminary_design(data)
    n_frames = prelim["geometry"]["number_of_frames"]
    roof_half_len = sqrt((data.width_m / 2.0) ** 2 + (data.ridge_height_m - data.eave_height_m) ** 2)
    csv_text = "\n".join([
        "Part,Qty,Length_m,Section,Material",
        f"Column, {2*n_frames}, {data.eave_height_m:.3f}, I_BU_{int(data.column_depth_mm)}x{int(data.column_flange_width_mm)}x{int(data.column_plate_thickness_mm)}, ASTM A572 Gr50",
        f"Rafter, {2*n_frames}, {roof_half_len:.3f}, I_BU_{int(data.rafter_depth_mm)}x{int(data.rafter_flange_width_mm)}x{int(data.rafter_plate_thickness_mm)}, ASTM A572 Gr50",
        f"Purlin Lines, {ceil(roof_half_len / data.purlin_spacing_m) * 2}, {data.length_m:.3f}, Z/C, ASTM A653 Gr50",
        f"Girt Rows, {ceil(data.eave_height_m / data.girt_spacing_m)}, {data.length_m:.3f}, Z/C, ASTM A653 Gr50",
    ])
    return {
        "warning": "Template only. Detailed plate/development lengths, hole patterns, and weld preps must be added in SolidWorks drawings.",
        "file_name": "peb_members_cutlist.csv",
        "csv_text": csv_text,
    }
