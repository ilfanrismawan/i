"""Generate standard SRT sentence-level and word-level subtitles for CapCut Pro.
Reads shot_plan.json and generates captions.srt and word_captions.srt in postproduction/.
"""
import json
from pathlib import Path

PROJECT = Path(r"c:\Users\HOG-PC001\Documents\i\iphone-crash-detection")
SHOT_PLAN_FILE = PROJECT / "shot_plan.json"
POST_DIR = PROJECT / "postproduction"
POST_DIR.mkdir(parents=True, exist_ok=True)

def format_srt_time(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int(round((seconds - int(seconds)) * 1000))
    if millis >= 1000:
        millis = 999
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

def main():
    with open(SHOT_PLAN_FILE, "r", encoding="utf-8") as f:
        plan = json.load(f)

    shots = plan["shots"]

    # 1. Generate sentence-level captions.srt
    sentence_srt_lines = []
    # 2. Generate word-level captions.srt
    word_srt_lines = []

    current_timeline_time = 0.0
    word_index = 1

    for i, shot in enumerate(shots, start=1):
        shot_duration = shot["duration_seconds"]
        shot_start = current_timeline_time
        shot_end = current_timeline_time + shot_duration
        narration = shot["narration"].strip()

        # Sentence cue
        sentence_srt_lines.append(str(i))
        sentence_srt_lines.append(f"{format_srt_time(shot_start)} --> {format_srt_time(shot_end)}")
        sentence_srt_lines.append(narration)
        sentence_srt_lines.append("")

        # Word-level cues
        words = narration.split()
        if words:
            word_dur = shot_duration / len(words)
            for j, word in enumerate(words):
                w_start = shot_start + j * word_dur
                w_end = shot_start + (j + 1) * word_dur
                word_srt_lines.append(str(word_index))
                word_srt_lines.append(f"{format_srt_time(w_start)} --> {format_srt_time(w_end)}")
                word_srt_lines.append(word)
                word_srt_lines.append("")
                word_index += 1

        current_timeline_time = shot_end

    sentence_file = POST_DIR / "captions.srt"
    word_file = POST_DIR / "word_captions.srt"

    with open(sentence_file, "w", encoding="utf-8") as f:
        f.write("\n".join(sentence_srt_lines))
    print(f"Created: {sentence_file}")

    with open(word_file, "w", encoding="utf-8") as f:
        f.write("\n".join(word_srt_lines))
    print(f"Created: {word_file}")

if __name__ == "__main__":
    main()
