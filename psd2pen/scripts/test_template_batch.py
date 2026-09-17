import copy
import unittest
from cards_pipeline import ROOT, read
from template_batch import payload, safe_name


class TemplateBatchTests(unittest.TestCase):
    def setUp(self):
        self.job=read(ROOT/'inputs/five_operators.json')['operators'][0]
        self.catalog=read(ROOT/'config/cards_assets.json')

    def test_presets_and_five_slots(self):
        slots=payload(self.job,self.catalog,'3l2r')
        self.assertEqual([s['slot'] for s in slots if s['visible']],[1,2,3,5,6])
        for src,dst in zip(self.job['slots'],slots):
            for prefix,count,selected in [('elite',3,src['elite']),('potential',6,src['potential'])]:
                values=range(count) if prefix=='elite' else range(1,count+1)
                actual=[v for v in values if dst['fields'][f'{prefix}_{v}']['enabled']]
                self.assertEqual(actual,[] if selected is None else [selected])

    def test_independent_visibility(self):
        job=copy.deepcopy(self.job)
        job['slots'][1]['visibility']={'elite':False,'level':True,'potential':False}
        fields=payload(job,self.catalog,'3l2r')[1]['fields']
        self.assertTrue(fields['level_visible']['enabled'])
        self.assertFalse(fields['elite_visible']['enabled'])
        self.assertFalse(fields['potential_visible']['enabled'])

    def test_reject_bad_filename(self):
        for name in ['../bad','a/b','a\\b','bad:','bad.','']:
            with self.assertRaises(ValueError):safe_name(name)

    def test_duplicate_player(self):
        job=copy.deepcopy(self.job);job['slots'][1]['player']=job['slots'][0]['player']
        with self.assertRaises(ValueError):payload(job,self.catalog,'3l2r')


if __name__=='__main__':unittest.main()
