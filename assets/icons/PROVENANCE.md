# Scale-Safe Status Icons Provenance & Specification

## 1. 概述 (Overview)
本项目用于 Rhine Lab 动态视频生成渲染管线。在 1080p 分辨率及更大画幅下，MAA 原始约 17–48 px 的切片图标直接放大容易产生明显像素锯齿或双线性模糊。

为此，本目录提供一组具有清晰明日方舟语义、几何精度统一、矢量无损的 SVG 状态图标集：
- 精英化阶段: `elite_0.svg`, `elite_1.svg`, `elite_2.svg`
- 潜能等级: `potential_1.svg` ~ `potential_6.svg`
- 基础八大职业: `profession_pioneer.svg`, `profession_warrior.svg`, `profession_sniper.svg`, `profession_tank.svg`, `profession_medic.svg`, `profession_support.svg`, `profession_caster.svg`, `profession_special.svg`

## 2. 知识产权与免责声明 (License & Attribution)
- **非官方原始素材**: 本目录下的 SVG 图标均为基于明日方舟游戏内公共语义与几何特征编写的**程序化/矢量重构版本**，用于满足高分辨率渲染需求；
- 严禁声称本 SVG 集合为鹰角网络 (Hypergryph) 官方导出的原始矢量资产；
- 原始游戏内设计著作权归上海鹰角网络科技有限公司所有。

## 3. 渲染使用策略 (Usage Policy)
- **优先策略**: Renderer 必须优先使用 `assets/icons/svg/` 中的高清晰度/矢量资源；
- **优雅降级 (Fallback)**: 若矢量资源不可用，可降级读取 `psd2pen/assets/psd_sources/` 或 MAA raster 小图；
- **尺寸安全限制**: 对低分辨率 raster 图标（<=48px），严禁在界面中以 nearest-neighbor 放大至 96px 以上，必须限制显示尺寸或在外围包裹矢量设计框，避免视觉马赛克。
