# 左 3＋右 2 五卡交付验收

验收日期：2026-09-16。已完成模板制作、真实统计 JSON 批量生成、原生导出、保存重开及独立命令行执行。

## 交付

- 原生文档：`../character_cards_5slot.pen`。
- 正式画板：`CHARACTER_CARDS_1920x1080_3L_2R`，节点 `ja7Jk`。
- 五角色图片：`five_slot_run_001/能天使/character_cards.png`、`推王/character_cards.png`、`小火龙/character_cards.png`、`小羊/character_cards.png`、`洁哥/character_cards.png`，后四者同属 `five_slot_run_001` 目录。
- JSON 输入：`../inputs/five_operators.json`。推王 hmi 精英化沿用已确认的 2。
- 一键入口：`../scripts/generate_five_cards.ps1`；详细操作：`../AUTOMATION.md`。

## 布局与数据

画布 1920×1080，RGBA 透明。继承已验收八卡组件，仅显示源槽位 1、2、3、5、6，隐藏 4、7、8，保持原始位置和比例。对应玩家为爱花、咯咯枝、东城、hmi、leo。每个角色仍保留八个可编辑组件实例和原始练度数据。

五个画板共 40 个槽位完成精英、等级、潜能、人物素材、裁切路径和可见性读回比对；25 个可见卡位全部正确。能天使左一、洁哥左二保留统计表要求的 NO INFO。

## 验证结果

| 验证 | 结果与证据 |
| --- | --- |
| 原生截图与导出 | 五角色均经 `TakeScreenshot`、`Export(scale:1)`；`five_slot_run_001/*/mcp_response.json` |
| 数据读回 | 5/5 PASS；各角色 `receipt.json` 绑定输入、脚本、导出 SHA-256 |
| PNG | 5/5 PASS，1920×1080 RGBA，中央与外围透明，隐藏卡位无残留；`five_slot_run_001/verification.json` |
| 保存与重开 | 用户完成保存、关闭、重新打开；Pencil 重新读取正式模板及五画板并独立导出 |
| 重开一致性 | 正式模板与五角色图片均逐字节一致；`five_slot_reopened/verification.json` |
| 独立脚本全流程 | prepare 后，`pencil_batch.py run` 通过本机官方 Pencil MCP stdio 连续生成五角色，退出码 0；`five_slot_cli_001/verification.json` |
| 命令行与原生工具一致性 | 五角色标准 PNG 均逐字节一致 |
| 脚本回归 | 9 项测试通过，包括五卡预设保留八实例、原有状态规则及过期输入拒绝 |
| 8slot 基线 | SHA-256 未改变：`cba070fc871228e7adbfd605fd210b09ea3b0fd82db5b7349f478e42d261ea0c` |

保存后的 5slot 文档 SHA-256：`5ebbc91e66ab5d0cd6c5cfca87f7a8e82175304e3f69564ec5b541733d8a2889`。

## 运行边界

必须运行 Pen.dev 并打开目标 5slot 文档。PNG 批量生成、结果记录与验收已实现脚本化；原生文档保存／关闭／重开没有 MCP API，仍由应用完成。本轮已真实执行该人工步骤。

原 QA、实验与八卡参考画板保留在新文档内，不进入指定五卡 PNG 导出。等级字体沿用已接受模板中的 Barlow Semi Condensed 近似；未重做单卡视觉设计。

本机验证使用 Python 3.13、mcp 1.30.0、Pillow 12.3.0。Pillow 只读原生图片做透明度检查。Windows 沙箱阻止官方 MCP 进程管道时，需要在正常用户终端或经授权的执行环境运行；不存在其他渲染器兜底。
