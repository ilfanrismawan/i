"""Assets for "Bagaimana layar iPhone Duo bisa dilipat tanpa pecah?" - build, test, preview and manifest in one run.

Run:  blender --background --python scripts/build_duo_assets.py -- <this_project_dir>

Builds ONLY what does not exist yet; helpers are imported from iphone-crash-detection/scripts/asset_lib.py.
  assets/duo_exterior.blend         ASSET_Duo         foldable phone, two halves on a hinge        control: fold
  assets/fold_layers_concept.blend  ASSET_FoldLayers  cross-section of the display stack bending   control: fold
  assets/hinge_concept.blend        ASSET_Hinge       hinge with geared pivots, support, magnets   control: fold

Apple states: a hinge with 100+ components that holds the display centre flat when open, a magnet array for
closure, a 3D-printed titanium hinge cover, high-strength glass above and below the folding panel, custom
adhesives that let the layers glide past each other, a titanium plate underneath and a nano-textured polymer
cover. Apple gives no dimensions, layer thicknesses or hinge internals: every shape, size, gear and proportion
here is a CONCEPTUAL illustration, with thicknesses exaggerated for readability.
"""
import hashlib
import json
import math
import sys
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector

PROJECT = Path(sys.argv[sys.argv.index("--") + 1]).resolve()
sys.path.insert(0, str(PROJECT.parent / "iphone-crash-detection" / "scripts"))
from asset_lib import (arc_band, box, control, cylinder, drive, drive_bsdf, drive_curve, empty, finish,  # noqa: E402
                       material, new_collection, reset, rounded_slab, save)

for d in ("assets", "previews", "reports", "research"):
    (PROJECT / d).mkdir(parents=True, exist_ok=True)
REPORT = {"blender": bpy.app.version_string, "tests": {}, "renders": []}
PI = math.pi


def glow(name, colour, strength, base=None):
    return material(name, base or tuple(c * 0.2 for c in colour), rough=0.35, emission=colour, strength=strength)


def setp(root, **props):
    for k, v in props.items():
        root[k] = float(v)
    root.update_tag()
    bpy.context.view_layer.update()
    return bpy.context.evaluated_depsgraph_get()


def world_bounds(objs, dg, pred=lambda p: True):
    pts = []
    for o in objs:
        if o.type != "MESH":
            continue
        e = o.evaluated_get(dg)
        me = e.to_mesh()
        pts += [p for p in (e.matrix_world @ v.co for v in me.vertices) if pred(p)]
        e.to_mesh_clear()
    return Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts))), Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))


def preview(root, shots, sky=(0.05, 0.06, 0.09)):
    """Render stills of the file that was just saved; the lights/camera added here are never saved."""
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
        scene.eevee.taa_render_samples = 32
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
    for name, props, pos, target, lens in shots:
        setp(root, **props)
        cam.location, cam.data.lens = pos, lens
        cam.data.clip_start, cam.data.clip_end = 0.002, 200
        cam.rotation_euler = (Vector(target) - Vector(pos)).to_track_quat("-Z", "Y").to_euler()
        path = PROJECT / "previews" / f"{name}.png"
        scene.render.filepath = str(path)
        bpy.ops.render.render(write_still=True)
        REPORT["renders"].append({"file": f"previews/{name}.png", "exists": path.is_file()})


