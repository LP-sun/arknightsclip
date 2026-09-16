# Project subagent strategy

## Scope and source of truth

These project-level agents support the current `arknightsclip` repository. The current checkout does not contain `renderers/rhine/`, `renderers/rhine/README.md`, or `docs/rhine_renderer.md`; no agent may claim a Rhine Renderer Phase 1 implementation exists here. For the actual checkout, current production entry points are `src/arknightsclip/`, scene data is built into `data/manifests/`, and renderer work is isolated under `experiments/`.

Custom agent files use Codex's project-level `.codex/agents/*.toml` schema. They are intentionally narrow: root retains architecture, shared-file ownership, visual direction, Git integration, Pen MCP state, and final acceptance.

## Roles

| Agent | Default model | Main purpose | Writes code? |
| --- | --- | --- | --- |
| `repo-researcher` | GPT-5.6 Luna | Code, contracts, assets, and dependency investigation | No |
| `implementation-worker` | GPT-5.6 Luna | Bounded, pre-designed implementation | Yes, explicitly delegated paths only |
| `visual-reviewer` | GPT-5.6 Sol | Screenshot and reference-based visual review | No |
| `motion-specialist` | GPT-5.6 Sol | Animation, camera, and deterministic timing diagnosis | No |
| `test-verifier` | GPT-5.6 Luna | Tests, determinism, asset, and smoke verification | No |
| `docs-reporter` | GPT-5.6 Luna | Evidence-based documentation and reports | Docs only, explicitly delegated paths |
| `git-reviewer` | GPT-5.6 Luna | Branch and diff safety review | No |

Use `repo-researcher`, `test-verifier`, and `git-reviewer` for independent read-only work. Invoke `implementation-worker` only after the root agent has fixed the design and named the writable paths. Use `visual-reviewer` only with concrete screenshots or reference images; use `motion-specialist` only with a precise problem, relevant files, target frames, and current captures or data. Use `docs-reporter` after implementation and verification have established facts.

Do not use these agents as general-purpose developers or delegate architecture, a shared renderer scene, visual direction, Git integration, or final acceptance. Astra is not a default subagent model; consider it only after two unsuccessful Sol-guided attempts at a core visual interpretation.

## Safety and escalation

Every agent starts by inspecting `git status --short --branch`, treats dirty state as someone else's work, and never cleans it. No agent may stash, commit, push, merge, rebase, reset, clean, restore, checkout, use force Git operations, or delete branches. The `git-reviewer` is strictly read-only.

`psd2pen/` is the formal visual source. Without explicit Pencil MCP access, all agents must leave every `.pen` file unchanged and return `PENCIL_MCP_NOT_CONNECTED` when a Pen inspection or edit is necessary. They may not bypass Pencil with raw JSON edits, scripts, React/Pillow rendering, or mouse-coordinate automation. The limited, documented accepted-template batch exception in `psd2pen/AGENTS.md` remains subject to its validation rules and is never implied by this strategy.

The Codex agent schema in this version supports per-agent sandbox modes but no project-relative allowlist for writable paths. The two workspace-write agents therefore enforce their narrow write scope in `developer_instructions`; root must name the exact files before delegating.

## Validation and invocation

Codex discovers these files from `.codex/agents/`. Use explicit role names in delegation prompts, state the task boundary and expected report, and set the parent turn's permissions before spawning because child agents inherit runtime permissions. The CLI in this environment exposes `codex agents` for session browsing, not a command to invoke or validate one named custom agent directly. Validate discovery with a strict-config run, then smoke-test through a normal subagent delegation:

1. Ask `repo-researcher`: "Find the current renderer-related entry point and list its main files. Do not modify anything."
2. Ask `git-reviewer`: "Inspect current Git status and report unrelated changes. Do not modify Git state."

Both smoke tests must leave Git state unchanged. Do not use `implementation-worker` as a smoke test against production code.
