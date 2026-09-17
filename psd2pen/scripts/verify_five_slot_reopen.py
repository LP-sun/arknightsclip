"""Compare independent native exports before/after user-confirmed save/reopen."""
from pathlib import Path
from cards_pipeline import ROOT, read, sha, dump


def main():
    run_path = ROOT / 'delivery/five_slot_run_001/run.json'
    run = read(run_path)
    reopened = ROOT / 'delivery/five_slot_reopened'
    comparisons = {}
    for job in run['commands']:
        receipt = read(Path(job['outputDirectory']) / 'receipt.json')
        original = Path(receipt['export'])
        second = reopened / original.name
        comparisons[job['operator']] = {
            'original_sha256': sha(original), 'reopened_sha256': sha(second),
            'identical': original.read_bytes() == second.read_bytes(),
        }
    baseline = sha(ROOT / 'character_cards_8slot.pen')
    result = {
        'save_reopen': 'User confirmed save, close, reopen; Pencil then read six frames and independently re-exported them.',
        'native_response_sha256': sha(reopened / 'mcp_response.json'),
        'baseline_8slot_unchanged': baseline == 'cba070fc871228e7adbfd605fd210b09ea3b0fd82db5b7349f478e42d261ea0c',
        'baseline_sha256': baseline,
        'five_slot_pen_sha256': sha(ROOT / 'character_cards_5slot.pen'),
        'comparisons': comparisons,
        'template_identical': (ROOT / 'delivery/five_slot_template/ja7Jk.png').read_bytes() == (reopened / 'ja7Jk.png').read_bytes(),
    }
    result['all_pass'] = (result['baseline_8slot_unchanged'] and result['template_identical']
                          and all(v['identical'] for v in comparisons.values()))
    dump(reopened / 'verification.json', result)
    print('PASS: save/reopen exports identical; 8slot unchanged' if result['all_pass'] else 'FAIL')
    raise SystemExit(0 if result['all_pass'] else 1)


if __name__ == '__main__':
    main()
