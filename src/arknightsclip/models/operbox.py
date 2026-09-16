"""
OperBox 扫描会话与素材 Provenance 数据模型
"""
import time
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Any, Tuple
from pathlib import Path

@dataclass
class CardROI:
    x: int
    y: int
    width: int
    height: int
    source_width: int = 1920
    source_height: int = 1080

    def to_list(self) -> List[int]:
        return [self.x, self.y, self.width, self.height]

    @classmethod
    def from_list(cls, lst: List[int], sw: int = 1920, sh: int = 1080) -> 'CardROI':
        return cls(x=lst[0], y=lst[1], width=lst[2], height=lst[3], source_width=sw, source_height=sh)

@dataclass
class CardProvenance:
    char_id: str
    name: str
    scan_id: str
    player_id: str
    source_page: str
    page_index: int
    card_index: int
    roi: List[int]
    capture_timestamp: str
    recognition_method: str = 'MaaCore OperBoxImageAnalyzer'
    recognition_confidence: Optional[float] = None
    candidate_count: int = 1
    selected_reason: str = 'best_crop'

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> 'CardProvenance':
        return cls(**d)

@dataclass
class CardCropCandidate:
    char_id: str
    name: str
    page_index: int
    card_index: int
    source_page: str
    roi: CardROI
    quality_score: float
    crop_image: Any = None
    is_edge: bool = False
    rejection_reason: Optional[str] = None

@dataclass
class OperBoxScanSession:
    scan_id: str
    player_id: str
    start_time: float = field(default_factory=time.time)
    pages_captured: int = 0
    operators_found: int = 0
    card_assets_captured: int = 0
    missing_card_assets: List[str] = field(default_factory=list)
    status: str = 'running'

    def to_summary(self) -> Dict[str, Any]:
        return {
            'scan_id': self.scan_id,
            'player_id': self.player_id,
            'start_time': self.start_time,
            'pages_captured': self.pages_captured,
            'operators_found': self.operators_found,
            'card_assets_captured': self.card_assets_captured,
            'missing_card_assets': self.missing_card_assets,
            'status': self.status,
        }
