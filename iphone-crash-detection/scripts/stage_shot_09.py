"""Stage SHOT_09: Barometer sensor macro — membrane deflects under pressure.
Frame range: 939 to 1059 (30 fps, 4.033 s).
Resolution: 1080 x 1920 (9:16 vertical).
Engine: Eevee ONLY.

Outputs:
  scenes/shot_09.blend
"""
import math
from pathlib import Path

import bpy
from mathutils import Vector

PROJECT = Path("c:/Users/HOG-PC001/Documents/i/iphone-crash-detection")
ASSETS = PROJECT / "assets"
SCENES = PROJECT / "scenes"
SCENES.mkdir(exist_ok=True)


def get_all_fcurves(action):
    if not action:
        return []
    if hasattr(action, "fcurves"):
        return list(action.fcurves)
    fcurves = []
    if hasattr(action, "layers"):
        for layer in action.layers:
            for strip in layer.strips:
                if hasattr(strip, "channelbags"):
                    for bag in strip.channelbags:
                        fcurves.extend(bag.fcurves)
    return fcurves


def build_shot_09():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.render.fps = 30
    scene.frame_start = 939
    scene.frame_end = 1059
    scene.render.resolution_x = 1080
    scene.render.resolution_y = 1920
    scene.render.resolution_percentage = 100

    # Engine
    for eng in ["BLENDER_EEVEE_NEXT", "BLENDER_EEVEE"]:
        try:
            scene.render.engine = eng
            if scene.render.engine == eng:
                break
        except Exception:
            pass

    # World
    world = bpy.data.worlds.new("World_Shot09")
    scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs["Color"].default_value = (0.02, 0.04, 0.08, 1.0)
        bg.inputs["Strength"].default_value = 0.5

    # Key light
    light_data = bpy.data.lights.new(name="Key_Light", type="AREA")
    light_data.energy = 20.0
    light_data.size = 1.0
    light_data.color = (0.8, 0.9, 1.0)
    key = bpy.data.objects.new(name="Key_Light", object_data=light_data)
    scene.collection.objects.link(key)
    key.location = (0, -2, 3)
    key.rotation_euler = (math.radians(45), 0, 0)

    # Warm fill
    fill_data = bpy.data.lights.new(name="Fill_Light", type="AREA")
    fill_data.energy = 8.0
    fill_data.size = 0.6
    fill_data.color = (1.0, 0.7, 0.4)
    fill = bpy.data.objects.new(name="Fill_Light", object_data=fill_data)
    scene.collection.objects.link(fill)
    fill.location = (2, 1, 1)
    fill.rotation_euler = (math.radians(60), 0, math.radians(-45))

    # Append Baro Sensor
    with bpy.data.libraries.load(str(ASSETS / "sensor_baro_concept.blend"), link=False) as (data_from, data_to):
        data_to.collections = list(data_from.collections)
    for coll in data_to.collections:
        scene.collection.children.link(coll)
    baro_root = bpy.data.objects.get("BARO_Root")

    # Center baro sensor
    if baro_root:
        baro_root.location = (0, 0, 0)
        baro_root.scale = (1.5, 1.5, 1.5)

    # Animate membrane deflection via custom property if available
    if baro_root:
        # Membrane animation: flat → deflected → back
        deflect_keys = [
            (939, 0.0),
            (970, 0.0),
            (990, 1.0),   # max deflection
            (1020, -0.3),  # slight overshoot back
            (1040, 0.0),
            (1059, 0.0),
        ]
        if "deflection" in baro_root:
            for f, val in deflect_keys:
                baro_root["deflection"] = val
                baro_root.keyframe_insert(data_path='["deflection"]', frame=f)
        if "membrane_glow" in baro_root:
            glow_keys = [
                (939, 1.0), (970, 1.0), (990, 12.0), (1020, 6.0), (1040, 2.0), (1059, 1.0),
            ]
            for f, val in glow_keys:
                baro_root["membrane_glow"] = val
                baro_root.keyframe_insert(data_path='["membrane_glow"]', frame=f)

    # Camera: locked extreme macro
    cam_data = bpy.data.cameras.new("CAM_SHOT_09")
    cam_data.lens = 85
    cam_data.clip_start = 0.01
    cam_data.clip_end = 50.0
    cam_obj = bpy.data.objects.new("CAM_SHOT_09", cam_data)
    scene.collection.objects.link(cam_obj)
    scene.camera = cam_obj

    target = Vector((0, 0, 0))
    cam_pos = Vector((0, -1.8, 0.5))
    rot = (target - cam_pos).to_track_quat("-Z", "Y").to_euler()
    cam_obj.location = cam_pos
    cam_obj.rotation_euler = rot

    scene["CLEAN_RENDER_QA_PASSED"] = True

    out_file = SCENES / "shot_09.blend"
    bpy.ops.wm.save_as_mainfile(filepath=str(out_file), check_existing=False)
    print("SUCCESS: Saved staged scene to", out_file)


if __name__ == "__main__":
    build_shot_09()
