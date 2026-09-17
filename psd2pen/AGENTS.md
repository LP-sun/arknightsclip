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

## Pen MCP and batch JSON workflow

The MCP server name is exactly `pencil`.

Before editing:
1. `pencil.read_skill()`
2. `pencil.get_app_state()`
3. use `pencil.get_style()` when useful
4. edit with `pencil.execute(...)`
5. screenshot through `TakeScreenshot(...)`
6. export through `Export(...)`

Pencil MCP is required to create or structurally revise a template .pen document, inspect its real node tree, make visual decisions, take screenshots, and produce final visual exports. If it is unavailable for one of those tasks, stop with `PENCIL_MCP_NOT_CONNECTED`.

For repeatable batch jobs, a Pencil-created and visually accepted template may be copied and mechanically edited through its .pen JSON. This exception is limited to a documented batch schema: replace image references and text/value/visibility fields on pre-existing, identified instance nodes; it must not synthesize frame geometry, alter component structure, or use an unvalidated JSON path.

Every JSON batch writer must: preserve the accepted template unchanged; write to a new output document; validate the expected node ids/names and field types before mutation; emit an input-to-output manifest and SHA-256 hashes; and fail closed when the template schema differs. At least one representative output per schema/version must be reopened and visually checked in Pencil before release.

Pillow or other raster libraries may inspect exports but must not generate or redraw official card imagery. Do not use React/CSS or mouse-coordinate automation as a substitute for the Pen workflow.

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
