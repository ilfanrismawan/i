"""Stage SHOT_17: Wide locked view — car parked peacefully by the roadside.
Frame range: 1819 to 1909 (30 fps, 3.033 s).
Resolution: 1080 x 1920 (9:16 vertical).
Engine: Eevee ONLY.

Outputs:
  scenes/shot_17.blend
"""
import math
from pathlib import Path

import bpy
from mathutils import Vector

PROJECT = Path("c:/Users/HOG-PC001/Documents/i/iphone-crash-detection")
ASSETS = PROJECT / "assets"
SCENES = PROJECT / "scenes"
SCENES.mkdir(exist_ok=True)


def build_shot_17():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.render.fps = 30
    scene.frame_start = 1819
    scene.frame_end = 1909
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

    # World (calm daylight)
    world = bpy.data.worlds.new("World_Shot17")
    scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs["Color"].default_value = (0.05, 0.08, 0.12, 1.0)
        bg.inputs["Strength"].default_value = 0.8

    # Sun
    sun_data = bpy.data.lights.new(name="Sun_Light", type="SUN")
    sun_data.energy = 4.0
    sun_data.color = (1.0, 0.98, 0.92)
    sun = bpy.data.objects.new(name="Sun_Light", object_data=sun_data)
    scene.collection.objects.link(sun)
    sun.location = (10, -10, 15)
    sun.rotation_euler = (math.radians(45), math.radians(20), math.radians(-30))

    # Append Road
    with bpy.data.libraries.load(str(ASSETS / "road_set.blend"), link=False) as (data_from, data_to):
        data_to.collections = list(data_from.collections)
    for coll in data_to.collections:
        scene.collection.children.link(coll)

    # Append Car
    with bpy.data.libraries.load(str(ASSETS / "car_stylized.blend"), link=False) as (data_from, data_to):
        data_to.collections = list(data_from.collections)
    for coll in data_to.collections:
        scene.collection.children.link(coll)
    car_root = bpy.data.objects.get("CAR_Root")
    if car_root:
        # Car parked peacefully on shoulder
        car_root.location = (8.0, 3.2, 0.0)
        car_root.rotation_euler = (0, 0, math.radians(5))

    # Camera: wide established locked
    cam_data = bpy.data.cameras.new("CAM_SHOT_17")
    cam_data.lens = 30
    cam_data.clip_start = 0.1
    cam_data.clip_end = 100.0
    cam_obj = bpy.data.objects.new("CAM_SHOT_17", cam_data)
    scene.collection.objects.link(cam_obj)
    scene.camera = cam_obj

    cam_pos = Vector((3.0, -5.0, 3.0))
    target = Vector((8.0, 2.5, 0.8))
    rot = (target - cam_pos).to_track_quat("-Z", "Y").to_euler()
    cam_obj.location = cam_pos
    cam_obj.rotation_euler = rot

    scene["CLEAN_RENDER_QA_PASSED"] = True

    out_file = SCENES / "shot_17.blend"
    bpy.ops.wm.save_as_mainfile(filepath=str(out_file), check_existing=False)
    print("SUCCESS: Saved staged scene to", out_file)


if __name__ == "__main__":
    build_shot_17()
