# arknightsclip 视觉资产审计报告 (Visual Asset Baseline Audit)

## 1. 干员数据与立绘 (Operators & Hero Art)
- **五玩家总去重干员数**: 254
- **SceneManifest 覆盖干员数 (6星主干)**: 146
- **各玩家原始干员数**: {"P1": 146, "P2": 221, "P3": 124, "P4": 122, "P5": 120}
- **Hero Art (full.png) 现有目录数**: 60
- **Manifest 缺失 Hero Art 数量**: 87 (占比 59.6%)
- **全量干员缺失 Hero Art 数量**: 195

### 重复立绘哈希 (Duplicate Hero Art Hashes)
- **SHA-256 `0bbe7c6f41924c30...`**: `char_103_angel, char_222_bpipe`
- **SHA-256 `d4205d69e6f0d38c...`**: `char_332_archet, char_436_whispr`
- **SHA-256 `df02fb9656046502...`**: `char_456_ash, char_472_pasngr`

## 2. 原始卡片资产 (cards_raw)
- **总计 cards_raw 切片数**: 633
- **各玩家切片数**: {"P1": 52, "P2": 215, "P3": 124, "P4": 122, "P5": 120}
- **分辨率分布**:
  - `220x447`: 229 张
  - `269x546`: 124 张
  - `177x359`: 122 张
  - `240x488`: 120 张
  - `147x298`: 38 张
- **宽高比范围 (H/W)**: 2.0272 ~ 2.0333 (基准比例约 2.03)

## 3. 玩家资料卡 (player_cards)
- **现存可用**: 4 / 5
- **缺失玩家**: 1 (具体详情如下)
- **P1**: ✓ P1.png (1325x746, .png)
- **P2**: ✓ P2.png (1918x1078, .png)
- **P3**: ✓ P3.jpg (2800x1289, .jpg)
- **P4**: ✗ MISSING
- **P5**: ✓ P5.jpg (2556x1179, .jpg)

## 4. Pen 矢量设计工程依赖 (Pen Asset References)
- **character_card_components.pen**:
  - 总引用数: 4 (去重 3)
  - 本地存在: 3
  - 缺失引用: 0
- **character_cards_5slot.pen**:
  - 总引用数: 288 (去重 55)
  - 本地存在: 55
  - 缺失引用: 0
- **character_cards_5slot_template.pen**:
  - 总引用数: 2053 (去重 166)
  - 本地存在: 55
  - 缺失引用: 111
  - 缺失文件类型示例: `['assets/raw_batch/char_003_kalts_1.png', 'assets/raw_batch/char_010_chen_1.png', 'assets/raw_batch/char_017_huang_1.png', 'assets/raw_batch/char_1012_skadi2_1.png', 'assets/raw_batch/char_1013_chen2_1.png']` ... (共 111 项)
- **character_cards_8slot.pen**:
  - 总引用数: 156 (去重 55)
  - 本地存在: 55
  - 缺失引用: 0
