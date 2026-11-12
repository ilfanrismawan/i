"""Phase 03b - supporting assets. Does not touch earlier asset files.

Run:  blender --background --python scripts/build_support_assets.py -- <project_dir>

Outputs:
  assets/car_interior_dash.blend  ASSET_CarDash      dashboard set with phone mount (real scale, forward = +X, right-hand drive)
  assets/car_cutaway.blend        ASSET_CarCutaway   far half of the car, open toward -Y, same axes as car_stylized
  assets/phone_ui_screens.blend   ASSET_PhoneUI      diegetic alert + call screens, icon-only (no text), phone_exterior axes
  assets/fx_schematics.blend      ASSET_FX_*         pressure wave, sound ripple, call wave, GPS trail, signal tracers
  assets/mini_cars.blend          ASSET_MiniCars     lanes of tiny cars over a chip (training-data metaphor)

Everything here is illustrative: waves, ripples, trails and pulses are drawing aids, not visible things.
The UI is a generic icon layout, not a copy of any real phone interface.
"""
import math
import sys
from pathlib import Path

import bmesh
import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
from asset_lib import (arc_band, box, bsdf_path, clamp, control, cylinder, drive, drive_bsdf, drive_curve, empty,  # noqa: E402
                       finish, material, new_collection, prism, reset, rounded_slab, save, torus)

PROJECT = Path(sys.argv[sys.argv.index("--") + 1]).resolve()
ASSETS = PROJECT / "assets"
PAINT, GLASS, TRIM = (0.92, 0.30, 0.12), (0.05, 0.09, 0.14), (0.10, 0.10, 0.12)


def glow(name, colour, strength=1.0, base=None):
    return material(name, base or tuple(c * 0.25 for c in colour), rough=0.5, emission=colour, strength=strength)


# ---------------------------------------------------------------- dashboard
def build_dash():
    reset()
    c = new_collection("ASSET_CarDash")
    root = empty("DASH_Root", (0, 0, 0), c, size=0.3)  # local z=0 is the dash top; place on the car's ANCHOR_Dash
    m_dash = material("DASH_Mat_Dash", (0.09, 0.09, 0.11), rough=0.6)
    m_soft = material("DASH_Mat_Soft", (0.16, 0.16, 0.19), rough=0.75)
    m_paint = material("DASH_Mat_Paint", PAINT, metallic=0.2, rough=0.3)
    m_metal = material("DASH_Mat_Metal", (0.65, 0.67, 0.70), metallic=0.9, rough=0.3)
    m_gauge = glow("DASH_Mat_Gauge", (0.3, 0.8, 1.0), 1.2)
    box("DASH_Body", (0.50, 1.56, 0.36), (0.22, 0, -0.18), c, m_dash, root, bevel=0.06, seg=4)
    box("DASH_TopPad", (0.44, 1.50, 0.03), (0.24, 0, 0.0), c, m_soft, root, bevel=0.012)
    box("DASH_Hood", (0.20, 0.44, 0.10), (0.10, -0.38, 0.05), c, m_soft, root, bevel=0.04)
    box("DASH_Gauges", (0.01, 0.34, 0.06), (0.005, -0.38, 0.04), c, m_gauge, root, bevel=0.004)
    for k, y in enumerate((-0.10, 0.10, 0.52)):
        box(f"DASH_Vent_{k + 1}", (0.02, 0.14, 0.05), (-0.02, y, -0.08), c, m_metal, root, bevel=0.008)
    box("DASH_Console", (0.06, 0.26, 0.20), (-0.02, 0.0, -0.24), c, m_soft, root, bevel=0.02)
    # windshield frame
    for sy, side in ((1, "L"), (-1, "R")):
        p = box(f"DASH_Pillar_{side}", (0.86, 0.07, 0.07), (0.47, sy * 0.78, 0.0), c, m_paint, root, bevel=0.02, origin_min_x=True)
        p.rotation_euler = (0, math.radians(-132), 0)
    box("DASH_RoofHeader", (0.10, 1.63, 0.06), (-0.10, 0, 0.64), c, m_paint, root, bevel=0.02)
    box("DASH_HoodOutside", (1.10, 1.60, 0.05), (1.05, 0, -0.06), c, m_paint, root, bevel=0.02)
    # steering wheel on the right-hand side (-Y when facing +X)
    wheel = empty("DASH_SteeringWheel", (-0.26, -0.38, -0.06), c, root, 0.2, "CIRCLE")
    wheel.rotation_euler = (0, math.radians(-68), 0)
    torus("DASH_WheelRim", 0.18, 0.018, (0, 0, 0), c, m_dash, wheel)
    cylinder("DASH_WheelHub", 0.055, 0.03, (0, 0, -0.01), c, m_soft, wheel, bevel=0.008)
    for k in range(3):
        s = box(f"DASH_WheelSpoke_{k + 1}", (0.17, 0.03, 0.014), (0, 0, -0.005), c, m_soft, wheel, origin_min_x=True)
        s.rotation_euler = (0, 0, math.radians(90 + 120 * k))
    cylinder("DASH_WheelColumn", 0.03, 0.24, (0, 0, -0.13), c, m_dash, wheel)
    # phone mount: stalk + cradle; the phone stands upright with its screen toward the driver (-X)
    cylinder("DASH_MountStalk", 0.012, 0.07, (0.06, 0.06, 0.045), c, m_metal, root)
    box("DASH_MountCradle", (0.012, 0.085, 0.10), (0.060, 0.06, 0.13), c, m_dash, root, bevel=0.004)
    box("DASH_MountLip", (0.022, 0.085, 0.008), (0.050, 0.06, 0.078), c, m_dash, root, bevel=0.002)
    mount = empty("ANCHOR_PhoneMount", (0.046, 0.06, 0.158), c, root, 0.03, "ARROWS")
    mount.rotation_euler = (0, 0, math.radians(-90))  # copy this transform to PHONE_Root: phone -Y (screen) -> -X
    empty("ANCHOR_DriverEye", (-0.75, -0.38, 0.28), c, root, 0.05)
    empty("CAM_Target_Dash", (0.046, 0.06, 0.158), c, root, 0.05, "SPHERE")
    control(root, "gauge_glow", 1.2, 0.0, 10.0, "Instrument cluster emission")
    drive_bsdf(m_gauge, "Emission Strength", root, "gauge_glow")
    save(ASSETS / "car_interior_dash.blend")


