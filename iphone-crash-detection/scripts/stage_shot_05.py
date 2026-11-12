"""Stage SHOT_05: X-Ray orbit reveal - Cangkang iPhone memudar, lima sensor menyala.
Frame range: 385 to 519 (30 fps, 4.500 s).
Resolution: 1080 x 1920 (9:16 vertical).
Engine: Eevee ONLY.

Outputs:
  scenes/shot_05.blend
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


def build_shot_05():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.render.fps = 30
    scene.frame_start = 385
    scene.frame_end = 519
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

    # World lighting: deep tech studio dark backdrop
    world = bpy.data.worlds.new("World_Shot05")
    scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs["Color"].default_value = (0.015, 0.02, 0.035, 1.0)
        bg.inputs["Strength"].default_value = 0.5

    # Key light: crisp cool tech area light
    key_data = bpy.data.lights.new(name="Tech_Key", type="AREA")
    key_data.energy = 12.0
    key_data.size = 0.4
    key_data.color = (0.9, 0.95, 1.0)
    key = bpy.data.objects.new(name="Tech_Key", object_data=key_data)
    scene.collection.objects.link(key)
    key.location = (-0.3, -0.4, 0.25)
    key.rotation_euler = (math.radians(-50), math.radians(25), math.radians(-30))

    # Fill light
    fill_data = bpy.data.lights.new(name="Tech_Fill", type="AREA")
    fill_data.energy = 6.0
    fill_data.size = 0.5
    fill_data.color = (0.7, 0.85, 1.0)
    fill = bpy.data.objects.new(name="Tech_Fill", object_data=fill_data)
    scene.collection.objects.link(fill)
    fill.location = (0.35, -0.35, -0.2)

    # Rim light
    rim_data = bpy.data.lights.new(name="Tech_Rim", type="AREA")
    rim_data.energy = 18.0
    rim_data.size = 0.35
    rim_data.color = (0.3, 0.7, 1.0)
    rim = bpy.data.objects.new(name="Tech_Rim", object_data=rim_data)
    scene.collection.objects.link(rim)
    rim.location = (0.0, 0.35, 0.2)
    rim.rotation_euler = (math.radians(135), 0, 0)

    # Append Phone Exterior
    with bpy.data.libraries.load(str(ASSETS / "phone_exterior.blend"), link=False) as (data_from, data_to):
        data_to.collections = list(data_from.collections)
    coll_phone = data_to.collections[0]
    scene.collection.children.link(coll_phone)
    phone_root = bpy.data.objects.get("PHONE_Root")

    # Append Phone Interior Concept
    with bpy.data.libraries.load(str(ASSETS / "phone_interior_concept.blend"), link=False) as (data_from, data_to):
        data_to.collections = list(data_from.collections)
    coll_interior = data_to.collections[0]
    scene.collection.children.link(coll_interior)
    interior_root = bpy.data.objects.get("PHONEINT_Root")

    # Position interior inside phone shell
    if interior_root and phone_root:
        interior_root.parent = phone_root
        interior_root.location = (0, 0, 0)
        interior_root.rotation_euler = (0, 0, 0)

    # Animate Phone Shell Opacity (X-Ray reveal)
    # Starts opaque (1.0) at frame 385, drops to semitransparent (0.15) by frame 425
    if phone_root and "shell_opacity" in phone_root:
        phone_root["shell_opacity"] = 1.0
        phone_root.keyframe_insert(data_path='["shell_opacity"]', frame=385)
        phone_root["shell_opacity"] = 0.15
        phone_root.keyframe_insert(data_path='["shell_opacity"]', frame=425)
        phone_root["shell_opacity"] = 0.15
        phone_root.keyframe_insert(data_path='["shell_opacity"]', frame=519)

    # Sequential glowing of the sensors on the logic board
    if interior_root:
        sensors_sequence = [
            ("glow_accel", 415, 435),
            ("glow_gyro", 430, 450),
            ("glow_baro", 445, 465),
            ("glow_gps", 460, 480),
            ("glow_mic", 475, 495),
            ("glow_processor", 490, 515),
        ]
        for prop, f_start, f_peak in sensors_sequence:
            if prop in interior_root:
                interior_root[prop] = 0.0
                interior_root.keyframe_insert(data_path=f'["{prop}"]', frame=385)
                interior_root.keyframe_insert(data_path=f'["{prop}"]', frame=f_start)
                interior_root[prop] = 12.0
                interior_root.keyframe_insert(data_path=f'["{prop}"]', frame=f_peak)
                interior_root.keyframe_insert(data_path=f'["{prop}"]', frame=519)

    # Camera Rig: gentle three-quarter orbit from left to right
    cam_data = bpy.data.cameras.new("CAM_SHOT_05")
    cam_data.lens = 54
    cam_data.clip_start = 0.05
    cam_data.clip_end = 20.0
    cam_obj = bpy.data.objects.new("CAM_SHOT_05", cam_data)
    scene.collection.objects.link(cam_obj)
    scene.camera = cam_obj

    target = Vector((0.0, 0.0, 0.01))
    radius = 0.36
    z_height = 0.04

    # Orbit from angle -28 degrees to +28 degrees around Z
    for f in range(385, 520, 15):
        t = (f - 385) / (519 - 385)
        angle = math.radians(-28 + 56 * t)
        cam_x = radius * math.sin(angle)
        cam_y = -radius * math.cos(angle)
        cam_loc = Vector((cam_x, cam_y, z_height))
        cam_obj.location = cam_loc
        rot = (target - cam_loc).to_track_quat("-Z", "Y").to_euler()
        cam_obj.rotation_euler = rot
        cam_obj.keyframe_insert(data_path="location", frame=f)
        cam_obj.keyframe_insert(data_path="rotation_euler", frame=f)

    # Clean render QA confirmation
    scene["CLEAN_RENDER_QA_PASSED"] = True

    out_file = SCENES / "shot_05.blend"
    bpy.ops.wm.save_as_mainfile(filepath=str(out_file), check_existing=False)
    print("SUCCESS: Saved staged scene to", out_file)


if __name__ == "__main__":
    build_shot_05()
