from PIL import Image, ImageDraw, ImageFont, ImageFilter
from pathlib import Path
import re, json
root=Path('.'); src=root/'generated/layered'; out=root/'generated/rhine/final_video_stills'; out.mkdir(parents=True,exist_ok=True)
fontp=root/'RhineLabUI_源码与Blender工程_2026-09-08/RhineLabUI/public/fonts/MiSans-Regular.woff2'
# PIL cannot use woff; use Windows CJK fallback
font_paths=[r'C:\Windows\Fonts\msyh.ttc',r'C:\Windows\Fonts\segoeui.ttf']
def font(size,bold=False):
 p=(r'C:\Windows\Fonts\msyhbd.ttc' if bold else r'C:\Windows\Fonts\msyh.ttc')
 try:return ImageFont.truetype(p,size)
 except:return ImageFont.load_default()
small=font(20); med=font(28); title=font(54,True); mono=font(18)
players=['P1  暮春之阳','P2  风笛','P3  银灰','P4  艾雅法拉','P5  塞雷娅']
folders=sorted(src.glob('*'),key=lambda p:int(re.match(r'(\d+)',p.name).group(1)) if re.match(r'(\d+)',p.name) else 999)
for i,d in enumerate(folders):
 im=Image.open(d/'full_composite.png').convert('RGB').resize((1920,1080),Image.Resampling.LANCZOS)
 # warm Rhine wash
 wash=Image.new('RGB',im.size,(234,229,225)); im=Image.blend(im,wash,0.20)
 dr=ImageDraw.Draw(im,'RGBA')
 # fine archive grid
 for x in range(80,1920,170): dr.line((x,120,x,940),fill=(95,105,100,35),width=1)
 for y in range(140,960,115): dr.line((70,y,1850,y),fill=(95,105,100,28),width=1)
 # header and footer panels
 dr.rectangle((52,38,1868,112),fill=(234,229,225,210),outline=(72,78,72,130),width=2)
 dr.text((82,57),'RHINE·LAB',font=title,fill=(27,29,25,255)); dr.text((420,68),'ANALYSIS OS  /  ARCHIVE ACCESS',font=med,fill=(53,61,55,230))
 dr.text((1550,68),f'RECORD {i+1:03d}  /  059',font=mono,fill=(53,61,55,230))
 # title plate
 label=d.name.split('_',1)[1] if '_' in d.name else d.name
 dr.rectangle((70,850,810,1010),fill=(234,229,225,218),outline=(198,139,63,220),width=3)
 dr.text((98,880),label,font=title,fill=(25,28,25,255)); dr.text((100,950),'ARCHIVE FILE  ·  CLEARANCE 06',font=small,fill=(115,93,65,255))
 # player status rail
 dr.rectangle((1100,850,1850,1010),fill=(38,45,40,205),outline=(210,155,76,230),width=2)
 dr.text((1130,870),'PLAYER INDEX / 5',font=small,fill=(242,237,227,255))
 for j,p in enumerate(players):
  y=900+j*20; dr.text((1130,y),p,font=font(16),fill=(242,237,227,255)); dr.text((1740,y),'SYNC',font=font(16),fill=(218,166,89,255))
 # amber scan line
 sx=90+(i%22)*75; dr.line((sx,125,sx,820),fill=(213,151,70,100),width=2)
 # corner metadata
 dr.text((82,122),'DATA STREAM // NORMALIZED FIVE-PLAYER DATA',font=small,fill=(59,69,62,210))
 im.save(out/f'{i:04d}.png',quality=95)
meta={'frames':len(folders),'fps':24,'duration_seconds':len(folders),'source':'generated/layered/full_composite.png','style':'RhineLabUI-inspired','players':players}
(root/'generated/rhine/final_video_manifest.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf-8')
print('generated',len(folders))
