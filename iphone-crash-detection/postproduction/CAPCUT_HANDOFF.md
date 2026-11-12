# CapCut Pro — shot-by-shot handoff

FPS: 30; frames: 2067; timeline: 68.900s.

1. Blender MUST use Eevee, with NO overlay/labels/subtitles baked into shot frames.
2. Render each shot individually to PNG images. Encode into high-quality MP4 with FFmpeg and validate dimensions, FPS, frame count and actual playback.
3. As soon as ONE shot passes QA, encode and import that MP4 into the SAME active CapCut Pro project. Adjust VO sync, cut timing and editing now. STOP before rendering the next shot by default, until the user confirms CapCut import and edit. This is MANUAL unless supported graphical control is genuinely available.
4. Edit pacing against recorded Indonesian VO. Narration should be understandable around age 7: short, everyday language, without unexplained technical jargon or CTA.
5. Import word_captions.srt if produced, check every word against recorded speech, then style captions word-by-word in CapCut. If timings are absent, align manually or generate accurate word timestamps with an audio aligner; never fabricate by word-count division.
6. Refer to editorial_cues.csv: choose motivated transitions, add transition-specific whoosh/soft movement SFX and separate contextual scene SFX. Avoid overusing transitions; add low BGM with ducking under voice.
7. Never use Blender/VSE/compositor or FFmpeg to concatenate finished shots. Export final 1080x1920 H.264 30 fps + AAC ONLY from CapCut after all editing; inspect on a mobile-sized screen.

This handoff does not create a CapCut project or auto-insert clips into CapCut. A valid existing MP4 is not proof its content was inspected. No copyrighted sound assets are supplied.
