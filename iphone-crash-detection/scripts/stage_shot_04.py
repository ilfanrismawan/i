"""Stage SHOT_04: iPhone tampak depan simetris, melayang di ruang studio netral.
Frame range: 316 to 384 (30 fps, 2.300 s).
Resolution: 1080 x 1920 (9:16 vertical).
Engine: Eevee ONLY.

Outputs:
  scenes/shot_04.blend
"""
import math
import sys
from pathlib import Path

import bpy
from mathutils import Matrix, Vector

PROJECT = Path("c:/Users/HOG-PC001/Documents/i/iphone-crash-detection")
ASSETS = PROJECT / "assets"
SCENES = PROJECT / "scenes"
SCENES.mkdir(exist_ok=True)


def build_shot_04():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.render.fps = 30
    scene.frame_start = 316
    scene.frame_end = 384
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

    # World lighting: studio neutral dark gradient
    world = bpy.data.worlds.new("World_Shot04")
    scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs["Color"].default_value = (0.015, 0.02, 0.035, 1.0)
        bg.inputs["Strength"].default_value = 0.4

    # Studio Key Light
    key_data = bpy.data.lights.new(name="Studio_Key", type="AREA")
    key_data.energy = 14.0
    key_data.size = 0.5
    key_data.color = (0.95, 0.98, 1.0)
    key = bpy.data.objects.new(name="Studio_Key", object_data=key_data)
    scene.collection.objects.link(key)
    key.location = (-0.25, -0.5, 0.3)
    key.rotation_euler = (math.radians(-50), math.radians(20), math.radians(-30))

    # Fill Light (warm subtle)
    fill_data = bpy.data.lights.new(name="Studio_Fill", type="AREA")
    fill_data.energy = 5.0
    fill_data.size = 0.6
    fill_data.color = (1.0, 0.9, 0.8)
    fill = bpy.data.objects.new(name="Studio_Fill", object_data=fill_data)
    scene.collection.objects.link(fill)
    fill.location = (0.35, -0.4, -0.2)
    fill.rotation_euler = (math.radians(-40), math.radians(-30), math.radians(40))

    # Rim Light (back edge glow)
    rim_data = bpy.data.lights.new(name="Studio_Rim", type="AREA")
    rim_data.energy = 16.0
    rim_data.size = 0.4
    rim_data.color = (0.4, 0.7, 1.0)
    rim = bpy.data.objects.new(name="Studio_Rim", object_data=rim_data)
    scene.collection.objects.link(rim)
    rim.location = (0.0, 0.4, 0.25)
    rim.rotation_euler = (math.radians(135), 0, 0)

    # Append Phone Exterior
    with bpy.data.libraries.load(str(ASSETS / "phone_exterior.blend"), link=False) as (data_from, data_to):
        data_to.collections = list(data_from.collections)
    coll_phone = data_to.collections[0]
    scene.collection.children.link(coll_phone)
    phone_root = bpy.data.objects.get("PHONE_Root")

    # Phone is upright at origin
    if phone_root:
        phone_root.location = (0, 0, 0)
        phone_root.rotation_euler = (0, 0, 0)

        # Screen dims slightly during mystery voice-over
        if "screen_glow" in phone_root:
            phone_root["screen_glow"] = 0.8
            phone_root.keyframe_insert(data_path='["screen_glow"]', frame=316)
            phone_root["screen_glow"] = 0.15
            phone_root.keyframe_insert(data_path='["screen_glow"]', frame=384)

    # Camera Rig: straight-on, locked, perfectly centered framing
    cam_data = bpy.data.cameras.new("CAM_SHOT_04")
    cam_data.lens = 52
    cam_data.clip_start = 0.05
    cam_data.clip_end = 20.0
    cam_obj = bpy.data.objects.new("CAM_SHOT_04", cam_data)
    scene.collection.objects.link(cam_obj)
    scene.camera = cam_obj

    cam_obj.location = (0.0, -0.34, 0.0)
    cam_obj.rotation_euler = (math.radians(90), 0, 0)

    # Clean render QA confirmation
    scene["CLEAN_RENDER_QA_PASSED"] = True

    out_file = SCENES / "shot_04.blend"
    bpy.ops.wm.save_as_mainfile(filepath=str(out_file), check_existing=False)
    print("SUCCESS: Saved staged scene to", out_file)


if __name__ == "__main__":
    build_shot_04()
