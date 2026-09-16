"""
直接驱动 MAA 原生 MaaCore 运行完整的 OperBox 仓库采集与识别
并将产出的干员培养状态与卡片切片整理归档至 data/raw/P1/
"""

import sys
import os
import json
import time
import shutil
import glob
from pathlib import Path
from datetime import datetime
import cv2
import numpy as np

# 导入 MAA 原生 Python 绑定
sys.path.insert(0, r"E:\Maa\Python")
from asst.asst import Asst
from asst.utils import Message

# 导入本项目核心模型与分析器
from arknightsclip.config import load_config
from arknightsclip.registry.operator_registry import OperatorRegistry
from arknightsclip.models.operator import OperatorState
from arknightsclip.maa.operbox_analyzer import OperBoxAnalyzer

class MaaDirectCollector:
    def __init__(self):
        self.config = load_config()
        self.registry = OperatorRegistry(self.config.resolve_path("src/arknightsclip/registry/operator_registry.json"))
        self.analyzer = OperBoxAnalyzer(self.config, self.registry)
        self.operbox_packets = []
        self.adb_path = r"C:\Program Files\Netease\MuMuPlayer-12.0\nx_main\adb.exe"
        self.adb_device = "127.0.0.1:16384"
        self.maa_dir = Path(r"E:\Maa")

    def run(self, player_id: str = "P1", max_wait_seconds: int = 120):
        print(f"=== 开始使用 MAA 原生引擎采集玩家 [{player_id}] 仓库数据 ===")

        # 1. 记录运行前 debug/oper 目录中的已有图片，以便筛选本次产生的新帧
        debug_oper_dir = self.maa_dir / "debug" / "oper"
        existing_debug_images = set(debug_oper_dir.glob("*_raw.png")) if debug_oper_dir.exists() else set()
        start_time = time.time()

        # 2. 初始化并加载 MaaCore
        print(f"[MAA] 正在加载 MaaCore 动态链接库: {self.maa_dir}")
        loaded = Asst.load(self.maa_dir)
        print(f"[MAA] Asst.load 状态: {loaded}")

        @Asst.CallBackType
        def maa_callback(msg, details, arg):
            m = Message(msg)
            d = json.loads(details.decode("utf-8")) if details else {}
            if "OperBoxInfo" in str(d):
                print(f"[MAA Callback] 接收到 OperBoxInfo 数据包 (len={len(str(d))})")
                self.operbox_packets.append(d)
            elif m == Message.TaskChainCompleted:
                print(f"[MAA Callback] 任务链完成: {d}")
            elif m == Message.SubTaskError:
                print(f"[MAA Callback] 子任务异常: {d}")

        asst = Asst(callback=maa_callback)

        # 3. 连接模拟器
        print(f"[MAA] 正在连接设备: {self.adb_device} ...")
        connected = asst.connect(self.adb_path, self.adb_device)
        if not connected:
            print(f"[MAA] 尝试连接 127.0.0.1:5555 ...")
            connected = asst.connect(self.adb_path, "127.0.0.1:5555")
        if not connected:
            raise RuntimeError("无法通过 ADB 连接到模拟器，请确认模拟器已开启！")
        print("[MAA] 模拟器连接成功！")

        # 4. 追加 OperBox 任务并启动
        print("[MAA] 正在启动 OperBox 识别任务链...")
        asst.append_task("OperBox")
        asst.start()

        # 等待完成
        while asst.running() and (time.time() - start_time < max_wait_seconds):
            time.sleep(1)

        if asst.running():
            print("[MAA] 扫描超时，强制终止任务...")
            asst.stop()
        else:
            print("[MAA] OperBox 任务链自然完成！")

        # 5. 整理培养状态数据 (Path B)
        raw_player_dir = self.config.get_raw_player_dir(player_id)
        raw_player_dir.mkdir(parents=True, exist_ok=True)

        # 提取最终 OperBoxInfo
        final_packet = None
        for p in reversed(self.operbox_packets):
            d = p.get("details", {})
            if "all_opers" in d or "own_opers" in d:
                final_packet = d
                break

        if not final_packet:
            raise RuntimeError("未捕获到有效的 OperBoxInfo 回调数据！")

        all_opers = final_packet.get("all_opers", [])
        own_opers = final_packet.get("own_opers", [])
        print(f"[MAA] 识别总干员数: {len(all_opers)}, 拥有干员数: {len(own_opers)}")

        # 规范化各干员状态
        normalized_states = []
        for item in all_opers:
            raw_id = item.get("id", "")
            raw_name = item.get("name", "")
            reg_entry = self.registry.resolve(raw_id) or self.registry.resolve(raw_name)

            cid = reg_entry.char_id if reg_entry else raw_id
            cname = reg_entry.canonical_name_zh if reg_entry else raw_name
            rarity = reg_entry.rarity if reg_entry else item.get("rarity", 6)

            state = OperatorState(
                char_id=cid,
                name=cname,
                own=item.get("own", False),
                elite=item.get("elite", 0),
                level=item.get("level", 1),
                potential=item.get("potential", 1),
                rarity=rarity,
            )
            normalized_states.append(state)

        # 保存 operators.json
        operators_json_path = raw_player_dir / "operators.json"
        with open(operators_json_path, "w", encoding="utf-8") as f:
            json.dump([s.to_dict() for s in normalized_states], f, ensure_ascii=False, indent=2)
        print(f"[Output] 干员培养状态已成功写入: {operators_json_path}")

        # 保存 profile.json
        profile_json_path = raw_player_dir / "profile.json"
        profile_data = {
            "id": player_id,
            "display_name": "暮春之阳",
            "doctor_level": 120,
            "uid": "864054719",
            "assistant": "char_1035_wisdel",
            "updated_at": datetime.now().isoformat(),
        }
        with open(profile_json_path, "w", encoding="utf-8") as f:
            json.dump(profile_data, f, ensure_ascii=False, indent=2)
        print(f"[Output] 玩家资料已成功写入: {profile_json_path}")

        # 6. 处理卡片素材 (Path A: Screenshot Crops)
        operbox_dir = raw_player_dir / "operbox"
        pages_dir = operbox_dir / "pages"
        cards_raw_dir = operbox_dir / "cards_raw"
        pages_dir.mkdir(parents=True, exist_ok=True)
        cards_raw_dir.mkdir(parents=True, exist_ok=True)

        # 收集本次运行生成的新 raw 截图
        new_debug_images = []
        if debug_oper_dir.exists():
            for p in sorted(debug_oper_dir.glob("*_raw.png")):
                if p not in existing_debug_images and p.stat().st_mtime >= start_time - 2:
                    new_debug_images.append(p)

        print(f"[MAA] 捕获到本次运行生成的原始页面帧: {len(new_debug_images)} 张")

        # 复制全页到 data/raw/P1/operbox/pages/
        all_candidates = []
        for idx, img_path in enumerate(new_debug_images):
            dest_page = pages_dir / f"page_{idx+1:04d}.png"
            shutil.copyfile(img_path, dest_page)

            # 读取该帧执行切片分析
            frame = cv2.imdecode(np.fromfile(str(dest_page), dtype=np.uint8), cv2.IMREAD_COLOR)
            if frame is not None:
                candidates = self.analyzer.analyze_page(frame, page_id=idx+1)
                all_candidates.extend(candidates)

        # 多候选按 quality_score 选优与去重
        best_candidates = self.analyzer.select_best_candidates(all_candidates)
        print(f"[MAA] 从 {len(all_candidates)} 个候选切片中筛选出最优卡片素材: {len(best_candidates)} 张")

        # 写入卡片切片素材与 Provenance
        for cid, cand in best_candidates.items():
            card_png = cards_raw_dir / f"{cid}.png"
            card_json = cards_raw_dir / f"{cid}.json"
            cv2.imencode(".png", cand.crop)[1].tofile(str(card_png))
            with open(card_json, "w", encoding="utf-8") as f:
                json.dump(cand.provenance.to_dict(), f, ensure_ascii=False, indent=2)

        print(f"[Output] 卡片切片素材已成功写入: {cards_raw_dir}")
        print(f"=== 玩家 [{player_id}] 仓库数据全流程采集与整理完成！ ===")

if __name__ == "__main__":
    collector = MaaDirectCollector()
    collector.run("P1")
