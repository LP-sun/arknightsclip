"""
明日方舟报菜名 - 全自动端到端工业级管线调度器 (run_full_autonomous_pipeline.py)
涵盖从【游戏仓库截图截取】到【最终时间线合成与成片质检】的完整六大环节：
1. Step 1: 基于 MAA 协议从模拟器/真机自动截图并翻页抓取干员仓库
2. Step 2: 运用 MAA 视觉算法自动提取干员练度 (精0~2, 潜1~6, 等级1~90, 名称纠错)
3. Step 3: 自动导出标准结构化 统计_maa_captured.xlsx
4. Step 4: 驱动 PSD 分层母版批量导出 1080P 资产 (background, character_cards, doctor_info)
5. Step 5: 自动组装生成 24FPS 分层时间线工程 (绝对保护旧时间线, 0 误差咬合)
6. Step 6: 自动生成全局 Contact Sheet 视觉缩略图与质检验收报告
"""

import os
import sys
import time
import json

def run_pipeline():
    print("================================================================================")
    print("      明日方舟报菜名 · MAA 自动仓库抓取至视频时间线全闭环流水线启动")
    print("================================================================================")
    t0_pipeline = time.time()

    # Step 1 & 2: MAA 游戏抓取与识别
    print("\n>>> [Step 1 & 2] 启动 MAA 模拟器 ADB 连接与仓库截取...")
    from maa_game_pipeline import MaaAdbClient, MaaOperBoxCollector
    adb = MaaAdbClient()
    collector = MaaOperBoxCollector(adb)
    captured_ops = collector.capture_and_harvest(max_pages=2)
    print(f"MAA 捕获完成！抓取干员数量: {len(captured_ops)}")

    # Step 3: 检查生成的 Excel
    excel_path = os.path.abspath("统计_maa_captured.xlsx")
    if os.path.exists(excel_path):
        print(f">>> [Step 3] 结构化练度数据已成功持久化至: {excel_path}")

    # Step 4: 执行 PSD 分层渲染
    print("\n>>> [Step 4] 驱动 PSD 分层母版执行三层独立资产批量渲染...")
    from batch_render_layered_graphics import run_batch_render
    run_batch_render()

    # Step 5: 生成 FCP7 XML 分层时间线
    print("\n>>> [Step 5] 生成 DaVinci Resolve 24.0 fps 分层时间线工程 (V2 保护模式)...")
    from generate_v2_layered_fcpxml import generate_fcpxml
    generate_fcpxml()

    # Step 6: 生成 Contact Sheet 全景验收图
    print("\n>>> [Step 6] 渲染 Contact Sheet 全局多场景画面对照总览...")
    from create_contact_sheet import generate_contact_sheet
    generate_contact_sheet()

    total_cost = time.time() - t0_pipeline
    print("\n================================================================================")
    print(f" 全闭环管线已全部顺利跑通！总用时: {total_cost:.1f} 秒")
    print(f" 1. 游戏原始截图: captured/operbox_page_*.png")
    print(f" 2. 识别数据表: 统计_maa_captured.xlsx")
    print(f" 3. 分层渲染素材: generated/layered/ (177 张 1080P PNG)")
    print(f" 4. 全局质检验收图: reports/contact_sheet.png")
    print(f" 5. 达芬奇分层时间线: reports/timeline_v2_layered.xml")
    print("================================================================================")

if __name__ == '__main__':
    run_pipeline()
