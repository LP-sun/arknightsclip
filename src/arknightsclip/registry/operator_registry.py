"""
明日方舟干员官方注册表 (Operator Registry)
建立全局唯一的 char_id 映射，支持官方中文名、英文名、常见缩写与别名消歧。

OCR 纠错策略（学习自 MAA ocr_replace 机制）：
  1. 字符级替换表 OCR_CHAR_FIXES：修正 EasyOCR 已知的系统性字形混淆
  2. 冒号后缀截断：「凯尔希:思衡托」→「凯尔希」（皮肤/模组名连读）
  3. Levenshtein 模糊匹配兜底：编辑距离 ≤1 时自动映射最近候选
"""

import json
from pathlib import Path
from typing import Dict, List, Optional
from ..models.operator import OperatorRegistryEntry

# MAA-style OCR 字符级纠错表
# 键=OCR 误读字符，值=正确字符
# 来源：对照 EasyOCR 在方舟仓库界面的已知系统性误读汇总
OCR_CHAR_FIXES: Dict[str, str] = {
    '壬': '王',   # 「推进之壬」→「推进之王」；「魔壬」→「魔王」  (三横→二横，高频混淆)
    '鹗': '鸮',   # 「白面鹗」→「白面鸮」  (形近鸟字旁)
    '祜': '祐',   # 「祜天寺若麦」→「祐天寺若麦」  (礻偏旁内笔画混淆)
    '亳': '毫',   # 「灰亳」→「灰毫」  (少一横形近混淆)
    '·': '·',    # 统一中点（全角·与间隔号·码位不同，归一到 U+00B7）
    ':': '·',    # 半角冒号→中点，处理「维娜:维多利亚」→「维娜·维多利亚」
}

