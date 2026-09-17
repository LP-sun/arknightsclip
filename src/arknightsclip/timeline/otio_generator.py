"""
OpenTimelineIO (OTIO) 分层时间线生成器
提供标准 OTIO 交换格式，支持主流 NLE (DaVinci Resolve, Premiere, Final Cut Pro)
"""

import json
from pathlib import Path
from typing import Dict, List, Optional
from ..config import ProjectConfig, load_config
from ..models.timeline import TimelineSequence

try:
    import opentimelineio as otio
except ImportError:
    otio = None

class OTIOGenerator:
    def __init__(self, config: Optional[ProjectConfig] = None):
        self.config = config or load_config()

    def build_timeline_otio(
        self,
        timeline_name: str = "明日方舟_六星干员报菜名_v2",
        output_path: Optional[Path] = None,
    ) -> Path:
        if otio is None:
            raise RuntimeError("未安装 opentimelineio 依赖")

        out_file = output_path or (self.config.resolve_path("reports") / "timeline_v2_layered.otio")
        out_file.parent.mkdir(parents=True, exist_ok=True)

        d_file = self.config.resolve_path("durations_24fps_perfect.json")
        if not d_file.exists():
            fallback_d = self.config.resolve_path("archive/legacy_data/durations_24fps_perfect.json")
            if fallback_d.exists():
                d_file = fallback_d
        durations: Dict[int, int] = {}
        if d_file.exists():
            with open(d_file, "r", encoding="utf-8") as f:
                durations = {int(k): v for k, v in json.load(f).items()}

        timeline = otio.schema.Timeline(name=timeline_name)
        v_track = otio.schema.Track(name="V1_Layered", kind=otio.schema.TrackKind.Video)

        curr_frame = 0
        for idx in range(len(durations)):
            dur = durations.get(idx, 24)
            clip = otio.schema.Clip(
                name=f"clip_{idx:03d}",
                source_range=otio.opentime.TimeRange(
                    start_time=otio.opentime.RationalTime(0, 24),
                    duration=otio.opentime.RationalTime(dur, 24),
                ),
            )
            v_track.append(clip)
            curr_frame += dur

        timeline.tracks.append(v_track)
        otio.adapters.write_to_file(timeline, str(out_file))
        print(f"[OTIOGenerator] 成功生成 OTIO 时间线: {out_file} (总计 {curr_frame} 帧)")
        return out_file
