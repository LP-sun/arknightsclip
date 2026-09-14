"""
明日方舟 - 基于 MAA 的仓库干员列表全自动截取与识别管线 (maa_game_pipeline.py)
核心功能：
1. 自动连接本地安卓模拟器 (MuMu Player 12 / 雷电 / 夜神 / 原生 ADB)
2. 自动化截取与翻页抓取游戏内【干员列表】全量卡片素材
3. 基于 MAA (MaaAssistantArknights) 视觉算法进行干员、精英度、潜能、等级全自动提取
4. 自动生成标准 统计_maa_captured.xlsx
5. 串联驱动 PSD 分层批量渲染与 DaVinci Resolve 自动编排
"""

import os
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'
import sys
import time
import json
import subprocess
import numpy as np
import cv2
from PIL import Image
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Tuple

@dataclass
class CapturedOperator:
    name: str
    elite: int       # 0, 1, 2
    level: int       # 1 ~ 90
    potential: int   # 1 ~ 6
    rarity: int = 6  # 默认 6 星
    bbox: List[int] = None
    page: int = 1

class MaaAdbClient:
    """ADB 通信与模拟器控制客户端"""
    def __init__(self, adb_path: Optional[str] = None, target_device: str = "127.0.0.1:16384"):
        self.target_device = target_device
        self.adb_path = adb_path or self._find_adb()
        self.connected = False
        self._ensure_connection()

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

    def _run_adb(self, args: List[str], timeout: int = 10) -> subprocess.CompletedProcess:
        cmd = [self.adb_path, '-s', self.target_device] + args
        return subprocess.run(cmd, capture_output=True, timeout=timeout)

    def _ensure_connection(self):
        try:
            connect_cmd = [self.adb_path, 'connect', self.target_device]
            res = subprocess.run(connect_cmd, capture_output=True, text=True, timeout=5)
            devices_res = subprocess.run([self.adb_path, 'devices'], capture_output=True, text=True, timeout=5)
            if self.target_device in devices_res.stdout:
                self.connected = True
                print(f"[ADB] 成功连接设备: {self.target_device}")
            else:
                print(f"[ADB] 连接返回: {res.stdout.strip()}")
        except Exception as e:
            print(f"[ADB] 尝试连接失败: {e}")

    def screencap(self) -> Optional[np.ndarray]:
        """高速内存截图，返回 BGR ndarray (1920x1080)"""
        try:
            self._ensure_connection()
            cmd = [self.adb_path, '-s', self.target_device, 'exec-out', 'screencap', '-p']
            res = subprocess.run(cmd, capture_output=True, timeout=8)
            if res.returncode == 0 and len(res.stdout) > 1000:
                img_array = np.frombuffer(res.stdout, dtype=np.uint8)
                img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
                return img
        except Exception as e:
            print(f"[ADB] 截图失败: {e}")
        return None

    def tap(self, x: int, y: int):
        self._run_adb(['shell', 'input', 'tap', str(x), str(y)])

    def swipe(self, x1: int, y1: int, x2: int, y2: int, duration_ms: int = 600):
        self._run_adb(['shell', 'input', 'swipe', str(x1), str(y1), str(x2), str(y2), str(duration_ms)])

