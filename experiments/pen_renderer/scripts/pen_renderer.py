"""
PenRenderer 原型实现 (experiments/pen_renderer/scripts/pen_renderer.py)
用于技术验证：单一五人 .pen 母版 + scene JSON -> 自动生成完整报菜名画面 -> 导出 1920x1080 PNG
"""

import os
import sys
import copy
import time
import json
from PIL import Image, ImageDraw, ImageFont, ImageColor

class PenRenderer:
    def __init__(self, base_asset_dir=None):
        if base_asset_dir is None:
            # 默认指向 experiments/pen_renderer
            self.base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        else:
            self.base_dir = os.path.abspath(base_asset_dir)
            
        self._init_fonts()

    def _init_fonts(self):
        font_dir = r"C:\Windows\Fonts"
        self.font_yahei_path = os.path.join(font_dir, "msyh.ttc")
        self.font_yahei_bold_path = os.path.join(font_dir, "msyhbd.ttc")
        self.font_impact_path = os.path.join(font_dir, "impact.ttf")
        self.font_arial_path = os.path.join(font_dir, "arial.ttf")
        self.font_bahnschrift_path = os.path.join(font_dir, "bahnschrift.ttf")
        self.font_simhei_path = os.path.join(font_dir, "simhei.ttf")

    def _get_font(self, font_family, font_size, font_weight="normal"):
        size = int(font_size)
        try:
            if "Bahnschrift" in font_family or "DIN" in font_family or "Bender" in font_family or "Oswald" in font_family:
                return ImageFont.truetype(self.font_bahnschrift_path, size)
            elif "Impact" in font_family:
                return ImageFont.truetype(self.font_impact_path, size)
            elif "SimHei" in font_family:
                return ImageFont.truetype(self.font_simhei_path, size)
            elif "YaHei" in font_family or "Microsoft" in font_family or "Sans" in font_family:
                if font_weight == "bold":
                    return ImageFont.truetype(self.font_yahei_bold_path, size)
                return ImageFont.truetype(self.font_yahei_path, size)
            else:
                return ImageFont.truetype(self.font_arial_path, size)
        except Exception:
            return ImageFont.load_default()

    def _resolve_asset_path(self, rel_url):
        if not rel_url:
            return None
        clean_url = rel_url.replace("./", "").replace("../", "").replace("/", os.sep)
        # 1. 优先尝试 experiments/shared
        shared_dir = os.path.abspath(os.path.join(self.base_dir, "..", "shared"))
        shared_path = os.path.join(shared_dir, clean_url)
        if os.path.exists(shared_path):
            return shared_path
        # 2. 尝试 self.base_dir
        full_path = os.path.join(self.base_dir, clean_url)
        if os.path.exists(full_path):
            return full_path
        # 3. 尝试相对于工作区根目录
        workspace_path = os.path.abspath(os.path.join(self.base_dir, "..", "..", clean_url))
        if os.path.exists(workspace_path):
            return workspace_path
        return shared_path

    def render_scene(self, template_path, manifest_path_or_dict, output_pen_path=None, output_png_path=None):
        """
        核心 API：
        1. 读取模板
        2. 应用 scene manifest 参数
        3. 更新五个 instance
        4. 替换中央干员立绘
        5. 保存派生 .pen (调试模式)
        6. 输出 PNG
        7. 输出 render metadata
        """
        t0 = time.time()
        
        # 1. 读取模板
        with open(template_path, 'r', encoding='utf-8') as f:
            template_doc = json.load(f)

        # 2. 读取 manifest
        if isinstance(manifest_path_or_dict, dict):
            manifest = manifest_path_or_dict
        else:
            with open(manifest_path_or_dict, 'r', encoding='utf-8') as f:
                manifest = json.load(f)

        # 3. 在内存中应用 manifest 参数
        modified_doc = self.apply_manifest(template_doc, manifest)

        # 4. 保存派生 .pen 文件
        if output_pen_path:
            os.makedirs(os.path.dirname(os.path.abspath(output_pen_path)), exist_ok=True)
            with open(output_pen_path, 'w', encoding='utf-8') as f:
                json.dump(modified_doc, f, indent=2, ensure_ascii=False)

        # 5. 渲染为 1920x1080 图像
        canvas = Image.new('RGBA', (1920, 1080), (0, 0, 0, 255))
        self._render_document(modified_doc, canvas)

        if output_png_path:
            os.makedirs(os.path.dirname(os.path.abspath(output_png_path)), exist_ok=True)
            canvas.save(output_png_path, 'PNG')

        render_duration = time.time() - t0
        metadata = {
            "template": template_path,
            "operator_id": manifest.get("operator", {}).get("id"),
            "operator_name": manifest.get("operator", {}).get("name"),
            "resolution": [1920, 1080],
            "render_time_seconds": round(render_duration, 4),
            "output_pen": output_pen_path,
            "output_png": output_png_path,
            "status": "SUCCESS"
        }
        return metadata

    def apply_manifest(self, doc, manifest):
        doc_copy = copy.deepcopy(doc)
        operator_info = manifest.get("operator", {})
        players_info = manifest.get("players", {})

        # 找到根场景 ROOT_REPORT_SCENE
        scene = None
        for child in doc_copy.get("children", []):
            if child.get("id") == "ROOT_REPORT_SCENE":
                scene = child
                break
        
        if not scene:
            raise ValueError("未在模板中找到 ROOT_REPORT_SCENE 节点！")

        # 1. 替换中央干员大立绘、背景代号水印与档案面板
        op_id = operator_info.get("id", "")
        op_name = operator_info.get("name", "")
        op_codename = "EXUSIAI" if "angel" in op_id else ("SIEGE" if "siege" in op_id else op_id.split("_")[-1].upper())
        op_class = "CLASS // SNIPER (速射狙击)" if "angel" in op_id else ("CLASS // VANGUARD (先锋干员)" if "siege" in op_id else "CLASS // OPERATOR")
        op_num = "103" if "angel" in op_id else ("002" if "siege" in op_id else "001")

        for child in scene.get("children", []):
            cid = child.get("id")
            if cid == "OPERATOR_FULL_ART":
                full_art_url = operator_info.get("full_art")
                if full_art_url:
                    child["fill"] = {
                        "type": "image",
                        "url": full_art_url,
                        "mode": "fill"
                    }
            elif cid == "BG_CODENAME_WATERMARK":
                child["content"] = op_codename
            elif cid == "OPERATOR_DOSSIER_PANEL":
                for d_child in child.get("children", []):
                    did = d_child.get("id")
                    if did == "OP_CN_NAME":
                        d_child["content"] = " ".join(list(op_name))
                    elif did == "OP_EN_NAME":
                        d_child["content"] = op_codename
                    elif did == "CLASS_TAG":
                        d_child["content"] = op_class
                    elif did == "REG_CODE":
                        d_child["content"] = f"RHODES ISLAND ARCHIVE · NO. {op_num}/138"

        # 2. 更新五个 Instance 节点 (P1 ~ P5)
        for p_key in ["P1", "P2", "P3", "P4", "P5"]:
            p_data = players_info.get(p_key)
            if not p_data:
                continue

            instance_node = None
            for child in scene.get("children", []):
                if child.get("id") == p_key:
                    instance_node = child
                    break
            
            if not instance_node:
                continue

            desc = instance_node.setdefault("descendants", {})
            own = p_data.get("own", False)

            # 无论是否持有，博士信息始终显示
            desc["DOCTOR_AVATAR"] = {
                "fill": {
                    "type": "image",
                    "url": p_data.get("avatar", ""),
                    "mode": "fill"
                }
            }
            desc["DOCTOR_NAME"] = {
                "content": p_data.get("display_name", p_key)
            }
            desc["DOCTOR_LEVEL"] = {
                "content": f"LV. {p_data.get('doctor_level', 120)}"
            }

            if own:
                # 已持有状态
                card_crop = operator_info.get("card_crop", "")
                desc["OPERATOR_CARD"] = {
                    "enabled": True,
                    "fill": {
                        "type": "image",
                        "url": card_crop,
                        "mode": "fill"
                    }
                }
                desc["STATE_DECOR_PANEL"] = {"enabled": True}
                desc["LV_LABEL"] = {"enabled": True}
                desc["OPERATOR_LEVEL"] = {
                    "enabled": True,
                    "content": str(p_data.get("level", 90))
                }
                # 精英度互斥
                elite_val = p_data.get("elite", 2)
                for e in [0, 1, 2]:
                    desc[f"ELITE_{e}"] = {"enabled": (e == elite_val)}

                # 潜能互斥 (1~6)
                pot_val = p_data.get("potential", 1)
                for p in range(1, 7):
                    desc[f"POTENTIAL_{p}"] = {"enabled": (p == pot_val)}

                # 隐藏 NO_INFO
                desc["NO_INFO"] = {"enabled": False}
            else:
                # 未持有状态
                desc["OPERATOR_CARD"] = {"enabled": False}
                desc["STATE_DECOR_PANEL"] = {"enabled": False}
                desc["LV_LABEL"] = {"enabled": False}
                desc["OPERATOR_LEVEL"] = {"enabled": False}
                for e in [0, 1, 2]:
                    desc[f"ELITE_{e}"] = {"enabled": False}
                for p in range(1, 7):
                    desc[f"POTENTIAL_{p}"] = {"enabled": False}
                # 显示 NO_INFO
                desc["NO_INFO"] = {"enabled": True}

        return doc_copy

    def _render_document(self, doc, canvas):
        # 建立组件字典
        components = {}
        scene = None
        for c in doc.get("children", []):
            if c.get("reusable"):
                components[c.get("id")] = c
            elif c.get("id") == "ROOT_REPORT_SCENE":
                scene = c

        if not scene:
            return

        # 递归渲染场景
        self._render_node(scene, canvas, offset_x=0, offset_y=0, components=components, overrides={})

    def _render_node(self, node, canvas, offset_x, offset_y, components, overrides):
        node_id = node.get("id", "")
        # 应用 overrides
        active_props = copy.deepcopy(node)
        if node_id in overrides:
            active_props.update(overrides[node_id])

        if active_props.get("enabled", True) is False:
            return

        node_type = active_props.get("type")
        x = offset_x + active_props.get("x", 0)
        y = offset_y + active_props.get("y", 0)
        w = active_props.get("width", 0)
        h = active_props.get("height", 0)

        # 处理 Instance (ref)
        if node_type == "ref":
            comp_id = active_props.get("ref")
            if comp_id in components:
                comp_node = components[comp_id]
                inst_descendants = active_props.get("descendants", {})
                self._render_node(comp_node, canvas, offset_x=x, offset_y=y, components=components, overrides=inst_descendants)
            return

        # 处理 Line
        if node_type == "line":
            stroke = active_props.get("stroke", {})
            s_color = self._parse_color(stroke.get("color", "#FFFFFF"))
            s_width = int(active_props.get("strokeWidth", 1))
            x1 = x + active_props.get("x1", 0)
            y1 = y + active_props.get("y1", 0)
            x2 = x + active_props.get("x2", w)
            y2 = y + active_props.get("y2", h)
            draw = ImageDraw.Draw(canvas)
            draw.line([(x1, y1), (x2, y2)], fill=s_color, width=s_width)
            return

        # 处理 Frame 与 Rectangle 与 Polygon
        if node_type in ["frame", "rectangle", "polygon"]:
            fill = active_props.get("fill")
            stroke = active_props.get("stroke")
            corner_radius = active_props.get("cornerRadius", 0)
            clip = active_props.get("clip", False)
            points = active_props.get("points")
            shadow = active_props.get("shadow")
            opacity = active_props.get("opacity", 1.0)

            # 硬质阴影渲染 (Hard offset shadow)
            if shadow and (w > 0 and h > 0):
                sh_col = self._parse_color(shadow.get("color", "#00000088"))
                sh_ox = int(shadow.get("offsetX", 4))
                sh_oy = int(shadow.get("offsetY", 4))
                sh_layer = Image.new('RGBA', (w, h), (0, 0, 0, 0))
                sh_draw = ImageDraw.Draw(sh_layer)
                if points:
                    pts = [(int(p[0]), int(p[1])) for p in points]
                    sh_draw.polygon(pts, fill=sh_col)
                else:
                    sh_draw.rounded_rectangle([0, 0, w, h], radius=corner_radius, fill=sh_col)
                canvas.paste(sh_layer, (x + sh_ox, y + sh_oy), sh_layer)

            # 创建图层用于可能的裁剪/渲染
            layer = Image.new('RGBA', (w, h), (0, 0, 0, 0))
            draw = ImageDraw.Draw(layer)

            # 1. 纯色/渐变填充
            if fill:
                f_type = fill.get("type", "color")
                if f_type == "color":
                    c_hex = fill.get("color", "#000000")
                    rgba = self._parse_color(c_hex)
                    if points:
                        pts = [(int(p[0]), int(p[1])) for p in points]
                        draw.polygon(pts, fill=rgba)
                    else:
                        draw.rounded_rectangle([0, 0, w, h], radius=corner_radius, fill=rgba)
                elif f_type == "gradient":
                    # 线性垂直渐变渲染
                    self._render_linear_gradient(layer, fill, w, h)
                elif f_type == "image":
                    img_url = fill.get("url")
                    resolved_img = self._resolve_asset_path(img_url)
                    if resolved_img and os.path.exists(resolved_img):
                        src_img = Image.open(resolved_img).convert('RGBA')
                        mode = fill.get("mode", "fill")
                        fitted_img = self._fit_image(src_img, w, h, mode)
                        layer.paste(fitted_img, (0, 0), fitted_img)

            # 2. 边框
            if stroke:
                s_color = self._parse_color(stroke.get("color", "#FFFFFF"))
                s_width = int(active_props.get("strokeWidth", 1))
                if points:
                    pts = [(int(p[0]), int(p[1])) for p in points]
                    draw.polygon(pts, outline=s_color, width=s_width)
                else:
                    draw.rounded_rectangle([0, 0, w, h], radius=corner_radius, outline=s_color, width=s_width)

            # 3. 递归渲染子元素到当前 layer
            children = active_props.get("children", [])
            if children:
                layout = active_props.get("layout")
                if layout == "vertical":
                    cur_y = 0
                    gap = active_props.get("gap", 0)
                    for child in children:
                        child_h = child.get("height", 0)
                        child_w = child.get("width", 0)
                        align = active_props.get("alignItems", "start")
                        child_x = (w - child_w) // 2 if align == "center" else child.get("x", 0)
                        self._render_node(child, layer, offset_x=child_x, offset_y=cur_y, components=components, overrides=overrides)
                        if child.get("type") == "text":
                            cur_y += child.get("fontSize", 14) + gap
                        else:
                            cur_y += child_h + gap
                else:
                    for child in children:
                        self._render_node(child, layer, offset_x=0, offset_y=0, components=components, overrides=overrides)

            # 4. 遮罩裁切 (Mask clip)
            if opacity < 1.0:
                # 调节透明度
                r, g, b, a = layer.split()
                a = a.point(lambda p: int(p * opacity))
                layer = Image.merge('RGBA', (r, g, b, a))

            if clip:
                mask = Image.new('L', (w, h), 0)
                mask_draw = ImageDraw.Draw(mask)
                if points:
                    pts = [(int(p[0]), int(p[1])) for p in points]
                    mask_draw.polygon(pts, fill=255)
                elif corner_radius > 0:
                    mask_draw.rounded_rectangle([0, 0, w, h], radius=corner_radius, fill=255)
                else:
                    mask_draw.rectangle([0, 0, w, h], fill=255)
                canvas.paste(layer, (x, y), mask)
            else:
                canvas.paste(layer, (x, y), layer)

        elif node_type == "text":
            content = str(active_props.get("content", ""))
            font_size = active_props.get("fontSize", 14)
            font_family = active_props.get("fontFamily", "Microsoft YaHei")
            font_weight = active_props.get("fontWeight", "normal")
            fill_color = self._parse_color(active_props.get("fill", "#FFFFFF"))
            
            # 若包含非 ASCII 字符（如中文或 ★ 符号），但选用了无 CJK 字形的西文字体，则自动回退到 YaHei 避免豆腐块
            has_non_ascii = any(ord(c) > 127 for c in content)
            if has_non_ascii and any(f in font_family for f in ["Bahnschrift", "Impact", "Arial", "Bender", "Oswald", "DIN"]):
                font_family = "Microsoft YaHei"

            font = self._get_font(font_family, font_size, font_weight)
            draw = ImageDraw.Draw(canvas)
            
            # 计算文字对齐
            text_align = active_props.get("textAlign", "left")
            text_w = draw.textlength(content, font=font)
            parent_w = active_props.get("width", text_w)
            if text_align == "center":
                tx = x + (parent_w - text_w) / 2
            elif text_align == "right":
                tx = x + parent_w - text_w
            else:
                tx = x
            draw.text((tx, y), content, font=font, fill=fill_color)

    def _render_linear_gradient(self, layer, fill, w, h):
        colors = fill.get("colors", [])
        if len(colors) < 2:
            return
        c0 = self._parse_color(colors[0]["color"])
        c1 = self._parse_color(colors[-1]["color"])
        draw = ImageDraw.Draw(layer)
        for i in range(h):
            ratio = i / float(h)
            r = int(c0[0] + (c1[0] - c0[0]) * ratio)
            g = int(c0[1] + (c1[1] - c0[1]) * ratio)
            b = int(c0[2] + (c1[2] - c0[2]) * ratio)
            a = int(c0[3] + (c1[3] - c0[3]) * ratio)
            draw.line([(0, i), (w, i)], fill=(r, g, b, a))

    def _fit_image(self, src_img, target_w, target_h, mode="fill"):
        sw, sh = src_img.size
        if sw == 0 or sh == 0 or target_w == 0 or target_h == 0:
            return src_img

        if mode == "fit":
            scale = min(target_w / sw, target_h / sh)
            nw, nh = int(sw * scale), int(sh * scale)
            resized = src_img.resize((nw, nh), Image.Resampling.LANCZOS)
            res = Image.new('RGBA', (target_w, target_h), (0, 0, 0, 0))
            res.paste(resized, ((target_w - nw) // 2, (target_h - nh) // 2))
            return res
        else: # "fill"
            scale = max(target_w / sw, target_h / sh)
            nw, nh = int(sw * scale), int(sh * scale)
            resized = src_img.resize((nw, nh), Image.Resampling.LANCZOS)
            # 居中裁剪
            left = (nw - target_w) // 2
            top = (nh - target_h) // 2
            return resized.crop((left, top, left + target_w, top + target_h))

    def _parse_color(self, hex_str):
        if not hex_str:
            return (255, 255, 255, 255)
        hex_str = hex_str.lstrip('#')
        if len(hex_str) == 6:
            r = int(hex_str[0:2], 16)
            g = int(hex_str[2:4], 16)
            b = int(hex_str[4:6], 16)
            return (r, g, b, 255)
        elif len(hex_str) == 8:
            r = int(hex_str[0:2], 16)
            g = int(hex_str[2:4], 16)
            b = int(hex_str[4:6], 16)
            a = int(hex_str[6:8], 16)
            return (r, g, b, a)
        elif len(hex_str) == 3:
            r = int(hex_str[0] * 2, 16)
            g = int(hex_str[1] * 2, 16)
            b = int(hex_str[2] * 2, 16)
        return (255, 255, 255, 255)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="PenRenderer CLI")
    parser.add_argument("--template", default="experiments/pen_renderer/report_5p_master.pen", help="Path to .pen master template")
    parser.add_argument("--manifest", required=True, help="Path to scene manifest JSON")
    parser.add_argument("--output", required=True, help="Path to output PNG")
    parser.add_argument("--output-pen", default=None, help="Optional path to output derived .pen")
    args = parser.parse_args()

    renderer = PenRenderer()
    meta = renderer.render_scene(
        template_path=args.template,
        manifest_path_or_dict=args.manifest,
        output_pen_path=args.output_pen,
        output_png_path=args.output
    )
    print(json.dumps(meta, indent=2, ensure_ascii=False))
