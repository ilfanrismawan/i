"""Phase 03 - mechanism assets (conceptual illustrations). Does not touch phase 02 files.

Run:  blender --background --python scripts/build_mechanism_assets.py -- <project_dir>

Outputs:
  assets/phone_interior_concept.blend  ASSET_PhoneInterior  real scale, same axes as phone_exterior (fits inside its shell)
  assets/sensor_accel_concept.blend    ASSET_SensorAccel    macro set, enlarged, mass on springs
  assets/sensor_gyro_concept.blend     ASSET_SensorGyro     macro set, enlarged, vibrating ring
  assets/sensor_baro_concept.blend     ASSET_SensorBaro     macro set, enlarged, flexing membrane

Apple does not publish the shape or position of these parts. Layout, shapes and colours here are
CONCEPTUAL: they show the general class of mechanism, not the real components of any iPhone.
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from asset_lib import (box, control, cylinder, disc_membrane, drive, drive_bsdf, empty, material,  # noqa: E402
                       new_collection, reset, rounded_slab, save, torus, tube, zigzag)

PROJECT = Path(sys.argv[sys.argv.index("--") + 1]).resolve()
ASSETS = PROJECT / "assets"
SENSORS = {  # id: (emission colour, position on the board x,z)
    "accel": ((1.00, 0.45, 0.10), (-0.0265, 0.006)),
    "gyro": ((0.10, 0.85, 1.00), (-0.0180, 0.006)),
    "baro": ((0.25, 1.00, 0.40), (-0.0220, -0.012)),
    "gps": ((1.00, 0.90, 0.15), (-0.0220, 0.056)),
}


def build_phone_interior():
    reset()
    c = new_collection("ASSET_PhoneInterior")
    root = empty("PHONEINT_Root", (0, 0, 0), c, size=0.03)
    m_board = material("PHONEINT_Mat_Board", (0.03, 0.16, 0.20), metallic=0.2, rough=0.55)
    m_batt = material("PHONEINT_Mat_Battery", (0.11, 0.11, 0.13), metallic=0.5, rough=0.4)
    m_part = material("PHONEINT_Mat_Part", (0.20, 0.21, 0.24), metallic=0.7, rough=0.4)
    m_chip = material("PHONEINT_Mat_ChipDark", (0.04, 0.04, 0.05), metallic=0.3, rough=0.45)
    m_lens = material("PHONEINT_Mat_CameraModule", (0.05, 0.05, 0.08), metallic=0.8, rough=0.2)

    rounded_slab("PHONEINT_Battery", 0.040, 0.083, 0.0034, 0.004, (0.011, 0.0002, -0.0135), c, m_batt, root, bevel=0.0004)
    rounded_slab("PHONEINT_Board", 0.020, 0.096, 0.0010, 0.002, (-0.022, 0.0005, 0.018), c, m_board, root)
    box("PHONEINT_TapticEngine", (0.030, 0.0030, 0.010), (0.012, 0.0002, -0.0625), c, m_part, root, bevel=0.0006)
    box("PHONEINT_Speaker", (0.022, 0.0030, 0.010), (-0.020, 0.0002, -0.0600), c, m_part, root, bevel=0.0006)
    bx, bz = 0.0715 / 2 - 0.0215, 0.1467 / 2 - 0.0215  # same centres as the exterior camera island
    for i, (dx, dz) in enumerate(((0.0075, 0.0075), (-0.0075, -0.0075))):
        cylinder(f"PHONEINT_CameraModule_{i + 1}", 0.0070, 0.0048, (bx + dx, 0.0010, bz + dz), c, m_lens, root, axis="Y", bevel=0.0004)
    for k, (x, z, w, h) in enumerate(((-0.027, 0.046, 0.005, 0.004), (-0.017, 0.045, 0.006, 0.006), (-0.026, 0.018, 0.004, 0.006),
                                      (-0.018, 0.017, 0.005, 0.003), (-0.022, -0.002, 0.008, 0.004), (-0.027, -0.022, 0.004, 0.005),
                                      (-0.017, -0.023, 0.005, 0.004))):
        box(f"PHONEINT_FillerChip_{k + 1}", (w, 0.0008, h), (x, -0.0004, z), c, m_chip, root, bevel=0.0002)

    def glowing(name, size, loc, colour, prop, label):
        m = material(f"PHONEINT_Mat_{name}", (0.10, 0.10, 0.12), metallic=0.4, rough=0.35, emission=colour, strength=0.0)
        ob = box(f"PHONEINT_{name}", size, loc, c, m, root, bevel=0.0003)
        control(root, prop, 0.0, 0.0, 30.0, f"Glow of the {label} (0 = off)")
        drive_bsdf(m, "Emission Strength", root, prop)
        empty(f"ANCHOR_{name}", (loc[0], loc[1] - size[1] / 2, loc[2]), c, root, 0.003)
        return ob

    glowing("Processor", (0.0130, 0.0012, 0.0130), (-0.022, -0.0006, 0.031), (0.55, 0.75, 1.00), "glow_processor", "main processor chip")
    for sid, (colour, (x, z)) in SENSORS.items():
        glowing(f"Sensor_{sid.capitalize()}", (0.0056, 0.0010, 0.0056), (x, -0.0005, z), colour, f"glow_{sid}", f"{sid} sensor marker")
    glowing("Sensor_Mic", (0.0050, 0.0022, 0.0028), (-0.0105, 0.0, -0.0708), (1.00, 0.30, 0.85), "glow_mic", "microphone module")
    empty("CAM_Target_PhoneInterior", (-0.012, 0, 0.012), c, root, 0.01, "SPHERE")
    save(ASSETS / "phone_interior_concept.blend")


def package(prefix, c, root, size, m_base, m_wall, wall_h=0.30):
    """Open-topped chip package: floor plus four low walls, so the camera can look in."""
    w, d = size
    box(f"{prefix}_Floor", (w, d, 0.08), (0, 0, -0.04), c, m_base, root, bevel=0.015)
    t = 0.10
    for name, sz, loc in (("N", (w, t, wall_h), (0, d / 2 - t / 2, wall_h / 2)), ("S", (w, t, wall_h), (0, -d / 2 + t / 2, wall_h / 2)),
                          ("E", (t, d - 2 * t, wall_h), (w / 2 - t / 2, 0, wall_h / 2)), ("W", (t, d - 2 * t, wall_h), (-w / 2 + t / 2, 0, wall_h / 2))):
        box(f"{prefix}_Wall_{name}", sz, loc, c, m_wall, root, bevel=0.012)


def bond_pads(prefix, c, root, half_w, half_d):
    """Gold contact pads in the package corners, each with a thin wire climbing to the wall."""
    m_gold = material(f"{prefix}_Mat_BondGold", (1.00, 0.78, 0.30), metallic=1.0, rough=0.25)
    k = 0
    for sx in (-1, 1):
        for sy in (-1, 1):
            k += 1
            box(f"{prefix}_BondPad_{k}", (0.14, 0.14, 0.02), (sx * half_w, sy * half_d, 0.01), c, m_gold, root, bevel=0.004)
            w = box(f"{prefix}_BondWire_{k}", (0.30, 0.018, 0.018), (sx * half_w, sy * half_d, 0.03), c, m_gold, root, origin_min_x=True)
            w.rotation_euler = (0, -math.radians(50), 0 if sx > 0 else math.pi)


def build_accel():
    reset()
    c = new_collection("ASSET_SensorAccel")
    root = empty("ACCEL_Root", (0, 0, 0), c, size=0.5)
    m_base = material("ACCEL_Mat_Base", (0.10, 0.13, 0.20), metallic=0.3, rough=0.5)
    m_wall = material("ACCEL_Mat_Wall", (0.20, 0.24, 0.33), metallic=0.4, rough=0.45)
    m_mass = material("ACCEL_Mat_Mass", (0.95, 0.62, 0.15), metallic=0.85, rough=0.3, emission=(1.0, 0.45, 0.10), strength=0.0)
    m_spring = material("ACCEL_Mat_Spring", (0.80, 0.82, 0.86), metallic=0.9, rough=0.3)
    m_post = material("ACCEL_Mat_Post", (0.35, 0.40, 0.52), metallic=0.5, rough=0.4)
    package("ACCEL", c, root, (3.0, 2.0), m_base, m_wall)
    TRAVEL, POST_X, MASS_HALF = 0.38, 1.15, 0.50
    rest = POST_X - MASS_HALF
    mass = box("ACCEL_Mass", (2 * MASS_HALF, 1.0, 0.14), (0, 0, 0.17), c, m_mass, root, bevel=0.03)
    m_hole = material("ACCEL_Mat_Hole", (0.05, 0.05, 0.07), rough=0.8)
    m_comb = material("ACCEL_Mat_FixedComb", (0.85, 0.50, 0.25), metallic=0.9, rough=0.35)
    for i in range(4):  # etch holes: a grid of small openings on the mass
        for j in range(4):
            box(f"ACCEL_MassHole_{i + 1}{j + 1}", (0.07, 0.07, 0.004), (-0.3 + 0.2 * i, -0.3 + 0.2 * j, 0.071), c, m_hole, mass)
    # sensing combs: fingers on the mass slide between fixed fingers, so their overlap changes with position
    FINGER, BLOCK_X = 0.50, 1.00
    for sy, row in ((-1, "S"), (1, "N")):
        box(f"ACCEL_CombArm_{row}", (0.08, 0.37, 0.10), (0, sy * 0.685, 0.0), c, m_mass, mass)
        for k, y in enumerate((0.58, 0.68, 0.78)):
            for sx, side in ((-1, "W"), (1, "E")):
                f = box(f"ACCEL_MovingFinger_{row}{side}{k + 1}", (FINGER, 0.035, 0.08), (sx * 0.04, sy * y, 0.0), c, m_mass, mass, origin_min_x=True)
                f.rotation_euler = (0, 0, 0 if sx > 0 else math.pi)
        for sx, side in ((-1, "W"), (1, "E")):
            box(f"ACCEL_CombBlock_{row}{side}", (0.12, 0.34, 0.20), (sx * BLOCK_X, sy * 0.69, 0.10), c, m_comb, root, bevel=0.015)
            for k, y in enumerate((0.63, 0.73)):
                f = box(f"ACCEL_FixedFinger_{row}{side}{k + 1}", (FINGER, 0.035, 0.08), (sx * (BLOCK_X - 0.06), sy * y, 0.17), c, m_comb, root, origin_min_x=True)
                f.rotation_euler = (0, 0, math.pi if sx > 0 else 0)
    bond_pads("ACCEL", c, root, 1.28, 0.78)
    for sx, side in ((-1, "W"), (1, "E")):
        for sy, row in ((-1, "S"), (1, "N")):
            box(f"ACCEL_Post_{side}{row}", (0.16, 0.16, 0.22), (sx * (POST_X + 0.08), sy * 0.32, 0.11), c, m_post, root, bevel=0.02)
            s = zigzag(f"ACCEL_Spring_{side}{row}", (sx * POST_X, sy * 0.32, 0.17), c, m_spring, root)
            s.rotation_euler = (0, 0, 0 if sx < 0 else math.pi)  # unit beam always points from its post to the mass
            s.scale = (rest, 1, 1)
            # when the mass moves +X the west springs stretch and the east springs compress
            drive(s, "scale", root, "displacement", 0, offset=rest, gain=TRAVEL if sx < 0 else -TRAVEL)
    control(root, "displacement", 0.0, -1.0, 1.0, "Mass position: -1 = fully toward -X, +1 = fully toward +X (jolt direction)")
    control(root, "mass_glow", 0.0, 0.0, 20.0, "Emission of the moving mass")
    drive(mass, "location", root, "displacement", 0, gain=TRAVEL)
    drive_bsdf(m_mass, "Emission Strength", root, "mass_glow")
    empty("ANCHOR_AccelMass", (0, 0, 0.24), c, mass, 0.1)
    empty("CAM_Target_Accel", (0, 0, 0.17), c, root, 0.2, "SPHERE")
    save(ASSETS / "sensor_accel_concept.blend")


def build_gyro():
    reset()
    c = new_collection("ASSET_SensorGyro")
    root = empty("GYRO_Root", (0, 0, 0), c, size=0.5)
    m_base = material("GYRO_Mat_Base", (0.08, 0.15, 0.20), metallic=0.3, rough=0.5)
    m_wall = material("GYRO_Mat_Wall", (0.16, 0.27, 0.34), metallic=0.4, rough=0.45)
    m_ring = material("GYRO_Mat_Ring", (0.20, 0.80, 0.95), metallic=0.8, rough=0.28, emission=(0.10, 0.85, 1.00), strength=0.0)
    m_spoke = material("GYRO_Mat_Spoke", (0.80, 0.82, 0.86), metallic=0.9, rough=0.3)
    m_pad = material("GYRO_Mat_Pad", (0.85, 0.50, 0.25), metallic=0.9, rough=0.35)
    package("GYRO", c, root, (2.6, 2.6), m_base, m_wall)
    cylinder("GYRO_Hub", 0.14, 0.24, (0, 0, 0.12), c, m_wall, root, bevel=0.02)
    rotor = empty("GYRO_Rotor", (0, 0, 0.19), c, root, 0.3, "CIRCLE")
    torus("GYRO_Ring", 0.78, 0.065, (0, 0, 0), c, m_ring, rotor)
    for k in range(8):  # folded spring spokes between hub and ring
        a = 2 * math.pi * k / 8
        sp = zigzag(f"GYRO_Spoke_{k + 1}", (0.14 * math.cos(a), 0.14 * math.sin(a), 0), c, m_spoke, rotor, folds=5, amp=0.045, thick=0.028, height=0.05)
        sp.rotation_euler = (0, 0, a)
        sp.scale = (0.60, 1, 1)
        box(f"GYRO_RingMark_{k + 1}", (0.05, 0.16, 0.012), (0.78 * math.cos(a + math.pi / 8), 0.78 * math.sin(a + math.pi / 8), 0.062), c, m_spoke, rotor).rotation_euler = (0, 0, a + math.pi / 8)
    for k in range(8):  # eight fixed electrodes around the ring: four large drive pads, four small sense pads
        a = math.pi / 4 * k
        big = k % 2 == 0
        p = box(f"GYRO_Pad_{k + 1}", (0.10, 0.50 if big else 0.26, 0.16), (1.05 * math.cos(a), 1.05 * math.sin(a), 0.14), c, m_pad, root, bevel=0.015)
        p.rotation_euler = (0, 0, a)
    cylinder("GYRO_HubCap", 0.09, 0.03, (0, 0, 0.255), c, m_pad, root, bevel=0.008)
    bond_pads("GYRO", c, root, 1.08, 1.08)
    control(root, "twist", 0.0, -1.0, 1.0, "Ring twist relative to the package when the car turns: +-1 = +-40 degrees")
    control(root, "vibration", 0.0, -1.0, 1.0, "Ring breathing: stretches along X at +1 and along Y at -1")
    control(root, "ring_glow", 0.0, 0.0, 20.0, "Emission of the ring")
    rotor.rotation_mode = "XYZ"
    drive(rotor, "rotation_euler", root, "twist", 2, gain=math.radians(40))
    drive(rotor, "scale", root, "vibration", 0, offset=1.0, gain=0.14)
    drive(rotor, "scale", root, "vibration", 1, offset=1.0, gain=-0.14)
    drive_bsdf(m_ring, "Emission Strength", root, "ring_glow")
    empty("ANCHOR_GyroRing", (0.78, 0, 0), c, rotor, 0.1)
    empty("CAM_Target_Gyro", (0, 0, 0.19), c, root, 0.2, "SPHERE")
    save(ASSETS / "sensor_gyro_concept.blend")


def build_baro():
    reset()
    c = new_collection("ASSET_SensorBaro")
    root = empty("BARO_Root", (0, 0, 0), c, size=0.5)
    m_base = material("BARO_Mat_Base", (0.08, 0.18, 0.12), metallic=0.3, rough=0.5)
    m_wall = material("BARO_Mat_Wall", (0.17, 0.32, 0.22), metallic=0.4, rough=0.45)
    m_cav = material("BARO_Mat_Cavity", (0.03, 0.05, 0.04), rough=0.7)
    m_mem = material("BARO_Mat_Membrane", (0.45, 0.95, 0.60), metallic=0.5, rough=0.25, emission=(0.25, 1.00, 0.40), strength=0.0)
    m_rim = material("BARO_Mat_Rim", (0.75, 0.80, 0.78), metallic=0.9, rough=0.3)
    m_pad = material("BARO_Mat_Strain", (0.90, 0.55, 0.20), metallic=0.9, rough=0.35)
    package("BARO", c, root, (2.6, 2.6), m_base, m_wall, wall_h=0.20)
    R, Z = 0.85, 0.42
    # hollow sealed chamber under the membrane, so the membrane has room to flex down
    tube("BARO_CavityWall", R + 0.10, R - 0.02, Z - 0.02, (0, 0, 0), c, m_wall, root)
    cylinder("BARO_CavityFloor", R, 0.04, (0, 0, 0.02), c, m_cav, root, segments=64)
    torus("BARO_Rim", R, 0.05, (0, 0, Z), c, m_rim, root)
    mem = disc_membrane("BARO_Membrane", R, (0, 0, Z + 0.01), c, m_mem, root)
    sol = mem.modifiers.new("Thickness", "SOLIDIFY")
    sol.thickness, sol.offset = 0.025, 0.0
    # darker concentric bands are part of the membrane mesh, so they bend with it and make the dip readable
    mem.data.materials.append(material("BARO_Mat_MembraneBand", (0.10, 0.45, 0.25), metallic=0.5, rough=0.3))
    for p in mem.data.polygons:
        if p.index // 64 in (2, 5, 8, 11):
            p.material_index = 1
    bond_pads("BARO", c, root, 1.08, 1.08)
    mem.shape_key_add(name="Basis")
    key = mem.shape_key_add(name="Deflect")
    key.slider_min, key.slider_max = -1.0, 1.0
    for i, v in enumerate(mem.data.vertices):
        r = min(1.0, math.hypot(v.co.x, v.co.y) / R)
        key.data[i].co = (v.co.x, v.co.y, -0.32 * (1 - r * r) ** 2)  # clamped-plate profile, edge stays fixed
    for k in range(4):
        a = math.pi / 2 * k + math.pi / 4
        p = box(f"BARO_Strain_{k + 1}", (0.26, 0.06, 0.02), ((R - 0.16) * math.cos(a), (R - 0.16) * math.sin(a), Z + 0.03), c, m_pad, root)
        p.rotation_euler = (0, 0, a)
    control(root, "pressure", 0.0, -1.0, 1.0, "+1 = outside air pushes the membrane in, -1 = membrane bulges out")
    control(root, "membrane_glow", 0.0, 0.0, 20.0, "Emission of the membrane")
    drive(mem.data.shape_keys, 'key_blocks["Deflect"].value', root, "pressure")
    drive_bsdf(m_mem, "Emission Strength", root, "membrane_glow")
    empty("ANCHOR_BaroMembrane", (0, 0, Z + 0.02), c, root, 0.1)
    empty("CAM_Target_Baro", (0, 0, Z), c, root, 0.2, "SPHERE")
    save(ASSETS / "sensor_baro_concept.blend")


build_phone_interior()
build_accel()
build_gyro()
build_baro()
print("MECHANISM_ASSETS_DONE")
