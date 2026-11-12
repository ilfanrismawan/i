#!/usr/bin/env python3
"""Validate asset manifest paths and optional sha256 against original files."""
import argparse, hashlib, json, pathlib, sys
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('manifest', nargs='?', default='asset_manifest.json'); p.add_argument('--check-hashes',action='store_true')
a=p.parse_args(); src=pathlib.Path(a.manifest).resolve()
try: obj=json.loads(src.read_text(encoding='utf-8'))
except Exception as e: print('ERROR:',e);sys.exit(2)
errors=[]; warnings=[]
if not isinstance(obj,dict) or not isinstance(obj.get('assets'),list): errors.append('manifest must have assets array')
else:
    seen=set()
    for i,x in enumerate(obj['assets']):
        if not isinstance(x,dict): errors.append(f'assets[{i}] must be object');continue
        for k in ('id','path','phase','status'):
            if not isinstance(x.get(k),str) or not x[k]:errors.append(f'assets[{i}] missing {k}')
        if x.get('id') in seen: errors.append(f'duplicate asset ID: {x.get("id")}')
        seen.add(x.get('id'))
        if x.get('path'):
            path=pathlib.Path(x['path']); path=path if path.is_absolute() else src.parent/path
            if not path.is_file(): errors.append(f'missing asset file: {path}');continue
            if a.check_hashes and x.get('source_sha256'):
                h=hashlib.sha256()
                with path.open('rb') as fh:
                    for chunk in iter(lambda:fh.read(1024*1024),b''):h.update(chunk)
                if h.hexdigest().lower()!=x['source_sha256'].lower():errors.append(f'hash mismatch: {path}')
            elif a.check_hashes: warnings.append(f'no source_sha256 for {path}')
for x in warnings: print('WARN:',x)
for x in errors: print('ERROR:',x)
print(f'Validation: {len(errors)} errors, {len(warnings)} warnings')
sys.exit(1 if errors else 0)
