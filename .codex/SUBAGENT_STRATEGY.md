# Project subagent strategy — permission-hardened baseline
# Project subagent strategy — permission-hardened baseline

## Scope and source of truth

These project-level agents support the current `arknightsclip` repository. The component source-of-truth boundaries are:

* `src/arknightsclip/`: Production data collection, OperBox analysis, normalization, and timeline export pipeline.
* `psd2pen/`: Production static Box and Pencil visual source of truth (Pencil MCP recommended for `.pen` layout and editing; programmatic scripting permitted). Note that for Rhine video production, `psd2pen` is optional: creators may choose either `psd2pen` layered components or raw screenshot-cropped rectangular cards (`data/raw/*/operbox/cards_raw/`).
* `renderers/rhine/`: Active Rhine-style dynamic renderer **work in progress (WIP)**. It is the only maintained Rhine renderer path, but it is **not yet production-ready or delivery-ready**. Known renderer limitations and TODOs are documented in `docs/rhine_renderer.md` and must not be described as completed.
* `experiments/rhine_pillow_mockup/`: Historical and rapid visual mockup exploration only; not a production renderer.

Scene data is built into `data/manifests/` from the normalized dataset in `data/normalized/five_players.json`, which draws from the reproducible public dataset in `data/raw/`.

Custom agent files use Codex's project-level `.codex/agents/*.toml` schema. They are intentionally narrow: root retains architecture, shared-file ownership, visual direction, Git integration, Pen/MCP state, permission elevation, and final acceptance.

This hardened package uses the stable `sandbox_mode` presets in `.codex/agents/*.toml` as the primary security mechanism. Granular permission profiles described here represent repository policy guidance rather than an active schema enforcement file; experimental permission profiles have not been committed as executable configs to prevent unverified configuration drift. Do not assume a project-level `.codex/config.toml` exists.

## Roles

| Agent | Default model | Main purpose | Sandbox / approval | Intended writes |
| --- | --- | --- | --- | --- |
| `repo-researcher` | GPT-5.6 Luna | Code, contracts, assets, dependency investigation | read-only / on-request | none |
| `implementation-worker` | GPT-5.6 Luna | Bounded, pre-designed implementation | workspace-write / on-request | exact delegated paths only (behavioral constraint) |
| `visual-reviewer` | GPT-5.6 Sol | Screenshot/reference visual review | read-only / on-request | none; may propose visual/style patches |
| `motion-specialist` | GPT-5.6 Sol | Animation/camera/deterministic timing diagnosis | read-only / on-request | none; may propose motion parameter patches |
| `test-verifier` | GPT-5.6 Luna | Tests, determinism, asset, smoke verification | read-only / on-request | none; can request temp/cache writes if needed |
| `docs-reporter` | GPT-5.6 Luna | Evidence-based documentation/reports | workspace-write / on-request | exact delegated docs paths only (behavioral constraint) |
| `git-reviewer` | GPT-5.6 Luna | Branch/diff safety review | read-only / on-request | none |
| `git-committer` | GPT-5.6 Luna | Staging & committing delegated changes | read-only / on-request | staging and commits via on-request approval |

The root agent uses `danger-full-access` so it can perform Git metadata writes; child roles retain their narrower settings.

Use `repo-researcher`, `test-verifier`, and `git-reviewer` for independent read-only work. Invoke `implementation-worker` after scoping design and naming writable paths. Use `visual-reviewer` with concrete screenshots or reference images; use `motion-specialist` with targeted timing/camera problems. Use `docs-reporter` after implementation and verification have established facts.

Astra is recommended for advanced visual and complex architectural design tasks. **Astra 视觉创造与升级权限**：在现有视觉效果不理想时，Astra 模型被全面授权主导创建新的 `.pen` 角色卡片、全景场景模板与 UI 框架组件，或对现有设计资产进行演进微调。建议优先通过 Pencil MCP 进行可视化操作，亦允许配合程序化脚本辅助生成复杂几何或排版图元。

## Permission model

Treat four layers separately:

1. **Sandbox / filesystem permissions** — the hard local execution boundary when honored by the active runtime.
2. **Approval policy** — whether the agent may ask to cross that boundary.
3. **MCP / app tool permissions** — independent capabilities; shell `read-only` does not make a mutable MCP tool read-only.
4. **Developer instructions** — behavioral constraints, not an OS-level allowlist.

Never describe an exact delegated path list as a hard filesystem boundary when the role uses `workspace-write`.

## Parent-session rule

Child runtime permissions can be affected by the parent/session mode. In particular, current `codex exec` builds have reported cases where a custom agent's `sandbox_mode = "read-only"` is replaced by the parent's `workspace-write` mode. Therefore:

