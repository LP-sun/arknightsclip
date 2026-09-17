# 明日方舟报菜名 · 历史冗余代码、数据与交付物归档库

本目录保存项目开发迭代过程中的探索性脚本、早期中间数据、切片资产以及历史交付成片，已与主生产管线解耦。

## 目录索引

- `legacy_scripts/`: 早期实验性与被重构替代的 Python 脚本 (共 50 个，含早期单图/分层渲染、切刀分析、打点试算及历史归档脚本等)。
- `legacy_data/`: 早期分析 JSON、图层契约与原始 OCR 识别 CSV 记录 (含 `composition_manifest.json`、`durations_24fps_perfect.json`、`edit_plan.json`、`slot_map.json`、`template_schema.json`、`统计_maa_captured.xlsx` 等)。
- `legacy_deliveries/`: 早期实验交付成片视频与交付报告 (含 `output_video.*`、`明日方舟_六星干员报菜名_v2/v3/v4*.mp4`、`明日方舟五周年*.mov` 及 `FINAL_PLACEHOLDER_VIDEO_REPORT.md`)。
- `legacy_media/`: 早期测试图、切片调试样本与临时音频波形文件。
- `legacy_folders/`: 早期中间处理目录 (如 `output/`, `output_clean/`, `cut_frames/` 及各博士原始 OCR 头像包)。
- `legacy_collection_pipeline/`: 早期 MAA 自动化采集管线脚本历史备份。

---

## 当前正式生产入口说明

自架构重构起，所有生产级功能均由 `src/arknightsclip/` 统一提供：
- 命令行入口：`arknightsclip --help` (或 `python -m arknightsclip`)
- 采集与识别：`src/arknightsclip/maa/operbox_collector.py` / `operbox_analyzer.py`
- 数据规范化：`src/arknightsclip/data/dataset_manager.py`
- 场景与时间线：`src/arknightsclip/scene/builder.py` / `src/arknightsclip/timeline/`
- 测试验证：`python tests/run_tests.py`
