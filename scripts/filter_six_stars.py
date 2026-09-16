"""
按用户要求：严格过滤仅保留六星干员 (rarity == 6)
1. 过滤 data/raw/P1/operators.json -> 仅保留六星干员 (146 位六星，P1 拥有 100 位)
2. 更新 data/raw/P1/profile.json -> 六星专属统计
3. 清理 data/raw/P1/operbox/cards_raw/ 中非六星卡片
4. 清理 data/manifests/ 中非六星清单，重新生成纯六星 SceneManifest
5. 更新 data/normalized/five_players.json
"""

import json
from pathlib import Path
from arknightsclip.config import load_config
from arknightsclip.registry.operator_registry import OperatorRegistry
from arknightsclip.scene.builder import SceneBuilder
from arknightsclip.data.dataset_manager import DatasetManager

def filter_to_six_stars():
    config = load_config()
    reg = OperatorRegistry(config.resolve_path("src/arknightsclip/registry/operator_registry.json"))

    raw_dir = config.get_raw_player_dir("P1")
    ops_file = raw_dir / "operators.json"
    cards_dir = raw_dir / "operbox" / "cards_raw"
    manifests_dir = config.get_manifests_dir()

    # 1. 过滤 operators.json
    with open(ops_file, "r", encoding="utf-8") as f:
        all_ops = json.load(f)

    six_star_ids = {e.char_id for e in reg.all_operators() if e.rarity == 6}
    six_star_ops = [o for o in all_ops if o["char_id"] in six_star_ids or o.get("rarity") == 6]

    owned_count = sum(1 for o in six_star_ops if o["own"])
    print(f"[Filter] 六星干员总数: {len(six_star_ops)}, P1 实际拥有: {owned_count}")

    with open(ops_file, "w", encoding="utf-8") as f:
        json.dump(six_star_ops, f, ensure_ascii=False, indent=2)
    print(f"✓ 已重写 {ops_file}，仅保留 {len(six_star_ops)} 位六星干员")

    # 2. 更新 profile.json
    prof_file = raw_dir / "profile.json"
    if prof_file.exists():
        with open(prof_file, "r", encoding="utf-8") as f:
            prof = json.load(f)
        prof["target_rarity"] = 6
        prof["six_star_owned"] = owned_count
        prof["six_star_total"] = len(six_star_ops)
        prof["six_star_rate"] = f"{owned_count / len(six_star_ops) * 100:.1f}%"
        with open(prof_file, "w", encoding="utf-8") as f:
            json.dump(prof, f, ensure_ascii=False, indent=2)
        print(f"✓ 已更新 {prof_file}")

    # 3. 清理 cards_raw 中的非六星卡片
    if cards_dir.exists():
        removed_count = 0
        for p in list(cards_dir.glob("*.png")):
            cid = p.stem
            entry = reg.get_by_id(cid)
            if entry and entry.rarity != 6:
                p.unlink()
                json_p = p.with_suffix(".json")
                if json_p.exists():
                    json_p.unlink()
                removed_count += 1
            elif not entry and not cid.startswith("char_"):
                # 未知/非干员临时切片清理
                p.unlink()
                json_p = p.with_suffix(".json")
                if json_p.exists():
                    json_p.unlink()
                removed_count += 1

        print(f"✓ 已清理 {removed_count} 份非六星卡片素材，剩余保留六星切片")

    # 4. 清理并重构 manifests (仅限 6 星)
    if manifests_dir.exists():
        for m in list(manifests_dir.glob("*.json")):
            m.unlink()
        print(f"✓ 已清空旧 manifests 目录")

    # 5. 更新 normalized five_players.json
    dm = DatasetManager(config, reg)
    ds = dm.merge_players(["P1"])
    print(f"✓ 已同步更新 {config.get_normalized_dir() / 'five_players.json'}")

    # 6. 重新构建 6 星 manifests
    sb = SceneBuilder(config, registry=reg)
    manifests = sb.build_all_scenes(rarity=6)
    print(f"✓ 成功生成 {len(manifests)} 份纯六星干员 SceneManifest 至: {manifests_dir}")

if __name__ == "__main__":
    filter_to_six_stars()
