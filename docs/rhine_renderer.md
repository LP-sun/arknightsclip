# Rhine Renderer (Production Source of Truth)

`renderers/rhine` 是本项目唯一正式的莱茵生命（Rhine Lab）UI 动态渲染管线后端。
Python 核心层负责数据采集、标准化、`SceneManifest` 与时间线；静态视觉资产以 `psd2pen` 为正式源头；本 TypeScript/Vite 渲染管线消费薄项目契约，并以帧寻址方式执行确定性图形渲染；最后可导出时间线与序列帧供 DaVinci Resolve 进行调色与母带制作。

---

## 架构与契约加载

### 1. 契约定义与位置
渲染器运行所需的项目契约位于：
`renderers/rhine/public/project.json` (Vite 开发与打包时直接挂载于根路径 `/project.json`)。

生成命令：
```powershell
python scripts/build_rhine_placeholder_project.py
```
该命令基于 `data/manifests/` 提取干员场景，同时写出：
* `renderers/rhine/public/project.json`（供渲染器即时读取）
* `generated/rhine/final_placeholder/project.json`（可再生审计留档）
* `reports/rhine_placeholder_inventory.md`（缺失素材与数据审阅报告）

### 2. 失败显式报错 (Fail Loudly)
渲染器严禁静默 fallback：
* 若 `/project.json` 加载失败（网络错误、HTTP 404/500 或 JSON 契约损坏），渲染器会立即设置 `window.__RHINE_RENDER_ERROR__` 并在画布上绘制醒目的深红致命错误横幅；
* 此时 `window.__RHINE_RENDER_READY__` 严格保持为 `false`；
* 渲染脚本与测试套件捕获到该状态后会直接中断退出，防止生成看似成功实则空白或缺省的无效帧。

---

## 确定性时间线与帧同步

### 1. `evaluate(frame)` 确定性求值
时间线求值核心位于 `renderers/rhine/src/timeline.js`。
* 函数签名：`evaluate(frame: number): FrameEvaluation`
* 所有相机位移、光效波纹（wave）和活跃干员索引均纯函数化地根据整型 `frame` 计算；
* 重复调用对同一帧的输出结果严格相同（`deepEqual`），不依赖系统时钟或渲染历史累计时间；
* 非法帧号（负数、小数、超出项目总帧数）均显式抛出 `RangeError`。

### 2. Playwright READY 状态机与防抢拍
自动化无头渲染器 `renderers/rhine/scripts/render-phase1.mjs`：
* 在渲染每个目标帧前，显式通过 `page.evaluate()` 将浏览器的 `__RHINE_RENDER_READY__` 重置为 `false`，彻底杜绝多帧间状态继承造成的时序竞争；
* 导航后使用 `page.waitForFunction()` 严格轮询等待 `window.__RHINE_RENDER_READY__ === true`；
* 若页面设置了 `window.__RHINE_RENDER_ERROR__`，立即抛出异常并以非零状态码退出。

---

## 运行与验证

进入 `renderers/rhine` 目录：

```powershell
# 1. 运行时间线评估器单元测试 (涵盖 0, 23, 24, 47, 48, 边界帧与异常测试)
npm test

# 2. 验证前端静态构建与打包产物
npm run build

# 3. 启动开发模式进行逐帧交互调试 (例如访问 http://localhost:5173/?frame=24)
npm run dev

# 4. 运行 Playwright 轻量烟雾测试 (自动捕获 0, 23, 24, 47, 48, 1007 关键帧)
npm run render:smoke

# 5. 执行全量 1008 帧确定性捕获
npm run render:phase1
```

---

## 历史实验与边界说明

* `experiments/rhine_pillow_mockup/`（原 `scripts/build_rhine_video.py`）仅作为早期 Pillow 静态视觉构思参考，不属于正式渲染器；
* 当前阶段输出为高清 PNG 图像序列；自动化的 ffmpeg 视频重压缩编码与 Resolve 轨道自动注入将在后续版本接入。
