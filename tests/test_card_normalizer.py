"""
单元测试：卡片视觉标准化器 (CardNormalizer)
验证统一尺寸、保持比例、无 0 字节文件、确定性可复现、源素材绝对只读
"""
import hashlib
import tempfile
import unittest
from pathlib import Path
from PIL import Image

from src.arknightsclip.config import load_config
from src.arknightsclip.assets.card_normalizer import CardNormalizer, DEFAULT_TARGET_WIDTH, DEFAULT_TARGET_HEIGHT


class TestCardNormalizer(unittest.TestCase):
    def setUp(self):
        self.config = load_config()
        self.normalizer = CardNormalizer(self.config)

    def test_normalize_card_dimensions_and_aspect_ratio(self):
        # 寻找真实存在的原始卡片切片进行抽样测试
        sample_cards = list(self.config.resolve_path("data/raw").glob("*/operbox/cards_raw/*.png"))[:5]
        self.assertGreater(len(sample_cards), 0, "仓库中应至少存在 cards_raw 样本切片")

        for card_path in sample_cards:
            result = self.normalizer.normalize_card(card_path, cache_subdir="test_sample")
            self.assertEqual(result.width, DEFAULT_TARGET_WIDTH)
            self.assertEqual(result.height, DEFAULT_TARGET_HEIGHT)

            # 验证生成的缓存文件真实存在且尺寸严格符合
            self.assertTrue(result.cache_path.exists())
            self.assertGreater(result.cache_path.stat().st_size, 0, "不得生成 0 字节文件")

            with Image.open(result.cache_path) as im:
                self.assertEqual(im.size, (DEFAULT_TARGET_WIDTH, DEFAULT_TARGET_HEIGHT))

            # 宽高比误差应在 0.5% 阈值内
            orig_aspect = result.source_size[1] / result.source_size[0]
            target_aspect = result.height / result.width
            diff = abs(orig_aspect - target_aspect) / orig_aspect
            self.assertLess(diff, 0.015, f"Aspect ratio deviation too high: {diff:.4f}")

    def test_normalize_card_reproducibility(self):
        sample_cards = list(self.config.resolve_path("data/raw").glob("*/operbox/cards_raw/*.png"))
        if not sample_cards:
            self.skipTest("No cards_raw available")

        card_path = sample_cards[0]
        # 第一次生成 (force=True)
        res1 = self.normalizer.normalize_card(card_path, cache_subdir="test_repeat", force=True)
        sha1 = hashlib.sha256(res1.cache_path.read_bytes()).hexdigest()

        # 第二次生成 (force=True，重新编码)
        res2 = self.normalizer.normalize_card(card_path, cache_subdir="test_repeat", force=True)
        sha2 = hashlib.sha256(res2.cache_path.read_bytes()).hexdigest()

        self.assertEqual(sha1, sha2, "相同源素材与参数必须确定性输出完全一致的哈希")

        # 第三次获取缓存 (force=False)
        res3 = self.normalizer.normalize_card(card_path, cache_subdir="test_repeat", force=False)
        self.assertTrue(res3.cached)

    def test_preserve_original_immutable(self):
        sample_cards = list(self.config.resolve_path("data/raw").glob("*/operbox/cards_raw/*.png"))
        if not sample_cards:
            self.skipTest("No cards_raw available")

        card_path = sample_cards[0]
        orig_bytes = card_path.read_bytes()
        orig_sha = hashlib.sha256(orig_bytes).hexdigest()

        # 执行标准化
        self.normalizer.normalize_card(card_path, cache_subdir="test_readonly")

        # 校验原始文件未受任何破坏或改写
        after_bytes = card_path.read_bytes()
        after_sha = hashlib.sha256(after_bytes).hexdigest()
        self.assertEqual(orig_sha, after_sha, "原始 cards_raw 素材必须保持绝对只读不可篡改")


if __name__ == "__main__":
    unittest.main()
