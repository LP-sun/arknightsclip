"""Extract two original PSD pixel assets for native Pencil replacement QA.

This does not render a card or modify any PSD/Pen document.
"""
from pathlib import Path
from psd_tools import PSDImage

root = Path(__file__).resolve().parents[1]
for source, layer_name, output in [
    ('推王.psd', '图层 42', 'siege_slot06.png'),
    ('小羊.psd', '图层 56', 'eyjafjalla_slot06.png'),
]:
    psd = PSDImage.open(root / source)
    group = next(layer for layer in psd if layer.name == '卡面')
    layer = next(layer for layer in group if layer.name == layer_name)
    destination = root / 'assets' / 'psd_sources' / output
    layer.topil().save(destination)
    print(source, layer_name, list(layer.bbox), destination)
