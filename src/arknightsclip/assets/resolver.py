"""
干员资产解析与校验器 (Asset Resolver)
以 char_id 为唯一定位键，管理 full art、portrait、avatar 等素材缓存与完整性校验。
严禁缺素材时私自 fallback 到能天使。
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Optional
from ..config import ProjectConfig
from ..registry.operator_registry import OperatorRegistry

class AssetResolver:
    def __init__(self, config: ProjectConfig, registry: Optional[OperatorRegistry] = None):
        self.config = config
        self.registry = registry or OperatorRegistry(
            config.resolve_path("src/arknightsclip/registry/operator_registry.json")
        )
        self.assets_root = config.resolve_path(config.pipeline.assets_dir) / "operators"
        self.assets_root.mkdir(parents=True, exist_ok=True)

    def get_operator_dir(self, char_id: str) -> Path:
        p = self.assets_root / char_id
        p.mkdir(parents=True, exist_ok=True)
        return p

    def get_full_art(self, char_id: str) -> Optional[Path]:
        p = self.assets_root / char_id / "full.png"
        return p if p.exists() else None

    def get_portrait(self, char_id: str) -> Optional[Path]:
        p = self.assets_root / char_id / "portrait.png"
        return p if p.exists() else None

    def get_avatar(self, char_id: str) -> Optional[Path]:
        p = self.assets_root / char_id / "avatar.png"
        return p if p.exists() else None

    def has_assets(self, char_id: str) -> bool:
        return self.get_full_art(char_id) is not None

    def validate_assets(self, target_char_ids: List[str]) -> List[str]:
        """校验目标干员集合是否全部具备立绘素材，返回缺失列表"""
        missing = []
        for cid in target_char_ids:
            if not self.has_assets(cid):
                entry = self.registry.get_by_id(cid)
                name = entry.canonical_name_zh if entry else cid
                missing.append(f"{cid} ({name})")
        return missing

    def sync_from_existing_sources(self):
        """从工程已有的素材源提取并固化至 assets/operators/<char_id>/ 目录"""
        psd_backup_dir = self.config.resolve_path("psd模板/全6星干员备份文件（较大）")
        generated_layered = self.config.resolve_path("generated/layered")

        # 1. 扫描 59 个已有的 layered 成果
        if generated_layered.exists():
            for s_dir in generated_layered.iterdir():
                if not s_dir.is_dir():
                    continue
                # folder name like '001_能天使'
                parts = s_dir.name.split("_", 1)
                op_name = parts[1] if len(parts) == 2 else s_dir.name
                entry = self.registry.resolve(op_name)
                if not entry:
                    continue

                target_dir = self.get_operator_dir(entry.char_id)
                bg_path = s_dir / "background.png"
                if bg_path.exists() and not (target_dir / "full.png").exists():
                    import shutil
                    shutil.copyfile(bg_path, target_dir / "full.png")

                meta_path = target_dir / "metadata.json"
                if not meta_path.exists():
                    with open(meta_path, "w", encoding="utf-8") as f:
                        json.dump({
                            "char_id": entry.char_id,
                            "canonical_name": entry.canonical_name_zh,
                            "rarity": entry.rarity,
                            "profession": entry.profession,
                        }, f, ensure_ascii=False, indent=2)
