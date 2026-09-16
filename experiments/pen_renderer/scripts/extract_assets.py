import os
import shutil
from PIL import Image
from psd_tools import PSDImage

def extract_spike_assets():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    assets_ui = os.path.join(base_dir, 'assets', 'ui')
    assets_ops = os.path.join(base_dir, 'assets', 'operators')
    assets_players = os.path.join(base_dir, 'assets', 'players')
    
    os.makedirs(assets_ui, exist_ok=True)
    os.makedirs(os.path.join(assets_ops, 'char_103_angel'), exist_ok=True)
    os.makedirs(os.path.join(assets_ops, 'char_002_siege'), exist_ok=True)
    os.makedirs(assets_players, exist_ok=True)

    print("1. 正在提取 PSD 基础底图与能天使立绘...")
    psd_angel_path = r'E:\明日方舟报菜名\psd模板\只需要模板\能天使.psd'
    if os.path.exists(psd_angel_path):
        psd_angel = PSDImage.open(psd_angel_path)
        
        # 提取背景 (Layer 0)
        bg_img = psd_angel[0].topil()
        bg_out = os.path.join(assets_ui, 'bg_clean.png')
        bg_img.save(bg_out, 'PNG')
        print(f"   -> 导出背景底图: {bg_out} ({bg_img.size})")

        # 提取能天使大立绘 (Layer 1)
        angel_full = psd_angel[1].topil()
        angel_out = os.path.join(assets_ops, 'char_103_angel', 'full.png')
        # 创建一个 1920x1080 透明画布保持原坐标
        angel_canvas = Image.new('RGBA', (1920, 1080), (0, 0, 0, 0))
        angel_bbox = psd_angel[1].bbox
        angel_canvas.paste(angel_full, (angel_bbox[0], angel_bbox[1]))
        angel_canvas.save(angel_out, 'PNG')
        print(f"   -> 导出能天使全画幅立绘: {angel_out}")

        # 提取 5 位博士头像
        # P1 (爱花), P2 (咯吱吱), P3 (东城), P4 (HMI), P5 (LEO)
        avatar_indices = [
            (1, 'P1'),
            (3, 'P2'),
            (5, 'P3'),
            (9, 'P4'),
            (12, 'P5')
        ]
        for l_idx, p_name in avatar_indices:
            av_layer = psd_angel[7][l_idx]
            av_img = av_layer.topil()
            av_path = os.path.join(assets_players, f'{p_name}.png')
            av_img.save(av_path, 'PNG')
            print(f"   -> 导出博士头像 {p_name}: {av_path} ({av_img.size})")

        # 提取卡面立绘切片用于 player card crop
        card_01 = psd_angel[2][0].topil()
        card_01_out = os.path.join(assets_ui, 'card_crop_angel.png')
        card_01.save(card_01_out, 'PNG')
        print(f"   -> 导出干员卡面立绘切片: {card_01_out}")

    # 提取推王立绘 (作为 variant_test)
    psd_siege_path = r'E:\明日方舟报菜名\psd模板\全6星干员备份文件（较大）\推王.psd'
    if os.path.exists(psd_siege_path):
        print("2. 正在提取推王立绘...")
        psd_siege = PSDImage.open(psd_siege_path)
        siege_full = psd_siege[1].topil()
        siege_bbox = psd_siege[1].bbox
        siege_canvas = Image.new('RGBA', (1920, 1080), (0, 0, 0, 0))
        siege_canvas.paste(siege_full, (siege_bbox[0], siege_bbox[1]))
        siege_out = os.path.join(assets_ops, 'char_002_siege', 'full.png')
        siege_canvas.save(siege_out, 'PNG')
        print(f"   -> 导出推王立绘: {siege_out}")

        card_siege = psd_siege[2][0].topil()
        card_siege_out = os.path.join(assets_ui, 'card_crop_siege.png')
        card_siege.save(card_siege_out, 'PNG')
        print(f"   -> 导出推王卡面切片: {card_siege_out}")

    print("3. 正在复用 MAA 精英化与潜能徽章素材...")
    maa_dir = r'E:\明日方舟报菜名\maa_templates'
    shutil.copy(os.path.join(maa_dir, 'OperBoxFlagElite1.png'), os.path.join(assets_ui, 'elite_1.png'))
    shutil.copy(os.path.join(maa_dir, 'OperBoxFlagElite2.png'), os.path.join(assets_ui, 'elite_2.png'))
    
    # 精0用透明占位
    e0 = Image.new('RGBA', (40, 40), (0, 0, 0, 0))
    e0.save(os.path.join(assets_ui, 'elite_0.png'))

    # 潜能 1~6
    p1 = Image.new('RGBA', (32, 32), (0, 0, 0, 0))
    p1.save(os.path.join(assets_ui, 'potential_1.png'))
    for pot in range(2, 7):
        src = os.path.join(maa_dir, f'OperBoxPotential{pot}.png')
        dst = os.path.join(assets_ui, f'potential_{pot}.png')
        shutil.copy(src, dst)

    print("素材准备完成！")

if __name__ == '__main__':
    extract_spike_assets()
