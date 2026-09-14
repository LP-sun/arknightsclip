"""
基于 psd-tools 与 PIL 的跨平台无头分层渲染引擎 (PSDToolsRenderer)
支持根据 SceneManifest 动态修改各玩家槽位的等级、精英度显隐、潜能显隐与 NO INFO 状态。
"""

import os
import numpy as np
from pathlib import Path
from typing import Dict, Optional, Any
from psd_tools import PSDImage
from PIL import Image, ImageDraw, ImageFont
from .renderer import PhotoshopRenderer
from ..models.scene import SceneManifest, PlayerSlotState
from ..config import ProjectConfig

class PSDToolsRenderer(PhotoshopRenderer):
    def __init__(self, config: ProjectConfig, template_path: Optional[Path] = None):
        self.config = config
        self.template_path = template_path or config.resolve_path(config.photoshop.master_template)
        if not self.template_path.exists():
            # 兼容使用已有的模板
            alt = config.resolve_path("psd模板/只需要模板/能天使.psd")
            if alt.exists():
                self.template_path = alt

    def render_scene(self, manifest: SceneManifest, output_dir: Path) -> Dict[str, Path]:
        output_dir.mkdir(parents=True, exist_ok=True)
        psd = PSDImage.open(str(self.template_path))

        card_group = psd[2]
        pot_group = psd[3]
        elite_group = psd[4]
        lvl_group = psd[5]

        # 针对 5 名玩家映射到前 5 个槽位
        player_keys = ["P1", "P2", "P3", "P4", "P5"]
        slots_to_apply = {}
        for idx, p_key in enumerate(player_keys, start=1):
            if p_key in manifest.players:
                slots_to_apply[idx] = manifest.players[p_key]
            else:
                # 默认未拥有
                slots_to_apply[idx] = PlayerSlotState(own=False, no_info=True)

        # 槽位 6, 7, 8 设为隐藏或 NO INFO
        for idx in range(6, 9):
            slots_to_apply[idx] = PlayerSlotState(own=False, no_info=True)

        level_text_draws = []

        # 动态应用槽位状态
        for slot_idx, state in slots_to_apply.items():
            self._apply_slot_state(
                slot_idx, state, card_group, pot_group, elite_group, lvl_group, level_text_draws
            )

        # 渲染 Composite
        comp = psd.composite().convert('RGBA')

        # 绘制动态等级文本
        draw = ImageDraw.Draw(comp)
        try:
            font = ImageFont.truetype("arial.ttf", 36)
        except Exception:
            font = ImageFont.load_default()

        for (bbox, text) in level_text_draws:
            draw.text((bbox[0], bbox[1] - 5), text, fill=(255, 255, 255, 255), font=font)

        # 拆分为三层规范素材 (遵从 Phase 1 验收标准)
        bg_path = output_dir / "background.png"
        cards_path = output_dir / "character_cards.png"
        doc_path = output_dir / "doctor_info.png"

        # 1. Background (Layer 0 + Layer 1)
        bg = Image.new('RGB', (1920, 1080), (0, 0, 0))
        if len(psd) > 0 and psd[0].topil():
            bg.paste(psd[0].topil(), (max(0, psd[0].bbox[0]), max(0, psd[0].bbox[1])))
        if len(psd) > 1 and psd[1].topil():
            l1 = psd[1].topil()
            bg.paste(l1, (psd[1].bbox[0], psd[1].bbox[1]), l1 if l1.mode == 'RGBA' else None)
        bg.save(bg_path, format='PNG')

        arr_full = np.array(comp)
        arr_bg = np.array(bg.convert('RGBA'))
        diff = np.max(np.abs(arr_full[:, :, :3].astype(np.int32) - arr_bg[:, :, :3].astype(np.int32)), axis=2)
        fg_mask = (diff > 4).astype(np.uint8) * 255

        # 2. Doctor Info (x <= 165 or x >= 1755)
        doc_mask = np.zeros((1080, 1920), dtype=np.uint8)
        doc_mask[:, :165] = fg_mask[:, :165]
        doc_mask[:, 1755:] = fg_mask[:, 1755:]
        doc_arr = arr_full.copy()
        doc_arr[:, :, 3] = doc_mask
        Image.fromarray(doc_arr, 'RGBA').save(doc_path, format='PNG')

        # 3. Character Cards (165 < x < 1755, 中间透空)
        cards_mask = np.zeros((1080, 1920), dtype=np.uint8)
        cards_mask[:, 165:1755] = fg_mask[:, 165:1755]
        cards_arr = arr_full.copy()
        cards_arr[:, :, 3] = cards_mask
        Image.fromarray(cards_arr, 'RGBA').save(cards_path, format='PNG')

        return {
            "background": bg_path,
            "character_cards": cards_path,
            "doctor_info": doc_path,
        }

    def _apply_slot_state(
        self,
        slot: int,
        state: PlayerSlotState,
        card_group: Any,
        pot_group: Any,
        elite_group: Any,
        lvl_group: Any,
        level_text_draws: list,
    ):
        # 槽位在能天使母版中的索引基数 (Slot 1..8)
        # 精英: 每个 slot 4 个 layer ([0]=base, [1]=精0, [2]=精一, [3]=精二)
        e_base = (slot - 1) * 4
        # 潜能: 每个 slot 7 个 layer ([0]=base, [1..6]=潜1..6)
        p_base = (slot - 1) * 7
        # 等级: 每个 slot 3 个 layer ([0]=base, [1]=text, [2]=LV)
        l_base = (slot - 1) * 3

        if state.own:
            # 1. 精英化: 互斥只显一个
            elite_group[e_base].visible = True
            elite_group[e_base + 1].visible = (state.elite == 0)
            elite_group[e_base + 2].visible = (state.elite == 1)
            elite_group[e_base + 3].visible = (state.elite == 2)

            # 2. 潜能: 互斥只显一个
            pot_group[p_base].visible = True
            for p_num in range(1, 7):
                pot_group[p_base + p_num].visible = (state.potential == p_num)

            # 3. 等级: 隐藏原文本并记录新绘制
            lvl_group[l_base].visible = True
            lvl_group[l_base + 1].visible = False # 隐藏原有静态文字
            lvl_group[l_base + 2].visible = True
            level_text_draws.append((lvl_group[l_base + 1].bbox, str(state.level)))

            # 4. 卡面: 卡面显，NO INFO 隐
            # 找到对应卡面和 NO INFO
            c_idx = (slot - 1) * 3 if slot > 1 else 0
            # 安全查找 NO INFO
            for layer in card_group:
                if "NO INFO" in layer.name and abs(layer.bbox[1] - lvl_group[l_base].bbox[1]) < 150:
                    layer.visible = False
        else:
            # 未拥有: 全部隐藏，显示 NO INFO
            elite_group[e_base].visible = False
            for i in range(1, 4):
                elite_group[e_base + i].visible = False

            pot_group[p_base].visible = False
            for i in range(1, 7):
                pot_group[p_base + i].visible = False

            for i in range(0, 3):
                lvl_group[l_base + i].visible = False

            for layer in card_group:
                if "NO INFO" in layer.name and abs(layer.bbox[1] - lvl_group[l_base].bbox[1]) < 150:
                    layer.visible = True