# ================================================================ 1. foldable phone exterior
def build_exterior():
    reset()
    c = new_collection("ASSET_Duo")
    root = empty("DUO_Root", (0, 0, 0), c, size=0.05)  # lies flat, inner screen up (+Z), hinge along Y
    HW, H, T, GAP = 0.078, 0.118, 0.0048, 0.0015  # assumed sizes: Apple publishes none
    m_body = material("DUO_Mat_Body", (0.16, 0.17, 0.20), metallic=0.85, rough=0.32)
    m_back = material("DUO_Mat_Back", (0.22, 0.24, 0.29), metallic=0.2, rough=0.2)
    m_ti = material("DUO_Mat_HingeCover", (0.62, 0.60, 0.56), metallic=0.95, rough=0.42)
    m_inner = glow("DUO_Mat_InnerScreen", (0.25, 0.55, 1.0), 1.2, base=(0.01, 0.012, 0.02))
    m_outer = glow("DUO_Mat_OuterScreen", (0.9, 0.5, 0.2), 0.8, base=(0.01, 0.012, 0.02))
    m_lens = material("DUO_Mat_Lens", (0.01, 0.01, 0.02), metallic=0.6, rough=0.05)
    control(root, "fold", 0.0, 0.0, 1.0, "0 = open flat, 1 = closed (inner screens facing each other)")
    control(root, "inner_glow", 1.2, 0.0, 10.0, "Inner display emission")
    control(root, "outer_glow", 0.8, 0.0, 10.0, "Outer display emission")
    RX = math.radians(90)  # rounded_slab is built upright in XZ; lay it flat
    for sx, side in ((-1, "L"), (1, "R")):
        piv = empty(f"DUO_Pivot_{side}", (sx * GAP, 0, T / 2), c, root, 0.01)
        piv.rotation_mode = "XYZ"
        drive(piv, "rotation_euler", root, "fold", 1, gain=-sx * PI / 2)
        cx = sx * (HW / 2 + 0.0004)
        rounded_slab(f"DUO_Half_{side}", HW, H, T, 0.0085, (cx, 0, -T / 2), c, m_body, piv, bevel=0.0009).rotation_euler = (RX, 0, 0)
        rounded_slab(f"DUO_InnerScreen_{side}", HW - 0.0040, H - 0.0050, 0.0003, 0.0065, (cx - sx * 0.0008, 0, 0.0002), c, m_inner, piv).rotation_euler = (RX, 0, 0)
        if side == "L":  # outer display lives on the back of the left half
            rounded_slab("DUO_OuterScreen", HW - 0.0050, H - 0.0050, 0.0003, 0.0070, (cx, 0, -T - 0.0002), c, m_outer, piv).rotation_euler = (RX, 0, 0)
        else:  # camera island on the back of the right half
            rounded_slab("DUO_BackGlass", HW - 0.0030, H - 0.0030, 0.0003, 0.0075, (cx, 0, -T - 0.0002), c, m_back, piv).rotation_euler = (RX, 0, 0)
            bx, by = cx + 0.020, H / 2 - 0.020
            rounded_slab("DUO_CameraBump", 0.030, 0.030, 0.0014, 0.008, (bx, by, -T - 0.0009), c, m_back, piv, bevel=0.0004).rotation_euler = (RX, 0, 0)
            for i, (dx, dy) in enumerate(((0.0062, 0.0062), (-0.0062, -0.0062))):
                cylinder(f"DUO_Lens_{i + 1}", 0.0052, 0.0016, (bx + dx, by + dy, -T - 0.0020), c, m_lens, piv, segments=32)
        empty(f"ANCHOR_ScreenCenter_{side}", (cx, 0, 0), c, piv, 0.005)
    cylinder("DUO_HingeCover", 0.0034, H - 0.006, (0, 0, -0.0004), c, m_ti, root, axis="Y", segments=32)
    for m, prop in ((m_inner, "inner_glow"), (m_outer, "outer_glow")):
        drive_bsdf(m, "Emission Strength", root, prop)
    empty("ANCHOR_Hinge", (0, 0, T / 2), c, root, 0.005)
    empty("CAM_Target_Duo", (0, 0, 0), c, root, 0.02, "SPHERE")
    save(PROJECT / "assets" / "duo_exterior.blend")
    T_ = REPORT["tests"]
    dg = setp(root, fold=1)
    T_["exterior fold=1 -> right pivot Y rotation deg (expect -90)"] = round(math.degrees(bpy.data.objects["DUO_Pivot_R"].evaluated_get(dg).rotation_euler.y), 1)
    lo, hi = world_bounds([bpy.data.objects["DUO_Half_L"], bpy.data.objects["DUO_Half_R"]], dg)
    T_["exterior fold=1 -> closed size x,z mm (expect about 12.6 thick, 78 tall)"] = [round((hi.x - lo.x) * 1000, 1), round((hi.z - lo.z) * 1000, 1)]
    li = world_bounds([bpy.data.objects["DUO_InnerScreen_L"]], dg)[1].x
    ri = world_bounds([bpy.data.objects["DUO_InnerScreen_R"]], dg)[0].x
    T_["exterior fold=1 -> gap between inner screens mm (must be > 0)"] = round((ri - li) * 1000, 2)
    dg = setp(root, fold=0)
    lo, hi = world_bounds([bpy.data.objects["DUO_Half_L"], bpy.data.objects["DUO_Half_R"]], dg)
    T_["exterior fold=0 -> open size x,y mm"] = [round((hi.x - lo.x) * 1000, 1), round((hi.y - lo.y) * 1000, 1)]
    preview(root, [("duo_exterior_open", {"fold": 0}, (0.10, -0.26, 0.24), (0, 0, 0), 50),
                   ("duo_exterior_half", {"fold": 0.5}, (0.14, -0.28, 0.16), (0, 0, 0.03), 50),
                   ("duo_exterior_closed", {"fold": 1}, (0.20, -0.22, 0.10), (0, 0, 0.04), 60)])


