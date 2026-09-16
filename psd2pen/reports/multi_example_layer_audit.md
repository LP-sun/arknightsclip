# Multi-example layer audit

## Scope and source inventory

Audited the five PSD-derived example groups in the project root. Each group contains the same three exported composites (not individually named Photoshop layer files):

| Group | PSD | Exports |
|---|---|---|
| 001_能天使 | 能天使.psd | background.png, character_cards.png, doctor_info.png |
| 002_推王 | 推王.psd | background.png, character_cards.png, doctor_info.png |
| 003_小火龙 | 小火龙.psd | background.png, character_cards.png, doctor_info.png |
| 004_小羊 | 小羊.psd | background.png, doctor_info.png, character_cards.png |
| 005_洁哥 | 洁哥.psd | background.png, doctor_info.png, character_cards.png |

All five `character_cards.png` files are 1920x1080. The three exports are cleanly separated by screen function; the card export itself is the ground truth for this task. No `exusiai_test.json` was found.

## Cross-sample correspondence

Across all five card composites, the same semantic regions recur:

1. Five left/right-facing horizontal cards around a large operator artwork area.
2. A directional polygonal card body: left-side cards point inward to the right; right-side cards point inward to the left.
3. A translucent light content field bounded by a white inner edge, dark metallic edge, grey extrusion/highlight, and soft outer shadow.
4. A dark level/profession block adjacent to the operator portrait, with circular `LV` and number treatment plus a large white profession/elite glyph.
5. A small dark diamond/hexagonal icon at the inward tip.
6. An owned operator portrait crop inside the card body, and a faded empty body with centered `--- NO INFO ---` for unowned slots.
7. A separate operator/doctor badge at the outer end of each card. It is visible in the composite but belongs to the surrounding player/doctor presentation and should not be mistaken for the reusable card frame.

The level values, operator artwork, crop content, background art, colour accents, and some tip icons vary by sample. The frame silhouette, card rhythm, level block geometry, NO INFO language, and directional placement remain stable.

## Shared vs operator-specific decomposition

### Shared reusable component structure

- `FRAME_OUTER_SHADOW`
- `FRAME_DARK_METAL`
- `FRAME_LIGHT_METAL`
- `FRAME_INNER_WHITE`
- `CONTENT_MASK`
- directional tip and decorative diagonal geometry
- `LEVEL_BADGE` container and typography hierarchy
- profession/elite glyph region
- `POTENTIAL_BADGE` anchor region
- `NO_INFO_STATE` wording, spacing, and faded panel treatment
- highlight/shadow and restrained translucent texture layers

### Operator-specific raster content

- operator portrait/artwork
- artwork crop/position within the mask
- operator-associated colour or scene texture visible behind the portrait
- level number and player data
- elite/potential values and their icon variants
- any operator-specific tip emblem

### Uncertain / needs review

- exact Photoshop source-layer names and blend modes, because the supplied exports are three screen composites rather than per-Photoshop-layer files;
- whether every tip emblem is an elite icon or a related operator/profession marker;
- exact crop polygon coordinates at production scale, to be measured from selected left and right cards;
- the separate outer doctor badge boundary relative to the requested `character_cards` layer.

## Canonical Pen component map

```text
CHARACTER_CARD_LEFT / CHARACTER_CARD_RIGHT
├─ FRAME
│  ├─ FRAME_OUTER_SHADOW
│  ├─ FRAME_DARK_METAL
│  ├─ FRAME_LIGHT_METAL
│  └─ FRAME_INNER_WHITE
├─ CONTENT_MASK
│  ├─ OPERATOR_IMAGE (owned)
│  ├─ DECORATIVE_TEXTURE
│  └─ NO_INFO_STATE (unowned, visibility-switched)
├─ LEVEL_BADGE
├─ ELITE_BADGE / PROFESSION_GLYPH
└─ POTENTIAL_BADGE / TIP_ICON
```

Rebuild in editable Pen nodes: silhouette, frame layers, mask, level badge structure, text, state switching, layout, and directional geometry. Raster assets are appropriate for operator artwork, inherently raster texture, and supplied emblem/icon artwork when available. The full flattened `character_cards.png` must not be used as the card implementation.

## Reference selection and plan change

- Primary reconstruction target: `001_能天使/character_cards.png`, because it clearly shows both directional families and multiple owned/unowned examples.
- Validation reference: `002_推王/character_cards.png`, which confirms the same frame system over a darker, high-contrast operator image; `004_小羊/character_cards.png` is an additional light/pink validation sample.
- Left-oriented reference: the left column cards in `001_能天使/character_cards.png` (tips point right).
- Right-oriented reference: the right column cards in `001_能天使/character_cards.png` (tips point left).

The five-sample audit changes the reconstruction plan in three ways: first, frame and state geometry will be parameterized before artwork is placed; second, left/right will be reconstructed as distinct directional components rather than flipping an entire card; third, operator artwork and level/icon data will remain replaceable assets/parameters. Stage 1 will use one owned card, but its silhouette, badge, and NO INFO reserve will be checked against the other four samples before advancing.

## Stage 0 result

STAGE 0 COMPLETE. The source audit is sufficient to begin measured single-card reconstruction. The per-source-layer naming/blend-mode uncertainty remains documented and will be resolved only where visual comparison or PSD inspection provides evidence.

## Stage 1 checkpoint

The first Pen card structure was created in `character_card_components.pen` and exported through Pencil. The current checkpoint is **NOT PASS**: the measured silhouette and layered frame are present, but the operator crop is currently rendered as a transparent checkerboard in Pencil export because the local image fill is not resolving. Work is intentionally held at Stage 1 until the crop asset path/import is fixed and the card can be visually compared again.
