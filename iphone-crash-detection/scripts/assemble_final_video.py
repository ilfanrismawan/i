"""Assemble all 18 rendered shots + voiceover audio + subtitles into the final master video.
Outputs:
  iphone-crash-detection/renders/final_iphone_crash_detection.mp4
"""
import subprocess
from pathlib import Path

PROJECT = Path(r"c:\Users\HOG-PC001\Documents\i\iphone-crash-detection")
RENDERS_DIR = PROJECT / "renders"
AUDIO_FILE = PROJECT / "audio" / "voice_over.mp3"
SRT_FILE = PROJECT / "postproduction" / "captions.srt"
OUTPUT_FILE = RENDERS_DIR / "final_iphone_crash_detection.mp4"

def main():
    # 1. Create concat list file
    concat_list = RENDERS_DIR / "concat_list.txt"
    lines = []
    for i in range(1, 19):
        shot_path = (RENDERS_DIR / f"shot_{i:02d}.mp4").resolve()
        # Format for ffmpeg concat demuxer: file 'path'
        # Windows backslashes need to be forward slashes or escaped
        formatted_path = str(shot_path).replace("\\", "/")
        lines.append(f"file '{formatted_path}'")

    with open(concat_list, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(f"Created concat list: {concat_list}")

    # 2. Run FFmpeg:
    # Concatenate video streams, mux voice_over.mp3 as audio stream,
    # burn subtitles with subtitles filter, encode to high quality 1080x1920 MP4
    srt_formatted = str(SRT_FILE.resolve()).replace("\\", "/").replace(":", "\\:")
    sub_filter = f"subtitles='{srt_formatted}':force_style='FontName=Arial,FontSize=16,Bold=1,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=1,Outline=2,Alignment=2,MarginV=60'"

    cmd = [
        "ffmpeg",
        "-f", "concat",
        "-safe", "0",
        "-i", str(concat_list),
        "-i", str(AUDIO_FILE),
        "-vf", sub_filter,
        "-c:v", "libx264",
        "-crf", "18",
        "-preset", "slow",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        str(OUTPUT_FILE),
        "-y"
    ]

    print("Running FFmpeg assembly...")
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    if res.returncode != 0:
        print("FFmpeg error with subtitles filter, falling back to clean concat with audio...")
        print(res.stdout[-1000:])
        # Fallback without burnt subtitles in case fontconfig or subtitles filter is unavailable
        cmd_fallback = [
            "ffmpeg",
            "-f", "concat",
            "-safe", "0",
            "-i", str(concat_list),
            "-i", str(AUDIO_FILE),
            "-c:v", "libx264",
            "-crf", "18",
            "-preset", "medium",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            "-b:a", "192k",
            "-shortest",
            str(OUTPUT_FILE),
            "-y"
        ]
        res_fb = subprocess.run(cmd_fallback, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        if res_fb.returncode != 0:
            print("Fallback failed:\n" + res_fb.stdout[-1000:])
            return False

    print(f"SUCCESS: Final video created at {OUTPUT_FILE}")

    # Verify with ffprobe
    cmd_probe = [
        "ffprobe",
        "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=width,height,r_frame_rate,nb_frames,duration",
        "-of", "default=noprint_wrappers=1",
        str(OUTPUT_FILE)
    ]
    res_probe = subprocess.run(cmd_probe, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    print("Video Stream:\n" + res_probe.stdout.strip())

    cmd_probe_a = [
        "ffprobe",
        "-v", "error",
        "-select_streams", "a:0",
        "-show_entries", "stream=codec_name,sample_rate,channels,duration",
        "-of", "default=noprint_wrappers=1",
        str(OUTPUT_FILE)
    ]
    res_probe_a = subprocess.run(cmd_probe_a, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    print("Audio Stream:\n" + res_probe_a.stdout.strip())

    return True

if __name__ == "__main__":
    main()
