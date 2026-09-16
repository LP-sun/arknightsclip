"""
五人玩家数据集管理器 (Dataset Manager)
负责读取各玩家独立的原始数据并合并规范化为全局唯一事实源: data/normalized/five_players.json
"""

import json
from pathlib import Path
from typing import Dict, List, Optional
from ..config import ProjectConfig
from ..models.player import PlayerProfile, PlayerDataSet, FivePlayersDataset
from ..models.operator import OperatorState
from ..registry.operator_registry import OperatorRegistry

class DatasetManager:
    def __init__(self, config: ProjectConfig, registry: Optional[OperatorRegistry] = None):
        self.config = config
        self.registry = registry or OperatorRegistry(
            config.resolve_path("src/arknightsclip/registry/operator_registry.json")
        )

    def merge_players(self, player_ids: Optional[List[str]] = None) -> FivePlayersDataset:
        """合并各玩家的 raw 数据，严格以 char_id 为主键聚合"""
        if not player_ids:
            player_ids = [p.id for p in self.config.players] or ["P1", "P2", "P3", "P4", "P5"]

        merged_players: Dict[str, PlayerDataSet] = {}
        for pid in player_ids:
            p_dir = self.config.get_raw_player_dir(pid)
            prof_file = p_dir / "profile.json"
            ops_file = p_dir / "operators.json"

            # 读取静态 Profile (优先配置中的静态资料)
            cfg_profile = next((p for p in self.config.players if p.id == pid), None)
            display_name = cfg_profile.display_name if cfg_profile else f"博士_{pid}"
            doctor_level = cfg_profile.doctor_level if cfg_profile else 120
            avatar = cfg_profile.avatar if cfg_profile else ""

            if prof_file.exists():
                with open(prof_file, "r", encoding="utf-8") as f:
                    raw_prof = json.load(f)
                    display_name = raw_prof.get("display_name", display_name)
                    doctor_level = raw_prof.get("doctor_level", doctor_level)

            profile = PlayerProfile(
                id=pid,
                display_name=display_name,
                doctor_level=doctor_level,
                avatar=avatar,
            )

            # 读取干员清单
            operators: Dict[str, OperatorState] = {}
            if ops_file.exists():
                with open(ops_file, "r", encoding="utf-8") as f:
                    raw_list = json.load(f)
                for item in raw_list:
                    op = OperatorState.from_dict(item)
                    # 经过 Registry 规整标准 char_id
                    reg_entry = self.registry.resolve(op.char_id) or self.registry.resolve(op.name)
                    if reg_entry:
                        op.char_id = reg_entry.char_id
                        op.name = reg_entry.canonical_name_zh
                        op.rarity = reg_entry.rarity
                    operators[op.char_id] = op

            merged_players[pid] = PlayerDataSet(
                player_id=pid,
                profile=profile,
                operators=operators,
            )

        dataset = FivePlayersDataset(
            players=merged_players,
            metadata={
                "version": "2.0",
                "player_count": len(merged_players),
                "players_included": player_ids,
            },
        )

        # 持久化至 data/normalized/five_players.json
        out_file = self.config.get_normalized_dir() / "five_players.json"
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(dataset.to_dict(), f, ensure_ascii=False, indent=2)

        print(f"[DatasetManager] 成功合并 {len(merged_players)} 名玩家数据至唯一事实源: {out_file}")
        return dataset

    def export_excel_for_inspection(self, dataset: FivePlayersDataset, output_path: Path):
        """将数据集导出为 Excel (仅作为人类可读的审查视图，严禁反向充当系统事实源)"""
        import openpyxl

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "FivePlayers_Inspection"

        # 获取涉及的所有干员
        all_cids = set()
        for p in dataset.players.values():
            all_cids.update(p.operators.keys())

        # 按 Registry 顺序排序
        sorted_cids = sorted(list(all_cids))

        # 表头
        ws.cell(row=1, column=1, value="属性")
        ws.cell(row=1, column=2, value="玩家ID / 姓名")
        for col_idx, cid in enumerate(sorted_cids, start=3):
            entry = self.registry.get_by_id(cid)
            name = entry.canonical_name_zh if entry else cid
            ws.cell(row=1, column=col_idx, value=cid)
            ws.cell(row=2, column=col_idx, value=name)

        # 写入数据
        row_curr = 3
        for prop, title in [("elite", "精英化"), ("level", "等级"), ("potential", "潜能")]:
            ws.cell(row=row_curr, column=1, value=title)
            for p_idx, (pid, pdata) in enumerate(dataset.players.items(), start=1):
                ws.cell(row=row_curr, column=2, value=f"{pid} - {pdata.profile.display_name}")
                for col_idx, cid in enumerate(sorted_cids, start=3):
                    op = pdata.operators.get(cid)
                    val = getattr(op, prop) if (op and op.own) else "-"
                    ws.cell(row=row_curr, column=col_idx, value=val)
                row_curr += 1
            row_curr += 1

        output_path.parent.mkdir(parents=True, exist_ok=True)
        wb.save(output_path)
        print(f"[DatasetManager] 人工审查 Excel 已导出至: {output_path}")