# ---------------------------------------------------------------- cutaway
def build_cutaway():
    reset()
    c = new_collection("ASSET_CarCutaway")
    root = empty("CUT_Root", (0, 0, 0), c, size=1.0)
    m_paint = material("CUT_Mat_Paint", PAINT, metallic=0.2, rough=0.3)
    m_cut = material("CUT_Mat_CutFace", (0.98, 0.72, 0.55), rough=0.6)  # lighter tone on sliced surfaces
    m_glass = material("CUT_Mat_Glass", (0.35, 0.55, 0.70), rough=0.1)
    m_dark = material("CUT_Mat_Interior", (0.13, 0.13, 0.16), rough=0.7)
    m_seat = material("CUT_Mat_Seat", (0.30, 0.33, 0.42), rough=0.8)
    m_tire = material("CUT_Mat_Tire", (0.03, 0.03, 0.035), rough=0.85)
    m_hub = material("CUT_Mat_Hub", (0.75, 0.77, 0.80), metallic=0.9, rough=0.3)
    HW, Y = 0.875, 0.4375  # half-car: occupies y in [0, 0.875]
    box("CUT_FloorPan", (4.10, HW, 0.20), (0, Y, 0.37), c, m_paint, root, bevel=0.04)
    box("CUT_EngineBay", (1.20, HW, 0.40), (1.45, Y, 0.66), c, m_cut, root, bevel=0.05)
    box("CUT_Trunk", (0.95, HW, 0.40), (-1.575, Y, 0.66), c, m_cut, root, bevel=0.05)
    box("CUT_SideWall", (2.00, 0.06, 0.40), (-0.15, HW - 0.03, 0.66), c, m_paint, root)
    box("CUT_SideGlass", (1.90, 0.03, 0.50), (-0.30, HW - 0.06, 1.11), c, m_glass, root)
    box("CUT_Roof", (1.60, HW, 0.07), (-0.30, Y, 1.40), c, m_paint, root, bevel=0.02)
    for name, x, ang in (("Windshield", 0.66, -121), ("RearWindow", -1.26, -59)):
        g = box(f"CUT_{name}", (0.64, HW, 0.035), (x, Y, 1.115), c, m_glass, root)
        g.rotation_euler = (0, math.radians(ang), 0)
    box("CUT_DashBlock", (0.34, HW - 0.08, 0.26), (0.72, Y, 0.86), c, m_dark, root, bevel=0.05)
    for name, x in (("Front", -0.05), ("Rear", -0.95)):
        box(f"CUT_SeatBase_{name}", (0.50, 0.50, 0.14), (x, 0.40, 0.56), c, m_seat, root, bevel=0.04)
        b = box(f"CUT_SeatBack_{name}", (0.13, 0.50, 0.62), (x - 0.30, 0.40, 0.88), c, m_seat, root, bevel=0.04)
        b.rotation_euler = (0, math.radians(-10), 0)
        box(f"CUT_Headrest_{name}", (0.11, 0.26, 0.16), (x - 0.37, 0.40, 1.27), c, m_seat, root, bevel=0.04)
    for name, x in (("F", 1.30), ("R", -1.30)):
        w = cylinder(f"CUT_Wheel_{name}", 0.34, 0.26, (x, 0.78, 0.34), c, m_tire, root, axis="Y", bevel=0.05)
        cylinder(f"CUT_Hub_{name}", 0.20, 0.28, (0, 0, 0), c, m_hub, w, axis="Y", segments=24)
    for sx, name in ((1, "Front"), (-1, "Rear")):
        box(f"CUT_Bumper{name}", (0.20, HW, 0.20), (sx * 2.02, Y, 0.36), c, material(f"CUT_Mat_Trim{name}", TRIM, rough=0.5), root, bevel=0.06)
    empty("ANCHOR_Dash", (0.60, 0.30, 0.99), c, root, 0.1)
    empty("ANCHOR_WaveStart", (0.95, 0.40, 1.05), c, root, 0.1)
    empty("ANCHOR_CabinCenter", (-0.30, 0.40, 1.00), c, root, 0.1)
    empty("CAM_Target_Cutaway", (-0.10, 0.40, 0.95), c, root, 0.3, "SPHERE")
    save(ASSETS / "car_cutaway.blend")


