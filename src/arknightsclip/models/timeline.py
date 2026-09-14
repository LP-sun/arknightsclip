"""
剪辑序列与时间线编排数据模型
严格解耦音乐节拍结构 (Sequence) 与画面练度内容 (Scene)
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any

@dataclass
class SequenceEntry:
    operator_id: str
    start_frame: int
    duration_frames: int
    transition: str = "hard_cut"
    clip_index: int = 0

    @property
    def end_frame(self) -> int:
        return self.start_frame + self.duration_frames

    def to_dict(self) -> Dict[str, Any]:
        return {
            "operator_id": self.operator_id,
            "start_frame": self.start_frame,
            "duration_frames": self.duration_frames,
            "transition": self.transition,
            "clip_index": self.clip_index,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SequenceEntry":
        return cls(
            operator_id=data["operator_id"],
            start_frame=data["start_frame"],
            duration_frames=data["duration_frames"],
            transition=data.get("transition", "hard_cut"),
            clip_index=data.get("clip_index", 0),
        )

@dataclass
class TimelineSequence:
    fps: float = 24.0
    entries: List[SequenceEntry] = field(default_factory=list)

    @property
    def total_frames(self) -> int:
        """动态求和总帧数，彻底告别写死数字"""
        if not self.entries:
            return 0
        return sum(e.duration_frames for e in self.entries)

    @property
    def duration_seconds(self) -> float:
        return self.total_frames / self.fps

    def to_dict(self) -> Dict[str, Any]:
        return {
            "fps": self.fps,
            "total_frames": self.total_frames,
            "duration_seconds": round(self.duration_seconds, 3),
            "entries": [e.to_dict() for e in self.entries],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TimelineSequence":
        entries = [SequenceEntry.from_dict(e) for e in data.get("entries", [])]
        return cls(fps=data.get("fps", 24.0), entries=entries)
