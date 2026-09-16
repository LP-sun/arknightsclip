"""Read native Pencil exports; do not create or render card artwork."""
from pathlib import Path
import hashlib
import json
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
export = ROOT / 'delivery' / 'qa' / 'Lwq9K.png'
im = Image.open(export).convert('RGBA')
alpha = im.getchannel('A')
checks = {
    'dimensions_1920x1080': im.size == (1920, 1080),
    'has_transparency': alpha.getextrema()[0] == 0,
    'has_visible_content': alpha.getextrema()[1] > 0,
    'central_operator_excluded': alpha.crop((800, 0, 1100, 1080)).getbbox() is None,
    'left_doctor_excluded': alpha.crop((0, 0, 130, 1080)).getbbox() is None,
    'right_doctor_excluded': alpha.crop((1820, 0, 1920, 1080)).getbbox() is None,
    'top_margin_transparent': alpha.crop((0, 0, 1920, 60)).getbbox() is None,
    'bottom_margin_transparent': alpha.crop((0, 1050, 1920, 1080)).getbbox() is None,
}
for side, x1, x2, tops in [('left', 157, 727, [187,401,615,829]),
                          ('right',1180,1764,[101,315,529,743])]:
    for index, top in enumerate(tops, 1):
        checks[f'{side}_{index}_visible'] = alpha.crop((x1,top,x2,top+184)).getbbox() is not None
reopened = ROOT / 'delivery' / 'reopened' / 'Lwq9K.png'
named = ROOT / 'delivery' / 'character_cards.png'
checks['reopened_export_exists'] = reopened.is_file()
checks['reopened_export_bytes_identical'] = reopened.is_file() and reopened.read_bytes() == export.read_bytes()
checks['named_delivery_bytes_identical'] = named.is_file() and named.read_bytes() == export.read_bytes()
files = [export, ROOT/'character_cards_8slot.pen',
         ROOT/'assets/psd_sources/source_manifest.json',
         ROOT/'reports/five_psd_template_audit.json']
files += sorted((ROOT/'delivery/qa').glob('*.png'))
files += [p for p in (reopened, named) if p.is_file()]
hashes = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
          for p in dict.fromkeys(files)}
result = {'scope':'PNG and file provenance only; not a visual gate or reopen proof',
          'checks':checks,'all_checks_pass':all(checks.values()),
          'alpha_bbox':alpha.getbbox(),'sha256':hashes}
out = ROOT/'delivery/png_verification.json'
out.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(result,ensure_ascii=False,indent=2))
raise SystemExit(0 if all(checks.values()) else 1)
