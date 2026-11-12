"""v4 regression gates: dynamic shots, cadence diversity, incremental CapCut status."""
import json, pathlib, subprocess, sys, tempfile, unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
def run(name,*args):return subprocess.run([sys.executable,str(ROOT/'scripts'/name),*map(str,args)],capture_output=True,text=True)
class V4Tests(unittest.TestCase):
 def test_dynamic_scaffold(self):
  with tempfile.TemporaryDirectory() as d:
   p=pathlib.Path(d)/'p';r=run('plan_project.py','--topic','Demo','--output',p)
   self.assertEqual(r.returncode,0,r.stderr)
   plan=json.loads((p/'shot_plan.json').read_text())
   self.assertEqual(len(plan['shots']),18)
   self.assertEqual(plan['shots'][-1]['end_frame'],1800)
   self.assertIn('angle_family',plan['shots'][0])
   r=run('validate_shot_diversity.py',p/'shot_plan.json')
   self.assertEqual(r.returncode,0,r.stderr)
 def test_monotony_is_detected(self):
  with tempfile.TemporaryDirectory() as d:
   f=pathlib.Path(d)/'p.json'
   f.write_text(json.dumps({'fps':30,'shots':[{'id':str(i),'start_frame':i*30+1,'end_frame':(i+1)*30,'angle_family':'front','camera_move':'orbit','shot_size':'medium','new_information':'same'} for i in range(6)]}))
   r=run('validate_shot_diversity.py',f,'--strict');self.assertNotEqual(r.returncode,0)
   self.assertIn('low angle diversity',r.stdout)
 def test_capcut_gate_never_infers_actual_edit(self):
  with tempfile.TemporaryDirectory() as d:
   d=pathlib.Path(d);plan=d/'plan.json';status=d/'status.json'
   plan.write_text(json.dumps({'fps':30,'shots':[{'id':'SHOT_01','start_frame':1,'end_frame':30},{'id':'SHOT_02','start_frame':31,'end_frame':60}]}))
   r=run('capcut_shot_gate.py','--plan',plan,'--status-file',status,'--shot','SHOT_02','--action','can-render-next')
   self.assertEqual(r.returncode,2)
   r=run('capcut_shot_gate.py','--plan',plan,'--status-file',status,'--shot','SHOT_01','--action','mark-edited','--confirmed-by-user')
   self.assertNotEqual(r.returncode,0)
   self.assertFalse(status.exists())
 def test_incremental_handoff_preserves_state(self):
  with tempfile.TemporaryDirectory() as d:
   d=pathlib.Path(d);plan=d/'plan.json';out=d/'postproduction'
   plan.write_text(json.dumps({'fps':30,'shots':[{'id':'SHOT_01','start_frame':1,'end_frame':30},{'id':'SHOT_02','start_frame':31,'end_frame':60}]}))
   r=run('build_postproduction.py','--shots',plan,'--output',out);self.assertEqual(r.returncode,0,r.stderr)
   f=out/'shot_status.json';status=json.loads(f.read_text());status['shots']['SHOT_01']['status']='EDITED_IN_CAPCUT';f.write_text(json.dumps(status))
   r=run('build_postproduction.py','--shots',plan,'--output',out);self.assertEqual(r.returncode,0,r.stderr)
   self.assertEqual(json.loads(f.read_text())['shots']['SHOT_01']['status'],'EDITED_IN_CAPCUT')
if __name__=='__main__':unittest.main()
