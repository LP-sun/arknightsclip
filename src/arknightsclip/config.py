"""
arknightsclip 统一配置管理模块
自动识别工程根目录，支持从 YAML 与环境变量读取，严禁任何机器写死的绝对路径。
"""

import os
import yaml
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any

@dataclass
class SwipeConfig:
    start_x: int = 1550
    start_y: int = 540
    end_x: int = 350
    end_y: int = 540
    duration_ms: int = 800
    settle_delay_sec: float = 1.5

@dataclass
class MaaConfig:
    maacore_path: str = ""
    adb_path: str = ""
    adb_device: str = "127.0.0.1:16384"
    template_dir: str = "maa_templates"
    swipe: SwipeConfig = field(default_factory=SwipeConfig)

@dataclass
class PhotoshopConfig:
    backend: str = "psd_tools"  # psd_tools | jsx | com
    exe_path: str = ""
    master_template: str = "templates/psd/report_5p_master.psd"
    schema_path: str = "templates/psd/report_5p_schema.json"

@dataclass
class ReferenceVideoConfig:
    enabled: bool = False
    path: str = "output_video.mp4"

@dataclass
class AudioConfig:
    bgm_path: str = "明日方舟五周年_六星干员报菜名_节奏卡点全合成.mov"

@dataclass
class DaVinciConfig:
    fps: float = 24.0
    width: int = 1920
    height: int = 1080
    timeline_name: str = "明日方舟_六星干员报菜名_5人分层合成_v3"
    reference_video: ReferenceVideoConfig = field(default_factory=ReferenceVideoConfig)
    audio: AudioConfig = field(default_factory=AudioConfig)

@dataclass
class PipelineConfig:
    player_count: int = 5
    data_dir: str = "data"
    assets_dir: str = "assets"
    generated_dir: str = "generated"
    reports_dir: str = "reports"
    target_rarity: int = 6

@dataclass
class PlayerProfile:
    id: str
    display_name: str
    doctor_level: int = 120
    avatar: str = ""

@dataclass
class ProjectConfig:
    project_root: Path
    maa: MaaConfig = field(default_factory=MaaConfig)
    photoshop: PhotoshopConfig = field(default_factory=PhotoshopConfig)
    davinci: DaVinciConfig = field(default_factory=DaVinciConfig)
    pipeline: PipelineConfig = field(default_factory=PipelineConfig)
    players: List[PlayerProfile] = field(default_factory=list)

    def resolve_path(self, relative_or_absolute: str) -> Path:
        """安全解析相对项目根目录的路径，防止机器特定绝对路径污染"""
        p = Path(relative_or_absolute)
        if p.is_absolute():
            return p
        return (self.project_root / p).resolve()

    def get_raw_player_dir(self, player_id: str) -> Path:
        p = self.resolve_path(self.pipeline.data_dir) / "raw" / player_id
        p.mkdir(parents=True, exist_ok=True)
        return p

    def get_normalized_dir(self) -> Path:
        p = self.resolve_path(self.pipeline.data_dir) / "normalized"
        p.mkdir(parents=True, exist_ok=True)
        return p

    def get_manifests_dir(self) -> Path:
        p = self.resolve_path(self.pipeline.data_dir) / "manifests"
        p.mkdir(parents=True, exist_ok=True)
        return p

def load_config(config_path: Optional[str] = None) -> ProjectConfig:
    """加载配置单例，具备动态向上递归寻找项目根目录能力"""
    # 确定项目根目录
    current_file = Path(__file__).resolve()
    # src/arknightsclip/config.py -> parents[2] 为根目录
    inferred_root = current_file.parents[2]

    # 支持环境变量覆写根目录
    env_root = os.environ.get("ARKNIGHTSCLIP_ROOT")
    project_root = Path(env_root).resolve() if env_root else inferred_root

    # 寻找配置文件
    cfg_file = None
    if config_path:
        cfg_file = Path(config_path)
    else:
        candidates = [
            project_root / "config" / "project.yaml",
            project_root / "config" / "project.example.yaml",
        ]
        for c in candidates:
            if c.exists():
                cfg_file = c
                break

    data: Dict[str, Any] = {}
    if cfg_file and cfg_file.exists():
        with open(cfg_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}

    # 构建 typed configs
    maa_data = data.get("maa", {})
    swipe_data = maa_data.get("swipe", {})
    swipe_cfg = SwipeConfig(
        start_x=swipe_data.get("start_x", 1550),
        start_y=swipe_data.get("start_y", 540),
        end_x=swipe_data.get("end_x", 350),
        end_y=swipe_data.get("end_y", 540),
        duration_ms=swipe_data.get("duration_ms", 800),
        settle_delay_sec=swipe_data.get("settle_delay_sec", 1.5),
    )
    maa_cfg = MaaConfig(
        maacore_path=maa_data.get("maacore_path", ""),
        adb_path=maa_data.get("adb_path", ""),
        adb_device=maa_data.get("adb_device", "127.0.0.1:16384"),
        template_dir=maa_data.get("template_dir", "maa_templates"),
        swipe=swipe_cfg,
    )

    ps_data = data.get("photoshop", {})
    ps_cfg = PhotoshopConfig(
        backend=ps_data.get("backend", "psd_tools"),
        exe_path=ps_data.get("exe_path", ""),
        master_template=ps_data.get("master_template", "templates/psd/report_5p_master.psd"),
        schema_path=ps_data.get("schema_path", "templates/psd/report_5p_schema.json"),
    )

    davinci_data = data.get("davinci", {})
    ref_vid = davinci_data.get("reference_video", {})
    ref_cfg = ReferenceVideoConfig(
        enabled=ref_vid.get("enabled", False),
        path=ref_vid.get("path", "output_video.mp4"),
    )
    aud_data = davinci_data.get("audio", {})
    aud_cfg = AudioConfig(
        bgm_path=aud_data.get("bgm_path", "明日方舟五周年_六星干员报菜名_节奏卡点全合成.mov"),
    )
    davinci_cfg = DaVinciConfig(
        fps=davinci_data.get("fps", 24.0),
        width=davinci_data.get("width", 1920),
        height=davinci_data.get("height", 1080),
        timeline_name=davinci_data.get("timeline_name", "明日方舟_六星干员报菜名_5人分层合成_v3"),
        reference_video=ref_cfg,
        audio=aud_cfg,
    )

    pipe_data = data.get("pipeline", {})
    pipe_cfg = PipelineConfig(
        player_count=pipe_data.get("player_count", 5),
        data_dir=pipe_data.get("data_dir", "data"),
        assets_dir=pipe_data.get("assets_dir", "assets"),
        generated_dir=pipe_data.get("generated_dir", "generated"),
        reports_dir=pipe_data.get("reports_dir", "reports"),
        target_rarity=pipe_data.get("target_rarity", 6),
    )

    players_data = data.get("players", [])
    players_list = []
    for p in players_data:
        players_list.append(PlayerProfile(
            id=p.get("id", "P1"),
            display_name=p.get("display_name", "博士"),
            doctor_level=p.get("doctor_level", 120),
            avatar=p.get("avatar", ""),
        ))

    return ProjectConfig(
        project_root=project_root,
        maa=maa_cfg,
        photoshop=ps_cfg,
        davinci=davinci_cfg,
        pipeline=pipe_cfg,
        players=players_list,
    )
