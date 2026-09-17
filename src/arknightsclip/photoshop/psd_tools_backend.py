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

# ============================================================
# 精确 card_group 索引映射（从 能天使.psd 结构导出，固定不变）
# ============================================================
# 卡面组 (psd[2]) 各槽位子图层索引:
#   Slot 1: card_base=[0], portrait=None,  no_info=[1]
#   Slot 2: card_base=[2], portrait=[3],   no_info=[4]
#   Slot 3: card_base=[5], portrait=[6],   no_info=[7]
#   Slot 4: card_base=[8], portrait=[9],   no_info=[10]
#   Slot 5: card_base=[11],portrait=[12],  no_info=[13]
#   Slot 6: card_base=[14],portrait=[15],  no_info=[16]  ← PSD默认portrait可见/no_info隐藏
#   Slot 7: card_base=[17],portrait=[18],  no_info=[19]  ← PSD默认portrait可见/no_info隐藏
#   Slot 8: card_base=[20],portrait=[21],  no_info=[22]
CARD_IDX = {
    1: {"card_base": 0, "portrait": None, "no_info": 1},
    2: {"card_base": 2, "portrait":    3, "no_info": 4},
    3: {"card_base": 5, "portrait":    6, "no_info": 7},
    4: {"card_base": 8, "portrait":    9, "no_info": 10},
    5: {"card_base": 11,"portrait":   12, "no_info": 13},
    6: {"card_base": 14,"portrait":   15, "no_info": 16},
    7: {"card_base": 17,"portrait":   18, "no_info": 19},
    8: {"card_base": 20,"portrait":   21, "no_info": 22},
}
# 精英等级组 (psd[4]) 每槽 4 个 layer: [base, 精0, 精一, 精二]
# 潜能组 (psd[3]) 每槽 7 个 layer: [base, 潜1..6]
# 角色等级组 (psd[5]) 每槽 3 个 layer: [base, text, LV]


