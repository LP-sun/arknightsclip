# Pen local image asset path diagnosis

Date: 2026-09-15

## Active document and node

- Active `.pen`: `E:\明日方舟报菜名\psd2pen\character_card_components.pen`
- Pencil URI used for MCP: `/E:/明日方舟报菜名/psd2pen/character_card_components.pen`
- Operator crop source: `E:\明日方舟报菜名\psd2pen\experiments\pen_character_card\reference\exusiai_operator_crop.png`
- Current image node: `Ey8XX`, named `CONTENT_MASK` (there is no node literally named `OPERATOR_IMAGE`)
- Native imported image node: `z2NjLM`

The initial stored fill was `reference/exusiai_operator_crop.png`. It is a forward-slash relative URL, not absolute, not a malformed Windows backslash path, and it exists only at the experiment-directory path—not at the `.pen` directory path—so it was not a valid `.pen`-relative asset for this document.

## Matrix

| Experiment | `.pen` full path | Asset full path | URL used | Canvas preview | TakeScreenshot | Export | Result |
|---|---|---|---|---|---|---|---|
| Initial direct URL | `E:\明日方舟报菜名\psd2pen\character_card_components.pen` | `E:\明日方舟报菜名\psd2pen\experiments\pen_character_card\reference\exusiai_operator_crop.png` | `reference/exusiai_operator_crop.png` | No, checkerboard | API succeeded; checkerboard | API succeeded; checkerboard | Failed |
| A, strict same-directory test | same | `E:\明日方舟报菜名\psd2pen\test_asset.png` (91 bytes) | `./test_asset.png` (stored by Pencil as `test_asset.png`) | No, checkerboard | Succeeded; checkerboard | Succeeded; checkerboard | Failed |
| B, strict adjacent subdirectory test | same | `E:\明日方舟报菜名\psd2pen\assets\operators\exusiai_card_crop.png` (120211 bytes) | `./assets/operators/exusiai_card_crop.png` (stored as `assets/operators/exusiai_card_crop.png`) | No, checkerboard | Succeeded; checkerboard | Succeeded; checkerboard | Failed |
| F, Pencil native import | same | Pencil-managed imported copy from the loaded crop | `screenshot-site.png` (discovered from imported node `z2NjLM`) | Yes, real crop | Succeeded; real crop | Succeeded; real crop | Passed |

For A and B, the files were verified to exist at the exact resolved locations before assignment. Both used forward slashes. The direct path experiments therefore rule out absolute-path syntax, backslash escaping, and missing files as the sole cause; Pencil's direct local URL resolution still returned checkerboard.

## Native workflow evidence

Pencil loaded the crop through its integrated browser using:

`file:///E:/明日方舟报菜名/psd2pen/experiments/pen_character_card/reference/exusiai_operator_crop.png`

`screenshot-to-canvas` created node `z2NjLM` with fill URL `screenshot-site.png`. Assigning that discovered native reference to `Ey8XX` produced the real operator artwork in the Pen canvas, in `TakeScreenshot(["OIAoS"])`, and in the exported file:

`E:\明日方舟报菜名\psd2pen\experiments\pen_character_card\iterations\OIAoS.png`

## Conclusion

The blocker is fixed through Pencil's native image import/reference workflow. The working fill on `Ey8XX` is now `screenshot-site.png`; the real operator crop is visible in canvas, screenshot, and export. STAGE 1 visual fidelity iteration may resume, but LEFT/RIGHT work has not been started.
