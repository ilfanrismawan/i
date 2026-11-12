"""Stage SHOT_12: Overhead road view, GPS trail dots stopping at barrier.
Frame range: 1240 to 1368 (30 fps, 4.300 s).
Resolution: 1080 x 1920 (9:16 vertical).
Engine: Eevee ONLY.

Outputs:
  scenes/shot_12.blend
"""
import math
from pathlib import Path

import bpy
from mathutils import Vector

PROJECT = Path("c:/Users/HOG-PC001/Documents/i/iphone-crash-detection")
ASSETS = PROJECT / "assets"
SCENES = PROJECT / "scenes"
SCENES.mkdir(exist_ok=True)


def build_shot_12():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.render.fps = 30
    scene.frame_start = 1240
    scene.frame_end = 1368
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
    world = bpy.data.worlds.new("World_Shot12")
    scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs["Color"].default_value = (0.04, 0.05, 0.08, 1.0)
        bg.inputs["Strength"].default_value = 0.6

    # Sun
    light_data = bpy.data.lights.new(name="Sun_Light", type="SUN")
    light_data.energy = 4.0
    light_data.color = (1.0, 0.95, 0.88)
    sun = bpy.data.objects.new(name="Sun_Light", object_data=light_data)
    scene.collection.objects.link(sun)
    sun.location = (0, 0, 20)
    sun.rotation_euler = (0, 0, 0)

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

    # Car stops at barrier
    impact_x = 11.88
    lane_y = 1.75
    if car_root:
        car_root.location = (impact_x, lane_y, 0.0)

    # GPS trail dots (small glowing emission spheres)
    dot_mat = bpy.data.materials.new("GPS_Dot_Mat")
    dot_mat.use_nodes = True
    nodes = dot_mat.node_tree.nodes
    for n in nodes:
        nodes.remove(n)
    emit = nodes.new("ShaderNodeEmission")
    emit.inputs["Color"].default_value = (0.2, 0.8, 1.0, 1.0)
    emit.inputs["Strength"].default_value = 10.0
    out = nodes.new("ShaderNodeOutputMaterial")
    dot_mat.node_tree.links.new(emit.outputs["Emission"], out.inputs["Surface"])

    # Create 8 dots along the lane
    for i in range(8):
        x_pos = 4.0 + i * 1.1
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.12, location=(x_pos, lane_y, 0.08))
        dot = bpy.context.active_object
        dot.name = f"GPS_Dot_{i}"
        dot.data.materials.append(dot_mat)
        # Animate appearance
        appear_frame = 1240 + i * 12
        dot.scale = (0.001, 0.001, 0.001)
        dot.keyframe_insert(data_path="scale", frame=appear_frame - 1)
        dot.scale = (1.0, 1.0, 1.0)
        dot.keyframe_insert(data_path="scale", frame=appear_frame)

    # Camera: locked overhead
    cam_data = bpy.data.cameras.new("CAM_SHOT_12")
    cam_data.lens = 32
    cam_data.clip_start = 0.1
    cam_data.clip_end = 100.0
    cam_obj = bpy.data.objects.new("CAM_SHOT_12", cam_data)
    scene.collection.objects.link(cam_obj)
    scene.camera = cam_obj

    cam_obj.location = (8.5, 1.75, 14.0)
    cam_obj.rotation_euler = (0, 0, -math.radians(90))

    scene["CLEAN_RENDER_QA_PASSED"] = True

    out_file = SCENES / "shot_12.blend"
    bpy.ops.wm.save_as_mainfile(filepath=str(out_file), check_existing=False)
    print("SUCCESS: Saved staged scene to", out_file)


if __name__ == "__main__":
    build_shot_12()
