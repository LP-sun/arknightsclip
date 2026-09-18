"""Probe, decode, and extract evidence from a completed production export."""
from pathlib import Path
import argparse
import json
import subprocess

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('video', type=Path)
parser.add_argument('--output', type=Path, default=ROOT / 'reports/rhinelab_reference/delivery')
args = parser.parse_args()
args.output.mkdir(parents=True, exist_ok=True)
probe = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', str(args.video)], encoding='utf-8'))
video = next(s for s in probe['streams'] if s['codec_type'] == 'video')
audio = next(s for s in probe['streams'] if s['codec_type'] == 'audio')
assert (video['width'], video['height']) == (1920, 1080)
assert video['r_frame_rate'] == '24/1'
assert video['codec_name'] == 'h264' and audio['codec_name'] == 'aac'
decoded = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(args.video), '-f', 'null', '-'], capture_output=True, text=True)
assert decoded.returncode == 0 and not decoded.stderr.strip(), decoded.stderr
black = subprocess.run(['ffmpeg', '-hide_banner', '-i', str(args.video), '-vf', 'blackdetect=d=0.1:pix_th=0.06', '-an', '-f', 'null', '-'], capture_output=True, text=True)
black_events = [s.strip() for s in black.stderr.splitlines() if 'black_start:' in s]
duration = float(probe['format']['duration'])
times = [0.8, 2.9, 25, 64, 100, 141, 175, max(0, duration - 0.5)]
for index, time in enumerate(times):
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(time), '-i', str(args.video), '-frames:v', '1', str(args.output / f'shot_{index:02d}.png')], check=True)
from PIL import Image, ImageDraw, ImageFont
sheet = Image.new('RGB', (1920, 4 * 580), '#e8e5e1')
draw = ImageDraw.Draw(sheet)
font = ImageFont.truetype('C:/Windows/Fonts/arial.ttf', 24)
for index, time in enumerate(times):
    with Image.open(args.output / f'shot_{index:02d}.png') as im:
        im.thumbnail((960, 540))
        x, y = (index % 2) * 960, (index // 2) * 580
        sheet.paste(im, (x, y))
        draw.text((x + 14, y + 548), f'{index+1:02} / {time:.2f}s', fill='#171a17', font=font)
sheet.save(args.output / 'contact_sheet.jpg', quality=95)
report = {'file': str(args.video.resolve()), 'duration': duration, 'width': video['width'], 'height': video['height'], 'fps': video['r_frame_rate'], 'frames': video.get('nb_frames'), 'video_codec': video['codec_name'], 'audio_codec': audio['codec_name'], 'audio_channels': audio.get('channels'), 'audio_sample_rate': audio.get('sample_rate'), 'full_decode': 'passed', 'black_events': black_events, 'sample_times': times, 'visual_review': 'pending human/model inspection of extracted frames'}
(args.output / 'ffprobe.json').write_text(json.dumps(probe, ensure_ascii=False, indent=2), encoding='utf-8')
(args.output / 'qa.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(report, ensure_ascii=False, indent=2))
