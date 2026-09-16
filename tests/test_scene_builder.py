import unittest
import tempfile
import json
import sys
from pathlib import Path

_src_dir = Path(__file__).resolve().parent.parent / "src"
if str(_src_dir) not in sys.path:
    sys.path.insert(0, str(_src_dir))

from arknightsclip.config import load_config
from arknightsclip.models.player import FivePlayersDataset, PlayerDataSet, PlayerProfile
from arknightsclip.models.operator import OperatorState
from arknightsclip.scene.builder import SceneBuilder

class TestSceneBuilder(unittest.TestCase):
    def setUp(self):
        self.config = load_config()
        self.test_dataset = FivePlayersDataset(
            players={
                "P1": PlayerDataSet(
                    player_id="P1",
                    profile=PlayerProfile(id="P1", display_name="测试博士1"),
                    operators={
                        "char_103_angel": OperatorState(
                            char_id="char_103_angel",
                            name="能天使",
                            own=True,
                            elite=2,
                            level=90,
                            potential=6,
                            rarity=6,
                        ),
                    },
                ),
                "P2": PlayerDataSet(
                    player_id="P2",
                    profile=PlayerProfile(id="P2", display_name="测试博士2"),
                    operators={
                        "char_103_angel": OperatorState(
                            char_id="char_103_angel",
                            name="能天使",
                            own=False,
                            elite=0,
                            level=1,
                            potential=1,
                            rarity=6,
                        ),
                    },
                ),
            }
        )
        self.builder = SceneBuilder(config=self.config, dataset=self.test_dataset)

    def test_build_scene_contract(self):
        manifest = self.builder.build_scene("char_103_angel")
        self.assertEqual(manifest.operator_id, "char_103_angel")
        self.assertEqual(manifest.operator_name, "能天使")
        self.assertEqual(manifest.rarity, 6)

        # 检查 P1 槽位
        p1 = manifest.players["P1"]
        self.assertTrue(p1.own)
        self.assertEqual(p1.elite, 2)
        self.assertEqual(p1.level, 90)
        self.assertEqual(p1.potential, 6)
        self.assertFalse(p1.no_info)

        # 检查 P2 槽位 (未拥有)
        p2 = manifest.players["P2"]
        self.assertFalse(p2.own)
        self.assertTrue(p2.no_info)
        self.assertIsNone(p2.card_asset_path)

        # 契约合法性校验
        self.assertTrue(manifest.validate())

    def test_build_all_scenes_persistence(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            out_dir = Path(tmp_dir)
            manifests = self.builder.build_all_scenes(
                target_char_ids=["char_103_angel"],
                save_dir=out_dir,
            )
            self.assertIn("char_103_angel", manifests)
            saved_file = out_dir / "char_103_angel.json"
            self.assertTrue(saved_file.exists())

            with open(saved_file, "r", encoding="utf-8") as f:
                saved_data = json.load(f)
            self.assertEqual(saved_data["operator_id"], "char_103_angel")
            self.assertTrue(saved_data["players"]["P1"]["own"])
            self.assertFalse(saved_data["players"]["P2"]["own"])

if __name__ == "__main__":
    unittest.main()
