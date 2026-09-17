# BGM 使用指南（当前正式版本）

## 音频与演示视频

正式 BGM 为 `bgm及使用指南/明日方舟报菜名（女神异闻录3  月行水上）.mp3`，时长约
186.296 秒。配套演示视频 `bgm使用例.mp4` 为 1920×1080、30 fps、约 186.24 秒，
用于理解画面节奏和干员唱名顺序，不作为当前视频的帧率来源。

## 当前顺序

`干员顺序.txt` 是本 BGM 版本的顺序事实源，共 137 位干员。制作脚本按文本顺序读取，
不按 operator_id 排序；生成的 `operator_sequence.json` 保存了每位干员的序号、名称、
operator_id、卡片路径和时长，便于审计。文本中与当前归一化数据不完全同名的条目仍保留
原唱名，并在 manifest 中以缺失 `operator_id` 标记。

## 帧与卡点规则

- 时间线 24 fps，视频 4470 帧（186.25 秒）。
- 片头 50 帧；这是历史 BGM 版本的实际片头值。
- 普通干员 24 帧（1 秒，约 2 个音乐 beat），使用 Hard Cut。
- 特殊段落沿用 `archive/legacy_data/durations_24fps_perfect.json`：傀影 98f、浊心斯卡蒂 194f、归溟幽灵鲨 321f、凯尔希·思衡托 185f 等。
- BGM 是音频参考，不能反向改变帧数；音频超出 186.25 秒时裁切尾部。

## 制作与检查

运行 `python scripts/build_bgm_guided_video.py`。输出目录为
`generated/rhine/bgm_guided_v1/`，包含 MP4、逐帧 PNG 和 `operator_sequence.json`。
用 ffprobe 检查 1920×1080、24/1 fps、4470 帧、H.264/AAC；抽查片头末帧、第一位干员、
特殊长留存起点以及最后一位干员的切换点。

本版本不使用 pen、不调用 DaVinci MCP；卡片直接读取各玩家
`data/raw/P*/operbox/cards_raw/*.png`。
