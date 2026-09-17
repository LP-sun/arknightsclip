# Project subagent strategy — permission-hardened baseline

## Scope and source of truth

These project-level agents support the current `arknightsclip` repository. The official production source of truth across components is strictly defined as:

* `src/arknightsclip/`: Production data collection, OperBox analysis, normalization, and timeline export pipeline.
* `psd2pen/`: Production static Box and Pencil visual source of truth (`.pen` modifications strictly restricted to Pencil MCP).
* `renderers/rhine/`: Production Rhine-style dynamic renderer (TypeScript, Vite, HTML5 Canvas, Playwright, Three.js assets).
* `experiments/rhine_pillow_mockup/`: Historical and rapid visual mockup exploration only; not a production renderer.

Scene data is built into `data/manifests/` from the normalized dataset in `data/normalized/five_players.json`, which draws from the reproducible public dataset in `data/raw/`.

Custom agent files use Codex's project-level `.codex/agents/*.toml` schema. They are intentionally narrow: root retains architecture, shared-file ownership, visual direction, Git integration, Pen/MCP state, permission elevation, and final acceptance.

This hardened package uses the stable `sandbox_mode` presets in `.codex/agents/*.toml` as the primary security mechanism. Granular permission profiles described here represent repository policy guidance rather than an active schema enforcement file; experimental permission profiles have not been committed as executable configs to prevent unverified configuration drift. Do not assume a project-level `.codex/config.toml` exists.

## Roles

| Agent | Default model | Main purpose | Sandbox / approval | Intended writes |
| --- | --- | --- | --- | --- |
| `repo-researcher` | GPT-5.6 Luna | Code, contracts, assets, dependency investigation | read-only / never | none |
| `implementation-worker` | GPT-5.6 Luna | Bounded, pre-designed implementation | workspace-write / never | exact delegated paths only (behavioral constraint) |
| `visual-reviewer` | GPT-5.6 Sol | Screenshot/reference visual review | read-only / never | none |
| `motion-specialist` | GPT-5.6 Sol | Animation/camera/deterministic timing diagnosis | read-only / never | none |
| `test-verifier` | GPT-5.6 Luna | Tests, determinism, asset, smoke verification | read-only / never | none; tests must use no-write modes |
| `docs-reporter` | GPT-5.6 Luna | Evidence-based documentation/reports | workspace-write / never | exact delegated docs paths only (behavioral constraint) |
| `git-reviewer` | GPT-5.6 Luna | Branch/diff safety review | read-only / never | none |
| `git-committer` | GPT-5.6 Luna | Explicit-path staging/local commit | read-only / on-request | `.git` only through exact approved Git commands |

No role uses `danger-full-access`.

Use `repo-researcher`, `test-verifier`, and `git-reviewer` for independent read-only work. Invoke `implementation-worker` only after the root agent has fixed the design and named the writable paths. Use `visual-reviewer` only with concrete screenshots or reference images; use `motion-specialist` only with a precise problem, relevant files, target frames, and current captures or data. Use `docs-reporter` after implementation and verification have established facts.

Do not use these agents as general-purpose developers or delegate architecture, a shared renderer scene, visual direction, Git integration, or final acceptance. Astra is not a default subagent model; consider it only under the project's normal model-escalation policy. This permission hardening does not change any model or reasoning-effort assignment from the supplied package.

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

`repo-researcher`, `visual-reviewer`, `motion-specialist`, `test-verifier`, and `git-reviewer` use `approval_policy = "never"`. A blocked operation is evidence that the task exceeds the role. They must report the block rather than request elevation.

`test-verifier` must distinguish `FAIL` from `INCONCLUSIVE_SANDBOX`. It should disable Python/pytest cache writes where compatible (`PYTHONDONTWRITEBYTECODE=1`, `pytest -p no:cacheprovider`) and must not convert a read-only verifier into a writer just to make a test run.

## Workspace-write roles

`implementation-worker` and `docs-reporter` use `workspace-write` but `approval_policy = "never"`.

Their exact-path restrictions are **behavioral**. Root must:

- explicitly enumerate writable paths in the delegation;
- avoid parallel ownership of the same file;
- review `git status`/diff after the worker returns;
- never delegate secrets, credentials, or paths outside the workspace;
- treat `UNEXPECTED_WRITE` as a stop condition, not as an invitation for the child to clean up.

## Git safety and git-committer

Every agent starts by inspecting `git status --short --branch`, treats dirty state as someone else's work, and never cleans it. Except for the narrowly approved `git-committer` commands, agents may not stage, commit, stash, push, merge, rebase, reset, clean, restore, checkout, force-push, or delete branches.

`git-committer` is intentionally `read-only + on-request`, not `workspace-write`. Normal Codex workspace sandboxes protect `.git`, so staging/committing requires explicit permission. The committer may request command-scoped approval only for:

1. `git add -- <exact delegated paths>`
2. `git commit -m <exact root-provided message>`

It must never request blanket Full Access. Before staging/committing it checks for unexpected staged content and for Git hooks, clean/process filters, or signing requirements that could execute additional code. If those are present, root handles the commit.

Git commit is a serialized phase. Do not run `git-committer` concurrently with any writer or any process that can mutate the index/working tree.

## MCP / Pencil boundary

`psd2pen/` is the formal visual source. Without explicit Pencil MCP access, agents must leave every `.pen` file unchanged and return `PENCIL_MCP_NOT_CONNECTED` when a Pen inspection or edit is necessary. They may not bypass Pencil with raw JSON edits, scripts, React/Pillow rendering, or mouse-coordinate automation. All `.pen` document modifications must be performed exclusively through Pencil MCP.

Shell sandboxing does not constrain MCP/app actions. Therefore:

- A read-only agent may use only MCP methods whose tool contract is explicitly read/inspect/screenshot-only.
- If a Pencil/MCP method can mutate, export-overwrite, create, delete, or its side effects are ambiguous, a read-only agent must not call it.
- Pen mutation belongs to a separately authorized root-controlled task; no `.pen` mutation is implied by `workspace-write`.

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
5. Exercise `git-committer` only in a disposable repository because its purpose is to modify `.git` after explicit approval.

TOML syntax and intended static safety invariants can be validated using Python's `tomllib` module across `.codex/agents/*.toml`. Static validation confirms schema correctness, but cannot prove the runtime honored the requested sandbox or MCP boundaries.
