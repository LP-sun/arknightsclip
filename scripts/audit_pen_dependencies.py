#!/usr/bin/env python3
"""
CLI script to audit all .pen design templates and generate portable dependency manifests.
"""

from pathlib import Path
import sys

# Ensure repo root is on sys.path
REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from arknightsclip.assets.pen_dependency_resolver import PenDependencyResolver


def main():
    resolver = PenDependencyResolver(REPO_ROOT)

    pen_files = [
        REPO_ROOT / "psd2pen" / "character_cards_5slot_template.pen",
        REPO_ROOT / "psd2pen" / "character_cards_5slot.pen",
        REPO_ROOT / "psd2pen" / "character_cards_8slot.pen",
        REPO_ROOT / "psd2pen" / "character_card_components.pen",
    ]

    # Filter to existing
    target_files = [p for p in pen_files if p.is_file()]
    print(f"Auditing {len(target_files)} Pen design templates...")

    out_json = REPO_ROOT / "reports" / "pen_asset_dependencies.json"
    out_md = REPO_ROOT / "reports" / "pen_asset_dependencies.md"

    manifest = resolver.generate_manifest(target_files, out_json, out_md)

    print(f"[SUCCESS] Wrote JSON manifest: {out_json}")
    print(f"[SUCCESS] Wrote Markdown report: {out_md}")
    print(f"Total raw_batch operator mappings: {len(manifest['raw_batch_operator_mapping'])}")


if __name__ == "__main__":
    main()
