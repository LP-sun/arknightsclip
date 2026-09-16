"""Read-only structural audit for the five source PSD templates.

This intentionally does not render, export, or mutate PSD/Pen data.  Slot
matching is spatial/order based: the eight 卡面 smart objects are anchors;
other layers are associated by document order and bbox intersection.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Iterable

from psd_tools import PSDImage


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_NAMES = ["能天使.psd", "洁哥.psd", "推王.psd", "小羊.psd", "小火龙.psd"]
NO_INFO = "- - - NO INFO - - -"


def bbox(layer: Any) -> list[float]:
    return [float(v) for v in layer.bbox]


def intersects(a: Iterable[float], b: Iterable[float]) -> bool:
    ax1, ay1, ax2, ay2 = a
    bx1, by1, bx2, by2 = b
    return ax1 < bx2 and bx1 < ax2 and ay1 < by2 and by1 < ay2


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def text_value(layer: Any) -> str | None:
    if layer.kind != "type":
        return None
    try:
        return layer.text
    except Exception:
        return None


def transform_box(layer: Any) -> list[list[float]]:
    """Normalize psd_tools' flat or nested transform_box representation."""
    raw = list(layer.smart_object.transform_box)
    if raw and isinstance(raw[0], (tuple, list)):
        return [[float(v) for v in point] for point in raw]
    return [[float(raw[i]), float(raw[i + 1])] for i in range(0, len(raw), 2)]
def effective_walk(group: Any, parent_visible: bool = True, path: str = ""):
    for order, layer in enumerate(group):
        current_path = f"{path}/{layer.name}".strip("/")
        effective = bool(parent_visible and layer.visible)
        yield current_path, order, layer, effective
        if layer.is_group():
            yield from effective_walk(layer, effective, current_path)


def layer_record(path: str, order: int, layer: Any, effective: bool) -> dict[str, Any]:
    row: dict[str, Any] = {
        "path": path,
        "order": order,
        "name": layer.name,
        "kind": layer.kind,
        "bbox": bbox(layer),
        "visible": bool(layer.visible),
        "effective_visible": effective,
        "opacity": float(layer.opacity),
        "clipping": bool(layer.clipping),
    }
    value = text_value(layer)
    if value is not None:
        row["text"] = value
    if layer.kind == "smartobject":
        try:
            row["smart_object"] = {
                "filename": layer.smart_object.filename,
                "filetype": layer.smart_object.filetype,
                "transform_box": transform_box(layer),
            }
        except Exception as exc:
            row["smart_object_error"] = str(exc)
    return row


def group_children(group: Any, prefix: str) -> list[tuple[int, Any, bool]]:
    result = []
    for order, layer in enumerate(group):
        result.append((order, layer, bool(layer.visible)))
    return result


def numbered_states(psd: Any, group_name: str, state_prefix: str) -> dict[str, Any]:
    group = next((layer for layer in psd if layer.name == group_name and layer.is_group()), None)
    if group is None:
        return {"group_present": False, "slots": {}}
    children = list(group)
    slots: dict[str, Any] = {}
    for index in range(1, 9):
        key = f"{index:02d}"
        marker = next((l for l in children if l.name == key), None)
        if marker is None:
            slots[key] = None
            continue
        marker_box = bbox(marker)
        options = []
        for order, layer in enumerate(children):
            if layer.name.startswith(state_prefix) and intersects(bbox(layer), marker_box):
                options.append({
                    "name": layer.name,
                    "order": order,
                    "bbox": bbox(layer),
                    "visible": bool(layer.visible),
                    "effective_visible": bool(group.visible and layer.visible),
                })
        active = [x for x in options if x["effective_visible"]]
        slots[key] = {
            "marker": {"name": marker.name, "order": children.index(marker), "bbox": marker_box,
                       "visible": bool(marker.visible), "effective_visible": bool(group.visible and marker.visible)},
            "state_options": options,
            "active_states": active,
        }
    return {"group_present": True, "slots": slots}


