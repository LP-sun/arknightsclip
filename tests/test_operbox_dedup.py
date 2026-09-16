import unittest
from arknightsclip.models.operator import OperatorState
from arknightsclip.models.operbox import CardROI, CardCropCandidate

class TestOperBoxDedup(unittest.TestCase):
    def test_dedup_across_pages(self):
        op1 = OperatorState(char_id='char_103_angel', name='Exusiai', own=True, elite=2, level=1, potential=6)
        op2 = OperatorState(char_id='char_103_angel', name='Exusiai', own=True, elite=2, level=90, potential=6)

        all_states = {}
        for op in [op1, op2]:
            if op.char_id not in all_states:
                all_states[op.char_id] = op
            else:
                existing = all_states[op.char_id]
                if existing.level == 1 and op.level > 1:
                    existing.level = op.level

        self.assertEqual(len(all_states), 1)
        self.assertEqual(all_states['char_103_angel'].level, 90)

    def test_candidate_dedup_best_selection(self):
        cands = [
            CardCropCandidate('char_010_chen', 'Chen', 1, 1, 'page_01', CardROI(10,10,10,10), 0.45),
            CardCropCandidate('char_010_chen', 'Chen', 2, 3, 'page_02', CardROI(300,10,10,10), 0.88),
            CardCropCandidate('char_010_chen', 'Chen', 3, 2, 'page_03', CardROI(100,10,10,10), 0.70),
        ]
        best = max(cands, key=lambda c: c.quality_score)
        self.assertEqual(best.page_index, 2)
        self.assertEqual(best.quality_score, 0.88)

if __name__ == '__main__':
    unittest.main()
