# AGENTS.md — psd2pen

## Mission

Recreate the original PSD `character_cards` layer in Pen.dev with high fidelity.

Order:
1. one owned card;
2. LEFT / RIGHT reusable components;
3. OWNED / NO_INFO;
4. 4 LEFT + 4 RIGHT full transparent layer (1920×1080), then derive 5 people by changing instance visibility/data only.

Do not rebuild the whole PSD screen.

## Accepted baseline and five-slot derivative

The user has accepted `character_cards_8slot.pen` as complete. Preserve it as the
baseline. `character_cards_5slot.pen` is the independent 3 LEFT + 2 RIGHT
derivative: retain all eight editable instances and show source slots
1, 2, 3, 5, 6; hide 4, 7, 8 without moving/rebuilding the cards.
Use `scripts/generate_five_cards.ps1` for JSON-to-Pencil-to-PNG batches.
Native document save/reopen remains an explicit Pen.dev application operation;
successful PNG exports do not prove the .pen document was saved.

## Required Pen MCP

The MCP server name is exactly `pencil`.

Before editing:
1. `pencil.read_skill()`
2. `pencil.get_app_state()`
3. use `pencil.get_style()` when useful
4. edit with `pencil.execute(...)`
5. screenshot through `TakeScreenshot(...)`
6. export through `Export(...)`

If Pencil MCP is unavailable, do not modify any `.pen` file in any way; stop with `PENCIL_MCP_NOT_CONNECTED`.

Do not directly edit raw `.pen` JSON, use scripts to rewrite `.pen` files, or substitute another renderer or automation path.

Data preparation and batch compilation may happen outside Pencil, but every mutation of a `.pen` document must be performed through Pencil MCP.

**硬性规则：无法连接 `pencil` MCP 时，请勿对任何 `.pen` 文件进行任何形式的修改。**

不得直接编辑 `.pen` JSON，不得通过 Python / PowerShell / Node 脚本批量改写 `.pen`，不得通过复制模板后离线改 JSON 的方式绕过 Pencil MCP。

命令行可以准备数据、manifest、Pencil 执行脚本和校验信息；所有 `.pen` 文档内容修改必须通过 Pencil MCP 完成。

Never silently substitute Pillow, React/CSS, direct raw `.pen` JSON mutation, or mouse-coordinate automation. Pillow or other raster libraries may inspect exports for verification but must not generate or redraw official card imagery.

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
