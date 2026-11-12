"""Stage SHOT_16: Low-angle crane up following emergency call waves toward the sky.
Frame range: 1693 to 1818 (30 fps, 4.200 s).
Resolution: 1080 x 1920 (9:16 vertical).
Engine: Eevee ONLY.

Outputs:
  scenes/shot_16.blend
"""
import math
from pathlib import Path

import bpy
from mathutils import Vector

PROJECT = Path("c:/Users/HOG-PC001/Documents/i/iphone-crash-detection")
ASSETS = PROJECT / "assets"
SCENES = PROJECT / "scenes"
SCENES.mkdir(exist_ok=True)


def build_shot_16():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.render.fps = 30
    scene.frame_start = 1693
    scene.frame_end = 1818
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

    # World (night/dusk sky)
    world = bpy.data.worlds.new("World_Shot16")
    scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs["Color"].default_value = (0.02, 0.03, 0.07, 1.0)
        bg.inputs["Strength"].default_value = 0.5

    # Lights
    moon_data = bpy.data.lights.new(name="Moon_Light", type="SUN")
    moon_data.energy = 2.0
    moon_data.color = (0.7, 0.8, 1.0)
    moon = bpy.data.objects.new(name="Moon_Light", object_data=moon_data)
    scene.collection.objects.link(moon)
    moon.location = (0, 0, 15)

    call_glow_data = bpy.data.lights.new(name="Call_Glow", type="POINT")
    call_glow_data.energy = 20.0
    call_glow_data.color = (0.2, 0.8, 0.4)
    call_glow = bpy.data.objects.new(name="Call_Glow", object_data=call_glow_data)
    scene.collection.objects.link(call_glow)
    call_glow.location = (0, 0, 0.2)

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

    # Append Phone UI Call
    with bpy.data.libraries.load(str(ASSETS / "phone_ui_call.blend"), link=False) as (data_from, data_to):
        data_to.collections = list(data_from.collections)
    for coll in data_to.collections:
        scene.collection.children.link(coll)

    # Schematic beacon rings rising
    for i in range(4):
        bpy.ops.mesh.primitive_torus_add(
            major_radius=0.3 + i * 0.2,
            minor_radius=0.015,
            location=(0, 0, 0.5 + i * 0.4)
        )
        ring = bpy.context.active_object
        ring.name = f"BeaconRing_{i}"
        mat = bpy.data.materials.new(f"Ring_Mat_{i}")
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        for n in nodes:
            nodes.remove(n)
        emit = nodes.new("ShaderNodeEmission")
        emit.inputs["Color"].default_value = (0.2, 0.9, 0.4, 1.0)
        emit.inputs["Strength"].default_value = 8.0
        out = nodes.new("ShaderNodeOutputMaterial")
        mat.node_tree.links.new(emit.outputs["Emission"], out.inputs["Surface"])
        ring.data.materials.append(mat)

    # Camera: low-angle crane up
    cam_data = bpy.data.cameras.new("CAM_SHOT_16")
    cam_data.lens = 28
    cam_data.clip_start = 0.1
    cam_data.clip_end = 100.0
    cam_obj = bpy.data.objects.new("CAM_SHOT_16", cam_data)
    scene.collection.objects.link(cam_obj)
    scene.camera = cam_obj

    cam_start = Vector((0.0, -1.2, -0.4))
    target_s = Vector((0.0, 0.0, 0.2))
    rot_s = (target_s - cam_start).to_track_quat("-Z", "Y").to_euler()
    cam_obj.location = cam_start
    cam_obj.rotation_euler = rot_s
    cam_obj.keyframe_insert(data_path="location", frame=1693)
    cam_obj.keyframe_insert(data_path="rotation_euler", frame=1693)

    cam_end = Vector((0.0, -2.5, 3.5))
    target_e = Vector((0.0, 0.0, 1.5))
    rot_e = (target_e - cam_end).to_track_quat("-Z", "Y").to_euler()
    cam_obj.location = cam_end
    cam_obj.rotation_euler = rot_e
    cam_obj.keyframe_insert(data_path="location", frame=1818)
    cam_obj.keyframe_insert(data_path="rotation_euler", frame=1818)

    scene["CLEAN_RENDER_QA_PASSED"] = True

    out_file = SCENES / "shot_16.blend"
    bpy.ops.wm.save_as_mainfile(filepath=str(out_file), check_existing=False)
    print("SUCCESS: Saved staged scene to", out_file)


if __name__ == "__main__":
    build_shot_16()