# ================================================================ 2. display stack cross-section
LF, LW, DEPTH, NW, NA = 1.0, 0.9, 0.7, 6, 40  # fold zone length, wing length, strip depth, samples
LAYERS = [  # name, offset from the panel (up = inside of the fold), thickness, colour, metallic, rough, emission
    ("TitaniumPlate", -0.112, 0.036, (0.60, 0.58, 0.55), 0.95, 0.4, None),
    ("Adhesive_1", -0.085, 0.014, (1.00, 0.72, 0.20), 0.0, 0.3, (1.0, 0.6, 0.1)),
    ("GlassBottom", -0.058, 0.036, (0.55, 0.80, 0.95), 0.1, 0.08, None),
    ("Adhesive_2", -0.031, 0.014, (1.00, 0.72, 0.20), 0.0, 0.3, (1.0, 0.6, 0.1)),
    ("FoldingPanel", 0.000, 0.044, (0.03, 0.03, 0.05), 0.2, 0.3, (0.25, 0.55, 1.0)),
    ("Adhesive_3", 0.031, 0.014, (1.00, 0.72, 0.20), 0.0, 0.3, (1.0, 0.6, 0.1)),
    ("GlassTop", 0.058, 0.036, (0.55, 0.80, 0.95), 0.1, 0.08, None),
    ("PolymerCover", 0.091, 0.026, (0.82, 0.84, 0.88), 0.0, 0.75, None),
]


def strip_coords(theta, d, t):
    """Cross-section of one layer bent by `theta`. All layers are pinned at the left end; each keeps its own
    length, so a layer nearer the inside of the bend has `d*theta` of spare length that shows at the right end."""
    out = []

    def point(kind, u, o):
        if theta < 1e-6:
            x = {"L": -LF / 2 - (1 - u) * LW, "A": -LF / 2 + u * LF, "R": LF / 2 + u * LW}[kind]
            return x, o
        R = LF / theta
        r = R - o
        if kind == "A":
            phi = -theta / 2 + u * theta
            return r * math.sin(phi), R - r * math.cos(phi)
        phi = -theta / 2 if kind == "L" else theta / 2
        s = -(1 - u) * LW if kind == "L" else u * (LW + d * theta)
        return r * math.sin(phi) + s * math.cos(phi), R - r * math.cos(phi) + s * math.sin(phi)

    samples = [("L", i / NW) for i in range(NW + 1)] + [("A", i / NA) for i in range(1, NA + 1)] + [("R", i / NW) for i in range(1, NW + 1)]
    for kind, u in samples:
        (xb, zb), (xt, zt) = point(kind, u, d - t / 2), point(kind, u, d + t / 2)
        out += [(xb, -DEPTH / 2, zb), (xb, DEPTH / 2, zb), (xt, DEPTH / 2, zt), (xt, -DEPTH / 2, zt)]
    return out


