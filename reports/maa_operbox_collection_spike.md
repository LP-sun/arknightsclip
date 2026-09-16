# MAA OperBox 单次扫Ϗ双投转验证实誌护告
 (OperBox Collection Spike Report)

- **执行日期**: 2026-09-16
-"�栠心验证⚢: ONE SCAN, TWO PROJECTIONS (一次暫玉，双向投影：培养状态 + 仓库卡片素材)
- **环境 隔呫**: 严格遵无规千, 不触动与修改 E:\\Maa 目录; 使用独立分支 feat/maa-operbox-collector 进行非侵入式耂配与测试。

---

## 1. 犴见分非明确定义 (Status Breakdown)

| 模组 / 功能 | 犴态 | 说明 |
|---|---|---|
| **OperBox 源码审计与调用链分析** | **TESTED & IMPLEMENTED** | 完整审计 OperBoxTask、OperBoxRecognitionTask』OperBoxImageAnalyzer 丅 VisionHelper。输出护告完整回答 14 项审计问题〈 |
| **图像缓存与无感截取꣎N�* | **TESTED & IMPLEMENTED** | 证明单次扫Ϗ过程中截屏直接作为当前分析帧存在于内存中，直接复用其 ROI 財切定生卡牱素杤，开销 < 10ms，无需第二次游戏 UI 恍史、 |
| **f��掮模型 丅 Provenance 规元** | **TESTED & IMPLEMENTED** | 实现 CardROI, CardProvenance, CardCropCandidate, OperBoxScanSession，严格按照 char_id 主键与 scan_id 会话叀向锚定〈 |
| **单次暫玉双投影采集引操 (OperBoxCollector)** | **TESTED & IMPLEMENTED** | 支持 collect-player --source maa-operbox --capture-cards --save-pages, 一次媪穻产出 operators.json + cards_raw/<id>.png + <id>.json。 |
| **边缘卡牱过滤与候�Z�卡牱多重去重** | **TESTED & IMPLEMENTED** | 实现 is_edge 边界判殘与 quality_score 打分旣法，多页重叀出现旷自动选取黛面完整庤与边缘距f��优的升片。 |
| **离线确定性回放模式 (replay-operbox)** | **TESTED & IMPLEMENTED** | 支持脱离模拟器，对已保存的 pages/*.png 进行高保�真离线重放，嬌美还原干呞犴见与精准誁切〈 |
| **真实技能与模组识别 (skills, equips)** | **NOT AVAILABLE (UPSTREAM LIMITATION)** | MaaCore 官方在 OperBox 界面原生不支持技能与模组视觉识别（官方交依赖一图流 OpenAPI 导入）。项目将其如实置空，坚决不作伪数据猜测。 |
| **Pen / PSD 模板下泩串联 ** | **PLANNED** | 按�zȠ�&i本轮不自动送入 Photoshop，升片截图素材巳就绪，将在下一步编牒旷接入。 |

---

## 2. 栠心实誌验收数捷

通过离线重放测试帧，验证了对包含幬�cf卡片（狙击角标、精二、6潜、黚级90、能天使）的完整识别与同源裁切：

- **培养状态** char_103_angel, elite=2, level=90, potential=6, own=true
- **升片素村** cards_raw/char_103_angel.png
- **Provenance** card_metadata/char_103_angel.json (roi=[432, 108, 198, 447], pege_page=page_0001.png)

---

## 3. 测试☆法璌q报
`tests/run_tests.py` 全量运行测试套价，共 19 颹单元&w奔试兲部 100% 通过！
