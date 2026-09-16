import json
import os

def generate_5p_master_pen():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    template_path = os.path.join(base_dir, 'templates', 'report_5p_master.pen')
    os.makedirs(os.path.dirname(template_path), exist_ok=True)

    # Component 定义: 440 x 220
    # 左侧是博士战术信息卡 (宽 130)，右侧是干员卡片展示窗 (宽 290)
    card_component = {
        "id": "comp_player_card",
        "name": "PLAYER_CARD_COMPONENT",
        "type": "frame",
        "reusable": True,
        "width": 440,
        "height": 220,
        "cornerRadius": 10,
        "fill": {
            "type": "color",
            "color": "#121417D9"
        },
        "stroke": {
            "type": "color",
            "color": "#3A444ECC"
        },
        "strokeWidth": 1.5,
        "clip": True,
        "children": [
            # 1. DOCTOR_CONTAINER 博士信息栏 (宽 130)
            {
                "id": "DOCTOR_CONTAINER",
                "name": "DOCTOR_CONTAINER",
                "type": "frame",
                "x": 10,
                "y": 10,
                "width": 125,
                "height": 200,
                "layout": "vertical",
                "gap": 8,
                "alignItems": "center",
                "children": [
                    # 头像容器 (圆形，带发光边框)
                    {
                        "id": "DOCTOR_AVATAR",
                        "name": "DOCTOR_AVATAR",
                        "type": "frame",
                        "width": 76,
                        "height": 76,
                        "cornerRadius": 38,
                        "clip": True,
                        "stroke": {
                            "type": "color",
                            "color": "#00B4D8CC"
                        },
                        "strokeWidth": 2,
                        "fill": {
                            "type": "image",
                            "url": "./assets/players/P1.png",
                            "mode": "fill"
                        }
                    },
                    # 博士等级徽环文本
                    {
                        "id": "DOCTOR_LEVEL",
                        "name": "DOCTOR_LEVEL",
                        "type": "text",
                        "content": "LV. 120",
                        "fontFamily": "Microsoft YaHei",
                        "fontSize": 14,
                        "fontWeight": "bold",
                        "fill": "#00F5D4",
                        "textAlign": "center"
                    },
                    # 博士代号名称
                    {
                        "id": "DOCTOR_NAME",
                        "name": "DOCTOR_NAME",
                        "type": "text",
                        "content": "Dr.Doctor",
                        "fontFamily": "Microsoft YaHei",
                        "fontSize": 14,
                        "fontWeight": "bold",
                        "fill": "#E2E8F0",
                        "textAlign": "center"
                    }
                ]
            },
            # 2. 分割线
            {
                "id": "DIVIDER",
                "name": "DIVIDER",
                "type": "rectangle",
                "x": 140,
                "y": 15,
                "width": 1,
                "height": 190,
                "fill": {
                    "type": "color",
                    "color": "#334155"
                }
            },
            # 3. OPERATOR_STATE_CONTAINER 干员卡面与练度展示区 (x: 150, 宽 280)
            {
                "id": "OPERATOR_STATE_CONTAINER",
                "name": "OPERATOR_STATE_CONTAINER",
                "type": "frame",
                "x": 150,
                "y": 10,
                "width": 280,
                "height": 200,
                "clip": True,
                "children": [
                    # A. 已持有态干员卡片
                    {
                        "id": "OPERATOR_CARD",
                        "name": "OPERATOR_CARD",
                        "type": "frame",
                        "x": 0,
                        "y": 0,
                        "width": 280,
                        "height": 200,
                        "cornerRadius": 6,
                        "clip": True,
                        "fill": {
                            "type": "image",
                            "url": "./assets/ui/card_crop_angel.png",
                            "mode": "fill"
                        },
                        "enabled": True
                    },
                    # B. 等级与角标半透明装饰底衬
                    {
                        "id": "STATE_DECOR_PANEL",
                        "name": "STATE_DECOR_PANEL",
                        "type": "rectangle",
                        "x": 0,
                        "y": 140,
                        "width": 280,
                        "height": 60,
                        "fill": {
                            "type": "gradient",
                            "gradientType": "linear",
                            "rotation": 0,
                            "colors": [
                                {"color": "#00000000", "position": 0},
                                {"color": "#05070AE6", "position": 0.5},
                                {"color": "#000000FA", "position": 1}
                            ]
                        },
                        "enabled": True
                    },
                    # C. 等级数字
                    {
                        "id": "LV_LABEL",
                        "name": "LV_LABEL",
                        "type": "text",
                        "x": 12,
                        "y": 166,
                        "content": "LV",
                        "fontFamily": "Impact",
                        "fontSize": 14,
                        "fill": "#00F5D4"
                    },
                    {
                        "id": "OPERATOR_LEVEL",
                        "name": "OPERATOR_LEVEL",
                        "type": "text",
                        "x": 36,
                        "y": 152,
                        "content": "90",
                        "fontFamily": "Impact",
                        "fontSize": 32,
                        "fontWeight": "bold",
                        "fill": "#FFFFFF",
                        "enabled": True
                    },
                    # D. 精英度徽章 (互斥 0/1/2)
                    {
                        "id": "ELITE_0",
                        "name": "ELITE_0",
                        "type": "frame",
                        "x": 160,
                        "y": 155,
                        "width": 36,
                        "height": 36,
                        "fill": {"type": "image", "url": "./assets/ui/elite_0.png", "mode": "fit"},
                        "enabled": False
                    },
                    {
                        "id": "ELITE_1",
                        "name": "ELITE_1",
                        "type": "frame",
                        "x": 160,
                        "y": 155,
                        "width": 36,
                        "height": 36,
                        "fill": {"type": "image", "url": "./assets/ui/elite_1.png", "mode": "fit"},
                        "enabled": False
                    },
                    {
                        "id": "ELITE_2",
                        "name": "ELITE_2",
                        "type": "frame",
                        "x": 160,
                        "y": 155,
                        "width": 36,
                        "height": 36,
                        "fill": {"type": "image", "url": "./assets/ui/elite_2.png", "mode": "fit"},
                        "enabled": True
                    },
                    # E. 潜能徽章 (互斥 1~6)
                    {
                        "id": "POTENTIAL_1",
                        "name": "POTENTIAL_1",
                        "type": "frame",
                        "x": 220,
                        "y": 155,
                        "width": 36,
                        "height": 36,
                        "fill": {"type": "image", "url": "./assets/ui/potential_1.png", "mode": "fit"},
                        "enabled": False
                    },
                    {
                        "id": "POTENTIAL_2",
                        "name": "POTENTIAL_2",
                        "type": "frame",
                        "x": 220,
                        "y": 155,
                        "width": 36,
                        "height": 36,
                        "fill": {"type": "image", "url": "./assets/ui/potential_2.png", "mode": "fit"},
                        "enabled": False
                    },
                    {
                        "id": "POTENTIAL_3",
                        "name": "POTENTIAL_3",
                        "type": "frame",
                        "x": 220,
                        "y": 155,
                        "width": 36,
                        "height": 36,
                        "fill": {"type": "image", "url": "./assets/ui/potential_3.png", "mode": "fit"},
                        "enabled": False
                    },
                    {
                        "id": "POTENTIAL_4",
                        "name": "POTENTIAL_4",
                        "type": "frame",
                        "x": 220,
                        "y": 155,
                        "width": 36,
                        "height": 36,
                        "fill": {"type": "image", "url": "./assets/ui/potential_4.png", "mode": "fit"},
                        "enabled": False
                    },
                    {
                        "id": "POTENTIAL_5",
                        "name": "POTENTIAL_5",
                        "type": "frame",
                        "x": 220,
                        "y": 155,
                        "width": 36,
                        "height": 36,
                        "fill": {"type": "image", "url": "./assets/ui/potential_5.png", "mode": "fit"},
                        "enabled": False
                    },
                    {
                        "id": "POTENTIAL_6",
                        "name": "POTENTIAL_6",
                        "type": "frame",
                        "x": 220,
                        "y": 155,
                        "width": 36,
                        "height": 36,
                        "fill": {"type": "image", "url": "./assets/ui/potential_6.png", "mode": "fit"},
                        "enabled": True
                    },
                    # F. 未持有 NO INFO 磨砂暗底面板
                    {
                        "id": "NO_INFO",
                        "name": "NO_INFO",
                        "type": "frame",
                        "x": 0,
                        "y": 0,
                        "width": 280,
                        "height": 200,
                        "cornerRadius": 6,
                        "fill": {
                            "type": "color",
                            "color": "#181B20FA"
                        },
                        "stroke": {
                            "type": "color",
                            "color": "#475569"
                        },
                        "strokeWidth": 1,
                        "layout": "vertical",
                        "justifyContent": "center",
                        "alignItems": "center",
                        "enabled": False,
                        "children": [
                            {
                                "id": "NO_INFO_TEXT",
                                "name": "NO_INFO_TEXT",
                                "type": "text",
                                "content": "- - -  NO INFO  - - -",
                                "fontFamily": "Impact",
                                "fontSize": 18,
                                "fill": "#64748B"
                            },
                            {
                                "id": "NO_INFO_SUB",
                                "name": "NO_INFO_SUB",
                                "type": "text",
                                "content": "未 获 得 干 员",
                                "fontFamily": "Microsoft YaHei",
                                "fontSize": 12,
                                "fill": "#475569"
                            }
                        ]
                    }
                ]
            }
        ]
    }

    # 根场景 ROOT_REPORT_SCENE
    scene = {
        "id": "ROOT_REPORT_SCENE",
        "name": "ROOT_REPORT_SCENE",
        "type": "frame",
        "x": 0,
        "y": 0,
        "width": 1920,
        "height": 1080,
        "clip": True,
        "fill": {
            "type": "image",
            "url": "./assets/ui/bg_clean.png",
            "mode": "fill"
        },
        "children": [
            # 顶部战术标题装饰栏
            {
                "id": "TOP_BAR",
                "name": "TOP_BAR",
                "type": "frame",
                "x": 40,
                "y": 30,
                "width": 1840,
                "height": 60,
                "children": [
                    {
                        "id": "PROJECT_TITLE",
                        "name": "PROJECT_TITLE",
                        "type": "text",
                        "content": "RHODES ISLAND // OPERATOR REGISTRY REPORT",
                        "fontFamily": "Impact",
                        "fontSize": 26,
                        "fill": "#E2E8F0"
                    },
                    {
                        "id": "PROJECT_SUBTITLE",
                        "name": "PROJECT_SUBTITLE",
                        "type": "text",
                        "x": 0,
                        "y": 34,
                        "content": "明日方舟六星干员报菜名 · 五人战术核验系统",
                        "fontFamily": "Microsoft YaHei",
                        "fontSize": 13,
                        "fill": "#00B4D8"
                    }
                ]
            },
            # 中央全画幅立绘区域
            {
                "id": "OPERATOR_FULL_ART",
                "name": "OPERATOR_FULL_ART",
                "type": "frame",
                "x": 0,
                "y": 0,
                "width": 1920,
                "height": 1080,
                "clip": True,
                "fill": {
                    "type": "image",
                    "url": "./assets/operators/char_103_angel/full.png",
                    "mode": "fill"
                }
            },
            # 五位玩家 Instance 节点 (左 3 右 2 完美平衡)
            # P1 (x: 40, y: 150)
            {
                "id": "P1",
                "name": "P1",
                "type": "ref",
                "ref": "comp_player_card",
                "x": 40,
                "y": 150,
                "descendants": {}
            },
            # P2 (x: 40, y: 440)
            {
                "id": "P2",
                "name": "P2",
                "type": "ref",
                "ref": "comp_player_card",
                "x": 40,
                "y": 440,
                "descendants": {}
            },
            # P3 (x: 40, y: 730)
            {
                "id": "P3",
                "name": "P3",
                "type": "ref",
                "ref": "comp_player_card",
                "x": 40,
                "y": 730,
                "descendants": {}
            },
            # P4 (x: 1440, y: 295) - 垂直居中呼吸感
            {
                "id": "P4",
                "name": "P4",
                "type": "ref",
                "ref": "comp_player_card",
                "x": 1440,
                "y": 295,
                "descendants": {}
            },
            # P5 (x: 1440, y: 585) - 垂直居中呼吸感
            {
                "id": "P5",
                "name": "P5",
                "type": "ref",
                "ref": "comp_player_card",
                "x": 1440,
                "y": 585,
                "descendants": {}
            }
        ]
    }

    doc = {
        "version": "2.17",
        "variables": {},
        "themes": {},
        "children": [
            card_component,
            scene
        ]
    }

    with open(template_path, 'w', encoding='utf-8') as f:
        json.dump(doc, f, indent=2, ensure_ascii=False)

    print(f"成功生成原生 .pen 母版模板: {template_path}")
    print(f"  - 包含单一通用组件: {card_component['id']} (PLAYER_CARD_COMPONENT)")
    print(f"  - 包含根场景: {scene['id']} (1920x1080)")
    print(f"  - 5 个实例槽位: P1, P2, P3, P4, P5")

if __name__ == '__main__':
    generate_5p_master_pen()
