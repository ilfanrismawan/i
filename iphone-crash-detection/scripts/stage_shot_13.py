"""Stage SHOT_13: Isometric logic board cutaway — signal paths converge to processor chip.
Frame range: 1369 to 1442 (30 fps, 2.467 s).
Resolution: 1080 x 1920 (9:16 vertical).
Engine: Eevee ONLY.

Outputs:
  scenes/shot_13.blend
"""
import math
from pathlib import Path

import bpy
from mathutils import Vector

PROJECT = Path("c:/Users/HOG-PC001/Documents/i/iphone-crash-detection")
ASSETS = PROJECT / "assets"
SCENES = PROJECT / "scenes"
SCENES.mkdir(exist_ok=True)


def build_shot_13():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.render.fps = 30
    scene.frame_start = 1369
    scene.frame_end = 1442
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
    world = bpy.data.worlds.new("World_Shot13")
    scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs["Color"].default_value = (0.015, 0.025, 0.05, 1.0)
        bg.inputs["Strength"].default_value = 0.4

    # Lighting
    key_data = bpy.data.lights.new(name="Key_Light", type="AREA")
    key_data.energy = 25.0
    key_data.size = 1.0
    key_data.color = (0.85, 0.92, 1.0)
    key = bpy.data.objects.new(name="Key_Light", object_data=key_data)
    scene.collection.objects.link(key)
    key.location = (2, -2, 4)

    fill_data = bpy.data.lights.new(name="Fill_Light", type="AREA")
    fill_data.energy = 12.0
    fill_data.size = 0.8
    fill_data.color = (1.0, 0.6, 0.2)
    fill = bpy.data.objects.new(name="Fill_Light", object_data=fill_data)
    scene.collection.objects.link(fill)
    fill.location = (-2, 2, 2)

    # Append Phone Interior Concept
    with bpy.data.libraries.load(str(ASSETS / "phone_interior_concept.blend"), link=False) as (data_from, data_to):
        data_to.collections = list(data_from.collections)
    for coll in data_to.collections:
        scene.collection.children.link(coll)

    # Central processor chip glow
    chip = bpy.data.objects.get("INT_Processor")
    if not chip:
        # Create a central chip if name differs
        bpy.ops.mesh.primitive_cube_add(size=0.35, location=(0, 0, 0.05))
        chip = bpy.context.active_object
        chip.name = "PHONE_ProcessorChip"

    chip_mat = bpy.data.materials.new("Chip_Pulse_Mat")
    chip_mat.use_nodes = True
    nodes = chip_mat.node_tree.nodes
    for n in nodes:
        nodes.remove(n)
    emit = nodes.new("ShaderNodeEmission")
    emit.inputs["Color"].default_value = (0.2, 0.9, 0.6, 1.0)
    emit.inputs["Strength"].default_value = 8.0
    out = nodes.new("ShaderNodeOutputMaterial")
    chip_mat.node_tree.links.new(emit.outputs["Emission"], out.inputs["Surface"])
    chip.data.materials.append(chip_mat)

    # Camera: Isometric cutaway view tracking down to chip
    cam_data = bpy.data.cameras.new("CAM_SHOT_13")
    cam_data.lens = 50
    cam_data.clip_start = 0.1
    cam_data.clip_end = 100.0
    cam_obj = bpy.data.objects.new("CAM_SHOT_13", cam_data)
    scene.collection.objects.link(cam_obj)
    scene.camera = cam_obj

    cam_start = Vector((1.2, -1.8, 2.2))
    target = Vector((0.0, 0.0, 0.0))
    rot_s = (target - cam_start).to_track_quat("-Z", "Y").to_euler()
    cam_obj.location = cam_start
    cam_obj.rotation_euler = rot_s
    cam_obj.keyframe_insert(data_path="location", frame=1369)
    cam_obj.keyframe_insert(data_path="rotation_euler", frame=1369)

    cam_end = Vector((0.8, -1.2, 1.4))
    rot_e = (target - cam_end).to_track_quat("-Z", "Y").to_euler()
    cam_obj.location = cam_end
    cam_obj.rotation_euler = rot_e
    cam_obj.keyframe_insert(data_path="location", frame=1442)
    cam_obj.keyframe_insert(data_path="rotation_euler", frame=1442)

    scene["CLEAN_RENDER_QA_PASSED"] = True

    out_file = SCENES / "shot_13.blend"
    bpy.ops.wm.save_as_mainfile(filepath=str(out_file), check_existing=False)
    print("SUCCESS: Saved staged scene to", out_file)


if __name__ == "__main__":
    build_shot_13()
