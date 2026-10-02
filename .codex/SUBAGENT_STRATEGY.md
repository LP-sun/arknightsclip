# Codex subagent strategy

Last reviewed: 2026-10-03. Model assignments below were resolved from Codex CLI 0.160.0 `model/list` and checked against official OpenAI model documentation.

## Source of truth

`renderers/production/` is the canonical production video renderer and exporter. `renderers/rhine/` is deprecated historical WIP for comparison and regression diagnosis only. `psd2pen/` is the static design source; it is not the production video entry point. This repository contains `.codex/config.toml`; runtime-observed permissions remain authoritative when Codex builds differ.

## Current model inventory

Codex runtime exposed `gpt-6-astra` (flagship; low/medium/high/xhigh/max/ultra), `gpt-6.1-sol` (current workhorse; low/medium/high/xhigh/max/ultra), and `gpt-6-luna` (efficient; low/medium/high/xhigh/max), all with text/image input. Older models were available but are superseded and are not selected.

| Agent | Model | Reasoning | Sandbox | Role |
|---|---|---:|---|---|
| repo-researcher | gpt-6-luna | medium | read-only | inventory and investigation |
| implementation-worker | gpt-6.1-sol | medium | workspace-write | delegated implementation |
| visual-director | gpt-6-astra | high | workspace-write | visual direction and redesign loop |
| visual-reviewer | gpt-6.1-sol | high | read-only | evidence-gated visual acceptance |
| motion-specialist | gpt-6.1-sol | high | read-only | motion choreography and timing |
| test-verifier | gpt-6-luna | medium | read-only | deterministic verification |
| docs-reporter | gpt-6-luna | medium | workspace-write | factual reports |
| git-reviewer | gpt-6-luna | medium | read-only | Git scope and risk review |
| git-committer | gpt-6-luna | low | workspace-write | staging, commit, normal push |

If a future runtime lacks a selected model, resolve to the newest available model in the same capability tier and record the runtime result; do not use a stale fixed-model claim.

## Shared operating policy

Preserve unrelated user changes. Root retains orchestration, ownership, integration, and final acceptance. Normal reads, edits in delegated scope, tests, temporary renders, `git add`, commits, and normal pushes are allowed. `reset --hard`, `clean -fdx`, force pushes, branch deletion, and history rewrites require separate user confirmation. YOLO/full access is a runtime execution mode, not permission to ignore those rules.

Pencil MCP is preferred for interactive `.pen` design, inspection, screenshots, and native export. Programmatic edits are allowed for deterministic geometry, bulk updates, coordinate computation, structured JSON, templates, and repetitive mechanical work. They require reopen/render, inspection of actual output, and structural validation; successful generation alone is not visual acceptance. If unavailable, report `PENCIL_MCP_UNAVAILABLE` and continue with an auditable validated path when suitable.

`visual-director` owns advanced composition redesign and implementation within delegated scope and must use inspect ? render ? screenshot ? diagnose ? modify ? render again. `visual-reviewer` cannot return PASS without rendered evidence and otherwise returns `INSUFFICIENT_VISUAL_EVIDENCE`. `motion-specialist` starts with choreography, timing, anticipation, settle, hold, stagger, easing, continuity, hierarchy, and beat synchronization; mathematical wave/Gaussian analysis is conditional on actual renderer use.

## Delegation

Use the strongest model only where ambiguity and visual value justify it. Keep implementation, tests, docs, and Git work autonomous within scope. Runtime sandbox and approval state outrank this prose.