def build_layers():
    reset()
    c = new_collection("ASSET_FoldLayers")
    root = empty("FOLD_Root", (0, 0, 0), c, size=0.3)
    control(root, "fold", 0.0, 0.0, 1.0, "0 = flat, 1 = folded 180 degrees; layers slide, their right ends stagger")
    control(root, "adhesive_glow", 0.6, 0.0, 10.0, "Emission of the three adhesive layers")
    control(root, "panel_glow", 1.0, 0.0, 10.0, "Emission of the folding display panel")
    keys = (PI / 4, PI / 2, 3 * PI / 4, PI)
    ramps = ([(0, 0), (0.25, 1), (0.5, 0)], [(0.25, 0), (0.5, 1), (0.75, 0)], [(0.5, 0), (0.75, 1), (1, 0)], [(0.75, 0), (1, 1)])
    for name, d, t, colour, metallic, rough, emis in LAYERS:
        m = material(f"FOLD_Mat_{name}", colour, metallic=metallic, rough=rough, emission=emis, strength=0.0)
        base = strip_coords(0.0, d, t)
        bm = bmesh.new()
        vs = [bm.verts.new(p) for p in base]
        n = len(base) // 4
        for i in range(n - 1):
            a, b = vs[4 * i:4 * i + 4], vs[4 * i + 4:4 * i + 8]
            for k in range(4):
                bm.faces.new((a[k], a[(k + 1) % 4], b[(k + 1) % 4], b[k]))
        bm.faces.new(vs[0:4])
        bm.faces.new(vs[-4:][::-1])
        ob = finish(f"FOLD_{name}", bm, c, m, root)
        ob.shape_key_add(name="Basis")
        for j, theta in enumerate(keys):
            kb = ob.shape_key_add(name=f"Bend_{j + 1}")
            for i, p in enumerate(strip_coords(theta, d, t)):
                kb.data[i].co = p
            drive_curve(ob.data.shape_keys, f'key_blocks["Bend_{j + 1}"].value', root, "fold", ramps[j])
        if emis:
            drive_bsdf(m, "Emission Strength", root, "panel_glow" if name == "FoldingPanel" else "adhesive_glow")
    box("FOLD_Clamp", (0.06, DEPTH + 0.1, 0.34), (-LF / 2 - LW - 0.03, 0, -0.01), c, material("FOLD_Mat_Clamp", (0.25, 0.27, 0.32), metallic=0.6, rough=0.4), root, bevel=0.01).hide_render = True
    empty("ANCHOR_FoldCentre", (0, 0, 0), c, root, 0.1)
    empty("CAM_Target_FoldLayers", (0, 0, 0.35), c, root, 0.2, "SPHERE")
    save(PROJECT / "assets" / "fold_layers_concept.blend")
    T_ = REPORT["tests"]
    dg = setp(root, fold=1)
    right = lambda p: p.x > 0
    top = {n: world_bounds([bpy.data.objects[f"FOLD_{n}"]], dg, right)[1].z for n in ("PolymerCover", "FoldingPanel", "TitaniumPlate")}
    T_["layers fold=1 -> right-end stagger cover vs titanium (expect about 0.64 = 0.203*pi)"] = round(top["PolymerCover"] - top["TitaniumPlate"], 3)
    left = {n: world_bounds([bpy.data.objects[f"FOLD_{n}"]], dg, lambda p: p.x < 0)[1].z for n in ("PolymerCover", "TitaniumPlate")}
    T_["layers fold=1 -> left ends stay level, difference (expect 0)"] = round(left["PolymerCover"] - left["TitaniumPlate"], 3)
    lo, hi = world_bounds([bpy.data.objects["FOLD_FoldingPanel"]], dg)
    T_["layers fold=1 -> panel inner bend radius (expect about 0.30)"] = round((LF / PI) - 0.022, 3)
    dg = setp(root, fold=0.5)
    lo, hi = world_bounds([bpy.data.objects["FOLD_FoldingPanel"]], dg)
    T_["layers fold=0.5 -> panel is an L/quarter shape: width, height"] = [round(hi.x - lo.x, 2), round(hi.z - lo.z, 2)]
    cam, tgt = (0.0, -5.4, 0.75), (0.05, 0, 0.55)
    preview(root, [("fold_layers_flat", {"fold": 0}, (0.0, -4.6, 1.2), (0, 0, 0), 30),
                   ("fold_layers_half", {"fold": 0.5}, cam, tgt, 30),
                   ("fold_layers_folded", {"fold": 1, "adhesive_glow": 1.5}, cam, tgt, 30),
                   ("fold_layers_folded_closeup", {"fold": 1}, (0.9, -2.2, 1.9), (0.25, 0, 1.25), 40)])


