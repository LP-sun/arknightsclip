import os
import sys
import json
import copy
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = r"E:\明日方舟报菜名"
sys.path.insert(0, BASE_DIR)
from experiments.pen_renderer.scripts.pen_renderer import PenRenderer

ITER_DIR = os.path.join(BASE_DIR, "experiments", "pen_renderer", "iterations")
SHARED_DIR = os.path.join(BASE_DIR, "experiments", "shared")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
MANIFEST_A = os.path.join(SHARED_DIR, "manifests", "exusiai_test.json")
MANIFEST_B = os.path.join(SHARED_DIR, "manifests", "variant_test.json")

os.makedirs(ITER_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)

def build_base_document(version="2.17"):
    return {
        "version": version,
        "variables": {},
        "themes": {},
        "children": []
    }

# =============================================================
# Iteration 1 (v1.1): Structural Purge (去圆角、去发光、硬质方块)
# =============================================================
def generate_iteration_1():
    doc = build_base_document()

    comp = {
        "id": "comp_player_card",
        "name": "PLAYER_CARD_COMPONENT",
        "type": "frame",
        "reusable": True,
        "width": 440,
        "height": 180,
        "cornerRadius": 0,
        "fill": {"type": "color", "color": "#1D1F20F2"},
        "stroke": {"type": "color", "color": "#3B434D"},
        "strokeWidth": 2,
        "shadow": {"color": "#00000088", "offsetX": 6, "offsetY": 6},
        "children": [
            # 博士方形头像
            {
                "id": "DOCTOR_CONTAINER",
                "type": "frame",
                "x": 0,
                "y": 0,
                "width": 110,
                "height": 180,
                "fill": {"type": "color", "color": "#15181C"},
                "stroke": {"type": "color", "color": "#282E35"},
                "strokeWidth": 1,
                "children": [
                    {
                        "id": "DOCTOR_AVATAR",
                        "type": "frame",
                        "x": 15,
                        "y": 15,
                        "width": 80,
                        "height": 80,
                        "cornerRadius": 0,
                        "stroke": {"type": "color", "color": "#0098DC"},
                        "strokeWidth": 2,
                        "fill": {"type": "image", "url": "assets/players/P1.png", "mode": "fill"}
                    },
                    {"id": "DOCTOR_TAG", "type": "text", "x": 15, "y": 102, "content": "P01 // DOC", "fontFamily": "Bahnschrift", "fontSize": 11, "fill": "#0098DC"},
                    {"id": "DOCTOR_NAME", "type": "text", "x": 10, "y": 118, "width": 90, "textAlign": "center", "content": "爱花", "fontFamily": "Microsoft YaHei", "fontSize": 14, "fontWeight": "bold", "fill": "#FFFFFF"},
                    {"id": "DOCTOR_LEVEL", "type": "text", "x": 10, "y": 146, "width": 90, "textAlign": "center", "content": "LV. 106", "fontFamily": "Bahnschrift", "fontSize": 14, "fill": "#8D8D8D"}
                ]
            },
            # 干员半身卡面
            {
                "id": "OPERATOR_CARD",
                "type": "frame",
                "x": 110,
                "y": 0,
                "width": 330,
                "height": 180,
                "fill": {"type": "image", "url": "assets/ui/card_crop_angel.png", "mode": "fill"},
                "clip": True
            },
            # 状态面板
            {
                "id": "STATE_DECOR_PANEL",
                "type": "frame",
                "x": 125,
                "y": 125,
                "width": 105,
                "height": 45,
                "fill": {"type": "color", "color": "#090A0BD9"},
                "children": [
                    {"id": "LV_LABEL", "type": "text", "x": 10, "y": 14, "content": "LV", "fontFamily": "Bahnschrift", "fontSize": 12, "fill": "#0098DC"},
                    {"id": "OPERATOR_LEVEL", "type": "text", "x": 30, "y": 8, "content": "90", "fontFamily": "Bahnschrift", "fontSize": 26, "fontWeight": "bold", "fill": "#FFFFFF"}
                ]
            },
            # 精英度
            {"id": "ELITE_0", "type": "frame", "x": 350, "y": 130, "width": 34, "height": 34, "fill": {"type": "image", "url": "assets/ui/elite_0.png", "mode": "fit"}},
            {"id": "ELITE_1", "type": "frame", "x": 350, "y": 130, "width": 34, "height": 34, "fill": {"type": "image", "url": "assets/ui/elite_1.png", "mode": "fit"}},
            {"id": "ELITE_2", "type": "frame", "x": 350, "y": 130, "width": 34, "height": 34, "fill": {"type": "image", "url": "assets/ui/elite_2.png", "mode": "fit"}},
            # 潜能
            {"id": "POTENTIAL_1", "type": "frame", "x": 390, "y": 130, "width": 34, "height": 34, "fill": {"type": "image", "url": "assets/ui/potential_1.png", "mode": "fit"}},
            {"id": "POTENTIAL_2", "type": "frame", "x": 390, "y": 130, "width": 34, "height": 34, "fill": {"type": "image", "url": "assets/ui/potential_2.png", "mode": "fit"}},
            {"id": "POTENTIAL_3", "type": "frame", "x": 390, "y": 130, "width": 34, "height": 34, "fill": {"type": "image", "url": "assets/ui/potential_3.png", "mode": "fit"}},
            {"id": "POTENTIAL_4", "type": "frame", "x": 390, "y": 130, "width": 34, "height": 34, "fill": {"type": "image", "url": "assets/ui/potential_4.png", "mode": "fit"}},
            {"id": "POTENTIAL_5", "type": "frame", "x": 390, "y": 130, "width": 34, "height": 34, "fill": {"type": "image", "url": "assets/ui/potential_5.png", "mode": "fit"}},
            {"id": "POTENTIAL_6", "type": "frame", "x": 390, "y": 130, "width": 34, "height": 34, "fill": {"type": "image", "url": "assets/ui/potential_6.png", "mode": "fit"}},
            # NO INFO
            {
                "id": "NO_INFO",
                "type": "frame",
                "x": 110,
                "y": 0,
                "width": 330,
                "height": 180,
                "fill": {"type": "color", "color": "#181B1F"},
                "children": [
                    {"id": "NO_INFO_TITLE", "type": "text", "x": 0, "y": 75, "width": 330, "textAlign": "center", "content": "[ NO RECORD ]", "fontFamily": "Bahnschrift", "fontSize": 20, "fill": "#6B7280"}
                ]
            }
        ]
    }

    scene = {
        "id": "ROOT_REPORT_SCENE",
        "type": "frame",
        "width": 1920,
        "height": 1080,
        "fill": {"type": "image", "url": "assets/ui/bg_clean.png", "mode": "fill"},
        "children": [
            {
                "id": "HEADER_GROUP",
                "type": "frame",
                "x": 60,
                "y": 45,
                "width": 600,
                "height": 80,
                "children": [
                    {"id": "TITLE_BAR", "type": "text", "x": 0, "y": 0, "content": "RHODES ISLAND TERMINAL // PERSONNEL ARCHIVE", "fontFamily": "Bahnschrift", "fontSize": 24, "fontWeight": "bold", "fill": "#22252A"},
                    {"id": "SUBTITLE_BAR", "type": "text", "x": 0, "y": 32, "content": "明日方舟六星干员报菜名 · 五人战术核验系统 (v1.1 结构去伪·硬质方框)", "fontFamily": "Microsoft YaHei", "fontSize": 13, "fill": "#0098DC"}
                ]
            },
            {"id": "OPERATOR_FULL_ART", "type": "frame", "x": 0, "y": 0, "width": 1920, "height": 1080, "fill": {"type": "image", "url": "assets/operators/char_103_angel/full.png", "mode": "fill"}},
            {"id": "P1", "type": "ref", "ref": "comp_player_card", "x": 50, "y": 160},
            {"id": "P2", "type": "ref", "ref": "comp_player_card", "x": 50, "y": 440},
            {"id": "P3", "type": "ref", "ref": "comp_player_card", "x": 50, "y": 720},
            {"id": "P4", "type": "ref", "ref": "comp_player_card", "x": 1430, "y": 290},
            {"id": "P5", "type": "ref", "ref": "comp_player_card", "x": 1430, "y": 570}
        ]
    }
    doc["children"] = [comp, scene]
    path = os.path.join(ITER_DIR, "v1_structural_purge.pen")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=2, ensure_ascii=False)
    return path

