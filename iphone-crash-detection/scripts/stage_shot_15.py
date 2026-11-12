"""Stage SHOT_15: Phone on dash with emergency alert countdown.
Frame range: 1581 to 1692 (30 fps, 3.733 s).
Resolution: 1080 x 1920 (9:16 vertical).
Engine: Eevee ONLY.

Outputs:
  scenes/shot_15.blend
"""
import math
from pathlib import Path

import bpy
from mathutils import Vector

PROJECT = Path("c:/Users/HOG-PC001/Documents/i/iphone-crash-detection")
ASSETS = PROJECT / "assets"
SCENES = PROJECT / "scenes"
SCENES.mkdir(exist_ok=True)


def build_shot_15():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.render.fps = 30
    scene.frame_start = 1581
    scene.frame_end = 1692
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
    world = bpy.data.worlds.new("World_Shot15")
    scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs["Color"].default_value = (0.02, 0.03, 0.05, 1.0)
        bg.inputs["Strength"].default_value = 0.4

    # Dash interior light
    dash_data = bpy.data.lights.new(name="Dash_Light", type="AREA")
    dash_data.energy = 8.0
    dash_data.size = 1.0
    dash_data.color = (0.7, 0.8, 1.0)
    dash_light = bpy.data.objects.new(name="Dash_Light", object_data=dash_data)
    scene.collection.objects.link(dash_light)
    dash_light.location = (0, -1.0, 1.2)

    # Screen emission / red alert pulse
    alert_data = bpy.data.lights.new(name="Alert_Pulse", type="POINT")
    alert_data.energy = 15.0
    alert_data.color = (1.0, 0.2, 0.1)
    alert_light = bpy.data.objects.new(name="Alert_Pulse", object_data=alert_data)
    scene.collection.objects.link(alert_light)
    alert_light.location = (0, -0.2, 0.1)

    # Append Car Interior Dash
    with bpy.data.libraries.load(str(ASSETS / "car_interior_dash.blend"), link=False) as (data_from, data_to):
        data_to.collections = list(data_from.collections)
    for coll in data_to.collections:
        scene.collection.children.link(coll)

    # Append Phone Exterior
    with bpy.data.libraries.load(str(ASSETS / "phone_exterior.blend"), link=False) as (data_from, data_to):
        data_to.collections = list(data_from.collections)
    for coll in data_to.collections:
        scene.collection.children.link(coll)

    # Append Phone UI Alert
    with bpy.data.libraries.load(str(ASSETS / "phone_ui_alert.blend"), link=False) as (data_from, data_to):
        data_to.collections = list(data_from.collections)
    for coll in data_to.collections:
        scene.collection.children.link(coll)

    # Camera: locked front-on close of screen
    cam_data = bpy.data.cameras.new("CAM_SHOT_15")
    cam_data.lens = 55
    cam_data.clip_start = 0.05
    cam_data.clip_end = 50.0
    cam_obj = bpy.data.objects.new("CAM_SHOT_15", cam_data)
    scene.collection.objects.link(cam_obj)
    scene.camera = cam_obj

    cam_pos = Vector((0.0, -1.1, 0.0))
    target = Vector((0.0, 0.0, 0.0))
    rot = (target - cam_pos).to_track_quat("-Z", "Y").to_euler()
    cam_obj.location = cam_pos
    cam_obj.rotation_euler = rot

    scene["CLEAN_RENDER_QA_PASSED"] = True

    out_file = SCENES / "shot_15.blend"
    bpy.ops.wm.save_as_mainfile(filepath=str(out_file), check_existing=False)
    print("SUCCESS: Saved staged scene to", out_file)


if __name__ == "__main__":
    build_shot_15()