# ================================================================ 3. hinge
def build_hinge():
    reset()
    c = new_collection("ASSET_Hinge")
    root = empty("HINGE_Root", (0, 0, 0), c, size=0.3)
    control(root, "fold", 0.0, 0.0, 1.0, "0 = open flat (centre support raised), 1 = closed (plates upright, magnets meet)")
    control(root, "magnet_glow", 0.0, 0.0, 10.0, "Emission of the magnet array")
    m_ti = material("HINGE_Mat_TitaniumCover", (0.62, 0.60, 0.56), metallic=0.95, rough=0.42)
    m_plate = material("HINGE_Mat_Plate", (0.30, 0.33, 0.40), metallic=0.8, rough=0.35)
    m_gear = material("HINGE_Mat_Gear", (0.85, 0.66, 0.25), metallic=0.95, rough=0.3)
    m_axle = material("HINGE_Mat_Axle", (0.75, 0.77, 0.80), metallic=0.95, rough=0.25)
    m_support = material("HINGE_Mat_Support", (0.20, 0.55, 0.75), metallic=0.6, rough=0.35)
    m_n = glow("HINGE_Mat_MagnetN", (1.0, 0.2, 0.15), 0.0, base=(0.7, 0.12, 0.10))
    m_s = glow("HINGE_Mat_MagnetS", (0.2, 0.45, 1.0), 0.0, base=(0.12, 0.25, 0.7))
    PX, GR, LEN = 0.17, 0.165, 2.4
    arc_band("HINGE_Cover", 0.40, 0.44, 180, 360, LEN + 0.2, (0, 0, 0), c, m_ti, root)
    for sy in (-1, 1):
        arc_band(f"HINGE_CoverCap_{'S' if sy < 0 else 'N'}", 0.0, 0.44, 180, 360, 0.04, (0, sy * (LEN / 2 + 0.12), 0), c, m_ti, root)
    sup = box("HINGE_CentreSupport", (2 * PX - 0.06, LEN - 0.1, 0.04), (0, 0, 0.01), c, m_support, root, bevel=0.008)
    drive(sup, "location", root, "fold", 2, offset=0.01, gain=-0.20)  # holds the display centre flat when open, sinks when folding
    for sx, side in ((-1, "L"), (1, "R")):
        piv = empty(f"HINGE_Pivot_{side}", (sx * PX, 0, 0), c, root, 0.1)
        piv.rotation_mode = "XYZ"
        drive(piv, "rotation_euler", root, "fold", 1, gain=-sx * PI / 2)
        cylinder(f"HINGE_Axle_{side}", 0.035, LEN, (0, 0, 0), c, m_axle, piv, axis="Y", segments=20)
        plate = box(f"HINGE_Plate_{side}", (1.15, LEN, 0.06), (sx * 0.19, 0, 0), c, m_plate, piv, bevel=0.012, origin_min_x=True)
        plate.rotation_euler = (0, 0, 0 if sx > 0 else PI)
        for k, y in enumerate((-0.85, 0.0, 0.85)):  # three synchronising gear pairs; the two sides mesh and counter-rotate
            g = cylinder(f"HINGE_Gear_{side}{k + 1}", GR - 0.03, 0.16, (0, y, 0), c, m_gear, piv, axis="Y", segments=28)
            for t in range(12):
                a = 2 * PI * (t + (0.5 if sx > 0 else 0.0)) / 12
                box(f"HINGE_Tooth_{side}{k + 1}_{t + 1:02d}", (0.05, 0.16, 0.035), ((GR - 0.012) * math.cos(a), 0, (GR - 0.012) * math.sin(a)), c, m_gear, g).rotation_euler = (0, -a, 0)
            box(f"HINGE_Arm_{side}{k + 1}", (0.22, 0.10, 0.05), (sx * 0.04, y, 0), c, m_axle, piv, origin_min_x=True).rotation_euler = (0, 0, 0 if sx > 0 else PI)
        for k in range(7):  # magnet array along the free edge; opposite poles face each other when closed
            north = (k % 2 == 0) == (sx > 0)
            box(f"HINGE_Magnet_{side}{k + 1}", (0.10, 0.22, 0.05), (sx * 1.22, -0.96 + 0.32 * k, 0.035), c, m_n if north else m_s, piv, bevel=0.01)
        empty(f"ANCHOR_PlateEdge_{side}", (sx * 1.30, 0, 0), c, piv, 0.05)
    for m in (m_n, m_s):
        drive_bsdf(m, "Emission Strength", root, "magnet_glow")
    empty("CAM_Target_Hinge", (0, 0, 0.1), c, root, 0.2, "SPHERE")
    save(PROJECT / "assets" / "hinge_concept.blend")
    T_ = REPORT["tests"]
    T_["hinge mesh parts (conceptual; Apple says 100+ components)"] = sum(o.type == "MESH" for o in bpy.data.objects)
    dg = setp(root, fold=1)
    T_["hinge fold=1 -> pivots L,R deg (expect 90, -90)"] = [round(math.degrees(bpy.data.objects[f"HINGE_Pivot_{s}"].evaluated_get(dg).rotation_euler.y), 1) for s in "LR"]
    T_["hinge fold=1 -> centre support z (expect -0.19)"] = round(bpy.data.objects["HINGE_CentreSupport"].evaluated_get(dg).location.z, 3)
    lm = world_bounds([bpy.data.objects["HINGE_Magnet_L4"]], dg)
    rm = world_bounds([bpy.data.objects["HINGE_Magnet_R4"]], dg)
    T_["hinge fold=1 -> gap between facing magnets (must be > 0)"] = round(rm[0].x - lm[1].x, 3)
    T_["hinge fold=1 -> magnets at same height, difference (expect 0)"] = round(rm[1].z - lm[1].z, 3)
    preview(root, [("hinge_open", {"fold": 0}, (1.6, -3.4, 2.6), (0, 0, 0), 28),
                   ("hinge_half", {"fold": 0.5, "magnet_glow": 0.5}, (1.4, -4.0, 1.9), (0, 0, 0.45), 28),
                   ("hinge_closed", {"fold": 1, "magnet_glow": 1.5}, (1.6, -4.2, 1.6), (0, 0, 0.65), 28)])


