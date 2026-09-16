# PSD 自动化前置审计报告 (PSD Automation Pre-Audit)

> **审计基准**：为准备 `feat/psd-template-automation` 分支上的最小技术验证（Photoshop UXP 驱动单个五人 PSD 母版进行全自动数据驱动渲染），对仓库内所有现存 PSD 相关资产、代码和报告进行全面基线审计。

---

## 一、 能力层级严格划分

### 1. 已验证能力 (Verified Capabilities)
以下能力在前期研发中已经过代码实测与输出检验，确认为 100% 可用且稳定的工程事实：
- **静态分层提取能力**：`batch_render_layered_graphics.py` 能够利用 `psd-tools` 从历史 59 个完整 PSD 中分别提取出 3 层全画幅（1920×1080）PNG（`background.png`, `character_cards.png`, `doctor_info.png`）。
- **八人 PSD 结构逆向与图层分析**：`reports/template_analysis.md`、`template_schema.json`、`slot_map.json` 已经完整逆向了历史 8 人版 PSD 中 209 个图层的层次、类型、边界坐标及显隐逻辑。
- **时间线装配与对齐能力**：`generate_v2_layered_fcpxml.py` 能够严格按照 24fps 卡点规范生成 4 视频轨 + 2 音频轨的 FCP7 XML，并在 DaVinci Resolve 中完成多层导入与精准对齐。
- **标准 SceneManifest 数据契约**：`experiments/shared/manifests/exusiai_test.json` 与 `variant_test.json` 已经确立了包含 5 位玩家状态（包含已持有、未持有、不同精英等级、不同潜能等级、不同等级数值）的规范数据结构。

### 2. 现有遗留能力 (Legacy / Out-of-Scope Capabilities)
以下能力属于既有历史管线或并存实验，**绝不能与本轮 PSD 动态渲染器混淆**：
- **遗留的“批量图层拆分”不是“动态参数化渲染器”**：
  - `batch_render_layered_graphics.py` 仅仅是对**已经由人工在 Photoshop 中做好的 59 个干员独立 PSD** 进行静态图层导出。
  - 它**不具备**接收 `SceneManifest` JSON、修改 PSD 内部文字、替换图片、改变图层显隐后动态渲染的能力。
- **Pillow / Pen / React Renderer 不是最终生产 Renderer**：
  - `experiments/pen_renderer/` 与 `experiments/react_renderer/` 是独立的矢量与网页技术 spike。
  - 虽然它们验证了同一份 JSON 驱动渲染的可行性，但它们使用的是自身引擎（Skia/PIL/Chromium）模拟视觉，**不代表 Photoshop 内部图层与效果的真实渲染**。
  - 本轮必须遵守：**PSD 是唯一视觉真源，Photoshop 是唯一最终渲染器**。

### 3. 本轮需要新实现能力 (Target Capabilities for This Spike)
本轮 `feat/psd-template-automation` 的核心技术攻关目标是建立一个**完全不依赖人工修改 PSD** 的 Photoshop 自动化链路：
- **五人母版 Layer Contract 规范与 Schema**：
  - 摆脱历史 PSD 中混乱的“按分类分组”结构（如全局的“卡面/卡面01”、“角色等级/111”），建立以玩家为核心的高聚合树形契约：`REPORT_ROOT/PLAYER_P1/OPERATOR_STATE/...`。
  - 制定 `templates/psd/report_5p_schema.json`，确保所有动态图层具备唯一的机器可寻址语义名称，严禁依赖图层数字索引或屏幕坐标。
- **Photoshop UXP 模板检查器 (Template Inspector)**：
  - 编写 `tools/photoshop/inspect_template.psjs`（及离线 python 校验工具），在渲染前递归遍历 PSD 图层树，验证是否包含全部必需语义图层、类型是否匹配（Text/SmartObject/Group）、是否有重名图层。如果缺失必需项直接报错中断。
- **Photoshop UXP 动态参数化渲染引擎 (Render Scene)**：
  - 编写 `tools/photoshop/render_scene.psjs`，实现四大核心自动化动作：
    1. **Smart Object 替换 (Smart Object replacement)**：替换中央大立绘 `OPERATOR_FULL_ART`、博士头像 `DOCTOR_AVATAR`、干员卡面 `OPERATOR_CARD`，并保持原有 Transform/Mask/LayerStyle/ClippingGroup 不变形。
    2. **纯文本内容更新 (Text layer update)**：通过 Photoshop DOM 仅更新 `textItem.contents`，严禁破坏模板原有的字体、字号、字距、颜色与图层样式。
    3. **互斥图层显隐控制 (Mutual exclusivity visibility)**：显式设置 `own=false`（触发 `NO_INFO`，隐藏卡面与练度）与 `own=true`（只点亮对应的一个 `ELITE_x` 与对应的一个 `POTENTIAL_y`）。
    4. **高保真标准导出 (High-Fidelity Export)**：自动化导出 1920×1080 PNG 与配套 `*.render.json` 元数据，随后**不保存关闭母版**，确保每次渲染始于绝对干净的 Master 状态。

---

## 二、 现有资产状态与母版定位确认

| 资产项 | 现状 | 本轮处置原则 |
| :--- | :--- | :--- |
| **59 个历史 8 人 PSD** | 存在于 `psd模板/全6星干员备份文件（较大）/` (总计 >2GB) | 保留为参考与视觉真源对照，不作为本轮动态五人渲染模板。 |
| **`report_5p_master_v0.psd`** | **仓库当前尚未存在** | **确认为 `WAITING_FOR_USER_AUTHORED_MASTER` 状态**。程序绝不盲目生成假母版伪称完成，而是提供标准规范、Schema 校验器、以及一份合规的结构 Fixture 供脚本验证链路。 |
| **Photoshop 运行环境** | 系统已安装 `Adobe Photoshop 2023` (v24.1) 于 `C:\Program Files\Adobe\Adobe Photoshop 2023\Photoshop.exe` | 支持 ExtendScript、UXP Scripting (`.psjs`) 以及 COM 桥接。本轮优先基于 UXP / `batchPlay` 原生脚本。 |
| **测试 Manifest** | 存在于 `experiments/shared/manifests/` | 100% 复用，涵盖了 P1~P5 的持有/未持有/精二/精一/不同潜能等全部测试边界。 |

---

## 三、 审计结论与工作规划

审计确认：**当前仓库不存在现成的“数据驱动 PSD 动态渲染器”**。旧版脚本仅能切片历史固定 PSD。
因此，本轮工作的唯一技术目标就是验证**“单个 PSD 母版 + 结构化 JSON → Photoshop UXP 自动修改并输出 PNG”**的真实可行性。
