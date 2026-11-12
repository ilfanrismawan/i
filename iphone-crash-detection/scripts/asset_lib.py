"""Shared bpy helpers for asset-building scripts (phase 03 onward). Import only; builds nothing by itself."""
import math

import bmesh
import bpy
from mathutils import Matrix, Vector


def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.context.scene.unit_settings.system = "METRIC"


def new_collection(name):
    c = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(c)
    return c


def bsdf(mat):
    return next(n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")


def material(name, color, metallic=0.0, rough=0.5, emission=None, strength=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = bsdf(m)
    for key, value in (("Base Color", (*color, 1.0)), ("Metallic", metallic), ("Roughness", rough)):
        if key in b.inputs:
            b.inputs[key].default_value = value
    if emission:
        for key in ("Emission Color", "Emission"):
            if key in b.inputs:
                b.inputs[key].default_value = (*emission, 1.0)
        b.inputs["Emission Strength"].default_value = strength
    m.diffuse_color = (*color, 1.0)
    return m


def finish(name, bm, coll, mat, parent=None, loc=(0, 0, 0), bevel=0.0, seg=3, smooth=False):
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    coll.objects.link(ob)
    if mat:
        me.materials.append(mat)
    ob.location = loc
    if parent:
        ob.parent = parent
    if bevel:
        md = ob.modifiers.new("Bevel", "BEVEL")
        md.width, md.segments, md.limit_method, md.angle_limit = bevel, seg, "ANGLE", math.radians(40)
        try:
            md.harden_normals = True
        except Exception:
            pass
    if bevel or smooth:
        for p in me.polygons:
            p.use_smooth = True
    return ob


def box(name, size, loc, coll, mat, parent=None, bevel=0.0, seg=3, origin_min_x=False):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co = Vector(((v.co.x + (0.5 if origin_min_x else 0.0)) * size[0], v.co.y * size[1], v.co.z * size[2]))
    return finish(name, bm, coll, mat, parent, loc, bevel, seg)


def cylinder(name, radius, depth, loc, coll, mat, parent=None, axis="Z", segments=48, bevel=0.0):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=segments, radius1=radius, radius2=radius, depth=depth)
    if axis == "Y":
        bmesh.ops.transform(bm, matrix=Matrix.Rotation(math.radians(90), 4, "X"), verts=bm.verts)
    elif axis == "X":
        bmesh.ops.transform(bm, matrix=Matrix.Rotation(math.radians(90), 4, "Y"), verts=bm.verts)
    ob = finish(name, bm, coll, mat, parent, loc, bevel, 2)
    for p in ob.data.polygons:
        p.use_smooth = len(p.vertices) == 4
    return ob


def rounded_slab(name, w, h, depth, radius, loc, coll, mat, parent=None, bevel=0.0, arc=8):
    """Rounded rectangle in the XZ plane extruded along Y, centred on its origin."""
    bm = bmesh.new()
    verts = []
    for cx, cz, start in ((w / 2 - radius, h / 2 - radius, 0), (-(w / 2 - radius), h / 2 - radius, 90),
                          (-(w / 2 - radius), -(h / 2 - radius), 180), (w / 2 - radius, -(h / 2 - radius), 270)):
        for i in range(arc + 1):
            a = math.radians(start + 90 * i / arc)
            verts.append(bm.verts.new((cx + radius * math.cos(a), -depth / 2, cz + radius * math.sin(a))))
    ext = bmesh.ops.extrude_face_region(bm, geom=[bm.faces.new(verts)])
    bmesh.ops.translate(bm, vec=(0, depth, 0), verts=[g for g in ext["geom"] if isinstance(g, bmesh.types.BMVert)])
    return finish(name, bm, coll, mat, parent, loc, bevel, 3)


def torus(name, major, minor, loc, coll, mat, parent=None, seg_major=64, seg_minor=12):
    """Ring lying in the XY plane."""
    bm = bmesh.new()
    rings = []
    for i in range(seg_major):
        a = 2 * math.pi * i / seg_major
        rings.append([bm.verts.new(((major + minor * math.cos(b)) * math.cos(a), (major + minor * math.cos(b)) * math.sin(a), minor * math.sin(b)))
                      for b in (2 * math.pi * j / seg_minor for j in range(seg_minor))])
    for i in range(seg_major):
        r0, r1 = rings[i], rings[(i + 1) % seg_major]
        for j in range(seg_minor):
            bm.faces.new((r0[j], r1[j], r1[(j + 1) % seg_minor], r0[(j + 1) % seg_minor]))
    return finish(name, bm, coll, mat, parent, loc, smooth=True)


def tube(name, r_outer, r_inner, height, loc, coll, mat, parent=None, segments=64):
    """Hollow cylinder standing on z=0 of its origin, open in the middle."""
    bm = bmesh.new()
    ring = lambda r, z: [bm.verts.new((r * math.cos(2 * math.pi * s / segments), r * math.sin(2 * math.pi * s / segments), z)) for s in range(segments)]
    ob, ot, it, ib = ring(r_outer, 0), ring(r_outer, height), ring(r_inner, height), ring(r_inner, 0)
    for a, b in ((ob, ot), (ot, it), (it, ib), (ib, ob)):
        for s in range(segments):
            n = (s + 1) % segments
            bm.faces.new((a[s], a[n], b[n], b[s]))
    return finish(name, bm, coll, mat, parent, loc, smooth=False)


def zigzag(name, loc, coll, mat, parent=None, folds=7, amp=0.11, thick=0.035, height=0.09):
    """Spring-like folded beam from x=0 to x=1 (unit length, origin at the fixed end). Scale X to stretch."""
    bm = bmesh.new()
    pts = [Vector((0, 0, 0))] + [Vector(((i + 0.5) / folds, amp if i % 2 == 0 else -amp, 0)) for i in range(folds)] + [Vector((1, 0, 0))]
    for a, b in zip(pts, pts[1:]):
        d = (b - a).normalized()
        n = Vector((-d.y, d.x, 0)) * thick / 2
        a2, b2 = a - d * thick / 2, b + d * thick / 2
        lo = [bm.verts.new(p + Vector((0, 0, -height / 2))) for p in (a2 - n, b2 - n, b2 + n, a2 + n)]
        hi = [bm.verts.new(p + Vector((0, 0, height / 2))) for p in (a2 - n, b2 - n, b2 + n, a2 + n)]
        bm.faces.new(lo[::-1])
        bm.faces.new(hi)
        for k in range(4):
            bm.faces.new((lo[k], lo[(k + 1) % 4], hi[(k + 1) % 4], hi[k]))
    return finish(name, bm, coll, mat, parent, loc)


def disc_membrane(name, radius, loc, coll, mat, parent=None, rings=14, segments=64):
    """Flat disc in the XY plane with enough rings to deform smoothly."""
    bm = bmesh.new()
    centre = bm.verts.new((0, 0, 0))
    prev = None
    for r in range(1, rings + 1):
        rad = radius * r / rings
        cur = [bm.verts.new((rad * math.cos(2 * math.pi * s / segments), rad * math.sin(2 * math.pi * s / segments), 0)) for s in range(segments)]
        for s in range(segments):
            if prev is None:
                bm.faces.new((centre, cur[s], cur[(s + 1) % segments]))
            else:
                bm.faces.new((prev[s], cur[s], cur[(s + 1) % segments], prev[(s + 1) % segments]))
        prev = cur
    return finish(name, bm, coll, mat, parent, loc, smooth=True)


def empty(name, loc, coll, parent=None, size=0.1, kind="PLAIN_AXES"):
    ob = bpy.data.objects.new(name, None)
    ob.empty_display_type, ob.empty_display_size, ob.location = kind, size, loc
    coll.objects.link(ob)
    if parent:
        ob.parent = parent
    return ob


def control(root, prop, default, lo, hi, description):
    root[prop] = float(default)
    root.id_properties_ui(prop).update(min=lo, max=hi, soft_min=lo, soft_max=hi, default=float(default), description=description)


def drive(idblock, path, root, prop, index=-1, offset=0.0, gain=1.0):
    """value = offset + gain * root[prop]; uses an F-modifier, no Python expression (works with auto-exec off)."""
    fc = idblock.driver_add(path) if index < 0 else idblock.driver_add(path, index)
    d = fc.driver
    d.type = "AVERAGE"
    v = d.variables.new()
    v.name, v.type = "v", "SINGLE_PROP"
    v.targets[0].id = root
    v.targets[0].data_path = f'["{prop}"]'
    for m in list(fc.modifiers):
        fc.modifiers.remove(m)
    mod = fc.modifiers.new("GENERATOR")
    mod.mode, mod.poly_order = "POLYNOMIAL", 1
    mod.coefficients = (offset, gain)
    return fc


def clamp(fc, lo, hi):
    """Clamp a driver's output (applied after the linear generator)."""
    lim = fc.modifiers.new("LIMITS")
    lim.use_min_y = lim.use_max_y = True
    lim.min_y, lim.max_y = lo, hi
    return fc


def drive_curve(idblock, path, root, prop, points, index=-1):
    """Piecewise-linear mapping root[prop] -> value through the given (input, output) points; constant outside."""
    fc = idblock.driver_add(path) if index < 0 else idblock.driver_add(path, index)
    d = fc.driver
    d.type = "AVERAGE"
    v = d.variables.new()
    v.name, v.type = "v", "SINGLE_PROP"
    v.targets[0].id = root
    v.targets[0].data_path = f'["{prop}"]'
    for m in list(fc.modifiers):
        fc.modifiers.remove(m)
    while fc.keyframe_points:  # new drivers come with default (0,0),(1,1) keys; drop them
        fc.keyframe_points.remove(fc.keyframe_points[0])
    for t, val in points:
        fc.keyframe_points.insert(t, val).interpolation = "LINEAR"
    fc.extrapolation = "CONSTANT"
    return fc


def drive_bsdf(mat, socket, root, prop, offset=0.0, gain=1.0):
    b = bsdf(mat)
    idx = list(b.inputs).index(b.inputs[socket])
    return drive(mat.node_tree, f'nodes["{b.name}"].inputs[{idx}].default_value', root, prop, offset=offset, gain=gain)


def bsdf_path(mat, socket):
    b = bsdf(mat)
    return f'nodes["{b.name}"].inputs[{list(b.inputs).index(b.inputs[socket])}].default_value'


def prism(name, pts_xz, depth, loc, coll, mat, parent=None):
    """Convex polygon given in the XZ plane, extruded along Y, centred in Y on its origin."""
    bm = bmesh.new()
    face = bm.faces.new([bm.verts.new((x, -depth / 2, z)) for x, z in pts_xz])
    ext = bmesh.ops.extrude_face_region(bm, geom=[face])
    bmesh.ops.translate(bm, vec=(0, depth, 0), verts=[g for g in ext["geom"] if isinstance(g, bmesh.types.BMVert)])
    return finish(name, bm, coll, mat, parent, loc)


def arc_band(name, r_in, r_out, a0, a1, depth, loc, coll, mat, parent=None, plane="XZ", steps=32):
    """Flat ring segment from angle a0 to a1 (degrees), thickness `depth` across the plane normal."""
    bm = bmesh.new()

    def P(r, a, h):
        c, s = r * math.cos(a), r * math.sin(a)
        return (c, h, s) if plane == "XZ" else (c, s, h)

    rows = []
    for i in range(steps + 1):
        a = math.radians(a0 + (a1 - a0) * i / steps)
        rows.append([bm.verts.new(P(r, a, h)) for r, h in ((r_in, -depth / 2), (r_out, -depth / 2), (r_out, depth / 2), (r_in, depth / 2))])
    for i in range(steps):
        p, q = rows[i], rows[i + 1]
        for k in range(4):
            bm.faces.new((p[k], p[(k + 1) % 4], q[(k + 1) % 4], q[k]))
    bm.faces.new(rows[0])
    bm.faces.new(rows[-1][::-1])
    return finish(name, bm, coll, mat, parent, loc)


def save(path):
    bpy.ops.wm.save_as_mainfile(filepath=str(path), check_existing=False)
    print("SAVED", path)
