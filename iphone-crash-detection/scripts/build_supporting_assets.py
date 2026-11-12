"""Phase 04 - supporting assets (dash, cabin cutaway, diegetic phone UI, schematic effects).
Builds independent .blend files for shots 03, 10, 11, 12, 13, 14, 15, 16.
Does not touch phase 02 or phase 03 files.

Run:  blender --background --python scripts/build_supporting_assets.py -- <project_dir>
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from asset_lib import (box, cylinder, empty, finish, material, new_collection, reset,
                       rounded_slab, save, torus, control, drive_bsdf)
import bmesh
import bpy
from mathutils import Matrix, Vector

PROJECT = Path(sys.argv[sys.argv.index("--") + 1]).resolve()
ASSETS = PROJECT / "assets"
ASSETS.mkdir(exist_ok=True)


# ---------------------------------------------------------------- DASHBOARD
def build_car_interior_dash():
    reset()
    c = new_collection("ASSET_CarInteriorDash")
    root = empty("DASH_Root", (0, 0, 0), c, size=0.2)

    m_dash = material("DASH_Mat_Body", (0.08, 0.08, 0.09), metallic=0.1, rough=0.7)
    m_trim = material("DASH_Mat_Trim", (0.15, 0.16, 0.18), metallic=0.6, rough=0.3)
    m_mount = material("DASH_Mat_Mount", (0.10, 0.10, 0.11), metallic=0.3, rough=0.5)
    m_glass = material("DASH_Mat_Glass", (0.7, 0.85, 0.95), metallic=0.1, rough=0.1)

    # Main dashboard top slab
    box("DASH_MainSlab", (1.40, 0.50, 0.18), (0, 0.10, -0.05), c, m_dash, root, bevel=0.015)
    # Lower console / centre stack
    box("DASH_Console", (0.35, 0.35, 0.40), (0, 0.20, -0.32), c, m_dash, root, bevel=0.01)
    # Windshield base angle
    box("DASH_Windshield", (1.45, 0.02, 0.50), (0, -0.15, 0.20), c, m_glass, root)
    # Steering wheel rim (on right or left side; let's put on left x=-0.35 for standard orientation)
    wheel = torus("DASH_SteeringWheel", 0.17, 0.016, (-0.35, 0.32, 0.05), c, m_trim, root)
    wheel.rotation_euler = (math.radians(-30), 0, 0)
    # Steering column
    cylinder("DASH_SteeringCol", 0.035, 0.30, (-0.35, 0.20, -0.05), c, m_dash, root, axis="Y")

    # Centre air vents
    box("DASH_Vent_L", (0.08, 0.01, 0.06), (-0.08, -0.08, 0.02), c, m_trim, root, bevel=0.002)
    box("DASH_Vent_R", (0.08, 0.01, 0.06), (0.08, -0.08, 0.02), c, m_trim, root, bevel=0.002)

    # Phone mount / holder: attached in centre dash (x=0, y=-0.04, z=0.08)
    # Base stalk
    cylinder("DASH_MountStalk", 0.012, 0.07, (0, -0.04, 0.04), c, m_mount, root, axis="Z")
    # Mount ball / joint & magnetic / clamp pad (tilted 15 degrees back)
    pad = box("DASH_MountPad", (0.060, 0.015, 0.090), (0, -0.04, 0.09), c, m_mount, root, bevel=0.003)
    pad.rotation_euler = (math.radians(-15), 0, 0)

    # Phone anchor: exact location and orientation where phone_exterior root sits in the mount
    # Phone root is at the centre of the phone body (Z upright, screen facing -Y)
    phone_anchor = empty("ANCHOR_PhoneMount", (0, -0.04 - 0.006, 0.09), c, root, size=0.05)
    phone_anchor.rotation_euler = (math.radians(-15), 0, 0)

    empty("CAM_Target_Dash", (0, 0, 0.08), c, root, 0.05, "SPHERE")
    control(root, "dash_ambient", 1.0, 0.0, 5.0, "Dashboard ambient reflection scale")
    save(ASSETS / "car_interior_dash.blend")


# ---------------------------------------------------------------- PHONE UI ALERT
def build_phone_ui_alert():
    reset()
    c = new_collection("ASSET_PhoneUIAlert")
    root = empty("UIALERT_Root", (0, 0, 0), c, size=0.05)

    # Screen dimensions: width 0.066, height 0.140, placed at y=0 (surface of phone screen)
    m_bg = material("UIALERT_Mat_BG", (0.08, 0.02, 0.02), metallic=0.0, rough=0.8, emission=(0.4, 0.05, 0.05), strength=0.5)
    m_warn = material("UIALERT_Mat_Warn", (1.0, 0.2, 0.0), metallic=0.0, rough=0.3, emission=(1.0, 0.25, 0.0), strength=4.0)
    m_circle = material("UIALERT_Mat_Ring", (1.0, 0.3, 0.1), metallic=0.0, rough=0.3, emission=(1.0, 0.3, 0.1), strength=5.0)
    m_slider = material("UIALERT_Mat_Slider", (0.2, 0.2, 0.22), metallic=0.1, rough=0.4, emission=(0.8, 0.8, 0.8), strength=1.5)
    m_pill_btn = material("UIALERT_Mat_Btn", (0.9, 0.9, 0.9), metallic=0.2, rough=0.2, emission=(1.0, 1.0, 1.0), strength=3.0)

    # Dark reddish emergency screen panel
    rounded_slab("UIALERT_ScreenPanel", 0.065, 0.138, 0.0004, 0.007, (0, -0.0002, 0), c, m_bg, root)

    # Warning Header Icon (stylized triangle/shield)
    cylinder("UIALERT_WarningBadge", 0.012, 0.0006, (0, -0.0006, 0.045), c, m_warn, root, axis="Y", segments=32)

    # Alert Title Bars (stylized clean bars representing "Crash Detected / SOS")
    box("UIALERT_TitleBar1", (0.046, 0.0005, 0.006), (0, -0.0006, 0.027), c, m_warn, root, bevel=0.001)
    box("UIALERT_TitleBar2", (0.034, 0.0005, 0.0035), (0, -0.0006, 0.019), c, m_slider, root, bevel=0.0008)

    # Countdown ring in center
    ring = torus("UIALERT_CountdownRing", 0.018, 0.0018, (0, -0.0006, -0.005), c, m_circle, root, seg_major=48)
    ring.rotation_euler = (math.radians(90), 0, 0)
    # Countdown number slab
    box("UIALERT_CountdownNumber", (0.008, 0.0005, 0.012), (0, -0.0006, -0.005), c, m_circle, root)

    # Bottom slider bar
    rounded_slab("UIALERT_SliderTrack", 0.052, 0.014, 0.0005, 0.006, (0, -0.0006, -0.045), c, m_slider, root)
    # Slider button thumb
    cylinder("UIALERT_SliderThumb", 0.0055, 0.0008, (-0.018, -0.0008, -0.045), c, m_pill_btn, root, axis="Y", segments=24)

    empty("ANCHOR_ScreenUI", (0, 0, 0), c, root, 0.02)
    empty("CAM_Target_UIALERT", (0, -0.001, 0), c, root, 0.02, "SPHERE")

    control(root, "alert_glow", 4.0, 0.0, 20.0, "UI alert glow intensity")
    drive_bsdf(m_warn, "Emission Strength", root, "alert_glow")
    drive_bsdf(m_circle, "Emission Strength", root, "alert_glow", gain=1.2)
    save(ASSETS / "phone_ui_alert.blend")


# ---------------------------------------------------------------- PHONE UI CALL
def build_phone_ui_call():
    reset()
    c = new_collection("ASSET_PhoneUICall")
    root = empty("UICALL_Root", (0, 0, 0), c, size=0.05)

    m_bg = material("UICALL_Mat_BG", (0.02, 0.04, 0.07), metallic=0.0, rough=0.8, emission=(0.05, 0.10, 0.20), strength=0.6)
    m_call = material("UICALL_Mat_ActiveCall", (0.1, 0.85, 0.3), metallic=0.0, rough=0.3, emission=(0.1, 0.9, 0.35), strength=4.5)
    m_pin = material("UICALL_Mat_Pin", (1.0, 0.3, 0.1), metallic=0.0, rough=0.2, emission=(1.0, 0.35, 0.1), strength=5.0)
    m_accent = material("UICALL_Mat_Accent", (0.4, 0.6, 0.9), metallic=0.1, rough=0.3, emission=(0.4, 0.65, 0.95), strength=2.5)

    # Calling Screen Panel
    rounded_slab("UICALL_ScreenPanel", 0.065, 0.138, 0.0004, 0.007, (0, -0.0002, 0), c, m_bg, root)

    # Calling Badge (stylized phone icon circle at top)
    cylinder("UICALL_CallBadge", 0.014, 0.0006, (0, -0.0006, 0.045), c, m_call, root, axis="Y", segments=32)

    # "Layanan Darurat Dipanggil" Header Bars
    box("UICALL_Banner1", (0.044, 0.0005, 0.0055), (0, -0.0006, 0.025), c, m_call, root, bevel=0.001)
    box("UICALL_Banner2", (0.032, 0.0005, 0.0035), (0, -0.0006, 0.016), c, m_accent, root, bevel=0.0008)

    # Map Mini Radar / Location Pin Area
    cylinder("UICALL_MapDisc", 0.022, 0.0005, (0, -0.0006, -0.012), c, m_bg, root, axis="Y", segments=36)
    # Radar pulse ring
    ring = torus("UICALL_RadarRing", 0.020, 0.0012, (0, -0.0006, -0.012), c, m_accent, root, seg_major=36)
    ring.rotation_euler = (math.radians(90), 0, 0)
    # GPS Pin (stylized cone + sphere head)
    cylinder("UICALL_PinBody", 0.004, 0.008, (0, -0.0008, -0.010), c, m_pin, root, axis="Z", segments=16)
    cylinder("UICALL_PinHead", 0.005, 0.004, (0, -0.0008, -0.005), c, m_pin, root, axis="Y", segments=20)

    # Bottom End-Call button (red circle)
    m_red = material("UICALL_Mat_EndBtn", (0.9, 0.1, 0.1), metallic=0.1, rough=0.3, emission=(0.95, 0.1, 0.1), strength=3.0)
    cylinder("UICALL_EndBtn", 0.012, 0.0008, (0, -0.0008, -0.045), c, m_red, root, axis="Y", segments=32)

    empty("ANCHOR_ScreenUICall", (0, 0, 0), c, root, 0.02)
    empty("CAM_Target_UICALL", (0, -0.001, 0), c, root, 0.02, "SPHERE")

    control(root, "call_glow", 4.0, 0.0, 20.0, "UI call glow intensity")
    drive_bsdf(m_call, "Emission Strength", root, "call_glow")
    drive_bsdf(m_pin, "Emission Strength", root, "call_glow", gain=1.1)
    save(ASSETS / "phone_ui_call.blend")


# ---------------------------------------------------------------- CAR CUTAWAY
def build_car_cutaway():
    reset()
    c = new_collection("ASSET_CarCutaway")
    root = empty("CUTAWAY_Root", (0, 0, 0), c, size=0.5)

    m_body = material("CUTAWAY_Mat_Body", (0.12, 0.40, 0.72), metallic=0.1, rough=0.35)
    m_edge = material("CUTAWAY_Mat_CutEdge", (1.00, 0.45, 0.10), metallic=0.3, rough=0.3, emission=(1.00, 0.45, 0.10), strength=3.0)
    m_interior = material("CUTAWAY_Mat_Interior", (0.12, 0.12, 0.14), metallic=0.1, rough=0.7)
    m_seat = material("CUTAWAY_Mat_Seat", (0.18, 0.19, 0.22), metallic=0.0, rough=0.8)
    m_glass = material("CUTAWAY_Mat_Glass", (0.8, 0.9, 1.0), metallic=0.1, rough=0.1)

    # Cutaway chassis: bottom floor plate (length 4.0m, width 0.95m for cut half, height 0.2m)
    box("CUTAWAY_Floor", (4.0, 0.95, 0.18), (0, 0.48, 0.15), c, m_interior, root, bevel=0.02)
    # Right-side body wall (intact side at +Y)
    box("CUTAWAY_SideWall", (3.8, 0.12, 0.90), (0, 0.90, 0.65), c, m_body, root, bevel=0.03)
    # Front hood/engine block area
    box("CUTAWAY_Hood", (1.3, 0.95, 0.35), (1.35, 0.48, 0.55), c, m_body, root, bevel=0.03)
    # Rear trunk area
    box("CUTAWAY_Trunk", (1.1, 0.95, 0.45), (-1.45, 0.48, 0.60), c, m_body, root, bevel=0.03)

    # Glowing cut boundary lines indicating schematic architectural section
    box("CUTAWAY_SectionLine_Floor", (4.02, 0.02, 0.02), (0, 0.01, 0.24), c, m_edge, root)
    box("CUTAWAY_SectionLine_Hood", (1.32, 0.02, 0.02), (1.35, 0.01, 0.73), c, m_edge, root)
    box("CUTAWAY_SectionLine_Roof", (1.82, 0.02, 0.02), (-0.10, 0.01, 1.35), c, m_edge, root)

    # Interior seats (driver & rear)
    # Front seat
    box("CUTAWAY_SeatFrontBase", (0.50, 0.45, 0.18), (0.10, 0.48, 0.34), c, m_seat, root, bevel=0.02)
    back1 = box("CUTAWAY_SeatFrontBack", (0.16, 0.42, 0.60), (-0.12, 0.48, 0.68), c, m_seat, root, bevel=0.02)
    back1.rotation_euler = (0, math.radians(-12), 0)
    # Rear seat
    box("CUTAWAY_SeatRearBase", (0.52, 0.45, 0.18), (-0.95, 0.48, 0.34), c, m_seat, root, bevel=0.02)
    back2 = box("CUTAWAY_SeatRearBack", (0.16, 0.42, 0.60), (-1.18, 0.48, 0.68), c, m_seat, root, bevel=0.02)
    back2.rotation_euler = (0, math.radians(-12), 0)

    # Cutaway Dash & Phone Mount
    box("CUTAWAY_Dash", (0.40, 0.92, 0.25), (0.65, 0.48, 0.62), c, m_interior, root, bevel=0.02)

    # Anchor for Phone in Cabin: at the dash mount position
    phone_anchor = empty("ANCHOR_PhoneInsideCabin", (0.62, 0.48, 0.82), c, root, size=0.06)
    phone_anchor.rotation_euler = (math.radians(-15), 0, math.radians(90))

    empty("CAM_Target_Cutaway", (0.3, 0.48, 0.7), c, root, 0.1, "SPHERE")
    control(root, "cutaway_glow", 3.0, 0.0, 15.0, "Cut edge glow strength")
    drive_bsdf(m_edge, "Emission Strength", root, "cutaway_glow")
    save(ASSETS / "car_cutaway.blend")


# ---------------------------------------------------------------- SCHEMATIC EFFECTS
def build_schematic_effects():
    reset()
    c = new_collection("ASSET_SchematicEffects")
    root = empty("SCHEMATIC_Root", (0, 0, 0), c, size=0.2)

    # 1. Pressure Wave Rings (for SHOT_10)
    m_wave = material("SCHEMATIC_Mat_Pressure", (0.2, 0.7, 1.0), metallic=0.0, rough=0.3, emission=(0.25, 0.8, 1.0), strength=4.0)
    for i in range(3):
        r = 0.20 + 0.15 * i
        ring = torus(f"SCHEMATIC_WaveRing_{i+1}", r, 0.008, (0, 0, 0), c, m_wave, root, seg_major=48)
        ring.rotation_euler = (math.radians(90), 0, 0)
    empty("ANCHOR_Effect_Pressure", (0, 0, 0), c, root, 0.1)

    # 2. Sound Ripple (for SHOT_11)
    m_sound = material("SCHEMATIC_Mat_Sound", (1.0, 0.3, 0.8), metallic=0.0, rough=0.3, emission=(1.0, 0.35, 0.85), strength=5.0)
    for i in range(4):
        rad = 0.015 + 0.012 * i
        rip = cylinder(f"SCHEMATIC_SoundArc_{i+1}", rad, 0.001, (0, 0, -0.015 * i), c, m_sound, root, axis="Z", segments=32)
        rip.scale = (1.0, 0.4, 1.0)
    empty("ANCHOR_Effect_Sound", (0, 0, 0), c, root, 0.02)

    # 3. GPS Trail Dots (for SHOT_12)
    m_gps = material("SCHEMATIC_Mat_Gps", (1.0, 0.85, 0.15), metallic=0.0, rough=0.2, emission=(1.0, 0.90, 0.20), strength=5.5)
    for i in range(12):
        x = -10.0 + 1.8 * i
        cylinder(f"SCHEMATIC_GpsDot_{i+1}", 0.14, 0.04, (x, 1.75, 0.05), c, m_gps, root, axis="Z", segments=16)
    empty("ANCHOR_Effect_Gps", (0, 1.75, 0.05), c, root, 0.5)

    # 4. Signal Tracers (for SHOT_13): 5 glowing curved paths converging on the processor chip
    m_signal = material("SCHEMATIC_Mat_Signal", (0.3, 0.9, 1.0), metallic=0.0, rough=0.2, emission=(0.35, 0.95, 1.0), strength=6.0)
    sensor_locs = [
        (-0.0265, 0.006),  # accel
        (-0.0180, 0.006),  # gyro
        (-0.0220, -0.012), # baro
        (-0.0220, 0.056),  # gps
        (-0.0105, -0.0708) # mic
    ]
    proc_loc = (-0.022, 0.031)
    for i, (sx, sz) in enumerate(sensor_locs):
        # Beam line connecting sensor to processor
        dx, dz = proc_loc[0] - sx, proc_loc[1] - sz
        dist = math.hypot(dx, dz)
        cx, cz = (sx + proc_loc[0]) / 2, (sz + proc_loc[1]) / 2
        ang = math.atan2(dx, dz)
        beam = box(f"SCHEMATIC_SignalBeam_{i+1}", (0.0008, 0.0008, dist), (cx, -0.0007, cz), c, m_signal, root)
        beam.rotation_euler = (0, -ang, 0)
    empty("ANCHOR_Effect_Tracers", (-0.022, 0, 0.031), c, root, 0.01)

    # 5. Mini Cars Instances (for SHOT_14): Grid of toy cars on processor
    m_mini_norm = material("SCHEMATIC_Mat_MiniNormal", (0.3, 0.7, 0.9), metallic=0.3, rough=0.4, emission=(0.3, 0.7, 0.9), strength=1.5)
    m_mini_crash = material("SCHEMATIC_Mat_MiniCrash", (1.0, 0.2, 0.1), metallic=0.3, rough=0.3, emission=(1.0, 0.25, 0.1), strength=6.0)
    for row in range(5):
        for col in range(5):
            mx = -0.028 + col * 0.0032
            mz = 0.024 + row * 0.0032
            is_crash = (row, col) in [(1, 2), (3, 1), (4, 3)]
            mat = m_mini_crash if is_crash else m_mini_norm
            box(f"SCHEMATIC_MiniCar_{row}_{col}", (0.0018, 0.0010, 0.0024), (mx, -0.0012, mz), c, mat, root, bevel=0.0002)
    empty("ANCHOR_Effect_MiniCars", (-0.022, -0.001, 0.031), c, root, 0.01)

    # 6. Call Wave Beacon (for SHOT_16): Radiating beacon rings expanding up from phone
    m_beacon = material("SCHEMATIC_Mat_Beacon", (0.1, 0.9, 0.4), metallic=0.0, rough=0.2, emission=(0.15, 0.95, 0.45), strength=5.0)
    for i in range(4):
        z = 0.08 + 0.06 * i
        r = 0.03 + 0.04 * i
        ring = torus(f"SCHEMATIC_BeaconRing_{i+1}", r, 0.002, (0, 0, z), c, m_beacon, root, seg_major=36)
    empty("ANCHOR_Effect_CallWave", (0, 0, 0.15), c, root, 0.05)

    control(root, "effect_glow", 4.0, 0.0, 20.0, "Schematic effect glow scale")
    drive_bsdf(m_wave, "Emission Strength", root, "effect_glow")
    drive_bsdf(m_signal, "Emission Strength", root, "effect_glow", gain=1.2)
    drive_bsdf(m_beacon, "Emission Strength", root, "effect_glow", gain=1.1)
    save(ASSETS / "schematic_effects.blend")


if __name__ == "__main__":
    print("Building supporting assets for", PROJECT)
    build_car_interior_dash()
    build_phone_ui_alert()
    build_phone_ui_call()
    build_car_cutaway()
    build_schematic_effects()
    print("DONE building all supporting assets.")
