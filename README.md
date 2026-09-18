# 明日方舟报菜名

将多位玩家的《明日方舟》干员仓库数据整理为五人对比画面，并导出可在 DaVinci Resolve 中继续编辑的分层时间线。项目覆盖数据采集、干员状态归一化、素材校验、场景清单生成和时间线导出；PSD 渲染与 Resolve 内的最终调色/特效仍需按本机环境完成。

## 当前入口与仓库状态

当前维护入口是 `src/arknightsclip/` 提供的 `arknightsclip` CLI，干员仓库采集与识别的唯一正式生产实现为 `src/arknightsclip/maa/operbox_collector.py` 与 `operbox_analyzer.py`。早期根目录脚本已统一归档至 `archive/legacy_collection_pipeline/`，仅作为历史记录追溯。

Pen/Pencil 相关功能以 [`psd2pen/`](psd2pen/) 为唯一正式实现和后续开发入口。它基于真实 PSD 视觉资产，推荐通过 Pencil MCP 完成编辑、截图与原生导出，亦允许脚本/代码辅助生成。`experiments/pen_renderer/` 和 `experiments/react_renderer/` 仅保留为早期效果较差的技术原型，不代表当前视觉质量，不得作为正式渲染管线、视觉基准或新功能落点。

Rhine 动态 renderer 位于 [`renderers/rhine/`](renderers/rhine/)，**当前状态为 WIP / 未完成**。它是后续唯一继续维护的 Rhine renderer 路径，但尚不视为 production-ready 或最终视频交付链路。制作莱茵生命风格呈现时，`psd2pen` 不是必选项，可灵活在 `psd2pen` 分层卡片与直接由截图切割的角色矩形卡片中二选一；视觉不满意时仅限 Astra 模型被允许创建新的 `.pen` 角色卡片素材（推荐使用 Pencil MCP 交互设计，亦支持脚本辅助生成）。具体规范见 [`docs/rhine_renderer.md`](docs/rhine_renderer.md)。

运行 `python tests/run_tests.py` 执行当前核心测试套件，覆盖数据模型、OperBox 解析、素材关联、场景清单和 24 fps 时间线生成。

## 快速开始

环境要求：Python 3.10+。采集阶段还需要可用的 ADB、模拟器/设备与 MAA；需要使用 Photoshop 后端时，还需要本机 Photoshop。仅运行离线数据处理、场景和时间线功能不需要这些外部程序。

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e . PyYAML

arknightsclip --help
python tests/run_tests.py
```

若未安装为可编辑包，也可以临时设置 `PYTHONPATH=src` 后执行 `python -m arknightsclip --help`。

开始前，从 [`config/project.example.yaml`](config/project.example.yaml) 复制或检查本地 [`config/project.yaml`](config/project.yaml)，至少确认 ADB 设备地址、素材/PSD 路径和五位玩家资料。配置文件可能包含本机路径与玩家信息，不应直接作为通用配置分发。

## 常用工作流

完整的输入、输出和检查点见 [`docs/workflow.md`](docs/workflow.md)。

```text
仓库页截图 / ADB 采集 → data/raw/<玩家>/ → merge-players
→ data/normalized/five_players.json → sync-assets + validate-assets
→ data/manifests/<干员>.json → export-timeline → DaVinci Resolve
```

```powershell
arknightsclip collect-player --player P1 --name "玩家 1" --pages 5
arknightsclip replay-operbox data/raw/P1/operbox/pages --player P1
arknightsclip merge-players
arknightsclip analyze-group
arknightsclip sync-assets
arknightsclip validate-assets --rarity 6
arknightsclip build-manifests
arknightsclip export-timeline --format all
```

## 项目结构

| 位置 | 作用 |
| --- | --- |
| `src/arknightsclip/` | 当前维护中的 Python 包与命令行入口。 |
| `config/` | 项目、设备、PSD 和玩家配置。 |
| `data/` | 公开数据集与标准化数据（治理规范参见 [`data/README.md`](data/README.md)）。 |
| `data/raw/` | 每位玩家的公开、可复现原始采集结果与仓库页截图。 |
| `data/normalized/` | 合并后的唯一事实源 `five_players.json` 与人工检查表。 |
| `data/manifests/` | 每位干员一份 `SceneManifest`，供图形和时间线阶段消费。 |
| `renderers/rhine/` | **WIP / 未完成**的 Rhine 风格动态 renderer；作为后续唯一维护路径，但当前不宣称 production-ready。 |
| `psd2pen/` | 唯一正式的 Pen/Pencil 实现、模板、自动化与验收交付。 |
| `assets/`、`generated/` | 素材缓存与可再生的图形输出。 |
| `experiments/rhine_pillow_mockup/` | 早期静态视觉探索原型，非正式渲染器。 |
| `experiments/pen_renderer/` | 已弃用的早期无头 PenRenderer 原型，仅供历史参考。 |
| `experiments/react_renderer/` | 效果较差的对照原型，不属于正式 Pen 管线。 |
| `reports/` | 统计、时间线与历史验收/技术报告；索引见 [`reports/README.md`](reports/README.md)。 |
| `tests/` | 核心数据模型、采集解析、场景和时间线测试。 |

<details>
<summary><b>历史归档与早期交付记录 (archive/，点击展开)</b></summary>

项目早期迭代中的探索性单图渲染、切刀分析、历史中间状态 JSON、图层契约及交付成片已完整收拢归档至 `archive/`（包含 `legacy_scripts/`、`legacy_data/`、`legacy_deliveries/` 等），与当前主生产管线解耦保持根目录整洁。详细索引请参见 [`archive/README.md`](archive/README.md)。
</details>

## 文档导航

- [`docs/DOCUMENTATION_GUIDE.md`](docs/DOCUMENTATION_GUIDE.md)：文档结构、语气与限制性表述约定。

- [`docs/architecture.md`](docs/architecture.md)：模块职责、数据契约和外部依赖边界。
- [`docs/workflow.md`](docs/workflow.md)：可复现的操作顺序、产物与排错入口。
- [`docs/rhine_renderer.md`](docs/rhine_renderer.md)：Rhine 动态 renderer 当前 WIP 状态、契约、Smoke 测试与未完成项。
- [`data/README.md`](data/README.md)：公开数据集定义与治理规范。
- [`docs/REPOSITORY_GOVERNANCE.md`](docs/REPOSITORY_GOVERNANCE.md)：仓库分支治理与合并规范。
- [`reports/README.md`](reports/README.md)：现有报告的分类、时效性与阅读顺序。
- [`psd2pen/AUTOMATION.md`](psd2pen/AUTOMATION.md)：PSD 转 Pen 子项目的自动化说明。

## 开发与验证

```powershell
python tests/run_tests.py
```

生成类命令会写入 `data/` 或 `reports/`；执行前请确认当前本地素材和配置可被覆盖。

## 许可与素材

本仓库包含或引用游戏相关素材及大型视频/PSD 文件。使用、分发和公开发布前，请自行确认游戏素材、音乐、模板和第三方工具的授权条件。
