#!/usr/bin/env python3
"""Comprehensive visual asset audit for arknightsclip.

Scans raw cards, player profile cards, operator hero art, MAA icons,
and Pen design assets. Produces machine-readable JSON and human-readable Markdown reports.
"""
from __future__ import annotations

import glob
import hashlib
import json
import os
import sys
from collections import Counter, defaultdict
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]


def get_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def audit_operators_and_hero_art() -> dict:
    # 1. Operators from normalized five_players.json
    fp_path = ROOT / "data/normalized/five_players.json"
    five_players_ops: set[str] = set()
    player_counts = {}
    if fp_path.exists():
        with open(fp_path, encoding="utf-8") as f:
            fp_data = json.load(f)
        for pid, pdata in fp_data.get("players", {}).items():
            ops = set(pdata.get("operators", {}).keys())
            player_counts[pid] = len(ops)
            five_players_ops.update(ops)

    # 2. Operators from manifests
    manifest_paths = sorted((ROOT / "data/manifests").glob("*.json"))
    manifest_ops: set[str] = set()
    manifest_names: dict[str, str] = {}
    for p in manifest_paths:
        try:
            with open(p, encoding="utf-8") as f:
                m = json.load(f)
            cid = m.get("operator_id")
            if cid:
                manifest_ops.add(cid)
                manifest_names[cid] = m.get("operator_name", cid)
        except Exception:
            pass

    # 3. Hero art (assets/operators/**/full.png)
    hero_arts: dict[str, Path] = {}
    hash_to_ops: dict[str, list[str]] = defaultdict(list)
    op_dirs = sorted((ROOT / "assets/operators").glob("*"))
    for op_dir in op_dirs:
        if not op_dir.is_dir():
            continue
        cid = op_dir.name
        full_png = op_dir / "full.png"
        if full_png.exists():
            hero_arts[cid] = full_png
            h = get_sha256(full_png)
            hash_to_ops[h].append(cid)

    # Detect duplicate hashes across distinct operators
    duplicates = {
        h: sorted(ops)
        for h, ops in hash_to_ops.items()
        if len(ops) > 1
    }

    manifest_missing_hero = sorted(manifest_ops - set(hero_arts.keys()))
    five_players_missing_hero = sorted(five_players_ops - set(hero_arts.keys()))

    return {
        "unique_operators_five_players": len(five_players_ops),
        "unique_operators_manifests": len(manifest_ops),
        "player_operator_counts": player_counts,
        "hero_art_count": len(hero_arts),
        "manifest_missing_hero_count": len(manifest_missing_hero),
        "manifest_missing_hero_operators": manifest_missing_hero,
        "five_players_missing_hero_count": len(five_players_missing_hero),
        "duplicate_hash_groups_count": len(duplicates),
        "duplicate_hash_groups": duplicates,
    }


def audit_cards_raw() -> dict:
    cards_pattern = ROOT / "data/raw/*/operbox/cards_raw/*.png"
    card_paths = sorted(Path(p) for p in glob.glob(str(cards_pattern)))

    per_player_counts: dict[str, int] = defaultdict(int)
    resolution_counts: Counter = Counter()
    aspect_ratios: list[float] = []

    for cp in card_paths:
        # parent directory structure: data/raw/<pid>/operbox/cards_raw/<file>
        parts = cp.parts
        try:
            raw_idx = parts.index("raw")
            pid = parts[raw_idx + 1]
            per_player_counts[pid] += 1
        except (ValueError, IndexError):
            per_player_counts["unknown"] += 1

        try:
            with Image.open(cp) as im:
                w, h = im.size
                resolution_counts[f"{w}x{h}"] += 1
                aspect_ratios.append(round(h / w, 4))
        except Exception as e:
            resolution_counts[f"corrupt ({e})"] += 1

    return {
        "total_cards_raw": len(card_paths),
        "per_player_card_counts": dict(per_player_counts),
        "resolution_distribution": dict(resolution_counts.most_common()),
        "aspect_ratio_min": min(aspect_ratios) if aspect_ratios else None,
        "aspect_ratio_max": max(aspect_ratios) if aspect_ratios else None,
    }


def audit_player_cards() -> dict:
    pc_dir = ROOT / "data/player_cards"
    found = {}
    candidates = ["P1", "P2", "P3", "P4", "P5"]
    if pc_dir.exists():
        for cand in candidates:
            matches = list(pc_dir.glob(f"{cand}.*"))
            if matches:
                p = matches[0]
                try:
                    with Image.open(p) as im:
                        size = f"{im.width}x{im.height}"
                except Exception:
                    size = "unreadable"
                found[cand] = {
                    "exists": True,
                    "filename": p.name,
                    "format": p.suffix.lower(),
                    "size_bytes": p.stat().st_size,
                    "resolution": size,
                }
            else:
                found[cand] = {
                    "exists": False,
                    "filename": None,
                    "format": None,
                    "size_bytes": 0,
                    "resolution": None,
                }
    return {
        "player_card_directory": "data/player_cards",
        "availability": found,
        "present_count": sum(1 for v in found.values() if v["exists"]),
        "missing_count": sum(1 for v in found.values() if not v["exists"]),
    }


