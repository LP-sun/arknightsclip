# Rhine Renderer Visual Acceptance Report

## 1. Acceptance Overview
This visual acceptance test suite validates the end-to-end rendering quality of Rhine Renderer,
verifying that both hero-art mode and first-class card-art fallback mode render deterministically
without visual distortion, clipping, or unhandled errors.

- **Canvas Resolution**: 1920 x 1080
- **Target Frame Rate**: 24.0 FPS
- **Safe Margins**: Top 36px, Bottom 36px, Left 40px, Right 40px
- **Contact Sheet**: `reports/acceptance_frames/contact_sheet.png`

## 2. Representative Frames Summary

| Frame # | Phase / Scenario | Target Operator | Render Mode | Verified Asset Source | Status |
|---|---|---|---|---|---|
| 0012 | Phase 1: Intro / First Operator (Hero Art Mode) | 能天使 (`char_103_angel`) | `hero_art` | `char_103_angel/full.png` | **PASSED** |
| 0036 | Phase 2: Full Artwork Showcase (Hero Art Mode) | 煌 (`char_017_huang`) | `hero_art` | `char_017_huang/full.png` | **PASSED** |
| 0060 | Phase 3: First-Class Card Specimen Fallback (No Hero Art) | 异客 (`char_472_pasngr`) | `card_art` | `cards_raw/char_472_pasngr.png` | **PASSED** |
| 0073 | Phase 4: Mid-Sequence 0.20s Smooth Entrance Momentum | 凯尔希 (`char_003_kalts`) | `hero_art` | `char_003_kalts/full.png` | **PASSED** |
| 0115 | Phase 5: Sequence Outro / High Progress Ribbon | 史尔特尔 (`char_350_surtr`) | `hero_art` | `char_350_surtr/full.png` | **PASSED** |

## 3. Verified Visual Acceptance Criteria
1. **Hero Art Presentation (Mode A)**: Full resolution character artwork properly scaled inside the 840x740 central specimen chamber.
2. **First-Class Card Art Fallback (Mode B)**: For operators missing full hero art (e.g. `char_472_pasngr`), gracefully falls back to displaying the OperBox card specimen alongside the 580x740 acquisition dossier panel without placeholder spoofing.
3. **Decoupled 1920x1080 Stage**: Header and footer telemetry reside within safe bounds; player acquisition matrix scales symmetrically without hardcoded Pen slot offsets.
4. **Continuous Motion Flow**: Camera macro drift and 0.20s transition momentum eliminate PowerPoint-like slideshow abruptness.