# ---------------------------------------------------------------- phone UI
def build_ui():
    reset()
    c = new_collection("ASSET_PhoneUI")
    root = empty("PHONEUI_Root", (0, 0, 0), c, size=0.03)  # same axes as PHONE_Root; parent to it
    Y0, T = -0.0046, 0.0002
    control(root, "alert_visible", 0.0, 0.0, 1.0, "1 shows the alert screen, 0 hides it")
    control(root, "call_visible", 0.0, 0.0, 1.0, "1 shows the calling screen, 0 hides it")
    control(root, "countdown", 0.0, 0.0, 1.0, "Lights the 12 countdown dots one after another")
    control(root, "ui_glow", 1.5, 0.0, 10.0, "Brightness of both screens' backgrounds")
    groups = {}
    for key in ("alert", "call"):
        g = empty(f"PHONEUI_{key.capitalize()}Group", (0, 0, 0), c, root, 0.02)
        for axis in range(3):
            drive(g, "scale", root, f"{key}_visible", axis)
        groups[key] = g
    white = glow("PHONEUI_Mat_White", (1.0, 1.0, 1.0), 2.0, base=(0.9, 0.9, 0.9))
    # --- alert: warning triangle, countdown ring, slide button
    a = groups["alert"]
    m_red = glow("PHONEUI_Mat_AlertBg", (0.85, 0.05, 0.04), 1.5, base=(0.25, 0.02, 0.02))
    m_redmark = material("PHONEUI_Mat_AlertMark", (0.45, 0.02, 0.02), rough=0.6)
    rounded_slab("PHONEUI_AlertBg", 0.0665, 0.1415, T, 0.0098, (0, Y0, 0), c, m_red, a)
    prism("PHONEUI_AlertTriangle", [(0, 0.058), (-0.021, 0.022), (0.021, 0.022)], T, (0, Y0 - 0.0003, 0), c, white, a)
    box("PHONEUI_AlertBar", (0.0042, T, 0.015), (0, Y0 - 0.0006, 0.0395), c, m_redmark, a)
    box("PHONEUI_AlertDot", (0.0042, T, 0.0042), (0, Y0 - 0.0006, 0.0275), c, m_redmark, a)
    for i in range(12):
        ang = math.pi / 2 - 2 * math.pi * i / 12
        m = glow(f"PHONEUI_Mat_CountDot_{i + 1:02d}", (1.0, 1.0, 1.0), 0.1, base=(0.35, 0.05, 0.05))
        cylinder(f"PHONEUI_CountDot_{i + 1:02d}", 0.0024, T, (0.0165 * math.cos(ang), Y0 - 0.0003, -0.010 + 0.0165 * math.sin(ang)), c, m, a, axis="Y", segments=20)
        clamp(drive(m.node_tree, bsdf_path(m, "Emission Strength"), root, "countdown", offset=-3.0 * i, gain=36.0), 0.1, 3.0)
    cylinder("PHONEUI_CountCentre", 0.0075, T, (0, Y0 - 0.0003, -0.010), c, white, a, axis="Y", segments=32)
    rounded_slab("PHONEUI_SlideTrack", 0.050, 0.013, T, 0.0064, (0, Y0 - 0.0003, -0.050), c, m_redmark, a)
    cylinder("PHONEUI_SlideKnob", 0.0054, T, (-0.0180, Y0 - 0.0006, -0.050), c, white, a, axis="Y", segments=32)
    # --- call: handset arc, signal arcs, location pin
    g = groups["call"]
    m_green = glow("PHONEUI_Mat_CallBg", (0.05, 0.75, 0.25), 1.5, base=(0.02, 0.20, 0.07))
    m_greenmark = material("PHONEUI_Mat_CallMark", (0.02, 0.30, 0.10), rough=0.6)
    rounded_slab("PHONEUI_CallBg", 0.0665, 0.1415, T, 0.0098, (0, Y0, 0), c, m_green, g)
    arc_band("PHONEUI_Handset", 0.0105, 0.0160, 20, 160, T, (0, Y0 - 0.0003, 0.026), c, white, g)  # handset: arch with two ear pieces
    for k, ang in enumerate((20, 160)):
        r = math.radians(ang)
        box(f"PHONEUI_HandsetEnd_{k + 1}", (0.0105, T, 0.0080), (0.0132 * math.cos(r), Y0 - 0.0003, 0.026 + 0.0132 * math.sin(r) - 0.002), c, white, g)
    for k, rad in enumerate((0.004, 0.008, 0.012)):
        arc_band(f"PHONEUI_SignalArc_{k + 1}", rad, rad + 0.0020, 50, 130, T, (0, Y0 - 0.0003, 0.047), c, white, g)
    cylinder("PHONEUI_PinHead", 0.0115, T, (0, Y0 - 0.0003, -0.022), c, white, g, axis="Y", segments=40)
    prism("PHONEUI_PinTip", [(-0.0096, -0.0285), (0.0096, -0.0285), (0, -0.046)], T, (0, Y0 - 0.0003, 0), c, white, g)
    cylinder("PHONEUI_PinDot", 0.0046, T, (0, Y0 - 0.0006, -0.022), c, m_greenmark, g, axis="Y", segments=24)
    for m in (m_red, m_green):
        drive_bsdf(m, "Emission Strength", root, "ui_glow")
    save(ASSETS / "phone_ui_screens.blend")


