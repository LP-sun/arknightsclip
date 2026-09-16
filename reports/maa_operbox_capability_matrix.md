# MAA OperBox 能力与数据字段矩阵 (MaaCore OperBox Capability Matrix)

本矩阵以官方 MaaAssistantArknights/MaaAssistantArknights (Commit 7e5de9b) 源码与本地运行时实测为准。

| Field | Native MaaCore | Existing in Analyzer | arknightsclip Extension | Extraction Method | Quality / Confidence |
|---|---|---|---|---|---|
| char_id | 是 (Yes) | 是 (box.id) | 注册表双重校验 (OperatorRegistry) | 官方 BattleData.find_first_oper 查表 | 高 (Deterministic) |
| name | 是 (Yes) | 是 (box.name) | 别名与错别字消歧 | OperNameAnalyzer + 字符二值化 OCR | 高 (0.95+) |
| own | 是 (Yes) | 是 (box.own=true) | 未拥有干员补全 (own=false) | 仓库列表在场检测 | 绝对 (Boolean) |
| elite | 是 (Yes) | 是 (box.elite) | 锚点相对偏移校验 | 模板匹配 (OperBoxFlagElite1/2.png) | 高 (0.85+) |
| level | 是 (Yes) | 是 (box.level) | 置信度校验与多尺度 OCR | OperBoxLevelOCR 区域数字 OCR | 中高 (无伪满级推断) |
| potential | 是 (Yes) | 是 (box.potential) | 默认潜1与模板比对 | 模板匹配 (OperBoxPotential2..6.png) | 高 (0.82+) |
| rarity | 是 (Yes) | 是 (box.rarity) | 注册表官方星级核验 | BattleData 静态数据表 | 绝对 (1..6) |
| card ROI | 部分 (仅锚点 flag_rect) | 是 (box.rect) | 扩展卡片全局视觉 ROI (visual_asset_roi) | 锚点偏移 + 边距扩展 | 高 (坐标几何推导) |
| source frame | 否 (内存析构) | 是 (m_image) | 完整原生分辨率页面保存 (pages/*.png) | 单次扫描控制器截屏捕获 | 绝对 (无压缩像素) |
| card PNG | 否 (原生不生成) | 否 | 单次扫描多投影裁切 (cards_raw/<id>.png) | 同一帧按照 card ROI 裁切落盘 | 绝对 (单次扫描副产物) |
| provenance | 否 | 否 | 完整 JSON 链路溯源 (<id>.json) | 记录 scan_id, page, roi, timestamp | 绝对 (可审计追溯) |
| mainSkillLevel | 否 (不支持) | 否 | 标记为 unavailable / null | 不支持视觉扫描 (需一图流 API) | N/A |
| skills | 否 (不支持) | 否 | 标记为 unavailable / null | 不支持视觉扫描 (需一图流 API) | N/A |
| equips | 否 (不支持) | 否 | 标记为 unavailable / null | 不支持视觉扫描 (需一图流 API) | N/A |

### 核心结论
1. 真实练度字段支持度：own, elite, level, potential, rarity 五大基础培养状态在 MaaCore 中全部原生支持视觉提取，无需使用精二默认90级或精一默认60级的任何猜测逻辑。
2. 素材与状态同源性 (Single-Scan Dual-Output)：由于 MaaCore 在识别卡片时已经取得了 cv::Mat m_image 和角标 box.rect，我们通过在同一扫描循环中加入卡片矩形扩展与质量评估逻辑，实现同一次 UI 遍历、两路投影直接落盘，无需二次遍历游戏仓库。
