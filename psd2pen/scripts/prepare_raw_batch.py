"""Adapt five raw inventories; fetch original artwork bytes, never render cards."""
import argparse
import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import urllib.request
import urllib.error
import time
from PIL import Image
from cards_pipeline import ROOT, YS, read, dump, sha, validate

BASE = 'https://raw.githubusercontent.com/ArknightsAssets/ArknightsAssets2/cn/assets/dyn/arts/characters'
SLOTS = [1, 2, 3, 5, 6]


def prepare(raw_root, output):
    out = Path(output).resolve()
    out.mkdir(parents=True, exist_ok=False)
    players = {}
    names = {}
    sources = {}
    for index in range(1, 6):
        player = f'P{index}'
        source = Path(raw_root) / player / 'operators.json'
        rows = read(source)
        players[player] = {}
        sources[player] = {'path': str(source.resolve()), 'sha256': sha(source)}
        for row in rows:
            cid = row['char_id']
            if cid in players[player] or row.get('needs_review'):
                raise ValueError(f'Duplicate or review-required raw record: {player}/{cid}')
            if cid in names and names[cid] != row['name']:
                raise ValueError(f'Conflicting name: {cid}')
            players[player][cid] = row
            names[cid] = row['name']
    duplicate_names = {name for name in names.values()
                       if sum(other == name for other in names.values()) > 1}
    labels = {cid: (f'{name}__{cid}' if name in duplicate_names else name)
              for cid, name in names.items()}
    asset_dir = ROOT / 'assets/raw_batch'
    asset_dir.mkdir(exist_ok=True)
    def fetch(cid):
        url = f'{BASE}/{cid}/{cid}_1.png'
        dest = asset_dir / f'{cid}_1.png'
        if not dest.exists():
            for attempt in range(3):
                try:
                    with urllib.request.urlopen(url, timeout=40) as response:
                        content = response.read()
                    if not content.startswith(b'\x89PNG\r\n\x1a\n'):
                        raise ValueError('Not PNG')
                    dest.write_bytes(content)
                    break
                except urllib.error.HTTPError as error:
                    if error.code != 404:
                        if attempt == 2:
                            raise RuntimeError(f'{cid}: {error}') from error
                        time.sleep(1)
                        continue
                    portrait_url = f'https://raw.githubusercontent.com/ArknightsAssets/ArknightsAssets2/cn/assets/dyn/arts/charportraits/{cid}_1.png'
                    try:
                        url = portrait_url
                        with urllib.request.urlopen(portrait_url, timeout=40) as response:
                            content = response.read()
                        if not content.startswith(b'\\x89PNG\\r\\n\\x1a\\n'):
                            raise ValueError('portrait fallback is not PNG')
                        dest.write_bytes(content)
                        break
                    except Exception as fallback_error:
                        if attempt == 2:
                            raise RuntimeError(f'{cid}: no source artwork ({fallback_error})') from fallback_error
                        time.sleep(1)
                except Exception as error:
                    if attempt == 2:
                        raise RuntimeError(f'{cid}: {error}') from error
                    time.sleep(1)
        with Image.open(dest) as image:
            bbox = image.getchannel('A').getbbox()
            size = image.size
        return cid, {'url': dest.relative_to(ROOT).as_posix(), 'sha256': sha(dest),
                     'source_url': url, 'image_size': size, 'alpha_bbox': bbox}
    artwork_ids = sorted(cid for cid in names
                         if any(rows.get(cid, {}).get('own') for rows in players.values()))
    with ThreadPoolExecutor(max_workers=5) as pool:
        artwork = dict(pool.map(fetch, artwork_ids))
    data = {'version': 1, 'operators': []}
    catalog = {}
    missing = []
    for cid, display_name in sorted(names.items()):
        name = labels[cid]
        catalog[name] = {}
        slots = []
        for slot in range(1,9):
            player = f'P{SLOTS.index(slot)+1}' if slot in SLOTS else f'UNUSED_{slot}'
            row = players.get(player, {}).get(cid)
            owned = bool(row and row['own'])
            if row is None and slot in SLOTS:
                missing.append({'operator': name, 'player': player, 'action': 'NO_INFO'})
            slots.append({'slot': slot, 'player': player, 'owned': owned,
                          'elite': row['elite'] if owned else None,
                          'level': row['level'] if owned else None,
                          'potential': row['potential'] if owned else None,
                          'visible': slot in SLOTS})
            if owned:
                a = artwork[cid]
                left, top, right, bottom = a['alpha_bbox']
                width, height = a['image_size']
                scale = min(480 / (right-left), 650 / (bottom-top))
                dx = (584-(right-left)*scale)/2-left*scale
                dy = 10-top*scale
                x = 157 if slot <= 4 else 1180
                y = YS[slot-1]
                catalog[name][str(slot)] = {**a, 'background': '#929696', 'bbox': [x+dx,y+dy,x+dx+width*scale,y+dy+height*scale]}
        data['operators'].append({'name': name, 'display_name': display_name, 'char_id': cid, 'slots': slots})
    validate(data, catalog)
    dump(out/'input.json', data)
    dump(out/'catalog.json', catalog)
    dump(out/'provenance.json', {'raw': sources, 'missing_records': missing,
        'player_to_slot': dict(zip(players,SLOTS)), 'source_labels': sorted({r.get('source','unspecified') for p in players.values() for r in p.values()}),
        'artwork': artwork, 'output_labels': labels, 'duplicate_display_names': sorted(duplicate_names),
        'artwork_policy': 'Default base artwork, same art for all players; raw input has no skin field. Original bytes retained.'})
    print(f'Prepared {len(names)} operators, {len(missing)} NO_INFO slots: {out}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('raw_root')
    parser.add_argument('--out',required=True)
    args = parser.parse_args()
    prepare(args.raw_root,args.out)
