#!/usr/bin/env python3
"""Track truthful shot-by-shot CapCut handoff and enforce editorial gate.

This script does NOT control CapCut. Import/edit statuses require explicit manual confirmation.
"""
import argparse, json, pathlib, subprocess, shutil, sys

STATUSES=['PLANNED','CLIP_READY_FOR_CAPCUT','WAITING_FOR_CAPCUT_IMPORT','IMPORTED_IN_CAPCUT','EDITED_IN_CAPCUT']

def probe(clip):
    ffprobe=shutil.which('ffprobe')
    if not ffprobe: raise ValueError('ffprobe unavailable: cannot verify clip')
    r=subprocess.run([ffprobe,'-v','error','-select_streams','v:0','-show_entries','stream=width,height,r_frame_rate,nb_frames,duration','-of','json',str(clip)],capture_output=True,text=True)
    if r.returncode: raise ValueError(f'ffprobe failed: {r.stderr}')
    streams=json.loads(r.stdout).get('streams') or []
    if not streams: raise ValueError('MP4 has no video stream')
    return streams[0]

def read(path):
    return json.loads(path.read_text(encoding='utf-8')) if path.exists() else {'shots':{}}

def atomic_write(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    temp=path.with_suffix('.tmp')
    temp.write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    temp.replace(path)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--plan',required=True);p.add_argument('--status-file',required=True)
    p.add_argument('--shot',required=True)
    p.add_argument('--action',required=True,choices=['clip-ready','mark-imported','mark-edited','can-render-next','show'])
    p.add_argument('--clip');p.add_argument('--confirmed-by-user',action='store_true')
    p.add_argument('--width',type=int,default=1080);p.add_argument('--height',type=int,default=1920)
    args=p.parse_args()
    plan=json.loads(pathlib.Path(args.plan).read_text(encoding='utf-8'))
    shots=plan['shots']; ids=[s['id'] for s in shots]
    if args.shot not in ids: p.error('unknown shot ID')
    path=pathlib.Path(args.status_file);data=read(path)
    for item in shots:data['shots'].setdefault(item['id'],{'status':'PLANNED','clip':None})
    record=data['shots'][args.shot]; current=record['status']
    if args.action=='clip-ready':
        if not args.clip: p.error('--clip required')
        clip=pathlib.Path(args.clip).resolve()
        if not clip.is_file() or clip.stat().st_size<=0 or clip.suffix.lower()!='.mp4':p.error('clip absent/empty/not MP4')
        stream=probe(clip)
        if (stream.get('width'),stream.get('height'))!=(args.width,args.height):p.error('clip dimensions mismatch')
        expected_fps=float(plan['fps']);num,den=map(int,stream['r_frame_rate'].split('/'))
        if abs(num/den-expected_fps)>0.02:p.error('clip fps mismatch')
        # This confirms technical media properties, not visual QA or actual CapCut import.
        record.update({'status':'WAITING_FOR_CAPCUT_IMPORT','clip':str(clip),'technical_media_verified':True,'visual_qa_user_confirmation':False})
    elif args.action=='mark-imported':
        if not args.confirmed_by_user:p.error('must explicitly supply --confirmed-by-user; do not infer CapCut import')
        if current!='WAITING_FOR_CAPCUT_IMPORT':p.error(f'clip not waiting for import; current={current}')
        record['status']='IMPORTED_IN_CAPCUT'
    elif args.action=='mark-edited':
        if not args.confirmed_by_user:p.error('must explicitly supply --confirmed-by-user; do not infer CapCut edit')
        if current!='IMPORTED_IN_CAPCUT':p.error(f'clip must first be confirmed imported; current={current}')
        record['status']='EDITED_IN_CAPCUT'
    elif args.action=='can-render-next':
        pos=ids.index(args.shot)
        if pos==0: print('ALLOW: first shot');return 0
        prev=ids[pos-1];state=data['shots'][prev]['status']
        if state!='EDITED_IN_CAPCUT':print(f'BLOCK: {prev} status={state}; import and edit in CapCut before rendering {args.shot}');return 2
        print(f'ALLOW: previous shot {prev} edited in CapCut');return 0
    if args.action!='show':atomic_write(path,data)
    print(json.dumps({'shot':args.shot,**record},ensure_ascii=False,indent=2))
    return 0
if __name__=='__main__':sys.exit(main())
