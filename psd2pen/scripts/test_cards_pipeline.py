import copy
import unittest
import tempfile
from pathlib import Path
from cards_pipeline import ROOT, read, validate, node, compile_batch

class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.data=read(ROOT/'inputs/five_operators.json')
        self.catalog=read(ROOT/'config/cards_assets.json')

    def test_real_40_slots(self):
        validate(self.data,self.catalog)
        self.assertEqual(sum(len(j['slots']) for j in self.data['operators']),40)

    def test_elite_zero_preserved(self):
        job=self.data['operators'][1];s=job['slots'][7]
        self.assertEqual(s['elite'],0)
        self.assertEqual(node(job,s,self.catalog)['descendants']['vH1ov']['fill']['url'],'assets/psd_sources/elite0.png')

    def test_missing_not_zero(self):
        self.data['operators'][1]['slots'][4]['elite']=None
        with self.assertRaises(ValueError):validate(self.data,self.catalog)

    def test_duplicate_slot(self):
        self.data['operators'][0]['slots'][0]['slot']=2
        with self.assertRaises(ValueError):validate(self.data,self.catalog)

    def test_fractional_level_rejected(self):
        self.data['operators'][0]['slots'][1]['level']=60.5
        with self.assertRaises(ValueError):validate(self.data,self.catalog)

    def test_hidden_instance_keeps_data(self):
        job=self.data['operators'][0];s=copy.deepcopy(job['slots'][1]);s['visible']=False
        n=node(job,s,self.catalog)
        self.assertFalse(n['enabled']);self.assertEqual(n['descendants']['bFlti']['content'],str(s['level']))

    def test_five_slot_batch_retains_eight_nodes(self):
        import json
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp)/'run'
            compile_batch(ROOT/'inputs/five_operators.json',ROOT/'config/cards_assets.json',out,'3l2r')
            manifest=read(out/'run.json')
            self.assertEqual(len(manifest['commands']),5)
            for command in manifest['commands']:
                self.assertTrue(command['filePath'].endswith('character_cards_5slot.pen'))
                js=Path(command['inputFile']).read_text(encoding='utf-8')
                nodes=json.loads(js.splitlines()[0][len('const nodes='):-1])
                self.assertEqual(len(nodes),8)
                self.assertEqual([i+1 for i,n in enumerate(nodes) if n['enabled']],[1,2,3,5,6])
                self.assertEqual(sum(n['enabled'] and n['ref']=='HVZ4i' for n in nodes),3)
                self.assertEqual(sum(n['enabled'] and n['ref']=='wUVzi' for n in nodes),2)
                self.assertIn('individual_exports', js)

    def test_changed_input_rejects_stale_run(self):
        from pencil_batch import check_run
        with tempfile.TemporaryDirectory() as tmp:
            source=Path(tmp)/'input.json'
            source.write_bytes((ROOT/'inputs/five_operators.json').read_bytes())
            out=Path(tmp)/'run'
            compile_batch(source,ROOT/'config/cards_assets.json',out,'3l2r')
            check_run(out/'run.json')
            source.write_text('{}',encoding='utf-8')
            with self.assertRaisesRegex(ValueError,'Stale input'):
                check_run(out/'run.json')

    def test_unowned_hides_stats(self):
        job=self.data['operators'][0];n=node(job,job['slots'][0],self.catalog)
        self.assertTrue(n['descendants']['MxQrR']['enabled'])
        self.assertFalse(n['descendants']['QEG16']['enabled'])

if __name__=='__main__':unittest.main()
