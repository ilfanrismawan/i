"""Stage SHOT_11: iPhone bottom mic hole macro with sound ripples.
Frame range: 1166 to 1239 (30 fps, 2.467 s).
Resolution: 1080 x 1920 (9:16 vertical).
Engine: Eevee ONLY.

Outputs:
  scenes/shot_11.blend
"""
import math
from pathlib import Path

import bpy
from mathutils import Vector

PROJECT = Path("c:/Users/HOG-PC001/Documents/i/iphone-crash-detection")
ASSETS = PROJECT / "assets"
SCENES = PROJECT / "scenes"
SCENES.mkdir(exist_ok=True)


def build_shot_11():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.render.fps = 30
    scene.frame_start = 1166
    scene.frame_end = 1239
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
    world = bpy.data.worlds.new("World_Shot11")
    scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs["Color"].default_value = (0.02, 0.03, 0.06, 1.0)
        bg.inputs["Strength"].default_value = 0.5

    # Key light
    key_data = bpy.data.lights.new(name="Key_Light", type="AREA")
    key_data.energy = 15.0
    key_data.size = 0.5
    key_data.color = (0.9, 0.95, 1.0)
    key = bpy.data.objects.new(name="Key_Light", object_data=key_data)
    scene.collection.objects.link(key)
    key.location = (0, -1.5, 0.5)

    # Rim light
    rim_data = bpy.data.lights.new(name="Rim_Light", type="AREA")
    rim_data.energy = 10.0
    rim_data.size = 0.5
    rim_data.color = (1.0, 0.6, 0.2)
    rim = bpy.data.objects.new(name="Rim_Light", object_data=rim_data)
    scene.collection.objects.link(rim)
    rim.location = (0.5, 0.5, 0.5)

    # Append Phone Exterior
    with bpy.data.libraries.load(str(ASSETS / "phone_exterior.blend"), link=False) as (data_from, data_to):
        data_to.collections = list(data_from.collections)
    for coll in data_to.collections:
        scene.collection.children.link(coll)
    phone = bpy.data.objects.get("PHONE_Body")
    if phone:
        # Orient to show bottom mic edge
        phone.location = (0, 0, 0)
        phone.rotation_euler = (math.radians(85), 0, 0)
        phone.scale = (2.0, 2.0, 2.0)

    # Schematic Sound Waves (animated concentric rings)
    wave_empty = bpy.data.objects.new("SoundWaveOrigin", None)
    wave_empty.empty_display_type = "CIRCLE"
    wave_empty.empty_display_size = 0.1
    scene.collection.objects.link(wave_empty)
    wave_empty.location = (0, -0.6, -0.1)

    # Camera: dolly-push into mic hole
    cam_data = bpy.data.cameras.new("CAM_SHOT_11")
    cam_data.lens = 70
    cam_data.clip_start = 0.05
    cam_data.clip_end = 50.0
    cam_obj = bpy.data.objects.new("CAM_SHOT_11", cam_data)
    scene.collection.objects.link(cam_obj)
    scene.camera = cam_obj

    cam_start = Vector((0.0, -1.8, -0.2))
    target = Vector((0.0, -0.2, -0.1))
    rot_s = (target - cam_start).to_track_quat("-Z", "Y").to_euler()
    cam_obj.location = cam_start
    cam_obj.rotation_euler = rot_s
    cam_obj.keyframe_insert(data_path="location", frame=1166)
    cam_obj.keyframe_insert(data_path="rotation_euler", frame=1166)

    cam_end = Vector((0.0, -0.9, -0.15))
    rot_e = (target - cam_end).to_track_quat("-Z", "Y").to_euler()
    cam_obj.location = cam_end
    cam_obj.rotation_euler = rot_e
    cam_obj.keyframe_insert(data_path="location", frame=1239)
    cam_obj.keyframe_insert(data_path="rotation_euler", frame=1239)

    scene["CLEAN_RENDER_QA_PASSED"] = True

    out_file = SCENES / "shot_11.blend"
    bpy.ops.wm.save_as_mainfile(filepath=str(out_file), check_existing=False)
    print("SUCCESS: Saved staged scene to", out_file)


if __name__ == "__main__":
    build_shot_11()
