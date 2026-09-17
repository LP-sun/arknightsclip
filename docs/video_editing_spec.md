# Current v0 video editing specification

This is the current baseline for the five-player six-star preview. It is an
editing/timeline contract, independent of the Rhine renderer implementation.

- Canvas: 1920×1080, constant 24 fps.
- Intro: frames 0–47 (48 frames / exactly 2 seconds).
- Operators: current normalized five-player dataset, ordered by `operator_id`;
  each scene is exactly 24 frames and uses a deterministic hard cut.
- No legacy timing files, special musical holds, or browser wall-clock timing.
- Total frames are `48 + operator_count * 24` (no outro in v0).
- Card assets are read directly from `data/raw/P*/operbox/cards_raw/*.png`.

`archive/legacy_data/durations_24fps_perfect.json` remains a historical timing
profile and is not a source of truth for current renders.
