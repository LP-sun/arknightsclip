"""
五人干员数据统计与团队深度分析器 (Group Stats Analyzer)
严格遵从规范计算：
1. 每人六星拥有数与拥有率
2. 五人联合图鉴率
3. 全员拥有角色 (Common Operators)
4. 五人全缺角色 (Missing Operators)
5. 单人独有角色 (Unique Operators)
6. 满潜 (潜六) 数量
7. 精二角色数量
8. 高等级 (Lv >= 80) 精二数量
9. 两两 Jaccard 图鉴相似度矩阵
10. 每人的独有覆盖贡献率 (Unique Coverage Contribution)
"""

import json
from pathlib import Path
from typing import Dict, List, Set, Any
from itertools import combinations
from ..models.player import FivePlayersDataset
from ..registry.operator_registry import OperatorRegistry

class GroupStatsAnalyzer:
    def __init__(self, registry: OperatorRegistry):
        self.registry = registry

    def analyze(self, dataset: FivePlayersDataset, target_rarity: int = 6) -> Dict[str, Any]:
        # 1. 获取目标稀有度全集
        all_target_ops = [
            e for e in self.registry.all_operators() if e.rarity == target_rarity
        ]
        total_target_count = len(all_target_ops)
        all_target_ids: Set[str] = {e.char_id for e in all_target_ops}

        # 2. 玩家拥有集合
        player_owned_map: Dict[str, Set[str]] = {}
        per_player_metrics: Dict[str, Dict[str, Any]] = {}

        for pid, pdata in dataset.players.items():
            owned_ids = {cid for cid, op in pdata.operators.items() if op.own and cid in all_target_ids}
            player_owned_map[pid] = owned_ids

            pot6_count = sum(1 for op in pdata.operators.values() if op.own and op.potential == 6 and op.char_id in all_target_ids)
            e2_count = sum(1 for op in pdata.operators.values() if op.own and op.elite == 2 and op.char_id in all_target_ids)
            high_lvl_count = sum(1 for op in pdata.operators.values() if op.own and op.elite == 2 and op.level >= 80 and op.char_id in all_target_ids)

            per_player_metrics[pid] = {
                "display_name": pdata.profile.display_name,
                "owned_count": len(owned_ids),
                "coverage_rate": round(len(owned_ids) / total_target_count if total_target_count else 0.0, 4),
                "potential_6_count": pot6_count,
                "elite_2_count": e2_count,
                "high_level_e2_count": high_lvl_count,
            }

        # 3. 联合图鉴
        union_owned: Set[str] = set()
        for s in player_owned_map.values():
            union_owned.update(s)
        union_count = len(union_owned)
        union_coverage = round(union_count / total_target_count if total_target_count else 0.0, 4)

        # 4. 全员拥有角色 (交集)
        if player_owned_map:
            common_owned = set.intersection(*player_owned_map.values())
        else:
            common_owned = set()

        # 5. 全员全缺角色
        missing_all = all_target_ids - union_owned

        # 6. 单人独有角色与独有覆盖贡献
        unique_owned: Dict[str, List[str]] = {}
        unique_contribution: Dict[str, int] = {}
        for pid, my_set in player_owned_map.items():
            other_union = set()
            for other_pid, other_set in player_owned_map.items():
                if other_pid != pid:
                    other_union.update(other_set)
            solo = my_set - other_union
            unique_owned[pid] = sorted(list(solo))
            unique_contribution[pid] = len(solo)
            per_player_metrics[pid]["unique_count"] = len(solo)
            per_player_metrics[pid]["unique_contribution_rate"] = round(len(solo) / union_count if union_count else 0.0, 4)

        # 7. 两两 Jaccard 相似度矩阵
        jaccard_matrix: Dict[str, Dict[str, float]] = {}
        p_keys = list(dataset.players.keys())
        for p1 in p_keys:
            jaccard_matrix[p1] = {}
            for p2 in p_keys:
                s1, s2 = player_owned_map[p1], player_owned_map[p2]
                if not s1 and not s2:
                    sim = 1.0
                else:
                    sim = len(s1 & s2) / len(s1 | s2)
                jaccard_matrix[p1][p2] = round(sim, 4)

        return {
            "target_rarity": target_rarity,
            "total_target_operators": total_target_count,
            "union_owned_count": union_count,
            "union_coverage_rate": union_coverage,
            "common_owned_count": len(common_owned),
            "common_owned_operators": [self._get_name(cid) for cid in sorted(list(common_owned))],
            "missing_all_count": len(missing_all),
            "missing_all_operators": [self._get_name(cid) for cid in sorted(list(missing_all))],
            "per_player": per_player_metrics,
            "unique_owned_by_player": {pid: [self._get_name(cid) for cid in ops] for pid, ops in unique_owned.items()},
            "jaccard_similarity": jaccard_matrix,
        }

    def _get_name(self, char_id: str) -> str:
        entry = self.registry.get_by_id(char_id)
        return entry.canonical_name_zh if entry else char_id

    def export_reports(self, stats: Dict[str, Any], json_path: Path, md_path: Path):
        json_path.parent.mkdir(parents=True, exist_ok=True)
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)

        # 生成专业 Markdown 报告
        lines = [
            "# 明日方舟报菜名 · 五名玩家团队练度深度审计报告",
            "",
            f"- **统计目标**：{stats['target_rarity']} 星干员",
            f"- **全量六星总数**：{stats['total_target_operators']} 位",
            f"- **五人联合图鉴**：**{stats['union_owned_count']}** 位 (联合图鉴率: **{stats['union_coverage_rate']*100:.1f}%**)",
            f"- **全员拥有干员**：**{stats['common_owned_count']}** 位",
            f"- **五人全缺干员**：**{stats['missing_all_count']}** 位",
            "",
            "## 1. 玩家个人核心数据概览",
            "",
            "| 玩家标识 | 博士名称 | 六星拥有数 | 图鉴率 | 精二数量 | 高练精二(≥80级) | 满潜数量 | 独有干员贡献 |",
            "| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |",
        ]
        for pid, p in stats["per_player"].items():
            lines.append(
                f"| **{pid}** | {p['display_name']} | {p['owned_count']} | {p['coverage_rate']*100:.1f}% | "
                f"{p['elite_2_count']} | {p['high_level_e2_count']} | {p['potential_6_count']} | {p.get('unique_count', 0)} 位 ({p.get('unique_contribution_rate', 0)*100:.1f}%) |"
            )

        lines.extend([
            "",
            "## 2. 两两 Jaccard 图鉴相似度矩阵",
            "",
        ])
        p_list = list(stats["per_player"].keys())
        header = "| 相似度 | " + " | ".join(p_list) + " |"
        sep = "| :--- | " + " | ".join([":---:" for _ in p_list]) + " |"
        lines.extend([header, sep])
        for p1 in p_list:
            row = [f"**{p1}**"]
            for p2 in p_list:
                sim = stats["jaccard_similarity"].get(p1, {}).get(p2, 0.0)
                row.append(f"{sim*100:.1f}%")
            lines.append("| " + " | ".join(row) + " |")

        if stats["missing_all_count"] > 0:
            lines.extend([
                "",
                "## 3. 五人共同缺失干员清单",
                "",
                ", ".join(stats["missing_all_operators"][:30]) + ("..." if stats["missing_all_count"] > 30 else ""),
            ])

        with open(md_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
        print(f"[GroupStatsAnalyzer] 报告已输出: {json_path} & {md_path}")
