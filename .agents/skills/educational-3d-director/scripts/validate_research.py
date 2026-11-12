#!/usr/bin/env python3
"""Validate claim source metadata and flag evidence gaps; does not verify URL content."""
import argparse,json,pathlib,sys,urllib.parse
ap=argparse.ArgumentParser(description=__doc__)
ap.add_argument('input');ap.add_argument('--strict',action='store_true',help='treat any unverified/unsupported claim as failure')
a=ap.parse_args()
data=json.loads(pathlib.Path(a.input).read_text(encoding='utf-8'))
if not isinstance(data.get('claims'),list): raise SystemExit('ERROR: claims array required')
errors=[];warnings=[];ids=set()
for i,c in enumerate(data['claims']):
    who=f'claims[{i}]'
    if not isinstance(c,dict): errors.append(f'{who} must be object');continue
    if not c.get('id') or c['id'] in ids: errors.append(f'{who} missing/duplicate id')
    ids.add(c.get('id'))
    if not isinstance(c.get('claim'),str) or not c['claim'].strip():errors.append(f'{who} missing claim')
    status=c.get('status','unverified')
    if status not in ('verified','qualified','disputed','unverified'):errors.append(f'{who} invalid status')
    sources=c.get('sources',[])
    if not isinstance(sources,list):errors.append(f'{who} sources must be list');continue
    if status in ('verified','qualified') and not sources: errors.append(f'{who} marked {status} with no sources')
    for j,s in enumerate(sources):
        if not isinstance(s,dict) or not s.get('url') or not s.get('publisher') or not s.get('title'):
            errors.append(f'{who}.sources[{j}] requires url, publisher, title');continue
        url=urllib.parse.urlsplit(s['url'])
        if url.scheme not in ('http','https') or not url.netloc: errors.append(f'{who}.sources[{j}] URL invalid')
    if status in ('unverified','disputed'): warnings.append(f'{who} not ready for factual narration: {status}')
    if c.get('visualization_type') not in ('exact','conceptual','illustrative','reconstruction'):warnings.append(f'{who} visualization_type missing/unknown')
for x in errors:print('ERROR:',x)
for x in warnings:print('WARN:',x)
print(f'Validated {len(data["claims"])} claims: {len(errors)} errors, {len(warnings)} warnings. Source content NOT independently checked.')
sys.exit(1 if errors or (a.strict and warnings) else 0)
