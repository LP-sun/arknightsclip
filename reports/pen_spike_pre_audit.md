# 明日方舟报菜名 · Pen.dev 平面渲染后端预审计报告 (Pre-Audit)

> **审计日期**：2026-09-14  
> **分支**：`feat/pen-renderer-spike`  
> **目标**：在完全保护现有 PSD / DaVinci Resolve 生产管线的前提下，对将平面渲染后端评估迁移到 pen.dev 的可行性进行全面逆向技术审计。

---

## 1. 现有 PSD 视觉与图层系统审计

通过对当前生产模板（`psd模板/只需要模板/能天使.psd` 及 59 个精细化历史 PSD）的图层树及 `reports/template_analysis.md` 深度审计，原生产 PSD 呈现典型的 **“按视觉属性全局横向切分”** 的 8 人固定布局：

```text
Root (1920 × 1080)
├── 0: 背景 (战术网格暗底, 全画幅 RGB)
├── 1: 42w5plpg... (全画幅干员大立绘与氛围背景, SmartObject / Pixel)
├── 2: 卡面 (8 位玩家倾斜卡框、卡面立绘切片及 `- - - NO INFO - - -` 磨砂暗底)
├── 3: 潜能 (8 位玩家潜能 1~6 专属金色发光星标组)
├── 4: 精英等级 (8 位玩家精 0 / 精一 / 精二专属阶级盾徽)
├── 5: 角色等级 (8 位玩家等级数字与 LV 标牌)
├── 6: 博士 背景 (左右战术卡框底衬面板)
├── 7: 头像 (8 位博士圆形头像与剪切蒙版)
└── 8: 博士等级 (博士名称、UID 及等级徽环)
```

### 关键痛点与迁移动因：
1. **PSD 结构对参数化不友好**：同一个玩家的属性散落在 7 个不同的顶级图层组中（例如玩家 1 的头像在组 7，等级在组 8，卡面在组 2，潜能在组 3）。这种结构在 Photoshop 中依靠绝对图层位置堆叠，无法天然以“对象/玩家组件”为单元进行参数化更新。
2. **文件体积极度臃肿**：单个 PSD 超过 100MB（推王 112MB、能天使 107MB、风笛 111MB），59 个干员占用了超 2GB 空间，且直接被 GitHub 100MB 限制拦截。
3. **渲染依赖厚重 GUI/COM**：Photoshop 或 psd-tools 解析复合图层耗时高（单张合成 2~5 秒）。

---

## 2. 元素迁移分类：原生 Node vs. Raster Asset

| 元素分类 | 元素名称 | 推荐载体 | 迁移策略与技术原因 |
| :--- | :--- | :--- | :--- |
| **画布结构** | 1920×1080 根画板 | pen.dev 原生 `frame` | `clip: true`，统筹全局布局与栅格。 |
| **文本元素** | 博士名、博士等级、干员等级 | pen.dev 原生 `text` | 动态绑定 `content`，利用 Google Fonts 或系统无衬线字体渲染。 |
| **容器/布局** | 玩家卡槽、头像容器、立绘裁切框 | pen.dev 原生 `frame` | 运用 flexbox/padding 与 `clip: true` 进行空间约束，防止立绘溢出变形。 |
| **几何形状** | 矩形背景条、半透明渐变条、遮罩 | pen.dev 原生 `rectangle` | 支持原生 `opacity`, 线性/径向渐变 (`gradient`) 与圆角 (`cornerRadius`)。 |
| **高复杂度 UI** | 精英图标 (精0/精1/精2) | **Raster Asset (PNG)** | 沿用 `maa_templates` 与 PSD 提取的高清透明 PNG，确保 100% 官方视觉一致。 |
| **高复杂度 UI** | 潜能图标 (潜1~潜6) | **Raster Asset (PNG)** | 矢量化重绘成本极高且难还原发光质感，保留透明 PNG。 |
| **战术装饰** | NO INFO 磨砂纹理卡底 | **Raster Asset (PNG)** | PSD 原版包含特定噪点和渐变网格，导出静态透明资产复用。 |
| **大画幅图像** | 干员全身大立绘 | pen.dev `rectangle` (Image Fill) | 设为 `mode: "fit"` 或 `"fill"`，配合 frame 边界居中展示。 |
| **动态角色卡** | 玩家当前干员头像/半身 | pen.dev `rectangle` (Image Fill) | `mode: "fill"`，固定宽高比例裁切。 |
| **全局底图** | 罗德岛战术背景底图 | **Raster Asset (PNG)** | 直接提取 PSD 背景层为高清 1080P PNG 作为底图。 |

---

## 3. Photoshop 特有效果在 pen.dev 的复刻风险评估

