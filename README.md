# 明日方舟报菜名 · 全自动工业级视频制作管线

基于 MAA 视觉协议与 DaVinci Resolve 的自动化端到端干员展示与报菜名视频生成流水线。

## 🌟 功能特性

1. **Step 1 & 2: MAA 游戏抓取与练度识别**
   - 通过 ADB 连接模拟器/真机，自动截取干员仓库。
   - 结合模板匹配与视觉算法识别干员精英化、潜能、等级与名称纠错。
2. **Step 3: 结构化数据持久化**
   - 自动生成结构化干员练度统计表 (`统计_maa_captured.xlsx`) 与元数据。
3. **Step 4: PSD 动态模板分层资产批量渲染**
   - 驱动 Photoshop 分层模板，批量导出 1080P 分离图层（背景、干员立绘卡片、博士信息等）。
4. **Step 5: 24FPS 分层时间线工程组装**
   - 自动生成 DaVinci Resolve 兼容的 FCP7 XML 分层时间线，精准咬合音频节奏点。
5. **Step 6: 全局 Contact Sheet 质检**
   - 渲染全局多场景画面对照总览图并输出验收报告。

## 📁 项目结构

- `run_full_autonomous_pipeline.py`: 全流程自动化调度入口脚本
- `maa_game_pipeline.py`: ADB 通信与仓库自动截取
- `maa_operator_extractor.py`: MAA 视觉算法与练度识别
- `batch_render_layered_graphics.py`: PSD 分层资产批量渲染
- `generate_v2_layered_fcpxml.py`: FCPXML 分层时间线生成
- `import_v2_timeline_to_davinci.py`: 导入达芬奇工程脚本
- `create_contact_sheet.py`: 质检全景预览图生成
- `maa_templates/`: MAA 图标匹配母版
- `*.json`: 时间轴、槽位映射与工程元数据配置

## 🚀 运行方法

```bash
python run_full_autonomous_pipeline.py
```
