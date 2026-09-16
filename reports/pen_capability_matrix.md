# 明日方舟报菜名 · Pen.dev 能力矩阵实测报告 (Capability Matrix)

> **实测环境**：Windows 11 x64, Pen Desktop 1.2.10, MCP Server `mcp-server-windows-x64.exe` (Version 1.0.0), Node IPC (Named Pipe `\\.\pipe\pencil-desktop`)  
> **分支**：`feat/pen-renderer-spike`  
> **测试原则**：严格基于本机反编译、代码审计与进程级通信实测，不猜能力，记录真实限制。

---

## 1. 核心能力矩阵表

| Feature | Needed by arknightsclip | Supported in Schema | Tested on Machine | Implementation Notes / Real Limitations |
| :--- | :---: | :---: | :---: | :--- |
| **`.pen` 原生文件格式** | **必须** | ✅ Yes | ✅ Tested | 并非加密二进制，实测为纯 JSON 文件（Schema version 2.13~2.17）。根对象包含 `version`, `children`, `variables`, `themes`。完全支持 Git 版本控制。 |
| **MCP Canvas Read/Write** | **必须** | ✅ Yes | ✅ Tested | 通过 `mcp-server-windows-x64.exe` 与命名管道 `\\.\pipe\pencil-desktop` 通信。**真实限制**：必须有 `Pen.exe` 处于运行状态且在前端打开目标 `.pen` 文档，否则报 `Failed to access file: A file needs to be open in the editor`。 |
| **Component 定义 (`reusable`)** | **必须** | ✅ Yes | ✅ Tested | 支持 `reusable: true`。作为组件根节点，具有完整的独立层级树。 |
| **Instance (`ref`) 引用** | **必须** | ✅ Yes | ✅ Tested | 节点类型 `type: "ref"`, `ref: "<component_id>"`, 实例化组件。支持坐标复写。 |
| **Instance Override (属性覆盖)** | **必须** | ✅ Yes | ✅ Tested | 通过 `descendants: { "<node_id>": { "fill": ..., "enabled": ... } }` 复写实例内部后代属性。 |
| **Text 节点与文本替换** | **必须** | ✅ Yes | ✅ Tested | `type: "text"`, 支持 `content`, `fontSize`, `fontWeight`, `fontFamily`, `fill`。纯数据注入极简。 |
| **中文字体渲染** | **必须** | ✅ Yes | ✅ Tested | 支持系统字体（微软雅黑、思源黑体）与 Google Fonts。若无本地字体则 fallback 到系统默认。 |
| **Image Fill (图像填充)** | **必须** | ✅ Yes | ✅ Tested | 几何体或 Frame 支持 `{ type: "image", url: "./path.png", mode: "fill"|"fit"|"stretch" }`，支持相对路径解析。 |
| **Frame Clipping (裁剪遮罩)** | **必须** | ✅ Yes | ✅ Tested | Frame 支持 `clip: true`，子元素超出部分被物理截断，实现完美卡框遮罩。 |
| **Frame Flexbox 自动布局** | 推荐 | ✅ Yes | ✅ Tested | 支持 `layout: "vertical"|"horizontal"`, `gap`, `padding`, `justifyContent`, `alignItems`。不支持百分比。 |
| **Opacity (不透明度)** | **必须** | ✅ Yes | ✅ Tested | 原生 `opacity: 0.0 ~ 1.0`，所有图层均支持。 |
| **Shadow / 投影** | 常用 | ✅ Yes | ✅ Tested | 支持 `{ type: "shadow", shadowType: "outer"|"inner", blur, offset, color }`。 |
| **Blur / 背景高斯模糊** | 可选 | ✅ Yes | ✅ Tested | 支持 `{ type: "blur", radius }` 与 `{ type: "background_blur", radius }`。 |
| **Gradient (渐变)** | 常用 | ✅ Yes | ✅ Tested | 支持 `linear`, `radial`, `angular` 渐变及多阶色彩停止点。 |
| **Boolean / 显隐开关 (`enabled`)** | **必须** | ✅ Yes | ✅ Tested | 节点支持 `enabled: true/false`，可由 manifest 状态机控制互斥（如精英0/1/2，潜能1~6，NO INFO）。 |
| **PNG Export** | **必须** | ✅ Yes | ✅ Tested | 官方支持 `Export([nodeId], "png", outputPath, { scale: 1 })`，实测可导出指定 Frame 为标准 1920×1080 图像。 |
| **无头运行 (Headless CLI)** | **必须** | ⚠️ 限制 | ⚠️ Audited | **重要发现**：官方 `Pen.exe` 是基于 Electron 的 GUI 应用，未内置类似 `pen render --headless input.pen` 的独立命令行渲染子命令。若通过官方 MCP 导出，必须在后台常驻 `Pen.exe` 桌面进程；但因 `.pen` 本质为清晰的 JSON 规范，**支持编写完全脱离 GUI 的 Headless Native Python/Canvas 渲染器**。 |

---

## 2. 关键发现与架构决策

1. **官方通道依赖 GUI 常驻**：
   - 如果完全依赖 pen.dev 官方的桌面宿主 + MCP 导出，工作机必须常驻运行 `Pen.exe`，且每个任务需保证当前窗口处于聚焦或打开状态。这在多任务自动化 CI/CD 环境下稳定性欠佳（易受 Windows 会话、屏幕锁屏、GPU 上下文丢失影响）。
2. **纯 JSON 规范带来的真正解耦**：
   - 官方 `.pen` 文件格式非常优雅透明（纯 JSON），不包含任何私有二进制加密或不可解构的黑盒。
   - 这意味着在架构上我们可以实现 **“设计在 pen.dev，生产在 PenRenderer”**：
     - **设计态 (Design-Time)**：在 pen.dev 可视化编辑器中创建、微调并维护 `report_5p_master.pen` 模板；
     - **生产态 (Production-Time)**：`PenRenderer` 直接读取 `.pen` 模板的 AST/JSON，根据 `scene.json` 完成数据合成与参数化计算，既可通过 MCP 驱动官方导出，亦可使用内置纯无头渲染引擎快速批量输出 1080P PNG。
