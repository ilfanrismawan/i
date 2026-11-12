"""New virtual cinematography regressions."""
import tempfile, unittest, subprocess, sys, json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
def run(n,*a):return subprocess.run([sys.executable,str(R/'scripts'/n),*map(str,a)],capture_output=True,text=True)
class V5(unittest.TestCase):
 def test_scaffold_has_virtual_fields_and_briefs(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'ep'
   self.assertEqual(run('plan_project.py','--topic','Water','--output',p).returncode,0)
   plan=json.loads((p/'shot_plan.json').read_text());self.assertIn('reveal_technique',plan['shots'][0]);self.assertEqual(len(plan['shots']),18)
   self.assertEqual(run('validate_virtual_cinematography.py',p/'shot_plan.json').returncode,0)
   r=run('build_camera_briefs.py',p/'shot_plan.json','--output',p/'briefs');self.assertEqual(r.returncode,0,r.stderr)
   self.assertEqual(len(list((p/'briefs').glob('*.md'))),18)
 def test_signature_movement_without_strategy_fails_strict(self):
  with tempfile.TemporaryDirectory() as d:
   f=Path(d)/'shots.json'
   f.write_text(json.dumps({'fps':30,'shots':[{'id':'A','start_frame':1,'end_frame':90,'reveal_technique':'micro_flythrough','camera_move':'push-through','shot_size':'macro','new_information':'internal structure'}]}))
   r=run('validate_virtual_cinematography.py',f,'--strict');self.assertNotEqual(r.returncode,0);self.assertIn('geometry_visibility_strategy',r.stdout);self.assertIn('scale_transition_strategy',r.stdout)
 def test_valid_signature_move_and_cam_brief(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d);f=p/'s.json'
   shot={'id':'SHOT_01','start_frame':1,'end_frame':90,'new_information':'Sensor behind glass','reveal_technique':'micro_flythrough','reveal_reason':'show hidden sensor','geometry_visibility_strategy':'cutaway non-destructive copy','scale_transition_strategy':'match two differently scaled sets','focal_target':'sensor_root','camera_angle_reason':'shows layers','camera_movement_reason':'follow glass','camera_move':'push-through','shot_size':'macro','transition_intent':'cut to sensor','narration':'Di dalam layar...'}
   f.write_text(json.dumps({'fps':30,'shots':[shot]}))
   r=run('validate_virtual_cinematography.py',f,'--strict');self.assertEqual(r.returncode,0,r.stdout)
   run('build_camera_briefs.py',f,'--output',p/'briefs');self.assertIn('non-destructive',list((p/'briefs').glob('*.md'))[0].read_text())
if __name__=='__main__':unittest.main()
