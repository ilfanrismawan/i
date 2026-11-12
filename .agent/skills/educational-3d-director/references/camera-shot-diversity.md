> **v5 update:** Read `virtual-cinematography.md` for advanced non-physical movement, required cross-section/scale strategies and per-shot camera briefs.

# Dynamic shot planning and cinematic camera language (v4)

## Story determines shot count

For a 45–75 second vertical fact explainer, **start with 12–20 shots per minute** (typically 12–20 for ~60 sec) as a creative planning target, not an inviolable numeric quota. Split a visual when its subject, mechanism state, storytelling purpose or vantage point changes. More shots are not automatically better; a complex mechanism may need a 5–7 second hold. Reject 6-shot/60-second autoplan unless beats demonstrably justify it.

Establish a separate **beat map** vs **shot list**. One narration beat may require 2–4 visual shots (establish → close-up → reveal → reaction). Shot duration usually 1.5–5s; preserve exceptional long holds for clarity. Every shot needs a meaningful new visual piece; no filler or repeated hero orbit. Time narration from actual voiceover if available; otherwise mark timing as provisional.

## Angle grammar

Choose angles from: eye-level three-quarter, low-angle hero, high-angle over-table, top-down orthographic, side-on cross-section, profile macro, over-the-shoulder, POV, front-on symmetry, extreme macro, under-glass/inside-object, isometric exploded assembly, wide establishing, diagonal reveal, rear 3/4; not all suit every topic. Vary shot scale (wide/medium/close-up/extreme macro). Every camera choice must explain what it reveals.

## Movement grammar

Choose from: locked-off with animated subject, slow dolly push/pull, controlled lateral truck, small arc orbit, crane/pedestal, tilt/pan motivated by tracked action, macro rack focus (not while scientific detail needs clarity), match-move, follow target, reveal with foreground parallax, controlled roll (rare), overhead drop-in, pull-through cutaway, reverse dolly reveal. Do not overuse zoom, orbit, or spin. Prefer physically coherent dolly to exaggerated focal zoom. Use safe easing with no camera penetration or 9:16 clipping.

## Sequence diversity gate

Evaluate every 5-shot window: at least 3 distinct **angle families**, at least 2 distinct **camera movement types** (locked-off counts), and meaningful shot-scale variation; make exceptions only with an explicit storytelling reason. Avoid >2 consecutive shots with same scale+angle+movement combination. Avoid >2 successive orbit shots. Prioritize motion of **scene objects** over constant camera motion. Track visual information gain per shot.

Use camera/lens/shot metadata:
`id, beat, duration, narration_excerpt, mechanism_step, subject, new_information, shot_size, angle_family, camera_move, move_start, move_end, focal_target, lens_mm_or_ortho, camera_rig, transition_intent, assets, frame_range, technical_QA`.

## What an engaging 60-second episode can look like

Illustrative structure (not fixed storyboard):
1. wide everyday establishing (locked); 2. over-the-shoulder action (truck-in); 3. fingertip extreme macro (locked); 4. profile contact (lateral); 5. under-glass cutaway (push-through); 6. isometric exploded layers (pedestal); 7. top-down sensor reveal (slow tilt); 8. diagonal TX detail (subtle parallax); 9. RX crossing macro (locked); 10. side-on baseline field (locked); 11. fingertip enters field (tracked dolly); 12. response hotspot overhead (small crane); 13. controller lead-in (match cut); 14. chip macro (controlled pan); 15. matrix transform (locked); 16. coordinate overlay visual represented by intrinsic sensor UI, not editor overlay (cut); 17. hand tap from profile (cut); 18. app close-up opens (locked); 19. pullback to original context (dolly-out).

Do not use this list verbatim for every video. Niche-specific camera design and information gain decide shot boundaries. Avoid simply cutting a long still shot into multiple identical angles for a quota.

## QA

Build shot-table and *contact sheet* with representative still per shot. Look for duplicate compositions, overly long static sections, insufficient focal variation, abrupt cuts, lost causal continuity, and vertical cropping. Render motion tests for cuts where source and destination camera axes are very different. No false technical labels or composited instructional overlays from Blender.
