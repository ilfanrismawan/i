"""Phase 02 - master assets. Builds three independent .blend files with bpy (headless).

Run:  blender --background --python scripts/build_master_assets.py -- <project_dir>

Outputs (never overwrites other phases' files):
  assets/phone_exterior.blend   collection ASSET_Phone  (real scale, metres, upright, screen faces -Y)
  assets/car_stylized.blend     collection ASSET_Car    (toy-styled, faces +X, root on ground)
  assets/road_set.blend         collection ASSET_Road   (road along X, barrier across the +Y lane)

All shapes are stylised illustrations, not manufacturer CAD. No logos or text.
"""
import math
import sys
from pathlib import Path

import bmesh
import bpy
from mathutils import Matrix, Vector

PROJECT = Path(sys.argv[sys.argv.index("--") + 1]).resolve()
ASSETS = PROJECT / "assets"
ASSETS.mkdir(exist_ok=True)


# ---------------------------------------------------------------- helpers
def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.context.scene.unit_settings.system = "METRIC"


def new_collection(name):
    c = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(c)
    return c


def material(name, color, metallic=0.0, rough=0.5, emission=None, strength=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")

    def put(key, value):
        if key in b.inputs:
            b.inputs[key].default_value = value

    put("Base Color", (*color, 1.0))
    put("Metallic", metallic)
    put("Roughness", rough)
    if emission:
        put("Emission Color", (*emission, 1.0))
        put("Emission", (*emission, 1.0))
        put("Emission Strength", strength)
    m.diffuse_color = (*color, 1.0)
    if hasattr(m, "blend_method"):
        try:
            m.blend_method = "HASHED"
        except Exception:
            pass
    return m


def finish(name, bm, coll, mat, parent=None, loc=(0, 0, 0), bevel=0.0, seg=3):
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
        md.width = bevel
        md.segments = seg
        md.limit_method = "ANGLE"
        md.angle_limit = math.radians(40)
        try:
            md.harden_normals = True
        except Exception:
            pass
        for p in me.polygons:
            p.use_smooth = True
    return ob


def box(name, size, loc, coll, mat, parent=None, bevel=0.0, seg=3, taper=None):
    """taper=(sx, sy): scale of the top face, for wedge/trapezoid shapes."""
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        top = v.co.z > 0
        v.co = Vector((v.co.x * size[0], v.co.y * size[1], v.co.z * size[2]))
        if taper and top:
            v.co.x *= taper[0]
            v.co.y *= taper[1]
    return finish(name, bm, coll, mat, parent, loc, bevel, seg)


def cylinder(name, radius, depth, loc, coll, mat, parent=None, axis="Z", segments=48, bevel=0.0, radius2=None):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=segments,
                          radius1=radius, radius2=radius if radius2 is None else radius2, depth=depth)
    if axis == "Y":
        bmesh.ops.transform(bm, matrix=Matrix.Rotation(math.radians(90), 4, "X"), verts=bm.verts)
    elif axis == "X":
        bmesh.ops.transform(bm, matrix=Matrix.Rotation(math.radians(90), 4, "Y"), verts=bm.verts)
    ob = finish(name, bm, coll, mat, parent, loc, bevel, 2)
    for p in ob.data.polygons:
        p.use_smooth = len(p.vertices) == 4
    return ob


def icosphere(name, radius, loc, coll, mat, parent=None, scale=(1, 1, 1)):
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=2, radius=radius)
    for v in bm.verts:
        v.co = Vector((v.co.x * scale[0], v.co.y * scale[1], v.co.z * scale[2]))
    return finish(name, bm, coll, mat, parent, loc)


