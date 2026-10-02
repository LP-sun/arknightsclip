#!/usr/bin/env python3
"""Validate project Codex agent registration and capability-tier policy."""
from __future__ import annotations
from pathlib import Path
import sys, tomllib
ROOT=Path(__file__).resolve().parent; AGENTS=ROOT/'agents'; errors=[]
INVENTORY={
 "gpt-6-astra":{"effort":{"low","medium","high","xhigh","max","ultra"},"tier":"flagship"},
 "gpt-6.1-sol":{"effort":{"low","medium","high","xhigh","max","ultra"},"tier":"strong"},
 "gpt-6-luna":{"effort":{"low","medium","high","xhigh","max"},"tier":"efficient"},
}
EXPECTED={
 "repo-researcher":("gpt-6-luna","medium","read-only"),
 "implementation-worker":("gpt-6.1-sol","medium","workspace-write"),
 "visual-director":("gpt-6-astra","high","workspace-write"),
 "visual-reviewer":("gpt-6.1-sol","high","read-only"),
 "motion-specialist":("gpt-6.1-sol","high","read-only"),
 "test-verifier":("gpt-6-luna","medium","read-only"),
 "docs-reporter":("gpt-6-luna","medium","workspace-write"),
 "git-reviewer":("gpt-6-luna","medium","read-only"),
 "git-committer":("gpt-6-luna","low","workspace-write"),
}
def load(path):
 try:return tomllib.loads(path.read_text(encoding="utf-8"))
 except Exception as e: errors.append(f"{path.name}: TOML parse error: {e}"); return {}
config=load(ROOT/'config.toml')
if config.get('approval_policy')!='on-request': errors.append('root approval_policy must be on-request')
if config.get('sandbox_mode')!='danger-full-access': errors.append('root sandbox_mode must be danger-full-access')
files=sorted(AGENTS.glob('*.toml')); seen={}; paths=set()
for path in files:
 d=load(path); n=d.get('name')
 if not isinstance(n,str) or not n: errors.append(f'{path.name}: missing name'); continue
 if n in seen: errors.append(f'duplicate agent name: {n}')
 seen[n]=d
 if d.get('model') not in INVENTORY: errors.append(f'{n}: model is not in current resolved inventory')
 if d.get('model_reasoning_effort') not in INVENTORY.get(d.get('model'),{}).get('effort',set()): errors.append(f'{n}: unsupported reasoning effort')
 if d.get('approval_policy')!='on-request': errors.append(f'{n}: approval_policy must be on-request')
 if d.get('sandbox_mode') not in {'read-only','workspace-write'}: errors.append(f'{n}: invalid sandbox_mode')
 if not d.get('developer_instructions'): errors.append(f'{n}: missing developer_instructions')
for n,(model,effort,sandbox) in EXPECTED.items():
 d=seen.get(n)
 if not d: errors.append(f'missing agent: {n}'); continue
 for key,want in [('model',model),('model_reasoning_effort',effort),('sandbox_mode',sandbox)]:
  if d.get(key)!=want: errors.append(f'{n}: expected {key}={want!r}')
reg=config.get('agents',{})
for n,d in seen.items():
 entry=reg.get(n)
 if not isinstance(entry,dict): errors.append(f'config.toml: {n} is not registered'); continue
 want=f'agents/{n}.toml'
 if entry.get('config_file')!=want: errors.append(f'config.toml: {n} config_file should be {want!r}')
for n in EXPECTED:
 if n not in reg: errors.append(f'config.toml: missing registration for {n}')
text='\n'.join(p.read_text(encoding='utf-8') for p in [ROOT/'SUBAGENT_STRATEGY.md',*files])
for needle in ['renderers/production/','INSUFFICIENT_VISUAL_EVIDENCE','PENCIL_MCP_UNAVAILABLE']:
 if needle not in text: errors.append(f'policy text missing {needle}')
print('Subagent config status')
for n in sorted(seen):
 d=seen[n]; print(f"{n:24} model={d.get('model'):14} reasoning={d.get('model_reasoning_effort'):6} sandbox={d.get('sandbox_mode')}")
if errors:
 print('\nFAILED:'); print('\n'.join(f'- {e}' for e in errors)); sys.exit(1)
print('\nStatic checks: PASS')
