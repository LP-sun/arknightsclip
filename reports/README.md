# 报告索引

`reports/` 同时保存当前流水线的输出和历史技术/验收记录。报告是某次素材、配置和时间线状态的快照；除非报告明确说明，否则不应把其中的数量、路径或结论视为当前运行结果。

## Pen/Pencil 报告的现行结论

`psd2pen/` 是唯一完整、正式的 Pen/Pencil 实现，也是唯一允许继续开发和进行视觉验收的入口。`experiments/pen_renderer/` 与 `experiments/react_renderer/` 的视觉效果均更差，只保留为历史原型。

所有 `pen_*`、`renderer_ab_*`、`renderer_benchmark*` 和 `renderer_stability.md` 均为旧实验报告。其中关于“高度忠于 PSD”“90%+ 还原”“推荐 PenRenderer/React 或混合架构”等判断已经失效，已由 `psd2pen/` 的真实 Pencil MCP 制作及验收结果取代。不得据此恢复旧路线或选择生产渲染器。

现行 Pen 文档与验收证据请从 [`../psd2pen/AUTOMATION.md`](../psd2pen/AUTOMATION.md) 和 [`../psd2pen/delivery/`](../psd2pen/delivery/) 开始阅读。

## 当前可再生输出

| 文件 | 由何命令生成 | 用途 |
| --- | --- | --- |
| `group_stats.json`、`group_stats.md` | `analyze-group` | 五位玩家的干员与练度统计。 |
| `timeline_v2_layered.xml`、`timeline_v2_layered.otio` | `export-timeline` 或历史导出脚本 | 导入剪辑软件的分层时间线。 |
| `render_report.json` | 渲染/导出阶段 | 记录一次渲染结果。 |

## 历史技术记录

| 报告 | 内容 |
| --- | --- |
| `maa_operbox_*.md` | OperBox 采集能力、缓存、来源与技术验证。 |
| `photoshop_spike_report.md` | Photoshop 单槽位自动化验证。 |
| `template_analysis.md` | 模板层级/结构分析。 |
| `edit_report.md`、`final_edit_report.md` | 特定版本时间线的编辑与验收快照。 |
| `maa_integration_report.md` | MAA 集成阶段记录。 |
| `pen_*`、`renderer_*` | 已被 `psd2pen/` 取代的旧渲染器实验、比较和决策记录。 |

历史报告的原始文件保留不改，以便追溯当时结论。阅读前应先查看生成日期和引用的成片/模板版本，并与当前 `config/project.yaml`、`data/normalized/` 和实际素材目录交叉确认。

更完整的现行操作说明请见 [`../docs/workflow.md`](../docs/workflow.md)，模块与数据契约见 [`../docs/architecture.md`](../docs/architecture.md)。
