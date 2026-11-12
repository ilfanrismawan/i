#!/usr/bin/env python3
"""Install this skill to Codex/Claude Code personal or project skill folders."""
import argparse,pathlib,shutil
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--target',choices=['codex','claude','both'],default='both')
p.add_argument('--scope',choices=['user','project'],default='user')
p.add_argument('--project-dir',default='.')
p.add_argument('--force',action='store_true',help='replace an existing installation')
a=p.parse_args(); source=pathlib.Path(__file__).resolve().parent.parent
if not (source/'SKILL.md').is_file():p.error('SKILL.md not found')
where={'codex':'.agents/skills','claude':'.claude/skills'}
root=pathlib.Path.home() if a.scope=='user' else pathlib.Path(a.project_dir).expanduser().resolve()
for target in (['codex','claude'] if a.target=='both' else [a.target]):
    dst=root/where[target]/source.name
    if dst.resolve()==source.resolve():print('Already in target location:',dst);continue
    if dst.exists():
        if not a.force: print('SKIPPED (exists; use --force):',dst);continue
        shutil.rmtree(dst)
    dst.parent.mkdir(parents=True,exist_ok=True)
    shutil.copytree(source,dst,ignore=shutil.ignore_patterns('__pycache__','*.pyc','.DS_Store'))
    print(f'Installed for {target}: {dst}')
print('Restart Codex/Claude Code if the skill is not discovered immediately.')
