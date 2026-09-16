
import os
import time
import json
import datetime
import subprocess
import numpy as np
import cv2
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Any

from ..config import ProjectConfig
from ..models.operator import OperatorState
from ..models.operbox import CardROI, CardProvenance, CardCropCandidate, OperBoxScanSession
from ..models.player import PlayerProfile, PlayerDataSet
from ..registry.operator_registry import OperatorRegistry
from .operbox_analyzer import OperBoxAnalyzer

class OperBoxCollector:
    def __init__(self, config: ProjectConfig, analyzer: Optional[OperBoxAnalyzer] = None):
        self.config = config
        self.registry = OperatorRegistry(config.resolve_path('src/arknightsclip/registry/operator_registry.json'))
        self.analyzer = analyzer or OperBoxAnalyzer(config, self.registry)
        self.adb_path = config.maa.adb_path or self._find_adb()
        self.adb_device = config.maa.adb_device

    def _find_adb(self) -> str:
        candidates = [
            r'C:\\Program Files\\Netease\\MuMuPlayer-12.0\\nx_device\\12.0\\shell\\adb.exe',
            r'C:\\Program Files\\Netease\\MuMuPlayer-12.0\\nx_main\\adb.exe',
            r'D:\\Program Files\\Netease\\MuMuPlayer-12.0\\nx_device\\12.0\\shell\\adb.exe',
            r'C:\\leidian\\LDPlayer9\\adb.exe',
            r'D:\\leidian\\LDPlayer9\\adb.exe',
            'adb'
        ]
        for c in candidates:
            if os.path.exists(c):
                return c
        return 'adb'

    def _run_adb(self, args: List[str], timeout: int = 10) -> subprocess.CompletedProcess:
        cmd = [self.adb_path, '-s', self.adb_device] + args
        return subprocess.run(cmd, capture_output=True, timeout=timeout)

    def connect(self) -> bool:
        try:
            subprocess.run([self.adb_path, 'connect', self.adb_device], capture_output=True, timeout=5)
            res = subprocess.run([self.adb_path, 'devices'], capture_output=True, text=True, timeout=5)
            return self.adb_device in res.stdout
        except Exception:
            return False

    def screencap(self) -> Optional[np.ndarray]:
        try:
            self.connect()
            cmd = [self.adb_path, '-s', self.adb_device, 'exec-out', 'screencap', '-p']
            res = subprocess.run(cmd, capture_output=True, timeout=8)
            if res.returncode == 0 and len(res.stdout) > 1000:
                arr = np.frombuffer(res.stdout, dtype=np.uint8)
                return cv2.imdecode(arr, cv2.IMREAD_COLOR)
        except Exception as e:
            print(f'[OperBoxCollector] 截图异常: {e}')
        return None

    def swipe(self, x1: int, y1: int, x2: int, y2: int, duration_ms: int = 800):
        self._run_adb(['shell', 'input', 'swipe', str(x1), str(y1), str(x2), str(y2), str(duration_ms)])

    def collect(
        self,
        player_id: str,
        display_name: str = '博士',
        max_pages: int = 5,
        capture_cards: bool = True,
        save_pages: bool = True,
        debug: bool = False
    ) -> PlayerDataSet:
        timestamp_str = datetime.datetime.now().strftime('%Y%m%dT%H%M%S')
        scan_id = f'{timestamp_str}_{player_id}'

        print(f'\n=======================================================')
        print(f' OperBox Single-Scan 启动')
        print(f' 会话 ID (scan_id): {scan_id}')
        print(f' 玩家标识: {player_id} ({display_name}) | 最大翻页: {max_pages}')
        print(f' 保存卡片素材 (capture_cards): {capture_cards} | 保留整页 (save_pages): {save_pages}')
        print(f'=======================================================')

        raw_player_dir = self.config.get_raw_player_dir(player_id)
        operbox_dir = raw_player_dir / 'operbox'
        pages_dir = operbox_dir / 'pages'
        cards_raw_dir = operbox_dir / 'cards_raw'
        meta_dir = operbox_dir / 'card_metadata'
        cand_dir = operbox_dir / 'candidates'

        for d in [raw_player_dir, operbox_dir, pages_dir, cards_raw_dir, meta_dir, cand_dir]:
            d.mkdir(parents=True, exist_ok=True)

        session = OperBoxScanSession(scan_id=scan_id, player_id=player_id)
        all_candidates: Dict[str, List[CardCropCandidate]] = {}
        all_states: Dict[str, OperatorState] = {}

        connected = self.connect()
        if not connected:
            print(f'[OperBoxCollector] 警告: 未检测到运行中的 ADB 设备 {self.adb_device}，无法进行在线捕获。')
        else:
            sw_cfg = self.config.maa.swipe
            for page_idx in range(1, max_pages + 1):
                page_name = f'page_{page_idx:04d}.png'
                print(f'\n[Page {page_idx:02d}] 正在抓取屏幕帧...')
                frame = self.screencap()
                if frame is None:
                    print(f'[Page {page_idx:02d}] 截图失败，扫描终止。')
                    break

                if save_pages:
                    cv2.imencode('.png', frame)[1].tofile(str(pages_dir / page_name))

                page_states, page_candidates = self.analyzer.analyze_page(
                    frame, page_index=page_idx, source_page_name=page_name
                )

                new_operators = 0
                for st in page_states:
                    if st.char_id not in all_states:
                        all_states[st.char_id] = st
                        new_operators += 1
                        print(f'   -> 识别干员: {st.name:8s} ({st.char_id}) | 精{st.elite} | Lv.{st.level:2d} | 潜{st.potential}')
                    else:
                        existing = all_states[st.char_id]
                        if existing.level == 1 and st.level > 1:
                            existing.level = st.level
                            existing.confidence['level'] = st.confidence.get('level')

                for cand in page_candidates:
                    if cand.crop_image is not None and not cand.is_edge:
                        all_candidates.setdefault(cand.char_id, []).append(cand)

                print(f'[Page {page_idx:02d}] 本页识别 {len(page_states)} 位干员，新增 {new_operators} 位')

                if new_operators == 0 and page_idx > 1:
                    print(f'[Page {page_idx:02d}] 连续翻页无新增干员，判定到达仓库末端。')
                    session.pages_captured = page_idx
                    break

                session.pages_captured = page_idx
                self.swipe(sw_cfg.start_x, sw_cfg.start_y, sw_cfg.end_x, sw_cfg.end_y, sw_cfg.duration_ms)
                time.sleep(sw_cfg.settle_delay_sec)

        saved_cards_count = 0
        missing_card_assets = []

        if capture_cards:
            for char_id, op in all_states.items():
                cands = all_candidates.get(char_id, [])
                if not cands:
                    missing_card_assets.append(char_id)
                    continue

                best_cand = max(cands, key=lambda c: c.quality_score)
                card_png_path = cards_raw_dir / f'{char_id}.png'
                cv2.imencode('.png', best_cand.crop_image)[1].tofile(str(card_png_path))

                provenance = CardProvenance(
                    char_id=char_id,
                    name=op.name,
                    scan_id=scan_id,
                    player_id=player_id,
                    source_page=best_cand.source_page,
                    page_index=best_cand.page_index,
                    card_index=best_cand.card_index,
                    roi=best_cand.roi.to_list(),
                    capture_timestamp=datetime.datetime.now().isoformat(),
                    candidate_count=len(cands),
                    selected_reason=f'best_quality_score_{best_cand.quality_score:.2f}'
                )
                with open(meta_dir / f'{char_id}.json', 'w', encoding='utf-8') as f:
                    json.dump(provenance.to_dict(), f, ensure_ascii=False, indent=2)

                saved_cards_count += 1

        session.operators_found = len(all_states)
        session.card_assets_captured = saved_cards_count
        session.missing_card_assets = missing_card_assets
        session.status = 'completed'

        with open(raw_player_dir / 'operators.json', 'w', encoding='utf-8') as f:
            json.dump([op.to_dict() for op in all_states.values()], f, ensure_ascii=False, indent=2)

        with open(raw_player_dir / 'capture_metadata.json', 'w', encoding='utf-8') as f:
            json.dump(session.to_summary(), f, ensure_ascii=False, indent=2)

        profile = PlayerProfile(id=player_id, display_name=display_name)
        with open(raw_player_dir / 'profile.json', 'w', encoding='utf-8') as f:
            json.dump({
                'id': profile.id,
                'display_name': profile.display_name,
                'doctor_level': profile.doctor_level,
                'avatar': profile.avatar,
            }, f, ensure_ascii=False, indent=2)

        print(f'\n=======================================================')
        print(f' 单次扫描汇总:')
        print(f'  - 识别拥有干员数: {len(all_states)}')
        print(f'  - 落盘卡片素材数: {saved_cards_count}')
        print(f'  - 缺失截图素材数: {len(missing_card_assets)}')
        print(f'  - 数据保存位置: {raw_player_dir}')
        print(f'=======================================================\n')

        return PlayerDataSet(
            player_id=player_id,
            profile=profile,
            operators=all_states,
            capture_metadata=session.to_summary()
        )

    def replay_from_pages(
        self,
        pages_dir: Path,
        player_id: str = 'P_REPLAY',
        output_dir: Optional[Path] = None,
        debug: bool = False
    ) -> Tuple[Dict[str, OperatorState], List[CardProvenance]]:
        pages = sorted(list(pages_dir.glob('*.png')))
        if not pages:
            print(f'[Replay] 在 {pages_dir} 中未找到任何 .png 页面')
            return {}, []

        scan_id = f'replay_{int(time.time())}_{player_id}'
        out_root = output_dir or (pages_dir.parent)
        cards_raw_dir = out_root / 'cards_raw'
        meta_dir = out_root / 'card_metadata'
        cards_raw_dir.mkdir(parents=True, exist_ok=True)
        meta_dir.mkdir(parents=True, exist_ok=True)

        all_candidates: Dict[str, List[CardCropCandidate]] = {}
        all_states: Dict[str, OperatorState] = {}

        for p_idx, p_file in enumerate(pages, start=1):
            frame = cv2.imdecode(np.fromfile(str(p_file), dtype=np.uint8), cv2.IMREAD_COLOR)
            if frame is None:
                continue

            page_states, page_candidates = self.analyzer.analyze_page(
                frame, page_index=p_idx, source_page_name=p_file.name
            )

            for st in page_states:
                if st.char_id not in all_states:
                    all_states[st.char_id] = st
                else:
                    if all_states[st.char_id].level == 1 and st.level > 1:
                        all_states[st.char_id].level = st.level

            for cand in page_candidates:
                if cand.crop_image is not None and not cand.is_edge:
                    all_candidates.setdefault(cand.char_id, []).append(cand)

        provenances: List[CardProvenance] = []
        for char_id, op in all_states.items():
            cands = all_candidates.get(char_id, [])
            if not cands:
                continue

            best_cand = max(cands, key=lambda c: c.quality_score)
            card_png_path = cards_raw_dir / f'{char_id}.png'
            cv2.imencode('.png', best_cand.crop_image)[1].tofile(str(card_png_path))

            prov = CardProvenance(
                char_id=char_id,
                name=op.name,
                scan_id=scan_id,
                player_id=player_id,
                source_page=best_cand.source_page,
                page_index=best_cand.page_index,
                card_index=best_cand.card_index,
                roi=best_cand.roi.to_list(),
                capture_timestamp=datetime.datetime.now().isoformat(),
                candidate_count=len(cands),
                selected_reason=f'best_quality_score_{best_cand.quality_score:.2f}'
            )
            with open(meta_dir / f'{char_id}.json', 'w', encoding='utf-8') as f:
                json.dump(prov.to_dict(), f, ensure_ascii=False, indent=2)

            provenances.append(prov)

        with open(out_root / 'operators.json', 'w', encoding='utf-8') as f:
            json.dump([op.to_dict() for op in all_states.values()], f, ensure_ascii=False, indent=2)

        return all_states, provenances
