# Photoshop PSD Renderer Spike (feat/psd-template-automation)

## 1. 实验目的
验证以 Adobe Photoshop 为核心渲染后端，基于单一 5 人 PSD 母版（`templates/psd/report_5p_master_v0.psd`）与场景描述 JSON（`manifests/exusiai_test.json`），通过 Photoshop UXP 自动化脚本完成：
- 智能对象替换（大立绘、博士头像、卡面半身）；
- 文本图层内容动态更新（保持原字形与图层样式）；
- 互斥状态显隐控制（持有状态、精英 0/1/2 互斥、潜能 1~6 互斥、NO INFO 激活）；
- 1920×1080 标准画幅高保真 PNG 栅格化导出；
- 不保存直接关闭母版，保证每次渲染从洁净状态开始。

## 2. 基本原则
1. **PSD 是唯一视觉真源**：不允许使用 Pillow、React 或 Chromium 代替 Photoshop 渲染最终画面。
2. **拒绝盲目假装完成**：由于人工美术母版需要专业设计师在 Photoshop 中绘制，如果 `report_5p_master_v0.psd` 尚未放置，系统明确报告 `WAITING_FOR_USER_AUTHORED_MASTER`，并使用严格合规的结构 Fixture 验证脚本流程。
3. **拒绝屏幕点击自动化**：不使用 pyautogui、AutoHotkey 或屏幕绝对坐标，全部通过 Photoshop UXP / DOM / batchPlay 稳定寻址。

## 3. 目录结构
```text
experiments/psd_renderer/
├─ README.md
├─ manifests/
│  ├─ exusiai_test.json
│  └─ variant_test.json
├─ outputs/
│  ├─ exusiai.png
│  ├─ exusiai.render.json
│  ├─ variant.png
│  └─ variant.render.json
└─ reference/
   └─ reference_psd.png
```
