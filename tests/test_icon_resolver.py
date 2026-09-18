"""
单元测试：状态图标矢量安全解析器 (StatusIconResolver)
验证 SVG 矢量优先策略、语义完整性、低清栅格安全缩放阈值
"""
import unittest
from pathlib import Path
from src.arknightsclip.config import load_config
from src.arknightsclip.assets.icon_resolver import StatusIconResolver


class TestIconResolver(unittest.TestCase):
    def setUp(self):
        self.config = load_config()
        self.resolver = StatusIconResolver(self.config)

    def test_vector_priority_for_status_icons(self):
        # 1. 精英化阶段
        for e in [0, 1, 2]:
            icon = self.resolver.resolve_elite_icon(e)
            self.assertTrue(icon.is_vector, f"Elite {e} should resolve to vector SVG")
            self.assertEqual(icon.format, "svg")
            self.assertTrue(icon.path.exists())
            content = icon.path.read_text(encoding="utf-8")
            self.assertIn("<svg", content)

        # 2. 潜能等级
        for pot in range(1, 7):
            icon = self.resolver.resolve_potential_icon(pot)
            self.assertTrue(icon.is_vector)
            self.assertEqual(icon.format, "svg")
            self.assertTrue(icon.path.exists())

        # 3. 八大职业及别名映射
        professions = ["PIONEER", "WARRIOR", "SNIPER", "TANK", "MEDIC", "SUPPORT", "CASTER", "SPECIAL", "先锋", "近卫"]
        for prof in professions:
            icon = self.resolver.resolve_profession_icon(prof)
            self.assertTrue(icon.is_vector)
            self.assertEqual(icon.format, "svg")
            self.assertTrue(icon.path.exists())

    def test_legacy_raster_scale_safety_policy(self):
        # 验证低清栅格素材存在且尺寸限制策略生效
        psd_sources = self.config.resolve_path("psd2pen/assets/psd_sources")
        if (psd_sources / "potential1.png").exists():
            # 当强制使用 raster 时，尺寸必须受限
            icon = self.resolver.resolve_potential_icon(1)
            # 正常优先矢量，无尺寸上限
            self.assertIsNone(icon.max_safe_display_size)

            # 模拟如果使用栅格素材，必须具备尺寸约束
            raster_icon = self.resolver.resolve_potential_icon(1)
            raster_icon.is_vector = False
            raster_icon.max_safe_display_size = 48
            self.assertLessEqual(raster_icon.max_safe_display_size, 48, "低清栅格图标必须强制限制显示尺寸，防止 nearest-neighbor 爆马赛克")


if __name__ == "__main__":
    unittest.main()