COMMON_ALIASES: Dict[str, List[str]] = {
    # 6星干员核心别名与常用民间简称/同音错别字
    "char_103_angel": ["能天使", "阿能", "Exusiai"],
    "char_112_siege": ["推进之王", "推王", "Siege"],
    "char_134_ifrit": ["伊芙利特", "小火龙", "Ifrit"],
    "char_180_amgoat": ["艾雅法拉", "小羊", "Eyjafjalla"],
    "char_291_aglina": ["安洁莉娜", "安洁丽娜", "洁哥", "Angelina"],
    "char_147_shining": ["闪灵", "Shining"],
    "char_179_cgbird": ["夜莺", "夜莺 psd", "Nightingale"],
    "char_136_hsguma": ["星熊", "Hoshiguma"],
    "char_202_demkni": ["塞雷娅", "赛雷娅", "塞妈", "赛爹", "Saria"],
    "char_172_svrash": ["银灰", "银老板", "SilverAsh"],
    "char_263_skadi": ["斯卡蒂", "蒂蒂", "Skadi"],
    "char_010_chen": ["陈", "老陈", "Ch'en"],
    "char_340_shwaz": ["黑", "Schwarz"],
    "char_188_helage": ["赫拉格", "老爷子", "Hellagur"],
    "char_248_mgllan": ["麦哲伦", "企鹅", "Magallan"],
    "char_213_mostma": ["莫斯提马", "小莫", "Mostima"],
    "char_017_huang": ["煌", "大猫", "Blaze"],
    "char_225_haak": ["阿", "老阿", "Aak", "a"],
    "char_2014_nian": ["年", "Nian"],
    "char_2013_cerber": ["刻俄柏", "刻俄伯", "小刻", "Ceobe"],
    "char_222_bpipe": ["风笛", "Bagpipe"],
    "char_250_phatom": ["傀影", "魁影", "Phantom"],
    "char_400_weedy": ["温蒂", "Weedy"],
    "char_113_cqbw": ["W", "Wpsd"],
    "char_197_poca": ["早露", "Rosa"],
    "char_358_lisa": ["铃兰", "Lisa", "Suzuran"],
    "char_293_thorns": ["棘刺", "Thorns"],
    "char_416_zumama": ["森蚺", "森染", "森然", "Eunectes", "Zumama"],
    "char_350_surtr": ["史尔特尔", "42", "42姐", "Surtr"],
    "char_423_blemsh": ["瑕光", "霞光", "霞光2", "Blemishine"],
    "char_311_mudrok": ["泥岩", "Mudrock"],
    "char_391_rosmon": ["迷迭香", "Rosmontis"],
    "char_264_f12yin": ["山", "Mountain"],
    "char_332_archet": ["空弦", "Archetto"],
    "char_362_saga": ["嵯峨", "Saga"],
    "char_2015_dusk": ["夕", "Dusk"],
    "char_456_ash": ["灰烬", "Ash"],
    "char_472_pasngr": ["异客", "神", "Passenger"],
    "char_1012_skadi2": ["浊心斯卡蒂", "浊心蒂", "红蒂", "浊蒂", "Skadi the Corrupting Heart"],
    "char_474_glady": ["歌蕾蒂娅", "格雷迪娅", "Gladiia"],
    "char_003_kalts": ["凯尔希", "老太婆", "Kal'tsit"],
    "char_426_billro": ["卡涅利安", "卡列涅安", "卡姐", "Carnelian"],
    "char_485_pallas": ["帕拉斯", "Pallas"],
    "char_437_mizuki": ["水月", "水母", "Mizuki"],
    "char_1013_chen2": ["假日威龙陈", "水陈", "Ch'en the Holungday"],
    "char_479_sleach": ["琴柳", "秦柳", "秦柳光", "Saileach"],
    "char_430_fartth": ["远牙", "Fartooth"],
    "char_420_flamtl": ["焰尾", "燕尾", "燕尾娅", "Flametail"],
    "char_1014_nearl2": ["耀骑士临光", "耀光", "异格临光", "Nearl the Radiant Knight"],
    "char_206_gnosis": ["灵知", "灵芝", "Gnosis"],
    "char_322_lmlee": ["老鲤", "老鲤鱼", "老李", "Lee"],
    "char_2023_ling": ["令", "Ling"],
    "char_377_gdglow": ["澄闪", "澄海闪", "粉毛", "Goldenglow"],
    "char_300_phenxi": ["菲亚梅塔", "肥鸭", "菲雅", "苦难陈述者", "Fiammetta"],
    "char_4039_horn": ["号角", "Horn"],
    "char_1023_ghost2": ["归溟幽灵鲨", "归鲨", "幽灵鲨异格", "Specter the Unchained"],
    "char_4042_lumen": ["流明", "刘明", "Lumen"],
    "char_4009_irene": ["艾丽妮", "Irene"],
    "char_4046_ebnhlz": ["黑键", "Ebenholz"],
    # 其他高频 6 星及衍生变体
    "char_427_vigil": ["伺夜", "饲夜", "Vigil"],
    "char_2025_shu": ["黍", "黍姐", "Shu"],
    "char_4132_ascln": ["阿斯卡纶", "阿斯卡伦", "Ascalon"],
    "char_4141_marcil": ["玛露西尔", "玛露希尔", "Marcille"],
    "char_1019_siege2": ["维娜·维多利亚", "维娜维多利亚", "异格推王", "王维娜"],
    "char_1039_thorn2": ["引星棘刺", "隐星棘刺", "异格棘刺"],
    "char_249_mlynh": ["玛恩纳", "叔叔", "Młynar"],
    "char_4055_bgsnow": ["鸿雪", "Pozyomka", "Pozëmka"],
    "char_1020_reed2": ["焰影苇草", "咒愈苇草", "Reed the Flame Shadow"],
    "char_1021_kroos2": ["寒芒克洛丝"],
    "char_1028_texas2": ["缄默德克萨斯", "翼德", "Texas the Omertosa"],
    "char_1029_yato2": ["麒麟R夜刀", "夜刀异格", "夜刀"],
    "char_1030_noirc2": ["火龙S黑角"],
    "char_1031_slchan": ["纯烬艾雅法拉", "提丰羊"],
    "char_1035_wisdel": ["维什戴尔", "Wis'adel"],
}

