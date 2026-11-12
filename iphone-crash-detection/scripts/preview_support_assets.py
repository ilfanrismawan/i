"""Phase 03b QA: reopen supporting assets, test controls, render Eevee stills in context.

Run:  blender --background --python scripts/preview_support_assets.py -- <project_dir>
Writes previews/support_assets/*.png and reports/support_assets_validation.json
"""
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Matrix, Vector

PROJECT = Path(sys.argv[sys.argv.index("--") + 1]).resolve()
OUT = PROJECT / "previews" / "support_assets"
OUT.mkdir(parents=True, exist_ok=True)
report = {"blender": bpy.app.version_string, "tests": {}, "renders": []}
T = report["tests"]


def setp(root, **props):
    for k, v in props.items():
        root[k] = float(v)
    root.update_tag()


def ev():
    bpy.context.view_layer.update()
    return bpy.context.evaluated_depsgraph_get()


def emission(mat_name, dg):
    m = bpy.data.materials[mat_name].evaluated_get(dg)
    return round(next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED").inputs["Emission Strength"].default_value, 3)


def O(name, dg):
    return bpy.data.objects[name].evaluated_get(dg)


def need(names):
    return [n for n in names if n not in bpy.data.objects]


# ---- 1. per-file structural and control tests
bpy.ops.wm.open_mainfile(filepath=str(PROJECT / "assets" / "car_interior_dash.blend"))
T["dash missing"] = need(["DASH_Root", "ANCHOR_PhoneMount", "ANCHOR_DriverEye", "CAM_Target_Dash"])
T["dash mount rotation z deg (expect -90)"] = round(math.degrees(bpy.data.objects["ANCHOR_PhoneMount"].rotation_euler.z), 1)

bpy.ops.wm.open_mainfile(filepath=str(PROJECT / "assets" / "car_cutaway.blend"))
T["cutaway missing"] = need(["CUT_Root", "ANCHOR_Dash", "ANCHOR_WaveStart", "ANCHOR_CabinCenter", "CAM_Target_Cutaway"])
ys = [(o.matrix_world @ Vector(c)).y for o in bpy.data.objects if o.type == "MESH" for c in o.bound_box]
T["cutaway y range (expect open side at about 0)"] = [round(min(ys), 3), round(max(ys), 3)]

bpy.ops.wm.open_mainfile(filepath=str(PROJECT / "assets" / "phone_ui_screens.blend"))
r = bpy.data.objects["PHONEUI_Root"]
dg = ev()
T["ui default: alert/call group scale (expect 0, 0)"] = [round(O("PHONEUI_AlertGroup", dg).scale.x, 3), round(O("PHONEUI_CallGroup", dg).scale.x, 3)]
setp(r, alert_visible=1, countdown=0.5)
dg = ev()
T["ui alert_visible=1 -> alert scale (expect 1)"] = round(O("PHONEUI_AlertGroup", dg).scale.x, 3)
T["ui countdown=0.5 -> dot 3, dot 7, dot 9 emission (expect 3, 0.1, 0.1)"] = [emission(f"PHONEUI_Mat_CountDot_{i:02d}", dg) for i in (3, 7, 9)]
ui_y = [(o.matrix_world @ Vector(c)).y for o in bpy.data.objects if o.type == "MESH" for c in o.bound_box]
T["ui sits in front of the screen: y range (screen front is -0.00427)"] = [round(min(ui_y), 5), round(max(ui_y), 5)]

bpy.ops.wm.open_mainfile(filepath=str(PROJECT / "assets" / "fx_schematics.blend"))
T["fx missing"] = need(["FXWAVE_Root", "FXSOUND_Root", "FXCALL_Root", "FXGPS_Root", "FXSIG_Root", "ANCHOR_SignalEnd"])
setp(bpy.data.objects["FXWAVE_Root"], travel=1)
setp(bpy.data.objects["FXSOUND_Root"], phase=1)
setp(bpy.data.objects["FXCALL_Root"], phase=1)
setp(bpy.data.objects["FXGPS_Root"], progress=0.5)
setp(bpy.data.objects["FXSIG_Root"], flow=1)
dg = ev()
T["wave travel=1 -> mover x (expect 1.0)"] = round(O("FXWAVE_Mover", dg).location.x, 3)
T["sound phase=1 -> ring 1 scale (expect 0.08)"] = round(O("FXSOUND_Ring_1", dg).scale.x, 3)
T["call phase=1 -> arc 1 z, scale (expect 0.6, 1.8)"] = [round(O("FXCALL_Arc_1", dg).location.z, 3), round(O("FXCALL_Arc_1", dg).scale.x, 3)]
T["gps progress=0.5 -> dot 7, dot 8, dot 9 scale (expect 1, 0, 0)"] = [round(O(f"FXGPS_Dot_{i:02d}", dg).scale.x, 3) for i in (7, 8, 9)]
T["signal flow=1 -> baro pulse x,z (expect -0.0285, 0.031)"] = [round(O("FXSIG_Pulse_baro", dg).location.x, 4), round(O("FXSIG_Pulse_baro", dg).location.z, 4)]
setp(bpy.data.objects["FXSIG_Root"], flow=0.5)
dg = ev()
T["signal flow=0.5 -> mic pulse x,z (expect -0.0105, about -0.0165)"] = [round(O("FXSIG_Pulse_mic", dg).location.x, 4), round(O("FXSIG_Pulse_mic", dg).location.z, 4)]

bpy.ops.wm.open_mainfile(filepath=str(PROJECT / "assets" / "mini_cars.blend"))
r = bpy.data.objects["MINI_Root"]
dg = ev()
x_n0, x_c0 = O("MINI_Car_1_1", dg).location.x, O("MINI_CrashCar_4_3", dg).location.x
setp(r, drive=1)
dg = ev()
T["mini drive=1 -> normal car moved (expect 1.5)"] = round(O("MINI_Car_1_1", dg).location.x - x_n0, 3)
T["mini drive=1 -> marked car moved (expect 0.9, stopped early)"] = round(O("MINI_CrashCar_4_3", dg).location.x - x_c0, 3)
T["mini drive=1 -> marked car emission (expect 6)"] = emission("MINI_Mat_CrashCar", dg)
T["mini car objects"] = sum(o.name.startswith(("MINI_Car_", "MINI_CrashCar_")) for o in bpy.data.objects)

# ---- 2. preview scene with appended copies
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
for eng in ("BLENDER_EEVEE_NEXT", "BLENDER_EEVEE"):
    try:
        scene.render.engine = eng
        break
    except Exception:
        continue
assert "EEVEE" in scene.render.engine
report["render_engine"] = scene.render.engine
scene.render.resolution_x, scene.render.resolution_y, scene.render.resolution_percentage = 540, 960, 100
scene.render.image_settings.file_format = "PNG"
try:
    scene.eevee.taa_render_samples = 32
    scene.view_settings.view_transform = "Standard"
except Exception:
    pass
FILES = {"phone_exterior": ["ASSET_Phone"], "phone_interior_concept": ["ASSET_PhoneInterior"], "car_stylized": ["ASSET_Car"],
         "road_set": ["ASSET_Road"], "car_interior_dash": ["ASSET_CarDash"], "car_cutaway": ["ASSET_CarCutaway"],
         "phone_ui_screens": ["ASSET_PhoneUI"], "mini_cars": ["ASSET_MiniCars"],
         "fx_schematics": ["ASSET_FX_PressureWave", "ASSET_FX_SoundRipple", "ASSET_FX_CallWave", "ASSET_FX_GpsTrail", "ASSET_FX_SignalTracers"]}
colls = {}
for stem, names in FILES.items():
    with bpy.data.libraries.load(str(PROJECT / "assets" / f"{stem}.blend"), link=False) as (src, dst):
        dst.collections = list(names)
    for col in dst.collections:
        colls[col.name] = col
        scene.collection.children.link(col)
world = bpy.data.worlds.new("PREVIEW_World")
world.use_nodes = True
bg = world.node_tree.nodes["Background"]
scene.world = world
for name, energy, rot in (("Key", 3.0, (50, 0, -35)), ("Fill", 1.0, (60, 0, 150))):
    L = bpy.data.objects.new(f"PREVIEW_{name}", bpy.data.lights.new(f"PREVIEW_{name}", "SUN"))
    L.data.energy = energy
    L.rotation_euler = tuple(math.radians(a) for a in rot)
    scene.collection.objects.link(L)
cam = bpy.data.objects.new("PREVIEW_Cam", bpy.data.cameras.new("PREVIEW_Cam"))
scene.collection.objects.link(cam)
scene.camera = cam
D = bpy.data.objects
PHONE, UI, INT, CAR, DASH, CUT = D["PHONE_Root"], D["PHONEUI_Root"], D["PHONEINT_Root"], D["CAR_Root"], D["DASH_Root"], D["CUT_Root"]
UI.parent = PHONE
INT.parent = PHONE
D["FXSIG_Root"].parent = PHONE
SKY, DARK = (0.55, 0.74, 0.95), (0.04, 0.05, 0.08)


def place(obj, matrix):
    obj.matrix_world = matrix
    bpy.context.view_layer.update()


def shot(name, show, cam_pos, target, lens, sky, clip=(0.005, 500)):
    for cname, col in colls.items():
        col.hide_render = cname not in show
    bg.inputs[0].default_value = (*sky, 1)
    cam.location, cam.data.lens = cam_pos, lens
    cam.data.clip_start, cam.data.clip_end = clip
    cam.rotation_euler = (Vector(target) - Vector(cam_pos)).to_track_quat("-Z", "Y").to_euler()
    bpy.context.view_layer.update()
    path = OUT / f"{name}.png"
    scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)
    report["renders"].append({"file": f"previews/support_assets/{name}.png", "exists": path.is_file()})


