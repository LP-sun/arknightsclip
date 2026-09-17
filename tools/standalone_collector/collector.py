#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
明日方舟干员仓库独立采集工具 (Arknights Operbox Standalone Collector)
===================================================================
特性：
1. 零第三方依赖：纯 Python 3.6+ 标准库实现，无需安装 cv2 / torch / easyocr 等。
2. 全局 UTF-8 运行支持：自适应 Windows 控制台代码页，解决中文字符编码问题。
3. 自动探测 ADB：内置主流模拟器（MuMu 12、雷电 9、夜神、逍遥等）默认路径。
4. 智能端口连接：自动扫描 16384、5555、7555 等常见模拟器端口。
5. 屏幕自适应：动态读取分辨率计算滑动手势，适配 16:9 与 21:9 超宽屏。
6. 智能停止检测：MD5 比对判定仓库滑动到底部，自动终止并打包。
7. 一键压缩归档：自动打包为 ZIP 文件并打开资源管理器高亮文件，便于发送。
"""

import os
import sys
import io

# 强制 UTF-8 环境变量
os.environ["PYTHONIOENCODING"] = "utf-8"
os.environ["PYTHONUTF8"] = "1"

# Windows 终端强制切换为 UTF-8 代码页并包装标准输入输出流
if sys.platform == "win32":
    try:
        import ctypes
        ctypes.windll.kernel32.SetConsoleOutputCP(65001)
        ctypes.windll.kernel32.SetConsoleCP(65001)
    except Exception:
        pass

    try:
        if hasattr(sys.stdout, "buffer"):
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
        if hasattr(sys.stderr, "buffer"):
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
        if hasattr(sys.stdin, "buffer"):
            sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding="utf-8", errors="replace")
    except Exception:
        pass

import time
import json
import hashlib
import zipfile
import argparse
import subprocess
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Tuple, Dict, Any

BANNER = r"""
==================================================================
           明日方舟干员仓库数据采集工具 (Standalone Collector)     
==================================================================
【准备工作】
 1. 打开安卓模拟器并启动《明日方舟》。
 2. 进入游戏【干员】仓库主界面。
 3. 右上角排序请切换为【稀有度】。
 4. 确保列表已滑动至【最左侧起始页】（6星干员排在最前面）。
