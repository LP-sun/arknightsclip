const canvas=document.querySelector('#stage'),ctx=canvas.getContext('2d');
const W=1920,H=1080; let project=null, images=new Map(), frame=0;
const ease=t=>{t=Math.max(0,Math.min(1,t));return t*t*t*(t*(t*6-15)+10)};
function loadImage(url){if(!url)return Promise.resolve(null);if(images.has(url))return images.get(url);const p=new Promise(r=>{const im=new Image();im.onload=()=>r(im);im.onerror=()=>r(null);im.src=url});images.set(url,p);return p}
function line(x1,y1,x2,y2,a=.35,w=1){ctx.globalAlpha=a;ctx.lineWidth=w;ctx.beginPath();ctx.moveTo(x1,y1);ctx.lineTo(x2,y2);ctx.stroke();ctx.globalAlpha=1}
function corner(x,y,s=28){line(x,y,x+s,y);line(x,y,x,y+s);line(x+W-2*x,y,x+W-2*x-s,y);line(x+W-2*x,y,x+W-2*x,y+s);line(x,H-y,x+s,H-y);line(x,H-y,x,H-y-s);line(W-x,H-y,W-x-s,H-y);line(W-x,H-y,W-x,H-y-s)}
function frameChrome(active,progress){
 ctx.fillStyle='#e8e5e1';ctx.fillRect(0,0,W,H);ctx.strokeStyle='#26302d';corner(44,42,30);ctx.strokeStyle='#9b876b';ctx.lineWidth=2;ctx.strokeRect(46,44,W-92,H-88);
 ctx.strokeStyle='#26302d';ctx.lineWidth=1;line(72,128,1848,128,.55,1);line(72,954,1848,954,.55,1);
 ctx.fillStyle='#0d1211';ctx.font='300 40px MiSans, sans-serif';ctx.fillText('RHINE LAB',72,92);ctx.font='300 15px monospace';ctx.fillText('SYNTHESIZE INFORMATION  /  INTERNAL DATABASE',72,113);
 ctx.textAlign='right';ctx.fillText('ARCHIVE ACCESS  //  SESSION AUTHORIZED',1848,92);ctx.textAlign='left';
 ctx.fillStyle='#a67d48';ctx.fillRect(72,146,7,7);ctx.fillStyle='#26302d';ctx.font='300 16px monospace';ctx.fillText(`OPERATOR ARCHIVE  /  ${String(active+1).padStart(3,'0')}  /  ${String(project.operators.length).padStart(3,'0')}`,92,153);
 ctx.fillStyle='#26302d';ctx.font='300 14px monospace';ctx.fillText('ANALYSIS FIELD',72,986);ctx.textAlign='right';ctx.fillText(`FRAME ${String(frame).padStart(4,'0')}   ${String(Math.round(progress*100)).padStart(3,'0')}%`,1848,986);ctx.textAlign='left';
}
let active=0;
async function render(f){frame=f;if(!project){const r=await fetch('/project.json');project=await r.json();for(const o of project.operators){if(o.operatorId)loadImage(`/operators/${o.operatorId}/full.png`)}};
 let op=project.operators.find(o=>f>=o.startFrame&&f<o.endFrame)||project.operators.at(-1);active=project.operators.indexOf(op);const local=Math.max(0,f-op.startFrame),dur=op.durationFrames,prog=dur?local/dur:0;const intro=f<project.introFrames;
 ctx.clearRect(0,0,W,H);ctx.save();ctx.lineJoin='miter';
 if(intro){ctx.fillStyle='#e8e5e1';ctx.fillRect(0,0,W,H);const q=ease(f/project.introFrames);ctx.strokeStyle='#26302d';ctx.lineWidth=2;ctx.globalAlpha=q;ctx.beginPath();ctx.arc(1450,570,245*q,0,Math.PI*2);ctx.stroke();ctx.beginPath();ctx.arc(1450,570,190*q,0,Math.PI*2);ctx.stroke();ctx.fillStyle='#0d1211';ctx.font='300 84px MiSans';ctx.fillText('RHINE LAB',110,270);ctx.font='300 26px monospace';ctx.fillText('OPERATOR ARCHIVE / ACCESS PROTOCOL',114,322);ctx.fillStyle='#a67d48';ctx.fillRect(114,370,160*q,5);ctx.globalAlpha=1;ctx.fillStyle='#26302d';ctx.font='300 18px monospace';ctx.fillText('IDENTITY CONFIRMED : JOYCE MOORE',114,910);ctx.fillText('REQUEST RECEIVED  /  START PROCESSING...',114,944);ctx.restore();window.__RHINE_RENDER_READY__=true;return}
 frameChrome(active,prog);const entering=ease(Math.min(1,local/18)),leaving=ease(Math.max(0,(local-(dur-18))/18));
 // depth grid and measurement geometry
 ctx.strokeStyle='#60706b';for(let x=120;x<1850;x+=86)line(x,190,x,900,.10,1);for(let y=205;y<910;y+=58)line(90,y,1830,y,.10,1);
 ctx.strokeStyle='#a67d48';ctx.globalAlpha=.5;ctx.beginPath();ctx.arc(1435,522,310+Math.sin(frame*.08)*5,0,Math.PI*2);ctx.stroke();ctx.globalAlpha=1;
 const img=await loadImage(op.operatorId?`/operators/${op.operatorId}/full.png`:null);const cx=1060+Math.sin(frame*.008)*18, cy=535+Math.sin(frame*.013)*8;
 if(img){const maxW=920,maxH=790,s=Math.min(maxW/img.width,maxH/img.height)*entering;const iw=img.width*s,ih=img.height*s;ctx.save();ctx.globalAlpha=.93;ctx.filter='saturate(.72) contrast(1.04)';ctx.drawImage(img,cx-iw/2,cy-ih/2,iw,ih);ctx.restore()}
 // precision photo mask and side information columns
 ctx.strokeStyle='#26302d';ctx.lineWidth=2;ctx.strokeRect(735,176,650,700);ctx.strokeStyle='#a67d48';ctx.strokeRect(760,201,600,650);
 ctx.fillStyle='#0d1211';ctx.font='300 76px MiSans';ctx.fillText(op.name,92,790);ctx.font='300 18px monospace';ctx.fillStyle='#53625e';ctx.fillText(`${op.operatorId||'UNRESOLVED'}  /  PERSONNEL RECORD`,96,824);ctx.fillStyle='#a67d48';ctx.fillRect(96,848,Math.min(300,80+prog*220),4);
 ctx.fillStyle='#26302d';ctx.font='300 14px monospace';ctx.fillText('SUBJECT STATUS',1515,245);ctx.font='300 30px monospace';ctx.fillText('ARCHIVED',1515,282);ctx.font='300 14px monospace';ctx.fillText('CLEARANCE / GENERAL',1515,340);ctx.fillText('SERIAL / X-'+String(active+1).padStart(3,'0'),1515,368);ctx.fillText('FRAME / '+String(frame).padStart(4,'0'),1515,396);
 const cards=op.players||[];cards.slice(0,5).forEach((p,i)=>{const x=92+i*174,y=570,w=148,h=126;ctx.fillStyle='rgba(238,239,232,.74)';ctx.fillRect(x,y,w,h);ctx.strokeStyle='#60706b';ctx.strokeRect(x,y,w,h);ctx.fillStyle='#26302d';ctx.font='300 13px monospace';ctx.fillText(p.id||`P${i+1}`,x+12,y+24);ctx.font='300 20px monospace';ctx.fillText(p.owned?'OWNED':'NO DATA',x+12,y+58);ctx.font='300 12px monospace';ctx.fillText(`E${p.elite??0}  LV${p.level??'--'}  P${p.potential??'--'}`,x+12,y+90);ctx.fillStyle='#a67d48';ctx.fillRect(x+12,y+108,p.owned?92:24,3)});
 ctx.restore();window.__RHINE_RENDER_READY__=true}
window.renderFrame=render;window.__RHINE_RENDER_READY__=false;window.addEventListener('error',e=>window.__RHINE_RENDER_ERROR__=e.message);render(0);