# =============================================================
# Iteration 2 (v1.2): Directional Chevron Geometry (方向性切角卡面)
# =============================================================
def generate_iteration_2():
    doc = build_base_document()

    # 左侧向右指向的多边形切角卡片 (460 x 180)
    comp_left = {
        "id": "comp_player_card_left",
        "name": "PLAYER_CARD_LEFT",
        "type": "frame",
        "reusable": True,
        "width": 460,
        "height": 180,
        "children": [
            # 六边形切角底板
            {
                "id": "CHEVRON_BG",
                "type": "polygon",
                "x": 0,
                "y": 0,
                "width": 460,
                "height": 180,
                "points": [[0, 0], [425, 0], [460, 90], [425, 180], [0, 180]],
                "fill": {"type": "color", "color": "#F8F9FA"},
                "stroke": {"type": "color", "color": "#3B434E"},
                "strokeWidth": 2,
                "shadow": {"color": "#00000066", "offsetX": 6, "offsetY": 6}
            },
            # 博士信息栏
            {
                "id": "DOCTOR_CONTAINER",
                "type": "frame",
                "x": 0,
                "y": 0,
                "width": 110,
                "height": 180,
                "fill": {"type": "color", "color": "#252930"},
                "children": [
                    {"id": "DOCTOR_AVATAR", "type": "frame", "x": 15, "y": 15, "width": 80, "height": 80, "stroke": {"type": "color", "color": "#0098DC"}, "strokeWidth": 2, "fill": {"type": "image", "url": "assets/players/P1.png", "mode": "fill"}},
                    {"id": "DOCTOR_NAME", "type": "text", "x": 10, "y": 106, "width": 90, "textAlign": "center", "content": "爱花", "fontFamily": "Microsoft YaHei", "fontSize": 13, "fontWeight": "bold", "fill": "#FFFFFF"},
                    {"id": "DOCTOR_LEVEL", "type": "text", "x": 10, "y": 136, "width": 90, "textAlign": "center", "content": "LV. 106", "fontFamily": "Bahnschrift", "fontSize": 14, "fill": "#FFD800"}
                ]
            },
            # 干员卡面 (多边形裁剪)
            {
                "id": "OPERATOR_CARD",
                "type": "polygon",
                "x": 110,
                "y": 0,
                "width": 255,
                "height": 180,
                "clip": True,
                "fill": {"type": "image", "url": "assets/ui/card_crop_angel.png", "mode": "fill"}
            },
            # 垂直等级栏
            {
                "id": "STATE_DECOR_PANEL",
                "type": "frame",
                "x": 365,
                "y": 0,
                "width": 60,
                "height": 180,
                "fill": {"type": "color", "color": "#252930"},
                "children": [
                    {"id": "LV_LABEL", "type": "text", "x": 0, "y": 25, "width": 60, "textAlign": "center", "content": "LV", "fontFamily": "Bahnschrift", "fontSize": 12, "fill": "#8D8D8D"},
                    {"id": "OPERATOR_LEVEL", "type": "text", "x": 0, "y": 42, "width": 60, "textAlign": "center", "content": "90", "fontFamily": "Bahnschrift", "fontSize": 30, "fontWeight": "bold", "fill": "#FFFFFF"}
                ]
            },
            # 精英度
            {"id": "ELITE_0", "type": "frame", "x": 378, "y": 115, "width": 34, "height": 34, "fill": {"type": "image", "url": "assets/ui/elite_0.png", "mode": "fit"}},
            {"id": "ELITE_1", "type": "frame", "x": 378, "y": 115, "width": 34, "height": 34, "fill": {"type": "image", "url": "assets/ui/elite_1.png", "mode": "fit"}},
            {"id": "ELITE_2", "type": "frame", "x": 378, "y": 115, "width": 34, "height": 34, "fill": {"type": "image", "url": "assets/ui/elite_2.png", "mode": "fit"}},
            # 潜能徽章 (位于右侧切角顶端)
            {"id": "POTENTIAL_1", "type": "frame", "x": 426, "y": 73, "width": 34, "height": 34, "fill": {"type": "image", "url": "assets/ui/potential_1.png", "mode": "fit"}},
            {"id": "POTENTIAL_2", "type": "frame", "x": 426, "y": 73, "width": 34, "height": 34, "fill": {"type": "image", "url": "assets/ui/potential_2.png", "mode": "fit"}},
            {"id": "POTENTIAL_3", "type": "frame", "x": 426, "y": 73, "width": 34, "height": 34, "fill": {"type": "image", "url": "assets/ui/potential_3.png", "mode": "fit"}},
            {"id": "POTENTIAL_4", "type": "frame", "x": 426, "y": 73, "width": 34, "height": 34, "fill": {"type": "image", "url": "assets/ui/potential_4.png", "mode": "fit"}},
            {"id": "POTENTIAL_5", "type": "frame", "x": 426, "y": 73, "width": 34, "height": 34, "fill": {"type": "image", "url": "assets/ui/potential_5.png", "mode": "fit"}},
            {"id": "POTENTIAL_6", "type": "frame", "x": 426, "y": 73, "width": 34, "height": 34, "fill": {"type": "image", "url": "assets/ui/potential_6.png", "mode": "fit"}},
            # 未持有 NO INFO
            {
                "id": "NO_INFO",
                "type": "frame",
                "x": 110,
                "y": 0,
                "width": 315,
                "height": 180,
                "fill": {"type": "color", "color": "#EFF1F4"},
                "children": [
                    {"id": "NO_INFO_TITLE", "type": "text", "x": 0, "y": 75, "width": 315, "textAlign": "center", "content": "- - -  NO INFO  - - -", "fontFamily": "Bahnschrift", "fontSize": 15, "fill": "#8D8D8D"}
                ]
            }
        ]
    }

    # 右侧卡片 (向左指向)
    comp_right = copy.deepcopy(comp_left)
    comp_right["id"] = "comp_player_card_right"
    comp_right["name"] = "PLAYER_CARD_RIGHT"
    comp_right["children"][0]["points"] = [[35, 0], [460, 0], [460, 180], [35, 180], [0, 90]]
    comp_right["children"][1]["x"] = 350
    comp_right["children"][2]["x"] = 95
    comp_right["children"][3]["x"] = 35
    for e in [0, 1, 2]:
        comp_right["children"][4 + e]["x"] = 48
    for p in range(1, 7):
        comp_right["children"][6 + p]["x"] = 0
    comp_right["children"][13]["x"] = 35

    scene = {
        "id": "ROOT_REPORT_SCENE",
        "type": "frame",
        "width": 1920,
        "height": 1080,
        "fill": {"type": "image", "url": "assets/ui/bg_clean.png", "mode": "fill"},
        "children": [
            {
                "id": "HEADER_GROUP",
                "type": "frame",
                "x": 60,
                "y": 45,
                "width": 600,
                "height": 80,
                "children": [
                    {"id": "TITLE_BAR", "type": "text", "x": 0, "y": 0, "content": "ARKNIGHTS OPERATOR REPORT", "fontFamily": "Bahnschrift", "fontSize": 24, "fontWeight": "bold", "fill": "#252930"},
                    {"id": "SUBTITLE_BAR", "type": "text", "x": 0, "y": 32, "content": "明日方舟六星干员报菜名 · 五人战术核验系统 (v1.2 指向性切角卡)", "fontFamily": "Microsoft YaHei", "fontSize": 13, "fill": "#0098DC"}
                ]
            },
            {"id": "OPERATOR_FULL_ART", "type": "frame", "x": 0, "y": 0, "width": 1920, "height": 1080, "fill": {"type": "image", "url": "assets/operators/char_103_angel/full.png", "mode": "fill"}},
            {"id": "P1", "type": "ref", "ref": "comp_player_card_left", "x": 40, "y": 170},
            {"id": "P2", "type": "ref", "ref": "comp_player_card_left", "x": 40, "y": 440},
            {"id": "P3", "type": "ref", "ref": "comp_player_card_left", "x": 40, "y": 710},
            {"id": "P4", "type": "ref", "ref": "comp_player_card_right", "x": 1420, "y": 290},
            {"id": "P5", "type": "ref", "ref": "comp_player_card_right", "x": 1420, "y": 560}
        ]
    }
    doc["children"] = [comp_left, comp_right, scene]
    path = os.path.join(ITER_DIR, "v2_chevron_geometry.pen")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=2, ensure_ascii=False)
    return path

