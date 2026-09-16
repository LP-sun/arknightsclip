"""
干员基础定义与练度状态数据模型
"""

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Any
from enum import Enum

class RecognitionMethod(str, Enum):
    MAACORE = "maacore"
    TEMPLATE = "template"
    OCR = "ocr"
    MANUAL = "manual"
    FIXTURE = "fixture"

@dataclass
class ConfidenceScore:
    value: Any
    confidence: float
    method: str

@dataclass
class OperatorRegistryEntry:
    char_id: str
    canonical_name_zh: str
    rarity: int
    profession: str
    release_order: int = 0
    name_en: str = ""
    aliases: List[str] = field(default_factory=list)

    def matches(self, query: str) -> bool:
        """检查名称或别名是否匹配"""
        q = query.strip()
        if q == self.canonical_name_zh or q == self.char_id or q == self.name_en:
            return True
        for a in self.aliases:
            if q == a:
                return True
        return False

@dataclass
class OperatorState:
    char_id: str
    name: str
    own: bool = True
    elite: int = 0         # 0, 1, 2
    level: int = 1         # 1 ~ 90
    potential: int = 1     # 1 ~ 6
    rarity: int = 6
    confidence: Dict[str, ConfidenceScore] = field(default_factory=dict)
    source: str = "maacore"
    needs_review: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "char_id": self.char_id,
            "name": self.name,
            "own": self.own,
            "elite": self.elite,
            "level": self.level,
            "potential": self.potential,
            "rarity": self.rarity,
            "confidence": {
                k: {"value": v.value, "confidence": v.confidence, "method": v.method}
                for k, v in self.confidence.items()
            },
            "source": self.source,
            "needs_review": self.needs_review,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "OperatorState":
        conf_dict = {}
        for k, v in data.get("confidence", {}).items():
            if isinstance(v, dict):
                conf_dict[k] = ConfidenceScore(
                    value=v.get("value"),
                    confidence=v.get("confidence", 1.0),
                    method=v.get("method", "unknown"),
                )
            else:
                conf_dict[k] = ConfidenceScore(value=v, confidence=1.0, method="unknown")

        return cls(
            char_id=data["char_id"],
            name=data["name"],
            own=data.get("own", True),
            elite=data.get("elite", 0),
            level=data.get("level", 1),
            potential=data.get("potential", 1),
            rarity=data.get("rarity", 6),
            confidence=conf_dict,
            source=data.get("source", "maacore"),
            needs_review=data.get("needs_review", False),
        )
