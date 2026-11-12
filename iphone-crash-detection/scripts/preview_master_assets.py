"""Phase 02 QA: reopen the master assets, validate them, and render Eevee preview stills.

Run:  blender --background --python scripts/preview_master_assets.py -- <project_dir>
Writes previews/master_assets/*.png and reports/master_assets_validation.json
"""
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

PROJECT = Path(sys.argv[sys.argv.index("--") + 1]).resolve()
OUT = PROJECT / "previews" / "master_assets"
OUT.mkdir(parents=True, exist_ok=True)
SPEC = {
    "phone_exterior": ("ASSET_Phone", "PHONE_Root", ["ANCHOR_ScreenCenter", "ANCHOR_MicHole", "ANCHOR_Interior", "CAM_Target_Phone"], ["shell_opacity", "screen_glow"]),
    "car_stylized": ("ASSET_Car", "CAR_Root", ["ANCHOR_FrontBumper", "ANCHOR_Dash", "ANCHOR_CabinCenter", "CAM_Target_Car"], ["wheel_rotation", "headlight_glow"]),
    "road_set": ("ASSET_Road", "ROAD_Root", ["ANCHOR_CarStart", "ANCHOR_CarStop", "ANCHOR_BarrierFace", "CAM_Target_Road"], []),
}
report = {"blender": bpy.app.version_string, "assets": {}, "renders": []}


def bounds(objs):
    dg = bpy.context.evaluated_depsgraph_get()
    pts = [o.evaluated_get(dg).matrix_world @ Vector(c) for o in objs if o.type == "MESH" for c in o.bound_box]
    lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    return [round(v, 4) for v in lo], [round(v, 4) for v in hi], [round(v, 4) for v in (hi - lo)]


# ---- 1. reopen each asset file on its own and check structure + controls
for stem, (coll_name, root_name, anchors, controls) in SPEC.items():
    bpy.ops.wm.open_mainfile(filepath=str(PROJECT / "assets" / f"{stem}.blend"))
    coll = bpy.data.collections.get(coll_name)
    root = bpy.data.objects.get(root_name)
    lo, hi, size = bounds(coll.all_objects)
    entry = {"collection": bool(coll), "root": bool(root), "objects": len(coll.all_objects),
             "meshes": sum(o.type == "MESH" for o in coll.all_objects), "bbox_min": lo, "bbox_max": hi, "size_m": size,
             "missing_anchors": [a for a in anchors if a not in bpy.data.objects],
             "missing_controls": [c for c in controls if c not in root.keys()], "control_tests": {}}
    if stem == "phone_exterior":
        root["shell_opacity"] = 0.25
        root["screen_glow"] = 4.0
        root.update_tag()
        bpy.context.view_layer.update()
        dg = bpy.context.evaluated_depsgraph_get()
        m = bpy.data.materials["PHONE_Mat_Frame"].evaluated_get(dg)
        b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
        s = bpy.data.materials["PHONE_Mat_Screen"].evaluated_get(dg)
        sb = next(n for n in s.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
        entry["control_tests"] = {"shell_opacity=0.25 -> frame alpha": round(b.inputs["Alpha"].default_value, 3),
                                  "screen_glow=4 -> emission strength": round(sb.inputs["Emission Strength"].default_value, 3)}
    if stem == "car_stylized":
        root["wheel_rotation"] = 1.5
        root.update_tag()
        bpy.context.view_layer.update()
        dg = bpy.context.evaluated_depsgraph_get()
        entry["control_tests"] = {"wheel_rotation=1.5 -> wheel Y rotation": round(bpy.data.objects["CAR_Wheel_FL"].evaluated_get(dg).rotation_euler[1], 3)}
    report["assets"][stem] = entry

# ---- 2. preview scene: append copies (source files stay untouched)
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
for eng in ("BLENDER_EEVEE_NEXT", "BLENDER_EEVEE"):
    try:
        scene.render.engine = eng
        break
    except Exception:
        continue
report["render_engine"] = scene.render.engine
assert "EEVEE" in scene.render.engine, "Eevee is required"
scene.render.resolution_x, scene.render.resolution_y, scene.render.resolution_percentage = 540, 960, 100
scene.render.image_settings.file_format = "PNG"
try:
    scene.eevee.taa_render_samples = 32
except Exception:
    pass
try:
    scene.view_settings.view_transform = "Standard"
except Exception:
    pass

colls = {}
for stem, (coll_name, *_rest) in SPEC.items():
    with bpy.data.libraries.load(str(PROJECT / "assets" / f"{stem}.blend"), link=False) as (src, dst):
        dst.collections = [coll_name]
    colls[stem] = dst.collections[0]
    scene.collection.children.link(colls[stem])

world = bpy.data.worlds.new("PREVIEW_World")
world.use_nodes = True
bg = world.node_tree.nodes["Background"]
scene.world = world
sun = bpy.data.objects.new("PREVIEW_Sun", bpy.data.lights.new("PREVIEW_Sun", "SUN"))
sun.data.energy = 3.5
sun.data.angle = math.radians(8)
sun.rotation_euler = (math.radians(52), 0, math.radians(-38))
scene.collection.objects.link(sun)
fill = bpy.data.objects.new("PREVIEW_Fill", bpy.data.lights.new("PREVIEW_Fill", "SUN"))
fill.data.energy = 1.0
fill.rotation_euler = (math.radians(60), 0, math.radians(150))
scene.collection.objects.link(fill)
cam = bpy.data.objects.new("PREVIEW_Cam", bpy.data.cameras.new("PREVIEW_Cam"))
scene.collection.objects.link(cam)
scene.camera = cam
phone, car = bpy.data.objects["PHONE_Root"], bpy.data.objects["CAR_Root"]
start, stop = bpy.data.objects["ANCHOR_CarStart"], bpy.data.objects["ANCHOR_CarStop"]


def shot(name, show, cam_pos, target, lens, sky, clip=(0.01, 500)):
    for stem, c in colls.items():
        c.hide_render = stem not in show
    bg.inputs[0].default_value = (*sky, 1)
    cam.location = cam_pos
    cam.data.lens = lens
    cam.data.clip_start, cam.data.clip_end = clip
    cam.rotation_euler = (Vector(target) - Vector(cam_pos)).to_track_quat("-Z", "Y").to_euler()
    bpy.context.view_layer.update()
    path = OUT / f"{name}.png"
    scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)
    report["renders"].append({"file": f"previews/master_assets/{name}.png", "exists": path.is_file(),
                              "bytes": path.stat().st_size if path.is_file() else 0})


