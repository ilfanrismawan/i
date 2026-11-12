"""Phase 03 QA: reopen mechanism assets, test every control, render Eevee stills (rest vs actuated).

Run:  blender --background --python scripts/preview_mechanism_assets.py -- <project_dir>
Writes previews/mechanism_assets/*.png and reports/mechanism_assets_validation.json
"""
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

PROJECT = Path(sys.argv[sys.argv.index("--") + 1]).resolve()
OUT = PROJECT / "previews" / "mechanism_assets"
OUT.mkdir(parents=True, exist_ok=True)
SPEC = {
    "phone_interior_concept": ("ASSET_PhoneInterior", "PHONEINT_Root",
                               ["ANCHOR_Processor", "ANCHOR_Sensor_Accel", "ANCHOR_Sensor_Gyro", "ANCHOR_Sensor_Baro", "ANCHOR_Sensor_Gps", "ANCHOR_Sensor_Mic", "CAM_Target_PhoneInterior"],
                               ["glow_processor", "glow_accel", "glow_gyro", "glow_baro", "glow_gps", "glow_mic"]),
    "sensor_accel_concept": ("ASSET_SensorAccel", "ACCEL_Root", ["ANCHOR_AccelMass", "CAM_Target_Accel"], ["displacement", "mass_glow"]),
    "sensor_gyro_concept": ("ASSET_SensorGyro", "GYRO_Root", ["ANCHOR_GyroRing", "CAM_Target_Gyro"], ["twist", "vibration", "ring_glow"]),
    "sensor_baro_concept": ("ASSET_SensorBaro", "BARO_Root", ["ANCHOR_BaroMembrane", "CAM_Target_Baro"], ["pressure", "membrane_glow"]),
}
report = {"blender": bpy.app.version_string, "assets": {}, "renders": []}


def evaluate():
    bpy.context.view_layer.update()
    return bpy.context.evaluated_depsgraph_get()


def bounds(objs):
    dg = evaluate()
    pts = [o.evaluated_get(dg).matrix_world @ Vector(c) for o in objs if o.type == "MESH" for c in o.bound_box]
    lo = [round(min(p[i] for p in pts), 4) for i in range(3)]
    hi = [round(max(p[i] for p in pts), 4) for i in range(3)]
    return lo, hi


def setp(root, **props):
    for k, v in props.items():
        root[k] = float(v)
    root.update_tag()


for stem, (coll_name, root_name, anchors, controls) in SPEC.items():
    bpy.ops.wm.open_mainfile(filepath=str(PROJECT / "assets" / f"{stem}.blend"))
    coll, root = bpy.data.collections[coll_name], bpy.data.objects[root_name]
    lo, hi = bounds(coll.all_objects)
    e = {"objects": len(coll.all_objects), "bbox_min": lo, "bbox_max": hi,
         "missing_anchors": [a for a in anchors if a not in bpy.data.objects],
         "missing_controls": [c for c in controls if c not in root.keys()], "control_tests": {}}
    t = e["control_tests"]
    if stem == "phone_interior_concept":
        shell = ((-0.03575, -0.0039, -0.07335), (0.03575, 0.0039, 0.07335))  # phone_exterior body
        e["fits_inside_phone_shell"] = all(lo[i] >= shell[0][i] - 1e-5 and hi[i] <= shell[1][i] + 1e-5 for i in range(3))
        setp(root, glow_accel=5)
        dg = evaluate()
        m = bpy.data.materials["PHONEINT_Mat_Sensor_Accel"].evaluated_get(dg)
        b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
        t["glow_accel=5 -> emission strength"] = round(b.inputs["Emission Strength"].default_value, 3)
    elif stem == "sensor_accel_concept":
        setp(root, displacement=1)
        dg = evaluate()
        t["displacement=1 -> mass x (expect 0.38)"] = round(bpy.data.objects["ACCEL_Mass"].evaluated_get(dg).matrix_world.translation.x, 3)
        t["displacement=1 -> west spring length (expect 1.03)"] = round(bpy.data.objects["ACCEL_Spring_WN"].evaluated_get(dg).scale.x, 3)
        t["displacement=1 -> east spring length (expect 0.27)"] = round(bpy.data.objects["ACCEL_Spring_EN"].evaluated_get(dg).scale.x, 3)
        tip = bpy.data.objects["ACCEL_MovingFinger_NE1"].evaluated_get(dg).matrix_world.translation.x + 0.50
        t["displacement=1 -> clearance moving finger tip to fixed block (must be > 0)"] = round(0.94 - tip, 3)
    elif stem == "sensor_gyro_concept":
        setp(root, twist=1, vibration=1)
        dg = evaluate()
        r = bpy.data.objects["GYRO_Rotor"].evaluated_get(dg)
        t["twist=1 -> rotor Z degrees (expect 40)"] = round(math.degrees(r.rotation_euler.z), 2)
        t["vibration=1 -> rotor scale x,y (expect 1.14, 0.86)"] = [round(r.scale.x, 3), round(r.scale.y, 3)]
    elif stem == "sensor_baro_concept":
        setp(root, pressure=1)
        dg = evaluate()
        ob = bpy.data.objects["BARO_Membrane"].evaluated_get(dg)
        me = ob.to_mesh()
        t["pressure=1 -> lowest membrane point, local z (expect about -0.33)"] = round(min(v.co.z for v in me.vertices), 3)
        ob.to_mesh_clear()
    report["assets"][stem] = e