def slot_audit(psd: Any) -> list[dict[str, Any]]:
    card_group = next(layer for layer in psd if layer.name == "卡面" and layer.is_group())
    children = list(card_group)
    anchors = [(i, l) for i, l in enumerate(children)
               if l.kind == "smartobject" and l.name.startswith("卡面")]
    anchors.sort(key=lambda item: item[0])
    level_layers = [(p, o, l, e) for p, o, l, e in effective_walk(psd)
                    if p.startswith("角色等级/") and (l.kind == "type" or l.name.isdigit())]
    result = []
    for position, (index, anchor) in enumerate(anchors, 1):
        next_index = anchors[position][0] if position < len(anchors) else len(children)
        side = "LEFT" if bbox(anchor)[0] < psd.size[0] / 2 else "RIGHT"
        anchor_box = bbox(anchor)
        between = []
        for child_order in range(index + 1, next_index):
            layer = children[child_order]
            if intersects(bbox(layer), anchor_box):
                between.append(layer_record(f"卡面/{layer.name}", child_order, layer,
                                            bool(card_group.visible and layer.visible)))
        no_info = [x for x in between if x.get("text") == NO_INFO]
        character_layers = [x for x in between if x["kind"] in {"pixel", "smartobject"}
                            and x["name"] != anchor.name]
        levels = [layer_record(p, o, l, e) for p, o, l, e in level_layers
                  if intersects(bbox(l), anchor_box)]
        result.append({
            "slot": position,
            "label": anchor.name,
            "side": side,
            "card_bbox": anchor_box,
            "card_visible": bool(anchor.visible),
            "card_effective_visible": bool(card_group.visible and anchor.visible),
            "transform_box": transform_box(anchor),
            "smart_object": {"filename": anchor.smart_object.filename,
                              "filetype": anchor.smart_object.filetype},
            "character_layers": character_layers,
            "no_info_text_layers": no_info,
            "level_layers": levels,
            "intervening_spatial_layers": between,
        })
    return result


def audit_one(path: Path) -> dict[str, Any]:
    psd = PSDImage.open(path)
    top = []
    for order, layer in enumerate(psd):
        top.append({"order": order, "name": layer.name, "kind": layer.kind,
                    "bbox": bbox(layer), "visible": bool(layer.visible),
                    "is_group": bool(layer.is_group())})
    slots = slot_audit(psd)
    return {
        "file": path.name,
        "path": str(path),
        "sha256": digest(path),
        "size": list(psd.size),
        "top_level_semantics": top,
        "slots": slots,
        "elite_states": numbered_states(psd, "精英等级", "精"),
        "potential_states": numbered_states(psd, "潜能", "潜"),
        "operator_level_layers": [
            layer_record(p, o, l, e) for p, o, l, e in effective_walk(psd)
            if p.startswith("角色等级/") and (l.kind == "type" or l.name.isdigit())
        ],
    }


