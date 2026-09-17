"""Render a self-contained Rhine Lab Golden Sample preview.

GOLDEN_SAMPLE_TEMPORARY_ADAPTER: this intentionally composes a focused eight-
operator cut from the normalized manifests while the WIP web renderer remains
under development. It never edits source data or .pen files.
"""
from __future__ import annotations
import json, math, subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "generated/rhine/golden_sample"
FPS, W, H = 24, 1920, 1080
OPS = [
    ("char_017_huang", "煌", "001_能天使"), ("char_112_siege", "推进之王", "002_推王"),
    ("char_134_ifrit", "伊芙利特", "003_小火龙"), ("char_180_amgoat", "艾雅法拉", "004_小羊"),
    ("char_003_kalts", "凯尔希", "005_洁哥"), ("char_010_chen", "陈", None),
    ("char_103_angel", "能天使", "001_能天使"), ("char_350_surtr", "史尔特尔", None),
]

def font(size, mono=False):
    paths = ["C:/Windows/Fonts/msyh.ttc", "C:/Windows/Fonts/seguisym.ttf", "C:/Windows/Fonts/consola.ttf"]
    return ImageFont.truetype(next(p for p in paths if Path(p).exists()), size)

F_BIG, F_MED, F_SMALL = font(92), font(30, True), font(22, True)

def fit_art(path: Path, box=(760, 180, 1180, 900)):
    if not path.exists(): return None
    im = Image.open(path).convert("RGBA"); im.thumbnail((box[2]-box[0], box[3]-box[1]))
    return im

def draw_frame(i: int, scenes):
    t, op_i = i / FPS, min(len(scenes)-1, max(0, int((i-36) / 27)))
    intro = i < 36; outro = i >= 36 + len(scenes)*27
    op = scenes[op_i] if not intro and not outro else scenes[0]
    local = 0 if intro else (i - 36 - op_i*27) / 27
    ease = 1 - (1-local)**3 if 0 <= local <= 1 else 1
    im = Image.new("RGBA", (W,H), (7,17,24,255)); d = ImageDraw.Draw(im)
    # archive world: depth planes, grid and restrained cyan scan glow
    for z in range(7):
        x = int(70 + z*54 - (t*38) % 54); y = 150 + z*105
        d.rectangle((x,y,W-80,y+1), fill=(37,94,105,100))
        d.line((x,y,x+270,y+150), fill=(38,99,111,90), width=1)
    for x in range(-100, W+200, 170): d.line((x,120,x+230,980), fill=(30,84,98,65), width=1)
    d.rectangle((54,46,1866,1018), outline=(61,154,160,150), width=2)
    d.text((84,70), "RHINE LAB  //  ARCHIVE ACCESS", font=F_MED, fill=(177,236,231,255))
    d.text((84,108), "RHI-07 / OPERATOR INDEX  •  LIVE SPECIMEN RETRIEVAL", font=F_SMALL, fill=(89,164,172,230))
    d.text((1510,72), f"FRAME {i:04d}  /  {int(t*100):02d}%", font=F_SMALL, fill=(125,205,204,220))
    # side archive cards (preceding/following operators create depth)
    for j, idx in enumerate((op_i-1, op_i+1)):
        if 0 <= idx < len(scenes):
            xx = 120 if j == 0 else 1510; yy = 300 + (j*90)
            d.rectangle((xx,yy,xx+245,yy+330), fill=(12,30,38,210), outline=(47,112,119,170), width=2)
            d.text((xx+18,yy+22), scenes[idx]["name"], font=font(30), fill=(175,215,210,220))
            d.text((xx+18,yy+280), f"0{idx+1:02d}  ARCHIVE", font=F_SMALL, fill=(79,169,171,220))
    # central specimen card with animated focus/slide
    shift = int((1-ease)*220) if not intro and not outro else 0
    d.rounded_rectangle((470+shift,150,1450+shift,948), radius=8, fill=(13,30,38,230), outline=(101,216,205,230), width=3)
    d.rectangle((500+shift,178,1420+shift,208), fill=(28,75,82,230))
    d.text((530+shift,181), f"SPECIMEN // {op['id'].upper()}", font=F_SMALL, fill=(181,238,224,255))
    art = fit_art(ROOT / "assets/operators" / op["id"] / "full.png")
    if art: im.alpha_composite(art, (790+shift,220))
    d.text((535+shift,690), op["name"], font=F_BIG, fill=(232,247,238,255))
    d.text((540+shift,800), f"{op['profession']}   RARITY {op['rarity']}   LEVEL {op['level']}", font=F_MED, fill=(129,219,207,255))
    d.text((540+shift,842), f"OWNER  P1 / {op['status']}     POTENTIAL {op['potential']}", font=F_SMALL, fill=(167,193,192,235))
    # accepted psd2pen Box visual integrated as an information layer
    if op.get('box'):
        box = Image.open(op['box']).convert('RGBA'); box.thumbnail((430,190))
        im.alpha_composite(box, (970+shift,710))
        d.text((970+shift,905), "PSd2Pen // FIVE-PLAYER BOX", font=F_SMALL, fill=(127,229,214,240))
    # scan pulse and transition accent
    scan_y = int(170 + ((i*11) % 760)); d.rectangle((500,scan_y,1420,scan_y+3), fill=(105,245,226,120))
    d.text((84,978), "ARCHIVE LOCK  ·  RHINE LAB VISUALIZATION SYSTEM", font=F_SMALL, fill=(90,168,170,220))
    if intro:
        d.rectangle((0,0,W,H), fill=(7,17,24, max(0, 210-i*6)))
        d.text((650,470), "RHINE LAB", font=font(118), fill=(215,245,232,245))
        d.text((748,610), "ARCHIVE INITIALIZATION", font=F_MED, fill=(103,206,196,240))
    if outro:
        d.rectangle((0,0,W,H), fill=(7,17,24, min(220,(i-(36+len(scenes)*27))*8)))
        d.text((650,500), "ARCHIVE LOCKED", font=font(76), fill=(215,245,232,245))
    return im.convert("RGB")

