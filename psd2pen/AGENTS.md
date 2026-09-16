# AGENTS.md — psd2pen

## Mission

Recreate the original PSD `character_cards` layer in Pen.dev with high fidelity.

Order:
1. one owned card;
2. LEFT / RIGHT reusable components;
3. OWNED / NO_INFO;
4. 4 LEFT + 4 RIGHT full transparent layer (1920×1080), then derive 5 people by changing instance visibility/data only.

Do not rebuild the whole PSD screen.

## Required Pen MCP

The MCP server name is exactly `pencil`.

Before editing:
1. `pencil.read_skill()`
2. `pencil.get_app_state()`
3. use `pencil.get_style()` when useful
4. edit with `pencil.execute(...)`
5. screenshot through `TakeScreenshot(...)`
6. export through `Export(...)`

If `pencil` is unavailable, stop with `PENCIL_MCP_NOT_CONNECTED`.

**硬性规则：无法连接 `pencil` MCP 时，请勿对任何 `.pen` 文件进行任何形式的修改。**
不得直接编辑原始 JSON、使用脚本批量改写、通过其他渲染器替代修改，或让子代理绕过此限制；只能停止相关工作并报告 `PENCIL_MCP_NOT_CONNECTED`。

Never silently substitute Pillow, React/CSS, direct raw `.pen` JSON mutation, or mouse-coordinate automation.

## Fidelity

`character_cards.png` is the visual ground truth.

Do not redesign it into generic cyberpunk UI.

Priority:
1. silhouette
2. layered metallic frame
3. operator crop
4. level badge
5. elite/potential placement
6. shadow/texture
7. NO INFO language

At least five single-card visual iterations are mandatory.

## Stage gates

- Stage 1: one owned card
- Stage 2: LEFT / RIGHT
- Stage 3: OWNED / NO_INFO
- Stage 4: 8-player layer (4 LEFT + 4 RIGHT)

Do not advance if Stage 1 is visibly weak.

## Subagents

Read `.codex/SUBAGENT_STRATEGY.md`.

Root owns Pen MCP state, visual judgement, stage gates, final acceptance.

Delegate only bounded mechanical work that does not edit the shared Pen document.

Model escalation policy:

Default:
- Use Luna for file inspection, measurements, scripts, asset inventory,
  repetitive Pen node edits, reporting, and deterministic tasks.

Escalate to Sol when:
- performing multimodal reference-vs-render visual review;
- deciding whether a stage passes;
- choosing between competing layout/material implementations;
- debugging a Pen design that failed to improve after one iteration.

Escalate to Astra only when:
- two consecutive Sol-guided visual iterations fail to materially improve fidelity;
- the reference requires a new structural interpretation;
- Pen.dev capability constraints require redesigning the rendering strategy.

After the high-level decision is made, return execution to Luna.
