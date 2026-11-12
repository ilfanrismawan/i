#!/usr/bin/env python3
"""Validate shot timeline continuity and warn on cinematic monotony (not an aesthetic guarantee)."""
import argparse, json, pathlib, sys

def analyze(plan):
    fps=plan['fps']; shots=plan['shots']; problems=[];warnings=[];prev=0
    if not shots: return ['no shots'],[]
    for i,s in enumerate(shots):
        a,b=s['start_frame'],s['end_frame']
        if not isinstance(a,int) or not isinstance(b,int) or a!=prev+1 or b<a:problems.append(f'shot {i+1}: invalid contiguous frames')
        prev=b
        dur=(b-a+1)/fps
        if dur>7: warnings.append(f'{s["id"]}: long {dur:.1f}s hold; justify for clarity')
        if dur<0.8:warnings.append(f'{s["id"]}: short {dur:.1f}s; ensure legibility')
        for key in ('angle_family','camera_move','shot_size','new_information'):
            if not s.get(key): warnings.append(f'{s["id"]}: missing {key}')
    if plan.get('total_frames') and prev!=plan['total_frames']:problems.append('total_frames mismatch')
    duration=prev/fps
    suggested=(duration/60*12,duration/60*20)
    if duration>=30 and len(shots)<suggested[0]: warnings.append(f'{len(shots)} shots for {duration:.1f}s: consider ~{suggested[0]:.0f}-{suggested[1]:.0f} when narrative warrants')
    for i in range(len(shots)-4):
        window=shots[i:i+5]
        angles={s.get('angle_family') for s in window if s.get('angle_family')}
        moves={s.get('camera_move') for s in window if s.get('camera_move')}
        if len(angles)<3:warnings.append(f'shots {i+1}-{i+5}: low angle diversity ({len(angles)})')
        if len(moves)<2:warnings.append(f'shots {i+1}-{i+5}: same camera movement')
    for i in range(2,len(shots)):
        triple=shots[i-2:i+1]
        if all((s.get('shot_size'),s.get('angle_family'),s.get('camera_move'))==(triple[0].get('shot_size'),triple[0].get('angle_family'),triple[0].get('camera_move')) for s in triple): warnings.append(f'shots {i-1}-{i+1}: repeated composition')
    return problems,list(dict.fromkeys(warnings))

def main():
    p=argparse.ArgumentParser();p.add_argument('shot_plan');p.add_argument('--strict',action='store_true',help='fail when cinematic warnings remain');args=p.parse_args()
    plan=json.loads(pathlib.Path(args.shot_plan).read_text(encoding='utf-8'))
    errors,warnings=analyze(plan)
    print(json.dumps({'shots':len(plan['shots']),'errors':errors,'warnings':warnings},indent=2))
    return 1 if errors or (args.strict and warnings) else 0
if __name__=='__main__':sys.exit(main())