def main():
    OUT.joinpath("frames").mkdir(parents=True, exist_ok=True)
    OUT.joinpath("representative_frames").mkdir(parents=True, exist_ok=True)
    scenes=[]
    for cid, name, boxdir in OPS:
        m=json.loads((ROOT/"data/manifests"/(cid+".json")).read_text(encoding="utf-8"))
        p1=m["players"]["P1"]; box=(ROOT/"psd2pen"/boxdir/"character_cards.png") if boxdir else None
        scenes.append({"id":cid,"name":name,"profession":m.get("profession","OPERATOR"),"rarity":m.get("rarity",6),"level":p1.get("level",1),"potential":p1.get("potential",1),"status":"OWNED" if p1.get("own") else "NO INFO","box":box if box and box.exists() else None})
    total=36+len(scenes)*27+36
    reps={0,"36","108","180","288","%d"%(total-1)}
    for i in range(total):
        frame=draw_frame(i,scenes); path=OUT/"frames"/f"{i:06d}.png"; frame.save(path)
        if i in {0,36,60,108,180,240,total-1}: frame.save(OUT/"representative_frames"/f"frame_{i:04d}.png")
    mp4=OUT/"golden_sample.mp4"
    subprocess.run(["ffmpeg","-y","-framerate","24","-i",str(OUT/"frames"/"%06d.png"),"-c:v","libx264","-pix_fmt","yuv420p","-movflags","+faststart",str(mp4)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    report={"status":"golden_sample_rendered","duration_seconds":round(total/FPS,3),"width":W,"height":H,"fps":FPS,"scene_count":len(scenes),"selected_operators":[s["name"] for s in scenes],"box_integrated":sum(bool(s["box"]) for s in scenes),"audio_source":None,"temporary_adapter":"GOLDEN_SAMPLE_TEMPORARY_ADAPTER"}
    (OUT/"render_report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps(report,ensure_ascii=False))
if __name__=="__main__": main()
