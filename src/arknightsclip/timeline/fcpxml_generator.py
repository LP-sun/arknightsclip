"""
FCP7 XML (xmeml v4) 分层时间线生成器
针对 DaVinci Resolve 严格规范：
- 严格 24.0 fps
- 4 视频轨 (V1 Background, V2 Character Cards, V3 Doctor Info, V4 Reference Video)
- 2 音频轨 (A1 Music, A2 Reference Audio)
- 4470 帧 (186.25 秒) 末端等长对齐
"""

import os
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Optional, Any
from ..config import ProjectConfig, load_config
from ..models.timeline import TimelineSequence, SequenceEntry

class FCPXMLGenerator:
    def __init__(self, config: Optional[ProjectConfig] = None):
        self.config = config or load_config()

    def build_timeline_xml(
        self,
        sequence: Optional[TimelineSequence] = None,
        durations_file: Optional[Path] = None,
        manifest_file: Optional[Path] = None,
        edit_plan_file: Optional[Path] = None,
        timeline_name: str = "明日方舟_六星干员报菜名_PSD分层母版合成_v2",
        output_xml: Optional[Path] = None,
    ) -> Path:
        """生成标准 FCP7 XML 时间线工程"""
        out_path = output_xml or (self.config.resolve_path("reports") / "timeline_v2_layered.xml")
        out_path.parent.mkdir(parents=True, exist_ok=True)

        # 加载时长配置
        d_file = durations_file or self.config.resolve_path("durations_24fps_perfect.json")
        m_file = manifest_file or self.config.resolve_path("composition_manifest.json")
        e_file = edit_plan_file or self.config.resolve_path("edit_plan.json")

        durations: Dict[int, int] = {}
        if d_file.exists():
            with open(d_file, "r", encoding="utf-8") as f:
                durations = {int(k): v for k, v in json.load(f).items()}

        manifest_59 = []
        if m_file.exists():
            with open(m_file, "r", encoding="utf-8") as f:
                manifest_59 = json.load(f).get("scenes", [])

        full_edit_plan = []
        if e_file.exists():
            with open(e_file, "r", encoding="utf-8") as f:
                full_edit_plan = json.load(f).get("clips", [])

        # 若未提供外部配置且有传入 sequence，则优先使用 sequence
        if sequence and sequence.entries:
            entries = sequence.entries
            total_duration = sequence.total_frames
        else:
            total_duration = sum(durations.values()) if durations else 4470

        # XML 根节点
        xmeml = ET.Element("xmeml", version="4")
        seq = ET.SubElement(xmeml, "sequence", id="sequence-1")
        ET.SubElement(seq, "name").text = timeline_name
        ET.SubElement(seq, "duration").text = str(total_duration)

        rate = ET.SubElement(seq, "rate")
        ET.SubElement(rate, "timebase").text = "24"
        ET.SubElement(rate, "ntsc").text = "FALSE"

        media = ET.SubElement(seq, "media")
        video = ET.SubElement(media, "video")

        format_elem = ET.SubElement(video, "format")
        sc = ET.SubElement(format_elem, "samplecharacteristics")
        ET.SubElement(sc, "width").text = "1920"
        ET.SubElement(sc, "height").text = "1080"
        sc_rate = ET.SubElement(sc, "rate")
        ET.SubElement(sc_rate, "timebase").text = "24"
        ET.SubElement(sc_rate, "ntsc").text = "FALSE"

        # 视频轨道
        track_v1 = ET.SubElement(video, "track")  # Background
        track_v2 = ET.SubElement(video, "track")  # Character Cards
        track_v3 = ET.SubElement(video, "track")  # Doctor Info
        track_v4 = ET.SubElement(video, "track")  # Sample Video

        def add_clip(track, clip_id: str, name: str, file_path: str, start: int, end: int, dur: int):
            item = ET.SubElement(track, "clipitem", id=f"clipitem-{clip_id}")
            ET.SubElement(item, "name").text = name
            ET.SubElement(item, "duration").text = str(dur)
            item_rate = ET.SubElement(item, "rate")
            ET.SubElement(item_rate, "timebase").text = "24"
            ET.SubElement(item_rate, "ntsc").text = "FALSE"
            ET.SubElement(item, "start").text = str(start)
            ET.SubElement(item, "end").text = str(end)
            ET.SubElement(item, "in").text = "0"
            ET.SubElement(item, "out").text = str(dur)

            file_elem = ET.SubElement(item, "file", id=f"file-{clip_id}")
            ET.SubElement(file_elem, "name").text = Path(file_path).name
            url = "file://localhost/" + str(Path(file_path).resolve()).replace("\\", "/")
            ET.SubElement(file_elem, "pathurl").text = url
            file_rate = ET.SubElement(file_elem, "rate")
            ET.SubElement(file_rate, "timebase").text = "24"
            ET.SubElement(file_rate, "ntsc").text = "FALSE"
            ET.SubElement(file_elem, "duration").text = str(dur)
            media_elem = ET.SubElement(file_elem, "media")
            video_elem = ET.SubElement(media_elem, "video")
            sc_f = ET.SubElement(video_elem, "samplecharacteristics")
            ET.SubElement(sc_f, "width").text = "1920"
            ET.SubElement(sc_f, "height").text = "1080"

        # 填充片段
        curr_frame = 0
        items_count = len(full_edit_plan) if full_edit_plan else (len(durations) if durations else 0)

        for idx in range(items_count):
            dur = durations.get(idx, 24)
            start_f = curr_frame
            end_f = curr_frame + dur
            plan_item = full_edit_plan[idx] if idx < len(full_edit_plan) else {}

            if idx == 0:
                # 片头
                title_bg = self.config.resolve_path("generated/graphics/000_片头.png")
                add_clip(track_v1, f"v1-{idx}", "000_片头", str(title_bg), start_f, end_f, dur)
            elif 1 <= idx <= min(59, len(manifest_59)):
                # 59 个真实分层场景
                s_data = manifest_59[idx - 1]
                s_id = s_data.get("scene_id", f"{idx:03d}")
                s_dir = self.config.resolve_path(f"generated/layered/{s_id}")
                bg_p = s_dir / "background.png"
                cards_p = s_dir / "character_cards.png"
                doc_p = s_dir / "doctor_info.png"

                add_clip(track_v1, f"v1-{idx}", f"{s_id}_BG", str(bg_p), start_f, end_f, dur)
                add_clip(track_v2, f"v2-{idx}", f"{s_id}_Cards", str(cards_p), start_f, end_f, dur)
                add_clip(track_v3, f"v3-{idx}", f"{s_id}_Doctor", str(doc_p), start_f, end_f, dur)
            else:
                # 其余干员
                c_name = plan_item.get("asset_id", f"clip_{idx:03d}")
                ext_img = self.config.resolve_path(plan_item.get("file", "generated/layered/001_能天使/background.png"))
                if not ext_img.exists():
                    ext_img = self.config.resolve_path("generated/layered/001_能天使/background.png")
                add_clip(track_v1, f"v1-{idx}", c_name, str(ext_img), start_f, end_f, dur)

            curr_frame += dur

        # 对照视频轨 V4
        sample_video = self.config.resolve_path("output_video.mp4")
        if sample_video.exists():
            add_clip(track_v4, "v4-sample", "样例对照视频", str(sample_video), 0, total_duration, total_duration)

        # 音频轨道
        audio = ET.SubElement(media, "audio")
        track_a1 = ET.SubElement(audio, "track")  # Music Audio
        track_a2 = ET.SubElement(audio, "track")  # Sample Video Audio

        def add_audio_clip(track, clip_id: str, name: str, file_path: str, dur: int):
            item = ET.SubElement(track, "clipitem", id=f"clipitem-{clip_id}")
            ET.SubElement(item, "name").text = name
            ET.SubElement(item, "duration").text = str(dur)
            item_rate = ET.SubElement(item, "rate")
            ET.SubElement(item_rate, "timebase").text = "24"
            ET.SubElement(item_rate, "ntsc").text = "FALSE"
            ET.SubElement(item, "start").text = "0"
            ET.SubElement(item, "end").text = str(dur)
            ET.SubElement(item, "in").text = "0"
            ET.SubElement(item, "out").text = str(dur)
            file_elem = ET.SubElement(item, "file", id=f"file-{clip_id}")
            ET.SubElement(file_elem, "name").text = Path(file_path).name
            url = "file://localhost/" + str(Path(file_path).resolve()).replace("\\", "/")
            ET.SubElement(file_elem, "pathurl").text = url

        audio_path = self.config.resolve_path("明日方舟五周年_六星干员报菜名_节奏卡点全合成.mov")
        if audio_path.exists():
            add_audio_clip(track_a1, "a1-music", "高保真配乐", str(audio_path), total_duration)
        if sample_video.exists():
            add_audio_clip(track_a2, "a2-sample", "样例视频原声", str(sample_video), total_duration)

        # 写入格式化 XML
        tree = ET.ElementTree(xmeml)
        ET.indent(tree, space="  ", level=0)
        tree.write(out_path, encoding="utf-8", xml_declaration=True)

        print(f"[FCPXMLGenerator] 成功生成 FCP7 XML: {out_path}")
        print(f"[FCPXMLGenerator] 严格 24.0 fps，总帧数: {curr_frame} 帧 ({curr_frame/24.0:.2f} 秒)")
        return out_path
