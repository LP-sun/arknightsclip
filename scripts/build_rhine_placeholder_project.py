"""Build a presentation-only Rhine placeholder project from manifests."""
from __future__ import annotations
import json, hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "generated/rhine/final_placeholder"
MANIFESTS = sorted((ROOT / "data/manifests").glob("*.json"))
SELECTED = MANIFESTS[:42]
FPS = 24

def slot_status(slot: dict) -> str:
    if slot.get("own") is False and slot.get("no_info") is True:
        return "confirmed_unowned"
    if slot.get("own") is True:
        if any(slot.get(k) is None for k in ("elite", "level", "potential")):
            return "unverified"
        return "confirmed_owned"
    return "missing_data"

def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    scenes, inventory = [], []
    for i, path in enumerate(SELECTED):
        data = json.loads(path.read_text(encoding="utf-8"))
        art = data.get("full_art_path") or ""
        asset_state = "ready" if art and Path(art).exists() else "placeholder_asset"
        players = []
        for pid, raw in data.get("players", {}).items():
            status = slot_status(raw)
            if asset_state == "placeholder_asset":
                inventory.append({"operator": data["operator_id"], "player": pid, "missing_field": "full_art", "placeholder_type": "ASSET_PENDING", "source_reason": "manifest full_art_path missing"})
            if status in {"missing_data", "unverified"}:
                inventory.append({"operator": data["operator_id"], "player": pid, "missing_field": "player_state", "placeholder_type": status.upper(), "source_reason": "source manifest incomplete or unverified"})
            players.append({"player_id": pid, "status": status, "placeholder": status not in {"confirmed_owned", "confirmed_unowned"}, "own": raw.get("own"), "elite": raw.get("elite"), "level": raw.get("level"), "potential": raw.get("potential")})
        scenes.append({"operator_id": data["operator_id"], "operator_name": data["operator_name"], "start_frame": i * 24, "duration_frames": 24, "full_art": art, "asset_status": asset_state, "players": players})
    project = {"version": 1, "kind": "placeholder_presentation", "fps": FPS, "width": 1920, "height": 1080, "source_manifest_count": len(MANIFESTS), "selected_scene_count": len(scenes), "scenes": scenes}
    (OUT / "project.json").write_text(json.dumps(project, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "placeholder_inventory.json").write_text(json.dumps(inventory, ensure_ascii=False, indent=2), encoding="utf-8")
    report = ["# Rhine placeholder inventory", "", f"Repository manifests: {len(MANIFESTS)}", f"Selected scenes: {len(scenes)} (deterministic lexical order, first 42)", "", "Unknown source fields are rendered as DATA PENDING or UNVERIFIED. Confirmed own=false/no_info=true remains NO INFO.", "", f"Placeholder records: {len(inventory)}", ""]
    report += [f"- {x['operator']} | {x['player']} | {x['missing_field']} | {x['placeholder_type']} | {x['source_reason']}" for x in inventory]
    (ROOT / "reports/rhine_placeholder_inventory.md").write_text("\n".join(report), encoding="utf-8")
    digest = hashlib.sha256((OUT / "project.json").read_bytes()).hexdigest()
    counts = {"confirmed_owned": 0, "confirmed_unowned": 0, "missing_data": 0, "unverified": 0, "placeholder_asset": sum(s["asset_status"] == "placeholder_asset" for s in scenes)}
    for s in scenes:
        for p in s["players"]: counts[p["status"]] = counts.get(p["status"], 0) + 1
    (OUT / "render_report.json").write_text(json.dumps({"project_sha256": digest, "fps": FPS, "frames": len(scenes)*24, "duration_seconds": len(scenes), "audio_source": r"E:\明日方舟报菜名\明日方舟报菜名\明日方舟报菜名（女神异闻录3  月行水上）.mp3", "status": "rendered_placeholder_preview", "status_counts": counts}, ensure_ascii=False, indent=2), encoding="utf-8")

if __name__ == "__main__": main()
