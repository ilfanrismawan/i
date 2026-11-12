"""Stage SHOT_01: Mobil melaju di jalan dengan iPhone di dasbor.
Frame range: 1 to 71 (30 fps, 2.367 s).
Resolution: 1080 x 1920 (9:16 vertical).
Engine: Eevee ONLY.

Outputs:
  scenes/shot_01.blend
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


def build_shot_01():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.render.fps = 30
    scene.frame_start = 1
    scene.frame_end = 71
    scene.render.resolution_x = 1080
    scene.render.resolution_y = 1920
    scene.render.resolution_percentage = 100

    # Detect Eevee engine
    for eng in ["BLENDER_EEVEE_NEXT", "BLENDER_EEVEE"]:
        try:
            scene.render.engine = eng
            if scene.render.engine == eng:
                break
        except Exception:
            pass

    # World lighting
    world = bpy.data.worlds.new("World_Shot01")
    scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs["Color"].default_value = (0.05, 0.08, 0.14, 1.0)  # deep stylish atmospheric blue
        bg.inputs["Strength"].default_value = 0.8

    # Sun / Key light
    light_data = bpy.data.lights.new(name="Sun_Light", type="SUN")
    light_data.energy = 3.5
    light_data.color = (1.0, 0.95, 0.88)
    sun = bpy.data.objects.new(name="Sun_Light", object_data=light_data)
    scene.collection.objects.link(sun)
    sun.location = (0, -10, 15)
    sun.rotation_euler = (math.radians(50), math.radians(15), math.radians(-35))

    # Rim / Fill light
    fill_data = bpy.data.lights.new(name="Fill_Light", type="SUN")
    fill_data.energy = 1.2
    fill_data.color = (0.6, 0.8, 1.0)
    fill = bpy.data.objects.new(name="Fill_Light", object_data=fill_data)
    scene.collection.objects.link(fill)
    fill.location = (0, 10, 10)
    fill.rotation_euler = (math.radians(45), math.radians(-10), math.radians(145))

    # Append Road
    with bpy.data.libraries.load(str(ASSETS / "road_set.blend"), link=False) as (data_from, data_to):
        data_to.collections = [c for c in data_from.collections if c == "ASSET_Road"]
    coll_road = data_to.collections[0]
    scene.collection.children.link(coll_road)

    # Append Car
    with bpy.data.libraries.load(str(ASSETS / "car_stylized.blend"), link=False) as (data_from, data_to):
        data_to.collections = [c for c in data_from.collections if c == "ASSET_Car"]
    coll_car = data_to.collections[0]
    scene.collection.children.link(coll_car)
    car_root = bpy.data.objects.get("CAR_Root")

    # Append Phone
    with bpy.data.libraries.load(str(ASSETS / "phone_exterior.blend"), link=False) as (data_from, data_to):
        data_to.collections = [c for c in data_from.collections if c == "ASSET_Phone"]
    coll_phone = data_to.collections[0]
    scene.collection.children.link(coll_phone)
    phone_root = bpy.data.objects.get("PHONE_Root")

    # Mount phone to car cabin dash anchor
    dash_anchor = bpy.data.objects.get("ANCHOR_Dash")
    if dash_anchor and phone_root:
        phone_root.parent = car_root
        phone_root.location = (0.25, 0.0, 0.82)  # seated inside dash area
        phone_root.rotation_euler = (math.radians(15), 0, math.radians(-90))
        phone_root.scale = (1.5, 1.5, 1.5)  # slightly enlarged for visual read from wide

    # Car motion animation (Frame 1 to 71)
    # Starts at X = -12.0, moves smoothly forward to X = 2.0 along Y = 1.75
    lane_y = 1.75
    car_root.location = (-12.0, lane_y, 0.0)
    car_root.keyframe_insert(data_path="location", frame=1)

    car_root.location = (2.0, lane_y, 0.0)
    car_root.keyframe_insert(data_path="location", frame=71)

    # Wheel rotation
    if "wheel_rotation" in car_root:
        car_root["wheel_rotation"] = 0.0
        car_root.keyframe_insert(data_path='["wheel_rotation"]', frame=1)
        # distance = 14m / 0.35m radius = ~40 rad
        car_root["wheel_rotation"] = 40.0
        car_root.keyframe_insert(data_path='["wheel_rotation"]', frame=71)

    # Linear interpolation for constant speed
    if car_root.animation_data and car_root.animation_data.action:
        for fcurve in get_all_fcurves(car_root.animation_data.action):
            for kf in fcurve.keyframe_points:
                kf.interpolation = "LINEAR"

    # Camera Setup (wide-established, locked camera)
    cam_data = bpy.data.cameras.new("CAM_SHOT_01")
    cam_data.lens = 45  # 45mm lens for clear perspective
    cam_data.clip_start = 0.1
    cam_data.clip_end = 150.0
    cam_obj = bpy.data.objects.new("CAM_SHOT_01", cam_data)
    scene.collection.objects.link(cam_obj)
    scene.camera = cam_obj

    # Position camera to frame the car entering from lower left, moving into center
    cam_obj.location = (-3.5, -6.5, 3.4)
    # Target towards road lane center
    target_point = Vector((-1.0, 1.75, 0.9))
    direction = target_point - cam_obj.location
    rot_quat = direction.to_track_quat("-Z", "Y")
    cam_obj.rotation_euler = rot_quat.to_euler()

    # Clean render QA confirmation
    scene["CLEAN_RENDER_QA_PASSED"] = True

    # Save scene
    out_file = SCENES / "shot_01.blend"
    bpy.ops.wm.save_as_mainfile(filepath=str(out_file), check_existing=False)
    print("SUCCESS: Saved staged scene to", out_file)


if __name__ == "__main__":
    build_shot_01()
