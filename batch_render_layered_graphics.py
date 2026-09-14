"""
明日方舟报菜名 - PSD 模板分层批量渲染器 (遵从 psd模板/README 规范)
1. 遍历 composition_manifest.json 中 59 个精细制作的 PSD 工程文件
2. 每一个 Scene 分别导出 3 层标准 1920x1080 图像：
   - background.png (1920x1080 RGB)
   - character_cards.png (1920x1080 RGBA, 保留透明通道, 中间透空展示立绘)
   - doctor_info.png (1920x1080 RGBA, 8位博士信息, 保留透明通道)
3. 严格全画幅导出 (Full Canvas, 不做 Trim, 天然对齐)
4. 输出至 generated/layered/<scene_id>/
5. 自动质检生成 reports/render_report.json
"""

import os
import sys
import time
import json
import numpy as np
from psd_tools import PSDImage
from PIL import Image

def run_batch_render():
    manifest_file = 'composition_manifest.json'
    with open(manifest_file, 'r', encoding='utf-8') as f:
        manifest = json.load(f)

    psd_dir = r'E:\明日方舟报菜名\psd模板\全6星干员备份文件（较大）'
    output_root = r'E:\明日方舟报菜名\generated\layered'
    os.makedirs(output_root, exist_ok=True)
    os.makedirs(r'E:\明日方舟报菜名\reports', exist_ok=True)

    report = {
        'total_scenes': len(manifest['scenes']),
        'success_count': 0,
        'failure_count': 0,
        'scenes': []
    }

    t0_all = time.time()
    for idx, scene in enumerate(manifest['scenes'], start=1):
        scene_id = scene['scene_id']
        op_name = scene['operator_name']
        psd_file = scene.get('psd_file')
        scene_dir = os.path.join(output_root, scene_id)
        os.makedirs(scene_dir, exist_ok=True)

        bg_path = os.path.join(scene_dir, 'background.png')
        cards_path = os.path.join(scene_dir, 'character_cards.png')
        doc_path = os.path.join(scene_dir, 'doctor_info.png')

        t_start = time.time()
        print(f"[{idx:02d}/59] 正在处理: {scene_id} ({psd_file})...", end='', flush=True)

        try:
            full_psd_path = os.path.join(psd_dir, psd_file)
            psd = PSDImage.open(full_psd_path)

            # 1. 提取 Background (Layer 0 + Layer 1)
            bg = Image.new('RGB', (1920, 1080), (0, 0, 0))
            if len(psd) > 0:
                l0 = psd[0].topil()
                if l0:
                    bg.paste(l0, (max(0, psd[0].bbox[0]), max(0, psd[0].bbox[1])))
            if len(psd) > 1:
                l1 = psd[1].topil()
                if l1:
                    bg.paste(l1, (psd[1].bbox[0], psd[1].bbox[1]), l1 if l1.mode == 'RGBA' else None)
            bg.save(bg_path, format='PNG')

            # 2. 读取原生 Composite
            full_rgba = psd.composite().convert('RGBA')
            arr_full = np.array(full_rgba)
            arr_bg = np.array(bg.convert('RGBA'))

            # 计算前景 Alpha 遮罩
            diff = np.max(np.abs(arr_full[:, :, :3].astype(np.int32) - arr_bg[:, :, :3].astype(np.int32)), axis=2)
            fg_mask = (diff > 4).astype(np.uint8) * 255

            # 3. 提取 Doctor Info (左边界 x<=165 或 右边界 x>=1755)
            doc_mask = np.zeros((1080, 1920), dtype=np.uint8)
            doc_mask[:, :165] = fg_mask[:, :165]
            doc_mask[:, 1755:] = fg_mask[:, 1755:]

            doc_arr = arr_full.copy()
            doc_arr[:, :, 3] = doc_mask
            doc_img = Image.fromarray(doc_arr, 'RGBA')
            doc_img.save(doc_path, format='PNG')

            # 4. 提取 Character Cards (165 < x < 1755, 中间透明)
            cards_mask = np.zeros((1080, 1920), dtype=np.uint8)
            cards_mask[:, 165:1755] = fg_mask[:, 165:1755]

            cards_arr = arr_full.copy()
            cards_arr[:, :, 3] = cards_mask
            cards_img = Image.fromarray(cards_arr, 'RGBA')
            cards_img.save(cards_path, format='PNG')

            # 质检
            cost = time.time() - t_start
            print(f" 完成 ({cost:.2f}s)")

            report['success_count'] += 1
            report['scenes'].append({
                'scene_id': scene_id,
                'operator': op_name,
                'status': 'SUCCESS',
                'files': {
                    'background': bg_path,
                    'character_cards': cards_path,
                    'doctor_info': doc_path
                },
                'resolution': [1920, 1080],
                'render_time_seconds': round(cost, 2)
            })

        except Exception as e:
            cost = time.time() - t_start
            print(f" 失败: {e}")
            report['failure_count'] += 1
            report['scenes'].append({
                'scene_id': scene_id,
                'operator': op_name,
                'status': 'FAILED',
                'error': str(e)
            })

    total_cost = time.time() - t0_all
    report['total_duration_seconds'] = round(total_cost, 2)

    with open(r'E:\明日方舟报菜名\reports\render_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"\n批量分层渲染全部完成！总用时: {total_cost:.1f}s, 成功: {report['success_count']}, 失败: {report['failure_count']}")
    print("报告已写入 reports/render_report.json")

if __name__ == '__main__':
    run_batch_render()
