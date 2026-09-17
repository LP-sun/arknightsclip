import sys
from pathlib import Path
_project_root = Path(__file__).resolve().parent.parent
_src_dir = _project_root / "src"
if str(_src_dir) not in sys.path:
    sys.path.insert(0, str(_src_dir))
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

import unittest
from arknightsclip.models.operbox import CardROI, CardProvenance, CardCropCandidate, OperBoxScanSession

class TestOperBoxSchema(unittest.TestCase):
    def test_card_roi_conversion(self):
        roi = CardROI(x=100, y=200, width=150, height=320, source_width=1920, source_height=1080)
        self.assertEqual(roi.to_list(), [100, 200, 150, 320])
        recreated = CardROI.from_list([100, 200, 150, 320], 1920, 1080)
        self.assertEqual(recreated.x, 100)
        self.assertEqual(recreated.y, 200)
        self.assertEqual(recreated.width, 150)
        self.assertEqual(recreated.height, 320)

    def test_provenance_schema_serialization(self):
        prov = CardProvenance(
            char_id="char_103_angel",
            name="��使�",
            scan_id="20260916T120000_P1",
            player_id="P1",
            source_page="page_0002.png",
            page_index=2,
            card_index=4,
            roi=[120, 240, 150, 320],
            capture_timestamp="2026-09-16T12:00:05",
            recognition_method="MaaCore OperBoxImageAnalyzer",
            candidate_count=2,
            selected_reason="best_quality_score_0.95"
        )
        d = prov.to_dict()
        self.assertEqual(d["char_id"], "char_103_angel")
        self.assertEqual(d["source_page"], "page_0002.png")
        self.assertEqual(d["roi"], [120, 240, 150, 320])
        self.assertEqual(d["player_id"], "P1")

        loaded = CardProvenance.from_dict(d)
        self.assertEqual(loaded.char_id, prov.char_id)
        self.assertEqual(loaded.scan_id, prov.scan_id)

    def test_scan_session_summary(self):
        sess = OperBoxScanSession(scan_id="test_scan_01", player_id="P1")
        sess.pages_captured = 3
        sess.operators_found = 45
        sess.card_assets_captured = 45
        summary = sess.to_summary()
        self.assertEqual(summary["scan_id"], "test_scan_01")
        self.assertEqual(summary["operators_found"], 45)
        self.assertEqual(summary["card_assets_captured"], 45)
        self.assertEqual(summary["missing_card_assets"], [])

    def test_name_roi_bicubic_upscale(self):
        import numpy as np
        from arknightsclip.config import load_config
        from arknightsclip.maa.operbox_analyzer import OperBoxAnalyzer

        cfg = load_config()
        analyzer = OperBoxAnalyzer(cfg)
        captured_shapes = []

        class MockOCR:
            def readtext(self, img):
                captured_shapes.append(img.shape)
                return [([], "令", 0.99)]

        analyzer._ocr_reader = MockOCR()
        # 创建 720p 模拟帧 (720, 1280, 3)
        frame = np.zeros((720, 1280, 3), dtype=np.uint8)
        # 调用 _recognize_name (锚点 fx=100, fy=200)
        name, conf = analyzer._recognize_name(frame, 100, 200)
        self.assertEqual(name, "令")
        self.assertEqual(conf, 0.99)
        self.assertEqual(len(captured_shapes), 1)
        # 原名字条尺寸 dw=128, dh=22
        # 双三次 2.0x 放大后高应为 44, 宽应为 256
        h, w = captured_shapes[0][:2]
        self.assertEqual(h, 44)
        self.assertEqual(w, 256)

if __name__ == '__main__':
    unittest.main()
