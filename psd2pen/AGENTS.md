# psd2pen agent policy

## Current accepted baseline

Preserve accepted Pen assets and their layer semantics. Treat reference PSDs, accepted `.pen` files, and exported PNGs as design evidence; do not silently replace accepted assets. Native save/reopen remains an explicit Pen.dev operation where Pencil does not expose persistence.

## Preferred Pencil workflow

Pencil MCP is the preferred interactive design, inspection, screenshot, and native export path. When available, inspect the current document and style before complex layout work, then render/export and inspect the actual result.

## Programmatic modification

Programmatic `.pen` edits are allowed for deterministic geometry, bulk instance/data updates, coordinate computation, structured JSON edits, template generation, and repetitive mechanical changes. They are auditable engineering operations, not proof of visual correctness. Afterward reopen/render, inspect screenshots or exports, and validate the document structure. If Pencil MCP is unavailable, report `PENCIL_MCP_UNAVAILABLE`; do not stop the whole task, and use a validated programmatic path when appropriate.

## Verification and preservation

Visual acceptance requires actual rendered frames, screenshots, a contact sheet, or rendered video evidence. Preserve accepted assets and report any intentionally changed baseline. Raster tools may inspect exports but must not silently become a replacement design system.

## Design versus production

`psd2pen/` is a static design/reference workflow. For video delivery, `renderers/production/` is canonical; `renderers/rhine/` is deprecated historical WIP. Design work must not redirect production tasks to Rhine.

## Agent responsibilities

Use `visual-director` for major visual direction and multi-iteration redesign, `visual-reviewer` for evidence-gated read-only acceptance, `motion-specialist` for temporal analysis, and `implementation-worker` for bounded mechanical work or explicitly delegated visual implementation. Root owns shared-file scope and final acceptance.

Historical reconstruction notes (character card stages and five-slot derivatives) are archival context, not a mandatory workflow for future tasks.
