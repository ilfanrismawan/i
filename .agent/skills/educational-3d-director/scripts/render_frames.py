"""Blender Eevee-only resumable shot renderer.
Example: blender -b scene.blend -P render_frames.py -- --out renders/shot_01 --start 1 --end 30 --preset preview
"""
import argparse, bpy, pathlib, sys
argv=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
p=argparse.ArgumentParser()
p.add_argument('--out',required=True);p.add_argument('--start',type=int,required=True);p.add_argument('--end',type=int,required=True)
p.add_argument('--preset',choices=['blocking','preview','final'],default='preview');p.add_argument('--force',action='store_true')
a=p.parse_args(argv)
if a.start<1 or a.start>a.end:p.error('invalid frame range')
scene=bpy.context.scene
try:
    enum=scene.bl_rna.properties['render']  # existence check only
    _=enum
except Exception:pass
engine_candidates=['BLENDER_EEVEE_NEXT','BLENDER_EEVEE']
selected=None
for engine in engine_candidates:
    try:
        scene.render.engine=engine
        if scene.render.engine==engine:
            selected=engine;break
    except (TypeError,ValueError,AttributeError):pass
if not selected:raise RuntimeError('Eevee unavailable: cannot silently fall back to Cycles')
presets={'blocking':(360,640,16),'preview':(540,960,32),'final':(1080,1920,32)}
w,h,samples=presets[a.preset]
scene.render.resolution_x=w;scene.render.resolution_y=h;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.film_transparent=False
if hasattr(scene,'eevee'):
    if hasattr(scene.eevee,'taa_render_samples'):scene.eevee.taa_render_samples=samples
    if hasattr(scene.eevee,'taa_samples'):scene.eevee.taa_samples=samples
# IMPORTANT: no broad hiding of FONT objects: original in-scene phone UI may use text.
# Use production-approved scene/view-layer clean-render collection visibility settings.
if not bool(scene.get('CLEAN_RENDER_QA_PASSED',False)):
    raise RuntimeError('Set scene custom property CLEAN_RENDER_QA_PASSED=True only after validating no explanatory overlays/debug elements appear in rendered frame.')
out=pathlib.Path(a.out).resolve();out.mkdir(parents=True,exist_ok=True)
for frame in range(a.start,a.end+1):
    path=out/f'frame_{frame:04d}.png'
    if path.is_file() and path.stat().st_size>0 and not a.force:
        print('SKIP (exists; external PNG validation recommended)',path);continue
    scene.frame_set(frame);scene.render.filepath=str(path)
    bpy.ops.render.render(write_still=True)
    if not path.is_file() or path.stat().st_size==0:raise RuntimeError(f'Output missing: {path}')
    print('OK',path)