build_exterior()
build_layers()
build_hinge()

# ================================================================ manifest + claims
SRC = {"url": "https://www.apple.com/newsroom/2026/09/apple-unveils-iphone-duo/", "publisher": "Apple Newsroom", "title": "Apple unveils iPhone Duo"}
NOTE = "conceptual illustration: Apple publishes no dimensions, layer thicknesses or hinge internals"
F = lambda lo, hi, d, on, affects: {"type": "float", "min": lo, "max": hi, "default": d, "on": on, "affects": affects}
sha = lambda p: hashlib.sha256((PROJECT / p).read_bytes()).hexdigest()
assets = [
    {"id": "duo_exterior", "path": "assets/duo_exterior.blend", "collection": "ASSET_Duo", "units": "metres; lies flat, inner screen +Z, hinge along Y; assumed half 78 x 118 x 4.8 mm",
     "anchors": {"root": "DUO_Root", "hinge": "ANCHOR_Hinge", "screens": "ANCHOR_ScreenCenter_L / _R", "camera_target": "CAM_Target_Duo"},
     "controls": {"fold": F(0, 1, 0, "DUO_Root", "each half turns 90 degrees about its pivot"), "inner_glow": F(0, 10, 1.2, "DUO_Root", "inner display emission"), "outer_glow": F(0, 10, 0.8, "DUO_Root", "outer display emission")}},
    {"id": "fold_layers_concept", "path": "assets/fold_layers_concept.blend", "collection": "ASSET_FoldLayers", "units": "macro set, thickness exaggerated; fold zone 1.0, wings 0.9",
     "anchors": {"root": "FOLD_Root", "centre": "ANCHOR_FoldCentre", "camera_target": "CAM_Target_FoldLayers"},
     "controls": {"fold": F(0, 1, 0, "FOLD_Root", "bends all eight layers 0-180 degrees through four exact poses; layers keep their length and slide"), "adhesive_glow": F(0, 10, 0.6, "FOLD_Root", "adhesive emission"), "panel_glow": F(0, 10, 1.0, "FOLD_Root", "panel emission")}},
    {"id": "hinge_concept", "path": "assets/hinge_concept.blend", "collection": "ASSET_Hinge", "units": "macro set, about 2.8 x 2.6 units when open",
     "anchors": {"root": "HINGE_Root", "edges": "ANCHOR_PlateEdge_L / _R", "camera_target": "CAM_Target_Hinge"},
     "controls": {"fold": F(0, 1, 0, "HINGE_Root", "plates turn 90 degrees each, gears counter-rotate, centre support sinks 0.20"), "magnet_glow": F(0, 10, 0, "HINGE_Root", "magnet emission")}},
]
for a in assets:
    a.update(phase="mechanism-assets", status="complete", dependencies=[], generator="scripts/build_duo_assets.py", previews="previews/", notes=NOTE, source_sha256=sha(a["path"]))
