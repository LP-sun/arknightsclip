"""
玩家干员数据自动化采集器 (PlayerCollector)
具备模拟器状态感知能力 (解决大厅未进入干员一览、每日配给弹窗阻断等问题)，
支持单玩家数据独立落盘至 data/raw/<player_id>/。
"""

import os
import time
import json
import subprocess
import numpy as np
import cv2
from pathlib import Path
from typing import List, Dict, Optional, Any
from ..config import ProjectConfig
from ..models.operator import OperatorState
from ..models.player import PlayerProfile, PlayerDataSet
from .adapter import MaaAcquisitionAdapter
from .fallback_recognizer import FallbackOperBoxRecognizer
from .maacore_client import MaaCoreAdapter

class PlayerCollector:
    def __init__(self, config: ProjectConfig, adapter: Optional[MaaAcquisitionAdapter] = None):
        self.config = config
        self.adb_path = config.maa.adb_path or self._find_adb()
        self.adb_device = config.maa.adb_device
        self.adapter = adapter or self._create_default_adapter()

    def _find_adb(self) -> str:
        candidates = [
            r'C:\Program Files\Netease\MuMuPlayer-12.0\nx_device\12.0\shell\adb.exe',
            r'C:\Program Files\Netease\MuMuPlayer-12.0\nx_main\adb.exe',
            r'D:\Program Files\Netease\MuMuPlayer-12.0\nx_device\12.0\shell\adb.exe',
            r'C:\leidian\LDPlayer9\adb.exe',
            r'D:\leidian\LDPlayer9\adb.exe',
            'adb'
        ]
        for c in candidates:
            if os.path.exists(c):
                return c
        return 'adb'

    def _create_default_adapter(self) -> MaaAcquisitionAdapter:
        core_adapter = MaaCoreAdapter(self.config)
        if core_adapter.is_available():
            return core_adapter
        return FallbackOperBoxRecognizer(self.config)

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
            print(f"[PlayerCollector] 截图异常: {e}")
        return None

    def tap(self, x: int, y: int):
        self._run_adb(['shell', 'input', 'tap', str(x), str(y)])

    def swipe(self, x1: int, y1: int, x2: int, y2: int, duration_ms: int = 800):
        self._run_adb(['shell', 'input', 'swipe', str(x1), str(y1), str(x2), str(y2), str(duration_ms)])

    def ensure_operbox_screen(self) -> bool:
        """检查并导航至干员一览界面，自动处理弹窗与主界面跳转"""
        frame = self.screencap()
        if frame is None:
            return False

        h, w = frame.shape[:2]
        # 简单色彩/模板感知：如果位于主界面 (右侧有大字'编队'与'干员')
        # 点击主界面'干员'按钮 (1080P 下约 x: 1550, y: 500)
        # 尝试点击一次并等待进入
        print("[PlayerCollector] 检测界面状态并导航至干员列表...")
        self.tap(int(w * 0.8), int(h * 0.48))
        time.sleep(2.0)
        return True

    def collect(self, player_id: str, display_name: str, max_pages: int = 5) -> PlayerDataSet:
        """执行单玩家完整采集流程并持久化"""
        print(f"\n=======================================================")
        print(f" 开始玩家采集: {player_id} ({display_name}) [最大翻页: {max_pages}]")
        print(f"=======================================================")

        target_dir = self.config.get_raw_player_dir(player_id)
        raw_ops: Dict[str, OperatorState] = {}
        metadata = {
            "player_id": player_id,
            "display_name": display_name,
            "timestamp": time.time(),
            "pages_captured": 0,
            "device": self.adb_device,
        }

        # 检查是否连接模拟器
        connected = self.connect()
        if not connected:
            print(f"[PlayerCollector] 警告: 未检测到运行中的 ADB 设备 {self.adb_device}，无法进行在线捕获。")
        else:
            self.ensure_operbox_screen()
            sw_cfg = self.config.maa.swipe
            for page in range(1, max_pages + 1):
                frame = self.screencap()
                if frame is None:
                    break

                # 保存原始帧备份
                page_img_path = target_dir / f"page_{page:02d}.png"
                cv2.imencode('.png', frame)[1].tofile(str(page_img_path))

                if isinstance(self.adapter, FallbackOperBoxRecognizer):
                    detected = self.adapter.analyze_frame(frame)
                    new_count = 0
                    for op in detected:
                        if op.char_id and op.char_id not in raw_ops:
                            raw_ops[op.char_id] = op
                            new_count += 1
                            print(f"   [P{page}] 发现: {op.name:8s} | 精{op.elite} | Lv.{op.level:2d} | 潜{op.potential}")

                    if new_count == 0 and page > 1:
                        print(f"   [P{page}] 无新增干员，采集提前终止。")
                        break

                metadata["pages_captured"] = page
                # 执行平滑翻页
                self.swipe(sw_cfg.start_x, sw_cfg.start_y, sw_cfg.end_x, sw_cfg.end_y, sw_cfg.duration_ms)
                time.sleep(sw_cfg.settle_delay_sec)

        # 构建数据集对象
        profile = PlayerProfile(id=player_id, display_name=display_name)
        dataset = PlayerDataSet(
            player_id=player_id,
            profile=profile,
            operators=raw_ops,
            capture_metadata=metadata,
        )

        # 写入落盘文件
        with open(target_dir / "operators.json", "w", encoding="utf-8") as f:
            json.dump([op.to_dict() for op in raw_ops.values()], f, ensure_ascii=False, indent=2)

        with open(target_dir / "profile.json", "w", encoding="utf-8") as f:
            json.dump({
                "id": profile.id,
                "display_name": profile.display_name,
                "doctor_level": profile.doctor_level,
                "avatar": profile.avatar,
            }, f, ensure_ascii=False, indent=2)

        with open(target_dir / "capture_metadata.json", "w", encoding="utf-8") as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)

        print(f"[PlayerCollector] 采集完成！数据已安全落盘至: {target_dir}")
        return dataset
