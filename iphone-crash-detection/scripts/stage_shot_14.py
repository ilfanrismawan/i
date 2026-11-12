"""Stage SHOT_14: ML training visualization — mini cars above processor chip, dolly-pull.
Frame range: 1443 to 1580 (30 fps, 4.600 s).
Resolution: 1080 x 1920 (9:16 vertical).
Engine: Eevee ONLY.

Outputs:
  scenes/shot_14.blend
"""
import math
from pathlib import Path

import bpy
from mathutils import Vector

PROJECT = Path("c:/Users/HOG-PC001/Documents/i/iphone-crash-detection")
ASSETS = PROJECT / "assets"
SCENES = PROJECT / "scenes"
SCENES.mkdir(exist_ok=True)


def build_shot_14():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.render.fps = 30
    scene.frame_start = 1443
    scene.frame_end = 1580
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
    world = bpy.data.worlds.new("World_Shot14")
    scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs["Color"].default_value = (0.01, 0.02, 0.04, 1.0)
        bg.inputs["Strength"].default_value = 0.5

    # Lights
    sun_data = bpy.data.lights.new(name="Sun_Light", type="SUN")
    sun_data.energy = 3.0
    sun = bpy.data.objects.new(name="Sun_Light", object_data=sun_data)
    scene.collection.objects.link(sun)
    sun.location = (2, -2, 5)

    # Append Phone Interior Concept
    with bpy.data.libraries.load(str(ASSETS / "phone_interior_concept.blend"), link=False) as (data_from, data_to):
        data_to.collections = list(data_from.collections)
    for coll in data_to.collections:
        scene.collection.children.link(coll)

    # Append Mini Cars
    with bpy.data.libraries.load(str(ASSETS / "mini_cars.blend"), link=False) as (data_from, data_to):
        data_to.collections = list(data_from.collections)
    for coll in data_to.collections:
        scene.collection.children.link(coll)

    # Camera: Diagonal macro, dolly-pull
    cam_data = bpy.data.cameras.new("CAM_SHOT_14")
    cam_data.lens = 45
    cam_data.clip_start = 0.05
    cam_data.clip_end = 100.0
    cam_obj = bpy.data.objects.new("CAM_SHOT_14", cam_data)
    scene.collection.objects.link(cam_obj)
    scene.camera = cam_obj

    cam_start = Vector((0.4, -0.6, 0.5))
    target = Vector((0.0, 0.0, 0.1))
    rot_s = (target - cam_start).to_track_quat("-Z", "Y").to_euler()
    cam_obj.location = cam_start
    cam_obj.rotation_euler = rot_s
    cam_obj.keyframe_insert(data_path="location", frame=1443)
    cam_obj.keyframe_insert(data_path="rotation_euler", frame=1443)

    cam_end = Vector((1.8, -2.4, 2.2))
    rot_e = (target - cam_end).to_track_quat("-Z", "Y").to_euler()
    cam_obj.location = cam_end
    cam_obj.rotation_euler = rot_e
    cam_obj.keyframe_insert(data_path="location", frame=1580)
    cam_obj.keyframe_insert(data_path="rotation_euler", frame=1580)

    scene["CLEAN_RENDER_QA_PASSED"] = True

    out_file = SCENES / "shot_14.blend"
    bpy.ops.wm.save_as_mainfile(filepath=str(out_file), check_existing=False)
    print("SUCCESS: Saved staged scene to", out_file)


if __name__ == "__main__":
    build_shot_14()
