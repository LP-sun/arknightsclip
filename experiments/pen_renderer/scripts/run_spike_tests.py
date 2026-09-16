import os
import sys
import json
import time

from pen_renderer import PenRenderer

def run_tests():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    template_path = os.path.join(base_dir, 'templates', 'report_5p_master.pen')
    
    manifest_a_path = os.path.join(base_dir, 'manifests', 'exusiai_test.json')
    manifest_b_path = os.path.join(base_dir, 'manifests', 'variant_test.json')

    out_pen_a = os.path.join(base_dir, 'outputs', 'test_A.pen')
    out_png_a = os.path.join(base_dir, 'outputs', 'test_A.png')

    out_pen_b = os.path.join(base_dir, 'outputs', 'test_B.pen')
    out_png_b = os.path.join(base_dir, 'outputs', 'test_B.png')

    renderer = PenRenderer(base_asset_dir=base_dir)

    print("================================================================================")
    print("      PenRenderer Spike: 参数化渲染验证")
    print("================================================================================")
    
    # Test A: 能天使场景
    print("\n[Test A] 正在渲染 能天使五人场景 (test_A.json)...")
    res_a = renderer.render_scene(
        template_path=template_path,
        manifest_path_or_dict=manifest_a_path,
        output_pen_path=out_pen_a,
        output_png_path=out_png_a
    )
    print(f"  -> Test A 完成! 耗时: {res_a['render_time_seconds']}s")
    print(f"  -> 输出 PNG: {out_png_a}")
    print(f"  -> 输出派生 .pen: {out_pen_a}")

    # Test B: 推进之王场景 (只变 JSON，完全相同模板)
    print("\n[Test B] 正在渲染 推进之王五人场景 (test_B.json)...")
    res_b = renderer.render_scene(
        template_path=template_path,
        manifest_path_or_dict=manifest_b_path,
        output_pen_path=out_pen_b,
        output_png_path=out_png_b
    )
    print(f"  -> Test B 完成! 耗时: {res_b['render_time_seconds']}s")
    print(f"  -> 输出 PNG: {out_png_b}")
    print(f"  -> 输出派生 .pen: {out_pen_b}")

    print("\n[验收验证]")
    print(f"  - Test A PNG 存在: {os.path.exists(out_png_a)}, 文件大小: {os.path.getsize(out_png_a)} 字节")
    print(f"  - Test B PNG 存在: {os.path.exists(out_png_b)}, 文件大小: {os.path.getsize(out_png_b)} 字节")

if __name__ == '__main__':
    run_tests()
