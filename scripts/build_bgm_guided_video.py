from __future__ import annotations
import json, re, subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'generated/rhine/bgm_guided_v1'; W,H,FPS=1920,1080,24
BGM=ROOT/'bgm及使用指南/明日方舟报菜名（女神异闻录3  月行水上）.mp3'; FONT='C:/Windows/Fonts/msyh.ttc'
def ft(n): return ImageFont.truetype(FONT,n)
def main():
    normalized=json.loads((ROOT/'data/normalized/five_players.json').read_text(encoding='utf8'))
    by_name={}
    for pid in ['P1','P2','P3','P4','P5']:
        for oid,o in normalized['players'][pid]['operators'].items(): by_name.setdefault(o.get('name',''),(oid,o))
    raw=(ROOT/'bgm及使用指南/干员顺序.txt').read_text(encoding='utf8')
    order=re.findall(r'[^\s]+',raw.split('）',1)[1])
    durations={int(k):v for k,v in json.loads((ROOT/'archive/legacy_data/durations_24fps_perfect.json').read_text()).items()}
    names=order[:137]; assert len(names)==137
    ops=[]
    for i,name in enumerate(names,1):
        oid,meta=by_name.get(name,(None,{})); card=None
        if oid:
            for pid in ['P1','P2','P3','P4','P5']:
                p=ROOT/'data/raw'/pid/'operbox/cards_raw'/f'{oid}.png'
                if p.exists(): card=p; break
        ops.append({'index':i,'name':name,'operator_id':oid,'card':str(card) if card else None,'duration_frames':durations[i]})
    OUT.joinpath('frames').mkdir(parents=True,exist_ok=True)
    def draw(i):
        im=Image.new('RGB',(W,H),(8,18,28)); d=ImageDraw.Draw(im); d.rectangle((50,45,1870,1035),outline=(50,155,155),width=3)
        if i<durations[0]: d.text((620,430),'RHINE LAB',font=ft(110),fill=(220,245,235)); d.text((690,580),'BGM GUIDED ARCHIVE',font=ft(36),fill=(110,220,204)); return im
        x=i-durations[0]; acc=0
        for op in ops:
            if x<acc+op['duration_frames']: break
            acc+=op['duration_frames']
        d.text((90,78),f"BGM GUIDED // NO.{op['index']:03d}",font=ft(30),fill=(160,230,220)); d.text((90,125),f"FRAME {i:04d}  /  SEGMENT {op['duration_frames']}F",font=ft(22),fill=(105,185,180))
        # Use the same full-art + card composition language as the reference video.
        if op['operator_id']:
            art=ROOT/'assets/operators'/op['operator_id']/'full.png'
            if art.exists():
                bg=Image.open(art).convert('RGB'); bg.thumbnail((1500,1000)); im.paste(bg,((W-bg.width)//2,(H-bg.height)//2))
                overlay=Image.new('RGBA',(W,H),(5,22,35,135)); im=Image.alpha_composite(im.convert('RGBA'),overlay).convert('RGB'); d=ImageDraw.Draw(im)
        d.rounded_rectangle((360,140,770,940),radius=6,fill=(245,245,240),outline=(255,255,255),width=4)
        if op['card']:
            card=Image.open(op['card']).convert('RGB'); card.thumbnail((370,760)); im.paste(card,(380+(390-card.width)//2,170))
        d.text((820,430),op['name'],font=ft(100),fill=(255,255,255),stroke_width=5,stroke_fill=(20,75,210))
        d.text((830,570),'六星干员报菜名',font=ft(42),fill=(255,255,255),stroke_width=2,stroke_fill=(20,75,210))
        d.text((830,900),op['operator_id'] or 'ORDER ENTRY / CARD NOT FOUND',font=ft(24),fill=(180,230,225))
        return im
    total=sum(durations.values())
    for i in range(total): draw(i).save(OUT/'frames'/f'{i:06d}.png')
    mp4=OUT/'rhine_five_players_bgm_guided.mp4'
    subprocess.run(['ffmpeg','-y','-framerate','24','-i',str(OUT/'frames/%06d.png'),'-i',str(BGM),'-map','0:v:0','-map','1:a:0','-c:v','libx264','-pix_fmt','yuv420p','-r','24','-c:a','aac','-b:a','192k','-t','186.25',str(mp4)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    manifest={'version':1,'fps':24,'width':W,'height':H,'total_frames':total,'bgm':str(BGM),'bgm_duration_seconds':186.296,'order_source':'bgm及使用指南/干员顺序.txt','scenes':ops}
    (OUT/'operator_sequence.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf8')
    print(json.dumps({'operators':len(ops),'frames':total,'video':str(mp4)},ensure_ascii=False))
if __name__=='__main__': main()
