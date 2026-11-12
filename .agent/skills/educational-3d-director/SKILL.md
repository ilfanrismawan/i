---
name: educational-3d-director
description: Research and fact-check surprising educational topics; plan, build, animate, validate, and render reusable Blender 3D explainers across niches; prepare FFmpeg and CapCut Pro post-production handoffs. Use for unknown facts, topic discovery/ranking, storyboard, asset reuse, phased bpy production, cinematic TikTok/Reels video, and editorial QA. Do not use for simple text-only questions or basic image edits.
---

# Educational 3D Director v5.0 — Virtual Cinematography → Eevee → CapCut-First

Build **mechanism-first educational animations** using Blender and Python (`bpy`) with independent, reusable assets and phase gates. This skill works in Codex and Claude Code and must adapt to the *actual* installed Blender version and workspace.

## CRITICAL v5 VIRTUAL CINEMATOGRAPHY UPGRADE

- Read `references/virtual-cinematography.md` **before** drafting camera plans. Act as a creative virtual cinematographer, not a physical camera operator limited by cranes/dollies or miniature camera sizes.
- For each suitable episode, **consider** microscopic fly-through, exploded-view flight, inside-object POV, signal-follow camera, X-ray reveal, time-frozen/bullet-time orbit, multi-scale pullback, portal match-cut, reverse-causality journey, infinite crane, or perspective morph. Use a technique only if it makes a specific mechanism or hidden fact comprehensible; do not insert them to satisfy a quota.
- Each shot must record a specific new reveal, focal target, angle, camera move, movement purpose, shot size, beginning/ending composition, transition rationale and any geometry/scale trick. A camera alone cannot move through opaque material and reveal internals; use shot-scoped cutaway or visibility controls or a matched scaled set. Do not destructively edit previous assets.
- Mix spectacular shots with orientation/locked-off shots, and vary shot angle, size, axis and movement. Never fill time with repeated phone orbit/zoom or arbitrary camera motion. Render a contact sheet and short motion tests **before** full-resolution Eevee shot production.
- Run `scripts/validate_shot_diversity.py` AND `scripts/validate_virtual_cinematography.py` on `shot_plan.json`, then generate per-shot execution guides with `scripts/build_camera_briefs.py`. Warnings require creative review, not blind autofilling.
- **Preserve v4 CapCut rules:** Eevee-only, clean shots without baked editorial overlays, one independent shot MP4 at a time, CapCut for all assembly/VO/word-by-word subtitles/transitions/SFX. Never stitch shots in Blender/FFmpeg and never claim native CapCut editing without verified capability.

## Operating contract

## CRITICAL v4 STOP RULES (override all earlier broad production language)

- **NEVER assemble or concatenate completed shots inside Blender, Blender VSE, Blender compositor, or FFmpeg.** Blender produces **only** independent 3D shots; FFmpeg may encode a **single** shot into MP4. Final film assembly happens **only in CapCut Pro**.
- **Per-shot editorial gate:** render ONE shot using Eevee → QA → encode that shot MP4 → prepare handoff → STOP and require actual CapCut import/edit confirmation before proceeding to next shot by default. Do not claim a clip was inserted into or edited in CapCut unless a user confirmed it or a genuinely connected graphical operator performed and verified it. No native CapCut automation is bundled.
- **Dynamic storyboard:** choose shot count from narrative: typically **12–20 distinct shots for ~60 seconds**, not an inflexible requirement. A 60-second six-shot template is a planning failure unless justified. Each shot reveals new information; check camera angle, shot scale, camera movement, action and pacing variety. Read `references/camera-shot-diversity.md` and `references/virtual-cinematography.md`; run both camera validators. More cuts alone do not guarantee engagement.
- **No Blender overlay:** do not burn captions, labels, arrows, technical diagrams as 2D overlays, watermarks or debug screens; actual 3D mechanisms and diegetic phone UI are allowed. Word-by-word subtitles and other editorial finishes are added **inside CapCut**.
- **VO-first editing:** write Indonesian suitable for a seven-year-old, record/select approved VO, align real word timing, and make/adjust per-shot durations to narration. Subtitles, transitions, scene SFX, transition SFX, and BGM/ducking belong only to CapCut finishing.
- If these rules conflict with older project prompts, phase docs, or inherited Blender master timelines, follow THIS section. A Blender master timeline is allowed strictly as a technical preview/reference, **never as final stitched movie**.


