# MaaCore 原生干员识别 (OperBox) 技术审计与集成报告

- **报告时间**：2026-09-14
- **目标**：基于 MAA (MaaAssistantArknights) 原版 C++ / Python 源码，深入调研 MaaCore 的实际 API、Task 声明、事件 Payload 与返回结构，确立真实 MaaCore 对接与 Fallback 视觉采集体系。

---

## 1. MaaCore 官方 OperBox 实现审计

通过对 MAA 仓库 `src/MaaCore/Task/Miscellaneous/OperBoxRecognitionTask.cpp` 与 `src/MaaCore/Vision/Oper/OperBoxImageAnalyzer.cpp` 的源码逆向审计：

### 1.1 官方 Task 机制与启动流程
1. **任务标识**：`OperBoxRecognitionTask`
2. **入场与前置动作** (`resource/tasks/tasks.json`)：
   - `OperBox`：检查或点击大厅“干员”按钮 (`OperBoxDefault`，720P ROI `[935, 300, 265, 110]`)
   - `OperBoxSortTabSelect`：OCR 识别并点击“等级”升降序标签，强制按等级降序排列
   - `OperBoxRoleTabSelect`：展开/折叠职业筛选栏
3. **循环翻页** (`OperBoxSlowlySwipeToTheRight`)：
   - 从 `(1090, 350)` 滑动至 `(100, 350)`，单次位移 990px（约 6 个干员宽度）
   - 终止条件：连续 3 次滑动后，屏幕末尾干员名称相同（到达列表终点）

### 1.2 官方回调事件与数据 Payload
当 `OperBoxRecognitionTask` 执行时，MaaCore 通过异步事件通道派发：
- **事件类型**：`AsstMsg::SubTaskExtraInfo`
- **Payload 顶层结构**：
  ```json
  {
    "what": "OperBoxInfo",
    "details": {
      "done": true,
      "all_opers": [ ... ],
      "own_opers": [
        {
          "id": "char_103_angel",
          "name": "能天使",
          "own": true,
          "elite": 2,
          "level": 90,
          "potential": 6,
          "rarity": 6
        },
        ...
      ]
    }
  }
  ```
- **字段解释**：
  - `id`：官方唯一干员 ID（由 `BattleDataConfig` 根据 `battle_data.json` 自动解析绑定）
  - `name`：官方标准干员名称
  - `own`：拥有状态 (`true`)
  - `elite`：精英阶段（通过模板匹配 `OperBoxFlagElite1/2.png` 得到 0, 1, 2）
  - `potential`：潜能等级（通过模板匹配 `OperBoxPotential2~6.png` 得到 1~6）
  - `level`：角色等级（由 `RegionOCRer` 在 `[5, 230, 37, 23]` 局部提取并转为纯数字）

---

## 2. 真实集成与 Fallback 分级架构

我们建立三级数据源容灾机制（`MaaAcquisitionAdapter`）：

```
[Level 1] MaaCore Native API
     ↓ (若本地未安装 MaaCore C-API/动态库)
[Level 2] FallbackOperBoxRecognizer (符合 MAA 1280x720 坐标体系的本地视觉引擎)
     ↓ (若局部图像模糊/置信度不足)
[Level 3] 标记 needs_review: true (写入人工审核队列，坚决杜绝自动猜 90)
```

### 2.1 拒绝伪逻辑（Anti-Cheat & Anti-Mock）
- **废弃规则**：彻底清除 `精二=90, 精一=60, 精零=1`。
- **置信度契约**：
  ```json
  {
    "level": {
      "value": 83,
      "confidence": 0.95,
      "method": "ocr"
    },
    "elite": {
      "value": 2,
      "confidence": 0.92,
      "method": "template"
    }
  }
  ```
- 若 `confidence < 0.6` 或 OCR 未提取出有效纯数字，`needs_review` 设为 `true`，`level` 保持为识别出的原始低信度值或回退标记，绝不允许伪造满级。

---

## 3. 本地集成实测结论

1. **模板与数据完备性**：
   - 官方全部 16 项 `OperBox` 模板已固化至 `maa_templates/`；
   - 官方 `battle_data.json`（全量 1375 干员）已解析生成 `operator_registry.json`。
2. **状态机与 ADB 驱动**：
   - 已实现对 MuMu 12 的 ADB 自动截屏与导航输入。
   - 增加对游戏大厅、弹窗与“干员一览”界面的状态判断，避免盲目前进导致的数据污染。
