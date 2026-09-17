"""
场景渲染清单构建器 (SceneManifest Builder)
负责将全局唯一事实源 FivePlayersDataset 结合 OperatorRegistry 与 AssetResolver，
自动为各个干员构建规范的 SceneManifest 渲染清单并持久化至 data/manifests/<char_id>.json。
"""

import json
from pathlib import Path
from typing import Dict, List, Optional
from ..config import ProjectConfig, load_config
from ..models.player import FivePlayersDataset
from ..models.scene import SceneManifest, PlayerSlotState
from ..registry.operator_registry import OperatorRegistry
from ..assets.resolver import AssetResolver

class SceneBuilder:
    def __init__(
        self,
        config: Optional[ProjectConfig] = None,
        dataset: Optional[FivePlayersDataset] = None,
        registry: Optional[OperatorRegistry] = None,
        asset_resolver: Optional[AssetResolver] = None,
    ):
        self.config = config or load_config()
        self.registry = registry or OperatorRegistry(
            self.config.resolve_path("src/arknightsclip/registry/operator_registry.json")
        )
        self.asset_resolver = asset_resolver or AssetResolver(self.config, self.registry)
        self.dataset = dataset

    def load_dataset_from_file(self, dataset_path: Optional[Path] = None) -> FivePlayersDataset:
        target = dataset_path or (self.config.get_normalized_dir() / "five_players.json")
        if not target.exists():
            raise FileNotFoundError(f"数据集文件不存在: {target}，请先执行 dataset_manager.merge_players()")
        with open(target, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.dataset = FivePlayersDataset.from_dict(data)
        return self.dataset

    def build_scene(self, char_id: str) -> SceneManifest:
        """为特定干员构建 5 位玩家槽位渲染清单"""
        if self.dataset is None:
            self.load_dataset_from_file()

        entry = self.registry.get_by_id(char_id) or self.registry.resolve(char_id)
        if entry:
            resolved_cid = entry.char_id
            name = entry.canonical_name_zh
            rarity = entry.rarity
            profession = entry.profession
        else:
            resolved_cid = char_id
            name = char_id
            rarity = 6
            profession = ""

        # 获取中央大立绘
        full_art = self.asset_resolver.get_full_art(resolved_cid)
        full_art_str = str(full_art) if full_art else ""

        # 组装 5 位玩家槽位状态
        slots: Dict[str, PlayerSlotState] = {}
        player_ids = [p.id for p in self.config.players] or ["P1", "P2", "P3", "P4", "P5"]

        for pid in player_ids:
            p_data = self.dataset.players.get(pid)
            op_state = p_data.operators.get(resolved_cid) if p_data else None

            if op_state and op_state.own:
                # 尝试获取该玩家由 OperBox 采集的切片素材
                crop_path = self.asset_resolver.get_player_card_crop(resolved_cid, pid)
                crop_str = str(crop_path) if crop_path else None
                slots[pid] = PlayerSlotState(
                    own=True,
                    elite=op_state.elite,
                    level=op_state.level,
                    potential=op_state.potential,
                    no_info=False,
                    card_asset_path=crop_str,
                )
            else:
                # 未拥有或缺席
                slots[pid] = PlayerSlotState(
                    own=False,
                    elite=0,
                    level=1,
                    potential=1,
                    no_info=True,
                    card_asset_path=None,
                )

        manifest = SceneManifest(
            operator_id=resolved_cid,
            operator_name=name,
            rarity=rarity,
            profession=profession,
            full_art_path=full_art_str,
            players=slots,
        )

        # 契约完整性校验
        assert manifest.validate(), f"构建出的 SceneManifest 校验未通过: {resolved_cid}"
        return manifest

    def build_all_scenes(
        self,
        target_char_ids: Optional[List[str]] = None,
        save_dir: Optional[Path] = None,
        rarity: Optional[int] = 6,
    ) -> Dict[str, SceneManifest]:
        """批量构建并持久化场景清单，默认严格过滤为 6 星干员 (rarity=6)"""
        if self.dataset is None:
            self.load_dataset_from_file()

        if target_char_ids is None:
            # 优先从 registry 中提取满足稀有度的干员 (默认 6 星)
            if rarity is not None:
                target_char_ids = sorted([e.char_id for e in self.registry.all_operators() if e.rarity == rarity])
            else:
                cids_set = set()
                for p in self.dataset.players.values():
                    cids_set.update(p.operators.keys())
                target_char_ids = sorted(list(cids_set))

        out_dir = save_dir or self.config.get_manifests_dir()
        out_dir.mkdir(parents=True, exist_ok=True)

        manifests: Dict[str, SceneManifest] = {}
        for cid in target_char_ids:
            manifest = self.build_scene(cid)
            if rarity is not None and manifest.rarity != rarity:
                continue
            manifests[cid] = manifest

            # 落盘
            out_file = out_dir / f"{cid}.json"
            with open(out_file, "w", encoding="utf-8") as f:
                json.dump(manifest.to_dict(), f, ensure_ascii=False, indent=2)

        print(f"[SceneBuilder] 成功构建并保存 {len(manifests)} 份 {f'{rarity}星' if rarity else '全量'} SceneManifest 至: {out_dir}")
        return manifests
