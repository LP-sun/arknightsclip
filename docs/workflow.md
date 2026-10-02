# 操作工作流

以下顺序以当前 `src/arknightsclip/cli.py` 的命令为准。先在项目根目录激活已安装项目的 Python 环境。

## 1. 配置与预检

1. 检查 `config/project.yaml`：`maa.adb_device`、PSD 模板路径、音频路径、五位玩家 ID/显示名。
2. 若需要在线采集，确认设备已被 ADB 识别，并在游戏内打开干员仓库。
3. 运行 `arknightsclip --help` 确认命令行可用。

不要把个人设备地址、本机绝对路径或玩家资料写入示例配置。

## 2. 获取玩家数据

```powershell
arknightsclip collect-player --player P1 --name "玩家 1" --pages 5
```

`--capture-cards` 和 `--save-pages` 默认开启。采集结果写入 `data/raw/P1/`；默认采用 `maa-operbox` 引擎。对每位玩家重复一次，并保持 `--player` 与配置中的 ID 一致。

已有仓库页截图时使用离线回放：

```powershell
arknightsclip replay-operbox data/raw/P1/operbox/pages --player P1
```

需要检查识别区域或去重行为时，在上述任一命令附加 `--debug-operbox`。

## 3. 合并与审阅数据

```powershell
arknightsclip merge-players
arknightsclip analyze-group
```

第一个命令生成 `data/normalized/five_players.json` 和 `five_players_inspection.xlsx`；第二个命令生成 `reports/group_stats.json` 与 `reports/group_stats.md`。先审阅检查表和统计报告，再进入素材/画面阶段。若识别错误，应回到对应玩家的原始页面重新采集或离线回放，而不是只修改下游清单。

## 4. 素材准备

```powershell
arknightsclip sync-assets
arknightsclip validate-assets --rarity 6
```

`sync-assets` 从已配置的历史来源复用素材；`validate-assets` 列出目标稀有度中缺少的立绘。验证出现缺失时，先补齐来源素材，再构建场景。必要时可运行 `arknightsclip spike-psd` 验证本机 PSD 操作链路。

## 5. 生成场景和时间线

```powershell
arknightsclip build-manifests
arknightsclip export-timeline --format all
```

前者在 `data/manifests/` 写出每位干员的五人槽位清单。后者在默认报告目录写出 FCP7 XML 和 OTIO；传入 `--output <路径>` 可在仅导出一种格式时覆盖输出文件。导入 DaVinci Resolve 后，确认媒体没有离线、分层轨道时长与配置 FPS 一致，再进行最终调色和渲染。

## 6. Production 视频渲染与导出

`renderers/production/` 是唯一核心视频渲染与导出入口。它读取生产契约，使用浏览器逐帧执行 `window.renderFrame(frame)`，然后用 ffmpeg 合成带音频的 MP4。`renderers/rhine/` 已废弃，仅用于历史排查。

> **视觉素材选型规范**：制作莱茵生命风格视频时，`psd2pen` **不是必选项**。制作时可自由选用：
> 1. `psd2pen` 产出的分层/矢量化 Pen 角色卡片；
> 2. 截图切割的角色矩形卡片（`data/raw/*/operbox/cards_raw/`）。
>
> 两者二选一即可投入渲染。此外，若视觉不满意，**仅限 Astra 模型**被允许创建新的 `.pen` 角色卡片素材（推荐使用 Pencil MCP，亦支持脚本/程序化辅助生成）。

### 6.1 生产契约与 Smoke 测试
```powershell
node renderers/production/build-production-data.mjs
cd renderers/production
..\rhine\node_modules\.bin\vite.cmd --config vite.config.mjs --host 127.0.0.1 --port 4173
node capture.mjs --base-url http://127.0.0.1:4173 --smoke
```
生产契约位于 `renderers/production/public/project.json`，当前基准视频为 `generated/rhine/main_export/rhine_operator_archive_final.mp4`。

### 6.2 完整 MP4 导出
```powershell
node capture.mjs --base-url http://127.0.0.1:4173 --out ..\..\generated\rhine\main_export
```
完整导出会写入 `generated/rhine/main_export/`，包括 PNG 序列、`capture-report.json` 和 `rhine_operator_archive_final.mp4`。

`renderers/rhine/` 已废弃，不应再运行或扩展。

## 常见问题

| 现象 | 优先检查 |
| --- | --- |
| `arknightsclip` 找不到 | 激活虚拟环境，并重新执行 `python -m pip install -e . PyYAML`。 |
| 采集失败 | ADB 设备地址、设备授权、游戏是否位于仓库页，以及 MAA/模板路径。 |
| 场景构建找不到数据集 | 先运行 `merge-players`，确认 `data/normalized/five_players.json` 存在。 |
| 素材验证缺失 | `assets/` 来源、干员 ID 与注册表映射；不要将其他干员素材替代。 |
| Resolve 中媒体离线或长度不对 | 检查导出 XML/OTIO 内路径、素材是否移动，以及 `davinci.fps` 与项目帧率。 |

## 回归验证

```powershell
python tests/run_tests.py
```

测试会写入部分可再生的标准化数据和临时目录；执行后请用 `git status` 区分预期生成物与待提交的代码/文档改动。
