"""Compile data-only jobs for the reusable v2 Pencil canvas (no new frames)."""
import argparse
import json
from pathlib import Path
from cards_pipeline import ROOT, LEFT, RIGHT, LAYOUTS, read, sha, dump, validate, node

ROLES = ['operator_image','no_info_panel','no_info_text','level_value',
         'level_visible','elite_icon','potential_visible','potential_icon','elite_visible']


def safe_name(value):
    if not isinstance(value, str) or not value or any(c in value for c in '<>:"/\\|?*') or value.endswith((' ', '.')) or value in ('.', '..'):
        raise ValueError('Unsafe output name: ' + repr(value))
    return value


def payload(job, catalog, layout):
    result = []
    for s in sorted(job['slots'], key=lambda s: s['slot']):
        ids = LEFT if s['slot'] <= 4 else RIGHT
        legacy = node(job, s, catalog)['descendants']
        fields = {ROLES[ids.index(k)]: v for k, v in legacy.items()
                  if k not in (ids[5], ids[7])}
        visibility = s.get('visibility', {})
        if not isinstance(visibility, dict) or set(visibility) - {'level','elite','potential'} or any(type(v) is not bool for v in visibility.values()):
            raise ValueError('visibility only accepts boolean level/elite/potential')
        for role in ('level','elite','potential'):
            fields[role+'_visible'] = {'enabled': visibility.get(role, s['owned'])}
        fields.setdefault('level_value', {'content': '1'})
        for e in range(3):
            fields['elite_'+str(e)] = {'enabled': s['elite'] == e}
        for p in range(1, 7):
            fields['potential_'+str(p)] = {'enabled': s['potential'] == p}
        result.append({'slot':s['slot'], 'player':safe_name(s['player']),
                       'visible':s.get('visible', True) and s['slot'] in LAYOUTS[layout]['slots'],
                       'fields':fields})
    players = [s['player'].casefold() for s in result if s['visible']]
    if len(players) != len(set(players)):
        raise ValueError('Visible player export filenames must be unique')
    return result