class PSDToolsRenderer(PhotoshopRenderer):
    def __init__(self, config: ProjectConfig, template_path: Optional[Path] = None):
        self.config = config
        self.template_path = template_path or config.resolve_path(config.photoshop.master_template)
        if not self.template_path.exists():
            for cand in [
                config.resolve_path("psd模板/只需要模板/能天使.psd"),
                Path(r"E:\明日方舟报菜名\psd模板\只需要模板\能天使.psd"),
            ]:
                if cand.exists():
                    self.template_path = cand
                    break

    def render_scene(self, manifest: SceneManifest, output_dir: Path) -> Dict[str, Path]:
        output_dir.mkdir(parents=True, exist_ok=True)
        psd = PSDImage.open(str(self.template_path))

        card_group  = psd[2]   # 卡面 (23 layers)
        pot_group   = psd[3]   # 潜能 (56 layers, 8 slots * 7)
        elite_group = psd[4]   # 精英等级 (32 layers, 8 slots * 4)
        lvl_group   = psd[5]   # 角色等级 (24 layers, 8 slots * 3)

        # 映射 P1..P8 槽位
        player_keys = ["P1", "P2", "P3", "P4", "P5", "P6", "P7", "P8"]
        slots_to_apply = {}
        for slot_idx, p_key in enumerate(player_keys, start=1):
            if p_key in manifest.players:
                slots_to_apply[slot_idx] = manifest.players[p_key]
            else:
                default_own = (slot_idx >= 6)
                slots_to_apply[slot_idx] = PlayerSlotState(own=default_own, no_info=not default_own)

        level_text_draws = []

        # ----------------------------------------------------------
        # 1. 严格设置各个 Group 的图层可见性
        # ----------------------------------------------------------
        for slot_idx in range(1, 9):
            state = slots_to_apply[slot_idx]
            ci = CARD_IDX[slot_idx]

            # (A) 卡面组: card_base, portrait, no_info
            card_group[ci["card_base"]].visible = True
            if ci["portrait"] is not None:
                card_group[ci["portrait"]].visible = state.own
            card_group[ci["no_info"]].visible = not state.own

            # (B) 精英组: 每槽 4 个 layer: [base, 精0, 精一, 精二]
            e_base = (slot_idx - 1) * 4
            elite_group[e_base].visible = state.own
            elite_group[e_base + 1].visible = (state.own and state.elite == 0)
            elite_group[e_base + 2].visible = (state.own and state.elite == 1)
            elite_group[e_base + 3].visible = (state.own and state.elite == 2)

            # (C) 潜能组: 每槽 7 个 layer: [base, 潜1..6]
            p_base = (slot_idx - 1) * 7
            has_pot = (state.own and 1 <= state.potential <= 6)
            pot_group[p_base].visible = has_pot
            for p_num in range(1, 7):
                pot_group[p_base + p_num].visible = (state.own and state.potential == p_num)

            # (D) 等级组: 每槽 3 个 layer: [circle_base, text, LV]
            l_base = (slot_idx - 1) * 3
            lvl_group[l_base].visible = state.own
            lvl_group[l_base + 1].visible = False  # 隐藏 PSD 静态文本，用 PIL 动态绘制
            lvl_group[l_base + 2].visible = state.own
            if state.own:
                level_text_draws.append((lvl_group[l_base + 1].bbox, str(state.level)))

        # ----------------------------------------------------------
        # 2. 原生合成: psd.composite() 精确保留原生混合模式与遮罩
        # ----------------------------------------------------------
        comp = psd.composite().convert('RGBA')

        # ----------------------------------------------------------
        # 3. 动态等级文本: 绘制在合成图对应圆圈中心
        # ----------------------------------------------------------
        draw = ImageDraw.Draw(comp)
        try:
            font = ImageFont.truetype("arial.ttf", 34)
        except Exception:
            font = ImageFont.load_default()

        for (bbox, text) in level_text_draws:
            # 居中对齐微调
            tx = bbox[0] + (bbox[2] - bbox[0] - 36) // 2 if len(bbox) >= 4 else bbox[0]
            ty = bbox[1] - 4
            draw.text((tx, ty), text, fill=(255, 255, 255, 255), font=font)

        # ----------------------------------------------------------
        # 4. 规范拆分三层素材
        # ----------------------------------------------------------
        bg_path    = output_dir / "background.png"
        cards_path = output_dir / "character_cards.png"
        doc_path   = output_dir / "doctor_info.png"

        # 1. Background (Layer 0 + Layer 1)
        bg = Image.new('RGB', (1920, 1080), (0, 0, 0))
        if len(psd) > 0 and psd[0].topil():
            l0 = psd[0].topil()
            bg.paste(l0, (max(0, psd[0].bbox[0]), max(0, psd[0].bbox[1])),
                     l0 if l0.mode == 'RGBA' else None)
        if len(psd) > 1 and psd[1].topil():
            l1 = psd[1].topil()
            bg.paste(l1, (psd[1].bbox[0], psd[1].bbox[1]),
                     l1 if l1.mode == 'RGBA' else None)
        bg.save(bg_path, format='PNG')

        arr_full = np.array(comp)
        arr_bg   = np.array(bg.convert('RGBA'))
        diff     = np.max(np.abs(
            arr_full[:, :, :3].astype(np.int32) - arr_bg[:, :, :3].astype(np.int32)
        ), axis=2)
        fg_mask = (diff > 4).astype(np.uint8) * 255

        # 2. Doctor Info (x <= 165 or x >= 1755)
        doc_mask = np.zeros((1080, 1920), dtype=np.uint8)
        doc_mask[:, :165]   = fg_mask[:, :165]
        doc_mask[:, 1755:]  = fg_mask[:, 1755:]
        doc_arr = arr_full.copy()
        doc_arr[:, :, 3] = doc_mask
        Image.fromarray(doc_arr, 'RGBA').save(doc_path, format='PNG')

        # 3. Character Cards (165 < x < 1755)
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