# ---------------------------------------------------------------- schematic effects
def build_fx():
    reset()
    # pressure wave: curved sheets that travel along local +X
    c = new_collection("ASSET_FX_PressureWave")
    root = empty("FXWAVE_Root", (0, 0, 0), c, size=0.3)
    m = glow("FXWAVE_Mat", (0.45, 1.0, 0.6), 2.0)
    control(root, "travel", 0.0, 0.0, 1.0, "Moves the wave fronts 1.0 m along local +X")
    control(root, "strength", 2.0, 0.0, 10.0, "Emission of the wave fronts")
    mover = empty("FXWAVE_Mover", (0, 0, 0), c, root, 0.1)
    drive(mover, "location", root, "travel", 0, gain=1.0)
    for k in range(5):
        s = arc_band(f"FXWAVE_Front_{k + 1}", 0.50, 0.50 + 0.022 - 0.003 * k, -32, 32, 0.50, (-0.50 - 0.11 * k, 0, 0), c, m, mover)
        s.scale = (1, 1, 1 - 0.06 * k)
    drive_bsdf(m, "Emission Strength", root, "strength")

    # sound ripple: rings that shrink toward the centre (sound arriving at the microphone)
    c = new_collection("ASSET_FX_SoundRipple")
    root = empty("FXSOUND_Root", (0, 0, 0), c, size=0.01)
    m = glow("FXSOUND_Mat", (1.0, 0.35, 0.85), 2.0)
    control(root, "phase", 0.0, 0.0, 1.0, "0 = rings wide, 1 = rings collapsed onto the centre")
    control(root, "strength", 2.0, 0.0, 10.0, "Emission of the rings")
    for k, s0 in enumerate((1.0, 0.72, 0.46, 0.22)):
        r = torus(f"FXSOUND_Ring_{k + 1}", 0.010, 0.0004, (0, 0, 0), c, m, root, seg_major=48, seg_minor=8)
        for axis in range(3):
            drive(r, "scale", root, "phase", axis, offset=s0, gain=-(s0 - 0.08))
    drive_bsdf(m, "Emission Strength", root, "strength")

    # call wave: arcs rising along +Z and widening (outgoing emergency call)
    c = new_collection("ASSET_FX_CallWave")
    root = empty("FXCALL_Root", (0, 0, 0), c, size=0.05)
    m = glow("FXCALL_Mat", (0.2, 1.0, 0.45), 2.5)
    control(root, "phase", 0.0, 0.0, 1.0, "Arcs rise 0.6 m and widen as the call goes out")
    control(root, "strength", 2.5, 0.0, 10.0, "Emission of the arcs")
    for k in range(4):
        a = arc_band(f"FXCALL_Arc_{k + 1}", 0.10 + 0.07 * k, 0.118 + 0.07 * k, 50, 130, 0.02, (0, 0, 0), c, m, root)
        drive(a, "location", root, "phase", 2, gain=0.6)
        for axis in (0, 2):
            drive(a, "scale", root, "phase", axis, offset=1.0, gain=0.8)
    drive_bsdf(m, "Emission Strength", root, "strength")

    # GPS trail: position dots, evenly spaced while cruising then bunching up at the stop
    c = new_collection("ASSET_FX_GpsTrail")
    root = empty("FXGPS_Root", (0, 0, 0), c, size=0.5)
    m = glow("FXGPS_Mat", (1.0, 0.85, 0.15), 3.0)
    m_stop = glow("FXGPS_Mat_Stop", (1.0, 0.15, 0.10), 3.0)
    control(root, "progress", 0.0, 0.0, 1.0, "Reveals the 14 dots one after another along local +X (0 to 24 m)")
    control(root, "strength", 3.0, 0.0, 10.0, "Emission of the dots")
    N, L = 14, 24.0
    for i in range(N):
        t = i / (N - 1)
        x = L * (1 - (1 - t) ** 2.4)
        last = i == N - 1
        d = cylinder(f"FXGPS_Dot_{i + 1:02d}", 0.42 if last else 0.28, 0.04, (x, 0, 0.03), c, m_stop if last else m, root, segments=24)
        for axis in range(3):
            clamp(drive(d, "scale", root, "progress", axis, offset=-float(i), gain=float(N)), 0.0, 1.0)
    for mm in (m, m_stop):
        drive_bsdf(mm, "Emission Strength", root, "strength")

    # signal tracers: five paths on the phone board, each with a pulse that runs to the processor
    c = new_collection("ASSET_FX_SignalTracers")
    root = empty("FXSIG_Root", (0, 0, 0), c, size=0.02)  # same axes as PHONEINT_Root
    control(root, "flow", 0.0, 0.0, 1.0, "0 = pulses at the sensors, 1 = pulses arrived at the processor")
    control(root, "strength", 3.0, 0.0, 20.0, "Emission of traces and pulses")
    YT = -0.0013
    paths = {
        "accel": ((1.00, 0.45, 0.10), [(-0.0265, 0.0090), (-0.0265, 0.0245)]),
        "gyro": ((0.10, 0.85, 1.00), [(-0.0180, 0.0090), (-0.0180, 0.0245)]),
        "baro": ((0.25, 1.00, 0.40), [(-0.0220, -0.0090), (-0.0220, 0.0010), (-0.0305, 0.0010), (-0.0305, 0.0310), (-0.0285, 0.0310)]),
        "gps": ((1.00, 0.90, 0.15), [(-0.0220, 0.0530), (-0.0220, 0.0375)]),
        "mic": ((1.00, 0.30, 0.85), [(-0.0105, -0.0690), (-0.0105, 0.0310), (-0.0155, 0.0310)]),
    }
    for sid, (colour, pts) in paths.items():
        m_trace = glow(f"FXSIG_Mat_Trace_{sid}", colour, 3.0)
        m_pulse = glow(f"FXSIG_Mat_Pulse_{sid}", colour, 3.0, base=(1, 1, 1))
        lengths = [math.dist(a, b) for a, b in zip(pts, pts[1:])]
        for k, (a, b) in enumerate(zip(pts, pts[1:])):
            w, h = abs(b[0] - a[0]) + 0.0005, abs(b[1] - a[1]) + 0.0005
            box(f"FXSIG_Trace_{sid}_{k + 1}", (w, 0.0002, h), ((a[0] + b[0]) / 2, YT, (a[1] + b[1]) / 2), c, m_trace, root)
        pulse = cylinder(f"FXSIG_Pulse_{sid}", 0.0013, 0.0004, (pts[0][0], YT - 0.0003, pts[0][1]), c, m_pulse, root, axis="Y", segments=20)
        acc, keys = 0.0, [(0.0, pts[0])]
        for seg, p in zip(lengths, pts[1:]):
            acc += seg
            keys.append((acc / sum(lengths), p))
        drive_curve(pulse, "location", root, "flow", [(t, p[0]) for t, p in keys], 0)
        drive_curve(pulse, "location", root, "flow", [(t, p[1]) for t, p in keys], 2)
        drive_bsdf(m_trace, "Emission Strength", root, "strength", gain=0.35)
        drive_bsdf(m_pulse, "Emission Strength", root, "strength")
        empty(f"ANCHOR_SignalStart_{sid}", (pts[0][0], YT, pts[0][1]), c, root, 0.002)
    empty("ANCHOR_SignalEnd", (-0.022, YT, 0.031), c, root, 0.003)
    save(ASSETS / "fx_schematics.blend")