# ---- preview scene (appended copies)
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
    scene.eevee.taa_render_samples = 48
    scene.view_settings.view_transform = "Standard"
except Exception:
    pass
colls = {}
for stem in list(SPEC) + ["phone_exterior"]:
    name = SPEC[stem][0] if stem in SPEC else "ASSET_Phone"
    with bpy.data.libraries.load(str(PROJECT / "assets" / f"{stem}.blend"), link=False) as (src, dst):
        dst.collections = [name]
    colls[stem] = dst.collections[0]
    scene.collection.children.link(colls[stem])
world = bpy.data.worlds.new("PREVIEW_World")
world.use_nodes = True
world.node_tree.nodes["Background"].inputs[0].default_value = (0.05, 0.06, 0.09, 1)
world.node_tree.nodes["Background"].inputs[1].default_value = 1.0
scene.world = world
for name, energy, rot in (("Key", 3.0, (50, 0, -35)), ("Fill", 1.2, (60, 0, 150))):
    L = bpy.data.objects.new(f"PREVIEW_{name}", bpy.data.lights.new(f"PREVIEW_{name}", "SUN"))
    L.data.energy = energy
    L.rotation_euler = tuple(math.radians(a) for a in rot)
    scene.collection.objects.link(L)
cam = bpy.data.objects.new("PREVIEW_Cam", bpy.data.cameras.new("PREVIEW_Cam"))
scene.collection.objects.link(cam)
scene.camera = cam
R = {k: bpy.data.objects[SPEC[k][1]] for k in SPEC}
PHONE = bpy.data.objects["PHONE_Root"]


def shot(name, show, cam_pos, target, lens, clip=(0.01, 100)):
    for stem, c in colls.items():
        c.hide_render = stem not in show
    cam.location, cam.data.lens = cam_pos, lens
    cam.data.clip_start, cam.data.clip_end = clip
    cam.rotation_euler = (Vector(target) - Vector(cam_pos)).to_track_quat("-Z", "Y").to_euler()
    bpy.context.view_layer.update()
    path = OUT / f"{name}.png"
    scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)
    report["renders"].append({"file": f"previews/mechanism_assets/{name}.png", "exists": path.is_file()})


I = "phone_interior_concept"
setp(R[I], glow_processor=1.2, glow_accel=2.5, glow_gyro=2.5, glow_baro=2.5, glow_gps=2.5, glow_mic=2.5)
shot("01_interior_alone_front", [I], (0.0, -0.33, 0.0), (0, 0, 0), 60, (0.005, 10))
setp(PHONE, shell_opacity=0.18, screen_glow=0.0)
shot("02_interior_in_shell_xray_three_quarter", [I, "phone_exterior"], (0.11, -0.31, 0.03), (0, 0, 0), 60, (0.005, 10))
setp(PHONE, shell_opacity=1.0)
shot("03_shell_solid_hides_interior", [I, "phone_exterior"], (0.11, -0.31, 0.03), (0, 0, 0), 60, (0.005, 10))

MACRO_CAM, MACRO_T = (0.0, -3.9, 3.6), (0, 0, 0.15)
A, G, B = "sensor_accel_concept", "sensor_gyro_concept", "sensor_baro_concept"
shot("04_accel_rest", [A], MACRO_CAM, MACRO_T, 28)
setp(R[A], displacement=1, mass_glow=0.6)
shot("05_accel_displacement_plus1", [A], MACRO_CAM, MACRO_T, 28)
shot("06_gyro_rest", [G], MACRO_CAM, MACRO_T, 28)
setp(R[G], twist=1, vibration=1, ring_glow=1.0)
shot("07_gyro_twist_vibration", [G], MACRO_CAM, MACRO_T, 28)
BARO_CAM, BARO_T = (0.0, -3.6, 2.9), (0, 0, 0.3)
shot("08_baro_rest", [B], BARO_CAM, BARO_T, 28)
setp(R[B], pressure=1, membrane_glow=0.3)
shot("09_baro_pressure_plus1", [B], BARO_CAM, BARO_T, 28)
setp(R[B], pressure=-1)
shot("10_baro_pressure_minus1", [B], BARO_CAM, BARO_T, 28)

(PROJECT / "reports").mkdir(exist_ok=True)
(PROJECT / "reports" / "mechanism_assets_validation.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
print("VALIDATION", json.dumps(report["assets"]))
print("RENDERS_OK", all(r["exists"] for r in report["renders"]), len(report["renders"]), report["render_engine"])