# UI close-ups on the phone (phone at origin)
setp(UI, alert_visible=1, call_visible=0, countdown=0.5)
shot("01_ui_alert_countdown_half", ["ASSET_Phone", "ASSET_PhoneUI"], (0.04, -0.30, 0.01), (0, 0, 0), 60, DARK)
setp(UI, alert_visible=0, call_visible=1)
shot("02_ui_call", ["ASSET_Phone", "ASSET_PhoneUI"], (0.04, -0.30, 0.01), (0, 0, 0), 60, DARK)
# signal tracers on the interior
setp(UI, call_visible=0)
setp(PHONE, shell_opacity=0.12)
setp(INT, glow_processor=1.0, glow_accel=2, glow_gyro=2, glow_baro=2, glow_gps=2, glow_mic=2)
setp(D["FXSIG_Root"], flow=0.55, strength=4)
shot("03_signal_tracers_flow_055", ["ASSET_Phone", "ASSET_PhoneInterior", "ASSET_FX_SignalTracers"], (0.02, -0.30, 0.0), (0, 0, 0), 60, DARK)
# sound ripple under the microphone hole
setp(PHONE, shell_opacity=1.0)
mic = D["ANCHOR_MicHole"].matrix_world.translation
place(D["FXSOUND_Root"], Matrix.Translation(mic + Vector((0, 0, -0.006))))
setp(D["FXSOUND_Root"], phase=0.35)
shot("04_sound_ripple_at_mic", ["ASSET_Phone", "ASSET_FX_SoundRipple"], (0.03, -0.05, -0.115), tuple(mic), 50, DARK, (0.002, 5))