| Photoshop 特效 | 原版实现 | pen.dev 支持现状 | 替代/规避方案 |
| :--- | :--- | :--- | :--- |
| **图层混合模式** | `Color Dodge` (颜色减淡), `Overlay` (叠加) | 原生支持常见 `blendMode`（包含 colorDodge, overlay, multiply 等） | 支持度良好，可通过 fill 的 `blendMode` 复刻，若有色差则烘焙进底图。 |
| **图层样式：高级投影/发光** | 多重外发光、内发光 | pen.dev 原生仅支持单一或数组 `shadow` (inner/outer) | 复杂发光效果（如潜能徽章流光）直接烘焙在透明 PNG 资产中。 |
| **斜切/自由变换** | 菱形倾斜卡面（Skew/Transform） | pen.dev 原生不支持 CSS skew / 仿射剪切变换 | **方案**：采用战术倒角卡框（Chamfer / Rounded Box）或倾斜切角 PNG 遮罩，不强行依赖 skew。 |
| **调整图层 (Curves/Levels)** | 调色曲线与色阶图层 | pen.dev 不支持调整图层（Adjustment Layers） | 在导入立绘资产前统一预调色或在 DaVinci 节点处理。 |

---

## 4. 组件化 (Component & Instance) 架构设计

原版 8 人 PSD 采用无继承的平铺图层，而 pen.dev 原生具备 **Reusable Component (`reusable: true`)** 与 **`ref` (Instance)** 机制。

### 核心组件：`PlayerCardComponent`
五位玩家的卡面具有 100% 相同的视觉层级与数据结构，因此将单一玩家卡定义为一个可复用 Component，五个玩家位置均作为其实例（`ref`）：

```text
ReportScene (1920 × 1080 Frame)
├── Background (Image / Gradient Fill)
├── OPERATOR_FULL_ART (Center Frame / Image Fill)
│
├── PLAYER_CARD_COMPONENT (reusable: true, 模板主件)
│   ├── DOCTOR_CONTAINER
│   │   ├── DOCTOR_AVATAR (Circle frame, Image Fill)
│   │   ├── DOCTOR_NAME (Text)
│   │   └── DOCTOR_LEVEL (Text)
│   └── OPERATOR_STATE_CONTAINER
│       ├── OPERATOR_CARD (Frame, Image Fill)
│       ├── OPERATOR_LEVEL (Text)
│       ├── ELITE_0 / ELITE_1 / ELITE_2 (Image nodes, mutual exclusive)
│       ├── POTENTIAL_1 .. POTENTIAL_6 (Image nodes, mutual exclusive)
│       └── NO_INFO (Masked Frame, for unowned state)
│
├── P1 [Instance of PLAYER_CARD_COMPONENT] (x: 40, y: 150)
├── P2 [Instance of PLAYER_CARD_COMPONENT] (x: 40, y: 450)
├── P3 [Instance of PLAYER_CARD_COMPONENT] (x: 40, y: 750)
├── P4 [Instance of PLAYER_CARD_COMPONENT] (x: 1400, y: 300)
└── P5 [Instance of PLAYER_CARD_COMPONENT] (x: 1400, y: 600)
```

---

## 5. 五人布局 (5-Player Balance) 空间规划

与旧版的 8 人（左4 / 右4）不同，本次 Spike 目标为 **五人布局**：
* **左侧 3 人（P1, P2, P3）**：垂直均匀排布在 $x \in [40, 520]$ 区间，$Y$ 坐标分布合理，卡片高度约 240px，间隙 60px。
* **中央立绘区域**：占据 $x \in [520, 1400]$ 的 880px 超大视觉重心，干员全身立绘享有充分展示空间，不被侧边遮挡。
* **右侧 2 人（P4, P5）**：放置于 $x \in [1400, 1880]$ 区间。
  * **视觉平衡关键**：为消除“左3右2”可能造成的右侧空旷感，右侧两人卡片保持与左侧完全相同的物理尺寸，但**整体垂直居中**（如 $Y_4 = 280, Y_5 = 580$），加大呼吸间距，兼顾战术信息密度与画面的稳重对称。

---

## 6. 参数化契约设计与状态机 (State Matrix)

通过统一的 `manifest.json` 驱动，每个 Slot 遵从确定的布尔/显隐状态机：

| 状态分支 | 字段判定 | 对应节点表现 |
| :--- | :--- | :--- |
| **已持有 (Owned)** | `own == true` | `OPERATOR_CARD` 显示；`OPERATOR_LEVEL` 显示并注入文本；对应的 `ELITE_x` 唯一显示；对应的 `POTENTIAL_x` 唯一显示；`NO_INFO` 强制隐藏。 |
| **未持有 (Missing)** | `own == false` | `OPERATOR_CARD` 隐藏；`OPERATOR_LEVEL` 隐藏；所有 `ELITE_*` 与 `POTENTIAL_*` 全部隐藏；`NO_INFO` 强制显示；**博士头像、名称、等级依然完整保留显示**。 |

---

## 7. 预审计结论

1. **结构升级必要性极高**：PSD 的 209 层绝对图层对于程序维护与版本控制是巨大负担；pen.dev 的单一 Component + 5 Instance 架构在概念模型上完胜 PSD。
2. **纯 Vector 盲目重绘不可取**：徽章与光效应当坚决保留为静态透明 PNG（Raster Asset），设计系统以 Frame 组装。
3. **技术路线确认**：立即进入 Step 2（pen.dev 实际能力与无头运行链路验证）。
