import os
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'
import cv2
import re
import numpy as np
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Any
from ..config import ProjectConfig
from ..models.operator import OperatorState, ConfidenceScore, RecognitionMethod
from ..models.operbox import CardROI, CardCropCandidate
from ..registry.operator_registry import OperatorRegistry

class OperBoxAnalyzer:
    def __init__(self, config: ProjectConfig, registry: Optional[OperatorRegistry] = None):
        self.config = config
        self.registry = registry or OperatorRegistry(
            config.resolve_path('src/arknightsclip/registry/operator_registry.json')
        )
        self.template_dir = config.resolve_path(config.maa.template_dir)
        
        self.role_templates: Dict[str, np.ndarray] = {}
        self.elite_templates: Dict[int, np.ndarray] = {}
        self.potential_templates: Dict[int, np.ndarray] = {}
        self._load_templates()

        self.MAA_REF_W = 1280
        self.MAA_REF_H = 720

        self.ROI_ROLE_TOP = [0, 78, 1145, 50]
        self.ROI_ROLE_BOTTOM = [0, 394, 1145, 50]

        self.OFFSET_ELITE = [11, 171, 24, 35]
        self.OFFSET_POTENTIAL = [99, 194, 24, 24]
        self.OFFSET_LEVEL = [5, 230, 37, 23]
        self.OFFSET_NAME = [0, 265, 128, 22]

        # 720P 下卡片包围盒 [-12, -8, 153.333, 298] -> 1080P 下精确对应 [x-18, y-12, 230, 447]
        self.CARD_VISUAL_OFFSET = [-12, -8, 230.0 / 1.5, 298]
        self.SAFE_LEFT_MARGIN_720P = 25
        self.SAFE_RIGHT_MARGIN_720P = 1275

        self._ocr_reader = None

    def _get_ocr(self):
        if self._ocr_reader is None:
            try:
                import easyocr
                self._ocr_reader = easyocr.Reader(['ch_sim', 'en'], gpu=False)
            except Exception as e:
                self._ocr_reader = False
        return self._ocr_reader

    def _load_templates(self):
        for r in range(1, 10):
            p = self.template_dir / f'OperBoxFlagRole{r}.png'
            if p.exists():
                img = cv2.imdecode(np.fromfile(str(p), dtype=np.uint8), cv2.IMREAD_COLOR)
                if img is not None:
                    self.role_templates[f'Role{r}'] = img

        for e in [1, 2]:
            p = self.template_dir / f'OperBoxFlagElite{e}.png'
            if p.exists():
                img = cv2.imdecode(np.fromfile(str(p), dtype=np.uint8), cv2.IMREAD_COLOR)
                if img is not None:
                    self.elite_templates[e] = img

        for pot in range(2, 7):
            p = self.template_dir / f'OperBoxPotential{pot}.png'
            if p.exists():
                img = cv2.imdecode(np.fromfile(str(p), dtype=np.uint8), cv2.IMREAD_COLOR)
                if img is not None:
                    self.potential_templates[pot] = img

    def analyze_page(
        self,
        frame_native: np.ndarray,
        page_index: int = 1,
        source_page_name: str = 'page_0001.png'
    ) -> Tuple[List[OperatorState], List[CardCropCandidate]]:
        native_h, native_w = frame_native.shape[:2]
        scale_x = native_w / float(self.MAA_REF_W)
        scale_y = native_h / float(self.MAA_REF_H)

        if (native_w, native_h) != (self.MAA_REF_W, self.MAA_REF_H):
            frame_720p = cv2.resize(frame_native, (self.MAA_REF_W, self.MAA_REF_H), interpolation=cv2.INTER_AREA)
        else:
            frame_720p = frame_native

        detected_flags = self._detect_role_flags(frame_720p)
        if not detected_flags:
            return [], []

        states: List[OperatorState] = []
        candidates: List[CardCropCandidate] = []

        for card_idx, flag in enumerate(detected_flags, start=1):
            fx, fy, fw, fh = flag['rect']

            name, name_conf = self._recognize_name(frame_720p, fx, fy)
            reg_entry = self.registry.resolve(name)
            char_id = reg_entry.char_id if reg_entry else f'unknown_{name}'
            canonical_name = reg_entry.canonical_name_zh if reg_entry else name
            rarity = reg_entry.rarity if reg_entry else 6

            elite, elite_conf = self._recognize_elite(frame_720p, fx, fy)
            potential, pot_conf = self._recognize_potential(frame_720p, fx, fy)
            level, lvl_conf = self._recognize_level(frame_720p, fx, fy, elite, rarity)

            state = OperatorState(
                char_id=char_id,
                name=canonical_name,
                own=True,
                elite=elite,
                level=level,
                potential=potential,
                rarity=rarity,
                confidence={
                    'name': ConfidenceScore(canonical_name, name_conf, 'ocr_name'),
                    'elite': ConfidenceScore(elite, elite_conf, 'tmpl_elite'),
                    'potential': ConfidenceScore(potential, pot_conf, 'tmpl_potential'),
                    'level': ConfidenceScore(level, lvl_conf, 'ocr_level'),
                },
                source='MaaCore OperBoxImageAnalyzer',
                needs_review=(reg_entry is None or lvl_conf < 0.6)
            )
            states.append(state)

            card_x_720 = fx + self.CARD_VISUAL_OFFSET[0]
            card_y_720 = fy + self.CARD_VISUAL_OFFSET[1]
            card_w_720 = self.CARD_VISUAL_OFFSET[2]
            card_h_720 = self.CARD_VISUAL_OFFSET[3]

            is_edge = (card_x_720 < self.SAFE_LEFT_MARGIN_720P) or ((card_x_720 + card_w_720) > self.SAFE_RIGHT_MARGIN_720P)

            nx = max(0, int(round(card_x_720 * scale_x)))
            ny = max(0, int(round(card_y_720 * scale_y)))
            nw = min(native_w - nx, int(round(card_w_720 * scale_x)))
            nh = min(native_h - ny, int(round(card_h_720 * scale_y)))

            card_roi = CardROI(x=nx, y=ny, width=nw, height=nh, source_width=native_w, source_height=native_h)

            crop_img = None
            if nw > 10 and nh > 10:
                crop_img = frame_native[ny:ny+nh, nx:nx+nw].copy()

            expected_area = (card_w_720 * scale_x) * (card_h_720 * scale_y)
            area_ratio = (nw * nh) / max(1.0, expected_area)
            edge_distance = min(card_x_720 - self.SAFE_LEFT_MARGIN_720P, self.SAFE_RIGHT_MARGIN_720P - (card_x_720 + card_w_720))
            edge_score = max(0.0, min(1.0, edge_distance / 100.0))

            quality_score = 0.6 * area_ratio + 0.4 * edge_score
            if is_edge:
                quality_score *= 0.3

            candidate = CardCropCandidate(
                char_id=char_id,
                name=canonical_name,
                page_index=page_index,
                card_index=card_idx,
                source_page=source_page_name,
                roi=card_roi,
                quality_score=quality_score,
                crop_image=crop_img,
                is_edge=is_edge,
                rejection_reason='partial_edge_card' if is_edge else None
            )
            candidates.append(candidate)

        return states, candidates

    def _detect_role_flags(self, frame_720p: np.ndarray) -> List[Dict[str, Any]]:
        results = []
        for r_name, tmpl in self.role_templates.items():
            tw, th = tmpl.shape[1], tmpl.shape[0]
            for roi in [self.ROI_ROLE_TOP, self.ROI_ROLE_BOTTOM]:
                rx, ry, rw, rh = roi
                roi_img = frame_720p[ry:ry+rh, rx:rx+rw]
                if roi_img.shape[0] < th or roi_img.shape[1] < tw:
                    continue
                match_res = cv2.matchTemplate(roi_img, tmpl, cv2.TM_CCOEFF_NORMED)
                threshold = 0.80
                locs = np.where(match_res >= threshold)
                for pt in zip(*locs[::-1]):
                    gx = rx + pt[0]
                    gy = ry + pt[1]
                    score = float(match_res[pt[1], pt[0]])
                    results.append({
                        'rect': [gx, gy, tw, th],
                        'score': score,
                        'role': r_name
                    })

        results.sort(key=lambda x: x['score'], reverse=True)
        kept = []
        for cand in results:
            cx, cy, cw, ch = cand['rect']
            overlap = False
            for k in kept:
                kx, ky, kw, kh = k['rect']
                if abs(cx - kx) < 25 and abs(cy - ky) < 25:
                    overlap = True
                    break
            if not overlap:
                kept.append(cand)

        kept.sort(key=lambda x: (0 if x['rect'][1] < 250 else 1, x['rect'][0]))
        return kept

    def _recognize_name(self, frame_720p: np.ndarray, fx: int, fy: int) -> Tuple[str, float]:
        dx, dy, dw, dh = self.OFFSET_NAME
        nx = max(0, fx + dx)
        ny = max(0, fy + dy)
        nw = min(frame_720p.shape[1] - nx, dw)
        nh = min(frame_720p.shape[0] - ny, dh)
        roi = frame_720p[ny:ny+nh, nx:nx+nw]

        ocr = self._get_ocr()
        if ocr and roi.size > 0:
            try:
                ocr_res = ocr.readtext(roi)
                for _, text, conf in ocr_res:
                    clean = text.strip()
                    if clean:
                        return clean, float(conf)
            except Exception:
                pass
        return '', 0.0

    def _recognize_elite(self, frame_720p: np.ndarray, fx: int, fy: int) -> Tuple[int, float]:
        dx, dy, dw, dh = self.OFFSET_ELITE
        nx = max(0, fx + dx)
        ny = max(0, fy + dy)
        nw = min(frame_720p.shape[1] - nx, dw)
        nh = min(frame_720p.shape[0] - ny, dh)
        roi = frame_720p[ny:ny+nh, nx:nx+nw]

        best_elite = 0
        best_score = 0.0
        for e, tmpl in self.elite_templates.items():
            if roi.shape[0] >= tmpl.shape[0] and roi.shape[1] >= tmpl.shape[1]:
                res = cv2.matchTemplate(roi, tmpl, cv2.TM_CCOEFF_NORMED)
                _, max_val, _, _ = cv2.minMaxLoc(res)
                if max_val > 0.80 and max_val > best_score:
                    best_score = max_val
                    best_elite = e
        return best_elite, best_score if best_elite > 0 else 1.0

    def _recognize_potential(self, frame_720p: np.ndarray, fx: int, fy: int) -> Tuple[int, float]:
        dx, dy, dw, dh = self.OFFSET_POTENTIAL
        nx = max(0, fx + dx)
        ny = max(0, fy + dy)
        nw = min(frame_720p.shape[1] - nx, dw)
        nh = min(frame_720p.shape[0] - ny, dh)
        roi = frame_720p[ny:ny+nh, nx:nx+nw]

        best_pot = 1
        best_score = 0.0
        for p, tmpl in self.potential_templates.items():
            if roi.shape[0] >= tmpl.shape[0] and roi.shape[1] >= tmpl.shape[1]:
                res = cv2.matchTemplate(roi, tmpl, cv2.TM_CCOEFF_NORMED)
                _, max_val, _, _ = cv2.minMaxLoc(res)
                if max_val > 0.78 and max_val > best_score:
                    best_score = max_val
                    best_pot = p
        return best_pot, best_score if best_pot > 1 else 1.0

    def _recognize_level(self, frame_720p: np.ndarray, fx: int, fy: int, elite: int, rarity: int) -> Tuple[int, float]:
        dx, dy, dw, dh = self.OFFSET_LEVEL
        nx = max(0, fx + dx)
        ny = max(0, fy + dy)
        nw = min(frame_720p.shape[1] - nx, dw)
        nh = min(frame_720p.shape[0] - ny, dh)
        roi = frame_720p[ny:ny+nh, nx:nx+nw]

        ocr = self._get_ocr()
        if ocr and roi.size > 0:
            try:
                ocr_res = ocr.readtext(roi, allowlist='0123456789')
                for _, text, conf in ocr_res:
                    digits = re.findall(r'\d+', text)
                    if digits:
                        lvl = int(digits[0])
                        if 1 <= lvl <= 90:
                            return lvl, float(conf)
            except Exception:
                pass

        return 1, 0.2
