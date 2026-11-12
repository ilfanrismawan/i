"""Stage SHOT_08: Gyroscope — Top-down view, car spinning on turntable, sensor tilts.
Frame range: 792 to 938 (30 fps, 4.900 s).
Resolution: 1080 x 1920 (9:16 vertical).
Engine: Eevee ONLY.

Outputs:
  scenes/shot_08.blend
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


def build_shot_08():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.render.fps = 30
    scene.frame_start = 792
    scene.frame_end = 938
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
    world = bpy.data.worlds.new("World_Shot08")
    scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs["Color"].default_value = (0.03, 0.05, 0.09, 1.0)
        bg.inputs["Strength"].default_value = 0.6

    # Sun
    light_data = bpy.data.lights.new(name="Sun_Light", type="SUN")
    light_data.energy = 3.5
    light_data.color = (1.0, 0.95, 0.88)
    sun = bpy.data.objects.new(name="Sun_Light", object_data=light_data)
    scene.collection.objects.link(sun)
    sun.location = (0, 0, 20)
    sun.rotation_euler = (math.radians(10), 0, 0)

    # Rim light from below for the sensor
    rim_data = bpy.data.lights.new(name="Rim_Light", type="AREA")
    rim_data.energy = 12.0
    rim_data.size = 1.5
    rim_data.color = (0.4, 0.7, 1.0)
    rim_obj = bpy.data.objects.new(name="Rim_Light", object_data=rim_data)
    scene.collection.objects.link(rim_obj)
    rim_obj.location = (0, 0, -2)
    rim_obj.rotation_euler = (math.radians(180), 0, 0)

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

    # Append Gyro Sensor
    with bpy.data.libraries.load(str(ASSETS / "sensor_gyro_concept.blend"), link=False) as (data_from, data_to):
        data_to.collections = list(data_from.collections)
    for coll in data_to.collections:
        scene.collection.children.link(coll)
    gyro_root = bpy.data.objects.get("GYRO_Root")

    # Position car at center of road for spin
    if car_root:
        car_root.location = (11.0, 1.75, 0.0)
        # Spin animation: car rotates 360° around Z
        car_root.rotation_euler = (0, 0, 0)
        car_root.keyframe_insert(data_path="rotation_euler", frame=792)
        car_root.rotation_euler = (0, 0, math.radians(360))
        car_root.keyframe_insert(data_path="rotation_euler", frame=938)
        # Make rotation linear
        if car_root.animation_data and car_root.animation_data.action:
            for fc in get_all_fcurves(car_root.animation_data.action):
                if "rotation_euler" in fc.data_path and fc.array_index == 2:
                    for kp in fc.keyframe_points:
                        kp.interpolation = "LINEAR"

    # Position gyro sensor in lower portion of frame
    if gyro_root:
        gyro_root.location = (11.0, 0.0, -1.0)
        gyro_root.scale = (0.35, 0.35, 0.35)
        # Tilt animation synced with car spin
        gyro_root.rotation_euler = (0, 0, 0)
        gyro_root.keyframe_insert(data_path="rotation_euler", frame=792)
        gyro_root.rotation_euler = (math.radians(15), math.radians(-10), math.radians(45))
        gyro_root.keyframe_insert(data_path="rotation_euler", frame=865)
        gyro_root.rotation_euler = (math.radians(-10), math.radians(15), math.radians(180))
        gyro_root.keyframe_insert(data_path="rotation_euler", frame=900)
        gyro_root.rotation_euler = (math.radians(5), math.radians(-5), math.radians(360))
        gyro_root.keyframe_insert(data_path="rotation_euler", frame=938)

    # Camera: crane from top-down to medium angle
    cam_data = bpy.data.cameras.new("CAM_SHOT_08")
    cam_data.lens = 35
    cam_data.clip_start = 0.1
    cam_data.clip_end = 100.0
    cam_obj = bpy.data.objects.new("CAM_SHOT_08", cam_data)
    scene.collection.objects.link(cam_obj)
    scene.camera = cam_obj

    # Start: top-down
    cam_obj.location = (11.0, 1.75, 12.0)
    cam_obj.rotation_euler = (0, 0, 0)  # looking straight down
    cam_obj.keyframe_insert(data_path="location", frame=792)
    cam_obj.keyframe_insert(data_path="rotation_euler", frame=792)

    # End: lower angle showing both car and sensor
    cam_end = Vector((11.0, -2.5, 5.0))
    target = Vector((11.0, 0.5, 0.0))
    rot_e = (target - cam_end).to_track_quat("-Z", "Y").to_euler()
    cam_obj.location = cam_end
    cam_obj.rotation_euler = rot_e
    cam_obj.keyframe_insert(data_path="location", frame=938)
    cam_obj.keyframe_insert(data_path="rotation_euler", frame=938)

    scene["CLEAN_RENDER_QA_PASSED"] = True

    out_file = SCENES / "shot_08.blend"
    bpy.ops.wm.save_as_mainfile(filepath=str(out_file), check_existing=False)
    print("SUCCESS: Saved staged scene to", out_file)


if __name__ == "__main__":
    build_shot_08()
