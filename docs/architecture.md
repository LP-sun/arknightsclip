# 架构与数据契约

`arknightsclip` 将“玩家拥有的干员状态”和“用于画面合成的素材”分离保存，再用场景清单连接。这样可在不重复采集的情况下重新生成统计、卡片图形与时间线。

## 完整管线架构

```text
OperBox (MAA/ADB/离线回放)
       │
       ▼
data/raw/ (公开、可复现基准数据集 P1–P5)
       │
       ▼
data/normalized/five_players.json (五人规范化唯一事实源)
       │
       ▼
data/manifests/<char_id>.json (SceneManifest 场景清单)
       │
       ├──────────────────────────────────────────────┐
       ▼                                              ▼
静态素材源 A: psd2pen/                     静态素材源 B: cards_raw/
(分层/矢量化 Pen 角色卡片)                 (仓库页截图切割的角色矩形切图)
       │                                              │
       └──────────────────────┬───────────────────────┘
                              ▼ (二选一使用即可)
                       renderers/rhine/
                   (WIP Rhine 动态 renderer)
                              │
                              ▼
                  时间线导出 (FCPXML / OTIO)
                              ▼
                     DaVinci Resolve / 最终合成
```

> **视觉素材规范**：制作莱茵风格动态呈现时，`psd2pen` **不是必选项**。管线支持在 `psd2pen` 产出卡片与游戏仓库截图切割的角色矩形卡片（`data/raw/*/operbox/cards_raw/`）中自由选择使用。若对视觉不满意，**仅限 Astra 模型**被授权创建新的 `.pen` 角色卡片素材（推荐使用 Pencil MCP 交互设计，亦允许脚本/代码辅助生成）。
>
> `renderers/rhine/` 是后续唯一维护的 Rhine renderer 路径，但当前明确处于 **WIP / 未完成** 状态，不视为 production-ready 或最终交付链路。已知 TODO 见 `docs/rhine_renderer.md`。

## 模块边界

| 模块 | 位置 | 职责 |
| --- | --- | --- |
| 配置 | `config.py` | 加载 YAML，解析相对项目根目录的路径。 |
| 干员注册表 | `registry/` | 将识别结果归一为 `char_id`、中文名、职业和稀有度。 |
| 采集与识别 | `maa/` | 经 MAA/ADB 获取仓库页，提取卡片及练度；支持从已保存页面离线回放。 |
| 数据集 | `data/`、`models/player.py` | 合并每位玩家的原始结果，形成五人唯一事实源。治理规范见 `data/README.md`。 |
| 素材解析 | `assets/` | 查找/同步干员立绘和玩家卡片切图，并检查缺失素材。 |
| 场景构建 | `scene/`、`models/scene.py` | 为每位干员生成五个玩家槽位的 `SceneManifest`。 |
| 静态视觉 | `psd2pen/` | 正式静态 Box 布局与 Pencil 视觉资产管线（建议使用 Pencil MCP 编辑，支持脚本生成）。 |
| 动态渲染 | `renderers/rhine/` | WIP Rhine 风格动态 renderer（TypeScript / Vite / Canvas / Playwright）；当前不宣称 production-ready。 |
| 时间线 | `timeline/` | 根据分层图形和时长配置生成 FCP7 XML 或 OTIO。 |

## 关键文件与契约

| 文件 | 生产者 | 消费者 | 约束 |
| --- | --- | --- | --- |
| `data/raw/<P?>/` | `collect-player` / `replay-operbox` | `merge-players` | 原始页面、识别状态和素材溯源；不要手工改写以免丢失审计依据。 |
| `data/normalized/five_players.json` | `merge-players` | `analyze-group`、`build-manifests` | 五位玩家的规范化唯一事实源。 |
| `assets/` | `sync-assets`、采集器 | `build-manifests`、渲染阶段 | 缺失立绘或卡片时应先补齐素材，不应用错误素材替代。 |
| `data/manifests/<char_id>.json` | `build-manifests` | 图形/时间线阶段 | 每个玩家槽位必须满足拥有状态和 `no_info` 的互斥规则。 |
| `reports/group_stats.*` | `analyze-group` | 人工审阅 | 统计的可读报告与 JSON 数据。 |
| `reports/*.xml`、`reports/*.otio` | `export-timeline` | DaVinci Resolve / OTIO 工具 | 时间线按配置 FPS 生成；当前配置目标为 24 fps。 |

## 场景状态规则

`PlayerSlotState` 的呈现契约如下：

- 已拥有：`own=true`、`no_info=false`；精英化为 0–2、潜能为 1–6、等级为 1–90，卡片素材可选。
- 未拥有：`own=false`、`no_info=true`，且不得关联玩家卡片素材。

这条规则让“未拥有”成为明确的画面状态，而非用其他干员或空数据伪装。

## 外部系统

- MAA/ADB：仅采集阶段需要；设备、ADB 和滑动参数配置在 `maa` 节。
- Photoshop：PSD 实际渲染或技术验证需要；后端由 `photoshop.backend` 控制。
- DaVinci Resolve：导入 XML/OTIO 后完成最终合成、调色、特效和交付渲染。

根目录的早期脚本已归档至 `archive/legacy_collection_pipeline/`，服务于历史制作追溯，不是当前生产接口。

## OperBox production source of truth

Production collection code lives only in:

- `src/arknightsclip/maa/operbox_collector.py`
- `src/arknightsclip/maa/operbox_analyzer.py`

Do not introduce a second OperBox collector or recognizer.

Do not restore FallbackOperBoxRecognizer.

Do not migrate the production collection flow to MaaCore without an explicit architecture decision.

Historical collection scripts are read-only references and must not receive new functionality.