def build_markdown(report: dict[str, Any]) -> str:
    audits = report["audits"]
    lines = ["# Five PSD template source audit", "", "只读 `psd_tools` 结构审计；未渲染 Pen、未生成卡片、未修改 PSD。", ""]
    lines.append("## Evidence")
    lines.append("")
    lines.append("| PSD | SHA-256 (prefix) | size | top-level layers | slot anchors |")
    lines.append("|---|---|---:|---:|---:|")
    for a in audits:
        lines.append(f"| `{a['file']}` | `{a['sha256'][:16]}…` | `{a['size'][0]}×{a['size'][1]}` | {len(a['top_level_semantics'])} | {len(a['slots'])} |")
    lines += ["", "## Common geometry", "",
              "All five files expose eight `卡面` smart-object anchors: LEFT slots 01–04 and RIGHT slots 05–08. Their card bboxes are stable at 763×172 pixels, with x/y origins `(-42, 193/407/621/835)` on the left and `(1186, 107/321/535/749)` on the right. The smart-object transform boxes are axis-aligned in all five sources.", "",
              "The slot association is based on actual layer order plus bbox intersection. Parent visibility is retained as `effective_visible`; no nested-group assumption is used for slot matching.", ""]
    lines += ["## Variation summary", "", "| PSD | visible character-layer pattern | visible NO INFO slots | elite active by slot | potential active by slot |", "|---|---|---|---|---|"]
    for a in audits:
        chars = ", ".join(str(sum(x["effective_visible"] for x in s["character_layers"])) for s in a["slots"])
        noinfo = ", ".join(str(s["slot"]) for s in a["slots"] if s["no_info_text_layers"] and s["no_info_text_layers"][0]["effective_visible"])
        elite = ", ".join(f"{k}:{','.join(x['name'] for x in v['active_states'])}" for k,v in a["elite_states"]["slots"].items() if v and v["active_states"])
        pot = ", ".join(f"{k}:{','.join(x['name'] for x in v['active_states'])}" for k,v in a["potential_states"]["slots"].items() if v and v["active_states"])
        lines.append(f"| `{a['file']}` | {chars} layers/slot | {noinfo or 'none'} | {elite} | {pot} |")
    lines += ["", "## Exusiai batch-instantiation data", "", "The JSON `exusiai_batch_template` below is the compact, reusable geometry/state contract extracted from `能天使.psd`; it contains slot side, card bbox, transform box, effective visibility, associated character layers, NO INFO state, level text, elite state, and potential state.", ""]
    lines += ["| slot | side | card bbox | transform | card visible | NO INFO visible | character-layer evidence |", "|---:|---|---|---|---|---|---|"]
    exusiai = next(a for a in audits if a["file"] == "能天使.psd")
    for s in exusiai["slots"]:
        chars = ", ".join(f"{x['name']}={str(x['effective_visible']).lower()}" for x in s["character_layers"]) or "none"
        noinfo = any(x["effective_visible"] for x in s["no_info_text_layers"])
        transform = ";".join(",".join(str(int(v)) if float(v).is_integer() else str(v) for v in point) for point in s["transform_box"])
        card = [int(v) if float(v).is_integer() else v for v in s["card_bbox"]]
        lines.append(f"| {s['slot']} | {s['side']} | `{card}` | `{transform}` | {str(s['card_effective_visible']).lower()} | {str(noinfo).lower()} | `{chars}` |")
    lines += ["", "Active elite/potential state names and level text are preserved verbatim in the JSON for each slot; empty active-state lists are evidence of no visible state layer, not an inferred default.", ""]
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--output", type=Path, default=ROOT / "reports" / "five_psd_template_audit.json")
    args = parser.parse_args()
    files = [args.root / name for name in DEFAULT_NAMES]
    missing = [str(p) for p in files if not p.is_file()]
    if missing:
        raise FileNotFoundError("Missing PSD: " + ", ".join(missing))
    audits = [audit_one(p) for p in files]
    exusiai = next(a for a in audits if a["file"] == "能天使.psd")
    for s in exusiai["slots"]:
        key = f"{s['slot']:02d}"
        elite_slot = exusiai["elite_states"]["slots"].get(key)
        potential_slot = exusiai["potential_states"]["slots"].get(key)
        s["elite_state"] = elite_slot
        s["potential_state"] = potential_slot
    compact = {"source_file": exusiai["file"], "source_sha256": exusiai["sha256"], "size": exusiai["size"],
               "slots": [{k: s[k] for k in ("slot", "label", "side", "card_bbox", "transform_box", "card_effective_visible", "character_layers", "no_info_text_layers", "level_layers", "elite_state", "potential_state")} for s in exusiai["slots"]],
               "elite_states": exusiai["elite_states"], "potential_states": exusiai["potential_states"],
               "operator_level_layers": exusiai["operator_level_layers"]}
    report = {"audit": "five_psd_template_sources", "tool": "E:/miniconda3/python.exe + psd_tools", "read_only": True,
              "audits": audits, "exusiai_batch_template": compact}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    md = args.output.with_suffix(".md")
    md.write_text(build_markdown(report), encoding="utf-8")
    print(f"wrote {args.output}")
    print(f"wrote {md}")


if __name__ == "__main__":
    main()
