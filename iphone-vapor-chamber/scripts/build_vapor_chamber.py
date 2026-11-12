"""New asset for the vapor-chamber episode. Reuses the existing phone assets; builds ONLY the missing one.

Run:  blender --background --python scripts/build_vapor_chamber.py -- <this_project_dir>
Output: assets/vapor_chamber_concept.blend (collection ASSET_VaporChamber) + previews/vapor_chamber_*.png

Conceptual illustration of a generic vapor chamber: Apple states only that deionized water is sealed
inside a chamber laser-welded to the aluminium body. Shapes, droplets and the loop are a drawing aid.
"""
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

PROJECT = Path(sys.argv[sys.argv.index("--") + 1]).resolve()
sys.path.insert(0, str(PROJECT.parent / "iphone-crash-detection" / "scripts"))  # shared helper library, not copied
from asset_lib import box, control, cylinder, drive, drive_bsdf, empty, material, new_collection, reset, save  # noqa: E402

reset()
c = new_collection("ASSET_VaporChamber")
root = empty("VAPOR_Root", (0, 0, 0), c, size=0.5)
m_shell = material("VAPOR_Mat_Shell", (0.62, 0.66, 0.72), metallic=0.9, rough=0.3)
m_wick = material("VAPOR_Mat_Wick", (0.72, 0.50, 0.30), metallic=0.8, rough=0.55)
m_chip = material("VAPOR_Mat_Chip", (0.25, 0.05, 0.03), rough=0.4, emission=(1.0, 0.25, 0.05), strength=0.0)
m_cool = material("VAPOR_Mat_CoolEnd", (0.10, 0.25, 0.45), metallic=0.6, rough=0.35, emission=(0.2, 0.6, 1.0), strength=0.0)
m_water = material("VAPOR_Mat_Water", (0.25, 0.60, 1.0), rough=0.1, emission=(0.2, 0.55, 1.0), strength=0.8)
m_steam = material("VAPOR_Mat_Steam", (0.95, 0.97, 1.0), rough=0.6, emission=(1.0, 0.85, 0.75), strength=0.8)
L, W, H = 3.6, 1.6, 0.50  # macro set; scale exaggerated, hot end at -X, cool end at +X
box("VAPOR_Floor", (L, W, 0.06), (0, 0, 0.03), c, m_shell, root, bevel=0.01)
box("VAPOR_WallBack", (L, 0.06, H), (0, W / 2 - 0.03, H / 2), c, m_shell, root)
for sx, name in ((-1, "Hot"), (1, "Cool")):
    box(f"VAPOR_End_{name}", (0.06, W, H), (sx * (L / 2 - 0.03), 0, H / 2), c, m_shell, root)
box("VAPOR_Lid", (L, W, 0.05), (0, 0, H + 0.025), c, m_shell, root, bevel=0.01).hide_render = True  # hidden lid; enable to close the chamber
box("VAPOR_Wick", (L - 0.16, W - 0.12, 0.07), (0, 0, 0.095), c, m_wick, root)
for i in range(17):  # wick ribs: a fine structure the liquid creeps along
    box(f"VAPOR_WickRib_{i + 1:02d}", (0.03, W - 0.14, 0.04), (-1.6 + 0.2 * i, 0, 0.15), c, m_wick, root)
box("VAPOR_Chip", (0.9, 0.9, 0.16), (-1.15, 0, -0.08), c, m_chip, root, bevel=0.02)
box("VAPOR_BodyPlate", (1.3, W, 0.10), (1.05, 0, -0.05), c, m_cool, root, bevel=0.02)

control(root, "cycle", 0.0, 0.0, 1.0, "One loop step: droplets creep toward the hot end, vapour drifts to the cool end; 0 and 1 look identical")
control(root, "heat", 0.0, 0.0, 10.0, "Glow of the hot chip under the chamber")
control(root, "cool_glow", 0.0, 0.0, 10.0, "Glow of the cool body plate")
control(root, "flow_glow", 0.8, 0.0, 10.0, "Glow of droplets and vapour")
STEP, N = 0.4, 9
for i in range(N):
    for row, y in enumerate((-0.45, 0.0, 0.45)):
        x0 = -1.6 + STEP * i + 0.13 * row
        d = cylinder(f"VAPOR_Drop_{i + 1}_{row + 1}", 0.055, 0.03, (x0, y, 0.185), c, m_water, root, segments=16)
        drive(d, "location", root, "cycle", 0, offset=x0, gain=-STEP)  # liquid returns toward the heat
        v = box(f"VAPOR_Steam_{i + 1}_{row + 1}", (0.10, 0.10, 0.10), (x0, y * 0.9, 0.36), c, m_steam, root, bevel=0.045, seg=3)
        drive(v, "location", root, "cycle", 0, offset=x0 - STEP * 0.5, gain=STEP)  # vapour carries heat away
drive_bsdf(m_chip, "Emission Strength", root, "heat")
drive_bsdf(m_cool, "Emission Strength", root, "cool_glow")
for m in (m_water, m_steam):
    drive_bsdf(m, "Emission Strength", root, "flow_glow")
empty("ANCHOR_HotSpot", (-1.15, 0, 0.0), c, root, 0.1)
empty("ANCHOR_CoolEnd", (1.05, 0, 0.0), c, root, 0.1)
empty("CAM_Target_Vapor", (0, 0, 0.2), c, root, 0.2, "SPHERE")
(PROJECT / "assets").mkdir(exist_ok=True)
save(PROJECT / "assets" / "vapor_chamber_concept.blend")

# ---- quick control test + two Eevee stills
def setp(**p):
    for k, val in p.items():
        root[k] = float(val)
    root.update_tag()
    bpy.context.view_layer.update()
    return bpy.context.evaluated_depsgraph_get()

d0 = bpy.data.objects["VAPOR_Drop_1_1"].location.x
dg = setp(cycle=1, heat=4, cool_glow=1.5)
print("TEST drop moved (expect -0.4):", round(bpy.data.objects["VAPOR_Drop_1_1"].evaluated_get(dg).location.x - d0, 3))
scene = bpy.context.scene
for eng in ("BLENDER_EEVEE_NEXT", "BLENDER_EEVEE"):
    try:
        scene.render.engine = eng
        break
    except Exception:
        continue
scene.render.resolution_x, scene.render.resolution_y = 540, 960
world = bpy.data.worlds.new("W")
world.use_nodes = True
world.node_tree.nodes["Background"].inputs[0].default_value = (0.04, 0.05, 0.08, 1)
scene.world = world
sun = bpy.data.objects.new("PreviewSun", bpy.data.lights.new("PreviewSun", "SUN"))
sun.data.energy, sun.rotation_euler = 3.0, (math.radians(50), 0, math.radians(-30))
scene.collection.objects.link(sun)
cam = bpy.data.objects.new("PreviewCam", bpy.data.cameras.new("PreviewCam"))
scene.collection.objects.link(cam)
scene.camera = cam
cam.data.lens = 26
(PROJECT / "previews").mkdir(exist_ok=True)
for name, cyc in (("vapor_chamber_cycle_000", 0.0), ("vapor_chamber_cycle_050", 0.5)):
    setp(cycle=cyc)
    cam.location = (0.0, -4.6, 3.0)
    cam.rotation_euler = (Vector((0, 0, 0.15)) - cam.location).to_track_quat("-Z", "Y").to_euler()
    scene.render.filepath = str(PROJECT / "previews" / f"{name}.png")
    bpy.ops.render.render(write_still=True)
    print("RENDERED", name, Path(scene.render.filepath).is_file())
