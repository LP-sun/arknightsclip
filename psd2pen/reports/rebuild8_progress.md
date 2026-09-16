# Eight-slot Pen rebuild

Target: reproduce the Exusiai reference as four LEFT and four RIGHT cards. This supersedes the earlier five-slot output requirement. Preserve the original experiment document.

## Verified source facts

- Original PSD has 1920x1080 canvas, nine top-level groups/layers, eight card smart objects.
- Card source positions: LEFT inner top y = 193, 407, 621, 835; RIGHT = 107, 321, 535, 749.
- Original card artwork, elite0/1/2 and potential1..6 were extracted directly from PSD raster layers. Pen renders the template; extraction does not implement its frame or layout.
- The card silhouette is derived from the embedded smart object's vector-mask knots and transform.
- Existing PNG exports use a difference mask rather than semantic PSD groups. Their hidden RGB can show a full scene in viewers that ignore alpha.
- Source NO INFO slots retain some levels/elite/potential badges. Artwork state and badge visibility must remain independent to reproduce this reference.

## Stage 1 evidence

1. `experiments/rebuild8/iter01/wUVzi.png`: original raster artwork and elite icon, rebuilt right silhouette.
2. `experiments/rebuild8/iter02/wUVzi.png`: original potential icon, badge placement, artwork opacity.
3. `experiments/rebuild8/iter03/wUVzi.png`: supported font substitute, inner edge, shadow.
4. `experiments/rebuild8/iter04/jRl4Y.png`: background-context comparison, vector-derived potential plate, transparent frame interior.
5. `experiments/rebuild8/iter05/jRl4Y.png`: numeric size/spacing/ring calibration.

The first diagnostic `iter01/Ha5vM.png` is a failed render probe and is NOT a successful visual iteration. Native Move out-and-back refreshed the new nested nodes; reference and final screenshots are required after insertion.

## Known limitation

Bahnschrift is the PSD's font but Pencil reports it invalid. Barlow Semi Condensed is used for editable level numbers and Barlow for small labels; typography is approximate, not pixel-identical.

## Current acceptance

Superseded on 2026-09-16 by `../delivery/acceptance_report.md`: nine iterations retained, LEFT/RIGHT and four-state review completed, eight-slot transparent layer exported, user-assisted native save/reopen followed by MCP readback and identical PNG re-export verified. Final whole-layer independent Sol review hit a 429 service limit; root visual/structural acceptance and PNG checks are recorded separately.
