# JSON 驱动的八卡／左三右二批量流程

## 从 data/raw 的五玩家库存批量生成

```powershell
.\.venv-pencil\Scripts\python.exe scripts/prepare_raw_batch.py ../data/raw --out delivery/raw_source_new
.\.venv-pencil\Scripts\python.exe scripts/cards_pipeline.py prepare delivery/raw_source_new/input.json --catalog delivery/raw_source_new/catalog.json --layout 3l2r --out delivery/raw_run_new
.\.venv-pencil\Scripts\python.exe scripts/pencil_batch.py run delivery/raw_run_new/run.json
.\.venv-pencil\Scripts\python.exe scripts/audit_raw_batch.py delivery/raw_source_new delivery/raw_run_new
```

原始 `P1..P5/operators.json` 映射到槽位 `1,2,3,5,6`；角色取五玩家集合的并集。经用户确认，缺少记录显示 NO INFO，不从其他表补值。保留 source 标记，fixture 数据不能声称为真实账号采集。角色素材从 ArknightsAssets/ArknightsAssets2 的 cn 分支按 char_id 下载默认立绘原始 PNG；记录来源 URL 和 SHA-256。raw 不含皮肤字段，因此精英化只决定徽章，全部使用默认立绘。原始数据、素材原图和既有五角色素材表不覆盖。

每次原生 `Export` 同时生成完整的 `character_cards.png` 和每位可见玩家的独立小卡。目录为 `<角色>/players/P1.png`、`P2.png`、`P3.png`、`P4.png`、`P5.png`。独立卡片由对应 Pencil 组件实例直接导出，保持透明背景；每张卡都与原生导出字节一致并在 `receipt.json` 记录 SHA-256。

本轮最终目录为 `delivery/raw_30_run_003`，输入及来源追溯为 `delivery/raw_30_source_003`；001/002 为裁切调试记录，不作为最终交付。新画板批量完成后需在 Pen.dev 保存当前文档。

## 左 3＋右 2 正式版本

`character_cards_5slot.pen` 是从已完成的八卡文档另存的独立版本。正式画板为 `CHARACTER_CARDS_1920x1080_3L_2R`（`ja7Jk`）。保留八个可编辑实例，仅显示源槽位 1、2、3、5、6；4、7、8 隐藏，原位置、尺寸、方向及素材不变。五名玩家依次为爱花、咯咯枝、东城、hmi、leo。文档内原 QA 和实验画板保留，不在指定画板的 PNG 导出范围内。

本轮交付：`delivery/five_slot_run_001/<角色>/character_cards.png`，五名角色均已完成原生截图、节点读回、透明度验证及保存重开后的再次导出。

独立命令行实跑记录：`delivery/five_slot_cli_001/run.json` 与 `verification.json`，官方 Pencil stdio 连接实测五角色成功。完整验收见 `delivery/FIVE_SLOT_ACCEPTANCE.md`。

### 一条命令批量生成

先在 Pen.dev 打开 `character_cards_5slot.pen`，并保持应用运行。JSON 格式与下文相同，仍提供八槽数据，五卡预设只控制可见性。Python 3.11+，首次安装隔离依赖：

```powershell
python -m venv .venv-pencil
.\.venv-pencil\Scripts\python.exe -m pip install -r scripts/requirements-pencil.txt
```

```powershell
.\scripts\generate_five_cards.ps1 -InputJson inputs/five_operators.json -OutputDirectory delivery/my_five_slot_run
```

脚本读取用户本机 `.codex/config.toml` 中的 `mcp_servers.pencil`，直接启动／连接官方 Pencil MCP，校验当前打开文件，通过 `execute` 创建画板、读回全部覆盖值、截图、`Export`，再检查 PNG 尺寸、透明度、八个区域的显隐状态，并将原生导出原字节复制为标准文件名。配置和凭据不复制到项目。命令行客户端需要可用的 Pencil 连接；连接或文件不匹配即停止，绝不修改原始 `.pen` 数据。

### 分步与恢复

```powershell
.\.venv-pencil\Scripts\python.exe scripts/cards_pipeline.py prepare inputs/five_operators.json --layout 3l2r --out delivery/my_five_slot_run
.\.venv-pencil\Scripts\python.exe scripts/pencil_batch.py run delivery/my_five_slot_run/run.json
.\.venv-pencil\Scripts\python.exe scripts/pencil_batch.py verify delivery/my_five_slot_run/run.json
```

同一 manifest 重试会复用同名画板并核对内容；已有画板若被手动改动则报错，不默默跳过。输入、素材表或编译脚本改变后须 prepare 新目录。每角色有 `receipt.json` 原生执行证据，总表是 `verification.json`。`run.json` 的 `prepared_not_rendered` 不表示已经生成；只有完成读回与 PNG 验证后才变为 `native_exports_verified`。

Pencil MCP 当前未提供原生保存／关闭／重开 API；批量图片生成可以一键完成，新画板的 `.pen` 持久保存仍须在 Pen.dev 操作。不要把 PNG 成功当作文档已经保存。`Pillow` 仅用于读取原生 PNG 检查 alpha，不生成或重绘卡片。

入口：`scripts/cards_pipeline.py`。示例真实数据：`inputs/five_operators.json`，来自本次统计表与已确认的D8精二修正。素材映射：`config/cards_assets.json`。

## 输入约定

```json
{
  "version": 1,
  "operators": [{
    "name": "能天使",
    "slots": [{
      "slot": 1,
      "player": "爱花",
      "owned": false,
      "elite": null,
      "level": null,
      "potential": null,
      "visible": true
    }]
  }]
}
```

