"""
MAA 数据采集适配器抽象基类
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any
from ..models.operator import OperatorState

class MaaAcquisitionAdapter(ABC):
    @abstractmethod
    def is_available(self) -> bool:
        """检查当前适配器环境是否就绪"""
        pass

    @abstractmethod
    def collect_operators(self, max_pages: int = 5) -> List[OperatorState]:
        """采集干员数据列表"""
        pass
