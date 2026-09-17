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

    def get_player_card_crop(self, char_id: str, player_id: str, edition: Optional[str] = None) -> Optional[Path]:
        """获取玩家由 OperBox 采集的特定干员卡片切片 (支持 edition='compact' (220px) | 'wide' (230px))"""
        player_dir = self.config.get_raw_player_dir(player_id) / "operbox"
        if edition in ("compact", "cards_compact"):
            p = player_dir / "cards_compact" / f"{char_id}.png"
            if p.exists():
                return p
        elif edition in ("wide", "cards_wide"):
            p = player_dir / "cards_wide" / f"{char_id}.png"
            if p.exists():
                return p
        p = player_dir / "cards_raw" / f"{char_id}.png"
        return p if p.exists() else None

    def get_player_card_provenance(self, char_id: str, player_id: str, edition: Optional[str] = None) -> Optional[Dict]:
        """获取玩家特定干员卡片切片的 Provenance 元数据 (优先从标准 card_metadata 读取)"""
        player_dir = self.config.get_raw_player_dir(player_id) / "operbox"
        if edition in ("compact", "cards_compact"):
            p = player_dir / "cards_compact" / f"{char_id}.json"
            if p.exists():
                return self._read_json(p)
        elif edition in ("wide", "cards_wide"):
            p = player_dir / "cards_wide" / f"{char_id}.json"
            if p.exists():
                return self._read_json(p)
        
        # 标准治理目录 card_metadata/
        meta_p = player_dir / "card_metadata" / f"{char_id}.json"
        if meta_p.exists():
            return self._read_json(meta_p)
        # 向下兼容历史路径 cards_raw/
        raw_p = player_dir / "cards_raw" / f"{char_id}.json"
        if raw_p.exists():
            return self._read_json(raw_p)
        return None

    def _read_json(self, p: Path) -> Optional[Dict]:
        try:
            with open(p, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None

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

    def sync_from_existing_sources(self) -> int:
        """从工程已有的素材源提取并固化至 assets/operators/<char_id>/ 目录"""
        import shutil
        generated_layered = self.config.resolve_path("generated/layered")

        synced_count = 0
        if generated_layered.exists():
            for s_dir in sorted(generated_layered.iterdir()):
                if not s_dir.is_dir():
                    continue
                # folder name like '001_能天使'
                parts = s_dir.name.split("_", 1)
                op_name = parts[1] if len(parts) == 2 else s_dir.name
                entry = self.registry.resolve(op_name)
                if not entry:
                    print(f"[AssetResolver] 未能识别素材目录: {s_dir.name}")
                    continue

                target_dir = self.get_operator_dir(entry.char_id)
                bg_path = s_dir / "background.png"
                if bg_path.exists() and not (target_dir / "full.png").exists():
                    shutil.copyfile(bg_path, target_dir / "full.png")

                meta_path = target_dir / "metadata.json"
                # 写入标准元数据
                with open(meta_path, "w", encoding="utf-8") as f:
                    json.dump({
                        "char_id": entry.char_id,
                        "canonical_name": entry.canonical_name_zh,
                        "rarity": entry.rarity,
                        "profession": entry.profession,
                    }, f, ensure_ascii=False, indent=2)
                synced_count += 1

        print(f"[AssetResolver] 已成功同步 {synced_count} 位干员母版素材至: {self.assets_root}")
        return synced_count
