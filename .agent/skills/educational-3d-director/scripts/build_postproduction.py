#!/usr/bin/env python3
"""Build incremental CapCut handoff, word-level subtitle SRT/CSV, and editorial cue sheets."""
import argparse, csv, json, pathlib, re


def stamp(seconds):
    ms=round(seconds*1000)
    h,rem=divmod(ms,3600000);m,rem=divmod(rem,60000);s,ms=divmod(rem,1000)
    return f'{h:02}:{m:02}:{s:02},{ms:03}'


def write_csv(path, rows, fields):
    with path.open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');w.writeheader();w.writerows(rows)


def words_from_source(path):
    data=json.loads(path.read_text(encoding='utf-8'))
    rows=data.get('words')
    if not isinstance(rows,list):
        raise ValueError('word captions require {"words": [{"start":...,"end":...,"text":"..."}]} from aligned audio')
    return rows


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--shots',required=True)
    p.add_argument('--captions',help='approved timed captions, legacy sentence-level only')
    p.add_argument('--word-captions',help='audio-aligned word timestamps JSON')
    p.add_argument('--output',required=True)
    p.add_argument('--ready-shot',help='optional completed shot ID, verified clip required')
    p.add_argument('--clip',help='verified MP4 path for --ready-shot')
    a=p.parse_args()
    plan=json.loads(pathlib.Path(a.shots).read_text(encoding='utf-8'))
    fps=plan.get('fps'); shots=plan.get('shots')
    if not isinstance(fps,(int,float)) or isinstance(fps,bool) or fps<=0 or not isinstance(shots,list) or not shots:
        raise ValueError('invalid shot plan')
    duration_frame=0;rows=[]; cue=[]
    for ix,shot in enumerate(shots):
        first=shot['start_frame'];end=shot['end_frame']
        if not isinstance(first,int) or not isinstance(end,int) or first!=duration_frame+1 or end<first:
            raise ValueError(f'gap/overlap at {shot.get("id")}')
        duration_frame=end
        rows.append({'shot_id':shot['id'],'start_frame':first,'end_frame':end,'start_seconds':round((first-1)/fps,4),'end_seconds':round(end/fps,4),'duration_seconds':round((end-first+1)/fps,4),'video_file':shot.get('source_video',''),'png_sequence':shot.get('source_sequence',''),'narration':shot.get('narration',''),'editor_notes':shot.get('editor_notes','')})
        cue.append({'shot_id':shot['id'],'in_seconds':round((first-1)/fps,3),'out_seconds':round(end/fps,3),'transition_in': 'hard cut' if ix==0 else 'match cut / short dissolve only if motivated', 'transition_sfx':'none / subtle whoosh if transition is used','scene_sfx':'select sound matching visible action; never imply false physics', 'bgm_notes':'low-volume ambience beneath voice','manual_review':'YES'})
    if plan.get('total_frames') is not None and duration_frame!=plan['total_frames']:
        raise ValueError('total_frames mismatch')
    duration=duration_frame/fps
    word_rows=[];lines=[];last_end=0.0
    if a.word_captions:
        for i,w in enumerate(words_from_source(pathlib.Path(a.word_captions)),1):
            text=str(w.get('text','')).strip()
            if len(text.split())!=1 or not text or not re.search(r'\w',text,re.UNICODE):
                raise ValueError(f'word #{i} must be exactly one spoken word')
            start=float(w['start']);end=float(w['end'])
            if start<0 or end<=start or start<last_end or end>duration+0.05:
                raise ValueError(f'invalid word timing #{i}')
            word_rows.append({'index':i,'start_seconds':start,'end_seconds':end,'word':text,'source':'approved audio alignment','manual_review':'YES'})
            lines += [str(i),f'{stamp(start)} --> {stamp(end)}',text,'']
            last_end=end
    if a.captions and a.word_captions:
        raise ValueError('choose either --captions or --word-captions')
    legacy_lines=[]
    if a.captions:
        data=json.loads(pathlib.Path(a.captions).read_text(encoding='utf-8'))
        end_last=0.0
        for i,c in enumerate(data['captions'],1):
            start=float(c['start']);end=float(c['end']);txt=str(c['text']).strip()
            if start<0 or end<=start or start<end_last or end>duration+0.05 or not txt:
                raise ValueError(f'invalid caption timing #{i}')
            legacy_lines += [str(i),f'{stamp(start)} --> {stamp(end)}',txt,''];end_last=end
    if bool(a.ready_shot) != bool(a.clip):
        raise ValueError('provide --ready-shot AND --clip together')
    # Preserve confirmed CapCut edits across repeated shot handoffs; never reset them.
    out=pathlib.Path(a.output).resolve(); existing_status=out/'shot_status.json'
    previous=json.loads(existing_status.read_text(encoding='utf-8')) if existing_status.exists() else {'shots':{}}
    shot_status={'shots':{r['shot_id']:previous.get('shots',{}).get(r['shot_id'],{'status':'PENDING_CAPCUT_HANDOFF','clip':''}) for r in rows}}
    if a.ready_shot:
        if a.ready_shot not in shot_status['shots']:
            raise ValueError('unknown ready-shot')
        clip=pathlib.Path(a.clip).resolve()
        if not clip.is_file() or clip.stat().st_size==0 or clip.suffix.lower()!='.mp4':
            raise ValueError('clip missing/empty/not MP4')
        # Existence is not complete media QA. Require the caller to complete ffprobe/playback checks.
        if shot_status['shots'][a.ready_shot].get('status') not in ('IMPORTED_IN_CAPCUT','EDITED_IN_CAPCUT'):
            shot_status['shots'][a.ready_shot]={'status':'CLIP_EXISTS_NEEDS_MEDIA_QA','clip':str(clip)}
        for r in rows:
            if r['shot_id']==a.ready_shot:r['video_file']=str(clip)
    out.mkdir(parents=True,exist_ok=True)
    write_csv(out/'edit_decisions.csv',rows,list(rows[0]))
    write_csv(out/'editorial_cues.csv',cue,list(cue[0]))
    (out/'shot_status.json').write_text(json.dumps(shot_status,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    if a.word_captions:
        write_csv(out/'word_captions.csv',word_rows,['index','start_seconds','end_seconds','word','source','manual_review'])
        (out/'word_captions.srt').write_text('\n'.join(lines),encoding='utf-8')
    if a.captions:
        (out/'captions.srt').write_text('\n'.join(legacy_lines),encoding='utf-8')
    guide=f'''# CapCut Pro — shot-by-shot handoff\n\nFPS: {fps}; frames: {duration_frame}; timeline: {duration:.3f}s.\n\n1. Blender MUST use Eevee, with NO overlay/labels/subtitles baked into shot frames.\n2. Render each shot individually to PNG images. Encode into high-quality MP4 with FFmpeg and validate dimensions, FPS, frame count and actual playback.\n3. As soon as ONE shot passes QA, encode and import that MP4 into the SAME active CapCut Pro project. Adjust VO sync, cut timing and editing now. STOP before rendering the next shot by default, until the user confirms CapCut import and edit. This is MANUAL unless supported graphical control is genuinely available.\n4. Edit pacing against recorded Indonesian VO. Narration should be understandable around age 7: short, everyday language, without unexplained technical jargon or CTA.\n5. Import word_captions.srt if produced, check every word against recorded speech, then style captions word-by-word in CapCut. If timings are absent, align manually or generate accurate word timestamps with an audio aligner; never fabricate by word-count division.\n6. Refer to editorial_cues.csv: choose motivated transitions, add transition-specific whoosh/soft movement SFX and separate contextual scene SFX. Avoid overusing transitions; add low BGM with ducking under voice.\n7. Never use Blender/VSE/compositor or FFmpeg to concatenate finished shots. Export final 1080x1920 H.264 30 fps + AAC ONLY from CapCut after all editing; inspect on a mobile-sized screen.\n\nThis handoff does not create a CapCut project or auto-insert clips into CapCut. A valid existing MP4 is not proof its content was inspected. No copyrighted sound assets are supplied.\n'''
    (out/'CAPCUT_HANDOFF.md').write_text(guide,encoding='utf-8')
    (out/'handoff_summary.json').write_text(json.dumps({'fps':fps,'shots':len(rows),'duration_seconds':duration,'word_captions_generated':bool(a.word_captions),'captions_generated':bool(a.captions),'ready_shot':a.ready_shot},indent=2)+'\n',encoding='utf-8')
    print(f'CapCut handoff created: {out}; {len(rows)} shots; word captions={len(word_rows)}')
if __name__=='__main__':main()