# =============================================================
# Iteration 3 (v1.3): 3-Tier Information Hierarchy & Industrial NO INFO
# =============================================================
def generate_iteration_3():
    path_v2 = os.path.join(ITER_DIR, "v2_chevron_geometry.pen")
    with open(path_v2, "r", encoding="utf-8") as f:
        doc = json.load(f)

    for comp in doc["children"][:2]:
        # 等级栏加粗、深炭黑背景、黄色高亮数字
        state_panel = comp["children"][3]
        state_panel["fill"] = {"type": "color", "color": "#1A1D24"}
        state_panel["children"][1]["fill"] = "#FFD800"

        # 博士信息降权
        doc_container = comp["children"][1]
        doc_container["children"].append({
            "id": "ARCHIVE_CODE",
            "type": "text",
            "x": 10,
            "y": 158,
            "width": 90,
            "textAlign": "center",
            "content": "RHODES-DOC",
            "fontFamily": "Bahnschrift",
            "fontSize": 9,
            "fill": "#5A6578"
        })

        # NO INFO 工业警示风格
        no_info = comp["children"][-1]
        no_info["fill"] = {"type": "color", "color": "#E5E7EB"}
        no_info["children"] = [
            {"id": "NO_INFO_TITLE", "type": "text", "x": 0, "y": 68, "width": 315, "textAlign": "center", "content": "/// NO DATA // NOT ACQUIRED ///", "fontFamily": "Bahnschrift", "fontSize": 13, "fontWeight": "bold", "fill": "#4B5563"},
            {"id": "NO_INFO_SUB", "type": "text", "x": 0, "y": 92, "width": 315, "textAlign": "center", "content": "档案数据库暂无当前干员调用凭证", "fontFamily": "Microsoft YaHei", "fontSize": 11, "fill": "#9CA3AF"}
        ]

    doc["children"][2]["children"][0]["children"][1]["content"] = "明日方舟六星干员报菜名 · 五人战术核验系统 (v1.3 三层信息动线)"

    path = os.path.join(ITER_DIR, "v3_three_tier_hierarchy.pen")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=2, ensure_ascii=False)
    return path

