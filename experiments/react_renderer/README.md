# React/CSS Renderer Spike (`experiments/react_renderer`)

本目录实现了基于 **React 19 + CSS + Playwright (Headless Chromium/Edge)** 的数据驱动报菜名自动化平面渲染后端 Spike。

## 1. 架构设计

* **数据与素材解耦**：与 `pen_renderer` 共享 `experiments/shared/` 下的统一业务输入：
  * `shared/manifests/`：场景描述 JSON（包含干员 ID、立绘、玩家持有时/未持有时状态数据）
  * `shared/assets/`：干员立绘、博士头像、UI 徽章素材
  * `shared/layout/report_5p_layout.json`：五人战术卡片与中央干员的绝对几何坐标契约
* **组件化复用**：
  * `src/components/ReportScene.tsx`：1920×1080 根场景容器
  * `src/components/PlayerCard.tsx`：五位玩家完全复用的单一卡片组件
  * `src/components/DoctorInfo.tsx`：博士头像、名称、等级信息
  * `src/components/OperatorCard.tsx`：持有干员时的半身立绘、等级、精英度与潜能徽章
  * `src/components/NoInfo.tsx`：未持有状态下的战术斜线水印
* **渲染内核**：
  * `src/render/renderScene.ts`：通过 `react-dom/server` 进行 SSR 拼接 HTML，通过 Playwright 加载本地 `file:///` 资源、等待 `document.fonts.ready` 与全量图片加载完成，以 `deviceScaleFactor: 1` 精确截取 1920×1080 无损 PNG。

## 2. 快速运行

```bash
# 进入目录
cd experiments/react_renderer

# 安装依赖
npm install

# 渲染单场景
npm run render -- --manifest ../shared/manifests/exusiai_test.json --output outputs/exusiai_test.png

# 批量渲染 shared/manifests 下的所有场景
npm run render-batch
```

## 3. 字体依赖说明

* 数字排版：系统内置 `Impact`
* 中文文本：优先匹配 `Microsoft YaHei`（微软雅黑）、备选 `SimHei`（黑体）
* 在 Playwright 中显式调用 `await document.fonts.ready`，杜绝字体未加载完成即截图的问题。
