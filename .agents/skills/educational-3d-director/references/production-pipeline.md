> **v4 editorial STOP gate:** Individual Eevee shot → encoded MP4 → CapCut Pro import/edit confirmation → next shot. Do not stitch clips in Blender or FFmpeg. See `capcut-first-workflow.md`.

# Production pipeline & quality gates

## Entry audit
Record topic, one-sentence audience question, platform, fps/resolution, duration, niche, language, tone, references, exact source assets, hardware/renderer, and factual confidence. If the user already supplied a project, inspect rather than scaffold over it.

## Scientific concept gate
For each on-screen claim create `concept`, `what is observed`, `internal mechanism`, `visual metaphor`, `what is simplified`, and `evidence/source to verify`. Separate actual mechanisms from illustrative overlay colors and inferred component geometry.

## Story gate
Draft hook → familiar action → impossible-to-see view → causal sequence → observable result → clear ending. Do not force CTAs. Each shot must have a purpose: establish scale, reveal geometry, trace input, show processing, prove output. Prefer 45–75 s unless requested otherwise. Compute frames exactly: duration × fps.

## Assets and interfaces gate
Reuse assets first. For each new asset define parent collection, local units/axes, location in screen/device coordinates, anchor empties, external dependencies, named controls and ranges, visibility policies, output `.blend`, scripts and previews. For each prior asset explicitly prohibit recreation. Maintain source-file hash checks when practical.

## Integration gate
Link assets or append non-destructively, create overrides where animation needs local control. Confirm upstream state drives downstream response; if frame order matters, bake events into a reproducible track. Avoid independent decorative effects disconnected from the story.

## Preview and render gate
1. Single-frame diagnostic render per shot.
2. Motion test for highest-risk transitions.
3. Full 360×640 or 540×960 low-res preview.
4. Validate time alignment, geometry intersections, camera framing, scientific meaning, consistent material/light treatment.
5. Full-resolution PNG sequence; resume incomplete frames.
6. Encode H.264 yuv420p to MP4, optional AAC audio; check count, fps, dimensions and duration.

## Failure policy
Do not claim a deliverable exists unless created and verified. If no Blender executable, generate scripts and report that preview renders remain unverified. If incompatible asset structure, preserve originals and create adapters. If video rendering is too expensive, deliver `.blend`, scripts, representative previews and exact remaining command.

## Deliverable minimum by phase
- planning: brief, shot plan, per-phase prompts, asset manifest
- asset: `.blend`, `bpy` generation/validation script, 2–3 previews, manifest delta
- mechanism: observable before/during/after previews, controls and scientific caveat
- animation: linked production scene, frame-continuity test, 7-ish shot storyboard
- final: frame outputs, MP4, render report, reproducible commands, limitation log
