# 八卡 Pen 模板交付

## 文件入口

- 可编辑文档：`../character_cards_8slot.pen`，保留相邻 `assets/`、`001_能天使/` 目录，避免相对素材路径失效。
- 正式透明图：`character_cards.png`，1920×1080，由 Pencil `Export` 以 scale=1 原生导出后原样复制命名。
- 最终八卡节点：`Lwq9K` / `CHARACTER_CARDS_1920x1080_4L_4R`。
- 左组件：`HVZ4i`；右组件：`wUVzi`。
- 历史文档 `character_card_components.pen` 与历史实验截图保留。

## 使用与批量替换

每张卡都是组件实例。`CONTENT/OPERATOR_IMAGE` 是独立的路径图像填充；替换图片时保持路径在画布坐标中的边界，再按原图尺寸调整图像节点的 x/y、width/height、viewBox 与路径坐标。不要整体水平翻转组件。

OWNED：开启 OPERATOR_IMAGE，关闭 NO_INFO_PANEL 与 NO_INFO_TEXT。NO_INFO：反向切换这三个节点。LEVEL_BADGE、ELITE_BADGE、POTENTIAL_BADGE 为独立组，按数据分别控制 enabled；精英图标为 ELITE_ICON，潜能为 POTENTIAL_ICON，等级数字为 LEVEL_NUMBER。

能天使实例采用真实状态：槽01隐藏等级与潜能；槽02/03为精一潜3；槽04为精二潜3；槽05为精二潜6；槽06持有、60级、精二潜4；槽07持有、90级、精二潜2；槽08为精一并隐藏潜能。除06/07外均显示NO INFO。

源智能对象顶部为左193/407/621/835，右107/321/535/749。Pen组件原点包含6px上边框余量，因此实例y为左187/401/615/829、右101/315/529/743；左x=157，右x=1180。组件宽度表示排除博士区域后的可见卡区，不等于原始763px智能对象宽度。

## 验证图

以下是验证画板，不是正式透明交付：

- `qa/y8c7Q6.png`：左右组件。
- `qa/ADRvM.png`：四状态矩阵。
- `qa/YYEuj.png`：推王深色、小羊浅色原PSD图层替换测试。
- `qa/I0hGYu.png`：单卡留边阴影检查。
- `qa/r2JDG3.png`：八卡叠原背景对照，不含博士信息。
- `../experiments/rebuild8/iter01..iter09/`：单卡迭代；iter01/Ha5vM.png为失败探针，不计有效迭代。

## 限制

Bahnschrift在此前Pencil运行中不可用，数字采用Barlow Semi Condensed，LV/NO INFO使用Barlow。字体、局部抗锯齿、金属色阶及软阴影是视觉近似，未宣称像素完全一致。

NO INFO的背景纹理由原场景透过半透明面板产生，未烘焙进透明卡层。五PSD的共同槽位结构已审计，但推王存在局部可见轮廓变化，不能把共同智能对象bbox等同于所有样本的可见轮廓完全相同。

机器检查见 `png_verification.json`；其仅证明PNG尺寸、透明区域、八槽有内容及文件哈希，不代替视觉审查或原生重新打开验证。
