"""Run inside Blender: blender -b source.blend -P inspect_blend.py -- --output audit.json"""
import bpy, json, pathlib, sys
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
output=pathlib.Path(args[args.index('--output')+1]) if '--output' in args else pathlib.Path('blend_audit.json')
def r(v): return [round(float(i),6) for i in v]
info={"blender_version":bpy.app.version_string,"blend_path":bpy.data.filepath,"scenes":[s.name for s in bpy.data.scenes],"collections":[x.name for x in bpy.data.collections],"objects":[],"missing_images":[]}
for o in bpy.data.objects:
    info['objects'].append({"name":o.name,"type":o.type,"dimensions":r(o.dimensions),"location":r(o.location),"rotation_euler":r(o.rotation_euler),"scale":r(o.scale),"parent":o.parent.name if o.parent else None,"collections":[c.name for c in o.users_collection],"custom_properties":list(o.keys())})
for i in bpy.data.images:
    if i.source=='FILE':
        path=pathlib.Path(bpy.path.abspath(i.filepath))
        if not path.is_file():info['missing_images'].append(str(path))
output.parent.mkdir(parents=True,exist_ok=True); output.write_text(json.dumps(info,indent=2),encoding='utf-8')
print(f'Wrote: {output}, {len(info["objects"])} objects')