# =============================================================
# Iteration 4 (v1.4): Asymmetric Balance & Rhodes Island Dossier
# =============================================================
def generate_iteration_4():
    path_v3 = os.path.join(ITER_DIR, "v3_three_tier_hierarchy.pen")
    with open(path_v3, "r", encoding="utf-8") as f:
        doc = json.load(f)

    scene = doc["children"][2]
    # 右下角建立 RHODES ISLAND OPERATOR DOSSIER 主档案模块
    operator_dossier = {
        "id": "OPERATOR_DOSSIER_PANEL",
        "type": "frame",
        "x": 1420,
        "y": 760,
        "width": 460,
        "height": 260,
        "fill": {"type": "color", "color": "#1A1D23F2"},
        "stroke": {"type": "color", "color": "#0098DC"},
        "strokeWidth": 2,
        "shadow": {"color": "#00000088", "offsetX": 6, "offsetY": 6},
        "children": [
            # 亮黄警示色边条
            {"id": "ACCENT_BAR", "type": "frame", "x": 0, "y": 0, "width": 8, "height": 260, "fill": {"type": "color", "color": "#FFD800"}},
            {"id": "TAG_HEADER", "type": "text", "x": 25, "y": 20, "content": "// RHODES ISLAND PERSONNEL DOSSIER // 战术干员主档", "fontFamily": "Microsoft YaHei", "fontSize": 12, "fill": "#0098DC"},
            {"id": "OP_CN_NAME", "type": "text", "x": 25, "y": 48, "content": "能 天 使", "fontFamily": "Microsoft YaHei", "fontSize": 34, "fontWeight": "bold", "fill": "#FFFFFF"},
            {"id": "OP_EN_NAME", "type": "text", "x": 25, "y": 96, "content": "EXUSIAI", "fontFamily": "Bahnschrift", "fontSize": 20, "fontWeight": "bold", "fill": "#CBD5E1"},
            {"id": "DIVIDER_LINE", "type": "line", "x": 25, "y": 130, "width": 400, "height": 0, "stroke": {"color": "#334155"}, "strokeWidth": 1},
            {"id": "CLASS_TAG", "type": "text", "x": 25, "y": 148, "content": "CLASS // SNIPER (速射狙击)", "fontFamily": "Microsoft YaHei", "fontSize": 13, "fill": "#94A3B8"},
            {"id": "RARITY_TAG", "type": "text", "x": 25, "y": 172, "content": "RARITY // ★★★★★★", "fontFamily": "Microsoft YaHei", "fontSize": 15, "fill": "#FFD800"},
            {"id": "REG_CODE", "type": "text", "x": 25, "y": 208, "content": "RHODES ISLAND ARCHIVE · NO. 103/138", "fontFamily": "Bahnschrift", "fontSize": 11, "fill": "#64748B"}
        ]
    }
    # 背后超大半透明 Codename
    bg_watermark = {
        "id": "BG_CODENAME_WATERMARK",
        "type": "text",
        "x": 650,
        "y": 400,
        "content": "EXUSIAI",
        "fontFamily": "Bahnschrift",
        "fontSize": 180,
        "fontWeight": "bold",
        "fill": "#00000010"
    }

    scene["children"].insert(1, bg_watermark)
    scene["children"].append(operator_dossier)
    scene["children"][0]["children"][1]["content"] = "明日方舟六星干员报菜名 · 五人战术核验系统 (v1.4 档案右下平衡)"

    path = os.path.join(ITER_DIR, "v4_rhodes_dossier.pen")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=2, ensure_ascii=False)
    return path

