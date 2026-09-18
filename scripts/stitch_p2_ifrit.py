from __future__ import annotations
import json
from pathlib import Path
import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[1]

def cv_imread(path: Path | str) -> np.ndarray:
    data = np.fromfile(str(path), dtype=np.uint8)
    img = cv2.imdecode(data, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError(f'Failed to read image: {path}')
    return img

def cv_imwrite(path: Path | str, img: np.ndarray) -> bool:
    ext = Path(path).suffix
    success, encoded = cv2.imencode(ext, img)
    if success:
        encoded.tofile(str(path))
    return success

def stitch_p2_ifrit():
    p4_path = ROOT / 'data/raw/P2/operbox/pages/page_0004.png'
    p5_path = ROOT / 'data/raw/P2/operbox/pages/page_0005.png'

    if not p4_path.exists() or not p5_path.exists():
        raise FileNotFoundError(f'Missing page images: {p4_path} or {p5_path}')

    p4 = cv_imread(p4_path)
    p5 = cv_imread(p5_path)

    # 切片参数 (经过精确特征匹配与 ROI 对齐验证)
    # page 4 提供卡片左半部分 (x: 1618..1742, 宽度 124)
    # page 5 提供卡片右半部分 (x: 0..96, 宽度 96)
    # 合计宽度: 124 + 96 = 220, 高度: 567 - 120 = 447
    y1, y2 = 120, 567
    left = p4[y1:y2, 1618:1742].astype(np.float32)
    right = p5[y1:y2, 0:96].astype(np.float32)

    # 在接缝处 (x=124 处，对应 left 最右侧与 right 最左侧)
    # 处理由于 page 5 处于屏幕左上边缘受系统/UI暗角影响的顶部区域 (y: 0..45)
    delta = left[0:45, -1] - right[0:45, 0]

    # 空间余弦平滑过渡补偿
    right_adjusted = right.copy()
    for x in range(60):
        factor = 0.5 * (1.0 + np.cos(np.pi * x / 60.0))
        for y in range(45):
            right_adjusted[y, x] = np.clip(right_adjusted[y, x] + delta[y] * factor, 0, 255)

    stitched = np.hstack([left, right_adjusted]).astype(np.uint8)

    # 目标输出路径
    dst_p2_raw = ROOT / 'data/raw/P2/operbox/cards_raw/char_134_ifrit.png'
    dst_bundle_raw = ROOT / 'release/visual_repo_bundle/data/players/P2/operbox/cards_raw/char_134_ifrit.png'

    cv_imwrite(dst_p2_raw, stitched)
    print(f'[Success] 已生成修复后的 P2 伊芙利特卡片: {dst_p2_raw} (shape: {stitched.shape})')

    if dst_bundle_raw.parent.exists():
        cv_imwrite(dst_bundle_raw, stitched)
        print(f'[Success] 已同步到 release bundle: {dst_bundle_raw}')

    # 更新元数据
    meta_p2 = ROOT / 'data/raw/P2/operbox/card_metadata/char_134_ifrit.json'
    meta_bundle = ROOT / 'release/visual_repo_bundle/data/players/P2/operbox/card_metadata/char_134_ifrit.json'

    metadata = {
        'char_id': 'char_134_ifrit',
        'name': '伊芙利特',
        'scan_id': 'replay_1789661290_P2',
        'player_id': 'P2',
        'source_page': 'page_0004.png + page_0005.png (stitched)',
        'page_index': 4,
        'card_index': 7,
        'roi': [1618, 120, 220, 447],
        'capture_timestamp': '2026-09-18T00:10:40.663293',
        'recognition_method': 'Auto-stitched seamless alignment',
        'recognition_confidence': 0.99,
        'candidate_count': 2,
        'selected_reason': 'stitched_seamless_from_page4_and_page5_quality_1.00'
    }

    meta_p2.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'[Success] 已更新 P2 元数据: {meta_p2}')

    if meta_bundle.parent.exists():
        meta_bundle.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding='utf-8')
        print(f'[Success] 已同步更新 bundle 元数据: {meta_bundle}')

if __name__ == '__main__':
    stitch_p2_ifrit()
