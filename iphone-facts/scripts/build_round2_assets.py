"""Round-2 topic assets: build, test, preview and write manifests in one run. Existing assets are not rebuilt.

Run:  blender --background --python iphone-facts/scripts/build_round2_assets.py -- <repo_root>

  iphone-quad-pixel/assets/sensor_quadpixel_concept.blend   ASSET_QuadPixel      48 MP sensor: four pixels act as one
  iphone-camera-control/assets/camera_control_concept.blend ASSET_CameraControl  one button, three sensing parts
  iphone-printed-port/assets/printed_port_concept.blend     ASSET_PrintedPort    titanium port printed layer by layer
  iphone-vapor-chamber/assets/heat_flow_schematic.blend     ASSET_FX_HeatFlow    arrows from hot to cool (drawing aid)

All four are CONCEPTUAL illustrations at exaggerated macro scale. Apple publishes what these parts do,
not their internal geometry; see each manifest's notes for exactly what is sourced.
"""
import hashlib
import json
import math
import sys
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector

REPO = Path(sys.argv[sys.argv.index("--") + 1]).resolve()
sys.path.insert(0, str(REPO / "iphone-crash-detection" / "scripts"))
from asset_lib import (box, clamp, control, cylinder, disc_membrane, drive, drive_bsdf, drive_curve, empty, finish,  # noqa: E402
                       material, new_collection, prism, reset, save)

REPORT = {"blender": bpy.app.version_string, "tests": {}, "renders": []}
T_ = REPORT["tests"]
PI = math.pi
F = lambda lo, hi, d, on, affects: {"type": "float", "min": lo, "max": hi, "default": d, "on": on, "affects": affects}


def glow(name, colour, strength=0.0, base=None, rough=0.35, metallic=0.0):
    return material(name, base or tuple(c * 0.35 for c in colour), metallic=metallic, rough=rough, emission=colour, strength=strength)


def setp(root, **props):
    for k, v in props.items():
        root[k] = float(v)
    root.update_tag()
    bpy.context.view_layer.update()
    return bpy.context.evaluated_depsgraph_get()


def E(name, dg):
    return bpy.data.objects[name].evaluated_get(dg)


def key_value(obj_name, key, dg):
    return round(E(obj_name, dg).data.shape_keys.key_blocks[key].value, 3)


def project(name):
    p = REPO / name
    for d in ("assets", "previews"):
        (p / d).mkdir(parents=True, exist_ok=True)
    return p


def preview(proj, root, shots, sky=(0.05, 0.06, 0.09)):
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
        cam.rotation_euler = (Vector(target) - Vector(pos)).to_track_quat("-Z", "Y").to_euler()
        path = proj / "previews" / f"{name}.png"
        scene.render.filepath = str(path)
        bpy.ops.render.render(write_still=True)
        REPORT["renders"].append({"file": f"{proj.name}/previews/{name}.png", "exists": path.is_file()})


def write_manifest(proj, topic, research_id, sourced, entries, extra_reuse=()):
    mf = proj / "asset_manifest.json"
    data = json.loads(mf.read_text(encoding="utf-8")) if mf.is_file() else {"schema_version": "1.0", "project": proj.name, "assets": []}
    data.setdefault("topic", topic)
    data.setdefault("research", f"../iphone-facts/research/topic_candidates_round2.json (id: {research_id})")
    data["sourced_facts"] = sourced
    for e in entries:
        e.update(phase="mechanism-assets", status="complete", dependencies=e.get("dependencies", []), generator="../iphone-facts/scripts/build_round2_assets.py",
                 previews="previews/", source_sha256=hashlib.sha256((proj / e["path"]).read_bytes()).hexdigest())
    ids = {e["id"] for e in entries}
    data["assets"] = [a for a in data["assets"] if a["id"] not in ids] + entries
    data["pending_assets"] = [p for p in data.get("pending_assets", []) if p not in ids]
    reuse = data.setdefault("reuse_do_not_recreate", [])
    for r in ("iphone-crash-detection/scripts/asset_lib.py (imported, not copied)", "iphone-crash-detection/assets/phone_exterior.blend", *extra_reuse):
        if r not in reuse:
            reuse.append(r)
    mf.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


