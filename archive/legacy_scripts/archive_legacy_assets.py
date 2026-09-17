"""
明日方舟报菜名 - 冗余历史代码与临时资产归档脚本
将前期的探索性脚本、临时分析 JSON、OCR CSV 以及中间帧目录安全迁移至 archive/ 归档库，
保持项目根目录极致清爽、规范、可维护。
"""

import os
import shutil

def run_archive():
    root = r"E:\明日方舟报菜名"
    archive_dir = os.path.join(root, "archive")
    scripts_dir = os.path.join(archive_dir, "legacy_scripts")
    data_dir = os.path.join(archive_dir, "legacy_data")
    media_dir = os.path.join(archive_dir, "legacy_media")
    folders_dir = os.path.join(archive_dir, "legacy_folders")

    for d in [scripts_dir, data_dir, media_dir, folders_dir]:
        os.makedirs(d, exist_ok=True)

    # 1. 冗余历史脚本 (45 个)
    legacy_scripts = [
        'try.py', 'trying.py', 'final.py', 'finialgpt.py', 'fixed2.0.py', 'gpt_fixed.py',
        'davinci_compose.py', 'davinci_compose_final.py', 'rebuild_perfect_timeline.py',
        'apply_perfect_grid_to_davinci.py', 'align_operators_timeline.py', 'calculate_quantized_timeline.py',
        'compute_24fps_durations.py', 'check_24fps_conversion.py', 'finetune_24fps.py',
        'compare_24fps_grid.py', 'analyze_cuts.py', 'analyze_grid.py', 'audio_beat_analysis.py',
        'check_audio_markers.py', 'check_long_items.py', 'find_exact_scene_cuts.py', 'scan_cuts.py',
        'match_cuts_ocr.py', 'inspect_sections.py', 'inspect_psd.py', 'inspect_davinci_timeline.py',
        'list_timelines.py', 'print_all_markers.py', 'print_top_levels.py', 'quick_inspect.py',
        'read_excel.py', 'transcribe_audio.py', 'verify_final.py', 'validate_output_graphics.py',
        'generate_clean_dataset.py', 'generate_clean_dataset_rhythm.py', 'generate_edit_plan.py',
        'generate_final_report.py', 'generate_graphics_manifest.py', 'generate_rhythm_timeline.py',
        'generate_template_schema.py', 'batch_render_graphics.py', 'apply_24fps_master_timeline.py',
        'apply_edit_plan_to_resolve.py'
    ]

    # 2. 冗余中间数据文件 (32 个)
    legacy_data = [
        'ai_beat_tracking.json', 'cuts_detected.json', 'cuts_ocr_results.json', 'exact_cuts.json',
        'graphics_manifest.json', 'operator_timeline_alignment.json', 'psd_layer_structure.json',
        'quantized_beats_analysis.json', 'raw_cuts.json', 'rhythm_timeline.json', 'whisper_result.json',
        'edit_plan.json',
        'dyk_1.csv', 'dyk_2.csv', 'dyk_3.csv', 'dyk_4.csv',
        'nzx_1.csv', 'nzx_2.csv', 'nzx_3.csv', 'nzx_4.csv',
        'wyf_1.csv', 'wyf_2.csv', 'wyf_3.csv', 'wyf_4.csv', 'wyf_5.csv',
        'yzx_1.csv', 'yzx_2.csv', 'yzx_3.csv', 'yzx_4.csv',
        'zyc_1.csv', 'zyc_2.csv', 'zyc_3.csv'
    ]

    # 3. 冗余临时媒体与裁剪文件 (7 个)
    legacy_media = [
        'audio_temp.wav', 'crop9.png', 'crop10.png', 'crop11.png',
        'test_174_clean.png', 'test_canvas.png', 'test_men_clean.png'
    ]

    # 4. 冗余历史中间目录 (9 个)
    legacy_dirs = [
        'cut_frames', 'dyk', 'nzx', 'output', 'output_clean', 'ref_samples', 'wyf', 'yzx', 'zyc'
    ]

    moved_count = 0
    # 迁移脚本
    for f in legacy_scripts:
        src = os.path.join(root, f)
        if os.path.exists(src):
            shutil.move(src, os.path.join(scripts_dir, f))
            moved_count += 1

    # 迁移数据
    for f in legacy_data:
        src = os.path.join(root, f)
        if os.path.exists(src):
            shutil.move(src, os.path.join(data_dir, f))
            moved_count += 1

    # 迁移媒体
    for f in legacy_media:
        src = os.path.join(root, f)
        if os.path.exists(src):
            shutil.move(src, os.path.join(media_dir, f))
            moved_count += 1

    # 迁移目录
    for d in legacy_dirs:
        src = os.path.join(root, d)
        if os.path.exists(src):
            dst = os.path.join(folders_dir, d)
            if os.path.exists(dst):
                shutil.rmtree(dst)
            shutil.move(src, dst)
            moved_count += 1

    # 写入 archive/README.md 归档说明
    archive_readme = """# 明日方舟报菜名 · 历史冗余代码与数据归档库

本目录保存项目开发迭代过程中的探索性脚本、早期剪刀识别中间数据与临时切片资产，已与主生产管线解耦。

## 目录索引

- `legacy_scripts/`: 早期实验性与被重构替代的 Python 脚本 (如单图渲染、早期切刀分析、音频打点试算等，共 45 个)。
- `legacy_data/`: 早期中间状态分析 JSON 与原始 OCR 识别 CSV 记录 (共 32 个)。
- `legacy_media/`: 早期测试图、切片调试样本与临时音频波形文件 (共 7 个)。
- `legacy_folders/`: 早期中间处理目录 (如 `output/`, `output_clean/`, `cut_frames/` 及各博士原始 OCR 头像包，共 9 个)。

---

## 主生产管线保留文件速查 (项目根目录)

- `run_full_autonomous_pipeline.py`: 全自动端到端工业级总调度器
- `maa_game_pipeline.py`: MAA 模拟器 ADB 连接与仓库截取引擎
- `maa_operator_extractor.py`: MAA 视觉练度识别与 Excel 导出引擎
- `batch_render_layered_graphics.py`: PSD 分层母版全画幅批量渲染器
- `generate_v2_layered_fcpxml.py`: DaVinci Resolve 24FPS 分层时间线 FCP7 XML 生成器
- `import_v2_timeline_to_davinci.py`: 达芬奇时间线工程自动导入脚本
- `create_contact_sheet.py`: 59 全场景缩略图拼版生成器
- `template_schema.json`: 母版 209 个图层结构契约
- `slot_map.json`: 8 个角色槽位坐标与图层映射表
- `composition_manifest.json`: 59 个场景的 8 玩家结构化练度
- `durations_24fps_perfect.json`: 量化校准的 24fps 单帧时长配置
- `统计_maa_captured.xlsx`: MAA 游戏抓取产出的结构化练度表
- `psd模板/`: 母版 PSD、59 个干员备份 PSD 与素材图库
- `generated/layered/`: 177 张标准 1080P 分层无损 PNG 资产
- `captured/`: 游戏原始抓取截屏与元数据
- `reports/`: 终检验收报告与全景质检图
"""

    with open(os.path.join(archive_dir, "README.md"), "w", encoding="utf-8") as f:
        f.write(archive_readme)

    print(f"成功将 {moved_count} 项冗余文件/目录迁移至 archive/ 归档库！")
    print(f"归档索引说明已写入: {os.path.join(archive_dir, 'README.md')}")

if __name__ == '__main__':
    run_archive()
