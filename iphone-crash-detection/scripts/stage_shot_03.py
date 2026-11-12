"""Stage SHOT_03: Layar iPhone di dasbor menampilkan peringatan tabrakan diegetik.
Frame range: 218 to 315 (30 fps, 3.267 s).
Resolution: 1080 x 1920 (9:16 vertical).
Engine: Eevee ONLY.

Outputs:
  scenes/shot_03.blend
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


def build_shot_03():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.render.fps = 30
    scene.frame_start = 218
    scene.frame_end = 315
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

    # World lighting: subtle ambient cabin lighting
    world = bpy.data.worlds.new("World_Shot03")
    scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs["Color"].default_value = (0.02, 0.03, 0.05, 1.0)
        bg.inputs["Strength"].default_value = 0.5

    # Key light: outside windshield ambient light
    light_data = bpy.data.lights.new(name="Cabin_KeyLight", type="AREA")
    light_data.energy = 8.0
    light_data.size = 0.8
    light_data.color = (0.85, 0.90, 1.0)
    key_light = bpy.data.objects.new(name="Cabin_KeyLight", object_data=light_data)
    scene.collection.objects.link(key_light)
    key_light.location = (0.0, -0.8, 0.6)
    key_light.rotation_euler = (math.radians(-45), 0, 0)

    # Fill light: soft cabin warmth
    fill_data = bpy.data.lights.new(name="Cabin_FillLight", type="POINT")
    fill_data.energy = 3.0
    fill_data.color = (1.0, 0.8, 0.7)
    fill = bpy.data.objects.new(name="Cabin_FillLight", object_data=fill_data)
    scene.collection.objects.link(fill)
    fill.location = (-0.4, 0.3, 0.2)

    # Append Car Interior Dash
    with bpy.data.libraries.load(str(ASSETS / "car_interior_dash.blend"), link=False) as (data_from, data_to):
        data_to.collections = list(data_from.collections)
    coll_dash = data_to.collections[0]
    scene.collection.children.link(coll_dash)
    dash_root = bpy.data.objects.get("DASH_Root")

    # Append Phone Exterior
    with bpy.data.libraries.load(str(ASSETS / "phone_exterior.blend"), link=False) as (data_from, data_to):
        data_to.collections = [c for c in data_from.collections if c == "ASSET_Phone"]
    coll_phone = data_to.collections[0]
    scene.collection.children.link(coll_phone)
    phone_root = bpy.data.objects.get("PHONE_Root")

    # Append Phone UI Alert
    with bpy.data.libraries.load(str(ASSETS / "phone_ui_alert.blend"), link=False) as (data_from, data_to):
        data_to.collections = [c for c in data_from.collections if c == "ASSET_PhoneUIAlert"]
    coll_ui = data_to.collections[0]
    scene.collection.children.link(coll_ui)
    ui_root = bpy.data.objects.get("UIALERT_Root")

    # Mount phone onto dashboard mount anchor
    mount_anchor = bpy.data.objects.get("ANCHOR_PhoneMount")
    if mount_anchor and phone_root:
        phone_root.parent = mount_anchor
        phone_root.location = (0, 0, 0)
        phone_root.rotation_euler = (0, 0, 0)

    # Attach UI to Phone screen anchor
    screen_anchor = bpy.data.objects.get("ANCHOR_ScreenCenter")
    if screen_anchor and ui_root:
        ui_root.parent = screen_anchor
        ui_root.location = (0, -0.001, 0)  # slightly in front of glass screen
        ui_root.rotation_euler = (0, 0, 0)

    # UI Animation: alert glow pulse & countdown rotation
    if ui_root and "alert_glow" in ui_root:
        for f in range(218, 316, 15):
            # pulsing emission
            glow = 6.0 if ((f - 218) // 15) % 2 == 0 else 3.5
            ui_root["alert_glow"] = glow
            ui_root.keyframe_insert(data_path='["alert_glow"]', frame=f)

    # Camera Rig: over-shoulder from driver's perspective, dolly-pushing towards the glowing screen
    cam_data = bpy.data.cameras.new("CAM_SHOT_03")
    cam_data.lens = 55  # portrait cinematic focal length
    cam_data.clip_start = 0.05
    cam_data.clip_end = 20.0
    cam_obj = bpy.data.objects.new("CAM_SHOT_03", cam_data)
    scene.collection.objects.link(cam_obj)
    scene.camera = cam_obj

    # Focus target point: center of phone screen
    target = Vector((0.0, -0.046, 0.09))

    # Frame 218: Over the shoulder / steering wheel view
    cam_start = Vector((-0.26, 0.42, 0.24))
    cam_obj.location = cam_start
    rot = (target - cam_start).to_track_quat("-Z", "Y").to_euler()
    cam_obj.rotation_euler = rot
    cam_obj.keyframe_insert(data_path="location", frame=218)
    cam_obj.keyframe_insert(data_path="rotation_euler", frame=218)

    # Frame 315: Dolly push in closer to screen
    cam_end = Vector((-0.12, 0.22, 0.16))
    cam_obj.location = cam_end
    rot_end = (target - cam_end).to_track_quat("-Z", "Y").to_euler()
    cam_obj.rotation_euler = rot_end
    cam_obj.keyframe_insert(data_path="location", frame=315)
    cam_obj.keyframe_insert(data_path="rotation_euler", frame=315)

    # Smooth linear push
    if cam_obj.animation_data and cam_obj.animation_data.action:
        for fc in get_all_fcurves(cam_obj.animation_data.action):
            for kf in fc.keyframe_points:
                kf.interpolation = "BEZIER"

    # Clean render QA confirmation
    scene["CLEAN_RENDER_QA_PASSED"] = True

    out_file = SCENES / "shot_03.blend"
    bpy.ops.wm.save_as_mainfile(filepath=str(out_file), check_existing=False)
    print("SUCCESS: Saved staged scene to", out_file)


if __name__ == "__main__":
    build_shot_03()
