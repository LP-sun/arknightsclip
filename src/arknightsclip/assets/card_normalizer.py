"""
Card Asset Normalizer (卡片视觉规格标准化器)
对来自不同玩家分辨率 (720p/1080p/2K/模拟器) 的 cards_raw 切片进行统一的高质量采样与归一化缓存。
严格保持原始宽高比，采用高质量 Lanczos 采样，克制微锐化，绝不破坏覆盖原始事实素材。
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple, Dict, List
from PIL import Image, ImageFilter

from ..config import ProjectConfig, load_config


# 1080p 视频基准显示规格：高度 680px，宽度 335px (基准比例 2.030)
DEFAULT_TARGET_WIDTH = 335
DEFAULT_TARGET_HEIGHT = 680


@dataclass
class NormalizedCardResult:
    cache_path: Path
    source_path: Path
    width: int
    height: int
    aspect_ratio: float
    source_size: Tuple[int, int]
    cached: bool


class CardNormalizer:
    def __init__(
        self,
        config: Optional[ProjectConfig] = None,
        target_size: Tuple[int, int] = (DEFAULT_TARGET_WIDTH, DEFAULT_TARGET_HEIGHT),
        apply_gentle_sharpen: bool = True,
    ):
        self.config = config or load_config()
        self.target_width, self.target_height = target_size
        self.target_aspect_ratio = self.target_height / self.target_width
        self.apply_gentle_sharpen = apply_gentle_sharpen

        self.cache_root = self.config.resolve_path("generated/cache/cards")
        self.cache_root.mkdir(parents=True, exist_ok=True)

    def _compute_file_sha256(self, path: Path) -> str:
        h = hashlib.sha256()
        with open(path, "rb") as f:
            while chunk := f.read(65536):
                h.update(chunk)
        return h.hexdigest()

    def normalize_card(
        self,
        source_path: Path,
        cache_subdir: Optional[str] = None,
        operator_id: Optional[str] = None,
        force: bool = False,
    ) -> NormalizedCardResult:
        """
        对单张原始卡片切片进行视觉标准化：
        1. 保持原图宽高比；
        2. 使用高质量 Lanczos 重采样；
        3. 精准无失真居中贴合至目标统一尺寸画幅；
        4. 可选轻微去模糊微锐化（无光晕效应）；
        5. 写入缓存目录 generated/cache/cards/，绝不篡改原始素材。
        """
        if not source_path.exists():
            raise FileNotFoundError(f"原始卡片素材不存在: {source_path}")

        cid = operator_id or source_path.stem
        out_dir = self.cache_root if not cache_subdir else (self.cache_root / cache_subdir)
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / f"{cid}.png"

        # 检查缓存是否有效 (若已存在且大小正常)
        if not force and out_path.exists() and out_path.stat().st_size > 0:
            with Image.open(out_path) as im:
                if im.size == (self.target_width, self.target_height):
                    with Image.open(source_path) as s_im:
                        s_size = s_im.size
                    return NormalizedCardResult(
                        cache_path=out_path,
                        source_path=source_path,
                        width=self.target_width,
                        height=self.target_height,
                        aspect_ratio=round(self.target_height / self.target_width, 4),
                        source_size=s_size,
                        cached=True,
                    )

        # 读取原始图像
        with Image.open(source_path) as raw_im:
            src_w, src_h = raw_im.size
            if src_w <= 0 or src_h <= 0:
                raise ValueError(f"无效的原始图片尺寸: {raw_im.size} in {source_path}")

            # 保持原始通道格式 (RGBA 优先，RGB 自动转 RGBA)
            img = raw_im.convert("RGBA")

            # 等比例缩放计算 (保持 aspect ratio，无拉伸)
            scale = min(self.target_width / src_w, self.target_height / src_h)
            new_w = max(1, int(round(src_w * scale)))
            new_h = max(1, int(round(src_h * scale)))

            # 高质量 Lanczos 采样
            resampled = img.resize((new_w, new_h), resample=Image.Resampling.LANCZOS)

            # 非常克制的微锐化 (防止缩放后轻微发虚，绝无 halo)
            if self.apply_gentle_sharpen:
                resampled = resampled.filter(
                    ImageFilter.UnsharpMask(radius=0.8, percent=35, threshold=3)
                )

            # 创建标准画幅底板并居中合成
            canvas = Image.new("RGBA", (self.target_width, self.target_height), (0, 0, 0, 0))
            offset_x = (self.target_width - new_w) // 2
            offset_y = (self.target_height - new_h) // 2
            canvas.paste(resampled, (offset_x, offset_y), mask=resampled)

            # 确定性保存 (无损压缩)
            canvas.save(out_path, format="PNG", optimize=True)

        return NormalizedCardResult(
            cache_path=out_path,
            source_path=source_path,
            width=self.target_width,
            height=self.target_height,
            aspect_ratio=round(self.target_height / self.target_width, 4),
            source_size=(src_w, src_h),
            cached=False,
        )

    def normalize_all_raw_cards(self, force: bool = False) -> Dict[str, List[NormalizedCardResult]]:
        """扫描所有玩家的 cards_raw 目录并统一预热标准化缓存"""
        results: Dict[str, List[NormalizedCardResult]] = {}
        for p in self.config.players:
            pid = p.id
            raw_dir = self.config.get_raw_player_dir(pid) / "operbox" / "cards_raw"
            if not raw_dir.exists():
                continue

            results[pid] = []
            for png in sorted(raw_dir.glob("*.png")):
                res = self.normalize_card(
                    source_path=png,
                    cache_subdir=pid,
                    operator_id=png.stem,
                    force=force,
                )
                results[pid].append(res)

        return results