class MaaOperBoxCollector:
    """基于 MAA 规范的干员仓库抓取器"""
    def __init__(self, adb_client: MaaAdbClient, output_dir: str = r"E:\明日方舟报菜名\captured"):
        self.adb = adb_client
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        
        # 加载 MAA 模板
        from maa_operator_extractor import MaaOperatorRecognizer
        self.recognizer = MaaOperatorRecognizer()

    def capture_and_harvest(self, max_pages: int = 5) -> List[CapturedOperator]:
        """
        自动翻页遍历游戏内的干员列表并抓取素材
        """
        all_operators: Dict[str, CapturedOperator] = {}
        print(f"\n=======================================================")
        print(f" 开始通过 MAA 视觉协议从游戏中抓取干员仓库数据 (最大翻页: {max_pages})")
        print(f"=======================================================")

        for page in range(1, max_pages + 1):
            print(f"\n[Page {page:02d}] 正在获取游戏截屏...")
            frame = self.adb.screencap()
            if frame is None:
                print(f"[Page {page:02d}] 截图失败，跳过")
                break

            # 保存当前页原始素材
            save_path = os.path.join(self.output_dir, f"operbox_page_{page:02d}.png")
            cv2.imencode('.png', frame)[1].tofile(save_path)
            print(f"[Page {page:02d}] 原始素材已保存至: {save_path}")

            # 识别当前画面的干员卡牌 (MAA 算法)
            page_opers = self._extract_operators_from_frame(frame, page)
            new_found = 0
            for op in page_opers:
                if op.name and op.name not in all_operators:
                    all_operators[op.name] = op
                    new_found += 1
                    print(f"   -> 发现新干员: {op.name:8s} | 精{op.elite} | Lv.{op.level:2d} | 潜{op.potential}")

            print(f"[Page {page:02d}] 本页新增 {new_found} 位干员，累计抓取: {len(all_operators)} 位")

            if new_found == 0 and page > 1:
                print(f"[Page {page:02d}] 未检测到新干员，判定已到达干员列表末端。")
                break

            # 模拟 MAA 的 OperBoxSlowlySwipeToTheRight 翻页手势
            # 从右侧 1550 匀速滑动至左侧 350
            print(f"[Page {page:02d}] 执行向右平滑翻页 (1550, 540 -> 350, 540)...")
            self.adb.swipe(1550, 540, 350, 540, 800)
            time.sleep(1.5) # 等待列表滑动惯性停止

        results = list(all_operators.values())
        print(f"\n干员仓库抓取完成！共捕获 {len(results)} 位有效干员。")
        self._export_results(results)
        return results

    def _extract_operators_from_frame(self, frame: np.ndarray, page: int) -> List[CapturedOperator]:
        """
        利用 MAA 锚点与相对几何偏移提取卡面信息
        """
        h, w = frame.shape[:2]
        # 在 Arknights 1080P 中，干员列表大致分为上下两排
        # 上排职业标 y ~ 117, 下排职业标 y ~ 591
        # 此处使用 MAA 模板匹配或网格扫描
        detected = []

        # 针对当前帧执行文本与练度识别
        try:
            import easyocr
            os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'
            reader = easyocr.Reader(['ch_sim', 'en'], gpu=False)
            ocr_results = reader.readtext(frame)

            # 筛选可能是干员名字的区域
            for bbox, text, conf in ocr_results:
                clean_name = text.strip()
                # 过滤明显不是干员名的短语
                if clean_name in ['今日配给', '加急许可', '等级', '职业', '稀有度', '信赖度', '升序', '降序', '筛选']:
                    continue
                if len(clean_name) >= 1 and conf > 0.4:
                    # 估算卡片 ROI
                    pts = np.array(bbox, dtype=np.int32)
                    bx, by, bw, bh = cv2.boundingRect(pts)
                    # 扩展至卡片整体
                    card_x = max(0, bx - 20)
                    card_y = max(0, by - 240)
                    card_w = min(w - card_x, 200)
                    card_h = min(h - card_y, 320)

                    card_roi = frame[card_y:card_y+card_h, card_x:card_x+card_w]
                    if card_roi.size > 0:
                        stats = self.recognizer.analyze_operator_card(card_roi)
                        detected.append(CapturedOperator(
                            name=clean_name,
                            elite=stats.elite,
                            level=stats.level,
                            potential=stats.potential,
                            bbox=[card_x, card_y, card_w, card_h],
                            page=page
                        ))
        except Exception as e:
            print(f"OCR 提取出错: {e}")

        return detected

    def _export_results(self, operators: List[CapturedOperator]):
        """导出为结构化 JSON 与 Excel"""
        # 1. 导出 JSON
        json_path = os.path.join(self.output_dir, "maa_harvested_operators.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump([asdict(o) for o in operators], f, ensure_ascii=False, indent=2)
        print(f"[Export] 数据清单已写入: {json_path}")

        # 2. 导出为标准 统计_maa_captured.xlsx
        from maa_operator_extractor import MaaOperatorRecognizer, OperatorStats
        rec = MaaOperatorRecognizer()
        player_dict = {
            "当前游戏捕获": {
                op.name: OperatorStats(
                    name=op.name,
                    level=op.level,
                    elite=op.elite,
                    potential=op.potential,
                    own=True
                ) for op in operators
            }
        }
        excel_path = os.path.join(r"E:\明日方舟报菜名", "统计_maa_captured.xlsx")
        rec.batch_export_to_excel(player_dict, excel_path)
        print(f"[Export] 标准练度表已导出: {excel_path}")

if __name__ == '__main__':
    adb = MaaAdbClient()
    collector = MaaOperBoxCollector(adb)
    collector.capture_and_harvest(max_pages=2)
