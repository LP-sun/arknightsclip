"""
Photoshop 渲染器统一抽象接口
为上层 Pipeline 屏蔽底层后端 (psd_tools / JSX / COM / UXP) 细节。
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict
from ..models.scene import SceneManifest

class PhotoshopRenderer(ABC):
    @abstractmethod
    def render_scene(self, manifest: SceneManifest, output_dir: Path) -> Dict[str, Path]:
        """根据场景清单动态渲染分层资产，返回输出文件映射字典"""
        pass
