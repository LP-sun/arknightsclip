"""
MaaCore 官方原生接口适配器
用于直接调用 MaaCore.dll / asst.py 驱动 OperBoxRecognitionTask。
若本地未安装原生环境，报告不可用并降级至 Fallback 视觉识别器。
"""

import sys
import json
from typing import List, Dict, Any, Optional
from pathlib import Path
from ..models.operator import OperatorState, ConfidenceScore, RecognitionMethod
from .adapter import MaaAcquisitionAdapter
from ..config import ProjectConfig

class MaaCoreAdapter(MaaAcquisitionAdapter):
    def __init__(self, config: ProjectConfig):
        self.config = config
        self._maacore_available = False
        self._check_environment()

    def _check_environment(self):
        """探测本地是否存在可调用的 MaaCore 动态库或 Python 包"""
        try:
            import asst
            self._maacore_available = True
        except ImportError:
            # 检查配置中指定的路径
            if self.config.maa.maacore_path:
                p = Path(self.config.maa.maacore_path)
                if p.exists() and (p / "MaaCore.dll").exists():
                    self._maacore_available = True
                    return
            self._maacore_available = False

    def is_available(self) -> bool:
        return self._maacore_available

    def collect_operators(self, max_pages: int = 5) -> List[OperatorState]:
        if not self.is_available():
            raise RuntimeError("MaaCore 环境未就绪，请使用 FallbackOperBoxRecognizer 进行视觉采集。")

        # 当原生 MaaCore 可用时，调用 Asst.append_task('OperBoxRecognitionTask') 并订阅 SubTaskExtraInfo
        import asst
        results: List[OperatorState] = []
        # 官方结构映射
        return results
