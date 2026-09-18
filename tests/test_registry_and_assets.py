"""
测试注册表消歧、资产解析与团队统计分析
"""

# 测试注册表消歧、资产解析与团队统计分析
from pathlib import Path
from dataclasses import replace
from tempfile import TemporaryDirectory
from src.arknightsclip.config import load_config
from src.arknightsclip.registry.operator_registry import OperatorRegistry
from src.arknightsclip.assets.resolver import AssetResolver
from src.arknightsclip.data.dataset_manager import DatasetManager
from src.arknightsclip.data.group_stats import GroupStatsAnalyzer

def config():
    return load_config()

def registry(cfg=None):
    if cfg is None:
        cfg = config()
    reg_path = cfg.resolve_path("src/arknightsclip/registry/operator_registry.json")
    return OperatorRegistry(reg_path)

def test_registry_resolution(registry):
    # 官方全称
    e1 = registry.resolve("能天使")
    assert e1 is not None
    assert e1.char_id == "char_103_angel"
    assert e1.rarity == 6

    # 别名 / 简称
    e2 = registry.resolve("推王")
    assert e2 is not None
    assert e2.canonical_name_zh == "推进之王"

    # 代号 42
    e3 = registry.resolve("42")
    assert e3 is not None
    assert e3.canonical_name_zh == "史尔特尔"

    # 前缀编号
    e4 = registry.resolve("001_能天使")
    assert e4 is not None
    assert e4.char_id == "char_103_angel"

def test_operator_registry_p0_aliases_and_ocr_protection(registry):
    # 1. 鸿雪 / Pozyomka / Pozëmka -> char_4055_bgsnow
    for name in ["鸿雪", "Pozyomka", "Pozëmka"]:
        e = registry.resolve(name)
        assert e is not None, f"Failed to resolve {name}"
        assert e.char_id == "char_4055_bgsnow", f"{name} mapped to {e.char_id}, expected char_4055_bgsnow"

    # 2. 卡涅利安 / Carnelian -> char_426_billro
    for name in ["卡涅利安", "Carnelian"]:
        e = registry.resolve(name)
        assert e is not None, f"Failed to resolve {name}"
        assert e.char_id == "char_426_billro", f"{name} mapped to {e.char_id}, expected char_426_billro"

    # 3. 空弦 / Archetto -> char_332_archet
    for name in ["空弦", "Archetto"]:
        e = registry.resolve(name)
        assert e is not None, f"Failed to resolve {name}"
        assert e.char_id == "char_332_archet", f"{name} mapped to {e.char_id}, expected char_332_archet"

    # 4. 絮雨 / Whisperain -> char_436_whispr
    for name in ["絮雨", "Whisperain"]:
        e = registry.resolve(name)
        assert e is not None, f"Failed to resolve {name}"
        assert e.char_id == "char_436_whispr", f"{name} mapped to {e.char_id}, expected char_436_whispr"

    # 5. 空串校验保护
    assert registry.resolve("") is None
    assert registry.resolve("   ") is None

    # 6. 单字干员精确解析
    single_chars = {
        "令": "char_2023_ling",
        "黍": "char_2025_shu",
        "山": "char_264_f12yin",
        "W": "char_113_cqbw",
        "年": "char_2014_nian",
        "夕": "char_2015_dusk",
        "真": "char_4204_mantra",
    }
    for char, expected_id in single_chars.items():
        e = registry.resolve(char)
        assert e is not None, f"Failed to resolve single-char operator {char}"
        assert e.char_id == expected_id, f"{char} resolved to {e.char_id}, expected {expected_id}"

    # 6.1 OCR 字符级修复 (灰亳 -> 灰毫)
    e_ash = registry.resolve("灰亳")
    assert e_ash is not None
    assert e_ash.char_id == "char_431_ashlok"

    # 7. 未知单字不得被 fuzzy fallback 错误匹配到其他干员
    unknown_singles = ["东", "南", "西", "北", "中", "发", "白", "甲", "乙", "丙"]
    for unknown in unknown_singles:
        assert registry.resolve(unknown) is None, f"Unknown single char '{unknown}' was incorrectly resolved"

    # 8. OCR 规范化测试（空格清理，. 与 : 转 ·）
    e_dot = registry.resolve("维娜.维多利亚")
    assert e_dot is not None
    assert e_dot.canonical_name_zh == "维娜·维多利亚"

    e_colon = registry.resolve("维娜:维多利亚")
    assert e_colon is not None
    assert e_colon.canonical_name_zh == "维娜·维多利亚"

    e_space = registry.resolve("维娜 . 维多利亚")
    assert e_space is not None
    assert e_space.canonical_name_zh == "维娜·维多利亚"

def test_asset_resolver_validation(config, registry):
    # 测试必须自包含，不能依赖后续资产缓存 PR 或开发者本机文件。
    with TemporaryDirectory() as tmp_dir:
        test_pipeline = replace(config.pipeline, assets_dir=tmp_dir)
        test_config = replace(config, pipeline=test_pipeline)
        full_art = Path(tmp_dir) / "operators" / "char_103_angel" / "full.png"
        full_art.parent.mkdir(parents=True, exist_ok=True)
        full_art.write_bytes(b"test asset")

        resolver = AssetResolver(test_config, registry)
        assert resolver.has_assets("char_103_angel") is True

        # 故意查询不存在的虚假干员 ID
        missing = resolver.validate_assets(["char_non_existent_test"])
        assert len(missing) == 1
        assert "char_non_existent_test" in missing[0]

def test_group_stats_computation(config, registry):
    dm = DatasetManager(config, registry)
    ds = dm.merge_players()
    assert len(ds.players) == 5

    analyzer = GroupStatsAnalyzer(registry)
    stats = analyzer.analyze(ds)

    assert "target_rarity" in stats
    assert stats["target_rarity"] == 6
    assert "union_coverage_rate" in stats
    assert 0.0 <= stats["union_coverage_rate"] <= 1.0
    assert "jaccard_similarity" in stats
    # 自身相似度必为 1.0
    for pid in ds.players.keys():
        assert stats["jaccard_similarity"][pid][pid] == 1.0

def test_no_unwhitelisted_duplicate_operator_artwork(config):
    """不允许两个不同 canonical operator ID 在没有显式 whitelist 的情况下共享完全相同的 full-art hash。"""
    import hashlib
    from collections import defaultdict

    assets_root = config.resolve_path(config.pipeline.assets_dir) / "operators"
    if not assets_root.exists():
        return

    # 显式白名单：合法共享哈希的 (char_id1, char_id2) 及其原因
    duplicate_whitelist = {}

    hash_to_ops = defaultdict(list)
    for op_dir in sorted(assets_root.iterdir()):
        if not op_dir.is_dir():
            continue
        full_png = op_dir / "full.png"
        if full_png.exists():
            h = hashlib.sha256(full_png.read_bytes()).hexdigest()
            hash_to_ops[h].append(op_dir.name)

    unwhitelisted_duplicates = []
    for h, ops in hash_to_ops.items():
        if len(ops) > 1:
            pair_key = tuple(sorted(ops))
            if pair_key not in duplicate_whitelist:
                unwhitelisted_duplicates.append((h, ops))

    assert not unwhitelisted_duplicates, f"发现未在白名单中的重复立绘哈希: {unwhitelisted_duplicates}"
