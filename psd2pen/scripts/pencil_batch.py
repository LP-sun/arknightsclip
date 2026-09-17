"""Execute compiled jobs through Pencil MCP and verify native exports (no renderer)."""
import argparse
import asyncio
import json
import os
from pathlib import Path
import shutil

from cards_pipeline import ROOT, YS, read, sha, dump, validate


def check_run(path):
    run = read(path)
    if run.get('template_compiler_sha256') and sha(ROOT / 'scripts/template_batch.py') != run['template_compiler_sha256']:
        raise ValueError('Template compiler changed: prepare a fresh run')
    for field in ('input', 'catalog'):
        if sha(run[field]) != run[field + '_sha256']:
            raise ValueError(f'Stale {field}: prepare a fresh run')
    if sha(ROOT / 'scripts/cards_pipeline.py') != run['compiler_sha256']:
        raise ValueError('Compiler changed: prepare a fresh run')
    for job in run['commands']:
        if sha(job['inputFile']) != job['script_sha256']:
            raise ValueError('Compiled script changed: prepare a fresh run')
    validate(read(run['input']), read(run['catalog']))
    return run


def record(run_path, operator, response):
    run = check_run(run_path)
    job = next(j for j in run['commands'] if j['operator'] == operator)
    if response.get('isError'):
        raise RuntimeError('Pencil failed; retain error and repair via editId/edits')
    text = '\n'.join(c.get('text', '') for c in response.get('content', []) if c.get('type') == 'text')
    evidence = []
    for line in text.splitlines():
        try:
            value = json.loads(line.strip())
        except ValueError:
            continue
        if isinstance(value, dict) and value.get('verification') == 'PASS':
            evidence.append(value)
    if len(evidence) != 1:
        raise ValueError('Missing unique native node-readback PASS; not a successful run')
    evidence = evidence[0]
    slots = evidence['slots']
    if [s['slot'] for s in slots] != list(range(1, 9)):
        raise ValueError('Readback must cover all eight editable instances')
    if [s['slot'] for s in slots if s['visible']] != job['visible_slots']:
        raise ValueError('Readback visibility mismatch')
    export = Path(job['outputDirectory']) / (evidence['frame'] + '.png')
    if not export.is_file() or str(export).replace('\\', '/') not in text.replace('\\', '/'):
        raise ValueError('Native export missing or not reported by Pencil')
    exported_ids = evidence.get('individual_exports')
    expected_ids = [s['id'] for s in slots if s['visible']]
    if exported_ids != expected_ids:
        raise ValueError('Native individual-card export list mismatch')
    players_dir = Path(job['outputDirectory']) / 'players'
    players_dir.mkdir(exist_ok=True)
    individual = []
    for slot in slots:
        if not slot['visible']:
            continue
        source = Path(job['outputDirectory']) / (slot['id'] + '.png')
        if not source.is_file():
            raise ValueError('Native individual-card PNG missing: ' + str(source))
        player = slot['player']
        named = players_dir / (player + '.png')
        shutil.copyfile(source, named)
        individual.append({'slot': slot['slot'], 'player': player, 'id': slot['id'], 'native_export': str(source),
                           'named_export': str(named),
                           'sha256': sha(source)})
    result = {**evidence, 'operator': operator, 'input_sha256': run['input_sha256'],
              'script_sha256': job['script_sha256'], 'export': str(export),
              'export_sha256': sha(export), 'individual_exports': individual, 'response_text': text}
    dump(Path(job['outputDirectory']) / 'receipt.json', result)
    return result


