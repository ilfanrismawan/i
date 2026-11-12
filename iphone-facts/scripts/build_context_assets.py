"""Context assets: "where is it on the phone" bodies for three topics, plus one shared preview lighting rig.

Run:  blender --background --python iphone-facts/scripts/build_context_assets.py -- <repo_root>

The existing phone models are NOT rebuilt: each file appends a copy of iphone-crash-detection's
phone_exterior (and phone_interior_concept) and only adds the topic-specific part.

  iphone-camera-control/assets/phone_with_camera_control.blend  ASSET_PhoneCameraControl  phone + side button
  iphone-printed-port/assets/phone_air_bottom.blend             ASSET_PhoneAir            thinned phone + titanium port
  iphone-vapor-chamber/assets/phone_17pro_body_adapter.blend    ASSET_PhoneVapor          phone + interior + chamber plate
  iphone-facts/assets/preview_lighting.blend                    RIG_PreviewLighting       three-light rig + neutral world

Conceptual: the phone is a generic stylised body, not the real iPhone 16 / Air / 17 Pro design. Position and
size of the button, port and chamber are illustrative; only iPhone Air's 5.6 mm thickness is an Apple figure.
"""
import hashlib
import json
import math
import sys
from pathlib import Path

import bmesh
import bpy

REPO = Path(sys.argv[sys.argv.index("--") + 1]).resolve()
sys.path.insert(0, str(REPO / "iphone-crash-detection" / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from asset_lib import box, control, drive, drive_bsdf, empty, finish, material, new_collection, reset, rounded_slab, save  # noqa: E402
from preview_lib import append_collection, preview, setp, world_bounds  # noqa: E402

SRC = REPO / "iphone-crash-detection" / "assets"
W, H, T = 0.0715, 0.1467, 0.0078
REPORT = {"blender": bpy.app.version_string, "tests": {}, "renders": []}
T_ = REPORT["tests"]
F = lambda lo, hi, d, on, affects: {"type": "float", "min": lo, "max": hi, "default": d, "on": on, "affects": affects}


def glow(name, colour, strength=0.0, base=None, metallic=0.0, rough=0.35):
    return material(name, base or tuple(c * 0.35 for c in colour), metallic=metallic, rough=rough, emission=colour, strength=strength)


def add_manifest(proj, entry):
    mf = proj / "asset_manifest.json"
    data = json.loads(mf.read_text(encoding="utf-8"))
    entry.update(phase="context-assets", status="complete", generator="../iphone-facts/scripts/build_context_assets.py", previews="previews/",
                 source_sha256=hashlib.sha256((proj / entry["path"]).read_bytes()).hexdigest())
    data["assets"] = [a for a in data["assets"] if a["id"] != entry["id"]] + [entry]
    data["pending_assets"] = [p for p in data.get("pending_assets", []) if not p.startswith(entry["id"])]
    mf.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def phone_objects():
    return [o for o in bpy.data.objects if o.name.startswith("PHONE_") and o.type == "MESH"]


# ---------------------------------------------------------------- 1. phone with Camera Control
def build_phone_camera_control():
    proj = REPO / "iphone-camera-control"
    reset()
    c = new_collection("ASSET_PhoneCameraControl")
    root = empty("PCC_Root", (0, 0, 0), c, size=0.05)
    c.children.link(append_collection(SRC / "phone_exterior.blend", "ASSET_Phone"))
    bpy.context.scene.collection.children.unlink(bpy.data.collections["ASSET_Phone"])
    phone = bpy.data.objects["PHONE_Root"]
    phone.parent = root
    control(root, "button_glow", 0.0, 0.0, 10.0, "Emission of the Camera Control button (to point it out)")
    control(root, "button_press", 0.0, 0.0, 1.0, "Button sinks 0.35 mm into the frame")
    m_btn = glow("PCC_Mat_Button", (0.3, 0.8, 1.0), 0.0, base=(0.05, 0.06, 0.09), metallic=0.3, rough=0.1)
    m_rim = material("PCC_Mat_ButtonRim", (0.20, 0.28, 0.42), metallic=0.9, rough=0.3)
    z = -0.024  # lower half of the right-hand edge
    box("PCC_ButtonRecess", (0.0006, 0.0042, 0.0200), (W / 2 - 0.0001, 0, z), c, m_rim, root, bevel=0.0002)
    btn = box("PCC_Button", (0.0010, 0.0032, 0.0180), (W / 2 + 0.0003, 0, z), c, m_btn, root, bevel=0.0004, seg=3)
    drive(btn, "location", root, "button_press", 0, offset=W / 2 + 0.0003, gain=-0.00035)
    drive_bsdf(m_btn, "Emission Strength", root, "button_glow")
    empty("ANCHOR_CameraControl", (W / 2 + 0.0008, 0, z), c, root, 0.005)
    empty("CAM_Target_PhoneCameraControl", (W / 2, 0, z), c, root, 0.01, "SPHERE")
    save(proj / "assets" / "phone_with_camera_control.blend")
    dg = setp(root, button_press=1)
    T_["button body: press=1 -> button x moved mm (expect -0.35)"] = round((bpy.data.objects["PCC_Button"].evaluated_get(dg).location.x - (W / 2 + 0.0003)) * 1000, 2)
    T_["button body: button sticks out of the frame mm at rest (expect about 0.8)"] = round((W / 2 + 0.0003 + 0.0005 - W / 2) * 1000, 2)
    T_["button body: phone parts reused (appended, not rebuilt)"] = len(phone_objects())
    preview(proj / "previews", root, [("phone_camera_control_side", {"button_press": 0, "button_glow": 2.5}, (0.20, -0.16, -0.01), (W / 2, 0, -0.012), 60),
                                      ("phone_camera_control_macro", {"button_glow": 1.0}, (0.085, -0.045, -0.034), (W / 2, 0, -0.024), 50)], REPORT)
    add_manifest(proj, {"id": "phone_with_camera_control", "path": "assets/phone_with_camera_control.blend", "collection": "ASSET_PhoneCameraControl",
                        "dependencies": ["iphone-crash-detection: phone_exterior (appended copy)", "camera_control_concept"],
                        "units": "metres, real scale; same axes as phone_exterior (upright, screen -Y); button on the +X edge",
                        "anchors": {"root": "PCC_Root", "phone": "PHONE_Root", "button": "ANCHOR_CameraControl", "camera_target": "CAM_Target_PhoneCameraControl"},
                        "controls": {"button_glow": F(0, 10, 0, "PCC_Root", "button emission"), "button_press": F(0, 1, 0, "PCC_Root", "button sinks 0.35 mm"),
                                     "shell_opacity": F(0, 1, 1, "PHONE_Root", "inherited from phone_exterior")},
                        "notes": "Generic phone body, not the real iPhone 16 design; button size and position are illustrative."})


# ---------------------------------------------------------------- 2. iPhone Air bottom with the printed port
def build_phone_air():
    proj = REPO / "iphone-printed-port"
    reset()
    c = new_collection("ASSET_PhoneAir")
    root = empty("AIR_Root", (0, 0, 0), c, size=0.05)
    c.children.link(append_collection(SRC / "phone_exterior.blend", "ASSET_Phone"))
    bpy.context.scene.collection.children.unlink(bpy.data.collections["ASSET_Phone"])
    phone = bpy.data.objects["PHONE_Root"]
    phone.parent = root
    AIR_T = 0.0056  # Apple: iPhone Air is 5.6 mm thick
    phone.scale = (1.0, AIR_T / T, 1.0)  # thin the reused body instead of modelling a new one
    bpy.data.objects["PHONE_Port"].hide_render = True  # replaced by the titanium port below
    control(root, "port_glow", 0.0, 0.0, 10.0, "Emission of the titanium port (to point it out)")
    control(root, "port_slide", 0.0, 0.0, 1.0, "Slides the port 12 mm out of the body along -Z (exploded view)")
    m_ti = glow("AIR_Mat_PortTitanium", (1.0, 0.6, 0.25), 0.0, base=(0.66, 0.64, 0.60), metallic=0.95, rough=0.38)
    A, RO, RI, DEPTH = 0.00285, 0.00160, 0.00122, 0.0070
    bm = bmesh.new()

    def ring(r, z):
        pts = []
        for cx, start in ((A, -90), (-A, 90)):
            for i in range(13):
                a = math.radians(start + 180 * i / 12)
                pts.append(bm.verts.new((cx + r * math.cos(a), r * math.sin(a), z)))
        return pts

    rings = [ring(RO, 0), ring(RO, DEPTH), ring(RI, DEPTH), ring(RI, 0)]
    n = len(rings[0])
    for a, b in ((0, 1), (1, 2), (2, 3), (3, 0)):
        for k in range(n):
            bm.faces.new((rings[a][k], rings[a][(k + 1) % n], rings[b][(k + 1) % n], rings[b][k]))
    port = finish("AIR_Port", bm, c, m_ti, root, (0, 0, -H / 2 - 0.0002), smooth=False)
    drive(port, "location", root, "port_slide", 2, offset=-H / 2 - 0.0002, gain=-0.012)
    box("AIR_PortTongue", (0.0052, 0.0006, 0.0050), (0, 0, 0.0030), c, material("AIR_Mat_PortTongue", (0.05, 0.05, 0.06), rough=0.5), port)
    drive_bsdf(m_ti, "Emission Strength", root, "port_glow")
    empty("ANCHOR_Port", (0, 0, -H / 2), c, root, 0.004)
    empty("CAM_Target_PhoneAir", (0, 0, -H / 2), c, root, 0.01, "SPHERE")
    save(proj / "assets" / "phone_air_bottom.blend")
    lo, hi = world_bounds([bpy.data.objects["PHONE_Frame"]])
    T_["air: body thickness mm (expect 5.6)"] = round((hi.y - lo.y) * 1000, 2)
    plo, phi = world_bounds([bpy.data.objects["AIR_Port"]])
    T_["air: port outer size mm x,y (expect about 8.9, 3.2) and it fits inside 5.6"] = [round((phi.x - plo.x) * 1000, 2), round((phi.y - plo.y) * 1000, 2)]
    dg = setp(root, port_slide=1)
    T_["air: port_slide=1 -> port moved mm (expect -12)"] = round((bpy.data.objects["AIR_Port"].evaluated_get(dg).location.z - (-H / 2 - 0.0002)) * 1000, 2)
    preview(proj / "previews", root, [("phone_air_bottom_port", {"port_slide": 0, "port_glow": 1.5}, (0.035, -0.075, -0.125), (0, 0, -H / 2), 50),
                                      ("phone_air_port_exploded", {"port_slide": 1, "port_glow": 1.5}, (0.045, -0.085, -0.130), (0, 0, -H / 2 - 0.006), 50),
                                      ("phone_air_thin_profile", {"port_slide": 0, "port_glow": 0}, (0.26, -0.03, 0.02), (0, 0, 0), 60)], REPORT)
    add_manifest(proj, {"id": "phone_air_bottom", "path": "assets/phone_air_bottom.blend", "collection": "ASSET_PhoneAir",
                        "dependencies": ["iphone-crash-detection: phone_exterior (appended copy, thinned)", "printed_port_concept"],
                        "units": "metres, real scale; body thinned to 5.6 mm (Apple figure); port at the bottom edge",
                        "anchors": {"root": "AIR_Root", "phone": "PHONE_Root", "port": "ANCHOR_Port", "camera_target": "CAM_Target_PhoneAir"},
                        "controls": {"port_glow": F(0, 10, 0, "AIR_Root", "port emission"), "port_slide": F(0, 1, 0, "AIR_Root", "port slides 12 mm out along -Z"),
                                     "shell_opacity": F(0, 1, 1, "PHONE_Root", "inherited from phone_exterior")},
                        "notes": "Generic phone body thinned in Y, not the real iPhone Air design (camera layout differs). Port shape and size are illustrative."})


# ---------------------------------------------------------------- 3. phone with interior and vapor chamber plate
def build_phone_vapor():
    proj = REPO / "iphone-vapor-chamber"
    reset()
    c = new_collection("ASSET_PhoneVapor")
    root = empty("PVC_Root", (0, 0, 0), c, size=0.05)
    for blend, name in (("phone_exterior.blend", "ASSET_Phone"), ("phone_interior_concept.blend", "ASSET_PhoneInterior")):
        c.children.link(append_collection(SRC / blend, name))
        bpy.context.scene.collection.children.unlink(bpy.data.collections[name])
    phone, interior = bpy.data.objects["PHONE_Root"], bpy.data.objects["PHONEINT_Root"]
    phone.parent = root
    interior.parent = phone
    control(root, "chamber_glow", 0.0, 0.0, 10.0, "Emission of the vapor chamber plate")
    control(root, "hot_end", 0.0, 0.0, 10.0, "Red glow on the chamber where it sits over the chip")
    control(root, "cool_end", 0.0, 0.0, 10.0, "Blue glow on the far end of the chamber")
    m_ch = glow("PVC_Mat_Chamber", (0.3, 0.75, 1.0), 0.0, base=(0.72, 0.50, 0.30), metallic=0.85, rough=0.4)
    m_hot = glow("PVC_Mat_HotZone", (1.0, 0.25, 0.05), 0.0, base=(0.5, 0.2, 0.15), metallic=0.5)
    m_cool = glow("PVC_Mat_CoolZone", (0.2, 0.55, 1.0), 0.0, base=(0.2, 0.3, 0.5), metallic=0.5)
    Y = 0.0026  # between the parts and the back glass
    rounded_slab("PVC_Chamber", 0.048, 0.060, 0.0006, 0.004, (-0.007, Y, 0.0), c, m_ch, root)
    rounded_slab("PVC_HotZone", 0.015, 0.015, 0.0002, 0.002, (-0.022, Y + 0.0004, 0.031 - 0.008), c, m_hot, root)
    rounded_slab("PVC_CoolZone", 0.016, 0.050, 0.0002, 0.002, (0.008, Y + 0.0004, 0.0), c, m_cool, root)
    for m, p in ((m_ch, "chamber_glow"), (m_hot, "hot_end"), (m_cool, "cool_end")):
        drive_bsdf(m, "Emission Strength", root, p)
    empty("ANCHOR_VaporChamber", (-0.007, Y, 0.0), c, root, 0.005)
    empty("ANCHOR_ChipUnderChamber", (-0.022, Y, 0.023), c, root, 0.004)
    empty("CAM_Target_PhoneVapor", (-0.004, 0, 0.005), c, root, 0.01, "SPHERE")
    save(proj / "assets" / "phone_17pro_body_adapter.blend")
    lo, hi = world_bounds([bpy.data.objects[n] for n in ("PVC_Chamber", "PVC_HotZone", "PVC_CoolZone")])
    T_["vapor body: chamber inside the shell (x within +-35.75, y below 3.9, z within +-73.35 mm)"] = bool(lo.x > -0.03575 and hi.x < 0.03575 and hi.y < 0.0039 and lo.y > -0.0039 and lo.z > -0.07335 and hi.z < 0.07335)
    T_["vapor body: chamber y range mm"] = [round(lo.y * 1000, 2), round(hi.y * 1000, 2)]
    T_["vapor body: interior markers reused"] = sum(o.name.startswith("PHONEINT_Sensor_") or o.name == "PHONEINT_Processor" for o in bpy.data.objects)
    back = (0.06, 0.30, 0.03)
    preview(proj / "previews", phone, [("phone_vapor_xray_back", {"shell_opacity": 0.14}, back, (0, 0, 0), 60)], REPORT)
    setp(root, hot_end=3, cool_end=2)
    setp(interior, glow_processor=3)
    preview(proj / "previews", phone, [("phone_vapor_xray_back_hot_cool", {"shell_opacity": 0.14}, back, (0, 0, 0), 60)], REPORT)
    add_manifest(proj, {"id": "phone_17pro_body_adapter", "path": "assets/phone_17pro_body_adapter.blend", "collection": "ASSET_PhoneVapor",
                        "dependencies": ["iphone-crash-detection: phone_exterior + phone_interior_concept (appended copies)", "vapor_chamber_concept"],
                        "units": "metres, real scale; same axes as phone_exterior; chamber plate sits toward the back (+Y), view it from the back",
                        "anchors": {"root": "PVC_Root", "phone": "PHONE_Root", "interior": "PHONEINT_Root", "chamber": "ANCHOR_VaporChamber", "chip": "ANCHOR_ChipUnderChamber", "camera_target": "CAM_Target_PhoneVapor"},
                        "controls": {"chamber_glow": F(0, 10, 0, "PVC_Root", "chamber plate emission"), "hot_end": F(0, 10, 0, "PVC_Root", "red zone over the chip"),
                                     "cool_end": F(0, 10, 0, "PVC_Root", "blue zone at the far end"), "shell_opacity": F(0, 1, 1, "PHONE_Root", "inherited"),
                                     "glow_processor": F(0, 30, 0, "PHONEINT_Root", "inherited from phone_interior_concept")},
                        "notes": "Generic phone and interior, not the real iPhone 17 Pro. Apple states the chamber is laser-welded into the aluminium unibody and moves heat from the A19 Pro; its outline and position here are illustrative."})


# ---------------------------------------------------------------- 4. shared preview lighting rig
def build_lighting():
    reset()
    c = new_collection("RIG_PreviewLighting")
    root = empty("LIGHT_Root", (0, 0, 0), c, size=0.3)
    control(root, "intensity", 1.0, 0.0, 5.0, "Multiplies all three lights")
    for name, kind, energy, rot, colour in (("Key", "SUN", 2.6, (50, 0, -38), (1.0, 0.97, 0.92)), ("Fill", "SUN", 0.9, (65, 0, 140), (0.85, 0.92, 1.0)),
                                            ("Rim", "SUN", 1.8, (115, 0, 200), (0.9, 0.95, 1.0))):
        L = bpy.data.objects.new(f"LIGHT_{name}", bpy.data.lights.new(f"LIGHT_{name}", kind))
        L.data.color, L.data.angle = colour, math.radians(12)
        L.rotation_euler = tuple(math.radians(a) for a in rot)
        L.parent = root
        c.objects.link(L)
        drive(L.data, "energy", root, "intensity", gain=energy)
    world = bpy.data.worlds.new("WORLD_NeutralDark")
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs[0].default_value = (0.035, 0.04, 0.055, 1)
    world.node_tree.nodes["Background"].inputs[1].default_value = 1.0
    world.use_fake_user = True
    bpy.context.scene.world = world
    out = REPO / "iphone-facts" / "assets"
    out.mkdir(exist_ok=True)
    save(out / "preview_lighting.blend")
    dg = setp(root, intensity=2)
    T_["lighting: intensity=2 -> key energy (expect 5.2)"] = round(bpy.data.objects["LIGHT_Key"].evaluated_get(dg).data.energy, 2)
    T_["lighting: lights / world"] = [sum(o.type == "LIGHT" for o in bpy.data.objects), world.name]


build_phone_camera_control()
build_phone_air()
build_phone_vapor()
build_lighting()
(REPO / "iphone-facts" / "reports").mkdir(exist_ok=True)
(REPO / "iphone-facts" / "reports" / "context_assets_validation.json").write_text(json.dumps(REPORT, indent=2) + "\n", encoding="utf-8")
print("TESTS", json.dumps(T_, indent=1))
print("RENDERS_OK", all(r["exists"] for r in REPORT["renders"]), len(REPORT["renders"]))
