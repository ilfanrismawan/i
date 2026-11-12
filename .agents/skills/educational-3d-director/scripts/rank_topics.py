#!/usr/bin/env python3
"""Rank editorial candidate topics without laundering unverified facts into claims."""
import argparse, json, pathlib, sys
KEYS = ('curiosity','familiarity','visualizability','learning_value','differentiation','feasibility')
WEIGHTS = {'curiosity':.23,'familiarity':.17,'visualizability':.22,'learning_value':.20,'differentiation':.10,'feasibility':.08}

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('input'); ap.add_argument('--output'); ap.add_argument('--min-status',choices=['all','qualified','verified'],default='all')
    a=ap.parse_args()
    data=json.loads(pathlib.Path(a.input).read_text(encoding='utf-8'))
    topics=data['topics']
    if not isinstance(topics,list): raise ValueError('topics must be a list')
    rows=[]
    for t in topics:
        vals=t['scores']
        for k in KEYS:
            n=vals[k]
            if isinstance(n,bool) or not isinstance(n,(int,float)) or not 1<=n<=5: raise ValueError(f'{t.get("id")}: {k} must be 1..5')
        status=t.get('research_status','research_required')
        if a.min_status=='verified' and status!='verified': continue
        if a.min_status=='qualified' and status not in ('verified','qualified'): continue
        score=round(sum(vals[k]*WEIGHTS[k] for k in KEYS),2)
        rows.append({'id':t['id'],'title':t['title'],'score_out_of_5':score,'research_status':status,'production_ready':status in ('verified','qualified') and bool(t.get('sources'))})
    rows.sort(key=lambda r:(-r['score_out_of_5'],r['id']))
    result={'rubric_weights':WEIGHTS,'ranked_topics':rows,'warning':'Editorial scores do not verify factual claims or source authenticity.'}
    out=json.dumps(result,ensure_ascii=False,indent=2)
    if a.output: pathlib.Path(a.output).write_text(out+'\n',encoding='utf-8')
    else: print(out)
if __name__=='__main__': main()