def script(slots, export):
    return 'const data='+json.dumps(slots, ensure_ascii=False)+';\nconst output='+json.dumps(export)+';\n'+r'''
const canvases=Get((n,c)=>c.depth===0&&n.name==='EXPORT_CHARACTER_CARDS'?n.id:undefined);
if(canvases.length!==1)throw new Error('Template v2: unique export canvas required');
const frame=canvases[0],canvas=Get(frame,{depth:1});
if(GetVariables().variables.template_version?.value!==2||canvas.width!==1920||canvas.height!==1080||canvas.children.length!==8)throw new Error('Template canvas schema mismatch');
const maps={};
for(const direction of ['LEFT','RIGHT']){
 const matches=Get((n,c)=>c.depth===0&&n.name==='CHARACTER_CARD_'+direction?n.id:undefined);
 if(matches.length!==1)throw new Error('Missing component '+direction);
 const component=Get(matches[0],{depth:0});
 if(!component.reusable)throw new Error('Wrong component version');
 const aliases={OPERATOR_IMAGE:'operator_image',NO_INFO_PANEL:'no_info_panel',NO_INFO_TEXT:'no_info_text',LEVEL_NUMBER:'level_value',LEVEL_BADGE:'level_visible',ELITE_BADGE:'elite_visible',POTENTIAL_BADGE:'potential_visible'};
 const entries=Get(matches[0],n=>aliases[n.name]||/^(ELITE_[012]|POTENTIAL_[1-6])$/.test(n.name)?{id:n.id,role:aliases[n.name]||n.name.toLowerCase(),type:n.type}:undefined);
 const roles={};for(const e of entries){if(roles[e.role])throw new Error('Duplicate role '+e.role);roles[e.role]=e;}
 maps[direction]={id:matches[0],roles};
}
const evidence=[],vars={};
for(const slot of data){
 const direction=slot.slot<=4?'LEFT':'RIGHT',map=maps[direction];
 const matches=canvas.children.filter(n=>n.name==='SLOT_'+String(slot.slot).padStart(2,'0'));
 if(matches.length!==1)throw new Error('Missing slot');
 const s=matches[0],ys=[187,401,615,829,101,315,529,743];
 if(s.type!=='ref'||s.ref!==map.id||s.x!==(direction==='LEFT'?157:1180)||s.y!==ys[slot.slot-1])throw new Error('Slot structure mismatch');
 for(const [role,props] of Object.entries(slot.fields)){
  if(!map.roles[role])throw new Error('Missing field '+role);
  const n=Get(s.id+'/'+map.roles[role].id,{depth:0,resolveInstances:true});
  if(role==='level_value'&&n.type!=='text')throw new Error('Wrong level type');
  if(role==='operator_image'&&n.type!=='path')throw new Error('Wrong image type');
 }
 evidence.push({slot:slot.slot,id:s.id,player:slot.player,visible:slot.visible});
}
Update(frame,{placeholder:true});
for(let i=0;i<data.length;i++){
 const slot=data[i],s=evidence[i],map=maps[slot.slot<=4?'LEFT':'RIGHT'];
 const prefix='slot'+String(slot.slot).padStart(2,'0')+'.';
 const controls={operator_image:'owned',no_info_panel:'no_info',no_info_text:'no_info',level_visible:'level_visible',elite_visible:'elite_visible',potential_visible:'potential_visible'};
 vars[prefix+'visible']={type:'boolean',value:slot.visible};
 for(const [role,props] of Object.entries(slot.fields))if(controls[role])vars[prefix+controls[role]]={type:'boolean',value:props.enabled};
 SetVariables(vars);
 Update(s.id,{enabled:'$'+prefix+'visible'});
 for(const [role,props] of Object.entries(slot.fields))Update(s.id+'/'+map.roles[role].id,{...props,...(controls[role]?{enabled:'$'+prefix+controls[role]}:{})});
}
function same(a,b){if(b&&typeof b==='object')return a!=null&&Object.entries(b).every(([k,v])=>same(a[k],v));return typeof b==='number'?Math.abs(a-b)<0.0001:a===b;}
for(let i=0;i<data.length;i++){
 const slot=data[i],s=evidence[i],map=maps[slot.slot<=4?'LEFT':'RIGHT'];
 if((Get(s.id,{depth:0,resolveVariables:true}).enabled!==false)!==slot.visible)throw new Error('Visibility readback failed');
 for(const [role,props] of Object.entries(slot.fields)){
  const n=Get(s.id+'/'+map.roles[role].id,{depth:0,resolveInstances:true,resolveVariables:true,includePathGeometry:true});
  if('geometry' in props)n.geometry=Get(s.id,{depth:0,includePathGeometry:true}).descendants[map.roles[role].id].geometry;
  for(const [k,v] of Object.entries(props))if(k==='enabled'?(n[k]!==false)!==v:!same(n[k],v))throw new Error('Field readback failed '+s.slot+'/'+role+'/'+k);
 }
}
Update(frame,{placeholder:false});
Print({verification:'PASS',frame,slots:evidence,individual_exports:evidence.filter(s=>s.visible).map(s=>s.id)});
TakeScreenshot([frame]);Export([frame],'png',output,{scale:1});
for(const s of evidence)if(s.visible)Export([s.id],'png',output,{scale:1});
'''


def prepare(input_path, catalog_path, out, layout='3l2r'):
    catalog=read(catalog_path);data=validate(read(input_path),catalog)
    compiled=[];seen=set()
    for job in data['operators']:
        name=safe_name(job['name'])
        if name.casefold() in seen:raise ValueError('Case-insensitive filename collision')
        seen.add(name.casefold())
        compiled.append((name,payload(job,catalog,layout)))
    out=Path(out).resolve();out.mkdir(parents=True,exist_ok=False)
    commands=[]
    for name,slots in compiled:
        export=(out/name).as_posix();p=out/(name+'.pencil.js')
        p.write_text(script(slots,export),encoding='utf-8')
        commands.append({'operator':name,'filePath':str(ROOT/'character_cards_5slot_template.pen'),
                         'inputFile':str(p),'script_sha256':sha(p),'outputDirectory':export,
                         'frameName':'EXPORT_CHARACTER_CARDS','visible_slots':[s['slot'] for s in slots if s['visible']]})
    dump(out/'run.json',{'input':str(Path(input_path).resolve()),'input_sha256':sha(input_path),
         'catalog':str(Path(catalog_path).resolve()),'catalog_sha256':sha(catalog_path),
         'compiler_sha256':sha(ROOT/'scripts/cards_pipeline.py'),
         'template_compiler_sha256':sha(__file__),'layout':layout,
         'status':'prepared_not_rendered','commands':commands})
    print(f'Prepared {len(commands)} fixed-canvas jobs: {out}/run.json')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('input')
    p.add_argument('--catalog',default=str(ROOT/'config/cards_assets.json'))
    p.add_argument('--out',required=True);p.add_argument('--layout',choices=LAYOUTS,default='3l2r')
    a=p.parse_args();prepare(a.input,a.catalog,a.out,a.layout)
