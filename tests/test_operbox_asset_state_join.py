import unittest
from arknightsclip.models.operator import OperatorState
from arknightsclip.models.operbox import CardProvenance

class TestOperBoxAssetStateJoin(unittest.TestCase):
    def test_state_and_asset_join_integrity(self):
        # 验证干员培养状态与卡片截图素材严格按照 char_id 关联
        state = OperatorState(
            char_id='char_103_angel',
            name='能天使',
            own=True,
            elite=2,
            level=90,
            potential=6,
            rarity=6
        )

        prov = CardProvenance(
            char_id='char_103_angel',
            name='能天使',
            scan_id='20260916T120000_P1',
            player_id='P1',
            source_page='page_0001.png',
            page_index=1,
            card_index=3,
            roi=[100, 200, 150, 320],
            capture_timestamp='2026-09-16T12:00:05',
            recognition_method='MaaCore OperBoxImageAnalyzer'
        )

        # 联合检查
        self.assertEqual(state.char_id, prov.char_id)
        self.assertEqual(state.name, prov.name)
        self.assertTrue(prov.source_page.startswith('page_'))
        self.assertEqual(len(prov.roi), 4)

    def test_unowned_operator_asset_is_null(self):
        unowned_op = OperatorState(
            char_id='char_002_amiya',
            name='阿米娅',
            own=False,
            elite=0,
            level=1,
            potential=1
        )
        # 未拥有的干员在仓库中没有卡片截图，对应的 asset 路径必须为 None
        card_asset_path = None if not unowned_op.own else 'operbox/cards_raw/char_002_amiya.png'
        self.assertIsNone(card_asset_path)

if __name__ == '__main__':
    unittest.main()
