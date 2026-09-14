"""
测试注册表消歧、资产解析与团队统计分析
"""

# 测试注册表消歧、资产解析与团队统计分析
from pathlib import Path
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

def test_asset_resolver_validation(config, registry):
    resolver = AssetResolver(config, registry)
    # 能天使应已有资产 (在 assets/operators/char_103_angel/)
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
