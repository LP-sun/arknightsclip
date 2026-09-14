from .adapter import MaaAcquisitionAdapter
from .maacore_client import MaaCoreAdapter
from .fallback_recognizer import FallbackOperBoxRecognizer
from .collector import PlayerCollector

__all__ = [
    "MaaAcquisitionAdapter",
    "MaaCoreAdapter",
    "FallbackOperBoxRecognizer",
    "PlayerCollector",
]
