"""Basic offline regression tests for utilities; no Blender or internet required."""
import json,pathlib,subprocess,sys,tempfile,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
def run(*cmd):return subprocess.run([sys.executable,str(ROOT/'scripts'/cmd[0]),*cmd[1:]],capture_output=True,text=True)
class SkillTests(unittest.TestCase):
    def test_topic_ranker(self):
        p=run('rank_topics.py',str(ROOT/'templates/topic_candidates.example.json'))
        self.assertEqual(p.returncode,0,p.stderr)
        self.assertEqual(json.loads(p.stdout)['ranked_topics'][0]['production_ready'],False)
    def test_research_gate(self):
        p=run('validate_research.py',str(ROOT/'templates/claims.example.json'))
        self.assertEqual(p.returncode,0,p.stderr)
        p=run('validate_research.py',str(ROOT/'templates/claims.example.json'),'--strict')
        self.assertNotEqual(p.returncode,0)
    def test_scaffold_and_handoff(self):
        with tempfile.TemporaryDirectory() as t:
            project=pathlib.Path(t)/'project';hand=pathlib.Path(t)/'handoff'
            p=run('plan_project.py','--topic','Kenapa bisa?','--niche','facts','--output',str(project))
            self.assertEqual(p.returncode,0,p.stderr)
            self.assertTrue((project/'research/claims.json').exists())
            p=run('validate_manifest.py',str(project/'asset_manifest.json'))
            self.assertEqual(p.returncode,0,p.stderr)
            caps=pathlib.Path(t)/'captions.json'
            caps.write_text(json.dumps({'captions':[{'start':0,'end':2.5,'text':'Halo, dunia.'}]}))
            p=run('build_postproduction.py','--shots',str(project/'shot_plan.json'),'--captions',str(caps),'--output',str(hand))
            self.assertEqual(p.returncode,0,p.stderr)
            self.assertTrue((hand/'edit_decisions.csv').exists())
            self.assertIn('00:00:02,500',(hand/'captions.srt').read_text())
    def test_word_captions_and_editorial_cues(self):
        with tempfile.TemporaryDirectory() as t:
            root=pathlib.Path(t);plan=root/'shot_plan.json';words=root/'words.json';out=root/'handoff'
            plan.write_text(json.dumps({'fps':30,'total_frames':90,'shots':[{'id':'shot_01','start_frame':1,'end_frame':60},{'id':'shot_02','start_frame':61,'end_frame':90}]}))
            words.write_text(json.dumps({'words':[{'start':0.1,'end':0.4,'text':'Pernah'},{'start':0.42,'end':0.7,'text':'nggak,'}]}))
            p=run('build_postproduction.py','--shots',str(plan),'--word-captions',str(words),'--output',str(out))
            self.assertEqual(p.returncode,0,p.stderr)
            self.assertIn('Pernah',(out/'word_captions.srt').read_text())
            self.assertEqual(len((out/'editorial_cues.csv').read_text(encoding='utf-8-sig').splitlines()),3)
            self.assertIn('PENDING_CAPCUT_HANDOFF',(out/'shot_status.json').read_text())
    def test_reject_fake_sentence_as_word(self):
        with tempfile.TemporaryDirectory() as t:
            root=pathlib.Path(t);plan=root/'plan.json';words=root/'words.json'
            plan.write_text(json.dumps({'fps':30,'shots':[{'id':'a','start_frame':1,'end_frame':90}]}))
            words.write_text(json.dumps({'words':[{'start':0,'end':1,'text':'dua kata'}]}))
            p=run('build_postproduction.py','--shots',str(plan),'--word-captions',str(words),'--output',str(root/'out'))
            self.assertNotEqual(p.returncode,0)
    def test_ready_shot_requires_real_file(self):
        with tempfile.TemporaryDirectory() as t:
            root=pathlib.Path(t);plan=root/'plan.json'
            plan.write_text(json.dumps({'fps':30,'shots':[{'id':'a','start_frame':1,'end_frame':30}]}))
            p=run('build_postproduction.py','--shots',str(plan),'--output',str(root/'out'),'--ready-shot','a','--clip',str(root/'missing.mp4'))
            self.assertNotEqual(p.returncode,0)
    def test_handoff_rejects_gap(self):
        with tempfile.TemporaryDirectory() as t:
            plan=pathlib.Path(t)/'plan.json';plan.write_text(json.dumps({'fps':30,'shots':[{'id':'A','start_frame':2,'end_frame':30}]}))
            p=run('build_postproduction.py','--shots',str(plan),'--output',str(pathlib.Path(t)/'out'))
            self.assertNotEqual(p.returncode,0)
if __name__=='__main__':unittest.main()

# v4 additions are loaded by unittest discovery from a separate test module.