def rounded_slab(name, w, h, depth, radius, loc, coll, mat, parent=None, bevel=0.0, arc=10):
    """Rounded rectangle in the XZ plane, extruded along +Y, centred on its own origin."""
    bm = bmesh.new()
    verts = []
    corners = [(w / 2 - radius, h / 2 - radius, 0), (-(w / 2 - radius), h / 2 - radius, 90),
               (-(w / 2 - radius), -(h / 2 - radius), 180), (w / 2 - radius, -(h / 2 - radius), 270)]
    for cx, cz, start in corners:
        for i in range(arc + 1):
            a = math.radians(start + 90 * i / arc)
            verts.append(bm.verts.new((cx + radius * math.cos(a), -depth / 2, cz + radius * math.sin(a))))
    face = bm.faces.new(verts)
    ext = bmesh.ops.extrude_face_region(bm, geom=[face])
    bmesh.ops.translate(bm, vec=(0, depth, 0), verts=[g for g in ext["geom"] if isinstance(g, bmesh.types.BMVert)])
    return finish(name, bm, coll, mat, parent, loc, bevel, 3)


def empty(name, loc, coll, parent=None, size=0.1, kind="PLAIN_AXES"):
    ob = bpy.data.objects.new(name, None)
    ob.empty_display_type = kind
    ob.empty_display_size = size
    ob.location = loc
    coll.objects.link(ob)
    if parent:
        ob.parent = parent
    return ob


def control(root, prop, default, lo, hi, description):
    root[prop] = float(default)
    root.id_properties_ui(prop).update(min=lo, max=hi, soft_min=lo, soft_max=hi, default=float(default), description=description)


def drive(idblock, path, root, prop, index=-1):
    fc = idblock.driver_add(path) if index < 0 else idblock.driver_add(path, index)
    d = fc.driver
    d.type = "AVERAGE"
    v = d.variables.new()
    v.name = "v"
    v.type = "SINGLE_PROP"
    v.targets[0].id = root
    v.targets[0].data_path = f'["{prop}"]'
    return fc