1. **Inspect first.** Read repository/project files, existing `.blend` assets, manifests, scripts, target platforms, and supplied references. Treat reference videos as visual inspiration, not permission to reproduce protected imagery.
2. **Choose production mode:** `discover-facts`, `research`, `plan`, `asset`, `integrate`, `preview`, `render`, `postproduction`, `validate`, or `repair`. Infer from user request; if a phase is named, complete *only* that phase. A request for a complete project may advance phase-by-phase after gates, as resources permit.
3. **Always reuse completed work.** Never regenerate a completed asset, replace a source model, or silently reset rigs/materials. Work in new files. Save changes only to phase-specific outputs; keep source asset hashes when practical. When missing dependencies block exact integration, report them and use non-destructive adapters, not fabricated results.
4. **Ground the science.** For niche/fact discovery read `references/fact-research.md` and `references/creative-formats.md` first; for all projects read `references/science-and-story.md`. Research requires actual authorized sources; never mark a claim verified without source metadata and source inspection. Apply the evidence gate before production. Distinguish confirmed facts, plausible reconstructions, and stylized explanatory metaphors. Do not assert proprietary internals or fake measurements.
5. **Design before modeling.** Produce project brief, target audience, narrative question, visual reveals, asset audit, shot list, camera plan, and constraints. Follow `references/production-pipeline.md` and `references/storyboard-spec.md`.
6. **Plain-language scripts mandatory.** All viewer-facing spoken scripts must be natural Indonesian understandable by a ~7-year-old: short sentences, minimal jargon, simple accurate cause/effect, no CTA by default. Read `references/plain-language.md`. Verify facts before simplifying.
7. **Build in stages.** Generate only the next missing component. Each stage gets scoped deliverables, testable controls, renders, and a STOP condition. Prefer `scripts/plan_project.py` to scaffold a niche-agnostic plan and phase prompts.
8. **Use Blender scripting robustly.** Detect Blender and API version, inspect object names/transforms, use local coordinates and named attachment points, keep deterministic keyframe evaluation, support headless execution, avoid unsafe render-intensive operations without previews, and require compatible Eevee presets for rendering.
9. **Validate actual outputs.** Inspect representative renders if image access exists, reopen generated `.blend`, verify objects, animation controls, shot framing, scene links, and frame/output files. Do not claim validation or final video production unless checks were executed.
10. **Eevee-only rendering + clean frames.** Read `references/eevee-shot-render.md`. All final 3D frames must use Blender Eevee, rendering separate shots; no explanatory/text/subtitle/debug overlay baked into Blender. Preserve scene-native UI where narratively relevant. Do not switch to Cycles without explicit user-requested policy change.
11. **Cost/performance:** render blocking stills first, short motion tests second, full low-resolution preview third, and final PNG sequence/MP4 only after QA. Preserve resumable frame sequences and do not overwrite valid outputs unnecessarily.
12. **Incremental CapCut Pro delivery.** Every finished, verified shot must immediately generate its own CapCut-ready MP4 and handoff entry. Read `references/capcut-editorial.md`. Final editing in CapCut Pro includes **word-by-word subtitles**, transitions, scene SFX and transition SFX, VO/music. Word timing requires actual recorded audio/aligned timestamps or manual verification. Do not claim automatic CapCut project manipulation.
13. **Post-production:** Blender separate shot frames → FFmpeg encode *each individual shot* → confirmed CapCut Pro editorial handoff; read `references/postproduction.md`. Generate EDL CSV and word-level SRT only from verified word timing data. Do not claim native CapCut project creation or CapCut GUI automation.
14. **Completion response:** summarize completed scope, actual file paths, preview status, validation findings, blockers, and next stage. Never pretend background work is happening.

## Trigger examples

- "Buat animasi 3D edukasi bagaimana wireless charging bekerja menggunakan Blender + Codex".
- "Buat aset untuk proses pembuatan keramik, tahap demi tahap, jangan ulang model sebelumnya".
- "Bangun video 9:16 mengenai cara kerja jantung dengan animasi cutaway".
- "Lanjutkan tahap berikutnya dari proyek penjelasan layar sentuh".
- "Perbaiki Blender scene yang broken tanpa mengubah source assets".
- "Cari fakta unik yang benar-benar terbukti, pilih yang menarik untuk animasi 3D".
- "Buat EDL, subtitle SRT dan paket editing CapCut Pro dari shot Blender".

## Phase selection

| Phase | Deliverable | Gate |
|---|---|---|
| 0 Discover / Verify | topic shortlist + scored leads + evidence register + asset audit | factual claims checked; unverified claims held |
| 1 Story | script, reveal logic, storyboard & beat map | sequence communicates why/how |
| 2 Master assets | existing-asset integration or reusable principal meshes | dimensions, naming, silhouettes pass |
| 3 Mechanism components | internals, layers, joints, pathways, etc. | structural relationships checked |
| 4 Behavior/effects | physical/chemical/mechanical abstracted mechanism | cause → effect, deterministic control |
| 5 Data/logic | controller, signal, process, procedural sequence as needed | measured vs conceptual distinguished |
| 6 Observable response | UI, motion result, output state, environmental change | consistent with upstream mechanism |
| 7 Cinematography | lighting, set, cameras, composition | mobile-readable shot renders |
| 8 Assembly | linked assets, timing, audio and shots | continuity/end-to-end events validated |
| 9 Final | preview QA, PNG frames, encode, report | all output paths verified |

These are **adaptable phase types**, not mandatory fixed steps. A masonry explainer may not need a controller; a Face ID explainer may need an optics stage; a historical explainer may use reconstructed architecture and maps. Read `references/niche-patterns.md`.

## For new topics

