#!/usr/bin/env python3
"""Create a reusable, niche-agnostic educational Blender production scaffold."""
import argparse, json, pathlib, re, textwrap

PHASES = [
 ("00", "discover", "Research, fact-check, and inventory existing source assets"),
 ("01", "storyboard", "Create storytelling beats, voiceover, shot list, and reveal order"),
 ("02", "master-assets", "Reuse or prepare the central hero 3D assets"),
 ("03", "mechanism-assets", "Build the missing internal components/cutaways"),
 ("04", "behavior", "Show physical/chemical/biological mechanism with verified metaphors"),
 ("05", "processing", "Visualize intermediate process or signals if actually needed"),
 ("06", "observable-response", "Animate the visible result driven by upstream cause"),
 ("07", "cinematography", "Make environments, lights and 9:16 camera rigs"),
 ("08", "integration", "Connect assets, continuity, audio, shot timeline"),
 ("09", "render-qa", "Run preview QA, frames and video encode")
]

def slug(s):
    return re.sub(r'[^a-z0-9]+','-',s.casefold()).strip('-')[:65] or 'educational-project'

def save(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--topic', required=True); p.add_argument('--niche', default='general')
    p.add_argument('--duration', type=int, default=60); p.add_argument('--fps', type=int, default=30)
    p.add_argument('--width', type=int, default=1080); p.add_argument('--height', type=int, default=1920)
    p.add_argument('--language', default='id-ID'); p.add_argument('--output', default=None)
    args=p.parse_args()
    if args.duration<5 or args.fps<1 or args.width<1 or args.height<1:
        p.error('duration, fps, width and height must be positive (duration >= 5)')
    root=pathlib.Path(args.output or slug(args.topic)).expanduser().resolve()
    for d in ['assets','scripts','scenes','renders/frames','previews','reports','prompts','references','research','postproduction']:
        (root/d).mkdir(parents=True,exist_ok=True)
    brief={"topic":args.topic,"niche":args.niche,"audience":"general curiosity","language":args.language,"narrative_question":args.topic,"duration_seconds":args.duration,"fps":args.fps,"resolution":[args.width,args.height],"visual_style":"stylized realistic educational 3D","render_engine":"Eevee ONLY", "editorial_assembly":"CapCut Pro ONLY", "shot_delivery":"one verified shot at a time; CapCut edit gate","voiceover_source":None,"existing_assets_to_inspect":[],"scientific_claims_to_verify":[],"production_status":"planning"}
    save(root/'project_brief.json', brief)
    save(root/'research'/'topic_candidates.json', {'topics': [], 'note':'Research leads must be externally verified before promotion to factual claims.'})
    save(root/'research'/'claims.json', {'claims': []})
    save(root/'research'/'sources.json', {'sources': []})
    save(root/'asset_manifest.json', {"schema_version":"1.0","project":slug(args.topic),"assets":[],"notes":"Record actual paths and original hashes; do not invent completed assets."})
    # A storyboard beat is not synonymous with one camera shot.
    # Start around 18 varied compositions for 60 s, then refine from narration.
    beat_names=['hook','hook','context','context','reveal','reveal','reveal',
                'mechanism','mechanism','mechanism','mechanism','mechanism',
                'result','result','result','ending','ending','ending']
    angle_families=['wide-established','over-shoulder','extreme-macro','side-profile','under-glass',
                    'isometric-cutaway','top-down','diagonal-macro','side-cross-section',
                    'three-quarter','overhead','under-object','macro-chip','front-on','profile-macro',
                    'over-shoulder','front-on','wide-established']
    camera_moves=['locked','dolly-push','locked','lateral-truck','push-through','crane',
                  'tilt','parallax','locked','follow','crane','match-move',
                  'pan','locked','dolly-pull','locked','small-orbit','dolly-pull']
    shot_sizes=['wide','medium','extreme-close','close','extreme-close','medium',
                'close','extreme-close','close','medium','close','close','extreme-close',
                'medium','close','medium','close','wide']
    n=max(1,round(args.duration*18/60))
    total=args.duration*args.fps
    if n>total:n=total
    shots=[];frame=1
    for i in range(n):
        count=total//n+(1 if i<total%n else 0)
        j=round(i*17/max(1,n-1))
        shots.append({"id":f'SHOT_{i+1:02d}',"beat":beat_names[j],"start_frame":frame,
            "end_frame":frame+count-1,"purpose":"EDIT: specify unique viewer-facing reveal",
            "new_information":"EDIT: unique information revealed in this shot",
            "narration":"EDIT: short Indonesian plain-language VO aligned to this shot",
            "assets":[],"angle_family":angle_families[j],"camera_move":camera_moves[j],
            "shot_size":shot_sizes[j],"camera_angle_reason":"EDIT: what this viewpoint reveals", "camera_movement_reason":"EDIT: why camera moves or holds", "focal_target":"EDIT: existing object / anchor", "movement_start":"EDIT: first composition", "movement_end":"EDIT: last composition", "reveal_technique":"none", "reveal_reason":"", "geometry_visibility_strategy":"", "scale_transition_strategy":"", "orientation_anchor":"EDIT: show spatial context", "camera":"EDIT: verify existing camera rig",
            "animation":"EDIT: meaningful cause-and-effect action", "transition_intent":"EDIT: motivated cut",
            "fact_status":"unverified planning placeholder", "qa":"EDIT: check visibility and relevance"})
        frame+=count
    save(root/'shot_plan.json', {"fps":args.fps,"total_frames":args.duration*args.fps,"shots":shots})
    for code, name, goal in PHASES:
        txt=f'''# PHASE {code} — {name}\n\nUse the educational-3d-director skill.\n\nTOPIC: {args.topic}\nNICHE: {args.niche}\nGOAL: {goal}\n\nRead project_brief.json, asset_manifest.json, shot_plan.json, existing Blender projects, and previous stage results before acting.\n\nMANDATORY:\n- Do not recreate, overwrite, or destructively alter existing completed assets.\n- Create ONLY deliverables belonging to this phase.\n- Make uncertain facts and visual metaphors explicit. Before modeling, record evidence in research/claims.json and source metadata; do not claim verification without actually inspecting sources.\n- Detect Blender and its bpy API version before writing version-specific code.\n- Record new assets with true dependencies and attachment transforms in asset_manifest.json.\n- Generate low-resolution representative previews, validate real output files, and document remaining limitations.\n- Maintain 9:16 {args.width}x{args.height}, {args.fps} fps final target.\n- If this phase is irrelevant to this niche, mark it skipped with a reason and propose the next relevant phase.\n\nSTOP after completing this phase. Do not start a later phase or full-resolution render automatically.\n'''
        (root/'prompts'/f'{code}_{name}.md').write_text(txt,encoding='utf-8')
    (root/'README.md').write_text(textwrap.dedent(f'''\
    # {args.topic}

    Generated cross-niche 3D explainer scaffold. **No assets or renders are created by this scaffold.**

    1. Review `project_brief.json` and confirm mechanism facts.
    2. Add existing asset file paths in `asset_manifest.json` and do not duplicate them.
    3. Refine `shot_plan.json` and phase prompts; omit phases irrelevant to the niche.
    4. Run the agent one phase at a time using prompts in `prompts/`.
    5. Render blocking previews before a final frame sequence.
    6. Render one Eevee shot at a time. Encode its own MP4; do not create a Blender or FFmpeg final edit.
    7. Import AND edit each verified shot in the SAME CapCut Pro project before the next render (unless explicit batch permission).
    8. Validate shot diversity AND virtual camera planning with scripts/validate_shot_diversity.py and scripts/validate_virtual_cinematography.py; generate camera briefs with scripts/build_camera_briefs.py. Generate editorial handoff with build_postproduction.py.

    Target: {args.duration}s, {args.fps} FPS, {args.width}x{args.height}.
    '''),encoding='utf-8')
    print(f'Created planning scaffold: {root}')
    print(f'Phases: {len(PHASES)}, suggested shots: {len(shots)}, frames: {args.duration*args.fps}')
if __name__=='__main__': main()