class OperatorRegistry:
    def __init__(self, registry_file: Optional[Path] = None):
        self._entries: Dict[str, OperatorRegistryEntry] = {} # char_id -> Entry
        self._name_to_id: Dict[str, str] = {}               # canonical_name / alias -> char_id
        if registry_file and registry_file.exists():
            self.load(registry_file)

    def load(self, registry_file: Path):
        with open(registry_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        for d in data.get("operators", []):
            cid = d.get("char_id", "")
            if not cid.startswith("char_"):
                continue
            entry = OperatorRegistryEntry(
                char_id=cid,
                canonical_name_zh=d["canonical_name_zh"],
                rarity=d.get("rarity", 6),
                profession=d.get("profession", ""),
                release_order=d.get("release_order", 0),
                name_en=d.get("name_en", ""),
                aliases=d.get("aliases", []),
            )
            self.register(entry)

        # 载入并合并全局常用民间别名映射
        for cid, alias_list in COMMON_ALIASES.items():
            if cid in self._entries:
                entry = self._entries[cid]
                for alias in alias_list:
                    if alias not in entry.aliases:
                        entry.aliases.append(alias)
                    self._name_to_id[alias] = cid
                    self._name_to_id[alias.lower()] = cid

    def register(self, entry: OperatorRegistryEntry):
        self._entries[entry.char_id] = entry
        self._name_to_id[entry.canonical_name_zh] = entry.char_id
        if entry.name_en:
            self._name_to_id[entry.name_en.lower()] = entry.char_id
        for alias in entry.aliases:
            self._name_to_id[alias] = entry.char_id

    def get_by_id(self, char_id: str) -> Optional[OperatorRegistryEntry]:
        return self._entries.get(char_id)

    def get(self, char_id: str, default: Optional[OperatorRegistryEntry] = None) -> Optional[OperatorRegistryEntry]:
        return self._entries.get(char_id, default)

    def __contains__(self, char_id: str) -> bool:
        return char_id in self._entries

    @staticmethod
    def _ocr_normalize(text: str) -> str:
        """
        MAA-style OCR 前处理：
        1. 移除 OCR 识别可能产生的空格（中文名不含空格）
        2. 字符级替换（字形混淆修正）
        3. 截断第一个中点·之后的内容（皮肤/模组后缀），仅保留干员本名
        """
        # Step 0: 清除所有空格（例如「维娜 .维多利亚」->「维娜.维多利亚」）
        cleaned = text.replace(' ', '')
        # Step 1: 字符级替换（包含 : 与 . → · 的统一）
        if '.' in cleaned and '·' not in cleaned:
            cleaned = cleaned.replace('.', '·')
        normalized = ''.join(OCR_CHAR_FIXES.get(c, c) for c in cleaned)
        return normalized

    @staticmethod
    def _levenshtein(a: str, b: str) -> int:
        """计算两字符串的编辑距离（Levenshtein distance）"""
        if len(a) < len(b):
            return OperatorRegistry._levenshtein(b, a)
        if not b:
            return len(a)
        prev = list(range(len(b) + 1))
        for i, ca in enumerate(a):
            curr = [i + 1]
            for j, cb in enumerate(b):
                curr.append(min(prev[j + 1] + 1, curr[j] + 1, prev[j] + (ca != cb)))
            prev = curr
        return prev[-1]

    def resolve(self, query: str) -> Optional[OperatorRegistryEntry]:
        """
        根据 ID、官方中文名、英文名或别名多维度解析干员。

        解析流程（学习自 MAA ocr_replace + 模糊匹配策略）：
        1. 空值校验保护（严禁空串匹配）
        2. 直接精确匹配（char_id / canonical_name / alias）
        3. OCR 字符纠错后精确匹配（壬→王 / 鹗→鸮 / 祜→祐 / :→· / 清除空格）
        4. 冒号/·后缀截断后匹配（「凯尔希:思衡托」→「凯尔希」）
        5. Levenshtein 编辑距离 ≤1 的模糊匹配兜底（仅限长≥2的词，杜绝单字被误匹配）
        """
        q = query.strip()
        if not q:
            return None

        # --- Step 1: 精确匹配 ---
        if q in self._entries:
            return self._entries[q]
        if q in self._name_to_id:
            return self._entries[self._name_to_id[q]]
        if q.lower() in self._name_to_id:
            return self._entries[self._name_to_id[q.lower()]]
        # 前缀匹配 (例如 '001_能天使' -> '能天使')
        if '_' in q:
            sub = q.split('_', 1)[1]
            if sub in self._name_to_id:
                return self._entries[self._name_to_id[sub]]

        # --- Step 2: OCR 字符纠错后精确匹配 ---
        q_norm = self._ocr_normalize(q)
        if q_norm != q:
            # 2a. 纠错后全串精确匹配（优先）：「凯尔希:思衡托」→「凯尔希·思衡托」→ kalts2
            if q_norm in self._name_to_id:
                return self._entries[self._name_to_id[q_norm]]

        # --- Step 3: 冒号 / 中点后缀截断（仅当纠错全串未命中时）---
        # 用于「纯皮肤/模组后缀连读」的情况，此时截断前缀才有意义
        for sep in (':', '·'):
            if sep in q_norm:
                prefix = q_norm.split(sep)[0].strip()
                if prefix and prefix in self._name_to_id:
                    return self._entries[self._name_to_id[prefix]]
            if sep in q:
                prefix_raw = q.split(sep)[0].strip()
                if prefix_raw and prefix_raw in self._name_to_id:
                    return self._entries[self._name_to_id[prefix_raw]]

        # --- Step 4: Levenshtein 模糊匹配（距离 ≤1，仅限长度>=2的中文官方名，避免单字乱匹配或匹配到俗称别名）---
        candidate_q = q_norm
        if len(candidate_q) >= 2:
            best_entry: Optional[OperatorRegistryEntry] = None
            best_dist = 2
            for cid, entry in self._entries.items():
                name = entry.canonical_name_zh
                if len(name) < 2 or abs(len(name) - len(candidate_q)) > 1:
                    continue
                d = self._levenshtein(candidate_q, name)
                if d < best_dist:
                    best_dist = d
                    best_entry = entry
            if best_entry is not None:
                return best_entry

        return None

    def all_operators(self) -> List[OperatorRegistryEntry]:
        return list(self._entries.values())

    def export(self, target_file: Path):
        data = {
            "version": "1.0",
            "total_operators": len(self._entries),
            "operators": [
                {
                    "char_id": e.char_id,
                    "canonical_name_zh": e.canonical_name_zh,
                    "rarity": e.rarity,
                    "profession": e.profession,
                    "release_order": e.release_order,
                    "name_en": e.name_en,
                    "aliases": e.aliases,
                }
                for e in self._entries.values()
            ],
        }
        target_file.parent.mkdir(parents=True, exist_ok=True)
        with open(target_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

def build_registry_from_battle_data(battle_data_file: Path, target_output: Path) -> OperatorRegistry:
    """从 MAA battle_data.json 编译官方权威干员注册表"""
    with open(battle_data_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    reg = OperatorRegistry()
    chars = data.get("chars", {})
    order = 1
    for cid, cinfo in chars.items():
        name = cinfo.get("name", "").strip()
        prof = cinfo.get("profession", "")
        rarity = cinfo.get("rarity", 0)
        name_en = cinfo.get("name_en", "")

        if not name or prof == "DRONE":
            continue

        aliases = list(COMMON_ALIASES.get(cid, []))
        entry = OperatorRegistryEntry(
            char_id=cid,
            canonical_name_zh=name,
            rarity=rarity,
            profession=prof,
            release_order=order,
            name_en=name_en,
            aliases=aliases,
        )
        reg.register(entry)
        order += 1

    reg.export(target_output)
    return reg