- Do **not** spawn a safety-critical read-only reviewer from a parent running Full Access / `--yolo`.
- When using non-interactive `codex exec`, do not rely on the child TOML alone as a security boundary. Run the parent itself read-only for read-only work, or verify the effective child sandbox from runtime/session metadata before trusting isolation.
- Runtime permission state is authoritative over prose in these files.

## Read-only roles

`repo-researcher`, `visual-reviewer`, `motion-specialist`, `test-verifier`, and `git-reviewer` use `approval_policy = "on-request"`. If a task requires an elevation (e.g., executing a targeted diagnostic, creating a temporary test artifact, or proposing a visual patch), the role requests explicit approval rather than silently failing.

`test-verifier` should distinguish `FAIL` from environment/permission barriers. It may request temporary cache or artifact writing permissions when necessary to execute test suites reliably.

## Workspace-write roles

`implementation-worker` and `docs-reporter` use `workspace-write` with `approval_policy = "on-request"`.

Their delegated write scopes are managed through explicit root instructions and review:
- Root explicitly enumerates writable paths in the delegation;
- Avoid parallel ownership of the same file across subagents;
- Review `git status`/diff after the worker returns;
- Stop and confirm before touching sensitive configuration or files outside the workspace.

## Git safety and confirmation rules

Git safety is governed by explicit user confirmation rather than rigid unconditional bans:
- **高影响操作确认规范**：所有具有潜在破坏性、不可逆或高影响力的 Git 操作（包括：`git push --force`、`git reset --hard`、`git clean -fdx`、分支删除、历史重写 `rebase -i` 或覆盖远端分支）**在操作前必须向用户单独确认**并获得明确授权后方可执行；
- 常规的只读状态检查（`git status`、`git diff`、`git log`）自由执行；
- Git 集成由主代理负责，并遵循主代理会话的显式确认策略；
- 严禁未经用户显式确认擅自清理或丢弃用户本地未提交的工作区现场。

## MCP / Pencil 视觉规范（推荐准则）

关于 `.pen` 矢量与图层设计文件的操作规范已全面转为**建议与灵活协作模式**：

1. **推荐优先使用 Pencil MCP**：强烈建议在进行 `.pen` 文档的可视化审查、图层调试、卡片布局与原生渲染导出时，优先通过 Pencil MCP 执行，以保障图层结构语义与可视化调试一致性；
2. **放宽脚本与代码生成限制（建议而非死禁）**：不再绝对禁止代码化或脚本辅助生成 `.pen`。对于需要密集坐标计算、批量切图对齐、数学波形生成（Procedural Generation）或快速修正 JSON 键值的场景，允许使用脚本与代码辅助处理；
3. **视觉创作自由度**：推荐由具备高阶审美与设计能力的 Astra 模型主导角色卡片、全景场景模板与 UI 框架的新建与美学演进；其他模型在必要时亦可执行维护性或局部微调任务。

## Granular permissions and policy boundary

A static project-relative exact-file allowlist is not enforced by Codex configuration in this repository. `implementation-worker` and `docs-reporter` therefore enforce narrow delegated write scope through `developer_instructions` plus root pre/post review.

Permission profiles and file scoping described in this document serve as documented policy guidance. Because current Codex releases do not provide a verified project-local permission profile schema in this workspace, no experimental configuration profiles have been committed as active or example configs to avoid unverified configuration drift.

## Validation and invocation

Codex discovers role files directly from `.codex/agents/*.toml`. Do not assume a project-level `.codex/config.toml` exists. Use explicit role names in delegation prompts, state the task boundary and expected report, and for writers name the exact owned paths.

Keep the root session on `on-request` approvals and avoid Full Access when spawning read-only children. The package caps concurrent subagent threads at 4. Git commit remains serialized regardless of that cap.

Recommended smoke tests:

1. Ask `repo-researcher`: "Find the current renderer-related entry point and list its main files. Do not modify anything."
2. Ask `git-reviewer`: "Inspect current Git status and report unrelated changes. Do not modify Git state."
3. Ask `test-verifier` to run one genuinely no-write check and verify `git status` is unchanged.
4. Exercise `implementation-worker` only against a disposable explicitly delegated path, then review the root diff.
5. Perform Git integration from the root agent, with the root session's explicit approval policy and runtime permissions.

TOML syntax and intended static safety invariants can be validated using Python's `tomllib` module across `.codex/agents/*.toml`. Static validation confirms schema correctness, but cannot prove the runtime honored the requested sandbox or MCP boundaries.