# =============================================================
# Iteration 5 (v1.5): Master Polishing (微质感、十字标、终极正统排版)
# =============================================================
def generate_iteration_5():
    path_v4 = os.path.join(ITER_DIR, "v4_rhodes_dossier.pen")
    with open(path_v4, "r", encoding="utf-8") as f:
        doc = json.load(f)

    scene = doc["children"][2]
    # 添加四个角的十字准星与档案系统标牌
    crosshairs = [
        {"id": "CH_TL", "type": "text", "x": 40, "y": 22, "content": "[ + ]  RHODES-OS VER 5.2.0  //  TAC-VERIFY", "fontFamily": "Bahnschrift", "fontSize": 11, "fill": "#64748B"},
        {"id": "CH_TR", "type": "text", "x": 1660, "y": 22, "content": "TACTICAL MONITOR // 24 FPS  [REC]", "fontFamily": "Bahnschrift", "fontSize": 11, "fill": "#64748B"},
        {"id": "CH_BL", "type": "text", "x": 40, "y": 1050, "content": "RESTRICTED ACCESS // FOR DOCTOR EYES ONLY", "fontFamily": "Bahnschrift", "fontSize": 11, "fill": "#64748B"},
        {"id": "CH_BR", "type": "text", "x": 1660, "y": 1050, "content": "SYSTEM STATUS: ACTIVE [OK]", "fontFamily": "Bahnschrift", "fontSize": 11, "fill": "#0098DC"}
    ]
    for ch in crosshairs:
        scene["children"].append(ch)

    scene["children"][0]["children"][1]["content"] = "明日方舟六星干员报菜名 · 五人战术核验系统 (v1.5 终极正统档案排版)"

    path = os.path.join(ITER_DIR, "v5_rhodes_personnel_archive.pen")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=2, ensure_ascii=False)
    return path

