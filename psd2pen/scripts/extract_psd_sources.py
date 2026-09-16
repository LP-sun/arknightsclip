"""Extract source raster assets and inspect PSD metadata; never render the Pen design."""
import json
from pathlib import Path
from psd_tools import PSDImage

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets' / 'psd_sources'
OUT.mkdir(parents=True, exist_ok=True)
psd = PSDImage.open(ROOT / '能天使.psd')
psd.topil().crop((1180,315,1764,499)).save(OUT/'reference_right_owned.png')
records = []

def walk(group, parent=''):
    for layer in group:
        path = f'{parent}/{layer.name}'.strip('/')
        row = dict(path=path, kind=layer.kind, bbox=list(layer.bbox), visible=layer.visible,
                   opacity=layer.opacity, clipping=layer.clipping)
        if layer.kind == 'type':
            row['text'] = layer.text
            row['font_resources'] = repr(layer.resource_dict)[:2000]
        records.append(row)
        if layer.is_group():
            walk(layer,path)
        else:
            name = None
            if path in ['卡面/图层 36','卡面/图层 38']:
                name = 'operator_e1.png' if path.endswith('36') else 'operator_e2.png'
            elif parent == '精英等级' and layer.kind == 'pixel' and 405 <= layer.bbox[1] <= 412:
                name = {'精0':'elite0.png','精一':'elite1.png','精二':'elite2.png'}.get(layer.name)
            elif parent == '潜能' and layer.kind == 'pixel' and 440 <= layer.bbox[1] <= 442:
                name = 'potential'+''.join(c for c in layer.name if c.isdigit())+'.png'
            if name:
                im=layer.topil()
                if im is not None:
                    im.save(OUT/name)
                    row['asset'] = str((OUT/name).relative_to(ROOT))
                    row['image_size'] = list(im.size)
            if path in ['卡面/卡面06','卡面/卡面01']:
                row['smartobject'] = dict(filename=layer.smart_object.filename,filetype=layer.smart_object.filetype)
                row['effects'] = repr(layer.effects)
                try:
                    with layer.smart_object.open() as f:
                        nested=PSDImage.open(f)
                        row['embedded_layers']=[dict(name=n.name,kind=n.kind,bbox=list(n.bbox)) for n in nested.descendants()]
                        row['nested_size']=list(nested.size)
                        row['vector_mask']=repr(nested[0].vector_mask)
                        row['vector_paths']=[repr(p) for p in nested[0].vector_mask.paths]
                        row['knots']=[dict(anchor=k.anchor,preceding=k.preceding,leaving=k.leaving) for k in nested[0].vector_mask.paths[0]]
                        row['transform']=layer.smart_object.transform_box
                except Exception as e:
                    row['embedded_error']=str(e)

walk(psd)
(OUT/'source_manifest.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')
for row in records:
    if row.get('asset') or row.get('smartobject') or row['path'].startswith('角色等级/666'):
        print(json.dumps(row,ensure_ascii=False))
