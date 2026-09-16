"""
MAA (MaaAssistantArknights) 仓库采集与识别模块
唯一正式生产实现：
- OperBoxCollector
- OperBoxAnalyzer
"""

from .operbox_analyzer import OperBoxAnalyzer
from .operbox_collector import OperBoxCollector

__all__ = [
    "OperBoxAnalyzer",
    "OperBoxCollector",
]
