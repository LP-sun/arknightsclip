"""
生成全 Scene 缩略图 Contact Sheet 验收图 (遵从 psd模板/README Phase 10 要求)
1. 扫描 generated/layered/ 下所有场景
2. 重构三层预览: V1(background) + V2(character_cards) + V3(doctor_info)
3. 生成 480x270 缩略图
4. 拼接为大尺寸网格全景图 reports/contact_sheet.png
"""

import os
import math
from PIL import Image, ImageDraw, ImageFont

def generate_contact_sheet():
    layered_dir = r"E:\明日方舟报菜名\generated\layered"
    scenes = sorted([d for d in os.listdir(layered_dir) if os.path.isdir(os.path.join(layered_dir, d))])
    
    if not scenes:
        print("未找到分层渲染场景！")
        return

    print(f"正在为 {len(scenes)} 个分层场景制作 Contact Sheet 验收全景图...")

    thumb_w, thumb_h = 384, 216 # 1/5 缩放
    cols = 6
    rows = math.ceil(len(scenes) / cols)

    sheet_w = cols * thumb_w
    sheet_h = rows * thumb_h
    sheet = Image.new("RGB", (sheet_w, sheet_h), (20, 20, 20))
    draw = ImageDraw.Draw(sheet)

    for idx, s_name in enumerate(scenes):
        s_path = os.path.join(layered_dir, s_name)
        bg_p = os.path.join(s_path, "background.png")
        cards_p = os.path.join(s_path, "character_cards.png")
        doc_p = os.path.join(s_path, "doctor_info.png")

        if os.path.exists(bg_p) and os.path.exists(cards_p) and os.path.exists(doc_p):
            bg = Image.open(bg_p).convert("RGBA")
            cards = Image.open(cards_p).convert("RGBA")
            doc = Image.open(doc_p).convert("RGBA")

            recon = Image.alpha_composite(bg, cards)
            recon = Image.alpha_composite(recon, doc).convert("RGB")

            thumb = recon.resize((thumb_w, thumb_h), Image.Resampling.LANCZOS)
            c = idx % cols
            r = idx // cols
            x = c * thumb_w
            y = r * thumb_h
            sheet.paste(thumb, (x, y))

            # 绘制场景名称标签
            draw.rectangle([x, y, x + 180, y + 22], fill=(0, 0, 0, 180))
            draw.text((x + 6, y + 4), s_name, fill=(255, 255, 255))

    out_file = r"E:\明日方舟报菜名\reports\contact_sheet.png"
    sheet.save(out_file, "PNG")
    print(f"Contact Sheet 成功保存至: {out_file} (尺寸: {sheet_w}x{sheet_h})")

if __name__ == "__main__":
    generate_contact_sheet()
