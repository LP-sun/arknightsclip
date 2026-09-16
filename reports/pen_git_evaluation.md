# 明日方舟报菜名 · Pen.dev 原生格式 Git 友好度评估报告

> **评估对象**：`templates/report_5p_master.pen`  
> **对比参照**：`psd模板/只需要模板/能天使.psd` (107 MB 二进制)  
> **分支**：`feat/pen-renderer-spike`

---

## 1. Git 关键维度量化对比

| 评估维度 | Photoshop PSD (现状) | pen.dev `.pen` 原生格式 | 提升与对比结论 |
| :--- | :--- | :--- | :--- |
| **文件存储格式** | 私有二进制复合格式 (Binary, Big-Endian) | 标准格式化 JSON (UTF-8) | **质的飞跃**：文本格式对所有版本控制系统友好。 |
| **单文件体积** | **107 ~ 112 MB** / 模板 | **10.5 KB** / 模板 | **体积缩减达 99.99%** (降低 10,000 倍)。 |
| **GitHub 存储限制** | 超出单文件 100MB 阈值，必须使用 Git LFS | 远低于限制，无需 LFS，直接纳入常规 Git 跟踪 | 避免免费 LFS 1GB 流量限制与带宽资费问题。 |
| **Diff 可读性 (Readability)** | 完全不可读 (`Binary files differ`) | 精准行级 Diff (显示节点名、字段名、新旧值) | Code Review 与审计极其直观。 |
| **合并与冲突解决 (Mergeability)** | 无法做任何三方代码合并，冲突即报废覆盖 | 支持标准 Git Merge 与 Conflict Markers | 支持团队协作微调不同 Component。 |
| **键序稳定性 (Key Ordering)** | 不适用 | 标准 JSON 属性树，只要序列化固定格式，diff 极其干净 | 无冗余重排与脏数据污染。 |

---

## 2. 真实修改场景 Diff 实测展示

在对 `report_5p_master.pen` 中的玩家名字内容与字体颜色进行微调时，Git 捕获的实际 Diff 如下：

```diff
--- a/experiments/pen_renderer/templates/report_5p_master.pen
+++ b/experiments/pen_renderer/templates/report_5p_master.pen
@@ -68,11 +68,11 @@
               "id": "DOCTOR_NAME",
               "name": "DOCTOR_NAME",
               "type": "text",
-              "content": "Dr.Doctor",
+              "content": "Dr.NewName",
               "fontFamily": "Microsoft YaHei",
               "fontSize": 14,
               "fontWeight": "bold",
-              "fill": "#E2E8F0",
+              "fill": "#FF0055",
               "textAlign": "center"
             }
           ]
```

### 评估结论：
`.pen` 格式在 Git 友好度与工程协作层面具有**压倒性优势**。它是现代化“Design-as-Code”理念的典范，彻底终结了美术素材无法进行版本审查的行业痛点。
