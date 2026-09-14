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

    def _get_font(self, font_family, font_size, font_weight="normal"):
        size = int(font_size)
        try:
            if "Impact" in font_family:
                return ImageFont.truetype(self.font_impact_path, size)
            elif "YaHei" in font_family or "Microsoft" in font_family or "SimHei" in font_family:
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

        # 1. 替换中央干员大立绘
        for child in scene.get("children", []):
            if child.get("id") == "OPERATOR_FULL_ART":
                full_art_url = operator_info.get("full_art")
                if full_art_url:
                    child["fill"] = {
                        "type": "image",
                        "url": full_art_url,
                        "mode": "fill"
                    }

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

        # 处理 Frame 与 Rectangle
        if node_type in ["frame", "rectangle"]:
            fill = active_props.get("fill")
            stroke = active_props.get("stroke")
            corner_radius = active_props.get("cornerRadius", 0)
            clip = active_props.get("clip", False)

            # 创建图层用于可能的圆角/clipping
            layer = Image.new('RGBA', (w, h), (0, 0, 0, 0))
            draw = ImageDraw.Draw(layer)

            # 1. 纯色/渐变填充
            if fill:
                f_type = fill.get("type", "color")
                if f_type == "color":
                    c_hex = fill.get("color", "#000000")
                    rgba = self._parse_color(c_hex)
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
                draw.rounded_rectangle([0, 0, w, h], radius=corner_radius, outline=s_color, width=s_width)

            # 3. 递归渲染子元素到当前 layer (或直接到 canvas)
            children = active_props.get("children", [])
            if children:
                # 如果有 flexbox layout="vertical"
                layout = active_props.get("layout")
                if layout == "vertical":
                    cur_y = 0
                    gap = active_props.get("gap", 0)
                    for child in children:
                        child_h = child.get("height", 0)
                        # 水平对齐居中
                        child_w = child.get("width", 0)
                        align = active_props.get("alignItems", "start")
                        child_x = (w - child_w) // 2 if align == "center" else child.get("x", 0)
                        self._render_node(child, layer, offset_x=child_x, offset_y=cur_y, components=components, overrides=overrides)
                        # 文本元素高度推断
                        if child.get("type") == "text":
                            cur_y += child.get("fontSize", 14) + gap
                        else:
                            cur_y += child_h + gap
                else:
                    for child in children:
                        self._render_node(child, layer, offset_x=0, offset_y=0, components=components, overrides=overrides)

            # 4. 如果有圆角 clip 遮罩
            if clip and corner_radius > 0:
                mask = Image.new('L', (w, h), 0)
                mask_draw = ImageDraw.Draw(mask)
                mask_draw.rounded_rectangle([0, 0, w, h], radius=corner_radius, fill=255)
                canvas.paste(layer, (x, y), mask)
            else:
                canvas.paste(layer, (x, y), layer)

        elif node_type == "text":
            content = str(active_props.get("content", ""))
            font_size = active_props.get("fontSize", 14)
            font_family = active_props.get("fontFamily", "Microsoft YaHei")
            font_weight = active_props.get("fontWeight", "normal")
            fill_color = self._parse_color(active_props.get("fill", "#FFFFFF"))
            
            font = self._get_font(font_family, font_size, font_weight)
            draw = ImageDraw.Draw(canvas)
            
            # 计算文字对齐
            text_align = active_props.get("textAlign", "left")
            if text_align == "center":
                # 如果指定了宽度，居中
                text_w = draw.textlength(content, font=font)
                parent_w = active_props.get("width", text_w)
                tx = x + (parent_w - text_w) / 2
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
