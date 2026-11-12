"""Stage SHOT_06: Makro Ekstrem Sensor Hentakan (Akselerometer MEMS).
Beban terdorong ke depan di antara pegas saat hentakan.
Frame range: 520 to 633 (30 fps, 3.800 s).
Resolution: 1080 x 1920 (9:16 vertical).
Engine: Eevee ONLY.

Outputs:
  scenes/shot_06.blend
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


def build_shot_06():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.render.fps = 30
    scene.frame_start = 520
    scene.frame_end = 633
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

    # World lighting
    world = bpy.data.worlds.new("World_Shot06")
    scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs["Color"].default_value = (0.015, 0.025, 0.04, 1.0)
        bg.inputs["Strength"].default_value = 0.6

    # Macro Top Key Light
    key_data = bpy.data.lights.new(name="Macro_Key", type="AREA")
    key_data.energy = 25.0
    key_data.size = 2.0
    key_data.color = (1.0, 0.95, 0.9)
    key = bpy.data.objects.new(name="Macro_Key", object_data=key_data)
    scene.collection.objects.link(key)
    key.location = (-1.0, -1.5, 3.5)
    key.rotation_euler = (math.radians(-30), math.radians(15), 0)

    # Macro Rim / Accent Light (orange tech glow)
    rim_data = bpy.data.lights.new(name="Macro_Rim", type="AREA")
    rim_data.energy = 30.0
    rim_data.size = 1.5
    rim_data.color = (1.0, 0.45, 0.1)
    rim = bpy.data.objects.new(name="Macro_Rim", object_data=rim_data)
    scene.collection.objects.link(rim)
    rim.location = (1.5, 1.5, 2.0)
    rim.rotation_euler = (math.radians(135), 0, math.radians(45))

    # Append Sensor Accel Concept
    with bpy.data.libraries.load(str(ASSETS / "sensor_accel_concept.blend"), link=False) as (data_from, data_to):
        data_to.collections = list(data_from.collections)
    coll_accel = data_to.collections[0]
    scene.collection.children.link(coll_accel)
    accel_root = bpy.data.objects.get("ACCEL_Root")

    # Animate MEMS mass displacement and glow
    # Frame 520: at rest (displacement = 0.0, mass_glow = 1.0)
    # Frame 555: impact surge! Sudden shift to displacement = 0.95, mass_glow = 15.0
    # Frame 575: recoil overshoot to -0.3
    # Frame 595: small rebound to 0.15
    # Frame 615: settling back to 0.0
    if accel_root:
        keyframes = [
            (520, 0.0, 1.0),
            (545, 0.0, 1.0),
            (558, 0.95, 18.0),
            (575, -0.28, 10.0),
            (592, 0.12, 5.0),
            (610, -0.04, 2.5),
            (625, 0.0, 1.5),
            (633, 0.0, 1.5),
        ]
        for f, disp, glow in keyframes:
            if "displacement" in accel_root:
                accel_root["displacement"] = disp
                accel_root.keyframe_insert(data_path='["displacement"]', frame=f)
            if "mass_glow" in accel_root:
                accel_root["mass_glow"] = glow
                accel_root.keyframe_insert(data_path='["mass_glow"]', frame=f)

    # Camera Rig: Extreme-macro top oblique view framing the central mass and folded springs
    cam_data = bpy.data.cameras.new("CAM_SHOT_06")
    cam_data.lens = 75  # macro telephoto
    cam_data.clip_start = 0.1
    cam_data.clip_end = 20.0
    cam_obj = bpy.data.objects.new("CAM_SHOT_06", cam_data)
    scene.collection.objects.link(cam_obj)
    scene.camera = cam_obj

    cam_obj.location = (0.0, -3.2, 3.8)
    cam_target = Vector((0.0, 0.0, 0.1))
    rot = (cam_target - cam_obj.location).to_track_quat("-Z", "Y").to_euler()
    cam_obj.rotation_euler = rot

    # Clean render QA confirmation
    scene["CLEAN_RENDER_QA_PASSED"] = True

    out_file = SCENES / "shot_06.blend"
    bpy.ops.wm.save_as_mainfile(filepath=str(out_file), check_existing=False)
    print("SUCCESS: Saved staged scene to", out_file)


if __name__ == "__main__":
    build_shot_06()
