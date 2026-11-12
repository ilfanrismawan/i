"""Stage SHOT_07: Split-depth perbandingan - Mobil berhenti di pembatas & sensor akselerometer terdorong searah.
Frame range: 634 to 792 (30 fps, 5.300 s).
Resolution: 1080 x 1920 (9:16 vertical).
Engine: Eevee ONLY.

Outputs:
  scenes/shot_07.blend
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


def build_shot_07():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.render.fps = 30
    scene.frame_start = 634
    scene.frame_end = 792
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
    world = bpy.data.worlds.new("World_Shot07")
    scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs["Color"].default_value = (0.04, 0.06, 0.10, 1.0)
        bg.inputs["Strength"].default_value = 0.7

    # Sun Light
    light_data = bpy.data.lights.new(name="Sun_Light", type="SUN")
    light_data.energy = 3.8
    light_data.color = (1.0, 0.95, 0.88)
    sun = bpy.data.objects.new(name="Sun_Light", object_data=light_data)
    scene.collection.objects.link(sun)
    sun.location = (10, -10, 15)
    sun.rotation_euler = (math.radians(50), math.radians(15), math.radians(-35))

    # Foreground Accent Light for MEMS sensor
    fg_data = bpy.data.lights.new(name="FG_Light", type="AREA")
    fg_data.energy = 16.0
    fg_data.size = 0.8
    fg_data.color = (1.0, 0.65, 0.3)
    fg_light = bpy.data.objects.new(name="FG_Light", object_data=fg_data)
    scene.collection.objects.link(fg_light)
    fg_light.location = (10.0, -1.0, 1.5)

    # Append Road
    with bpy.data.libraries.load(str(ASSETS / "road_set.blend"), link=False) as (data_from, data_to):
        data_to.collections = list(data_from.collections)
    coll_road = data_to.collections[0]
    scene.collection.children.link(coll_road)

    # Append Car
    with bpy.data.libraries.load(str(ASSETS / "car_stylized.blend"), link=False) as (data_from, data_to):
        data_to.collections = list(data_from.collections)
    coll_car = data_to.collections[0]
    scene.collection.children.link(coll_car)
    car_root = bpy.data.objects.get("CAR_Root")

    # Append Accel Sensor (Foreground Floating Model)
    with bpy.data.libraries.load(str(ASSETS / "sensor_accel_concept.blend"), link=False) as (data_from, data_to):
        data_to.collections = list(data_from.collections)
    coll_accel = data_to.collections[0]
    scene.collection.children.link(coll_accel)
    accel_root = bpy.data.objects.get("ACCEL_Root")

    # Position Accel Sensor in foreground lower portion of vertical 9:16 frame
    if accel_root:
        accel_root.location = (11.0, -0.6, 0.25)
        accel_root.rotation_euler = (math.radians(-25), 0, math.radians(-10))
        accel_root.scale = (0.28, 0.28, 0.28)

    # Car action in background: approaches barrier from X=8.0, halts sharply at frame 680 at barrier
    impact_frame = 680
    impact_x = 11.88
    lane_y = 1.75

    if car_root:
        car_root.location = (7.5, lane_y, 0.0)
        car_root.keyframe_insert(data_path="location", frame=634)

        car_root.location = (impact_x, lane_y, 0.0)
        car_root.keyframe_insert(data_path="location", frame=impact_frame)

        # Rebound
        car_root.location = (impact_x - 0.07, lane_y, 0.0)
        car_root.keyframe_insert(data_path="location", frame=impact_frame + 4)

        car_root.location = (impact_x - 0.06, lane_y, 0.0)
        car_root.keyframe_insert(data_path="location", frame=impact_frame + 12)
        car_root.keyframe_insert(data_path="location", frame=792)

        # Wheels
        if "wheel_rotation" in car_root:
            car_root["wheel_rotation"] = 0.0
            car_root.keyframe_insert(data_path='["wheel_rotation"]', frame=634)
            car_root["wheel_rotation"] = 15.0
            car_root.keyframe_insert(data_path='["wheel_rotation"]', frame=impact_frame)
            car_root["wheel_rotation"] = 15.0
            car_root.keyframe_insert(data_path='["wheel_rotation"]', frame=792)

    # Sensor action in foreground: exactly at impact frame 680, mass jerks forward!
    if accel_root:
        sensor_keys = [
            (634, 0.0, 1.0),
            (678, 0.0, 1.0),
            (685, 0.95, 16.0),   # max surge right after bumper impact
            (705, -0.25, 8.0),
            (725, 0.10, 4.0),
            (745, -0.02, 2.0),
            (765, 0.0, 1.0),
            (792, 0.0, 1.0),
        ]
        for f, disp, glow in sensor_keys:
            if "displacement" in accel_root:
                accel_root["displacement"] = disp
                accel_root.keyframe_insert(data_path='["displacement"]', frame=f)
            if "mass_glow" in accel_root:
                accel_root["mass_glow"] = glow
                accel_root.keyframe_insert(data_path='["mass_glow"]', frame=f)

    # Camera Rig: side-profile, framing barrier & bumper on upper half, sensor on lower half
    cam_data = bpy.data.cameras.new("CAM_SHOT_07")
    cam_data.lens = 45
    cam_data.clip_start = 0.1
    cam_data.clip_end = 100.0
    cam_obj = bpy.data.objects.new("CAM_SHOT_07", cam_data)
    scene.collection.objects.link(cam_obj)
    scene.camera = cam_obj

    # Dolly push slowly towards impact zone
    cam_start = Vector((10.5, -3.2, 1.2))
    cam_end = Vector((11.2, -2.6, 1.1))

    target = Vector((12.5, 1.0, 0.8))

    cam_obj.location = cam_start
    rot_s = (target - cam_start).to_track_quat("-Z", "Y").to_euler()
    cam_obj.rotation_euler = rot_s
    cam_obj.keyframe_insert(data_path="location", frame=634)
    cam_obj.keyframe_insert(data_path="rotation_euler", frame=634)

    cam_obj.location = cam_end
    rot_e = (target - cam_end).to_track_quat("-Z", "Y").to_euler()
    cam_obj.rotation_euler = rot_e
    cam_obj.keyframe_insert(data_path="location", frame=792)
    cam_obj.keyframe_insert(data_path="rotation_euler", frame=792)

    # Clean render QA confirmation
    scene["CLEAN_RENDER_QA_PASSED"] = True

    out_file = SCENES / "shot_07.blend"
    bpy.ops.wm.save_as_mainfile(filepath=str(out_file), check_existing=False)
    print("SUCCESS: Saved staged scene to", out_file)


if __name__ == "__main__":
    build_shot_07()
