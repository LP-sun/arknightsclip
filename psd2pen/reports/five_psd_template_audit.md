# Five PSD template source audit

只读 `psd_tools` 结构审计；未渲染 Pen、未生成卡片、未修改 PSD。

## Evidence

| PSD | SHA-256 (prefix) | size | top-level layers | slot anchors |
|---|---|---:|---:|---:|
| `能天使.psd` | `c4a2f791c43ac613…` | `1920×1080` | 9 | 8 |
| `洁哥.psd` | `82d5499bae5c34c0…` | `1920×1080` | 7 | 8 |
| `推王.psd` | `1857208706124726…` | `1920×1080` | 9 | 8 |
| `小羊.psd` | `0b2c63ded626f489…` | `1920×1080` | 7 | 8 |
| `小火龙.psd` | `6682e33be52f2434…` | `1920×1080` | 7 | 8 |

## Common geometry

All five files expose eight `卡面` smart-object anchors: LEFT slots 01–04 and RIGHT slots 05–08. Their card bboxes are stable at 763×172 pixels, with x/y origins `(-42, 193/407/621/835)` on the left and `(1186, 107/321/535/749)` on the right. The smart-object transform boxes are axis-aligned in all five sources.

The slot association is based on actual layer order plus bbox intersection. Parent visibility is retained as `effective_visible`; no nested-group assumption is used for slot matching.

## Variation summary

| PSD | visible character-layer pattern | visible NO INFO slots | elite active by slot | potential active by slot |
|---|---|---|---|---|
| `能天使.psd` | 0, 0, 0, 0, 0, 1, 1, 0 layers/slot | 1, 2, 3, 4, 5, 8 | 01:精二, 02:精一, 03:精一, 04:精二, 05:精二, 06:精二, 07:精二, 08:精一 | 02:潜3, 03:潜3, 04:潜3, 05:潜6, 06:潜4, 07:潜2 |
| `洁哥.psd` | 1, 0, 1, 1, 1, 1, 1, 1 layers/slot | 2 | 01:精二, 03:精二, 04:精二, 05:精二, 06:精二, 07:精二, 08:精一 | 01:潜1, 03:潜3, 04:潜2, 05:潜6, 06:潜3, 07:潜3, 08:潜2 |
| `推王.psd` | 1, 1, 1, 1, 1, 1, 1, 1 layers/slot | none | 01:精二, 02:精二, 03:精二, 05:精二, 06:精二, 07:精二, 08:精0 | 01:潜2, 02:潜2, 03:潜5, 05:潜3, 06:潜3, 07:潜1, 08:潜1 |
| `小羊.psd` | 1, 1, 1, 1, 1, 1, 1, 1 layers/slot | none | 01:精二, 02:精二, 03:精二, 04:精二, 05:精二, 06:精二, 07:精二, 08:精二 | 01:潜1, 02:潜1, 03:潜1, 04:潜1, 05:潜3, 06:潜1, 07:潜1, 08:潜1 |
| `小火龙.psd` | 1, 1, 1, 1, 1, 1, 1, 1 layers/slot | none | 01:精二, 02:精二, 03:精二, 04:精二, 05:精二, 06:精二, 07:精二, 08:精二 | 01:潜2, 02:潜2, 03:潜3, 04:潜1, 05:潜5, 06:潜1, 07:潜4, 08:潜1 |

## Exusiai batch-instantiation data

The JSON `exusiai_batch_template` below is the compact, reusable geometry/state contract extracted from `能天使.psd`; it contains slot side, card bbox, transform box, effective visibility, associated character layers, NO INFO state, level text, elite state, and potential state.

| slot | side | card bbox | transform | card visible | NO INFO visible | character-layer evidence |
|---:|---|---|---|---|---|---|
| 1 | LEFT | `[-42, 193, 721, 365]` | `-42,193;721,193;721,365;-42,365` | true | true | `none` |
| 2 | LEFT | `[-42, 407, 721, 579]` | `-42,407;721,407;721,579;-42,579` | true | true | `图层 32=false` |
| 3 | LEFT | `[-42, 621, 721, 793]` | `-42,621;721,621;721,793;-42,793` | true | true | `图层 35=false` |
| 4 | LEFT | `[-42, 835, 721, 1007]` | `-42,835;721,835;721,1007;-42,1007` | true | true | `图层 37=false` |
| 5 | RIGHT | `[1186, 107, 1949, 279]` | `1949,279;1186,279;1186,107;1949,107` | true | true | `图层 33=false` |
| 6 | RIGHT | `[1186, 321, 1949, 493]` | `1949,493;1186,493;1186,321;1949,321` | true | false | `图层 36=true` |
| 7 | RIGHT | `[1186, 535, 1949, 707]` | `1949,707;1186,707;1186,535;1949,535` | true | false | `图层 38=true` |
| 8 | RIGHT | `[1186, 749, 1949, 921]` | `1949,921;1186,921;1186,749;1949,749` | true | true | `图层 34=false` |

Active elite/potential state names and level text are preserved verbatim in the JSON for each slot; empty active-state lists are evidence of no visible state layer, not an inferred default.

