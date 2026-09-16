import copy
import unittest
from cards_pipeline import ROOT, read, validate, node

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
        self.assertFalse(n['enabled']);self.assertEqual(n['descendants']['bFlti']['content'],'90')

    def test_unowned_hides_stats(self):
        job=self.data['operators'][0];n=node(job,job['slots'][0],self.catalog)
        self.assertTrue(n['descendants']['MxQrR']['enabled'])
        self.assertFalse(n['descendants']['QEG16']['enabled'])

if __name__=='__main__':unittest.main()
