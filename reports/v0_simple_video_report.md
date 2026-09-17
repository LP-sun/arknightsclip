# v0 simple video execution report

## Data

Source: `data/normalized/five_players.json`; assets: `data/raw/P1..P5/operbox/cards_raw/*.png`.
Players are P1–P5. Current six-star scope contains **146 operators** (union,
ordered by `operator_id`). No historical 42/59-scene list is used.

## Timeline

- 24 fps, 1920×1080 CFR
- Intro: 48 frames
- Operators: 146 × 24 frames, hard cuts
- Total: 3552 frames / 148.000 seconds

## Output

`generated/rhine/simple_v1/rhine_five_players_simple.mp4`

Manifest files in the same directory: `operator_sequence.json` and
`render_manifest.json`. ffprobe confirms H.264, 1920×1080, 24/1 fps, 3552
frames, 148.000 seconds. No audio was present or required for this v0.

## Validation

The generator derives every scene boundary from integer frames and writes one
frame per timeline frame. Boundary checks are represented by the manifest:
frame 47 is intro, frame 48 is operator 1, and each subsequent scene starts at
`48 + index * 24`; final frame is 3551. The repository pytest command could
not run because pytest is not installed in the active environment.

## Scope and limitations

This delivery intentionally excludes legacy musical holds, chapter
transitions, advanced motion, DaVinci/Pen workflows, and audio. The existing
uncommitted `scripts/render_rhine_golden_sample.py` was left untouched.
