# 数据集定义与治理规范 (Dataset Governance)

本项目的数据目录 `data/` 包含《明日方舟》干员仓库的公开样本、标准化数据源以及场景清单。

---

## 目录结构

```text
data/
├── raw/                      # 公开、可复现的原始采集数据集
│   ├── P1/
│   │   ├── operators.json    # 干员识别输出与置信度元数据
│   │   └── operbox/
│   │       ├── pages/        # 仓库页原始截图 (PNG)
│   │       ├── cards_raw/    # 干员卡片切图 (PNG)
│   │       └── card_metadata/# 逐卡片识别定位与置信度 JSON
│   ├── P2/ ... P5/           # 玩家 2 至 5 的实际样本数据
├── normalized/               # 多玩家标准化与合并数据
│   ├── five_players.json     # 五人规范化唯一事实源 (Source of Truth)
│   └── five_players_inspection.xlsx # 用于人工核查与审阅的表格
└── manifests/                # 场景清单 (Scene Manifests)
    └── char_*.json           # 逐干员五玩家槽位清单
```

---

## 1. `data/raw/` 公开数据集定位

`data/raw/P1` 至 `data/raw/P5` 是本项目的**公开、可复现基准数据集**。

### 允许公开的内容
* **仓库页原始截图** (`operbox/pages/*.png`)：游戏内公开可见的干员仓库列表截图；
* **干员卡片切图** (`operbox/cards_raw/*.png`)：用于界面拼装和视觉合成的卡片裁剪图；
* **卡片识别元数据** (`operbox/card_metadata/*.json`)：OCR 边界框、数值与置信度；
* **玩家识别名** (`profile.display_name`)：参与本项目的玩家公开展示昵称（已明确获得授权长期公开）；
* **干员拥有与练度数据** (`operators.json`)：用于测试与渲染的干员等级、潜能、精英化等级。

### 数据集用途
1. **OCR 回归测试**：验证 OCR 引擎对不同屏幕缩放、字形和背景的识别稳定性；
2. **OperBox 管线验证**：验证多页去重、跨页卡片重叠抑制与边缘卡片剔除；
3. **确定性复现**：在脱机环境下完整复现从采集数据到五人对比画面的全过程；
4. **渲染器输入**：作为 `SceneManifest`、`psd2pen` 静态图层和 Rhine 动态渲染器的输入源。

---

## 2. 严禁提交的机密与敏感数据

尽管 `data/raw/` 属于公开数据集，但**严禁**在仓库内提交以下任何隐私或敏感凭证：

* 游戏账号登录凭据（用户名、密码、Token、Session Cookie、JWT）；
* 任何第三方服务 API Key 或私有 Token；
* ADB 私有认证密钥与授权材料 (`adbkey`, `adbkey.pub`)；
* 游戏 UID（如未来有隐私要求或协议限制，严格予以脱敏）；
* MCP 服务或 Codex 的私有认证材料；
* 本地环境配置文件 (`.env` 或包含私有路径的 `config/project.yaml`)。

---

## 3. 大文件存储策略 (Git LFS)

为了控制 Git 仓库体积，并支持大规模图像样本的可复现性，后续新增或修改的原始二进制数据统一纳入 Git LFS 管理（规则配置于 `.gitattributes`）：

* `data/raw/*/operbox/pages/*.png`：仓库页原始截图
* `data/raw/*/operbox/cards_raw/*.png`：干员卡片切图
* `data/normalized/*.xlsx`：人工审阅 Excel 检查表

现有历史 Git commit 中的已有对象保持现状（不执行历史重写以保证稳定追踪），后续的新增与变更严格通过 LFS 追踪。
