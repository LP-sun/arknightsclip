"""Apply approved batch data to a Pencil template JSON copy.

This tool is intentionally mechanical. It never creates geometry or changes
the node tree; it only updates registered instance descendants.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path


ALLOWED = {"enabled", "content", "fill", "x", "y", "width", "height", "viewBox"}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def walk(node):
    if isinstance(node, dict):
        yield node
        for value in node.values():
            yield from walk(value)
    elif isinstance(node, list):
        for value in node:
            yield from walk(value)


def index_nodes(doc):
    indexed = {}
    for node in walk(doc):
        node_id = node.get("id")
        if node_id:
            if node_id in indexed:
                raise ValueError(f"duplicate node id: {node_id}")
            indexed[node_id] = node
    return indexed


def validate_job(job, nodes):
    if not isinstance(job, dict) or not isinstance(job.get("updates"), list):
        raise ValueError("job must contain an updates array")
    seen = set()
    for update in job["updates"]:
        node_id = update.get("id")
        fields = update.get("fields")
        if not isinstance(node_id, str) or node_id not in nodes:
            raise ValueError(f"unknown node id: {node_id}")
        if node_id in seen:
            raise ValueError(f"duplicate update for node: {node_id}")
        seen.add(node_id)
        if not isinstance(fields, dict) or not fields:
            raise ValueError(f"empty fields for node: {node_id}")
        illegal = set(fields) - ALLOWED
        if illegal:
            raise ValueError(f"unsupported fields for {node_id}: {sorted(illegal)}")


def apply(template: Path, job_path: Path, output: Path, receipt: Path):
    if output.exists() or receipt.exists():
        raise ValueError("refusing to overwrite output or receipt")
    doc = load(template)
    job = load(job_path)
    nodes = index_nodes(doc)
    validate_job(job, nodes)
    result = copy.deepcopy(doc)
    result_nodes = index_nodes(result)
    for update in job["updates"]:
        result_nodes[update["id"]].update(copy.deepcopy(update["fields"]))
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    receipt.parent.mkdir(parents=True, exist_ok=True)
    receipt.write_text(json.dumps({
        "template": str(template.resolve()),
        "template_sha256": sha(template),
        "job": str(job_path.resolve()),
        "job_sha256": sha(job_path),
        "output": str(output.resolve()),
        "output_sha256": sha(output),
        "updated_nodes": [u["id"] for u in job["updates"]],
        "status": "written",
    }, ensure_ascii=False, indent=2), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("template")
    parser.add_argument("job")
    parser.add_argument("output")
    parser.add_argument("--receipt", required=True)
    args = parser.parse_args()
    apply(Path(args.template), Path(args.job), Path(args.output), Path(args.receipt))
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
