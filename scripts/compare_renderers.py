import os
import sys
from PIL import Image, ImageDraw, ImageFont, ImageChops

def create_ab_comparison(scene_name, pen_img_path, react_img_path, ref_img_path=None, output_path=None):
    if not os.path.exists(pen_img_path) or not os.path.exists(react_img_path):
        print(f"Error: Missing input image for {scene_name}")
        return

    pen_img = Image.open(pen_img_path).convert('RGBA')
    react_img = Image.open(react_img_path).convert('RGBA')

    # 计算第三栏：如果有参考图用参考图，否则计算绝对差异图 (Absolute Difference)
    if ref_img_path and os.path.exists(ref_img_path):
        third_img = Image.open(ref_img_path).convert('RGBA')
        third_label = "RIGHT: REFERENCE (PSD)"
    else:
        # 放大差异以便肉眼观察
        diff = ImageChops.difference(pen_img, react_img)
        diff_enhanced = diff.point(lambda p: min(255, p * 4))
        third_img = diff_enhanced
        third_label = "RIGHT: ABSOLUTE DIFFERENCE (x4 ENHANCED)"

    # 缩放至宽 960，高 540
    target_w, target_h = 960, 540
    p_thumb = pen_img.resize((target_w, target_h), Image.Resampling.LANCZOS)
    r_thumb = react_img.resize((target_w, target_h), Image.Resampling.LANCZOS)
    t_thumb = third_img.resize((target_w, target_h), Image.Resampling.LANCZOS)

    # 创建 3 联屏大图: 宽 2880, 高 540 + 60(标题栏) = 600
    sheet = Image.new('RGBA', (target_w * 3, target_h + 60), (15, 18, 24, 255))
    draw = ImageDraw.Draw(sheet)

    # 加载字体
    try:
        font_title = ImageFont.truetype(r"C:\Windows\Fonts\arial.ttf", 22)
        font_sub = ImageFont.truetype(r"C:\Windows\Fonts\msyh.ttc", 16)
    except Exception:
        font_title = font_sub = ImageFont.load_default()

    # 绘制顶部栏
    draw.rectangle([(0, 0), (target_w * 3, 60)], fill=(10, 12, 16, 255))
    draw.text((30, 16), f"ARKNIGHTS RENDERER A/B COMPARISON · SCENE: {scene_name.upper()}", fill=(226, 232, 240), font=font_title)

    # 绘制三联图像
    sheet.paste(p_thumb, (0, 60))
    sheet.paste(r_thumb, (target_w, 60))
    sheet.paste(t_thumb, (target_w * 2, 60))

    # 绘制面板标签
    labels = [
        (15, 75, "LEFT: PEN.DEV (AST HEADLESS)", (0, 180, 216, 220)),
        (target_w + 15, 75, "CENTER: REACT / CSS (CHROMIUM)", (76, 201, 140, 220)),
        (target_w * 2 + 15, 75, third_label, (239, 71, 111, 220))
    ]

    for x, y, text, bg_color in labels:
        bbox = draw.textbbox((x, y), text, font=font_sub)
        pad = 6
        draw.rectangle([(bbox[0] - pad, bbox[1] - pad), (bbox[2] + pad, bbox[3] + pad)], fill=(10, 14, 20, 210), outline=bg_color, width=1)
        draw.text((x, y), text, fill=(255, 255, 255), font=font_sub)

    # 绘制分割线
    draw.line([(target_w, 60), (target_w, target_h + 60)], fill=(50, 60, 75, 255), width=2)
    draw.line([(target_w * 2, 60), (target_w * 2, target_h + 60)], fill=(50, 60, 75, 255), width=2)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    sheet.save(output_path, "PNG")
    print(f"成功生成 A/B 对比大图: {output_path}")

def main():
    base_dir = r"E:\明日方舟报菜名"
    reports_ab_dir = os.path.join(base_dir, "reports", "renderer_ab")
    os.makedirs(reports_ab_dir, exist_ok=True)

    pen_dir = os.path.join(base_dir, "experiments", "pen_renderer", "outputs")
    react_dir = os.path.join(base_dir, "experiments", "react_renderer", "outputs")
    ref_psd = os.path.join(base_dir, "experiments", "shared", "reference", "reference_psd.png")

    # 1. exusiai_test
    create_ab_comparison(
        scene_name="exusiai_test",
        pen_img_path=os.path.join(pen_dir, "exusiai_test.png"),
        react_img_path=os.path.join(react_dir, "exusiai_test.png"),
        ref_img_path=ref_psd,
        output_path=os.path.join(reports_ab_dir, "exusiai_test_comparison.png")
    )

    # 2. variant_test
    create_ab_comparison(
        scene_name="variant_test",
        pen_img_path=os.path.join(pen_dir, "variant_test.png"),
        react_img_path=os.path.join(react_dir, "variant_test.png"),
        ref_img_path=None,
        output_path=os.path.join(reports_ab_dir, "variant_test_comparison.png")
    )

if __name__ == "__main__":
    main()
