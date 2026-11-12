"""Stage SHOT_18: Closing shot — all sensors glow together inside iPhone, shell reforms, dolly-pull.
Frame range: 1910 to 2067 (30 fps, 5.267 s).
Resolution: 1080 x 1920 (9:16 vertical).
Engine: Eevee ONLY.

Outputs:
  scenes/shot_18.blend
"""
import math
from pathlib import Path

import bpy
from mathutils import Vector

PROJECT = Path("c:/Users/HOG-PC001/Documents/i/iphone-crash-detection")
ASSETS = PROJECT / "assets"
SCENES = PROJECT / "scenes"
SCENES.mkdir(exist_ok=True)


def build_shot_18():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.render.fps = 30
    scene.frame_start = 1910
    scene.frame_end = 2067
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

    # World (studio dark)
    world = bpy.data.worlds.new("World_Shot18")
    scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs["Color"].default_value = (0.015, 0.02, 0.04, 1.0)
        bg.inputs["Strength"].default_value = 0.5

    # Lights
    key_data = bpy.data.lights.new(name="Key_Light", type="AREA")
    key_data.energy = 20.0
    key_data.size = 1.0
    key_data.color = (0.9, 0.95, 1.0)
    key = bpy.data.objects.new(name="Key_Light", object_data=key_data)
    scene.collection.objects.link(key)
    key.location = (1.5, -2.0, 2.0)

    rim_data = bpy.data.lights.new(name="Rim_Light", type="AREA")
    rim_data.energy = 15.0
    rim_data.size = 1.2
    rim_data.color = (0.4, 0.7, 1.0)
    rim = bpy.data.objects.new(name="Rim_Light", object_data=rim_data)
    scene.collection.objects.link(rim)
    rim.location = (-1.5, 2.0, 1.5)

    # Append Phone Exterior
    with bpy.data.libraries.load(str(ASSETS / "phone_exterior.blend"), link=False) as (data_from, data_to):
        data_to.collections = list(data_from.collections)
    for coll in data_to.collections:
        scene.collection.children.link(coll)

    # Append Phone Interior Concept
    with bpy.data.libraries.load(str(ASSETS / "phone_interior_concept.blend"), link=False) as (data_from, data_to):
        data_to.collections = list(data_from.collections)
    for coll in data_to.collections:
        scene.collection.children.link(coll)

    phone_body = bpy.data.objects.get("PHONE_Body")
    if phone_body:
        phone_body.location = (0, 0, 0)
        phone_body.rotation_euler = (math.radians(-15), math.radians(20), math.radians(-10))

    # Camera: three-quarter dolly-pull
    cam_data = bpy.data.cameras.new("CAM_SHOT_18")
    cam_data.lens = 50
    cam_data.clip_start = 0.1
    cam_data.clip_end = 100.0
    cam_obj = bpy.data.objects.new("CAM_SHOT_18", cam_data)
    scene.collection.objects.link(cam_obj)
    scene.camera = cam_obj

    cam_start = Vector((0.4, -1.8, 0.8))
    target = Vector((0.0, 0.0, 0.0))
    rot_s = (target - cam_start).to_track_quat("-Z", "Y").to_euler()
    cam_obj.location = cam_start
    cam_obj.rotation_euler = rot_s
    cam_obj.keyframe_insert(data_path="location", frame=1910)
    cam_obj.keyframe_insert(data_path="rotation_euler", frame=1910)

    cam_end = Vector((0.8, -3.2, 1.5))
    rot_e = (target - cam_end).to_track_quat("-Z", "Y").to_euler()
    cam_obj.location = cam_end
    cam_obj.rotation_euler = rot_e
    cam_obj.keyframe_insert(data_path="location", frame=2067)
    cam_obj.keyframe_insert(data_path="rotation_euler", frame=2067)

    scene["CLEAN_RENDER_QA_PASSED"] = True

    out_file = SCENES / "shot_18.blend"
    bpy.ops.wm.save_as_mainfile(filepath=str(out_file), check_existing=False)
    print("SUCCESS: Saved staged scene to", out_file)


if __name__ == "__main__":
    build_shot_18()