def verify(run_path):
    from PIL import Image  # Read-only image inspection. Never create/save/rasterize images.
    run = check_run(run_path)
    results = []
    for job in run['commands']:
        receipt = read(Path(job['outputDirectory']) / 'receipt.json')
        export = Path(receipt['export'])
        if receipt['script_sha256'] != job['script_sha256'] or receipt['input_sha256'] != run['input_sha256']:
            raise ValueError('Stale receipt')
        if receipt['export_sha256'] != sha(export):
            raise ValueError('Export changed after native verification')
        for card in receipt.get('individual_exports', []):
            named = Path(card['named_export'])
            native = Path(card['native_export'])
            if not named.is_file() or named.read_bytes() != native.read_bytes():
                raise ValueError('Named individual-card export changed or missing')
            with Image.open(named) as im:
                if im.mode != 'RGBA' or im.width <= 0 or im.height <= 0 or im.getchannel('A').getbbox() is None:
                    raise ValueError('Invalid individual-card PNG: ' + str(named))
        with Image.open(export) as im:
            checks = {'size': im.size == (1920, 1080), 'rgba': im.mode == 'RGBA'}
            if not all(checks.values()):
                raise ValueError(f'{job["operator"]}: wrong image dimensions/mode')
            alpha = im.getchannel('A')
            checks['transparent_center'] = alpha.crop((800, 0, 1100, 1080)).getbbox() is None
            checks['transparent_top'] = alpha.crop((0, 0, 1920, 60)).getbbox() is None
            checks['transparent_bottom'] = alpha.crop((0, 1050, 1920, 1080)).getbbox() is None
            checks['no_left_doctor'] = alpha.crop((0, 0, 130, 1080)).getbbox() is None
            checks['no_right_doctor'] = alpha.crop((1820, 0, 1920, 1080)).getbbox() is None
            for i, y in enumerate(YS, 1):
                x1, x2 = (150, 750) if i <= 4 else (1170, 1780)
                present = alpha.crop((x1, y - 3, x2, y + 193)).getbbox() is not None
                checks[f'slot_{i}_visibility'] = present == (i in job['visible_slots'])
        checks['individual_card_count'] = len(receipt.get('individual_exports', [])) == len(job['visible_slots'])
        results.append({'operator': job['operator'], 'checks': checks, 'sha256': sha(export),
                        'all_pass': all(checks.values())})
    passed = all(r['all_pass'] for r in results)
    if passed:
        for job in run['commands']:
            receipt = read(Path(job['outputDirectory']) / 'receipt.json')
            shutil.copyfile(receipt['export'], Path(job['outputDirectory']) / 'character_cards.png')
    report = {'layout': run['layout'], 'input_sha256': run['input_sha256'],
              'all_pass': passed, 'results': results,
              'scope': 'Native node readback and PNG alpha/size/provenance; saving/reopening and visual review are separate gates.'}
    dump(Path(run_path).parent / 'verification.json', report)
    run['status'] = 'native_exports_verified' if passed else 'verification_failed'
    dump(run_path, run)
    if not passed:
        raise ValueError('PNG verification failed; see verification.json')
    print(f'PASS: {len(results)} native PNGs; named character_cards.png in each operator directory')
    return report


async def execute_session(session, run_path):
    await session.initialize()
    names = {tool.name for tool in (await session.list_tools()).tools}
    def tool_name(short):
        options = [n for n in names if n == short or n.endswith('__' + short)]
        if len(options) != 1:
            raise RuntimeError('PENCIL_MCP_NOT_CONNECTED: missing/ambiguous ' + short)
        return options[0]
    async def call(short, args):
        result = await session.call_tool(tool_name(short), args)
        data = result.model_dump(mode='json', exclude_none=True)
        if data.get('isError'):
            raise RuntimeError('Pencil tool failed: ' + json.dumps(data, ensure_ascii=False))
        return data
    await call('read_skill', {})
    for path in ('pen-schema.md', 'execute.md', 'guide/components.md'):
        await call('read_skill', {'path': path})
    run = check_run(run_path)
    for job in run['commands']:
        state = await call('get_app_state', {})
        state_text = '\n'.join(c.get('text', '') for c in state.get('content', []))
        active = next((line for line in state_text.splitlines() if 'Currently active canvas editor:' in line), '')
        if Path(job['filePath']).as_posix().lower() not in active.replace('\\', '/').lower():
            raise RuntimeError('Open the target document in Pen.dev before running: ' + job['filePath'])
        response = await call('execute', {'filePath': job['filePath'],
                                        'input': Path(job['inputFile']).read_text(encoding='utf-8')})
        record(run_path, job['operator'], response)
        print('Exported and read back:', job['operator'], flush=True)
    verify(run_path)


async def run_connected(run_path, config_path):
    import tomllib
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    with Path(config_path).open('rb') as handle:
        config = tomllib.load(handle).get('mcp_servers', {}).get('pencil')
    if not config or config.get('enabled') is False:
        raise RuntimeError('PENCIL_MCP_NOT_CONNECTED: no enabled pencil server in configuration')
    if config.get('command'):
        params = StdioServerParameters(command=config['command'], args=config.get('args', []),
                                      env={**os.environ, **config.get('env', {})})
        async with stdio_client(params) as (reader, writer):
            async with ClientSession(reader, writer) as session:
                await execute_session(session, run_path)
    elif config.get('url'):
        import httpx
        from mcp.client.streamable_http import streamable_http_client
        headers = dict(config.get('http_headers', {}))
        for key, env in config.get('env_http_headers', {}).items():
            headers[key] = os.environ[env]
        if config.get('bearer_token_env_var'):
            headers['Authorization'] = 'Bearer ' + os.environ[config['bearer_token_env_var']]
        async with httpx.AsyncClient(headers=headers, timeout=180) as client:
            async with streamable_http_client(config['url'], http_client=client) as (reader, writer, _):
                async with ClientSession(reader, writer) as session:
                    await execute_session(session, run_path)
    else:
        raise RuntimeError('PENCIL_MCP_NOT_CONNECTED: unsupported transport configuration')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    for name in ('run', 'verify', 'record'):
        p = sub.add_parser(name)
        p.add_argument('manifest')
        if name == 'run':
            p.add_argument('--config', default=str(Path.home() / '.codex/config.toml'))
        if name == 'record':
            p.add_argument('--operator', required=True)
            p.add_argument('--response', required=True)
    args = parser.parse_args()
    if args.command == 'run':
        asyncio.run(run_connected(args.manifest, args.config))
    elif args.command == 'verify':
        verify(args.manifest)
    else:
        record(args.manifest, args.operator, read(args.response))


if __name__ == '__main__':
    main()
