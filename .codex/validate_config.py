#!/usr/bin/env python3
"""Static validator for the subagent configuration package.

Checks TOML syntax, sandbox modes, and approval policies.
"""
from __future__ import annotations

from pathlib import Path
import sys
import tomllib

ROOT = Path(__file__).resolve().parent
AGENTS = ROOT / "agents"

READ_ONLY_ROLES = {
    "repo-researcher",
    "visual-reviewer",
    "motion-specialist",
    "test-verifier",
    "git-reviewer",
}
WORKSPACE_ROLES = {"implementation-worker", "docs-reporter"}

errors: list[str] = []


def load(path: Path) -> dict:
    try:
        return tomllib.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"{path.name}: TOML parse error: {exc}")
        return {}


config = load(ROOT / "config.toml")
if config.get("approval_policy") != "on-request":
    errors.append("config.toml: root approval_policy must be on-request")

agent_files = sorted(AGENTS.glob("*.toml"))
seen: dict[str, dict] = {}
for path in agent_files:
    data = load(path)
    name = data.get("name")
    if not isinstance(name, str) or not name:
        errors.append(f"{path.name}: missing non-empty name")
        continue
    if not data.get("description"):
        errors.append(f"{path.name}: missing description")
    if not data.get("developer_instructions"):
        errors.append(f"{path.name}: missing developer_instructions")
    if data.get("sandbox_mode") == "danger-full-access":
        errors.append(f"{name}: danger-full-access is forbidden")
    seen[name] = data

for name in sorted(READ_ONLY_ROLES):
    data = seen.get(name)
    if not data:
        errors.append(f"missing agent: {name}")
        continue
    if data.get("sandbox_mode") != "read-only":
        errors.append(f"{name}: expected sandbox_mode=read-only")
    if data.get("approval_policy") != "on-request":
        errors.append(f"{name}: expected approval_policy=on-request")

for name in sorted(WORKSPACE_ROLES):
    data = seen.get(name)
    if not data:
        errors.append(f"missing agent: {name}")
        continue
    if data.get("sandbox_mode") != "workspace-write":
        errors.append(f"{name}: expected sandbox_mode=workspace-write")
    if data.get("approval_policy") != "on-request":
        errors.append(f"{name}: expected approval_policy=on-request")

registered = (config.get("agents") or {})
for name in seen:
    role = registered.get(name)
    if not isinstance(role, dict):
        errors.append(f"config.toml: agent role {name!r} is not explicitly registered")
        continue
    expected = f"agents/{name}.toml"
    if role.get("config_file") != expected:
        errors.append(f"config.toml: {name} config_file should be {expected!r}")

print("Subagent config status")
print("=" * 37)
for name in sorted(seen):
    data = seen[name]
    print(f"{name:24} sandbox={data.get('sandbox_mode'):15} approval={data.get('approval_policy')}")

if errors:
    print("\nFAILED:")
    for error in errors:
        print(f"- {error}")
    sys.exit(1)

print("\nStatic checks: PASS")
