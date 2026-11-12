# CapCut-first editorial handoff (MANDATORY v4)

## Non-negotiable responsibilities

**Blender = only 3D shot production.** Build and animate assets, render *individual shot* frame sequences with Eevee. Blender VSE, Blender compositor, and Blender animation timelines MUST NOT concatenate, crossfade, or arrange all rendered shots into a final film. A master Blender timeline MAY exist as a technical staging/continuity reference, but MUST NOT be used as final edited export.

**FFmpeg = clip conversion and verification only.** It may encode a single shot's frame sequence to that shot's MP4, probe media, perform delivery conversions. It MUST NOT concatenate all shots into final movie, burn subtitles, put on transitions, or add final sound design.

**CapCut Pro = sole editorial assembly and finishing.** Place shots on editing timeline, trim/retime against approved VO, add transitions, scene SFX, transition SFX, BGM + ducking, word-by-word subtitles, perform finishing and export 1080x1920/30fps. Do not burn narration, overlay, title, labels, subtitle into Blender shot; diegetic smartphone application UI is permitted.

## Shot lifecycle (blocking gate)

1. `PLANNED` → `ANIMATED` → `RENDERING` → `RENDERED` → `QA_PASSED` → `CLIP_READY_FOR_CAPCUT`
2. Immediately encode and verify the single shot clip (FFprobe full dimensions/FPS/duration + playable file). Create editor handoff with source shot range, narration beat, recommended trim, transition, separate scene and transition SFX, VO timing, caption support.
3. Mark `WAITING_FOR_CAPCUT_IMPORT` and **STOP**. Do NOT render the next shot yet for sequential mode. User imports the clip into the *existing* CapCut project and places/edits it; add VO, sound and captions as timing exists.
4. Only after user confirms should the status be marked `IMPORTED_IN_CAPCUT` then `EDITED_IN_CAPCUT`, and the next shot begins. If no actual CapCut access, do not claim those statuses and do not fabricate screenshots or editing output.
5. Exception: user can explicitly authorize batch rendering, but still hand off every shot immediately and do not perform final compositing in Blender/FFmpeg.

The same CapCut project remains the primary timeline across all shots. Avoid creating a new project for each clip. Capture user-confirmed actual clip placement/edited status separately from media QA.

## Word-by-word captions

- Align to the final **recorded** Indonesian voice-over audio, not a guessed reading duration. Accept actual per-word timestamps from an aligner plus user/editor review.
- One spoken word per SRT cue; handle punctuation, overlaps and revised recording. When timing is unavailable, deliver only a caption-work checklist, not fake SRT timings.
- Captions get imported and styled in CapCut. The same subtitle style persists across shots; refine pacing, emphasis, and platform safe area manually.

## Audio and pacing

- Preferred sequence: choose/record VO → mark beats → storyboard and time shots → render one shot → CapCut trim against VO → sync word captions + transitions + SFX → next shot.
- Give per-shot cue rows: `shot_id`, `vo_excerpt`, `vo_in/out`, `visual_event`, `scene_sfx`, `transition_type`, `transition_sfx`, `music_notes`, `caption_status`, `capcut_status`.
- Recommend motivated hard cuts, match cuts, L/J cuts, occasional whip/zoom transitions where the visual link justifies them; do not add a flashy transition to every cut. Sound effects must serve the visual, not mask the VO.

## Honest execution / unavailable CapCut control

- Existing standalone Python skill has **no supported CapCut GUI control** or native editable CapCut project creation. Do not automate `.ccproj`/JSON internal formats by guessing. If independently authorized, connected computer-use control is genuinely available, it may be used for CapCut GUI and confirmed visually; otherwise explicitly require user import/edit confirmation.
- Completion report must distinguish (a) clip made, (b) CapCut handoff prepared, and (c) user-confirmed CapCut import/edit. Never collapse (a) into (c).
