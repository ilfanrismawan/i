"""Bundle all editorial assets into postproduction/capcut_import_package.
Creates symlinks or copies of clips, audio, and subtitle files for 1-click import into CapCut.
"""
import shutil
from pathlib import Path

PROJECT = Path(r"c:\Users\HOG-PC001\Documents\i\iphone-crash-detection")
PACKAGE_DIR = PROJECT / "postproduction" / "capcut_import_package"
PACKAGE_DIR.mkdir(parents=True, exist_ok=True)

# 1. Copy/link all 18 MP4s
for i in range(1, 19):
    src = PROJECT / "renders" / f"shot_{i:02d}.mp4"
    dst = PACKAGE_DIR / f"{i:02d}_shot_{i:02d}.mp4"
    if src.exists():
        shutil.copy2(src, dst)
        print(f"Copied: {dst.name}")

# 2. Copy voiceover
vo_src = PROJECT / "audio" / "voice_over.mp3"
if vo_src.exists():
    shutil.copy2(vo_src, PACKAGE_DIR / "voice_over.mp3")
    print("Copied: voice_over.mp3")

# 3. Copy subtitles
shutil.copy2(PROJECT / "postproduction" / "captions.srt", PACKAGE_DIR / "captions.srt")
shutil.copy2(PROJECT / "postproduction" / "word_captions.srt", PACKAGE_DIR / "word_captions.srt")
print("Copied: captions.srt & word_captions.srt")