def audit_pen_files() -> dict:
    def extract_urls(node, urls):
        if isinstance(node, dict):
            for k, v in node.items():
                if k == "url" and isinstance(v, str):
                    urls.append(v)
                elif isinstance(v, (dict, list)):
                    extract_urls(v, urls)
        elif isinstance(node, list):
            for item in node:
                extract_urls(item, urls)

    pen_results = {}
    pen_paths = sorted((ROOT / "psd2pen").glob("*.pen"))
    for pen_path in pen_paths:
        try:
            with open(pen_path, encoding="utf-8") as f:
                data = json.load(f)
            urls: list[str] = []
            extract_urls(data, urls)
            unique_urls = sorted(set(urls))
            pen_dir = pen_path.parent
            missing = []
            present = []
            for u in unique_urls:
                target = (pen_dir / u).resolve()
                if target.exists():
                    present.append(u)
                else:
                    missing.append(u)
            pen_results[pen_path.name] = {
                "total_references": len(urls),
                "unique_references": len(unique_urls),
                "present_count": len(present),
                "missing_count": len(missing),
                "missing_references": missing,
            }
        except Exception as e:
            pen_results[pen_path.name] = {"error": str(e)}

    return pen_results


def run_audit() -> dict:
    report = {
        "title": "arknightsclip Visual Asset Audit Baseline",
        "operators": audit_operators_and_hero_art(),
        "cards_raw": audit_cards_raw(),
        "player_cards": audit_player_cards(),
        "pen_assets": audit_pen_files(),
    }
    return report


def format_markdown(data: dict) -> str:
    ops = data["operators"]
    cards = data["cards_raw"]
    pc = data["player_cards"]
    pen = data["pen_assets"]

    lines = [
        "# arknightsclip 视觉资产审计报告 (Visual Asset Baseline Audit)",
        "",
        "## 1. 干员数据与立绘 (Operators & Hero Art)",
        f"- **五玩家总去重干员数**: {ops['unique_operators_five_players']}",
        f"- **SceneManifest 覆盖干员数 (6星主干)**: {ops['unique_operators_manifests']}",
        f"- **各玩家原始干员数**: {json.dumps(ops['player_operator_counts'])}",
        f"- **Hero Art (full.png) 现有目录数**: {ops['hero_art_count']}",
        f"- **Manifest 缺失 Hero Art 数量**: {ops['manifest_missing_hero_count']} (占比 {ops['manifest_missing_hero_count']/max(ops['unique_operators_manifests'],1)*100:.1f}%)",
        f"- **全量干员缺失 Hero Art 数量**: {ops['five_players_missing_hero_count']}",
        "",
        "### 重复立绘哈希 (Duplicate Hero Art Hashes)",
    ]

    if ops["duplicate_hash_groups"]:
        for h, cids in ops["duplicate_hash_groups"].items():
            lines.append(f"- **SHA-256 `{h[:16]}...`**: `{', '.join(cids)}`")
    else:
        lines.append("- 无重复立绘哈希。")

    lines.extend([
        "",
        "## 2. 原始卡片资产 (cards_raw)",
        f"- **总计 cards_raw 切片数**: {cards['total_cards_raw']}",
        f"- **各玩家切片数**: {json.dumps(cards['per_player_card_counts'])}",
        "- **分辨率分布**:",
    ])
    for res, cnt in cards["resolution_distribution"].items():
        lines.append(f"  - `{res}`: {cnt} 张")
    lines.append(f"- **宽高比范围 (H/W)**: {cards['aspect_ratio_min']} ~ {cards['aspect_ratio_max']} (基准比例约 2.03)")

    lines.extend([
        "",
        "## 3. 玩家资料卡 (player_cards)",
        f"- **现存可用**: {pc['present_count']} / 5",
        f"- **缺失玩家**: {pc['missing_count']} (具体详情如下)",
    ])
    for pid, info in pc["availability"].items():
        status = f"✓ {info['filename']} ({info['resolution']}, {info['format']})" if info["exists"] else "✗ MISSING"
        lines.append(f"- **{pid}**: {status}")

    lines.extend([
        "",
        "## 4. Pen 矢量设计工程依赖 (Pen Asset References)",
    ])
    for fname, pinfo in pen.items():
        if "error" in pinfo:
            lines.append(f"- **{fname}**: 错误 `{pinfo['error']}`")
            continue
        lines.append(f"- **{fname}**:")
        lines.append(f"  - 总引用数: {pinfo['total_references']} (去重 {pinfo['unique_references']})")
        lines.append(f"  - 本地存在: {pinfo['present_count']}")
        lines.append(f"  - 缺失引用: {pinfo['missing_count']}")
        if pinfo["missing_references"]:
            lines.append(f"  - 缺失文件类型示例: `{pinfo['missing_references'][:5]}` ... (共 {pinfo['missing_count']} 项)")

    return "\n".join(lines) + "\n"


def main():
    report_data = run_audit()

    reports_dir = ROOT / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)

    json_path = reports_dir / "visual_asset_audit.json"
    md_path = reports_dir / "visual_asset_audit.md"

    json_str = json.dumps(report_data, ensure_ascii=False, indent=2)
    json_path.write_text(json_str, encoding="utf-8")

    md_str = format_markdown(report_data)
    md_path.write_text(md_str, encoding="utf-8")

    print(f"[Audit] 审计完成！")
    print(f"  - 机器可读: {json_path}")
    print(f"  - 人类可读: {md_path}")
    print(f"  - 存在重复立绘哈希组: {report_data['operators']['duplicate_hash_groups_count']}")
    print(f"  - cards_raw 分辨率种数: {len(report_data['cards_raw']['resolution_distribution'])}")
    print(f"  - 缺失 player_card 数量: {report_data['player_cards']['missing_count']}")


if __name__ == "__main__":
    main()
