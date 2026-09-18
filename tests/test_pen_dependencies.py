"""
Unit tests for Pen asset dependency auditor and resolver.
"""

from pathlib import Path
import unittest

from arknightsclip.assets.pen_dependency_resolver import PenDependencyResolver


class TestPenDependencies(unittest.TestCase):
    def setUp(self):
        self.repo_root = Path(__file__).resolve().parents[1]
        self.resolver = PenDependencyResolver(self.repo_root)

    def test_character_cards_5slot_has_zero_unresolved(self):
        pen_path = self.repo_root / "psd2pen" / "character_cards_5slot.pen"
        if not pen_path.is_file():
            self.skipTest("character_cards_5slot.pen not found")

        result = self.resolver.audit_pen_file(pen_path)
        self.assertEqual(result.missing_count, 0)
        self.assertEqual(result.unique_urls, 55)

    def test_character_cards_5slot_template_raw_batch_resolution(self):
        pen_path = self.repo_root / "psd2pen" / "character_cards_5slot_template.pen"
        if not pen_path.is_file():
            self.skipTest("character_cards_5slot_template.pen not found")

        result = self.resolver.audit_pen_file(pen_path)
        raw_batch_deps = [d for d in result.dependencies.values() if "raw_batch" in d.raw_url]

        self.assertEqual(len(raw_batch_deps), 111)

        # Every raw_batch reference must have a known char_id and remote source URL
        for dep in raw_batch_deps:
            self.assertIsNotNone(dep.char_id)
            self.assertTrue(dep.char_id.startswith("char_"))
            self.assertIsNotNone(dep.remote_source_url)
            self.assertIn(dep.char_id, dep.remote_source_url)
            # Manifest should exist for each 6-star operator
            manifest_file = self.repo_root / "data" / "manifests" / f"{dep.char_id}.json"
            self.assertTrue(manifest_file.is_file(), f"Missing manifest for {dep.char_id}")

            # If hero art exists, resolution_type must be hero_art
            hero_file = self.repo_root / "assets" / "operators" / dep.char_id / "full.png"
            if hero_file.is_file():
                self.assertEqual(dep.resolution_type, "hero_art")
                self.assertTrue(dep.is_present_on_disk)
            else:
                self.assertEqual(dep.resolution_type, "unresolved")

    def test_generate_manifest_creates_valid_reports(self):
        pen_path = self.repo_root / "psd2pen" / "character_cards_5slot.pen"
        if not pen_path.is_file():
            self.skipTest("character_cards_5slot.pen not found")

        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_json = Path(tmpdir) / "pen_manifest.json"
            tmp_md = Path(tmpdir) / "pen_manifest.md"

            manifest = self.resolver.generate_manifest([pen_path], tmp_json, tmp_md)
            self.assertTrue(tmp_json.is_file())
            self.assertTrue(tmp_md.is_file())
            self.assertIn("version", manifest)
            self.assertIn("pen_files", manifest)


if __name__ == "__main__":
    unittest.main()
