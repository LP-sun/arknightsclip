# JSON 驱动的八卡批量流程

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

此实现是MCP驱动的编译流程，不是无需Pen连接的独立渲染器。Pencil没有在当前接口提供保存/关闭/重开方法，最终原生文档保存与重开仍需要在应用中完成。

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