- Run `python scripts/plan_project.py --topic "..." --niche "..." --duration 60 --fps 30 --output PROJECT_DIR` from this skill directory, or manually follow its file schemas.
- Read generated `project_brief.json`, `asset_manifest.json`, `shot_plan.json`, and `prompts/`; customize estimated mechanism facts and which stages actually apply **before** creating geometry.
- Prefer reusing available `.blend`/GLB/FBX files if supplied. No assumption that a model file is inherently clean or accurate.
- Treat an uploaded video as reference for pacing/style; don't mimic distinctive branding or copyrighted designs.

## For continuing an existing project

- Inspect the repository and existing manifest *without* overwriting files.
- Identify actual last completed gate and choose the next missing deliverable.
- When asked "Tahap 6" or another ordinal stage, align the requested stage with the user's already-established stage naming rather than forcibly mapping to generic phases.
- Output a self-contained, executable phase prompt if the user asks for a prompt instead of running Blender.
- Read `references/codex-claude-usage.md` for tool-specific use.

## References

- `references/production-pipeline.md`: step gates, deliverables, test strategy.
- `references/storyboard-spec.md`: shots, timing, cameras, vertical compositions, voiceover.
- `references/science-and-story.md`: scientific accuracy and visual metaphors.
- `references/niche-patterns.md`: niche templates.
- `references/asset-contract.md`: manifest, coordinate, reuse, and animation interfaces.
- `references/codex-claude-usage.md`: prompts and installation.
- `references/fact-research.md`: source-quality gates, uncertainty, surprising fact discovery.
- `references/creative-formats.md`: mechanisms, unusual facts, debunks, reconstruction storytelling.
- `references/postproduction.md`: FFmpeg and CapCut Pro editorial handoff.
- `references/plain-language.md`: seven-year-old-readable Indonesian voice-over quality gate.
- `references/eevee-shot-render.md`: Eevee-only, clean shot rendering and resumable delivery.
- `references/capcut-editorial.md`: per-shot editing, subtitles by word, transitions and SFX.
- `references/capcut-first-workflow.md`: binding STOP gate and separation of editing responsibilities.
- `references/camera-shot-diversity.md`: dynamic 12–20/60s planning, cinematic variety and information-gain test.
- `references/virtual-cinematography.md`: physically impossible/expensive camera reveals, practical Blender strategies, lens, scale, safety and quality controls.

## Bundled utilities

- `scripts/plan_project.py`: generate a fresh cross-niche project brief, reusable manifest, shot plan, phase prompt starters.
- `scripts/validate_manifest.py`: check manifest structure and asset file references; optional hash integrity check.
- `scripts/inspect_blend.py`: Blender `bpy` script for headless source asset inspection (run with Blender executable).
- `scripts/render_frames.py`: Blender headless render helper for ranges, presets, and skip-existing frames.
- `scripts/install_skill.py`: copy this skill to Codex and/or Claude Code skill folders.
- `scripts/validate_shot_diversity.py`: check timeline structure, camera-angle variety and shot-duration warnings.
- `scripts/validate_virtual_cinematography.py`: catch unmotivated virtual camera moves, absent cutaway/scale strategy and weak visual continuity.
- `scripts/build_camera_briefs.py`: generate reusable per-shot camera instructions from shot_plan.json.
- `scripts/capcut_shot_gate.py`: truthful, manual-confirmation status gate after every encoded clip.
- `scripts/rank_topics.py`: score topic candidates without conferring factual verification.
- `scripts/validate_research.py`: check claim statuses and source metadata (not external source contents).
- `scripts/build_postproduction.py`: generate edit_decisions.csv, optional timed SRT, CapCut editing guide.

If scripts are unavailable in the runtime, apply instructions manually and report limitations. Scripts are helpers, not a replacement for scientific verification or Blender scene inspection.

## Fact discovery mode

When asked "cari fakta unik", start with a sourced and scored candidate list; do not immediately model. Use `templates/topic_candidates.example.json`, `scripts/rank_topics.py`, `templates/claims.example.json`, `scripts/validate_research.py`. Treat `research_required` as a stop before factual animation. Cite actual sources in research handoffs, not guessed URLs.

## FFmpeg + CapCut Pro mode

When user has CapCut Pro, prefer Blender for 3D + FFmpeg for mechanical video encoding + CapCut Pro for editorial pace, VO, SFX, BGM and subtitles. `scripts/build_postproduction.py --shots shot_plan.json --output postproduction` creates a portable EDL and instructions; supply `--captions captions.json` only if real audio-derived word timings have been supplied; use `--word-captions` for one word per cue. Do not fabricate VO files or native CapCut projects.

## Mandatory v3 production gate

Before committing any new episode, confirm: script has passed the seven-year-old language gate; Blender shot renders use Eevee; explanatory overlays are absent from rendered frames; every finished shot is separately encoded and placed in a CapCut handoff folder; transition/SFX cue sheets exist; word-by-word subtitle output is created only from trustworthy audio-derived timings. A finished shot is not equivalent to a CapCut import without direct evidence.
