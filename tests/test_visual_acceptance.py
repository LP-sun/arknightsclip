"""
Unit tests for Rhine visual acceptance and contact sheet coverage.
"""

from pathlib import Path
import unittest


class TestVisualAcceptance(unittest.TestCase):
    def setUp(self):
        self.repo_root = Path(__file__).resolve().parents[1]
        self.acceptance_dir = self.repo_root / "reports" / "acceptance_frames"
        self.report_md = self.repo_root / "reports" / "rhine_visual_acceptance.md"

    def test_visual_acceptance_frames_exist(self):
        expected_frames = [
            "01_intro_hero_art_char_103_angel.png",
            "02_hero_art_char_017_huang.png",
            "03_card_art_fallback_char_472_pasngr.png",
            "04_mid_sequence_transition.png",
            "05_ending_scene.png",
            "contact_sheet.png",
        ]
        for name in expected_frames:
            frame_path = self.acceptance_dir / name
            self.assertTrue(frame_path.is_file(), f"Missing acceptance frame: {name}")
            self.assertGreater(frame_path.stat().st_size, 50_000, f"Frame {name} is unusually small")

    def test_visual_acceptance_report_contents(self):
        self.assertTrue(self.report_md.is_file(), "Missing rhine_visual_acceptance.md")
        content = self.report_md.read_text(encoding="utf-8")
        self.assertIn("Rhine Renderer Visual Acceptance Report", content)
        self.assertIn("1920 x 1080", content)
        self.assertIn("char_103_angel", content)
        self.assertIn("char_472_pasngr", content)
        self.assertIn("hero_art", content)
        self.assertIn("card_art", content)


if __name__ == "__main__":
    unittest.main()