# ================================================================ 1. quad-pixel sensor
def build_quad_pixel():
    proj = project("iphone-quad-pixel")
    reset()
    c = new_collection("ASSET_QuadPixel")
    root = empty("QUAD_Root", (0, 0, 0), c, size=0.5)
    control(root, "merge", 0.0, 0.0, 1.0, "0 = 64 separate pixels, 1 = each group of four closes up and works as one big pixel")
    control(root, "pixel_glow", 0.4, 0.0, 10.0, "Emission of the colour filters")
    control(root, "quad_glow", 0.0, 0.0, 10.0, "Emission of the merged-pixel caps")
    control(root, "crop_glow", 0.0, 0.0, 10.0, "Emission of the frame around the middle quarter (2x Telephoto crop)")
    N, PITCH, SIZE, SHIFT = 8, 0.50, 0.42, 0.04
    colours = {"G": (0.15, 0.95, 0.30), "R": (1.0, 0.18, 0.12), "B": (0.15, 0.40, 1.0)}
    m_filter = {k: glow(f"QUAD_Mat_Filter_{k}", v, 0.4) for k, v in colours.items()}
    m_cap = {k: glow(f"QUAD_Mat_Cap_{k}", v, 0.0, base=tuple(min(1, x + 0.25) for x in v)) for k, v in colours.items()}
    m_diode = material("QUAD_Mat_Photodiode", (0.07, 0.08, 0.12), metallic=0.4, rough=0.4)
    m_lens = material("QUAD_Mat_Microlens", (0.85, 0.92, 1.0), metallic=0.1, rough=0.05)
    m_sub = material("QUAD_Mat_Substrate", (0.05, 0.10, 0.09), metallic=0.3, rough=0.5)
    m_crop = glow("QUAD_Mat_CropFrame", (1.0, 1.0, 1.0), 0.0, base=(0.9, 0.9, 0.9))
    half = N * PITCH / 2
    box("QUAD_Substrate", (N * PITCH + 0.5, N * PITCH + 0.5, 0.12), (0, 0, -0.06), c, m_sub, root, bevel=0.03)
    for i in range(N):
        for j in range(N):
            x, y = -half + PITCH * (i + 0.5), -half + PITCH * (j + 0.5)
            key = [["G", "R"], ["B", "G"]][(j // 2) % 2][(i // 2) % 2]  # quad-Bayer: each 2x2 block shares one colour
            px = empty(f"QUAD_Pixel_{i + 1}_{j + 1}", (x, y, 0), c, root, 0.05)
            drive(px, "location", root, "merge", 0, offset=x, gain=SHIFT if i % 2 == 0 else -SHIFT)
            drive(px, "location", root, "merge", 1, offset=y, gain=SHIFT if j % 2 == 0 else -SHIFT)
            box(f"QUAD_Diode_{i + 1}_{j + 1}", (SIZE, SIZE, 0.14), (0, 0, 0.07), c, m_diode, px)
            box(f"QUAD_Filter_{i + 1}_{j + 1}", (SIZE, SIZE, 0.05), (0, 0, 0.165), c, m_filter[key], px)
            cylinder(f"QUAD_Lens_{i + 1}_{j + 1}", 0.19, 0.05, (0, 0, 0.215), c, m_lens, px, segments=20, bevel=0.024)
    for qi in range(N // 2):
        for qj in range(N // 2):
            key = [["G", "R"], ["B", "G"]][qj % 2][qi % 2]
            cap = box(f"QUAD_MergedCap_{qi + 1}_{qj + 1}", (0.90, 0.90, 0.03), (-half + PITCH * (2 * qi + 1), -half + PITCH * (2 * qj + 1), 0.262), c, m_cap[key], root, bevel=0.012)
            for axis in range(3):
                clamp(drive(cap, "scale", root, "merge", axis, offset=-1.0, gain=2.0), 0.0, 1.0)  # appears during the second half of the merge
    q = half / 2
    for name, size, loc in (("N", (2 * q + 0.06, 0.06, 0.04), (0, q, 0.31)), ("S", (2 * q + 0.06, 0.06, 0.04), (0, -q, 0.31)),
                            ("E", (0.06, 2 * q + 0.06, 0.04), (q, 0, 0.31)), ("W", (0.06, 2 * q + 0.06, 0.04), (-q, 0, 0.31))):
        box(f"QUAD_CropFrame_{name}", size, loc, c, m_crop, root)
    for m in m_filter.values():
        drive_bsdf(m, "Emission Strength", root, "pixel_glow")
    for m in m_cap.values():
        drive_bsdf(m, "Emission Strength", root, "quad_glow")
    drive_bsdf(m_crop, "Emission Strength", root, "crop_glow")
    empty("CAM_Target_QuadPixel", (0, 0, 0.15), c, root, 0.2, "SPHERE")
    save(proj / "assets" / "sensor_quadpixel_concept.blend")
    x0, y0 = E("QUAD_Pixel_1_1", bpy.context.evaluated_depsgraph_get()).location.x, bpy.data.objects["QUAD_Pixel_1_1"].location.y
    dg = setp(root, merge=1)
    T_["quad merge=1 -> pixel 1,1 moved x,y (expect 0.04, 0.04)"] = [round(E("QUAD_Pixel_1_1", dg).location.x - x0, 3), round(E("QUAD_Pixel_1_1", dg).location.y - y0, 3)]
    T_["quad merge=1 -> merged cap scale (expect 1)"] = round(E("QUAD_MergedCap_1_1", dg).scale.x, 3)
    dg = setp(root, merge=0.4)
    T_["quad merge=0.4 -> merged cap scale (expect 0)"] = round(E("QUAD_MergedCap_1_1", dg).scale.x, 3)
    T_["quad pixels / merged caps (expect 64 / 16)"] = [sum(o.name.startswith("QUAD_Pixel_") for o in bpy.data.objects), sum(o.name.startswith("QUAD_MergedCap_") for o in bpy.data.objects)]
    cam = (2.6, -3.6, 4.0)
    preview(proj, root, [("quad_pixel_separate", {"merge": 0, "quad_glow": 0, "crop_glow": 0}, cam, (0, 0, 0), 30),
                         ("quad_pixel_merged", {"merge": 1, "quad_glow": 0.8}, cam, (0, 0, 0), 30),
                         ("quad_pixel_centre_crop", {"merge": 0, "quad_glow": 0, "crop_glow": 3}, (0.0, -0.4, 6.5), (0, 0, 0), 30)])
    write_manifest(proj, "Kamera 48 MP iPhone biasanya cuma memotret 12 MP. Kenapa?", "empat-jadi-satu",
                   "Apple (iPhone 14 Pro): the quad-pixel sensor combines every four pixels into one large quad pixel equivalent to 2.44 um for most photos (12 MP); ProRAW uses 48 MP; the 2x Telephoto uses the middle 12 megapixels.",
                   [{"id": "sensor_quadpixel_concept", "path": "assets/sensor_quadpixel_concept.blend", "collection": "ASSET_QuadPixel",
                     "units": "macro set, 8 x 8 pixels at 0.5 pitch; a real sensor has 48 million, this shows a tiny patch",
                     "anchors": {"root": "QUAD_Root", "pixels": "QUAD_Pixel_<col>_<row>", "camera_target": "CAM_Target_QuadPixel"},
                     "controls": {"merge": F(0, 1, 0, "QUAD_Root", "pixels close up in fours; merged caps appear in the second half"),
                                  "pixel_glow": F(0, 10, 0.4, "QUAD_Root", "colour filter emission"), "quad_glow": F(0, 10, 0, "QUAD_Root", "merged cap emission"),
                                  "crop_glow": F(0, 10, 0, "QUAD_Root", "frame around the middle quarter")},
                     "notes": "Conceptual. Pixels do not physically move in a real sensor: the sliding together is a metaphor for reading four as one. Colour layout and microlenses are a generic quad-Bayer illustration."}])


# ================================================================ 2. Camera Control button
def build_camera_control():
    proj = project("iphone-camera-control")
    reset()
    c = new_collection("ASSET_CameraControl")
    root = empty("CC_Root", (0, 0, 0), c, size=0.5)  # cross-section seen from -Y; button length along X
    control(root, "press", 0.0, 0.0, 1.0, "0-0.4 = light press (force sensor flexes), 0.4-1 = full click (switch dome snaps)")
    control(root, "slide", 0.0, -1.0, 1.0, "Finger position along the button")
    control(root, "finger_visible", 0.0, 0.0, 1.0, "Shows the finger marker")
    control(root, "touch_glow", 0.0, 0.0, 10.0, "Emission of the capacitive (touch) layer")
    control(root, "force_glow", 0.0, 0.0, 10.0, "Emission of the force sensor")
    control(root, "switch_glow", 0.0, 0.0, 10.0, "Emission of the tactile switch dome")
    m_frame = material("CC_Mat_Frame", (0.55, 0.57, 0.62), metallic=0.9, rough=0.35)
    m_cap = material("CC_Mat_Cap", (0.06, 0.07, 0.10), metallic=0.3, rough=0.12)
    m_touch = glow("CC_Mat_Capacitive", (1.0, 0.75, 0.2), 0.0, metallic=0.8)
    m_force = glow("CC_Mat_ForceSensor", (0.2, 0.9, 1.0), 0.0, metallic=0.6)
    m_gauge = material("CC_Mat_StrainGauge", (0.85, 0.5, 0.25), metallic=0.9, rough=0.35)
    m_dome = glow("CC_Mat_SwitchDome", (1.0, 0.35, 0.75), 0.0, metallic=0.8)
    m_base = material("CC_Mat_SwitchBase", (0.12, 0.13, 0.16), rough=0.5)
    m_finger = material("CC_Mat_Finger", (0.95, 0.75, 0.62), rough=0.6)
    D = 0.9
    box("CC_Frame_L", (1.2, D + 0.3, 0.80), (-1.85, 0, 0.40), c, m_frame, root, bevel=0.04)
    box("CC_Frame_R", (1.2, D + 0.3, 0.80), (1.85, 0, 0.40), c, m_frame, root, bevel=0.04)
    box("CC_Frame_Floor", (4.9, D + 0.3, 0.10), (0, 0, -0.05), c, m_frame, root)
    box("CC_Frame_Back", (2.5, 0.10, 0.80), (0, D / 2 + 0.10, 0.40), c, m_frame, root)
    press_cap = [(0, 0.0), (0.4, -0.03), (1, -0.13)]
    cap = box("CC_Cap", (2.36, D, 0.16), (0, 0, 0.70), c, m_cap, root, bevel=0.05, seg=4)
    drive_curve(cap, "location", root, "press", [(t, 0.70 + v) for t, v in press_cap], 2)
    box("CC_CapacitiveLayer", (2.16, D - 0.1, 0.025), (0, 0, -0.095), c, m_touch, cap)
    box("CC_Plunger_Upper", (0.22, 0.4, 0.09), (0, 0, -0.15), c, m_frame, cap)
    finger = cylinder("CC_FingerMarker", 0.26, 0.16, (0, 0, 0.17), c, m_finger, cap, segments=32, bevel=0.07)
    drive(finger, "location", root, "slide", 0, gain=0.85)
    for axis in range(3):
        drive(finger, "scale", root, "finger_visible", axis)
    carrier = empty("CC_ForceCarrier", (0, 0, 0), c, root, 0.2)  # the whole force-sensor stage travels during the click phase
    drive_curve(carrier, "location", root, "press", [(0, 0), (0.4, 0), (1, -0.10)], 2)
    L, n = 2.3, 24
    bm = bmesh.new()
    vs = []
    for i in range(n + 1):
        x = -L / 2 + L * i / n
        vs += [bm.verts.new((x, -0.3, -0.02)), bm.verts.new((x, 0.3, -0.02)), bm.verts.new((x, 0.3, 0.02)), bm.verts.new((x, -0.3, 0.02))]
    for i in range(n):
        a, b = vs[4 * i:4 * i + 4], vs[4 * i + 4:4 * i + 8]
        for k in range(4):
            bm.faces.new((a[k], a[(k + 1) % 4], b[(k + 1) % 4], b[k]))
    bm.faces.new(vs[0:4])
    bm.faces.new(vs[-4:][::-1])
    beam = finish("CC_ForceBeam", bm, c, m_force, carrier, (0, 0, 0.485))
    beam.shape_key_add(name="Basis")
    sag = beam.shape_key_add(name="Flex")
    for i, v in enumerate(beam.data.vertices):
        sag.data[i].co = (v.co.x, v.co.y, v.co.z - 0.035 * (1 - (2 * v.co.x / L) ** 2))
    drive_curve(beam.data.shape_keys, 'key_blocks["Flex"].value', root, "press", [(0, 0), (0.4, 1), (1, 1)])
    for sx in (-1, 1):
        box(f"CC_BeamPost_{'L' if sx < 0 else 'R'}", (0.12, 0.6, 0.20), (sx * 1.09, 0, 0.365), c, m_frame, carrier)
        for k in range(3):
            box(f"CC_StrainGauge_{'L' if sx < 0 else 'R'}{k + 1}", (0.30, 0.04, 0.012), (sx * 0.62, -0.14 + 0.14 * k, 0.511), c, m_gauge, carrier)
    box("CC_Plunger_Lower", (0.18, 0.3, 0.13), (0, 0, 0.385), c, m_frame, carrier)
    box("CC_SwitchBase", (0.9, 0.7, 0.12), (0, 0, 0.06), c, m_base, root, bevel=0.02)
    dome = disc_membrane("CC_SwitchDome", 0.34, (0, 0, 0.125), c, m_dome, root, rings=10, segments=40)
    for v in dome.data.vertices:
        v.co.z = 0.19 * (1 - (math.hypot(v.co.x, v.co.y) / 0.34) ** 2)
    dome.modifiers.new("Thickness", "SOLIDIFY").thickness = 0.02
    dome.shape_key_add(name="Basis")
    snap = dome.shape_key_add(name="Snap")
    for i, v in enumerate(dome.data.vertices):
        snap.data[i].co = (v.co.x, v.co.y, 0.03 * (1 - (math.hypot(v.co.x, v.co.y) / 0.34) ** 2))
    drive_curve(dome.data.shape_keys, 'key_blocks["Snap"].value', root, "press", [(0, 0), (0.55, 0), (0.7, 1), (1, 1)])  # sudden: this is the click
    for m, p in ((m_touch, "touch_glow"), (m_force, "force_glow"), (m_dome, "switch_glow")):
        drive_bsdf(m, "Emission Strength", root, p)
    empty("ANCHOR_CapTop", (0, 0, 0.08), c, cap, 0.1)
    empty("CAM_Target_CameraControl", (0, 0, 0.38), c, root, 0.2, "SPHERE")
    save(proj / "assets" / "camera_control_concept.blend")
    dg = setp(root, press=0.4)
    T_["button press=0.4 -> cap z, beam flex, dome snap (expect 0.67, 1, 0)"] = [round(E("CC_Cap", dg).location.z, 3), key_value("CC_ForceBeam", "Flex", dg), key_value("CC_SwitchDome", "Snap", dg)]
    dg = setp(root, press=1)
    T_["button press=1 -> cap z, carrier z, dome snap (expect 0.57, -0.1, 1)"] = [round(E("CC_Cap", dg).location.z, 3), round(E("CC_ForceCarrier", dg).location.z, 3), key_value("CC_SwitchDome", "Snap", dg)]
    dg = setp(root, press=0, slide=1, finger_visible=1)
    T_["button slide=1 -> finger x (expect 0.85)"] = round(E("CC_FingerMarker", dg).location.x, 3)
    cam, tgt = (0.0, -5.0, 1.5), (0, 0, 0.38)
    preview(proj, root, [("camera_control_rest", {"press": 0, "finger_visible": 0, "slide": 0}, cam, tgt, 32),
                         ("camera_control_light_press", {"press": 0.4, "force_glow": 2.0, "finger_visible": 1}, cam, tgt, 32),
                         ("camera_control_full_click", {"press": 1, "force_glow": 0.5, "switch_glow": 2.5}, cam, tgt, 32),
                         ("camera_control_slide", {"press": 0, "slide": 0.8, "touch_glow": 2.5, "force_glow": 0, "switch_glow": 0}, (1.8, -4.0, 2.6), tgt, 32)])
    write_manifest(proj, "Satu tombol iPhone 16 punya tiga alat perasa", "camera-control",
                   "Apple (iPhone 16): Camera Control has a tactile switch that powers the click, a high-precision force sensor that enables the light press, and a capacitive sensor for touch interactions (sliding).",
                   [{"id": "camera_control_concept", "path": "assets/camera_control_concept.blend", "collection": "ASSET_CameraControl",
                     "units": "macro set, about 4.9 wide; cross-section meant to be seen from -Y",
                     "anchors": {"root": "CC_Root", "cap_top": "ANCHOR_CapTop", "camera_target": "CAM_Target_CameraControl"},
                     "controls": {"press": F(0, 1, 0, "CC_Root", "cap travel in two stages; beam flexes by 0.4, dome snaps between 0.55 and 0.7"),
                                  "slide": F(-1, 1, 0, "CC_Root", "finger marker +-0.85 along the cap"), "finger_visible": F(0, 1, 0, "CC_Root", "finger marker scale"),
                                  "touch_glow": F(0, 10, 0, "CC_Root", "capacitive layer"), "force_glow": F(0, 10, 0, "CC_Root", "force beam"), "switch_glow": F(0, 10, 0, "CC_Root", "switch dome")},
                     "notes": "Conceptual. Apple names the three parts and what each enables; their shapes, stacking order and travel distances here are an illustration. Sapphire crystal is mentioned by Apple only for its cases, so the cap is not labelled sapphire."}])


# ================================================================ 3. 3D-printed titanium port
def stadium(a, r, z, n=14):
    pts = []
    for cx, start in ((a, -90), (-a, 90)):
        for i in range(n + 1):
            ang = math.radians(start + 180 * i / n)
            pts.append((cx + r * math.cos(ang), r * math.sin(ang), z))
    return pts


def build_printed_port():
    proj = project("iphone-printed-port")
    reset()
    c = new_collection("ASSET_PrintedPort")
    root = empty("PRINT_Root", (0, 0, 0), c, size=0.5)
    control(root, "print_progress", 0.0, 0.0, 1.0, "Reveals the 30 printed layers of the port from bottom to top")
    control(root, "powder_level", 0.0, 0.0, 1.0, "Raises the powder bed (and the recoater) to the height of the part")
    control(root, "recoat", 0.0, -1.0, 1.0, "Sweeps the recoater blade across the bed")
    control(root, "laser_glow", 0.0, 0.0, 20.0, "Emission of the six laser beams and their spots")
    control(root, "part_glow", 0.0, 0.0, 10.0, "Emission of the freshly fused top layers")
    m_ti = glow("PRINT_Mat_Titanium", (1.0, 0.55, 0.2), 0.0, base=(0.66, 0.64, 0.60), metallic=0.95, rough=0.38)
    m_powder = material("PRINT_Mat_Powder", (0.42, 0.42, 0.44), metallic=0.3, rough=0.95)
    m_machine = material("PRINT_Mat_Machine", (0.16, 0.18, 0.22), metallic=0.5, rough=0.45)
    m_plate = material("PRINT_Mat_BuildPlate", (0.45, 0.47, 0.52), metallic=0.9, rough=0.3)
    m_laser = glow("PRINT_Mat_Laser", (1.0, 0.25, 0.1), 0.0, base=(1.0, 0.5, 0.4))
    NL, LH = 30, 0.02
    H = NL * LH
    A, RO, RI = 0.36, 0.25, 0.185  # stadium-shaped tube: 1.22 x 0.5 outside, like a USB-C opening
    box("PRINT_BuildPlate", (2.6, 1.8, 0.08), (0, 0, -0.04), c, m_plate, root, bevel=0.01)
    for name, size, loc in (("N", (3.0, 0.1, 0.9), (0, 1.0, 0.25)), ("S", (3.0, 0.1, 0.25), (0, -1.0, -0.075)), ("E", (0.1, 2.1, 0.9), (1.5, 0, 0.25)), ("W", (0.1, 2.1, 0.9), (-1.5, 0, 0.25))):
        box(f"PRINT_Wall_{name}", size, loc, c, m_machine, root)
    for i in range(NL):
        bm = bmesh.new()
        rings = [[bm.verts.new(p) for p in stadium(A, r, z)] for r, z in ((RO, 0), (RO, LH), (RI, LH), (RI, 0))]
        n = len(rings[0])
        for a, b in ((0, 1), (1, 2), (2, 3), (3, 0)):
            for k in range(n):
                bm.faces.new((rings[a][k], rings[a][(k + 1) % n], rings[b][(k + 1) % n], rings[b][k]))
        sl = finish(f"PRINT_Layer_{i + 1:02d}", bm, c, m_ti, root, (0, 0, i * LH))
        for axis in range(3):
            clamp(drive(sl, "scale", root, "print_progress", axis, offset=-float(i), gain=float(NL)), 0.0, 1.0)
    follower = empty("PRINT_LayerFollower", (0, 0, 0), c, root, 0.2)  # rides at the height of the layer being fused
    drive(follower, "location", root, "print_progress", 2, gain=H)
    box("PRINT_LaserHead", (1.6, 1.0, 0.18), (0, 0, 2.3), c, m_machine, root, bevel=0.03)
    for k in range(6):  # Apple: six lasers work at once
        t = k / 6
        px, py = stadium(A, (RO + RI) / 2, 0, n=30)[int(t * 62) % 62][:2]
        cylinder(f"PRINT_LaserBeam_{k + 1}", 0.012, 2.2, (px, py, 1.1 + LH), c, m_laser, follower, segments=10)
        cylinder(f"PRINT_LaserSpot_{k + 1}", 0.05, 0.012, (px, py, LH + 0.006), c, m_laser, follower, segments=16)
    powder = box("PRINT_PowderBed", (2.9, 1.9, 1.0), (0, 0, -0.5), c, m_powder, root)
    drive(powder, "location", root, "powder_level", 2, offset=-0.5, gain=H)
    top = empty("PRINT_PowderTop", (0, 0, 0), c, root, 0.2)
    drive(top, "location", root, "powder_level", 2, gain=H)
    blade = box("PRINT_Recoater", (0.10, 1.9, 0.22), (0, 0, 0.13), c, m_machine, top, bevel=0.02)
    drive(blade, "location", root, "recoat", 0, gain=1.3)
    drive_bsdf(m_laser, "Emission Strength", root, "laser_glow")
    drive_bsdf(m_ti, "Emission Strength", root, "part_glow")
    empty("ANCHOR_PartTop", (0, 0, H), c, root, 0.1)
    empty("CAM_Target_PrintedPort", (0, 0, 0.3), c, root, 0.2, "SPHERE")
    save(proj / "assets" / "printed_port_concept.blend")
    dg = setp(root, print_progress=0.5)
    T_["print progress=0.5 -> layer 15, 16, 17 scale (expect 1, 0, 0)"] = [round(E(f"PRINT_Layer_{i:02d}", dg).scale.x, 3) for i in (15, 16, 17)]
    T_["print progress=0.5 -> laser follower z (expect 0.3)"] = round(E("PRINT_LayerFollower", dg).location.z, 3)
    dg = setp(root, powder_level=1, recoat=1)
    T_["print powder_level=1 -> powder top z (expect 0.6); recoat=1 -> blade x (expect 1.3)"] = [round(E("PRINT_PowderBed", dg).location.z + 0.5, 3), round(E("PRINT_Recoater", dg).location.x, 3)]
    T_["print layers / laser beams (expect 30 / 6)"] = [sum(o.name.startswith("PRINT_Layer_") for o in bpy.data.objects), sum(o.name.startswith("PRINT_LaserBeam_") for o in bpy.data.objects)]
    cam, tgt = (2.4, -3.6, 2.6), (0, 0, 0.55)
    preview(proj, root, [("printed_port_printing_half", {"print_progress": 0.5, "powder_level": 0.0, "recoat": -1, "laser_glow": 6, "part_glow": 0.6}, cam, tgt, 30),
                         ("printed_port_in_powder", {"print_progress": 0.7, "powder_level": 0.68, "recoat": 0.6, "laser_glow": 6}, cam, tgt, 30),
                         ("printed_port_finished", {"print_progress": 1, "powder_level": 0, "recoat": -1, "laser_glow": 0, "part_glow": 0}, (1.6, -2.6, 1.5), (0, 0, 0.3), 40)])
    write_manifest(proj, "Lubang cas iPhone Air dicetak dari serbuk titanium", "port-cetak-3d",
                   "Apple: iPhone Air's titanium USB-C port is 3D-printed, thinner and stronger, using 33 percent less material than forging. Apple's printing process (described for Apple Watch cases): 100 percent recycled titanium powder of 50 micron particles, six lasers working at once, 60 micron layers. The 900-layer and 20-hour figures are for watch cases, NOT the port.",
                   [{"id": "printed_port_concept", "path": "assets/printed_port_concept.blend", "collection": "ASSET_PrintedPort",
                     "units": "macro set; port tube 1.22 x 0.5 x 0.6, drawn as 30 thick layers (a real print has far more, far thinner layers)",
                     "anchors": {"root": "PRINT_Root", "part_top": "ANCHOR_PartTop", "camera_target": "CAM_Target_PrintedPort"},
                     "controls": {"print_progress": F(0, 1, 0, "PRINT_Root", "reveals layers bottom to top; six laser spots ride on the current layer"),
                                  "powder_level": F(0, 1, 0, "PRINT_Root", "powder bed and recoater height"), "recoat": F(-1, 1, 0, "PRINT_Root", "blade sweep +-1.3"),
                                  "laser_glow": F(0, 20, 0, "PRINT_Root", "beams and spots"), "part_glow": F(0, 10, 0, "PRINT_Root", "hot-metal glow of the part")},
                     "notes": "Conceptual. Machine shape, part shape and layer count are illustrative; only the facts listed in sourced_facts come from Apple."}])


# ================================================================ 4. heat-flow arrows for the vapor chamber episode
def build_heat_flow():
    proj = project("iphone-vapor-chamber")
    reset()
    c = new_collection("ASSET_FX_HeatFlow")
    root = empty("FXHEAT_Root", (0, 0, 0), c, size=0.3)
    control(root, "flow", 0.0, 0.0, 1.0, "Arrows advance one spacing along +X; 0 and 1 look identical (loops)")
    control(root, "strength", 2.0, 0.0, 10.0, "Emission of the arrows")
    mover = empty("FXHEAT_Mover", (0, 0, 0), c, root, 0.1)
    drive(mover, "location", root, "flow", 0, gain=0.4)
    N = 9
    for i in range(N):
        t = i / (N - 1)
        colour = (1.0 - 0.8 * t, 0.25 + 0.35 * t, 0.1 + 0.9 * t)  # hot red at -X fading to cool blue at +X
        m = glow(f"FXHEAT_Mat_{i + 1}", colour, 2.0)
        a = prism(f"FXHEAT_Arrow_{i + 1}", [(-0.10, -0.16), (0.12, 0.0), (-0.10, 0.16), (-0.04, 0.0)][0:3], 0.03, (-1.6 + 0.4 * i, 0, 0), c, m, mover)
        a.rotation_euler = (math.radians(90), 0, 0)  # lay the arrow flat in XY, pointing +X
        drive_bsdf(m, "Emission Strength", root, "strength")
    save(proj / "assets" / "heat_flow_schematic.blend")
    dg = setp(root, flow=1)
    T_["heat flow=1 -> mover x (expect 0.4)"] = round(E("FXHEAT_Mover", dg).location.x, 3)
    preview(proj, root, [("heat_flow_arrows", {"flow": 0.5, "strength": 2.5}, (0.0, -1.2, 4.6), (0, 0, 0), 30)])
    write_manifest(proj, "Ada air di dalam iPhone 17 Pro, dan itu sengaja (ruang uap)", "ruang-uap",
                   "Apple (iPhone 17 Pro): deionized water is sealed inside an Apple-designed vapor chamber laser-welded into the aluminum unibody; heat from A19 Pro moves into the unibody and is spread; up to 40 percent better sustained performance.",
                   [{"id": "heat_flow_schematic", "path": "assets/heat_flow_schematic.blend", "collection": "ASSET_FX_HeatFlow", "dependencies": ["vapor_chamber_concept"],
                     "units": "macro set matching vapor_chamber_concept; nine arrows from x=-1.6 to x=1.6",
                     "anchors": {"root": "FXHEAT_Root"},
                     "controls": {"flow": F(0, 1, 0, "FXHEAT_Root", "arrows advance 0.4 (one spacing)"), "strength": F(0, 10, 2, "FXHEAT_Root", "emission")},
                     "notes": "Illustrative drawing aid: heat is not visible."}])


build_quad_pixel()
build_camera_control()
build_printed_port()
build_heat_flow()
(REPO / "iphone-facts" / "reports").mkdir(exist_ok=True)
(REPO / "iphone-facts" / "reports" / "round2_assets_validation.json").write_text(json.dumps(REPORT, indent=2) + "\n", encoding="utf-8")
print("TESTS", json.dumps(T_, indent=1))
print("RENDERS_OK", all(r["exists"] for r in REPORT["renders"]), len(REPORT["renders"]))
