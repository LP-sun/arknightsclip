import os
import sys
import time
import json
import tracemalloc

from pen_renderer import PenRenderer

def run_benchmarks():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    template_path = os.path.join(base_dir, 'templates', 'report_5p_master.pen')
    manifest_a_path = os.path.join(base_dir, 'manifests', 'exusiai_test.json')
    manifest_b_path = os.path.join(base_dir, 'manifests', 'variant_test.json')

    renderer = PenRenderer(base_asset_dir=base_dir)

    print("================================================================================")
    print("      PenRenderer 性能基准测试 (单场景 vs 10 场景批处理)")
    print("================================================================================")

    # 1. 单场景测试
    tracemalloc.start()
    t0_single = time.time()
    res_single = renderer.render_scene(
        template_path=template_path,
        manifest_path_or_dict=manifest_a_path,
        output_pen_path=os.path.join(base_dir, 'outputs', 'bench_single.pen'),
        output_png_path=os.path.join(base_dir, 'outputs', 'bench_single.png')
    )
    t_single = time.time() - t0_single
    mem_current, mem_peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    print(f"\n[单场景结果]")
    print(f"  - 总耗时: {t_single:.4f} 秒")
    print(f"  - 峰值内存: {mem_peak / 1024 / 1024:.2f} MB")

    # 2. 10 场景批处理测试
    print(f"\n[10 场景批处理测试启动...]")
    with open(manifest_a_path, 'r', encoding='utf-8') as f:
        base_manifest = json.load(f)

    batch_times = []
    tracemalloc.start()
    t0_batch = time.time()
    
    for i in range(1, 11):
        m = json.load(open(manifest_a_path if i % 2 == 1 else manifest_b_path, 'r', encoding='utf-8'))
        # 变动部分参数模拟多场景
        m['players']['P1']['level'] = 50 + (i * 3) % 40
        m['players']['P1']['potential'] = (i % 6) + 1
        m['players']['P2']['own'] = (i % 3 != 0)
        
        out_pen = os.path.join(base_dir, 'outputs', f'bench_batch_{i:02d}.pen')
        out_png = os.path.join(base_dir, 'outputs', f'bench_batch_{i:02d}.png')

        t0_iter = time.time()
        res = renderer.render_scene(template_path, m, out_pen, out_png)
        dt = time.time() - t0_iter
        batch_times.append(dt)
        print(f"  - Scene {i:02d}/10: {dt:.4f}s")

    t_batch_total = time.time() - t0_batch
    avg_iter = sum(batch_times) / len(batch_times)
    b_current, b_peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    print(f"\n[10 场景批处理统计]")
    print(f"  - 总批处理耗时: {t_batch_total:.4f} 秒")
    print(f"  - 平均单场景耗时: {avg_iter:.4f} 秒")
    print(f"  - 吞吐率: {10 / t_batch_total:.2f} scenes/second")
    print(f"  - 批处理峰值内存: {b_peak / 1024 / 1024:.2f} MB")
    print(f"  - 预估 138 场景全量耗时: {avg_iter * 138 / 60:.2f} 分钟 (约 {avg_iter * 138:.1f} 秒)")

    # 保存报告 JSON
    bench_data = {
        "single_scene": {
            "total_time_seconds": round(t_single, 4),
            "peak_memory_mb": round(mem_peak / 1024 / 1024, 2)
        },
        "batch_10_scenes": {
            "total_time_seconds": round(t_batch_total, 4),
            "average_time_seconds": round(avg_iter, 4),
            "throughput_fps": round(10 / t_batch_total, 2),
            "peak_memory_mb": round(b_peak / 1024 / 1024, 2),
            "estimated_138_scenes_seconds": round(avg_iter * 138, 1)
        }
    }
    with open(os.path.join(base_dir, 'outputs', 'benchmark_result.json'), 'w', encoding='utf-8') as f:
        json.dump(bench_data, f, indent=2)

if __name__ == '__main__':
    run_benchmarks()
