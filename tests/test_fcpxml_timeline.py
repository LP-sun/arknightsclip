import unittest
import tempfile
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

_src_dir = Path(__file__).resolve().parent.parent / "src"
if str(_src_dir) not in sys.path:
    sys.path.insert(0, str(_src_dir))

from arknightsclip.config import load_config
from arknightsclip.timeline.fcpxml_generator import FCPXMLGenerator
from arknightsclip.timeline.otio_generator import OTIOGenerator

class TestTimelineGenerators(unittest.TestCase):
    def setUp(self):
        self.config = load_config()
        self.xml_gen = FCPXMLGenerator(self.config)
        self.otio_gen = OTIOGenerator(self.config)

    def test_fcpxml_structure_and_integrity(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            out_xml = Path(tmp_dir) / "test_timeline.xml"
            res_path = self.xml_gen.build_timeline_xml(output_xml=out_xml)
            self.assertTrue(res_path.exists())

            # 解析并验证 XML 契约
            tree = ET.parse(res_path)
            root = tree.getroot()
            self.assertEqual(root.tag, "xmeml")
            self.assertEqual(root.get("version"), "4")

            seq = root.find("sequence")
            self.assertIsNotNone(seq)
            self.assertEqual(seq.find("rate/timebase").text, "24")
            self.assertEqual(seq.find("rate/ntsc").text, "FALSE")
            self.assertEqual(seq.find("duration").text, "4470")

            # 验证 4 个视频轨
            v_tracks = seq.findall("media/video/track")
            self.assertEqual(len(v_tracks), 4)

            # 验证 2 个音频轨
            a_tracks = seq.findall("media/audio/track")
            self.assertEqual(len(a_tracks), 2)

    def test_otio_generation(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            out_otio = Path(tmp_dir) / "test_timeline.otio"
            res_path = self.otio_gen.build_timeline_otio(output_path=out_otio)
            self.assertTrue(res_path.exists())
            self.assertGreater(res_path.stat().st_size, 100)

if __name__ == "__main__":
    unittest.main()