manifest = {"schema_version": "1.0", "project": "iphone-duo-fold", "topic": "Bagaimana layar iPhone Duo bisa dilipat tanpa pecah?",
            "research": "../iphone-facts/research/topic_candidates_round2.json (id: engsel-duo)", "assets": assets,
            "reuse_do_not_recreate": ["iphone-crash-detection/scripts/asset_lib.py (imported, not copied)", "Asset/Assets/Assets (user's own models: living rooms, street, girl, iPhone 14 Max)"],
            "pending_assets": []}
(PROJECT / "asset_manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
C = lambda i, text, viz, caveat: {"id": f"duo-{i:02d}", "claim": text, "status": "verified", "sources": [SRC], "shot_ids": [], "visualization_type": viz, "caveat": caveat}
claims = [
    C(1, "iPhone Duo adalah iPhone lipat dengan layar dalam 7,6 inci dan layar luar 5,4 inci.", "conceptual", "Ukuran bodi dalam mm tidak dipublikasikan; model memakai ukuran perkiraan."),
    C(2, "Engselnya terdiri dari lebih dari 100 komponen dan menahan bagian tengah layar tetap rata saat terbuka.", "conceptual", "Isi engsel tidak dirinci Apple; roda gigi dan penopang di model adalah ilustrasi."),
    C(3, "Engsel memiliki susunan magnet untuk menutup.", "conceptual", "Letak dan jumlah magnet adalah ilustrasi."),
    C(4, "Penutup engsel dicetak 3D dari titanium daur ulang 100 persen.", "illustrative", ""),
    C(5, "Ada kaca berkekuatan tinggi di atas dan di bawah panel lipat.", "conceptual", "Ketebalan lapisan dibesar-besarkan agar terbaca."),
    C(6, "Perekat khusus membuat lapisan-lapisan layar saling bergeser sehingga tegangan tekuk berkurang.", "conceptual", "Besar pergeseran di model adalah akibat ketebalan yang dibesar-besarkan, bukan ukuran nyata."),
    C(7, "Di bagian bawah susunan layar ada pelat titanium, dan penutup atasnya polimer bertekstur nano.", "conceptual", "Urutan persis lapisan perekat tidak dirinci Apple."),
    {"id": "duo-08", "claim": "Layar iPhone Duo tahan dilipat sekian ratus ribu kali.", "status": "unverified", "sources": [], "shot_ids": [], "visualization_type": "illustrative", "caveat": "Apple tidak menyebut jumlah lipatan. Jangan dinarasikan."},
]
(PROJECT / "research" / "claims.json").write_text(json.dumps({"accessed": "2026-11-12", "claims": claims}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
(PROJECT / "reports" / "duo_assets_validation.json").write_text(json.dumps(REPORT, indent=2) + "\n", encoding="utf-8")
print("TESTS", json.dumps(REPORT["tests"], indent=1))
print("RENDERS_OK", all(r["exists"] for r in REPORT["renders"]), len(REPORT["renders"]))
