# PenRenderer Spike (实验性隔离分支)

本目录为 `pen.dev` 作为平面报菜名模板渲染后端的独立概念验证（PoC）与性能基准实验目录。

> **工作原则**：
> 1. 完全不改动生产环境已跑通的 PSD / Photoshop / DaVinci Resolve 管线；
> 2. 不删除现有 PSD 文件与旧时间线逻辑；
> 3. 不将实验代码混入生产管线调度入口；
> 4. 验证五人布局单一 `.pen` 母版 + Scene JSON 的自动参数化与 PNG 导出能力。

---

## 📁 目录结构说明

- `templates/`
  - `report_5p_master.pen`: 原生五人报菜名母版模板，采用单一通用组件 `PLAYER_CARD_COMPONENT` + 5 个 `ref` 实例结构。
- `manifests/`
  - `exusiai_test.json`: 能天使场景 Manifest (P1/P2/P4/P5 已持有，P3 未持有 NO INFO)。
  - `variant_test.json`: 推进之王场景 Manifest (P1/P3/P4 已持有，P2/P5 未持有 NO INFO)。证明**只变 JSON，完全相同模板**。
- `outputs/`
  - `test_A.png`: 能天使 1920×1080 渲染结果。
  - `test_B.png`: 推进之王 1920×1080 渲染结果。
  - `pen_scene.png`: A/B 对比基准渲染图。
  - `test_A.pen`, `test_B.pen`: 派生的独立参数化 `.pen` 文档。
  - `benchmark_result.json`: 性能基准测试原始数据。
  - `pen_smoke_timeline.xml`: 达芬奇独立 10 秒 Smoke Test 时间线工程。
- `reference/`
  - `reference_psd.png`: 原版 PSD 8 人复合渲染对比参考图。
- `assets/`
  - `ui/`: 提取的高清战术背景底图、精英/潜能徽标切片。
  - `operators/`: 能天使与推王全画幅高清立绘。
  - `players/`: 5 位博士头像切片。
- `scripts/`
  - `pen_renderer.py`: `PenRenderer` 核心类实现。
  - `create_master_pen.py`: 生成 `report_5p_master.pen` 脚本。
  - `extract_assets.py`: 从原版 PSD 与 MAA 模板提取素材脚本。
  - `run_spike_tests.py`: 运行 Test A 与 Test B 渲染脚本。
  - `benchmark_pen_renderer.py`: 性能基准自动化评测脚本。
  - `create_ab_comparison.py`: 生成三联 A/B 对比画板脚本。
  - `run_resolve_smoke_test.py`: 达芬奇 10 秒时间线生成与导入验证脚本。

---

## 🚀 快速复现指令

```bash
# 1. 运行参数化验证 (生成 test_A.png 与 test_B.png)
python experiments/pen_renderer/scripts/run_spike_tests.py

# 2. 运行性能基准评测 (单场景与 10 场景批处理)
python experiments/pen_renderer/scripts/benchmark_pen_renderer.py

# 3. 运行视觉对比生成 (输出 reports/pen_ab_comparison.png)
python experiments/pen_renderer/scripts/create_ab_comparison.py
```
