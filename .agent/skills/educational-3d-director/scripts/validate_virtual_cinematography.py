#!/usr/bin/env python3
"""Audit storyboard camera logic; outputs actionable warnings, not an aesthetic guarantee."""
import argparse, json, pathlib, sys
SIGNATURE={'micro_flythrough','exploded_flight','interior_pov','signal_follow','xray_orbit','bullet_time_orbit','multiscale_pullback','time_frozen_flight','reverse_causality','portal_matchcut','infinite_crane','non_euclidean_reveal','perspective_morph','extreme_macro_track'}
NEEDS_VISIBILITY={'micro_flythrough','exploded_flight','interior_pov','xray_orbit','multiscale_pullback','portal_matchcut','non_euclidean_reveal'}
DISORIENTING={'micro_flythrough','interior_pov','bullet_time_orbit','multiscale_pullback','portal_matchcut','non_euclidean_reveal','perspective_morph'}

def analyze(plan):
    errors=[]; warnings=[]; shots=plan.get('shots',[])
    if not shots:return ['missing shots'], []
    fps=plan.get('fps',0)
    if not isinstance(fps,(int,float)) or fps<=0:return ['invalid fps'],[]
    for i,s in enumerate(shots):
        id=s.get('id',f'index_{i+1}')
        tech=s.get('reveal_technique','none') or 'none'
        if tech!='none' and tech not in SIGNATURE:errors.append(f'{id}: unknown reveal_technique {tech!r}')
        if tech in SIGNATURE and not s.get('reveal_reason'):warnings.append(f'{id}: signature move lacks reveal_reason')
        if tech in NEEDS_VISIBILITY and not s.get('geometry_visibility_strategy'):warnings.append(f'{id}: {tech} needs geometry_visibility_strategy')
        if tech in {'micro_flythrough','multiscale_pullback'} and not s.get('scale_transition_strategy'):warnings.append(f'{id}: {tech} needs scale_transition_strategy')
        for key in ('focal_target','camera_angle_reason','camera_movement_reason','transition_intent'):
            if not s.get(key):warnings.append(f'{id}: missing {key}')
        if not s.get('new_information') or str(s.get('new_information','')).strip().upper().startswith('EDIT:'):warnings.append(f'{id}: explain what new information is revealed')
        if s.get('camera_move') in ('orbit','small-orbit','xray_orbit') and i>=2 and all(x.get('camera_move') in ('orbit','small-orbit','xray_orbit') for x in shots[i-2:i+1]):warnings.append(f'{id}: 3 orbit movements in succession')
        if i>0 and shots[i-1].get('reveal_technique') in DISORIENTING and tech in DISORIENTING and not s.get('orientation_anchor'):
            warnings.append(f'{id}: back-to-back disorienting reveals require orientation anchor')
        duration=(s.get('end_frame',0)-s.get('start_frame',1)+1)/fps
        if duration<=0:errors.append(f'{id}: invalid duration')
    if len(shots)>=5:
        for i in range(len(shots)-4):
            w=shots[i:i+5]
            if len({x.get('shot_size') for x in w})<2:warnings.append(f'shots {i+1}-{i+5}: no shot-scale contrast')
            if len({x.get('camera_move') for x in w})<2:warnings.append(f'shots {i+1}-{i+5}: no camera movement contrast')
    return errors,list(dict.fromkeys(warnings))

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('shot_plan');ap.add_argument('--strict',action='store_true');ap.add_argument('--report',help='write JSON report');args=ap.parse_args()
    p=json.loads(pathlib.Path(args.shot_plan).read_text(encoding='utf-8'))
    errors,warnings=analyze(p)
    report={'shots':len(p.get('shots',[])),'signature_reveal_shots':sum(s.get('reveal_technique','none') not in ('','none',None) for s in p.get('shots',[])),'errors':errors,'warnings':warnings}
    if args.report:
        target=pathlib.Path(args.report);target.parent.mkdir(parents=True,exist_ok=True);target.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))
    return 1 if errors or (args.strict and warnings) else 0
if __name__=='__main__':sys.exit(main())