def drive_bsdf(mat, socket, root, prop):
    b = next(n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    idx = list(b.inputs).index(b.inputs[socket])
    drive(mat.node_tree, f'nodes["{b.name}"].inputs[{idx}].default_value', root, prop)


def save(name):
    path = ASSETS / name
    bpy.ops.wm.save_as_mainfile(filepath=str(path), check_existing=False)
    print("SAVED", path)


# ---------------------------------------------------------------- phone
def build_phone():
    reset()
    c = new_collection("ASSET_Phone")
    W, H, T = 0.0715, 0.1467, 0.0078  # metres; generic 6.1-inch class smartphone
    root = empty("PHONE_Root", (0, 0, 0), c, size=0.05)
    m_frame = material("PHONE_Mat_Frame", (0.30, 0.42, 0.62), metallic=0.85, rough=0.32)
    m_back = material("PHONE_Mat_BackGlass", (0.42, 0.55, 0.74), metallic=0.1, rough=0.18)
    m_screen = material("PHONE_Mat_Screen", (0.01, 0.012, 0.018), rough=0.08, emission=(0.10, 0.14, 0.22), strength=0.3)
    m_dark = material("PHONE_Mat_Dark", (0.02, 0.02, 0.025), rough=0.35)
    m_lens = material("PHONE_Mat_Lens", (0.01, 0.01, 0.02), metallic=0.6, rough=0.05)
    m_metal = material("PHONE_Mat_LensRing", (0.55, 0.62, 0.74), metallic=0.9, rough=0.25)

    rounded_slab("PHONE_Frame", W, H, T, 0.0120, (0, 0, 0), c, m_frame, root, bevel=0.0011)
    rounded_slab("PHONE_Screen", W - 0.0042, H - 0.0042, 0.0005, 0.0100, (0, -(T / 2 + 0.00012), 0), c, m_screen, root)
    rounded_slab("PHONE_BackGlass", W - 0.0030, H - 0.0030, 0.0005, 0.0106, (0, T / 2 + 0.00012, 0), c, m_back, root)
    # camera island, seen from the back it sits top-left => +X when the screen faces -Y
    bx, bz, by = W / 2 - 0.0215, H / 2 - 0.0215, T / 2 + 0.0012
    rounded_slab("PHONE_CameraBump", 0.0340, 0.0340, 0.0020, 0.0090, (bx, by, bz), c, m_back, root, bevel=0.0006)
    for i, (dx, dz) in enumerate([(0.0075, 0.0075), (-0.0075, -0.0075)]):
        cylinder(f"PHONE_LensRing_{i + 1}", 0.0078, 0.0026, (bx + dx, by + 0.0016, bz + dz), c, m_metal, root, axis="Y", bevel=0.0004)
        cylinder(f"PHONE_LensGlass_{i + 1}", 0.0056, 0.0028, (bx + dx, by + 0.0017, bz + dz), c, m_lens, root, axis="Y")
    cylinder("PHONE_Flash", 0.0028, 0.0010, (bx - 0.0080, by + 0.0010, bz + 0.0080), c,
             material("PHONE_Mat_Flash", (0.95, 0.92, 0.80), rough=0.3), root, axis="Y")
    # bottom edge: port and two rows of holes (microphone / speaker openings)
    box("PHONE_Port", (0.0086, 0.0026, 0.0012), (0, 0, -H / 2 + 0.0002), c, m_dark, root)
    for side in (-1, 1):
        for i in range(4):
            cylinder(f"PHONE_BottomHole_{'L' if side < 0 else 'R'}{i + 1}", 0.00065, 0.0012,
                     (side * (0.0105 + i * 0.0030), 0, -H / 2 + 0.0002), c, m_dark, root, axis="Z", segments=16)
    # side buttons
    box("PHONE_ButtonPower", (0.0010, 0.0026, 0.0150), (W / 2 + 0.0002, 0, 0.020), c, m_frame, root, bevel=0.0003)
    box("PHONE_ButtonVolUp", (0.0010, 0.0026, 0.0090), (-W / 2 - 0.0002, 0, 0.030), c, m_frame, root, bevel=0.0003)
    box("PHONE_ButtonVolDown", (0.0010, 0.0026, 0.0090), (-W / 2 - 0.0002, 0, 0.017), c, m_frame, root, bevel=0.0003)

    empty("ANCHOR_ScreenCenter", (0, -T / 2, 0), c, root, 0.01)
    empty("ANCHOR_MicHole", (-0.0105, 0, -H / 2), c, root, 0.005)
    empty("ANCHOR_Interior", (0, 0, 0), c, root, 0.01)
    empty("CAM_Target_Phone", (0, 0, 0), c, root, 0.02, "SPHERE")

    control(root, "shell_opacity", 1.0, 0.0, 1.0, "1 = solid body, 0 = fully see-through (x-ray shots)")
    control(root, "screen_glow", 0.3, 0.0, 8.0, "Screen emission strength")
    for m in (m_frame, m_back, m_screen):
        drive_bsdf(m, "Alpha", root, "shell_opacity")
    drive_bsdf(m_screen, "Emission Strength", root, "screen_glow")
    save("phone_exterior.blend")


# ---------------------------------------------------------------- car
def build_car():
    reset()
    c = new_collection("ASSET_Car")
    root = empty("CAR_Root", (0, 0, 0), c, size=1.0)
    m_paint = material("CAR_Mat_Paint", (0.92, 0.30, 0.12), metallic=0.2, rough=0.28)
    m_glass = material("CAR_Mat_Glass", (0.05, 0.09, 0.14), metallic=0.3, rough=0.08)
    m_tire = material("CAR_Mat_Tire", (0.03, 0.03, 0.035), rough=0.85)
    m_hub = material("CAR_Mat_Hub", (0.75, 0.77, 0.80), metallic=0.9, rough=0.3)
    m_trim = material("CAR_Mat_Trim", (0.10, 0.10, 0.12), rough=0.5)
    m_head = material("CAR_Mat_Headlight", (1.0, 0.95, 0.8), emission=(1.0, 0.92, 0.7), strength=2.0)
    m_tail = material("CAR_Mat_Taillight", (0.8, 0.05, 0.05), emission=(1.0, 0.05, 0.03), strength=1.0)

    box("CAR_Body", (4.10, 1.75, 0.58), (0, 0, 0.56), c, m_paint, root, bevel=0.14, seg=4)
    box("CAR_Hood", (1.15, 1.60, 0.10), (1.35, 0, 0.87), c, m_paint, root, bevel=0.045, seg=3)
    box("CAR_Cabin", (2.25, 1.58, 0.56), (-0.30, 0, 1.11), c, m_glass, root, bevel=0.07, seg=3, taper=(0.70, 0.86))
    box("CAR_Roof", (1.55, 1.34, 0.07), (-0.30, 0, 1.40), c, m_paint, root, bevel=0.03, seg=3)
    for sx, name in ((1, "Front"), (-1, "Rear")):
        box(f"CAR_Bumper{name}", (0.20, 1.70, 0.20), (sx * 2.02, 0, 0.36), c, m_trim, root, bevel=0.06)
    for sy, side in ((1, "L"), (-1, "R")):
        box(f"CAR_Headlight_{side}", (0.08, 0.34, 0.14), (2.035, sy * 0.58, 0.66), c, m_head, root, bevel=0.03)
        box(f"CAR_Taillight_{side}", (0.08, 0.34, 0.12), (-2.035, sy * 0.58, 0.68), c, m_tail, root, bevel=0.03)
        box(f"CAR_Mirror_{side}", (0.14, 0.10, 0.10), (0.62, sy * 0.92, 0.98), c, m_paint, root, bevel=0.03)
    wheels = []
    for sx, fr in ((1, "F"), (-1, "R")):
        for sy, side in ((1, "L"), (-1, "R")):
            w = cylinder(f"CAR_Wheel_{fr}{side}", 0.34, 0.26, (sx * 1.30, sy * 0.78, 0.34), c, m_tire, root, axis="Y", bevel=0.05)
            hub = cylinder(f"CAR_Hub_{fr}{side}", 0.20, 0.28, (0, 0, 0), c, m_hub, w, axis="Y", segments=24)
            for k in range(5):  # spokes make the spin readable
                a = 2 * math.pi * k / 5
                box(f"CAR_Spoke_{fr}{side}_{k + 1}", (0.05, 0.30, 0.16), (0.11 * math.cos(a), 0, 0.11 * math.sin(a)), c, m_trim, hub).rotation_euler = (0, -a + math.pi / 2, 0)
            wheels.append(w)

    empty("ANCHOR_FrontBumper", (2.12, 0, 0.40), c, root, 0.15)
    empty("ANCHOR_Dash", (0.55, 0, 0.98), c, root, 0.1)
    empty("ANCHOR_CabinCenter", (-0.30, 0, 1.05), c, root, 0.1)
    empty("CAM_Target_Car", (0, 0, 0.70), c, root, 0.3, "SPHERE")

    control(root, "wheel_rotation", 0.0, -100000.0, 100000.0, "Wheel spin in radians (positive = rolling toward +X)")
    control(root, "headlight_glow", 2.0, 0.0, 20.0, "Headlight emission strength")
    for w in wheels:
        w.rotation_mode = "XYZ"
        drive(w, "rotation_euler", root, "wheel_rotation", 1)
    drive_bsdf(m_head, "Emission Strength", root, "headlight_glow")
    save("car_stylized.blend")


# ---------------------------------------------------------------- road
def build_road():
    reset()
    c = new_collection("ASSET_Road")
    root = empty("ROAD_Root", (0, 0, 0), c, size=1.0)
    LANE_Y = 1.75  # left-hand traffic: the car travels toward +X in the +Y lane
    m_grass = material("ROAD_Mat_Grass", (0.33, 0.52, 0.30), rough=0.9)
    m_asphalt = material("ROAD_Mat_Asphalt", (0.10, 0.10, 0.115), rough=0.8)
    m_line = material("ROAD_Mat_Line", (0.92, 0.92, 0.88), rough=0.6)
    m_curb = material("ROAD_Mat_Curb", (0.62, 0.62, 0.60), rough=0.7)
    m_conc = material("ROAD_Mat_Concrete", (0.74, 0.73, 0.70), rough=0.75)
    m_red = material("ROAD_Mat_BarrierRed", (0.85, 0.12, 0.10), rough=0.5)
    m_trunk = material("ROAD_Mat_Trunk", (0.30, 0.20, 0.13), rough=0.9)
    m_leaf = material("ROAD_Mat_Leaf", (0.20, 0.48, 0.24), rough=0.85)
    m_pole = material("ROAD_Mat_Pole", (0.35, 0.37, 0.40), metallic=0.6, rough=0.45)
    m_lamp = material("ROAD_Mat_Lamp", (1.0, 0.95, 0.8), emission=(1.0, 0.9, 0.7), strength=1.5)

    box("ROAD_Ground", (90, 44, 0.10), (0, 0, -0.07), c, m_grass, root)
    box("ROAD_Asphalt", (90, 7.0, 0.02), (0, 0, -0.01), c, m_asphalt, root)
    for sy in (1, -1):
        box(f"ROAD_EdgeLine_{'L' if sy > 0 else 'R'}", (90, 0.12, 0.006), (0, sy * 3.25, 0.003), c, m_line, root)
        box(f"ROAD_Curb_{'L' if sy > 0 else 'R'}", (90, 0.30, 0.16), (0, sy * 3.65, 0.06), c, m_curb, root, bevel=0.03)
    for i in range(-8, 9):
        box(f"ROAD_LaneDash_{i + 9:02d}", (2.2, 0.14, 0.006), (i * 5.0, 0, 0.003), c, m_line, root)
    # barrier: three concrete blocks closing the +Y lane, with a red band (no text)
    for k, dy in enumerate((-1.15, 0.0, 1.15)):
        b = box(f"ROAD_Barrier_{k + 1}", (0.62, 1.08, 0.90), (14.0, LANE_Y + dy, 0.45), c, m_conc, root, bevel=0.05, taper=(0.45, 0.96))
        box(f"ROAD_BarrierBand_{k + 1}", (0.50, 1.10, 0.14), (0, 0, 0.12), c, m_red, b, bevel=0.02, taper=(0.86, 1.0))
    # scale props
    for k, (x, y) in enumerate([(-22, 6.5), (-9, -7.5), (3, 7.8), (16, -6.8), (24, 8.5), (-30, -9.0)]):
        t = cylinder(f"ROAD_TreeTrunk_{k + 1}", 0.22, 2.2, (x, y, 1.1), c, m_trunk, root, segments=10, radius2=0.14)
        icosphere(f"ROAD_TreeCrown_{k + 1}", 1.6, (0, 0, 2.2), c, m_leaf, t, scale=(1, 1, 1.15))
    for k, x in enumerate((-18, 0, 18)):
        p = cylinder(f"ROAD_LampPole_{k + 1}", 0.08, 6.0, (x, 4.3, 3.0), c, m_pole, root, segments=12)
        box(f"ROAD_LampArm_{k + 1}", (0.10, 1.8, 0.10), (0, -0.85, 2.95), c, m_pole, p)
        box(f"ROAD_LampHead_{k + 1}", (0.45, 0.30, 0.08), (0, -1.70, 2.88), c, m_lamp, p, bevel=0.02)

    empty("ANCHOR_CarStart", (-16.0, LANE_Y, 0), c, root, 0.5)
    empty("ANCHOR_CarStop", (14.0 - 0.31 - 2.12, LANE_Y, 0), c, root, 0.5)  # car root when its bumper anchor meets the barrier face
    empty("ANCHOR_BarrierFace", (14.0 - 0.31, LANE_Y, 0.45), c, root, 0.3)
    empty("CAM_Target_Road", (6.0, LANE_Y, 0.6), c, root, 0.5, "SPHERE")
    save("road_set.blend")


build_phone()
build_car()
build_road()
print("MASTER_ASSETS_DONE", bpy.app.version_string)
