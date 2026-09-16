import unittest
import numpy as np
from arknightsclip.models.operbox import CardROI, CardCropCandidate

class TestOperBoxCropSelection(unittest.TestCase):
    def test_edge_rejection_and_scoring(self):
        c1 = CardCropCandidate(
            char_id="char_103_angel", name="��使�", page_index=1, card_index=1,
            source_page="page_0001.png", roi=CardROI(10, 50, 80, 400),
            quality_score=0.25, crop_image=np.zeros((400, 80, 3), dtype=np.uint8),
            is_edge=True, rejection_reason="partial_edge_card"
        )
        c2 = CardCropCandidate(
            char_id="char_103_angel", name="��使�", page_index=2, card_index=3,
            source_page="page_0002.png", roi=CardROI(300, 50, 190, 440),
            quality_score=0.92, crop_image=np.zeros((440, 190, 3), dtype=np.uint8),
            is_edge=False, rejection_reason=None
        )
        candidates = [c1, c2]

        valid = [c for c in candidates if not c.is_edge]
        self.assertEqual(len(valid), 1)
        best = max(valid, key=lambda c: c.quality_score)
        self.assertEqual(best.page_index, 2)
        self.assertEqual(best.quality_score, 0.92)

if __name__ == '__main__':
    unittest.main()
