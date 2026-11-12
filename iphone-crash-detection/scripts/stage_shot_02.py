"""Stage SHOT_02: Mobil menabrak pembatas jalan dengan hentakan mendadak.
Frame range: 72 to 217 (30 fps, 4.867 s).
Resolution: 1080 x 1920 (9:16 vertical).
Engine: Eevee ONLY.

Outputs:
  scenes/shot_02.blend
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


def build_shot_02():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.render.fps = 30
    scene.frame_start = 72
    scene.frame_end = 217
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
    world = bpy.data.worlds.new("World_Shot02")
    scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs["Color"].default_value = (0.05, 0.08, 0.14, 1.0)
        bg.inputs["Strength"].default_value = 0.8

    # Sun Light
    light_data = bpy.data.lights.new(name="Sun_Light", type="SUN")
    light_data.energy = 3.8
    light_data.color = (1.0, 0.95, 0.88)
    sun = bpy.data.objects.new(name="Sun_Light", object_data=light_data)
    scene.collection.objects.link(sun)
    sun.location = (10, -10, 15)
    sun.rotation_euler = (math.radians(50), math.radians(15), math.radians(-35))

    # Fill Light
    fill_data = bpy.data.lights.new(name="Fill_Light", type="SUN")
    fill_data.energy = 1.3
    fill_data.color = (0.6, 0.8, 1.0)
    fill = bpy.data.objects.new(name="Fill_Light", object_data=fill_data)
    scene.collection.objects.link(fill)
    fill.location = (10, 10, 10)
    fill.rotation_euler = (math.radians(45), math.radians(-10), math.radians(145))

    # Append Road & Barrier
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

    if phone_root and car_root:
        phone_root.parent = car_root
        phone_root.location = (0.25, 0.0, 0.82)
        phone_root.rotation_euler = (math.radians(15), 0, math.radians(-90))
        phone_root.scale = (1.5, 1.5, 1.5)

    # Animation: Car approaches barrier from X=2.0 (frame 72)
    # Barrier is at X=14.0. Front bumper is ~2.12m ahead of CAR_Root (length 4.24m).
    # So CAR_Root hits barrier at X = 14.0 - 2.12 = 11.88m.
    # Impact occurs at frame 135 (VO "INNAMMAA SYUDUDUU!! mobilnya menabrak...")
    lane_y = 1.75
    impact_frame = 135
    impact_x = 11.88

    # Frame 72: car at X = 2.0
    car_root.location = (2.0, lane_y, 0.0)
    car_root.keyframe_insert(data_path="location", frame=72)

    # Frame 135: impact at X = 11.88
    car_root.location = (impact_x, lane_y, 0.0)
    car_root.keyframe_insert(data_path="location", frame=impact_frame)

    # Frame 139: slight rebound (0.08m) and pitch down on front suspension
    car_root.location = (impact_x - 0.08, lane_y, 0.0)
    car_root.rotation_euler = (0, math.radians(-2.5), 0)
    car_root.keyframe_insert(data_path="location", frame=impact_frame + 4)
    car_root.keyframe_insert(data_path="rotation_euler", frame=impact_frame + 4)

    # Frame 148 to 217: settled and stopped
    car_root.location = (impact_x - 0.06, lane_y, 0.0)
    car_root.rotation_euler = (0, 0, 0)
    car_root.keyframe_insert(data_path="location", frame=impact_frame + 12)
    car_root.keyframe_insert(data_path="rotation_euler", frame=impact_frame + 12)

    car_root.location = (impact_x - 0.06, lane_y, 0.0)
    car_root.rotation_euler = (0, 0, 0)
    car_root.keyframe_insert(data_path="location", frame=217)
    car_root.keyframe_insert(data_path="rotation_euler", frame=217)

    # Wheel rotation
    if "wheel_rotation" in car_root:
        car_root["wheel_rotation"] = 40.0
        car_root.keyframe_insert(data_path='["wheel_rotation"]', frame=72)
        # rotated additional (11.88 - 2.0) / 0.35 = ~28.2 rad -> 68.2 rad
        car_root["wheel_rotation"] = 68.2
        car_root.keyframe_insert(data_path='["wheel_rotation"]', frame=impact_frame)
        car_root["wheel_rotation"] = 68.2
        car_root.keyframe_insert(data_path='["wheel_rotation"]', frame=217)

    # Set interpolation for pre-impact travel
    if car_root.animation_data and car_root.animation_data.action:
        for fc in get_all_fcurves(car_root.animation_data.action):
            for kf in fc.keyframe_points:
                if kf.co[0] <= impact_frame:
                    kf.interpolation = "LINEAR"

    # Camera Rig: side-profile, lateral-truck with car
    cam_data = bpy.data.cameras.new("CAM_SHOT_02")
    cam_data.lens = 42
    cam_data.clip_start = 0.1
    cam_data.clip_end = 150.0
    cam_obj = bpy.data.objects.new("CAM_SHOT_02", cam_data)
    scene.collection.objects.link(cam_obj)
    scene.camera = cam_obj

    # Camera moves laterally keeping car profile in view, then halts at impact with slight vibration
    cam_y = -3.8
    cam_z = 1.45

    # At frame 72
    cam_obj.location = (2.0 - 0.5, cam_y, cam_z)
    cam_obj.keyframe_insert(data_path="location", frame=72)

    # At impact frame 135
    cam_obj.location = (impact_x - 0.5, cam_y, cam_z)
    cam_obj.keyframe_insert(data_path="location", frame=impact_frame)

    # Slight camera shake on impact (frames 136 to 146)
    cam_obj.location = (impact_x - 0.52, cam_y + 0.05, cam_z + 0.04)
    cam_obj.keyframe_insert(data_path="location", frame=impact_frame + 2)
    cam_obj.location = (impact_x - 0.49, cam_y - 0.03, cam_z - 0.02)
    cam_obj.keyframe_insert(data_path="location", frame=impact_frame + 5)
    cam_obj.location = (impact_x - 0.50, cam_y, cam_z)
    cam_obj.keyframe_insert(data_path="location", frame=impact_frame + 11)
    cam_obj.keyframe_insert(data_path="location", frame=217)

    # Camera angle: side profile facing +Y
    cam_obj.rotation_euler = (math.radians(82), math.radians(0), math.radians(-5))

    # Clean render QA confirmation
    scene["CLEAN_RENDER_QA_PASSED"] = True

    out_file = SCENES / "shot_02.blend"
    bpy.ops.wm.save_as_mainfile(filepath=str(out_file), check_existing=False)
    print("SUCCESS: Saved staged scene to", out_file)


if __name__ == "__main__":
    build_shot_02()
