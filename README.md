# 明日方舟报菜名

将多位玩家的《明日方舟》干员仓库数据整理为五人对比画面，并导出可在 DaVinci Resolve 中继续编辑的分层时间线。项目覆盖数据采集、干员状态归一化、素材校验、场景清单生成和时间线导出；PSD 渲染与 Resolve 内的最终调色/特效仍需按本机环境完成。

## 当前入口与仓库状态

当前维护入口是 `src/arknightsclip/` 提供的 `arknightsclip` CLI，干员仓库采集与识别的唯一正式生产实现为 `src/arknightsclip/maa/operbox_collector.py` 与 `operbox_analyzer.py`。早期根目录脚本已统一归档至 `archive/legacy_collection_pipeline/`，仅作为历史记录追溯。

截至本次整理，`python tests/run_tests.py` 已通过 23 项核心测试，覆盖数据模型、OperBox 解析、素材关联、场景清单和 24 fps 时间线生成。

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
| `data/raw/` | 每位玩家的原始采集结果与仓库页截图。 |
| `data/normalized/` | 合并后的唯一事实源 `five_players.json` 与人工检查表。 |
| `data/manifests/` | 每位干员一份 `SceneManifest`，供图形和时间线阶段消费。 |
| `assets/`、`generated/` | 素材缓存与可再生的图形输出。 |
| `reports/` | 统计、时间线与历史验收/技术报告；索引见 [`reports/README.md`](reports/README.md)。 |
| `tests/` | 核心数据模型、采集解析、场景和时间线测试。 |
| 根目录旧脚本与 `archive/` | 早期实验和交付记录。 |

## 文档导航

- [`docs/architecture.md`](docs/architecture.md)：模块职责、数据契约和外部依赖边界。
- [`docs/workflow.md`](docs/workflow.md)：可复现的操作顺序、产物与排错入口。
- [`reports/README.md`](reports/README.md)：现有报告的分类、时效性与阅读顺序。
- [`psd2pen/AUTOMATION.md`](psd2pen/AUTOMATION.md)：PSD 转 Pen 子项目的自动化说明。

## 开发与验证

```powershell
python tests/run_tests.py
```

生成类命令会写入 `data/` 或 `reports/`；执行前请确认当前本地素材和配置可被覆盖。

## 许可与素材

本仓库包含或引用游戏相关素材及大型视频/PSD 文件。使用、分发和公开发布前，请自行确认游戏素材、音乐、模板和第三方工具的授权条件。