STUDIO, SKY = (0.82, 0.86, 0.92), (0.55, 0.74, 0.95)
shot("01_phone_front", ["phone_exterior"], (0.10, -0.30, 0.04), (0, 0, 0), 60, STUDIO, (0.005, 10))
shot("02_phone_back", ["phone_exterior"], (-0.11, 0.30, 0.05), (0, 0, 0), 60, STUDIO, (0.005, 10))
shot("03_phone_bottom_macro", ["phone_exterior"], (0.02, -0.035, -0.125), (0, 0, -0.072), 50, STUDIO, (0.002, 5))
phone["shell_opacity"] = 0.3
phone.update_tag()
shot("04_phone_shell_opacity_030", ["phone_exterior"], (0.10, -0.30, 0.04), (0, 0, 0), 60, STUDIO, (0.005, 10))
phone["shell_opacity"] = 1.0
phone.update_tag()

car.location = (4.0, start.location.y, 0)
shot("05_car_three_quarter", ["car_stylized", "road_set"], (10.5, -4.6, 2.3), (4.0, 1.75, 0.7), 40, SKY)
shot("06_car_rear_three_quarter", ["car_stylized", "road_set"], (-2.5, 7.2, 2.0), (4.0, 1.75, 0.7), 40, SKY)
car.location = (-2.0, start.location.y, 0)
shot("07_road_wide_shot01_framing", ["car_stylized", "road_set"], (-13.0, -9.5, 7.5), (5.0, 1.75, 0.4), 28, SKY)
car.location = stop.location
shot("08_car_at_barrier_profile", ["car_stylized", "road_set"], (11.5, -8.5, 1.3), (11.9, 1.75, 0.75), 45, SKY)
shot("09_road_top_down", ["car_stylized", "road_set"], (9.0, 1.75, 26.0), (9.0, 1.76, 0.0), 35, SKY)
bumper = bpy.data.objects["ANCHOR_FrontBumper"].matrix_world.translation
face = bpy.data.objects["ANCHOR_BarrierFace"].matrix_world.translation
report["car_stop_contact_gap_m"] = round(face.x - bumper.x, 4)

(PROJECT / "reports").mkdir(exist_ok=True)
(PROJECT / "reports" / "master_assets_validation.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
print("PREVIEW_DONE", json.dumps(report["assets"], indent=1))
print("RENDERS", json.dumps(report["renders"]))
print("GAP", report["car_stop_contact_gap_m"], "ENGINE", report["render_engine"])