# dashboard: phone on the mount, seen from the driver's eye
mount = D["ANCHOR_PhoneMount"].matrix_world.copy()
place(PHONE, mount)
setp(UI, alert_visible=1, countdown=0.75)
eye = tuple(D["ANCHOR_DriverEye"].matrix_world.translation)
tgt = tuple(mount.translation)
shot("05_dash_driver_view_alert", ["ASSET_CarDash", "ASSET_Phone", "ASSET_PhoneUI"], (-0.62, -0.20, 0.30), tgt, 30, SKY)
setp(UI, alert_visible=0, call_visible=1)
place(D["FXCALL_Root"], Matrix.Translation(mount.translation + Vector((0, 0, 0.09))) @ Matrix.Rotation(math.radians(90), 4, "Z"))
setp(D["FXCALL_Root"], phase=0.5)
shot("06_dash_low_angle_call_wave", ["ASSET_CarDash", "ASSET_Phone", "ASSET_PhoneUI", "ASSET_FX_CallWave"], (-0.48, -0.02, 0.02), (0.046, 0.06, 0.30), 28, SKY)

# cutaway cabin with pressure wave, seen from the open side
place(CUT, Matrix.Identity(4))
setp(UI, call_visible=0)
dash = D["ANCHOR_Dash"].matrix_world.translation if "ANCHOR_Dash.001" not in D else D["ANCHOR_Dash.001"].matrix_world.translation
cut_dash = next(o for o in colls["ASSET_CarCutaway"].all_objects if o.name.startswith("ANCHOR_Dash")).matrix_world.translation
place(PHONE, Matrix.Translation(cut_dash + Vector((0, 0, 0.09))) @ Matrix.Rotation(math.radians(-90), 4, "Z"))
ws = D["ANCHOR_WaveStart"].matrix_world.translation
place(D["FXWAVE_Root"], Matrix.Translation(ws) @ Matrix.Rotation(math.radians(180), 4, "Z"))  # fronts run from the windshield toward the rear
setp(D["FXWAVE_Root"], travel=0.75, strength=0.7)
shot("07_cutaway_pressure_wave", ["ASSET_CarCutaway", "ASSET_Phone", "ASSET_FX_PressureWave"], (0.1, -5.2, 1.25), (0.1, 0.4, 0.95), 50, SKY)

# GPS trail on the road, car stopped at the barrier
stop = D["ANCHOR_CarStop"].matrix_world.translation
place(CAR, Matrix.Translation(stop))
place(D["FXGPS_Root"], Matrix.Translation(stop + Vector((-24.0, 0, 0))))
setp(D["FXGPS_Root"], progress=1)
shot("08_gps_trail_overhead", ["ASSET_Road", "ASSET_Car", "ASSET_FX_GpsTrail"], (stop.x - 9.0, 1.74, 34.0), (stop.x - 9.0, 1.75, 0), 32, SKY)

# mini cars
setp(D["MINI_Root"], drive=0.85)
shot("09_mini_cars_drive_085", ["ASSET_MiniCars"], (-3.2, -3.6, 3.4), (0, 0, 0), 30, DARK)

(PROJECT / "reports").mkdir(exist_ok=True)
(PROJECT / "reports" / "support_assets_validation.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
print("TESTS", json.dumps(T, indent=1))
print("RENDERS_OK", all(r["exists"] for r in report["renders"]), len(report["renders"]), report["render_engine"])
