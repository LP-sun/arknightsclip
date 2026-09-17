# 仓库分支治理与合并规范 (Repository Governance)

本文档明确 `LP-sun/arknightsclip` 仓库的分支管理、代码合入守则及资产提交流程。

---

## 1. 分支策略与 PR 规范

* **保护主干**：`main` 分支作为唯一生产主干，严禁直接在 `main` 上执行日常功能开发或实验性提交；
* **Pull Request 流程**：所有新特性 (`feat/*`)、缺陷修复 (`fix/*`)、架构整理 (`chore/*`) 及文档更新 (`docs/*`) 均须通过独立分支发起 Pull Request，经人工 review 后合入；
* **杜绝历史分支回流**：严禁将已经合并 (merged) 或废弃的历史分支重新合并回 `main`；
* **保持线性/清晰历史**：建议在 PR 合并时使用 rebase 或 squash 合并，避免产生空无意义的循环 merge commit。

---

## 2. Git 安全红线与确认规范 (Confirmation-Gated Git Rules)

对于具有破坏性、不可逆或高影响力的关键 Git 操作，**必须在执行前向用户单独提出确认请求并获得显式授权**，严禁未经确认私自执行：

* **强制推送 (Force Push)**：对 `main` 或受保护远程分支执行 `git push --force` 或 `git push --force-with-lease` 前，**操作前必须向用户单独确认**，说明覆盖远端提交的理由与潜在影响；
* **重写已推送历史**：执行 `git filter-repo`、大型交互式变基 (`git rebase -i`)、历史改写或 `git lfs migrate import` 前，**操作前必须向用户单独确认**；
* **工作区破坏性重置**：执行可能丢弃未提交内容的命令（如 `git reset --hard`、`git clean -fdx`、`git restore .`）前，**操作前必须向用户单独确认**，严禁擅自清理或覆盖用户本地未提交成果；
* **分支删除与历史变更**：删除本地/远程分支或执行导致提交脱钩的操作前，**操作前必须向用户单独确认**；
* **主干直接变基/修改**：除用户显式指示直接合入外，常规功能修改走独立分支 PR；若需直接在 `main` 上执行快进合入或复杂变基，**操作前必须向用户单独确认**。

---

## 3. CI 质量门禁 (Merge Gate)

* 仓库配置了自动化持续集成流水线 (`.github/workflows/ci.yml`)；
* **合入前提**：PR 合入前必须确保 CI 中以下核心阶段全部通过：
  1. Python 核心契约与数据模型测试套件 (`tests/run_tests.py`)
  2. 卡片与模板管线测试 (`test_cards_pipeline.py`, `test_template_batch.py`)
  3. Python 代码编译检查 (`compileall`)
  4. Rhine 时间线求值器测试与构建 (`npm test`, `npm run build`)
* CI 仅测试纯软件/脱机依赖，不挂接外部 GUI（Photoshop、Resolve）、真机 ADB 或 live MAA 采集。

---

## 4. 资产与生成物提交策略 (Artifacts Policy)

* **允许直接入库的代码与数据**：
  * `src/**`, `scripts/**`, `renderers/**`, `psd2pen/**`
  * `data/raw/**`（公开、可复现基准截图与元数据，新增 PNG 走 Git LFS）
  * `data/normalized/*.json`, `data/manifests/**`
  * `docs/**`, 长期重要技术与审计报告
* **严禁直接提交的生成物**：
  * 渲染过程帧 (`generated/**/frames/`, `reports/exported_frames/`)
  * 临时单帧截屏与中间探索切片 (`generated/**/stills/`, `reports/spike_*`)
  * 最终导出的视频二进制文件 (`*.mp4`, `*.mov`)
  * 依赖包与缓存 (`node_modules/`, `__pycache__/`, `.npm-cache/`)
* **成片交付分发**：
  * 渲染成片统一发布至 GitHub Release Assets 或专属对象存储/网盘，不在 Git 仓库内存储大体积视听媒体 blob。

---

## 5. 当前配置状态说明

> [!NOTE]
> 当前本地自动化脚本未配置 GitHub Admin 访问令牌，因此云端 GitHub Branch Protection Ruleset 处于未自动写入状态 (`BRANCH_PROTECTION_NOT_CONFIGURED`)。
> 仓库管理员可在 GitHub 仓库设置 (Settings -> Branches -> Branch protection rules) 中勾选：
> 1. *Require a pull request before merging*
> 2. *Require status checks to pass before merging* (指定 `test-python` 和 `test-rhine`)
> 3. *Do not allow bypassing the above settings*
> 4. *Block force pushes*
