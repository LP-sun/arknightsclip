# Rhine Pillow Visual Mockup (Historical Experiment)

This is a historical / rapid visual mockup.
It is not the production Rhine renderer.

**Production source of truth: `renderers/rhine/`**

---

## 说明

本目录下的 `build_rhine_video.py` 是早期用于快速验证莱茵生命（Rhine Lab）UI 视觉风格（档案网格、暖白底色、琥珀色扫光、干员状态栏）的 Pillow 原型脚本。

其定位为**探索性实验/视觉原型**，不具备生产级时间线控制、帧级精确回放或与 DaVinci Resolve / Playwright 对接的能力。

正式的生产级 Rhine 动态渲染管线请使用：
`renderers/rhine/` (基于 TypeScript / Vite / HTML5 Canvas / Playwright / Three.js 资产标准)。
