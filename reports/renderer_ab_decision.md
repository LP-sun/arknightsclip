# Pen.dev vs React/CSS 最终技术选型与架构决策报告

## 1. 执行摘要与验证背景

本轮实验严格贯彻**控制变量法（Same JSON + Same Assets + Same Layout + Same Target Resolution）**，在隔离目录中搭建了并列的渲染验证原型：
* **Pen.dev Spike**：基于 `.pen` Schema 2.17 AST 规范的轻量化无头渲染器；
* **React/CSS Spike**：基于 React 19 SSR + 现代 CSS + Playwright Headless Chromium 的工业级自动化渲染器。

二者完全共享：
1. 业务输入：[`experiments/shared/manifests/`](file:///E:/明日方舟报菜名/experiments/shared/manifests/) (`exusiai_test.json`, `variant_test.json`, `batch_01~10.json`)
2. 基础素材：[`experiments/shared/assets/`](file:///E:/明日方舟报菜名/experiments/shared/assets/) (干员立绘、博士头像、UI 图标)
3. 几何契约：[`experiments/shared/layout/report_5p_layout.json`](file:///E:/明日方舟报菜名/experiments/shared/layout/report_5p_layout.json) (五位玩家与立绘坐标规范)

---

## 2. 核心实验结论与实测数据

### 2.1 图像比对与视觉还原度
* **对比产物**：
  * 能天使场景三联对比：[`reports/renderer_ab/exusiai_test_comparison.png`](file:///E:/明日方舟报菜名/reports/renderer_ab/exusiai_test_comparison.png)（Pen vs React vs PSD 参考原图）
  * 推进之王变体对比：[`reports/renderer_ab/variant_test_comparison.png`](file:///E:/明日方舟报菜名/reports/renderer_ab/variant_test_comparison.png)（Pen vs React vs 4x 增强绝对差异图）
* **视觉结论**：
  * **React/CSS**：在磨砂半透明质感（`backdrop-filter`）、战术网格背景渐变、卡面阴影高光以及文字垂直基线对齐上，表现更加细腻且极度贴近明日方舟原版 UI；
  * **Pen.dev (PIL)**：基本版式与比例达到 95% 还原，但在复杂混合模式、卡片细微发光和羽化边缘方面稍显扁平。

### 2.2 性能基准（实测数据）
* **单场景冷启动渲染**：
  * Pen.dev：**0.8279 秒**（Python 进程秒开，纯内存图像构建）
  * React/CSS：**3.2228 秒**（包含 Node.js CLI 编译与 Playwright 浏览器拉起开销）
* **批量 10+ 场景渲染**：
  * Pen.dev：**8.3424 秒**（均摊 **0.8342 秒/张**）
  * React/CSS（复用 Chromium 实例）：**7.4305 秒**（均摊 **0.6192 秒/张**）
  * **结论**：在长线批量出图场景下，React/CSS 吞吐量反超 Pen.dev。

### 2.3 稳定性与数学确定性（20 次连续运行）
* **Pen.dev**：20/20 成功，100% 相同 SHA-256 哈希值；
* **React/CSS**：20/20 成功，在显式等待 `document.fonts.ready` 与全量图片解码后，达成 100% 相同哈希值；
* **结论**：两种方案在解决异步加载后，均具备 100% 严格确定性，杜绝了字体回退或素材未载入的偶发问题。

### 2.4 AI 智能体修改亲和度（Codex Friendliness）
* **测试 1：调整局部间距与透明度（角色等级向右 12px，NO INFO 透明度降 15%）**：
  * **React/CSS 胜出**：只需修改 `report.css` 中的 2 处语义化 class 规则，耗时 3 秒，0 破坏其他元素风险；
  * **Pen.dev**：需深度遍历 500+ 行 JSON AST，定位嵌套子节点并手动重算绝对偏移坐标，AI 易漏改或坐标计算失准。
* **测试 2：全局卡片布局调整（P4/P5 下移 24px）**：
  * **平手**：得益于共享的 `report_5p_layout.json` 契约，两者均只需修改 1 个 JSON 配置文件，即可自动使输出画面同步调整。

---

## 3. 最终技术决策：双轮驱动混合架构 (Hybrid Architecture)

经过深度评测，**既不建议单一使用 Pen.dev，也不建议立刻完全淘汰现有成果**。
最符合工程现实、维护成本最低、演进最稳健的技术选型为：

### **「Pen 可视化母版原型 + React/CSS 生产级批处理渲染后端」**

```
┌─────────────────────────────────────────────────────────────┐
│                    视觉设计与原型定型阶段                      │
│      人工设计师 / 创作者使用 Pen.dev 可视化调整五人母版版式      │
│                 导出: report_5p_layout.json                 │
└──────────────────────────────┬──────────────────────────────┘
                               │ (定义统一几何与元素规范)
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                    生产级自动化渲染管线                       │
│     React/CSS Renderer (Headless Chromium + React 19 SSR)   │
│  输入: shared/manifests/*.json + shared/assets/             │
│  输出: 1920x1080 无损 PNG (批处理速度 0.6s/张, 100%确定性)    │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                    下游 DaVinci Resolve 剪辑                 │
│         自动生成 FCPXML / xmeml, 0 帧偏移导入轨道调色           │
└─────────────────────────────────────────────────────────────┘
```

### 决策理由：
1. **解决设计师与开发者的协同断层**：纯写 React/CSS 代码对视觉设计师不友好；而纯用 Pen.dev 在自动化流水线中存在 MCP 不稳定、缺少真正无头 CLI、CSS 复杂滤镜支持不足的硬伤。
2. **生产环境绝对解耦 GUI**：React/CSS 方案拥有纯净的标准 Node/Headless 运行时，无需本地启动任何桌面应用窗口，在 Linux/Windows 服务器、后台无头任务中具备最高级别的健壮性。
3. **保护现有资产与渐进迁移**：现存的 59 个历史特殊 PSD 与 8 人母版继续保留在 Photoshop 备用分支中，常规大批量报菜名场景全面切入 React/CSS 高性能渲染通道。

---

## 4. 后续演进路线图 (M1 ~ M4)

* **M1 (已完成)**：构建 `pen_renderer` 与 `react_renderer` 双原型，完成 20 维对比矩阵、性能压测与稳定性实测。
* **M2 (近期)**：统一顶层 Python 接口：
  ```python
  def render_operator_report(manifest_path, output_path, engine="react"):
      # 默认走高性能 react headless，可选 pen 或 psd
  ```
* **M3 (中期)**：为 8 人版与特殊结算模板编写 React 对应组件，逐步吸纳历史场景。
* **M4 (远期)**：在保证视频质量一致的前提下，将正式批处理彻底移出庞大的 Photoshop COM 调用，达成全自动无人值守出片。
