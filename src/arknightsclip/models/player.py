"""
玩家配置文件与结构化干员库数据集模型
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from .operator import OperatorState

@dataclass
class PlayerProfile:
    id: str
    display_name: str
    doctor_level: int = 120
    avatar: str = ""
    uid: Optional[str] = None

@dataclass
class PlayerDataSet:
    player_id: str
    profile: PlayerProfile
    operators: Dict[str, OperatorState] = field(default_factory=dict) # char_id -> OperatorState
    capture_metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "player_id": self.player_id,
            "profile": {
                "id": self.profile.id,
                "display_name": self.profile.display_name,
                "doctor_level": self.profile.doctor_level,
                "avatar": self.profile.avatar,
                "uid": self.profile.uid,
            },
            "operators": {
                char_id: op.to_dict() for char_id, op in self.operators.items()
            },
            "capture_metadata": self.capture_metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PlayerDataSet":
        prof_data = data.get("profile", {})
        prof = PlayerProfile(
            id=prof_data.get("id", data.get("player_id", "P1")),
            display_name=prof_data.get("display_name", "博士"),
            doctor_level=prof_data.get("doctor_level", 120),
            avatar=prof_data.get("avatar", ""),
            uid=prof_data.get("uid"),
        )
        ops = {}
        for char_id, op_dict in data.get("operators", {}).items():
            ops[char_id] = OperatorState.from_dict(op_dict)

        return cls(
            player_id=data["player_id"],
            profile=prof,
            operators=ops,
            capture_metadata=data.get("capture_metadata", {}),
        )

@dataclass
class FivePlayersDataset:
    players: Dict[str, PlayerDataSet] = field(default_factory=dict) # P1..P5 -> PlayerDataSet
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "players": {p_id: p_data.to_dict() for p_id, p_data in self.players.items()},
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FivePlayersDataset":
        players = {}
        for p_id, p_data in data.get("players", {}).items():
            players[p_id] = PlayerDataSet.from_dict(p_data)
        return cls(players=players, metadata=data.get("metadata", {}))