==================================================================
"""

# 常见模拟器 ADB 可执行文件搜索路径
COMMON_ADB_PATHS = [
    # 当前目录及子目录
    r".\adb.exe",
    r".\platform-tools\adb.exe",
    r".\tools\adb.exe",
    # MuMu 模拟器 12
    r"C:\Program Files\Netease\MuMuPlayer-12.0\nx_device\12.0\shell\adb.exe",
    r"C:\Program Files\Netease\MuMuPlayer-12.0\nx_main\adb.exe",
    r"D:\Program Files\Netease\MuMuPlayer-12.0\nx_device\12.0\shell\adb.exe",
    r"D:\Program Files\Netease\MuMuPlayer-12.0\nx_main\adb.exe",
    # 雷电模拟器 9 / 5 / 4
    r"C:\leidian\LDPlayer9\adb.exe",
    r"D:\leidian\LDPlayer9\adb.exe",
    r"E:\leidian\LDPlayer9\adb.exe",
    r"C:\Program Files\leidian\LDPlayer9\adb.exe",
    r"D:\Program Files\leidian\LDPlayer9\adb.exe",
    # 夜神模拟器
    r"C:\Program Files\Nox\bin\adb.exe",
    r"D:\Program Files\Nox\bin\adb.exe",
    r"C:\Program Files (x86)\Nox\bin\adb.exe",
    r"D:\Program Files (x86)\Nox\bin\adb.exe",
    # 逍遥模拟器
    r"C:\Program Files\Microvirt\MEmu\adb.exe",
    r"D:\Program Files\Microvirt\MEmu\adb.exe",
]

# 常见模拟器连接端口
COMMON_PORTS = [
    "127.0.0.1:16384",  # MuMu 12 主端口
    "127.0.0.1:16385",  # MuMu 12 多开 1
    "127.0.0.1:5555",   # 雷电 / MuMu 共享端口
    "127.0.0.1:7555",   # MuMu 6
    "127.0.0.1:62001",  # 夜神
    "127.0.0.1:21503",  # 逍遥
    "127.0.0.1:5554",   # 蓝叠
]


class StandaloneCollector:
    def __init__(self, adb_path: Optional[str] = None, device_addr: Optional[str] = None):
        self.adb_path = adb_path or self._find_adb()
        self.device_addr = device_addr
        self.screen_w = 1920
        self.screen_h = 1080

    def _find_adb(self) -> str:
        # 1. 检查 PATH 中的 adb
        try:
            res = subprocess.run(
                ["adb", "version"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="ignore",
                timeout=3
            )
            if res.returncode == 0:
                return "adb"
        except Exception:
            pass

        # 2. 检查常见安装位置
        for p in COMMON_ADB_PATHS:
            p_obj = Path(p).resolve()
            if p_obj.is_file():
                return str(p_obj)

        return "adb"

    def _run_adb(self, args: List[str], timeout: int = 15, binary: bool = False) -> subprocess.CompletedProcess:
        cmd = [self.adb_path]
        if self.device_addr:
            cmd.extend(["-s", self.device_addr])
        cmd.extend(args)
        return subprocess.run(cmd, capture_output=True, timeout=timeout)

    def detect_and_connect(self) -> bool:
        print(f"[1/4] 检查 ADB 工具: {self.adb_path}")
        try:
            ver = subprocess.run(
                [self.adb_path, "version"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="ignore",
                timeout=5
            )
            if ver.returncode != 0:
                print(f"[错误] 无法执行 ADB: {self.adb_path}")
                return False
            first_line = ver.stdout.splitlines()[0] if ver.stdout.splitlines() else "OK"
            print(f"      ADB 就绪: {first_line}")
        except Exception as e:
            print(f"[错误] 启动 ADB 失败: {e}")
            return False

        # 检查是否已指定设备
        if self.device_addr:
            print(f"[2/4] 正在连接指定设备: {self.device_addr} ...")
            self._run_adb(["connect", self.device_addr], timeout=5)
            devices = self.get_online_devices()
            if self.device_addr in devices:
                print(f"      [OK] 连接成功: {self.device_addr}")
                return True
            print(f"      [失败] 无法连接到设备 {self.device_addr}")

        # 自动探测已在线的设备
        online = self.get_online_devices()
        if online:
            self.device_addr = online[0]
            print(f"[2/4] 发现已连接设备: {self.device_addr}")
            return True

        # 尝试扫描常见端口
        print("[2/4] 未发现活动设备，正在自动探测模拟器端口...")
        for port in COMMON_PORTS:
            print(f"      尝试连接 {port} ...", end="", flush=True)
            subprocess.run([self.adb_path, "connect", port], capture_output=True, timeout=3)
            online = self.get_online_devices()
            if port in online:
                self.device_addr = port
                print(" [成功]")
                return True
            print(" [未发现]")

        print("\n[提示] 未能自动识别到模拟器设备。")
        manual = input("请输入模拟器 ADB 地址 (例如 127.0.0.1:16384，直接回车退出): ").strip()
        if manual:
            subprocess.run([self.adb_path, "connect", manual], capture_output=True, timeout=5)
            online = self.get_online_devices()
            if manual in online or any(manual in d for d in online):
                self.device_addr = manual
                print(f"      [OK] 手动连接成功: {self.device_addr}")
                return True

        return False

    def get_online_devices(self) -> List[str]:
        try:
            res = subprocess.run(
                [self.adb_path, "devices"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="ignore",
                timeout=5
            )
            devices = []
            for line in res.stdout.splitlines()[1:]:
                line = line.strip()
                if not line:
                    continue
                parts = line.split()
                if len(parts) >= 2 and parts[1] == "device":
                    devices.append(parts[0])
            return devices
        except Exception:
            return []

    def update_screen_size(self) -> Tuple[int, int]:
        try:
            res = self._run_adb(["shell", "wm", "size"], timeout=5)
            text = res.stdout.decode("utf-8", errors="ignore")
            for line in text.splitlines():
                if "size:" in line:
                    parts = line.split(":")[-1].strip().split("x")
                    if len(parts) == 2:
                        self.screen_w = int(parts[0])
                        self.screen_h = int(parts[1])
                        break
        except Exception as e:
            print(f"[警告] 读取屏幕分辨率失败，使用默认 1920x1080: {e}")
        return self.screen_w, self.screen_h

    def screencap(self) -> Optional[bytes]:
        """抓取当前屏幕原始 PNG 字节流"""
        try:
            res = self._run_adb(["exec-out", "screencap", "-p"], timeout=10, binary=True)
            if res.returncode == 0 and len(res.stdout) > 1000:
                if res.stdout[:8] == b"\x89PNG\r\n\x1a\n":
                    return res.stdout
        except Exception as e:
            print(f"[警告] 截图异常: {e}")
        return None

    def swipe_next_page(self, settle_sec: float = 1.3):
        """按分辨率动态计算手势滑动到下一页"""
        start_x = int(self.screen_w * 0.82)
        end_x = int(self.screen_w * 0.20)
        y = int(self.screen_h * 0.50)
        duration_ms = 850

        self._run_adb([
            "shell", "input", "swipe",
            str(start_x), str(y), str(end_x), str(y), str(duration_ms)
        ])
        time.sleep(settle_sec)

    def run_collection(
        self,
        player_name: str,
        max_pages: int = 24,
        output_base_dir: str = "./captures"
    ) -> Optional[Path]:
        w, h = self.update_screen_size()
        aspect = w / max(1, h)
        print(f"[3/4] 模拟器屏幕参数: {w}x{h} (宽高比: {aspect:.2f}:1)")
        if aspect > 2.0:
            print("      [提示] 检测到带鱼屏/超宽屏布局，已适配手势滑动与后续中心裁切。")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_player = "".join(c for c in player_name if c.isalnum() or c in ("-", "_")).strip() or "doctor"
        session_folder_name = f"{safe_player}_{timestamp}"
        out_dir = Path(output_base_dir).resolve() / session_folder_name
        pages_dir = out_dir / "pages"
        pages_dir.mkdir(parents=True, exist_ok=True)

        print(f"[4/4] 开始自动捕获 (最大页数: {max_pages})")
        print(f"      输出目录: {out_dir}")
        print("------------------------------------------------------------------")

        captured_hashes: List[str] = []
        captured_files: List[Path] = []

        for p_idx in range(1, max_pages + 1):
            page_filename = f"page_{p_idx:04d}.png"
            page_path = pages_dir / page_filename

            print(f" -> 正在捕获第 [{p_idx:02d}/{max_pages}] 页...", end="", flush=True)
            png_bytes = self.screencap()
            if not png_bytes:
                print(" [截屏失败，重试一次...]", end="", flush=True)
                time.sleep(1.0)
                png_bytes = self.screencap()
                if not png_bytes:
                    print(" [仍然失败，终止扫描]")
                    break

            # 计算图像散列
            cur_hash = hashlib.md5(png_bytes).hexdigest()

            # 保存文件
            with open(page_path, "wb") as f:
                f.write(png_bytes)

            size_kb = len(png_bytes) / 1024.0
            print(f" [已保存: {size_kb:.1f} KB, MD5: {cur_hash[:8]}]")

            # 检测是否滑动到了末页（连续两页内容完全一致）
            if captured_hashes and cur_hash == captured_hashes[-1]:
                print(f"      [完成] 检测到第 {p_idx} 页与前一页完全相同，已到达干员仓库末端！")
                try:
                    page_path.unlink()
                except Exception:
                    pass
                break

            captured_hashes.append(cur_hash)
            captured_files.append(page_path)

            if p_idx < max_pages:
                self.swipe_next_page()

        total_pages = len(captured_files)
        if total_pages == 0:
            print("[错误] 未能成功抓取到任何有效页面截图！")
            return None

        # 写入元数据
        metadata = {
            "player_name": player_name,
            "session_id": session_folder_name,
            "timestamp": datetime.now().isoformat(),
            "device_address": self.device_addr,
            "screen_width": w,
            "screen_height": h,
            "total_pages": total_pages,
            "pages": [
                {"page_index": i + 1, "filename": p.name, "md5": hsh}
                for i, (p, hsh) in enumerate(zip(captured_files, captured_hashes[:total_pages]))
            ]
        }
        with open(out_dir / "manifest.json", "w", encoding="utf-8") as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)

        # 自动打包 ZIP
        zip_path = Path(output_base_dir).resolve() / f"Arknights_Operbox_{session_folder_name}.zip"
        print("------------------------------------------------------------------")
        print(f"正在打包采集数据至 ZIP 压缩包...")
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for root, _, files in os.walk(out_dir):
                for file in files:
                    full_p = Path(root) / file
                    rel_p = full_p.relative_to(out_dir)
                    zf.write(full_p, arcname=str(rel_p))

        print(f"[OK] 采集与打包完成！")
        print(f"  - 抓取总页数: {total_pages} 页")
        print(f"  - 原始截图目录: {out_dir}")
        print(f"  - 导出压缩包: {zip_path}")
        print("==================================================================")
        print("【发送指引】")
        print(f"请将压缩包【{zip_path.name}】直接发送给项目维护者即可！")
        print("==================================================================")

        if sys.platform == "win32" and zip_path.exists():
            try:
                subprocess.Popen(f'explorer.exe /select,"{zip_path}"')
            except Exception:
                pass

        return zip_path


def main():
    print(BANNER)
    parser = argparse.ArgumentParser(description="明日方舟干员仓库独立免配置采集脚本")
    parser.add_argument("--name", default="", help="玩家昵称/代号（例如 wyf、P2）")
    parser.add_argument("--device", default="", help="ADB 设备地址（例如 127.0.0.1:16384）")
    parser.add_argument("--adb", default="", help="自定义 adb.exe 路径")
    # 146 位全六星基准需求 ~18 页，加 33% 安全裕度设定为 24 页，MD5 到达末尾会自动提前终止
    parser.add_argument("--pages", type=int, default=24, help="最大翻页捕获数（基于146全六星+安全冗余，默认 24）")
    parser.add_argument("--output", default="./captures", help="数据导出保存目录")
    args = parser.parse_args()

    player_name = args.name.strip()
    if not player_name:
        try:
            player_name = input("请输入您的昵称或玩家代号 (例如: 张三 / P2，回车默认 Player): ").strip()
        except EOFError:
            player_name = "Player"
        if not player_name:
            player_name = "Player"

    collector = StandaloneCollector(
        adb_path=args.adb.strip() or None,
        device_addr=args.device.strip() or None
    )

    if not collector.detect_and_connect():
        print("[错误] 未能连接到模拟器，程序退出。请确认模拟器已开启并在设置中开启 ADB 调试。")
        input("按 Enter 键退出...")
        sys.exit(1)

    collector.run_collection(
        player_name=player_name,
        max_pages=args.pages,
        output_base_dir=args.output
    )

    input("\n采集已完成，按 Enter 键关闭窗口...")


if __name__ == "__main__":
    main()
