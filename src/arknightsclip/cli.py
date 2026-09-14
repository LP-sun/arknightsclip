"""
arknightsclip 统一命令行入口 (CLI)
支持子命令：
  collect-player   采集单玩家干员仓库数据
  merge-players    合并多玩家数据至 data/normalized/five_players.json
  analyze-group    执行五人练度深度统计并输出审计报告
  sync-assets      同步与抽取干员立绘素材
  validate-assets  校验目标干员立绘完整性 (坚决报错，绝不偷换能天使)
  spike-psd        执行单一 PSD 模板动态操作技术验证
"""

import argparse
import sys
from pathlib import Path
from .config import load_config
from .registry.operator_registry import OperatorRegistry
from .assets.resolver import AssetResolver
from .data.dataset_manager import DatasetManager
from .data.group_stats import GroupStatsAnalyzer
from .photoshop.spike import run_photoshop_spike

def main():
    parser = argparse.ArgumentParser(description="明日方舟报菜名 - 自动化流水线")
    subparsers = parser.add_subparsers(dest="command", help="可执行子命令")

    # 1. collect-player
    p_collect = subparsers.add_parser("collect-player", help="采集单名玩家干员数据")
    p_collect.add_argument("--player", required=True, help="玩家标识，如 P1, P2")
    p_collect.add_argument("--name", default="博士", help="玩家昵称")
    p_collect.add_argument("--pages", type=int, default=5, help="最大截屏翻页数")

    # 2. merge-players
    subparsers.add_parser("merge-players", help="合并各玩家 raw 数据至规范化 canonical JSON")

    # 3. analyze-group
    subparsers.add_parser("analyze-group", help="深度统计五人团队图鉴与练度指标")

    # 4. sync-assets
    subparsers.add_parser("sync-assets", help="从历史素材源同步缓存立绘素材")

    # 5. validate-assets
    p_val_assets = subparsers.add_parser("validate-assets", help="校验目标干员素材完整性")
    p_val_assets.add_argument("--rarity", type=int, default=6, help="校验的干员稀有度")

    # 6. spike-psd
    subparsers.add_parser("spike-psd", help="运行 Photoshop 单槽位动态操作 Spike")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    cfg = load_config()
    reg = OperatorRegistry(cfg.resolve_path("src/arknightsclip/registry/operator_registry.json"))

    if args.command == "collect-player":
        from .maa.collector import PlayerCollector
        collector = PlayerCollector(cfg)
        collector.collect(args.player, args.name, max_pages=args.pages)

    elif args.command == "merge-players":
        dm = DatasetManager(cfg, reg)
        ds = dm.merge_players()
        excel_out = cfg.resolve_path("data/normalized/five_players_inspection.xlsx")
        dm.export_excel_for_inspection(ds, excel_out)

    elif args.command == "analyze-group":
        dm = DatasetManager(cfg, reg)
        norm_file = cfg.resolve_path("data/normalized/five_players.json")
        if not norm_file.exists():
            print("[CLI] five_players.json 不存在，先执行 merge-players...")
            ds = dm.merge_players()
        else:
            import json
            from .models.player import FivePlayersDataset
            with open(norm_file, "r", encoding="utf-8") as f:
                ds = FivePlayersDataset.from_dict(json.load(f))

        analyzer = GroupStatsAnalyzer(reg)
        stats = analyzer.analyze(ds)
        json_out = cfg.resolve_path("reports/group_stats.json")
        md_out = cfg.resolve_path("reports/group_stats.md")
        analyzer.export_reports(stats, json_out, md_out)

    elif args.command == "sync-assets":
        resolver = AssetResolver(cfg, reg)
        resolver.sync_from_existing_sources()
        print(f"[CLI] 素材已同步至: {resolver.assets_root}")

    elif args.command == "validate-assets":
        resolver = AssetResolver(cfg, reg)
        target_ops = [e.char_id for e in reg.all_operators() if e.rarity == args.rarity]
        missing = resolver.validate_assets(target_ops)
        if missing:
            print(f"[CLI] 警告: 发现 {len(missing)} 位目标干员缺失立绘素材:")
            for m in missing[:15]:
                print(f"  - 缺失: {m}")
            if len(missing) > 15:
                print(f"  ... 等共 {len(missing)} 位")
        else:
            print(f"[CLI] 完美！所有 {len(target_ops)} 位目标干员素材均已就绪。")

    elif args.command == "spike-psd":
        report = run_photoshop_spike()
        print(f"[CLI] Photoshop Spike 完成: {report['status']}")
        for f in report["verified_features"]:
            print(f"  ✓ {f}")

if __name__ == "__main__":
    main()
