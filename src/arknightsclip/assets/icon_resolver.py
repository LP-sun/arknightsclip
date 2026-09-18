"""
Status Icon Resolver (状态图标解析与安全策略)
优先提供矢量 SVG 与高分辨率素材；
当降级至历史 MAA 或低清切片时，强制限制安全显示尺寸，防止 nearest-neighbor 放大导致像素马赛克。
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from ..config import ProjectConfig, load_config


@dataclass
class ResolvedIcon:
    name: str
    path: Path
    format: str  # "svg" | "png" | "jpg"
    is_vector: bool
    max_safe_display_size: Optional[int]  # None 表示矢量无限制，整型表示低清栅格最大安全显示像素


class StatusIconResolver:
    def __init__(self, config: Optional[ProjectConfig] = None):
        self.config = config or load_config()
        self.root = self.config.project_root
        self.svg_dir = self.root / "assets/icons/svg"
        self.raster_psd_dir = self.root / "psd2pen/assets/psd_sources"
        self.maa_dir = self.root / "external/MaaAssistantArknights/resource/template/Battle/Formation"

    def resolve_elite_icon(self, elite_level: int) -> ResolvedIcon:
        """解析精英阶段图标 (优先 SVG -> 降级至 psd_sources/elite{level}.png)"""
        svg_path = self.svg_dir / f"elite_{elite_level}.svg"
        if svg_path.exists():
            return ResolvedIcon(
                name=f"elite_{elite_level}",
                path=svg_path,
                format="svg",
                is_vector=True,
                max_safe_display_size=None,
            )

        raster_path = self.raster_psd_dir / f"elite{elite_level}.png"
        if raster_path.exists():
            return ResolvedIcon(
                name=f"elite_{elite_level}",
                path=raster_path,
                format="png",
                is_vector=False,
                max_safe_display_size=64,
            )

        # 最终兜底
        return ResolvedIcon(
            name=f"elite_{elite_level}",
            path=svg_path,
            format="svg",
            is_vector=True,
            max_safe_display_size=None,
        )

    def resolve_potential_icon(self, potential_level: int) -> ResolvedIcon:
        """解析潜能等级图标 (优先 SVG -> 降级至 psd_sources/potential{level}.png)"""
        svg_path = self.svg_dir / f"potential_{potential_level}.svg"
        if svg_path.exists():
            return ResolvedIcon(
                name=f"potential_{potential_level}",
                path=svg_path,
                format="svg",
                is_vector=True,
                max_safe_display_size=None,
            )

        raster_path = self.raster_psd_dir / f"potential{potential_level}.png"
        if raster_path.exists():
            return ResolvedIcon(
                name=f"potential_{potential_level}",
                path=raster_path,
                format="png",
                is_vector=False,
                max_safe_display_size=48,
            )

        return ResolvedIcon(
            name=f"potential_{potential_level}",
            path=svg_path,
            format="svg",
            is_vector=True,
            max_safe_display_size=None,
        )

    def resolve_profession_icon(self, profession: str) -> ResolvedIcon:
        """解析职业图标 (优先 SVG)"""
        clean_prof = profession.lower().strip()
        alias_map = {
            "pioneer": "pioneer", "vanguard": "pioneer", "先锋": "pioneer",
            "warrior": "warrior", "guard": "warrior", "近卫": "warrior",
            "sniper": "sniper", "狙击": "sniper",
            "tank": "tank", "defender": "tank", "重装": "tank",
            "medic": "medic", "医疗": "medic",
            "support": "support", "supporter": "support", "辅助": "support",
            "caster": "caster", "术师": "caster", "法师": "caster",
            "special": "special", "specialist": "special", "特种": "special",
        }
        canonical = alias_map.get(clean_prof, "warrior")
        svg_path = self.svg_dir / f"profession_{canonical}.svg"

        return ResolvedIcon(
            name=f"profession_{canonical}",
            path=svg_path,
            format="svg",
            is_vector=True,
            max_safe_display_size=None,
        )
