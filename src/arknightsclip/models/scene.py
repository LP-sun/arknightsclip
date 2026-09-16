"""
分层渲染场景清单与槽位状态数据模型
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional

@dataclass
class PlayerSlotState:
    own: bool
    elite: int = 0
    level: int = 1
    potential: int = 1
    no_info: bool = False
    card_asset_path: Optional[str] = None

    def __post_init__(self):
        # 自动满足互斥条件
        if not self.own:
            self.no_info = True
            self.card_asset_path = None

    def validate(self) -> bool:
        if self.own:
            if self.no_info:
                return False
            if not (0 <= self.elite <= 2):
                return False
            if not (1 <= self.potential <= 6):
                return False
            if not (1 <= self.level <= 90):
                return False
        else:
            if not self.no_info:
                return False
            if self.card_asset_path is not None:
                return False
        return True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "own": self.own,
            "elite": self.elite,
            "level": self.level,
            "potential": self.potential,
            "no_info": self.no_info,
            "card_asset_path": self.card_asset_path,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PlayerSlotState":
        return cls(
            own=data.get("own", True),
            elite=data.get("elite", 0),
            level=data.get("level", 1),
            potential=data.get("potential", 1),
            no_info=data.get("no_info", not data.get("own", True)),
            card_asset_path=data.get("card_asset_path"),
        )

@dataclass
class SceneManifest:
    operator_id: str
    operator_name: str
    rarity: int = 6
    profession: str = ""
    full_art_path: str = ""
    players: Dict[str, PlayerSlotState] = field(default_factory=dict) # P1..P5 -> PlayerSlotState

    def validate(self) -> bool:
        """检验整个场景清单的完整性与各玩家状态合法性"""
        if not self.operator_id or not self.operator_name:
            return False
        for p_id, slot in self.players.items():
            if not slot.validate():
                return False
        return True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "operator_id": self.operator_id,
            "operator_name": self.operator_name,
            "rarity": self.rarity,
            "profession": self.profession,
            "full_art_path": self.full_art_path,
            "players": {p_id: slot.to_dict() for p_id, slot in self.players.items()},
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SceneManifest":
        players = {}
        for p_id, s_dict in data.get("players", {}).items():
            players[p_id] = PlayerSlotState.from_dict(s_dict)
        return cls(
            operator_id=data["operator_id"],
            operator_name=data["operator_name"],
            rarity=data.get("rarity", 6),
            profession=data.get("profession", ""),
            full_art_path=data.get("full_art_path", ""),
            players=players,
        )
