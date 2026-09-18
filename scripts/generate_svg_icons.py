import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
out_dir = ROOT / "assets/icons/svg"
out_dir.mkdir(parents=True, exist_ok=True)

# 1. Potential 1..6
for pot in range(1, 7):
    svg_lines = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" width="100" height="100">',
        f'  <!-- Potential Level {pot} -->',
        '  <polygon points="50,22 78,50 50,78 22,50" fill="#1a3644" stroke="#319795" stroke-width="3" />',
        '  <polygon points="50,32 68,50 50,68 32,50" fill="#285e61" />',
    ]
    for i in range(6):
        angle = math.radians(i * 60 - 90)
        nx = 50 + 38 * math.cos(angle)
        ny = 50 + 38 * math.sin(angle)
        active = (i < pot)
        fill_c = "#4fd1c5" if active else "#1a202c"
        stroke_c = "#e6fffa" if active else "#4a5568"
        r = 6 if active else 4.5
        svg_lines.append(f'  <circle cx="{nx:.1f}" cy="{ny:.1f}" r="{r}" fill="{fill_c}" stroke="{stroke_c}" stroke-width="1.5" />')
    svg_lines.append(f'  <text x="50" y="56" font-family="monospace" font-size="20" font-weight="bold" fill="#e6fffa" text-anchor="middle">{pot}</text>')
    svg_lines.append('</svg>')
    (out_dir / f"potential_{pot}.svg").write_text("\n".join(svg_lines), encoding="utf-8")

# 2. Professions
professions = {
    "pioneer": (
        '<polygon points="30,20 70,20 85,45 50,85 15,45" fill="#234e52" stroke="#4fd1c5" stroke-width="3" />\n'
        '  <polyline points="35,42 50,28 65,42" fill="none" stroke="#e6fffa" stroke-width="4" stroke-linecap="round" />\n'
        '  <polyline points="35,62 50,48 65,62" fill="none" stroke="#e6fffa" stroke-width="4" stroke-linecap="round" />'
    ),
    "warrior": (
        '<polygon points="50,12 80,40 70,88 30,88 20,40" fill="#234e52" stroke="#4fd1c5" stroke-width="3" />\n'
        '  <line x1="50" y1="22" x2="50" y2="78" stroke="#e6fffa" stroke-width="5" stroke-linecap="round" />\n'
        '  <line x1="32" y1="36" x2="68" y2="36" stroke="#e6fffa" stroke-width="4" stroke-linecap="round" />'
    ),
    "sniper": (
        '<circle cx="50" cy="50" r="38" fill="#143644" stroke="#4fd1c5" stroke-width="3" />\n'
        '  <circle cx="50" cy="50" r="22" fill="none" stroke="#81e6d9" stroke-width="2" />\n'
        '  <line x1="50" y1="8" x2="50" y2="92" stroke="#e6fffa" stroke-width="3" />\n'
        '  <line x1="8" y1="50" x2="92" y2="50" stroke="#e6fffa" stroke-width="3" />\n'
        '  <circle cx="50" cy="50" r="4" fill="#ffffff" />'
    ),
    "tank": (
        '<path d="M50,12 L84,24 L80,64 L50,88 L20,64 L16,24 Z" fill="#234e52" stroke="#4fd1c5" stroke-width="3" />\n'
        '  <path d="M50,24 L72,34 L68,60 L50,76 L32,60 L28,34 Z" fill="#285e61" stroke="#81e6d9" stroke-width="2" />\n'
        '  <rect x="46" y="38" width="8" height="24" fill="#e6fffa" />'
    ),
    "medic": (
        '<circle cx="50" cy="50" r="38" fill="#1a3644" stroke="#4fd1c5" stroke-width="3" />\n'
        '  <rect x="42" y="24" width="16" height="52" fill="#e6fffa" rx="2" />\n'
        '  <rect x="24" y="42" width="52" height="16" fill="#e6fffa" rx="2" />'
    ),
    "support": (
        '<polygon points="50,14 82,32 82,68 50,86 18,68 18,32" fill="#234e52" stroke="#4fd1c5" stroke-width="3" />\n'
        '  <polygon points="50,28 70,40 70,60 50,72 30,60 30,40" fill="#285e61" stroke="#81e6d9" stroke-width="2" />\n'
        '  <circle cx="50" cy="50" r="6" fill="#e6fffa" />'
    ),
    "caster": (
        '<polygon points="50,10 82,50 50,90 18,50" fill="#1a3644" stroke="#4fd1c5" stroke-width="3" />\n'
        '  <polygon points="50,24 72,50 50,76 28,50" fill="#285e61" stroke="#81e6d9" stroke-width="2" />\n'
        '  <polygon points="50,36 62,50 50,64 38,50" fill="#e6fffa" />'
    ),
    "special": (
        '<polygon points="50,14 84,34 76,82 50,88 24,82 16,34" fill="#234e52" stroke="#4fd1c5" stroke-width="3" />\n'
        '  <path d="M50,24 L68,44 L50,56 L32,44 Z" fill="#81e6d9" />\n'
        '  <polyline points="28,66 50,78 72,66" fill="none" stroke="#e6fffa" stroke-width="3" stroke-linecap="round" />'
    ),
}

for p_name, body in professions.items():
    content = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" width="100" height="100">\n  <!-- Profession: {p_name.upper()} -->\n  {body}\n</svg>'
    (out_dir / f"profession_{p_name}.svg").write_text(content, encoding="utf-8")

print(f"Generated {len(professions)} profession SVGs and 6 potential SVGs into {out_dir}")