def render_all_iterations():
    engine = PenRenderer(base_asset_dir=SHARED_DIR)
    
    iters = [
        ("Iter 1 (去圆角/去发光)", generate_iteration_1(), os.path.join(ITER_DIR, "iter1_structural_purge.png")),
        ("Iter 2 (指向性切角卡面)", generate_iteration_2(), os.path.join(ITER_DIR, "iter2_chevron_geometry.png")),
        ("Iter 3 (三层信息动线)", generate_iteration_3(), os.path.join(ITER_DIR, "iter3_three_tier_hierarchy.png")),
        ("Iter 4 (右下档案视觉平衡)", generate_iteration_4(), os.path.join(ITER_DIR, "iter4_rhodes_dossier.png")),
        ("Iter 5 (终极正统档案终版)", generate_iteration_5(), os.path.join(ITER_DIR, "iter5_rhodes_archive_exusiai.png"))
    ]

    rendered_images = []
    print("\n--- 开始执行 5 次连续迭代渲染 ---")
    for name, pen_file, out_png in iters:
        print(f"  -> 渲染 {name}: {pen_file} ...")
        engine.render_scene(pen_file, MANIFEST_A, output_png_path=out_png)
        rendered_images.append((name, out_png))

    # 另外为 Iteration 5 渲染场景 B (推进之王)，验证跨场景参数化表现
    out_siege = os.path.join(ITER_DIR, "iter5_rhodes_archive_siege.png")
    print(f"  -> 渲染 Iter 5 变体场景 (推进之王): {out_siege} ...")
    engine.render_scene(iters[-1][1], MANIFEST_B, output_png_path=out_siege)

    # 替换当前主母版 report_5p_master.pen
    master_dest = os.path.join(BASE_DIR, "experiments", "pen_renderer", "report_5p_master.pen")
    import shutil
    shutil.copy2(iters[-1][1], master_dest)
    print(f"成功将 Iteration 5 写入主母版: {master_dest}")

    # 生成 5 次设计演进全景对比图 (5-Panel Visual Contact Sheet)
    generate_evolution_contact_sheet(rendered_images)

