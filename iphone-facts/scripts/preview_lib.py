"""Shared test/preview helpers for asset scripts. Import only; builds nothing by itself."""
import math

import bpy
from mathutils import Vector


def setp(root, **props):
    for k, v in props.items():
        root[k] = float(v)
    root.update_tag()
    bpy.context.view_layer.update()
    return bpy.context.evaluated_depsgraph_get()


def world_bounds(objs, dg=None):
    dg = dg or bpy.context.evaluated_depsgraph_get()
    pts = []
    for o in objs:
        if o.type == "MESH":
            e = o.evaluated_get(dg)
            pts += [e.matrix_world @ Vector(c) for c in e.bound_box]
    lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    return lo, hi


def append_collection(blend_path, name):
    """Append (copy) a collection from another asset file into the current scene; the source file is untouched."""
    with bpy.data.libraries.load(str(blend_path), link=False) as (src, dst):
        dst.collections = [name]
    col = dst.collections[0]
    bpy.context.scene.collection.children.link(col)
    return col


def preview(out_dir, root, shots, report, sky=(0.05, 0.06, 0.09), samples=32):
    """Render 540x960 Eevee stills. Lights/camera/world made here are not saved unless the caller saves afterwards."""
    scene = bpy.context.scene
    for eng in ("BLENDER_EEVEE_NEXT", "BLENDER_EEVEE"):
        try:
            scene.render.engine = eng
            break
        except Exception:
            continue
    assert "EEVEE" in scene.render.engine
    scene.render.resolution_x, scene.render.resolution_y, scene.render.resolution_percentage = 540, 960, 100
    try:
        scene.eevee.taa_render_samples = samples
        scene.view_settings.view_transform = "Standard"
    except Exception:
        pass
    world = bpy.data.worlds.new("PREVIEW_World")
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs[0].default_value = (*sky, 1)
    scene.world = world
    for name, energy, rot in (("Key", 3.0, (48, 0, -35)), ("Fill", 1.4, (62, 0, 150))):
        L = bpy.data.objects.new(f"PREVIEW_{name}", bpy.data.lights.new(f"PREVIEW_{name}", "SUN"))
        L.data.energy, L.rotation_euler = energy, tuple(math.radians(a) for a in rot)
        scene.collection.objects.link(L)
    cam = bpy.data.objects.new("PREVIEW_Cam", bpy.data.cameras.new("PREVIEW_Cam"))
    scene.collection.objects.link(cam)
    scene.camera = cam
    out_dir.mkdir(parents=True, exist_ok=True)
    for name, props, pos, target, lens in shots:
        setp(root, **props)
        cam.location, cam.data.lens = pos, lens
        cam.data.clip_start, cam.data.clip_end = 0.002, 200
        cam.rotation_euler = (Vector(target) - Vector(pos)).to_track_quat("-Z", "Y").to_euler()
        path = out_dir / f"{name}.png"
        scene.render.filepath = str(path)
        bpy.ops.render.render(write_still=True)
        report["renders"].append({"file": f"{out_dir.parent.name}/previews/{name}.png", "exists": path.is_file()})
