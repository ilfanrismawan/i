#!/usr/bin/env python3
"""Convert a shot plan into per-shot virtual camera briefs for Blender/Codex/Claude."""
import argparse, json, pathlib, re

def main():
    p=argparse.ArgumentParser();p.add_argument('shot_plan');p.add_argument('--output',required=True);args=p.parse_args()
    plan=json.loads(pathlib.Path(args.shot_plan).read_text(encoding='utf-8'))
    out=pathlib.Path(args.output);out.mkdir(parents=True,exist_ok=True)
    for i,shot in enumerate(plan['shots']):
        ident=re.sub(r'[^A-Za-z0-9_-]','_',str(shot.get('id',f'SHOT_{i+1:02d}')))
        def g(k):return str(shot.get(k) or 'NOT SPECIFIED — inspect source assets and storyboard')
        text=f'''# CAMERA BRIEF — {ident}

- Narrative beat: {g('beat')}
- Voice-over: {g('narration')}
- New information: {g('new_information')}
- Subject: {g('subject')}
- Angle: {g('angle_family')} — {g('camera_angle_reason')}
- Shot size: {g('shot_size')}
- Movement: {g('camera_move')} — {g('camera_movement_reason')}
- Movement start: {g('movement_start')}
- Movement end: {g('movement_end')}
- Focal target: {g('focal_target')}
- Camera rig: {g('camera_rig')}
- Lens or ortho: {g('lens_mm_or_ortho')}
- Virtual reveal: {g('reveal_technique')}
- Reveal purpose: {g('reveal_reason')}
- Geometry visibility: {g('geometry_visibility_strategy')}
- Scale transition: {g('scale_transition_strategy')}
- Transition to next (CapCut): {g('transition_intent')}
- Spatial anchor: {g('orientation_anchor')}
- Technical QA: {g('technical_qa')}

## Agent instructions
Reuse existing assets and actual attachment points. In Blender, animate only this shot, using Eevee. No editorial overlays, no final concatenation. For a fly-through, specify a non-destructive cross-section/visibility transition or matched separate scaled environment; never pass through an opaque mesh and assume it becomes transparent. Validate clipping and technical clarity in 9:16 with multiple frame samples, then encode a **single-shot** MP4 and hand it off to CapCut Pro. Do not claim CapCut editing occurred without evidence. Stop at the per-shot CapCut gate.
'''
        (out/f'{ident}.md').write_text(text,encoding='utf-8')
    print(f'Created {len(plan["shots"])} camera briefs in {out}')
if __name__=='__main__':main()