def generate_evolution_contact_sheet(rendered_list):
    thumb_w, thumb_h = 576, 324
    sheet = Image.new('RGBA', (thumb_w * 5, thumb_h + 70), (15, 18, 24, 255))
    draw = ImageDraw.Draw(sheet)

    try:
        font_title = ImageFont.truetype(r"C:\Windows\Fonts\bahnschrift.ttf", 24)
        font_sub = ImageFont.truetype(r"C:\Windows\Fonts\msyh.ttc", 15)
        # 使用微软雅黑绘制包含中文字符的标牌，避免方块乱码
        font_badge = ImageFont.truetype(r"C:\Windows\Fonts\msyh.ttc", 13)
    except Exception:
        font_title = font_sub = font_badge = ImageFont.load_default()

    draw.rectangle([(0, 0), (thumb_w * 5, 70)], fill=(10, 12, 16, 255))
    draw.text((30, 15), "ARKNIGHTS RENDERER · 5-STEP DESIGN EVOLUTION (RHODES PERSONNEL ARCHIVE)", fill=(226, 232, 240), font=font_title)
    draw.text((30, 44), "从泛化赛博 HUD 到《明日方舟》正统硬边档案工业排版的 5 次渐进迭代", fill=(0, 152, 220), font=font_sub)

    colors = [
        (100, 116, 139),
        (0, 152, 220),
        (255, 216, 0),
        (76, 201, 140),
        (239, 71, 111)
    ]

    for idx, (name, img_path) in enumerate(rendered_list):
        im = Image.open(img_path).convert('RGBA')
        thumb = im.resize((thumb_w, thumb_h), Image.Resampling.LANCZOS)
        x_pos = idx * thumb_w
        sheet.paste(thumb, (x_pos, 70))

        # 绘制标牌
        draw.rectangle([(x_pos + 10, 80), (x_pos + thumb_w - 10, 112)], fill=(10, 14, 20, 220), outline=colors[idx], width=1)
        draw.text((x_pos + 20, 88), f"STEP {idx+1}: {name}", fill=(255, 255, 255), font=font_badge)

        if idx > 0:
            draw.line([(x_pos, 70), (x_pos, thumb_h + 70)], fill=(40, 45, 55), width=2)

    out_sheet = os.path.join(REPORTS_DIR, "pen_design_evolution_5_steps.png")
    sheet.save(out_sheet, "PNG")
    print(f"\n成功生成 5 次设计演进全景对比图: {out_sheet}")

if __name__ == "__main__":
    render_all_iterations()