# ---------------------------------------------------------------- mini cars
def build_mini_cars():
    reset()
    c = new_collection("ASSET_MiniCars")
    root = empty("MINI_Root", (0, 0, 0), c, size=0.5)
    control(root, "drive", 0.0, 0.0, 1.0, "All cars roll along +X; the marked ones stop dead at 0.6 and light up")
    m_chip = material("MINI_Mat_Chip", (0.07, 0.09, 0.14), metallic=0.5, rough=0.35)
    m_lane = material("MINI_Mat_Lane", (0.16, 0.20, 0.30), rough=0.6)
    m_car = material("MINI_Mat_Car", (0.55, 0.75, 1.0), rough=0.4, emission=(0.3, 0.55, 1.0), strength=0.4)
    m_crash = material("MINI_Mat_CrashCar", (1.0, 0.35, 0.15), rough=0.4, emission=(1.0, 0.25, 0.05), strength=0.4)
    box("MINI_Chip", (4.4, 3.2, 0.12), (0, 0, -0.06), c, m_chip, root, bevel=0.04)
    bm = bmesh.new()
    for size, off in (((0.24, 0.12, 0.05), (0, 0, 0.035)), ((0.12, 0.10, 0.04), (-0.01, 0, 0.08))):
        geom = bmesh.ops.create_cube(bm, size=1.0)["verts"]
        for v in geom:
            v.co.x, v.co.y, v.co.z = v.co.x * size[0] + off[0], v.co.y * size[1] + off[1], v.co.z * size[2] + off[2]
    proto = finish("MINI_CarMesh_Proto", bm, c, m_car, root, (0, 0, -5))
    proto.hide_render = proto.hide_viewport = True
    LANES, PER, SPAN, TRAVEL = 9, 8, 4.0, 1.5
    crashed = {(1, 5), (3, 2), (4, 6), (6, 3), (7, 7), (8, 1)}
    for lane in range(LANES):
        y = -1.28 + 0.32 * lane
        box(f"MINI_Lane_{lane + 1}", (4.2, 0.20, 0.006), (0, y, 0.003), c, m_lane, root)
        for k in range(PER):
            x0 = -SPAN / 2 - TRAVEL / 2 + (k + ((lane * 37) % 10) / 10) * (SPAN / PER)
            car = bpy.data.objects.new(f"MINI_Car_{lane + 1}_{k + 1}", proto.data)
            c.objects.link(car)
            car.parent, car.location = root, (x0, y, 0.006)
            if (lane, k) in crashed:
                car.data = proto.data.copy()
                car.data.materials[0] = m_crash
                car.name = f"MINI_CrashCar_{lane + 1}_{k + 1}"
                drive_curve(car, "location", root, "drive", [(0.0, x0), (0.6, x0 + 0.6 * TRAVEL)], 0)
            else:
                drive(car, "location", root, "drive", 0, offset=x0, gain=TRAVEL)
    drive_curve(m_crash.node_tree, bsdf_path(m_crash, "Emission Strength"), root, "drive", [(0.0, 0.4), (0.6, 0.4), (0.68, 6.0)])
    empty("CAM_Target_MiniCars", (0, 0, 0.05), c, root, 0.3, "SPHERE")
    save(ASSETS / "mini_cars.blend")


build_dash()
build_cutaway()
build_ui()
build_fx()
build_mini_cars()
print("SUPPORT_ASSETS_DONE")
