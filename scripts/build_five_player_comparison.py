from __future__ import annotations
import json
import re
import argparse
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

from arknightsclip.config import load_config
from arknightsclip.registry.operator_registry import OperatorRegistry

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'generated/rhine/five_player_comparison_v1'
W, H = 1920, 1080
FONT = 'C:/Windows/Fonts/msyh.ttc'

def ft(n):
    return ImageFont.truetype(FONT, n)

def build_manifest():
    reg = OperatorRegistry(ROOT / 'src/arknightsclip/registry/operator_registry.json')
    d = json.loads((ROOT / 'data/normalized/five_players.json').read_text(encoding='utf8'))
    names = re.findall(r'[^\s]+', (ROOT / 'bgm及使用指南/干员顺序.txt').read_text(encoding='utf8').split('）', 1)[1])[:137]
    durations = {int(k): v for k, v in json.loads((ROOT / 'archive/legacy_data/durations_24fps_perfect.json').read_text()).items()}

    ops = []
    for i, n in enumerate(names, 1):
        entry = reg.resolve(n)
        oid = entry.char_id if entry else None
        canonical_name = entry.canonical_name_zh if entry else n
        states = {}
        cards = {}
        for pid in ['P1', 'P2', 'P3', 'P4', 'P5']:
            o = d['players'][pid]['operators'].get(oid, {}) if oid else {}
            states[pid] = o
            p = ROOT / 'data/raw' / pid / 'operbox/cards_raw' / f'{oid}.png' if oid else None
            cards[pid] = str(p) if p and p.exists() else None
        ops.append({
            'index': i,
            'name': n,
            'canonical_name': canonical_name,
            'operator_id': oid,
            'states': states,
            'cards': cards,
            'duration_frames': durations[i]
        })

    total_frames = 50 + sum(durations[i] for i in range(1, 138))
    manifest = {
        'fps': 24,
        'width': W,
        'height': H,
        'total_frames': total_frames,
        'intro_frames': 50,
        'operators': ops
    }
    OUT.mkdir(parents=True, exist_ok=True)
    manifest_path = OUT / 'comparison_manifest.json'
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf8')
    print(f"[Manifest] comparison_manifest.json 已成功生成并更新: {manifest_path}")
    return ops, total_frames, durations

def render_video(ops, total_frames):
    scenes_dir = OUT / 'scenes'
    scenes_dir.mkdir(parents=True, exist_ok=True)

    def draw_scene(op=None):
        im = Image.new('RGB', (W, H), (8, 18, 28))
        d0 = ImageDraw.Draw(im)
        d0.rectangle((42, 38, 1878, 1042), outline=(55, 160, 160), width=3)
        if op is None:
            d0.text((610, 430), 'RHINE LAB', font=ft(110), fill=(220, 245, 235))
            d0.text((610, 585), 'FIVE PLAYER COMPARISON', font=ft(38), fill=(110, 220, 204))
            return im

        if op['operator_id']:
            art = ROOT / 'assets/operators' / op['operator_id'] / 'full.png'
            if art.exists():
                bg = Image.open(art).convert('RGB')
                bg.thumbnail((1800, 950))
                im.paste(bg, ((W - bg.width) // 2, (H - bg.height) // 2))
                im = Image.blend(im, Image.new('RGB', (W, H), (5, 22, 35)), 0.48)

        d0 = ImageDraw.Draw(im)
        d0.text((75, 62), f"FIVE PLAYER ARCHIVE  //  NO.{op['index']:03d}  {op['name']}", font=ft(30), fill=(225, 245, 235), stroke_width=2, stroke_fill=(10, 50, 80))
        d0.text((80, 105), f"{op['duration_frames']}F SEGMENT   HARD CUT", font=ft(21), fill=(120, 210, 200))

        for j, pid in enumerate(['P1', 'P2', 'P3', 'P4', 'P5']):
            x0 = 70 + j * 370
            y0 = 610
            d0.rounded_rectangle((x0, y0, x0 + 340, 1015), radius=5, fill=(238, 239, 232), outline=(255, 255, 255), width=3)
            if op['cards'][pid]:
                c = Image.open(op['cards'][pid]).convert('RGB')
                c.thumbnail((190, 300))
                im.paste(c, (x0 + 75, y0 + 15))
            o = op['states'][pid]
            status = 'OWNED' if o.get('own') else 'NOT OWNED'
            d0.text((x0 + 16, 930), f'{pid}  {status}', font=ft(22), fill=(25, 65, 75))
            d0.text((x0 + 16, 965), f"E{o.get('elite', 0)}  LV{o.get('level', 1)}  POT{o.get('potential', 1)}", font=ft(19), fill=(45, 100, 105))

        return im

    print(f"[Render] 生成 {len(ops)+1} 张场景图，再按精确帧长拼接...")
    intro = scenes_dir / 'scene_000_intro.png'; draw_scene().save(intro)
    concat = OUT / 'concat.txt'
    lines = [f"file '{intro.as_posix()}'", f"duration {50/24:.9f}"]
    for op in ops:
        p = scenes_dir / f"scene_{op['index']:03d}.png"
        draw_scene(op).save(p)
        lines += [f"file '{p.as_posix()}'", f"duration {op['duration_frames']/24:.9f}"]
    # concat demuxer needs the final file repeated to retain its duration.
    last_scene = scenes_dir / f"scene_{ops[-1]['index']:03d}.png"
    lines.append(f"file '{last_scene.as_posix()}'")
    concat.write_text('\n'.join(lines), encoding='utf8')

    mp4 = OUT / 'rhine_five_player_comparison.mp4'
    bgm = ROOT / 'bgm及使用指南/明日方舟报菜名（女神异闻录3  月行水上）.mp3'
    cmd = [
        'ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i', str(concat),
        '-i', str(bgm), '-map', '0:v', '-map', '1:a',
        '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-r', '24', '-c:a', 'aac',
        '-t', '186.25', str(mp4)
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"[Video] 视频合成完成: {mp4}")

def main():
    parser = argparse.ArgumentParser(description="构建五人对比视频与场景清单")
    parser.add_argument("--manifest-only", action="store_true", help="仅更新 comparison_manifest.json，不重新渲染视频帧")
    args = parser.parse_args()

    ops, total_frames, durations = build_manifest()
    if not args.manifest_only:
        render_video(ops, total_frames)

if __name__ == '__main__':
    main()
