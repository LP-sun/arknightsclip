"""Compare all visible converted slots independently against immutable raw inputs."""
import argparse
from pathlib import Path
from cards_pipeline import read, sha, dump

def audit(source, run):
    source, run = Path(source), Path(run)
    provenance = read(source/'provenance.json')
    data = read(source/'input.json')
    verification = read(run/'verification.json')
    if not verification['all_pass']:
        raise ValueError('Native PNG verification did not pass')
    raw = {}
    for player, info in provenance['raw'].items():
        if sha(info['path']) != info['sha256']:
            raise ValueError('Raw data changed')
        raw[player] = {r['char_id']: r for r in read(info['path'])}
    count, owned, missing = 0, 0, 0
    for job in data['operators']:
        for player, slot in provenance['player_to_slot'].items():
            actual = next(s for s in job['slots'] if s['slot']==slot)
            expected = raw[player].get(job['char_id'])
            is_owned = bool(expected and expected['own'])
            assert actual['owned'] == is_owned
            assert actual['player'] == player and actual['visible']
            for key in ('elite','level','potential'):
                assert actual[key] == (expected[key] if is_owned else None), (player,job['name'],key)
            count += 1
            owned += is_owned
            missing += expected is None
    assert len(verification['results']) == len(data['operators'])
    result = {'all_pass':True, 'operators':len(data['operators']), 'visible_slots_checked':count,
        'owned_slots':owned, 'missing_records_no_info':missing, 'raw_unchanged':True,
        'input_sha256':sha(source/'input.json'), 'source_labels':provenance['source_labels'],
        'png_report_sha256':sha(run/'verification.json')}
    dump(run/'raw_data_audit.json',result)
    print(result)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('source'); p.add_argument('run')
    a=p.parse_args(); audit(a.source,a.run)
