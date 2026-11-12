# Virtual Cinematography Director — v5

## Purpose
Exploit freedom unavailable to conventional physical cameras to *teach something*. A camera can pass through a solid object only by an authored cutaway, hidden geometry, material transition, matched set switch, or non-physical camera space. Do not pretend that Blender's camera can see through opaque geometry by itself. All effects remain stylized scientific explanations, not evidence of real micro-scale appearance.

## Required creative sequence
1. Map voice-over sentence → specific claim/reveal → physical/mechanism location → intended audience discovery.
2. Break into visual **beats** (what is learned), then into shots (how it is seen). One beat may need multiple shots. ~12–20 meaningful shots per 60 seconds is a starting heuristic, not a mandate.
3. Design an *angle ladder*: wide familiar context → observed contact → profile proof → macro evidence → impossible scale dive → cross-section → mechanism close-up → process outcome → return to familiar view. Adapt each episode instead of reusing a fixed sequence.
4. Give every shot a real focal target, shot scale, camera angle family, motivated movement, start/end compositions, new visual information and transition plan. Include both moving and locked-off compositions.
5. For each nonphysical technique, specify `reveal_technique`, `geometry_visibility_strategy`, `scale_transition_strategy`, and `scientific_disclaimer` when appropriate; choose transitions that are visually coherent. Do not automatically apply these to every shot.
6. Make 9:16 safe-area and readability tests before final render. The audience must be able to tell *where* the camera is and *what changed*.

## Reusable virtual camera techniques (choose selectively)

| Technique ID | What it shows | Blender implementation guide | Common failure |
|---|---|---|---|
| `micro_flythrough` | Dive past macroscopic surface into microscopic mechanism | Two scenes or differently scaled collection instances + matched camera pose, transition/match-cut + true cross section; animate camera path; hide occluding geometry | Real-world scale impossible in one set; clipping/z-fighting |
| `exploded_flight` | Travel between disassembled layers | Use existing explode controller; camera Bezier path through measured gaps; visibility/near clip QA | Camera intersects layer or components overlap |
| `interior_pov` | View from inside a solid product/body | Controlled cutaway mesh/material or separate interior set; camera follows corridor anchor | Unrealistic visual presented as actual photo |
| `signal_follow` | Follow abstract electricity, fluid flow, light path | Curve path + Follow Path / evaluated position; show *schematic* tracer and avoid literal glowing electrons | Signal is falsely represented as visible matter |
| `xray_orbit` | Reveal internal components while circling object | Animate non-destructive outer-shell visibility using shot-specific material overrides; lock interior anchoring | Transparent sorting and scientific ambiguity |
| `bullet_time_orbit` | Freeze a crucial moment and inspect it | Retimed/frozen asset animation; orbit camera about contact target; return to action | Entire video freezes or viewers lose continuity |
| `multiscale_pullback` | Show same process from micro to human scale | Matched shot-space sets with scale-aware camera, no fake huge lens zoom; align landmarks | Unmotivated teleport jump |
| `time_frozen_flight` | Examine parts of a transient event while frozen | Freeze evaluated action at event time, animate camera independently; separate motion resumes | Frozen object state is not deterministic |
| `reverse_causality` | Trace current effect back to its causes | Reverse pre-baked causal animation with clear narration that it is a reverse explanation | Suggests real physics runs backwards |
| `portal_matchcut` | Connect two distant objects/sets by a common shape | Pose/shape/lighting match, cut or masking in CapCut; Blender renders each shot independently | Invisible edit faked as continuous single shot |
| `infinite_crane` | Show a large-scale structure | Camera rail/Bezier path + level-of-detail sets | Lost spatial reference or missing background |
| `non_euclidean_reveal` | Rearrange complex spatial relations for clarity | Explicitly conceptual warp of object transforms (not real material behavior) | Misleads viewers about actual geometry |
| `perspective_morph` | Move from product look to schematic understanding | Transition from perspective to orthographic via matched cut or calibrated interpolation; maintain projected focal size | Perspective jumps distort scale |
| `extreme_macro_track` | Follow tiny moving component | Camera follows tracked object with speed limits and adequate depth of field | Unreadable details and severe clipping |

## Variation requirements
- In every five consecutive shots, usually use >=3 angle families, >=2 movement families and >=2 shot sizes. Do not treat these as hard artistic quotas: justify any purposeful exception.
- Avoid more than two back-to-back orbit shots. Do not use `micro_flythrough`, `xray_orbit`, or other signature effects solely to meet a quota; explain their revelation purpose. For a 60-second mechanism explainer, include one or more scale/visibility reveals *where the subject warrants it*, but a safety-critical or historically uncertain reconstruction can prefer clear, stationary explanatory compositions.
- If a shot uses extreme movement, follow it with an anchor shot or clear visual orientation before another disorienting move.
- Keep 3D camera movement separate from CapCut transitions. Blender renders each shot individually in Eevee, **without editorial overlays**, and the final video is assembled only in CapCut.

## Camera rig and animation rules
- Reuse existing camera rigs; create shot-specific cameras only when needed. Build named target empties, paths, and constraints with no destructive changes to source assets. Maintain world/local transforms consistently.
- Parameterize camera path endpoints, look-at point, lens/orthographic scale, interpolation, depth of field, clipping, focus target and optional subject-visibility gate. No assumptions about actual model size.
- Avoid cubic overshoot through geometry, collision with meshes, camera entering an opaque object before material/visibility change, unpredictable handler state, and unreproducible procedural randomness. Evaluate frames out of order and headlessly.
- Distinguish *physical camera movement* from *set/geometry manipulation*, including tricks such as breaking physical scale; document when it is a visual metaphor.
- Keep technical diagrams legible at portrait phone size; hide all debug and overlays at final rendering.

## Shot planning schema (recommended fields)
`id, beat, start_frame, end_frame, narration, subject, new_information, camera_angle_reason, shot_size, angle_family, camera_move, camera_movement_reason, movement_family, movement_start, movement_end, focal_target, camera_rig, lens_mm_or_ortho, reveal_technique, reveal_reason, geometry_visibility_strategy, scale_transition_strategy, transition_intent, orientation_anchor, cinematic_qa, technical_qa`.

`camera_move` may remain a familiar camera vocabulary, while `reveal_technique` is a distinct conceptual technique such as `micro_flythrough`. Do not label all camera moves `orbit` even when the reveal is unusual. Map a complex reveal to multiple shots when necessary.

## Review before rendering
- Run `python scripts/validate_shot_diversity.py shot_plan.json` and `python scripts/validate_virtual_cinematography.py shot_plan.json`; investigate warnings rather than padding meaningless shots.
- Generate specific camera briefs with `python scripts/build_camera_briefs.py shot_plan.json --output previews/camera_briefs`.
- Render contact sheet (representative frame per shot) + short motion tests for high-risk moves. Check time, screen clipping, cutaway visibility, spatial continuity, causal clarity and visual accessibility.
- For optimization on modest GPUs/APUs: do not overuse transparency/volumetrics, use Eevee, short reusable shot instances, visibility by scene, and preview resolution before final frames.
