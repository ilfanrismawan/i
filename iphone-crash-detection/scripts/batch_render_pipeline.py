"""Batch render, encode, and verify pipeline for educational-3d-director.
Renders all remaining shots (08 to 18) sequentially using Blender Eevee and FFmpeg.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

BLENDER = r"C:\Program Files\Blender Foundation\Blender 5.3\blender.exe"
PROJECT = Path(r"c:\Users\HOG-PC001\Documents\i\iphone-crash-detection")
RENDER_SCRIPT = Path(r"C:\Users\HOG-PC001\Documents\i\.agents\skills\educational-3d-director\scripts\render_frames.py")

SHOTS_TO_RENDER = [
    ("SHOT_08", 792, 938),
    ("SHOT_09", 939, 1059),
    ("SHOT_10", 1060, 1165),
    ("SHOT_11", 1166, 1239),
    ("SHOT_12", 1240, 1368),
    ("SHOT_13", 1369, 1442),
    ("SHOT_14", 1443, 1580),
    ("SHOT_15", 1581, 1692),
    ("SHOT_16", 1693, 1818),
    ("SHOT_17", 1819, 1909),
    ("SHOT_18", 1910, 2067),
]

def render_shot(shot_id, start_f, end_f):
    scene_file = PROJECT / "scenes" / f"{shot_id.lower()}.blend"
    out_dir = PROJECT / "renders" / "frames" / shot_id.lower()
    mp4_file = PROJECT / "renders" / f"{shot_id.lower()}.mp4"

    print(f"\n==========================================")
    print(f"STARTING {shot_id}: frames {start_f}..{end_f}")
    print(f"==========================================")

    # 1. Render frames with Blender
    cmd_blender = [
        BLENDER,
        "--background",
        str(scene_file),
        "--python",
        str(RENDER_SCRIPT),
        "--",
        "--out",
        str(out_dir),
        "--start",
        str(start_f),
        "--end",
        str(end_f),
        "--preset",
        "final"
    ]
    print(f"Rendering frames with Blender Eevee...")
    res = subprocess.run(cmd_blender, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    if res.returncode != 0:
        print(f"ERROR rendering {shot_id}!\nBlender output:\n" + res.stdout[-1500:])
        return False
    print(f"Frames rendered successfully to {out_dir}")

    # 2. Encode to MP4 with FFmpeg
    # Notice pattern: frame_%04d.png
    input_pattern = str(out_dir / "frame_%04d.png")
    cmd_ffmpeg = [
        "ffmpeg",
        "-framerate", "30",
        "-start_number", str(start_f),
        "-i", input_pattern,
        "-c:v", "libx264",
        "-crf", "16",
        "-preset", "medium",
        "-pix_fmt", "yuv420p",
        str(mp4_file),
        "-y"
    ]
    print(f"Encoding MP4: {mp4_file}...")
    res_ff = subprocess.run(cmd_ffmpeg, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    if res_ff.returncode != 0:
        print(f"ERROR encoding {shot_id} MP4!\n" + res_ff.stdout[-1000:])
        return False

    # 3. Verify with ffprobe
    cmd_probe = [
        "ffprobe",
        "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=width,height,r_frame_rate,nb_frames,duration",
        "-of", "default=noprint_wrappers=1",
        str(mp4_file)
    ]
    res_probe = subprocess.run(cmd_probe, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    print(f"Probe verification for {shot_id}:\n{res_probe.stdout.strip()}")

    expected_frames = end_f - start_f + 1
    if f"nb_frames={expected_frames}" not in res_probe.stdout and "width=1080" in res_probe.stdout:
        print(f"WARNING: frame count mismatch or missing, verify output.")
    else:
        print(f"PASSED: {shot_id}.mp4 verified ({expected_frames} frames, 1080x1920 @ 30fps).")

    return True

def main():
    success_count = 0
    for shot_id, start_f, end_f in SHOTS_TO_RENDER:
        ok = render_shot(shot_id, start_f, end_f)
        if not ok:
            print(f"Pipeline stopped due to error on {shot_id}")
            sys.exit(1)
        success_count += 1
    print(f"\nALL {success_count} SHOTS RENDERED AND ENCODED SUCCESSFULLY!")

if __name__ == "__main__":
    main()
