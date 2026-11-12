# FFmpeg + CapCut Pro postproduction

Read **references/capcut-editorial.md** and **references/eevee-shot-render.md** for binding rules. Use Blender Eevee to render clean shots individually; encode each completed shot, hand it off for immediate import into CapCut Pro and edit with word-by-word subtitles, motivated transitions, scene SFX, transition SFX, voiceover and BGM. Word timing must come from approved audio alignment. Use `scripts/build_postproduction.py` to generate EDL and cue sheets. No direct CapCut API control is assumed.

**v4 override:** Blender and FFmpeg never create a final assembled multi-shot movie. The per-shot MP4s are ordered and edited in CapCut only. Require actual import/edit confirmation; see `capcut-first-workflow.md`.
