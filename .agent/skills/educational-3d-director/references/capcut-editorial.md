> **v4 binding override:** Read `capcut-first-workflow.md`. Never stitch the final video in Blender or FFmpeg. Import/edit each shot in CapCut before continuing to the next render unless user explicitly chooses batch mode.

# CapCut Pro editorial standard — each finished shot

For each shot when it passes QA:
1. Export a clean `shot_XX.mp4` (Eevee render via PNG sequence + FFmpeg), no overlays or burned-in subtitle text.
2. Add/update `postproduction/edit_decisions.csv`, `postproduction/shot_status.json` and `postproduction/CAPCUT_HANDOFF.md`; label the shot `READY_FOR_CAPCUT` only after validating the video file.
3. **CapCut import/edit is a manual action** unless a real supported integration is accessible. Recommend importing the clip immediately into the active CapCut Pro project and placing in sequence at its current editorial position, with the narration as timing anchor. Never claim that a clip was inserted into CapCut without evidence.
4. Plan transitions at *specific shot boundaries*, not each cut by default. Prefer match cut, clean hard cut, restrained zoom/push or short dissolve; add whoosh/swipe or soft impact SFX selectively at meaningful transitions. Avoid flashy transitions that obscure explanations.
5. SFX: touch/tap, movement, soft mechanical clicks, material and UI feedback only when consistent with what viewers see; separate `transition_sfx` vs `scene_sfx` in cue sheet. Never make scientific field lines sound like actual electricity unless clearly stylized.
6. BGM under voiceover with ducking. Start with VO and keep it clearly intelligible on phone speakers; no fixed universal loudness ratio.
7. **Word-by-word captions**: one spoken word per subtitle cue, timed to *recorded, approved audio*. Prefer verified word timestamps from forced alignment or careful manual timing. Do not invent timestamps by dividing sentence duration equally. Preserve punctuation with the final word when sensible; handle hesitations/repetitions as spoken. Create `word_captions.srt` (one word/cue) and `word_captions.csv`; CapCut import behavior varies, so inspect the result and style as dynamic word-by-word captions in CapCut. If CapCut version lacks required import/styling, manually align/edit there. Provide a manual-review flag for poor/conflicting alignment.
8. To keep subtitles legible: small number of words simultaneously, high contrast, consistent positioning inside platform-safe zones; no permanent full-screen technical overlays. The zero-overlay rule refers to **Blender render** and to absence of explanatory baked-in overlays; word captions belong to CapCut final edit by user request.
9. Final export after editorial completion: 1080x1920, 30 fps, H.264, AAC. Review at native resolution with sound and captions. No CTA unless explicitly requested.

## What can be automated
- FFmpeg shot encoding, verifying clip properties; generating shot list, editable transition/SFX recommendations and word-level subtitle files from valid timestamps.
- Creating an import-ready folder after each completed shot.

## What is not promised
- Direct API control of CapCut UI, automatic project insertion, proprietary CapCut project creation, auto-acquisition/licensing of SFX/BGM, or accurate word timings without authoritative audio/alignment.