上述仅展示单槽字段；实际每个角色必须提供1–8全部八槽。槽1–4左，5–8右。持有时elite为0/1/2，level为1–90整数，potential为1–6整数；未持有时三值全部null。精零0不等于空白。visible省略默认为true；五人输出仅将三个实例设为false，不删除槽位或重排布局。name当前限现有五角色，player仅用于图层名，不新增博士信息。

素材沿用已验证PSD逐槽裁切，不由elite自动推断皮肤。精英化只控制徽章。角色图可在素材目录中明确更换url、bbox、sha256；不支持的持有槽（例如当前没有配置素材的能天使槽1）会报错，应先从PSD提取并配置，不能临时选另一个人物。

## 命令（在项目目录运行）

```powershell
& 'E:\miniconda3\python.exe' scripts/cards_pipeline.py validate inputs/five_operators.json
& 'E:\miniconda3\python.exe' scripts/cards_pipeline.py prepare inputs/five_operators.json --out delivery/json_run_001
```

prepare仅生成run.json和每角色.pencil.js，不表示图片已生成。输出目录必须是新的，避免旧图冒充本轮结果。

执行代理必须连接pencil，先read_skill/get_app_state，再按run.json中的filePath，通过pencil.execute传入对应inputFile的内容。必须检查读取脚本命令的exit_code，禁止把shell错误文本传给Pencil。生成命令会校验模板节点存在、创建八实例、截图并以scale=1导出。相同输入哈希对应同名画板，重试会复用已有画板，避免重复；若人为改过该画板，应检查或另用新输入版本。Pencil调用失败按返回editId/edits修复，不得用别的渲染方式绕过。

也可用 `scripts/pencil_batch.py run <run.json>` 直接执行上述任务，自动连接 Pencil；手动 MCP 执行适用于代理已有连接的场景。两种方式都必须保持 Pen.dev 运行并打开对应模板。Pencil没有在当前接口提供保存/关闭/重开方法，最终原生文档保存与重开仍需要在应用中完成。

## 从现有统计表转换

```powershell
& 'E:\miniconda3\python.exe' scripts/cards_pipeline.py from-xlsx 统计.xlsx --overrides inputs/approved_overrides.json --output inputs/imported.json
```

适配器固定读取Sheet1 A1:G29：C:G五角色，4:11精英化、13:20等级、22:29潜能。覆盖文件D8=2仅适用于已由用户确认的这份统计表；其他表不要直接沿用。缺失某项会拒绝，不会自动填0。原工作簿不修改。直接JSON输入的validate/prepare仅依赖Python标准库；Excel适配器需要openpyxl。

## 验证边界

每次执行后读回八个实例的练度覆盖值，与输入40槽比对；检查PNG为1920×1080 RGBA及透明区域，截图检查图像正常解析。最终保存/重开后再次导出并比较。生成任务文件、自动化测试通过都不能代替这些渲染验收。

```powershell
& 'E:\miniconda3\python.exe' scripts/test_cards_pipeline.py
```

旧prepare_stats_batch.py为历史一次性流程，新的JSON工作流不调用它，也不会重写历史导出。

## 命令行与 Pencil 的职责边界

当前新增固定画板模板入口：`scripts/generate_template_cards.ps1`。
在 Pen.dev 打开 `character_cards_5slot_template.pen` 后运行该脚本；默认读取
`inputs/five_operators.json`，支持 `-InputJson`、`-Catalog`、`-Layout`、
`-OutputDirectory` 和 `-PrepareOnly`。数据编译器为 `scripts/template_batch.py`。
该入口复用 `EXPORT_CHARACTER_CARDS` 和 `SLOT_01..08`，通过名称解析语义节点，
不会按角色新增画板。左右组件各预置三种精英与六种潜能图标，批次仅切换显示。
完整说明和验收证据见 `delivery/template_v2/README.md`。

### 自动化数据流与职责边界

```text
raw / input JSON
    ↓
data normalization
    ↓
batch manifest / generated Pencil script
    ↓
Pencil MCP (唯一合法 .pen 修改入口)
    ↓
.pen document mutation
    ↓
Pencil native screenshot / export
    ↓
PNG verification / receipts
```

**核心原则：Pencil MCP 是所有 `.pen` 文件修改的唯一合法入口。**

1. **命令行自动化的合法范围**：
   * 将 raw 数据或外部输入格式化、规范化；
   * 编译批处理任务与生成 `.pencil.js` / `run.json` 执行计划；
   * 调用官方 Pencil MCP 客户端通道驱动应用；
   * 归档原生导出的 PNG、生成每位玩家的小卡副本；
   * 记录输入输出 SHA-256 收据与 manifest；
   * 使用 Pillow 仅作导出的 PNG alpha 透明度及尺寸静态校验。

2. **严禁离线修改 `.pen`**：
   * 严禁任何脚本直接读取 `.pen` JSON 后写回；
   * 严禁通过复制模板离线修改 JSON 生成新 `.pen`；
   * 严禁绕过 Pencil MCP 擅自修改节点、文本、图片、可见性或几何结构。

3. **保存与持久化**：
   * Pillow 或其他栅格库仅可检查导出的 PNG，不得生成或重绘卡片；
   * Pencil MCP 尚未提供保存、关闭或重开文档的 API，因此每次新增画板后仍须在 Pen.dev 手动保存；PNG 导出成功不能证明文档已保存。
