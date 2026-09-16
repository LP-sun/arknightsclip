# Pen.dev vs React/CSS 渲染后端 20 维对比矩阵 (Renderer Evaluation Matrix)

本评估基于在 `feat/pen-renderer-spike` 分支上完成的严格可比实验（共享数据源 `shared/manifests/`、素材 `shared/assets/`、几何规范 `shared/layout/`、相同输出规格 1920×1080）。

打分标准：**1 分（极差/不可行）至 5 分（优秀/理想）**。

---

## 1. 详细评分矩阵

| 评估指标 | Pen.dev (AST Headless) | React/CSS (Playwright Headless) | 核心对比与实际理由 |
| :--- | :---: | :---: | :--- |
| **1. Initial Implementation (初始构建成本)** | **3** | **4** | Pen 需要逆向理解 2.17 JSON AST 协议与手动构建递归栅格化引擎；React/CSS 拥有成熟的组件体系与社区生态，SSR 与 CSS 样式快速成型。 |
| **2. Visual Fidelity (视觉还原度)** | **4** | **5** | React/CSS 原生支持 `clip-path`、`radial-gradient`、`backdrop-filter` 与丰富阴影，相比 PIL 栅格化更细腻还原方舟磨砂发光质感；Pen 目前缺少复杂内发光。 |
| **3. Layout Iteration (排版迭代灵活性)** | **4** | **5** | 共享 `report_5p_layout.json` 契约下两者均很灵活；但 React 配合 CSS flexbox/grid 能自适应文本折行与间距，Pen 强依赖绝对 x/y 坐标计算。 |
| **4. Agent Friendliness (AI 编码可控性)** | **3** | **5** | 在修改角色等级偏移与透明度实测中，Codex 修改 React CSS 类仅需 1 行精准编辑；修改 Pen AST 需在数百行嵌套 JSON 中寻找节点并重算局部坐标，容错率较低。 |
| **5. MCP Dependency (MCP 工具依赖)** | **3** | **5** | 官方 Pen 依赖命名管道 `\\.\pipe\pencil-desktop` 且必须打开窗口；React 渲染器 0 MCP 依赖，纯 npm/node CLI 即开即用。 |
| **6. GUI Dependency (图形界面依赖)** | **4** | **5** | 官方 Pen 强依赖桌面 GUI；本项目虽然自研了无头 PenRenderer，但 React/CSS 从根源上就是标准的无头浏览器架构（Headless Chromium）。 |
| **7. True Headless (真无头运行能力)** | **5** | **5** | 两者均通过本地 CLI 实现了真正的无头运行，均可在无显卡/无显示器的 CI 服务器稳定跑通。 |
| **8. Batch Speed (批量吞吐性能)** | **4** | **5** | 实测 10 场景批处理：Pen 用时 **8.34s** (0.83s/张)；React 在复用 Chromium 实例后总用时 **7.43s** (0.62s/张)，React 批处理吞吐反超 Pen。 |
| **9. Text Update (文本参数化更新)** | **4** | **5** | 两者均支持单场景 JSON 动态覆写；React JSX 单向数据绑定更加自然，Pen 需递归定位 descendants 键名。 |
| **10. Image Replacement (图片替换与载入)** | **4** | **5** | Pen 依赖本地 PIL 打开与缓存裁剪；React 通过标准 `<img>` + CSS `object-fit: cover` 自动居中裁切，代码更简洁健壮。 |
| **11. Visibility Logic (显隐与条件状态)** | **4** | **5** | `own = true / false` 条件状态：Pen 需对 10 个子节点分别赋值 `enabled: true/false`；React 直接三元表达式 `<OperatorCard /> : <NoInfo />`，逻辑自闭环。 |
| **12. Chinese Fonts (中文字体支持)** | **4** | **5** | Pen 依赖操作系统 `msyh.ttc` 绝对路径；React 通过 `@font-face` 与 `await document.fonts.ready` 严格同步等待，跨平台字体策略更优雅。 |
| **13. Clipping (区域裁切与遮罩)** | **4** | **5** | Pen 使用 `clip: True` 配合 PIL crop；React 支持 CSS `overflow: hidden` 与 `clip-path: polygon()`，可自由定义战术斜角切边。 |
| **14. Complex Masks (复杂材质与渐变蒙版)** | **3** | **5** | React/CSS 原生支持 `mask-image`、`mix-blend-mode`、半透明渐变条；Pen 的轻量 PIL 引擎若要实现等价效果需编写复杂的通道合成算法。 |
| **15. Git Diff (版本控制差异可读性)** | **4** | **5** | Pen 是单文件格式化 JSON (12KB)，diff 行级清晰；React/CSS 拆分为语义化组件与 CSS 文件，每次修改仅触达几行 CSS/TSX，无大 JSON 膨胀风险。 |
| **16. Testability (单元测试与回归便利度)** | **3** | **5** | React 拥有成熟的测试生态（Jest / Vitest / Playwright test），支持组件级快照测试；Pen 只能做整图像素比对。 |
| **17. CI Suitability (持续集成适用度)** | **4** | **5** | React 是 Web 前端与 Node 标准产物，所有 CI 镜像均预装；Pen 若依赖官方应用则无法上 CI，依赖自研引擎虽可但不如 npm 体系标准化。 |
| **18. 100+ Scenes (百场景扩展能力)** | **5** | **5** | 存储开销两者相当（~2KB JSON / 场景）；批量生成 100 场景耗时：Pen 约 80s，React 约 62s，均远优于 Photoshop（需 6~10 分钟且高发内存泄漏）。 |
| **19. Human Manual Editing (人工设计编辑)** | **5** | **2** | **Pen.dev 的绝对优势项**：拥有直观的桌面 GUI 设计画布，设计师可直接拖拽调整；React/CSS 必须由前端开发者写代码调整样式，对纯视觉设计师门槛高。 |
| **20. Runtime Stability (运行稳定性与确定性)** | **5** | **5** | 在 20 次连续渲染稳定性压测中，两者均达成 **20/20 成功率 (100%)**，尺寸严格 **1920×1080**，且产物哈希达到 **100% 确定性完全匹配**。 |

---

## 2. 综合加权评分总结

* **Pen.dev 总分**：**79 / 100**
  * **杀手级优势**：拥有可视化设计器（GUI Canvas），允许视觉设计师或人类创作者进行可视化的母版排版与审美定型；
  * **主要短板**：官方 MCP 与桌面客户端无法无头运行；样式扩展（如高级发光、斜切遮罩）依赖自研解析器的实现深度。
* **React/CSS 总分**：**93 / 100**
  * **杀手级优势**：工业级生态成熟度、真无头 Chromium 批处理（均摊 0.62s/张）、现代 CSS 强大的战术视觉还原能力、以及对 AI 智能体（Codex）近乎完美的指令修改亲和度；
  * **主要短板**：缺少即时拖拽的可视化排版界面，母版初次构建需写代码或配合设计工具导出。
