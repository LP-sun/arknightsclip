from __future__ import annotations
import json, subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'generated/rhine/simple_v1'; W,H,FPS=1920,1080,24
FONT='C:/Windows/Fonts/msyh.ttc'
def f(n): return ImageFont.truetype(FONT,n)
def main():
    data=json.loads((ROOT/'data/normalized/five_players.json').read_text(encoding='utf8'))
    ops={}
    for pid in ['P1','P2','P3','P4','P5']:
        for oid,o in data['players'][pid]['operators'].items():
            if int(o.get('rarity',0))==6: ops.setdefault(oid, {'id':oid,'name':o.get('name',oid),'players':{}})['players'][pid]=o
    seq=[]
    for oid in sorted(ops):
        item=ops[oid]; item['index']=len(seq)+1; item['start_frame']=48+len(seq)*24; item['duration_frames']=24
        item['card']=None
        for pid in ['P1','P2','P3','P4','P5']:
            p=ROOT/'data/raw'/pid/'operbox/cards_raw'/f'{oid}.png'
            if p.exists(): item['card']=str(p); break
        seq.append(item)
    OUT.joinpath('frames').mkdir(parents=True,exist_ok=True)
    def frame(i):
        im=Image.new('RGB',(W,H),(7,18,27)); d=ImageDraw.Draw(im)
        d.rectangle((50,45,1870,1035),outline=(48,150,151),width=3)
        if i<48:
            d.text((650,440),'RHINE LAB',font=f(110),fill=(220,245,235)); d.text((700,590),'FIVE PLAYER COLLECTION',font=f(34),fill=(112,220,204)); return im
        op=seq[(i-48)//24]; local=(i-48)%24
        d.text((85,75),f"RHINE LAB // OPERATOR {op['index']:03d}",font=f(30),fill=(155,230,220)); d.text((85,125),f"FRAME {i:04d}   HARD CUT / {local:02d}",font=f(22),fill=(100,180,180))
        d.rounded_rectangle((390,180,1530,950),radius=10,fill=(12,35,45),outline=(95,220,205),width=3)
        if op['card']:
            card=Image.open(op['card']).convert('RGB'); card.thumbnail((620,650)); im.paste(card,(650,220))
        d.text((470,820),op['name'],font=f(72),fill=(230,248,239)); d.text((470,900),op['id'],font=f(24),fill=(120,210,200))
        for n,pid in enumerate(['P1','P2','P3','P4','P5']):
            o=op['players'].get(pid,{}); txt=f"{pid}  {'OWNED' if o.get('own') else 'NO INFO'}  E{o.get('elite',0)} L{o.get('level',1)} P{o.get('potential',1)}"; d.text((90,240+n*48),txt,font=f(22),fill=(180,220,215))
        return im
    for i in range(48+24*len(seq)): frame(i).save(OUT/'frames'/f'{i:06d}.png')
    mp4=OUT/'rhine_five_players_simple.mp4'; subprocess.run(['ffmpeg','-y','-framerate','24','-i',str(OUT/'frames/%06d.png'),'-c:v','libx264','-pix_fmt','yuv420p','-r','24',str(mp4)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    manifest={'version':1,'fps':24,'width':W,'height':H,'intro':{'start_frame':0,'duration_frames':48},'scenes':seq,'total_frames':48+24*len(seq)}
    (OUT/'operator_sequence.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf8'); (OUT/'render_manifest.json').write_text(json.dumps({'video':str(mp4),'frame_count':manifest['total_frames'],'operator_count':len(seq)},ensure_ascii=False,indent=2),encoding='utf8')
    print(json.dumps({'operators':len(seq),'frames':manifest['total_frames'],'video':str(mp4)},ensure_ascii=False))
if __name__=='__main__': main()
