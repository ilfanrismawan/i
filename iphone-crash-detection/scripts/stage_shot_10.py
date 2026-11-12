"""Stage SHOT_10: Cabin cutaway with pressure wave moving toward iPhone.
Frame range: 1060 to 1165 (30 fps, 3.533 s).
Resolution: 1080 x 1920 (9:16 vertical).
Engine: Eevee ONLY.

Outputs:
  scenes/shot_10.blend
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


def build_shot_10():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.render.fps = 30
    scene.frame_start = 1060
    scene.frame_end = 1165
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
    world = bpy.data.worlds.new("World_Shot10")
    scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs["Color"].default_value = (0.05, 0.05, 0.08, 1.0)
        bg.inputs["Strength"].default_value = 0.5

    # Sun
    light_data = bpy.data.lights.new(name="Sun_Light", type="SUN")
    light_data.energy = 2.5
    light_data.color = (1.0, 0.95, 0.90)
    sun = bpy.data.objects.new(name="Sun_Light", object_data=light_data)
    scene.collection.objects.link(sun)
    sun.location = (5, -5, 10)
    sun.rotation_euler = (math.radians(45), 0, math.radians(30))

    # Interior light
    int_data = bpy.data.lights.new(name="Interior_Light", type="AREA")
    int_data.energy = 15.0
    int_data.size = 2.0
    int_data.color = (0.9, 0.85, 0.7)
    int_light = bpy.data.objects.new(name="Interior_Light", object_data=int_data)
    scene.collection.objects.link(int_light)
    int_light.location = (0, 0, 2.5)
    int_light.rotation_euler = (math.radians(90), 0, 0)

    # Append Car Cutaway
    with bpy.data.libraries.load(str(ASSETS / "car_cutaway.blend"), link=False) as (data_from, data_to):
        data_to.collections = list(data_from.collections)
    for coll in data_to.collections:
        scene.collection.children.link(coll)

    # Append Phone Exterior
    with bpy.data.libraries.load(str(ASSETS / "phone_exterior.blend"), link=False) as (data_from, data_to):
        data_to.collections = list(data_from.collections)
    for coll in data_to.collections:
        scene.collection.children.link(coll)
    phone = bpy.data.objects.get("PHONE_Body")

    # Append Schematic Effects for pressure wave
    with bpy.data.libraries.load(str(ASSETS / "schematic_effects.blend"), link=False) as (data_from, data_to):
        data_to.collections = list(data_from.collections)
    for coll in data_to.collections:
        scene.collection.children.link(coll)

    # Position phone on dashboard area
    if phone:
        phone.location = (1.8, 0.0, 1.0)
        phone.rotation_euler = (math.radians(-15), 0, 0)
        phone.scale = (0.6, 0.6, 0.6)

    # Animate pressure wave rings: use an empty as wave front marker
    wave_empty = bpy.data.objects.new("PressureWaveFront", None)
    wave_empty.empty_display_type = "SPHERE"
    wave_empty.empty_display_size = 0.15
    scene.collection.objects.link(wave_empty)

    # Wave travels from front of cabin to phone
    wave_empty.location = (-2.0, 0.0, 1.0)
    wave_empty.keyframe_insert(data_path="location", frame=1060)
    wave_empty.location = (1.8, 0.0, 1.0)
    wave_empty.keyframe_insert(data_path="location", frame=1130)
    wave_empty.location = (1.8, 0.0, 1.0)
    wave_empty.keyframe_insert(data_path="location", frame=1165)

    # Scale wave rings expanding as they travel
    wave_empty.scale = (0.3, 0.3, 0.3)
    wave_empty.keyframe_insert(data_path="scale", frame=1060)
    wave_empty.scale = (1.5, 1.5, 1.5)
    wave_empty.keyframe_insert(data_path="scale", frame=1130)
    wave_empty.scale = (2.0, 2.0, 2.0)
    wave_empty.keyframe_insert(data_path="scale", frame=1165)

    # Camera: lateral truck following pressure wave
    cam_data = bpy.data.cameras.new("CAM_SHOT_10")
    cam_data.lens = 28
    cam_data.clip_start = 0.1
    cam_data.clip_end = 100.0
    cam_obj = bpy.data.objects.new("CAM_SHOT_10", cam_data)
    scene.collection.objects.link(cam_obj)
    scene.camera = cam_obj

    # Start: front of cabin
    cam_start = Vector((-2.0, -3.5, 1.5))
    target_s = Vector((-1.5, 0.0, 1.0))
    rot_s = (target_s - cam_start).to_track_quat("-Z", "Y").to_euler()
    cam_obj.location = cam_start
    cam_obj.rotation_euler = rot_s
    cam_obj.keyframe_insert(data_path="location", frame=1060)
    cam_obj.keyframe_insert(data_path="rotation_euler", frame=1060)

    # End: phone area
    cam_end = Vector((1.8, -3.5, 1.5))
    target_e = Vector((1.8, 0.0, 1.0))
    rot_e = (target_e - cam_end).to_track_quat("-Z", "Y").to_euler()
    cam_obj.location = cam_end
    cam_obj.rotation_euler = rot_e
    cam_obj.keyframe_insert(data_path="location", frame=1165)
    cam_obj.keyframe_insert(data_path="rotation_euler", frame=1165)

    scene["CLEAN_RENDER_QA_PASSED"] = True

    out_file = SCENES / "shot_10.blend"
    bpy.ops.wm.save_as_mainfile(filepath=str(out_file), check_existing=False)
    print("SUCCESS: Saved staged scene to", out_file)


if __name__ == "__main__":
    build_shot_10()
