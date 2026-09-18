"""
Rhine 场景渲染状态求值器 (Render State Evaluator)
为任意干员确定性求值渲染模式 (hero_art / card_art / metadata_only)，
实现一等公民级别的素材缺失降级 (first-class fallback)，绝不静默冒用其他干员素材。
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Any, Optional, List

from ..config import ProjectConfig, load_config
from ..registry.operator_registry import OperatorRegistry
from ..assets.resolver import AssetResolver


@dataclass
class OperatorRenderState:
    operator_id: str
    operator_name: str
    render_mode: str  # "hero_art" | "card_art" | "metadata_only"
    hero_art_path: Optional[str] = None
    card_art_path: Optional[str] = None
    rarity: int = 6
    profession: str = ""
    is_fallback: bool = False
    fallback_reason: Optional[str] = None
    players: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    def validate(self) -> bool:
        if not self.operator_id or not self.operator_name:
            return False
        if self.render_mode not in ("hero_art", "card_art", "metadata_only"):
            return False
        if self.render_mode == "hero_art" and not self.hero_art_path:
            return False
        if self.render_mode == "card_art" and not self.card_art_path:
            return False
        return True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "operator_id": self.operator_id,
            "operator_name": self.operator_name,
            "render_mode": self.render_mode,
            "hero_art_path": self.hero_art_path,
            "card_art_path": self.card_art_path,
            "rarity": self.rarity,
            "profession": self.profession,
            "is_fallback": self.is_fallback,
            "fallback_reason": self.fallback_reason,
            "players": self.players,
        }


class RhineRenderStateEvaluator:
    def __init__(
        self,
        config: Optional[ProjectConfig] = None,
        registry: Optional[OperatorRegistry] = None,
        asset_resolver: Optional[AssetResolver] = None,
    ):
        self.config = config or load_config()
        self.registry = registry or OperatorRegistry(
            self.config.resolve_path("src/arknightsclip/registry/operator_registry.json")
        )
        self.asset_resolver = asset_resolver or AssetResolver(self.config, self.registry)
        self.root = self.config.project_root

    def evaluate_operator(
        self,
        operator_id: str,
        player_data: Optional[Dict[str, Any]] = None,
    ) -> OperatorRenderState:
        """
        对单个干员求值渲染状态：
        1. 优先检查真实的 hero art (full.png)
        2. 若缺失，降级至卡片切片 (card_art)
        3. 若仍缺失，降级至纯元数据 (metadata_only)
        绝不调用或伪装成能天使等其他干员的图。
        """
        entry = self.registry.get_by_id(operator_id) or self.registry.resolve(operator_id)
        cid = entry.char_id if entry else operator_id
        name = entry.canonical_name_zh if entry else operator_id
        rarity = entry.rarity if entry else 6
        profession = entry.profession if entry else "OPERATOR"

        # 1. 检查 Hero Art
        hero_art_path = self.asset_resolver.get_full_art(cid)
        hero_art_valid = False
        hero_art_str: Optional[str] = None
        if hero_art_path and hero_art_path.exists() and hero_art_path.stat().st_size > 0:
            hero_art_valid = True
            try:
                hero_art_str = str(hero_art_path.relative_to(self.root)).replace("\\", "/")
            except ValueError:
                hero_art_str = str(hero_art_path).replace("\\", "/")

        # 2. 检查 Card Art (从任意拥有该干员的玩家切片中提取)
        card_art_path: Optional[str] = None
        player_slots: Dict[str, Dict[str, Any]] = {}

        player_ids = ["P1", "P2", "P3", "P4", "P5"]
        for pid in player_ids:
            p_dict = (player_data or {}).get(pid, {})
            # 兼容两种结构：直接是 op_state，或整个 player_info 下的 operators dict
            op_dict = p_dict.get("operators", {}).get(cid) if "operators" in p_dict else p_dict
            own = bool(op_dict.get("own", False))
            elite = op_dict.get("elite", 0) if own else 0
            level = op_dict.get("level", 1) if own else 1
            potential = op_dict.get("potential", 1) if own else 1

            slot_card = None
            if own:
                crop = self.asset_resolver.get_player_card_crop(cid, pid)
                if crop and crop.exists():
                    try:
                        slot_card = str(crop.relative_to(self.root)).replace("\\", "/")
                    except ValueError:
                        slot_card = str(crop).replace("\\", "/")
                    if card_art_path is None:
                        card_art_path = slot_card

            player_slots[pid] = {
                "own": own,
                "elite": elite,
                "level": level,
                "potential": potential,
                "card_asset_path": slot_card,
            }

        # 3. 决定渲染模式
        if hero_art_valid and hero_art_str:
            return OperatorRenderState(
                operator_id=cid,
                operator_name=name,
                render_mode="hero_art",
                hero_art_path=hero_art_str,
                card_art_path=card_art_path,
                rarity=rarity,
                profession=profession,
                is_fallback=False,
                fallback_reason=None,
                players=player_slots,
            )
        elif card_art_path:
            return OperatorRenderState(
                operator_id=cid,
                operator_name=name,
                render_mode="card_art",
                hero_art_path=None,
                card_art_path=card_art_path,
                rarity=rarity,
                profession=profession,
                is_fallback=True,
                fallback_reason="Hero art not present; fallen back to OperBox card specimen",
                players=player_slots,
            )
        else:
            return OperatorRenderState(
                operator_id=cid,
                operator_name=name,
                render_mode="metadata_only",
                hero_art_path=None,
                card_art_path=None,
                rarity=rarity,
                profession=profession,
                is_fallback=True,
                fallback_reason="Neither hero art nor card art available; rendered via telemetry metadata",
                players=player_slots,
            )

    def evaluate_all_from_five_players(
        self,
        five_players_path: Optional[Path] = None,
    ) -> Dict[str, OperatorRenderState]:
        """遍历 five_players.json 中所有干员，确认全部能安全生成合法状态且不崩溃"""
        p = five_players_path or (self.config.get_normalized_dir() / "five_players.json")
        with open(p, "r", encoding="utf-8") as f:
            data = json.load(f)

        all_cids = set()
        players_data = data.get("players", {})
        for pdata in players_data.values():
            all_cids.update(pdata.get("operators", {}).keys())

        states: Dict[str, OperatorRenderState] = {}
        for cid in sorted(all_cids):
            # 组装各玩家对该干员的数据
            per_player = {
                pid: pinfo.get("operators", {}).get(cid, {})
                for pid, pinfo in players_data.items()
            }
            state = self.evaluate_operator(cid, per_player)
            assert state.validate(), f"Render state failed validation for {cid}"
            states[cid] = state

        return states
