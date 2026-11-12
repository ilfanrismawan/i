> **v4 shot design:** A narrative beat is not one fixed camera shot. For a 60-second video plan ~12–20 distinct information-bearing camera shots (flexibly) and audit variety with `references/camera-shot-diversity.md`. Do not default to 6-7 long shots.

# Storyboard specification

Use shot_plan.json schema exemplified in `templates/shot_plan.example.json`. Each shot should contain IDs, `start_frame`, `end_frame` inclusive, required collections, camera, narration, mechanism/visual claim, motion, transitions, lighting and QA criteria.

## Frames
For N-second film at F FPS, total frames N*F (start 1). For shot durations d_i, make each continuous inclusive frame range, e.g. [1,210], [211,450]; sum durations must match. Don't confuse 1-indexed frame endpoints with timestamp seconds.

## Script
Writing a 60-s Indonesian narrative: use measured voice-over if provided; otherwise estimate speaking time and mark provisional. Ensure explanations are accurate rather than packing dense claims. No automatic CTA. Retention relies on question → delayed reveal → mechanism → resolution.

## Camera grammar
- familiar wide/medium hero first
- macro push for "what you don't see"
- cutaway or exploded view only when physical relation matters
- orthographic technical hold for complex mechanisms
- process follow shot for signal/energy/material flow (label if abstract)
- matching orientation for shot continuity
- final pullback to everyday object

## 9:16 composition
1080×1920/30fps default. Reserve text and app-UI-safe space; adjust camera to subjects rather than shrinking all diagrams. Labels large enough to read on mobile. Avoid focus blur hiding scientific evidence. Animate within subject scale and do not bury detail in overly broad scene shots.

## Multi-shot dependencies
Carry shared event/trajectory/phase data across shots: same finger/contact, same machine movement, same flow path, same coordinate in UI. The effects should be caused by prior steps, not independently keyframed. If a time-remap is used, document it.
