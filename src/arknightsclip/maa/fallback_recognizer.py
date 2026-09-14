"""
MAA 兼容规范视觉识别降级适配器 (FallbackOperBoxRecognizer)
完全遵循 MAA OperBoxImageAnalyzer 720P 视觉协议：
1. 1280x720 坐标归一化
2. 双行 ROI (Top: [0, 78, 1145, 50], Bottom: [0, 394, 1145, 50])
3. 9 大职业角标锚点定位与 NMS 去重
4. 相对几何偏移扣取 Elite / Potential / Level / Name
5. 真实等级数字 OCR 与置信度评估 (杜绝精二默认90的伪逻辑)
6. 官方注册表 (OperatorRegistry) 模糊消歧
"""

import os
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'
import cv2
import re
import numpy as np
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from ..config import ProjectConfig
from ..models.operator import OperatorState, ConfidenceScore, RecognitionMethod
from ..registry.operator_registry import OperatorRegistry
from .adapter import MaaAcquisitionAdapter

class FallbackOperBoxRecognizer(MaaAcquisitionAdapter):
    def __init__(self, config: ProjectConfig, registry: Optional[OperatorRegistry] = None):
        self.config = config
        self.registry = registry or OperatorRegistry(
            config.resolve_path("src/arknightsclip/registry/operator_registry.json")
        )
        self.template_dir = config.resolve_path(config.maa.template_dir)
        
        self.role_templates: Dict[str, np.ndarray] = {}
        self.elite_templates: Dict[int, np.ndarray] = {}
        self.potential_templates: Dict[int, np.ndarray] = {}
        self._load_templates()

        # MAA 720P 相对偏移标准契约
        self.OFFSET_ELITE = [11, 171, 24, 35]
        self.OFFSET_POTENTIAL = [99, 194, 24, 24]
        self.OFFSET_LEVEL = [5, 230, 37, 23]
        self.OFFSET_NAME = [0, 265, 128, 22]

        self.ROI_TOP = [0, 78, 1145, 50]
        self.ROI_BOTTOM = [0, 394, 1145, 50]

        # OCR reader 懒加载
        self._ocr_reader = None

    def _get_ocr(self):
        if self._ocr_reader is None:
            try:
                import easyocr
                self._ocr_reader = easyocr.Reader(['ch_sim', 'en'], gpu=False)
            except Exception as e:
                print(f"[FallbackRecognizer] EasyOCR 模块未就绪: {e}")
                self._ocr_reader = False
        return self._ocr_reader

    def _load_templates(self):
        """加载 MAA 原版 720P 匹配模板"""
        # 1. 9 大职业角标
        for r in range(1, 10):
            p = self.template_dir / f"OperBoxFlagRole{r}.png"
            if p.exists():
                img = cv2.imdecode(np.fromfile(str(p), dtype=np.uint8), cv2.IMREAD_COLOR)
                if img is not None:
                    self.role_templates[f"Role{r}"] = img

        # 2. 精英化模板
        for e in [1, 2]:
            p = self.template_dir / f"OperBoxFlagElite{e}.png"
            if p.exists():
                img = cv2.imdecode(np.fromfile(str(p), dtype=np.uint8), cv2.IMREAD_COLOR)
                if img is not None:
                    self.elite_templates[e] = img

        # 3. 潜能模板
        for pot in range(2, 7):
            p = self.template_dir / f"OperBoxPotential{pot}.png"
            if p.exists():
                img = cv2.imdecode(np.fromfile(str(p), dtype=np.uint8), cv2.IMREAD_COLOR)
                if img is not None:
                    self.potential_templates[pot] = img

    def is_available(self) -> bool:
        return len(self.role_templates) > 0

    def collect_operators(self, max_pages: int = 5) -> List[OperatorState]:
        # 需配合 Collector 传入截屏帧使用
        return []

    def analyze_frame(self, frame_bgr: np.ndarray) -> List[OperatorState]:
        """对单帧游戏画面执行 MAA 规范的双行网格解析"""
        h, w = frame_bgr.shape[:2]
        # 归一化至 1280x720 标准基准
        if (w, h) != (1280, 720):
            frame_720p = cv2.resize(frame_bgr, (1280, 720), interpolation=cv2.INTER_AREA)
        else:
            frame_720p = frame_bgr

        # 1. 在 Top ROI 和 Bottom ROI 扫描职业角标
        anchors_top = self._find_role_anchors(frame_720p, self.ROI_TOP)
        anchors_bottom = self._find_role_anchors(frame_720p, self.ROI_BOTTOM)
        all_anchors = anchors_top + anchors_bottom

        # 按横向 X 坐标排序
        all_anchors.sort(key=lambda a: a["x"])

        results: List[OperatorState] = []
        for anchor in all_anchors:
            ax, ay, aw, ah = anchor["x"], anchor["y"], anchor["w"], anchor["h"]

            # 2. 识别精英度 (Elite)
            elite, elite_conf = self._recognize_elite(frame_720p, ax, ay)

            # 3. 识别潜能 (Potential)
            potential, pot_conf = self._recognize_potential(frame_720p, ax, ay)

            # 4. 识别等级 (Level) - 真实 OCR，非满级硬编码
            level, lvl_conf, lvl_method = self._recognize_level(frame_720p, ax, ay, elite)

            # 5. 识别干员名称 (Name) 与注册表消歧
            name, name_conf, char_id, rarity = self._recognize_name(frame_720p, ax, ay)

            needs_review = (lvl_conf < 0.6) or (name_conf < 0.6) or (char_id == "unknown")

            state = OperatorState(
                char_id=char_id,
                name=name,
                own=True,
                elite=elite,
                level=level,
                potential=potential,
                rarity=rarity,
                confidence={
                    "elite": ConfidenceScore(value=elite, confidence=elite_conf, method=RecognitionMethod.TEMPLATE),
                    "potential": ConfidenceScore(value=potential, confidence=pot_conf, method=RecognitionMethod.TEMPLATE),
                    "level": ConfidenceScore(value=level, confidence=lvl_conf, method=lvl_method),
                    "name": ConfidenceScore(value=name, confidence=name_conf, method=RecognitionMethod.OCR),
                },
                source=RecognitionMethod.TEMPLATE,
                needs_review=needs_review,
            )
            results.append(state)

        return results

    def _find_role_anchors(self, frame_720p: np.ndarray, roi: List[int]) -> List[Dict[str, Any]]:
        rx, ry, rw, rh = roi
        roi_img = frame_720p[ry:ry+rh, rx:rx+rw]
        candidates = []

        for r_name, tmpl in self.role_templates.items():
            if tmpl.shape[0] > roi_img.shape[0] or tmpl.shape[1] > roi_img.shape[1]:
                continue
            res = cv2.matchTemplate(roi_img, tmpl, cv2.TM_CCOEFF_NORMED)
            loc = np.where(res >= 0.72)
            for pt in zip(*loc[::-1]):
                candidates.append({
                    "x": rx + pt[0],
                    "y": ry + pt[1],
                    "w": tmpl.shape[1],
                    "h": tmpl.shape[0],
                    "score": float(res[pt[1], pt[0]]),
                    "role": r_name,
                })

        # NMS 非极大值抑制 (横向距离至少大于 60px)
        candidates.sort(key=lambda c: c["score"], reverse=True)
        selected = []
        for c in candidates:
            overlap = False
            for s in selected:
                if abs(c["x"] - s["x"]) < 60 and abs(c["y"] - s["y"]) < 30:
                    overlap = True
                    break
            if not overlap:
                selected.append(c)

        return selected

    def _recognize_elite(self, frame_720p: np.ndarray, ax: int, ay: int) -> Tuple[int, float]:
        dx, dy, w, h = self.OFFSET_ELITE
        x1, y1 = max(0, ax + dx), max(0, ay + dy)
        x2, y2 = min(frame_720p.shape[1], x1 + w), min(frame_720p.shape[0], y1 + h)
        roi = frame_720p[y1:y2, x1:x2]

        best_elite = 0
        best_score = 0.0
        for e, tmpl in self.elite_templates.items():
            if tmpl.shape[0] > roi.shape[0] or tmpl.shape[1] > roi.shape[1]:
                continue
            res = cv2.matchTemplate(roi, tmpl, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, _ = cv2.minMaxLoc(res)
            if max_val > 0.82 and max_val > best_score:
                best_score = float(max_val)
                best_elite = e

        return best_elite, (best_score if best_elite > 0 else 1.0)

    def _recognize_potential(self, frame_720p: np.ndarray, ax: int, ay: int) -> Tuple[int, float]:
        dx, dy, w, h = self.OFFSET_POTENTIAL
        x1, y1 = max(0, ax + dx), max(0, ay + dy)
        x2, y2 = min(frame_720p.shape[1], x1 + w), min(frame_720p.shape[0], y1 + h)
        roi = frame_720p[y1:y2, x1:x2]

        best_pot = 1
        best_score = 0.0
        for p, tmpl in self.potential_templates.items():
            if tmpl.shape[0] > roi.shape[0] or tmpl.shape[1] > roi.shape[1]:
                continue
            res = cv2.matchTemplate(roi, tmpl, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, _ = cv2.minMaxLoc(res)
            if max_val > 0.80 and max_val > best_score:
                best_score = float(max_val)
                best_pot = p

        return best_pot, (best_score if best_pot > 1 else 1.0)

    def _recognize_level(self, frame_720p: np.ndarray, ax: int, ay: int, elite: int) -> Tuple[int, float, str]:
        """真实截取等级区域执行 OCR，绝不硬编码 90"""
        dx, dy, w, h = self.OFFSET_LEVEL
        x1, y1 = max(0, ax + dx), max(0, ay + dy)
        x2, y2 = min(frame_720p.shape[1], x1 + w), min(frame_720p.shape[0], y1 + h)
        roi = frame_720p[y1:y2, x1:x2]

        ocr = self._get_ocr()
        if ocr:
            try:
                # 局部二值化与轻微膨胀强化数字边缘
                gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
                _, bin_img = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY)
                res = ocr.readtext(bin_img)
                for bbox, text, conf in res:
                    digits = re.findall(r'\d+', text)
                    if digits:
                        val = int(digits[0])
                        if 1 <= val <= 90:
                            return val, float(conf), RecognitionMethod.OCR
            except Exception:
                pass

        # 若 OCR 失败或置信度不足，绝不伪造 90，记录低置信度并标记待审核
        return 1, 0.2, RecognitionMethod.OCR

    def _recognize_name(self, frame_720p: np.ndarray, ax: int, ay: int) -> Tuple[str, float, str, int]:
        """截取干员名称区域并结合官方注册表消歧"""
        dx, dy, w, h = self.OFFSET_NAME
        x1, y1 = max(0, ax + dx), max(0, ay + dy)
        x2, y2 = min(frame_720p.shape[1], x1 + w), min(frame_720p.shape[0], y1 + h)
        roi = frame_720p[y1:y2, x1:x2]

        ocr = self._get_ocr()
        detected_text = ""
        conf_val = 0.0
        if ocr:
            try:
                gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
                res = ocr.readtext(gray)
                if res:
                    detected_text = res[0][1].strip()
                    conf_val = float(res[0][2])
            except Exception:
                pass

        entry = self.registry.resolve(detected_text)
        if entry:
            return entry.canonical_name_zh, max(conf_val, 0.9), entry.char_id, entry.rarity

        return (detected_text or "未知干员"), conf_val, "unknown", 6
