"""
轻量级无依赖测试套件运行器
"""

import sys
from pathlib import Path

_project_root = Path(__file__).resolve().parent.parent
_src_dir = _project_root / "src"
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))
if str(_src_dir) not in sys.path:
    sys.path.insert(0, str(_src_dir))

import traceback
from tests.test_data_models import (
    test_operator_registry_entry,
    test_player_slot_state_own,
    test_player_slot_state_not_own,
    test_player_slot_state_invalid_level,
    test_player_slot_state_invalid_elite,
    test_player_slot_state_invalid_potential,
    test_scene_manifest_consistency,
    test_timeline_sequence_derived_duration,
)
from tests.test_registry_and_assets import (
    config,
    registry,
    test_registry_resolution,
    test_operator_registry_p0_aliases_and_ocr_protection,
    test_asset_resolver_validation,
    test_group_stats_computation,
)
from tests.test_operbox_schema import TestOperBoxSchema
from tests.test_operbox_crop_selection import TestOperBoxCropSelection
from tests.test_operbox_dedup import TestOperBoxDedup
from tests.test_operbox_asset_state_join import TestOperBoxAssetStateJoin
from tests.test_scene_builder import TestSceneBuilder
from tests.test_fcpxml_timeline import TestTimelineGenerators

def run_all():
    tests = [
        ("test_operator_registry_entry", test_operator_registry_entry),
        ("test_player_slot_state_own", test_player_slot_state_own),
        ("test_player_slot_state_not_own", test_player_slot_state_not_own),
        ("test_player_slot_state_invalid_level", test_player_slot_state_invalid_level),
        ("test_player_slot_state_invalid_elite", test_player_slot_state_invalid_elite),
        ("test_player_slot_state_invalid_potential", test_player_slot_state_invalid_potential),
        ("test_scene_manifest_consistency", test_scene_manifest_consistency),
        ("test_timeline_sequence_derived_duration", test_timeline_sequence_derived_duration),
    ]

    cfg = config()
    reg = registry(cfg)

    # 初始化测试类
    ts_builder = TestSceneBuilder()
    ts_builder.setUp()
    ts_timeline = TestTimelineGenerators()
    ts_timeline.setUp()

    tests_with_fixtures = [
        ("test_registry_resolution", lambda: test_registry_resolution(reg)),
        ("test_operator_registry_p0_aliases_and_ocr_protection", lambda: test_operator_registry_p0_aliases_and_ocr_protection(reg)),
        ("test_asset_resolver_validation", lambda: test_asset_resolver_validation(cfg, reg)),
        ("test_group_stats_computation", lambda: test_group_stats_computation(cfg, reg)),
        ("test_operbox_card_roi_conversion", lambda: TestOperBoxSchema().test_card_roi_conversion()),
        ("test_operbox_provenance_schema", lambda: TestOperBoxSchema().test_provenance_schema_serialization()),
        ("test_operbox_scan_session_summary", lambda: TestOperBoxSchema().test_scan_session_summary()),
        ("test_operbox_name_roi_bicubic_upscale", lambda: TestOperBoxSchema().test_name_roi_bicubic_upscale()),
        ("test_operbox_crop_selection", lambda: TestOperBoxCropSelection().test_edge_rejection_and_scoring()),
        ("test_operbox_dedup_across_pages", lambda: TestOperBoxDedup().test_dedup_across_pages()),
        ("test_operbox_candidate_dedup", lambda: TestOperBoxDedup().test_candidate_dedup_best_selection()),
        ("test_operbox_state_asset_join", lambda: TestOperBoxAssetStateJoin().test_state_and_asset_join_integrity()),
        ("test_operbox_unowned_asset_null", lambda: TestOperBoxAssetStateJoin().test_unowned_operator_asset_is_null()),
        ("test_scene_builder_contract", lambda: ts_builder.test_build_scene_contract()),
        ("test_scene_builder_persistence", lambda: ts_builder.test_build_all_scenes_persistence()),
        ("test_timeline_fcpxml_structure", lambda: ts_timeline.test_fcpxml_structure_and_integrity()),
        ("test_timeline_otio_generation", lambda: ts_timeline.test_otio_generation()),
    ]

    passed = 0
    failed = 0

    print("================================================================================")
    print("                arknightsclip Phase 2 契约与单元测试套件")
    print("================================================================================")

    for name, func in tests + tests_with_fixtures:
        try:
            func()
            passed += 1
            print(f"  ✓ {name:45s} PASSED")
        except Exception as e:
            failed += 1
            print(f"  ✗ {name:45s} FAILED: {e}")
            traceback.print_exc()

    print("================================================================================")
    print(f"测试完成: {passed} 通过, {failed} 失败")
    print("================================================================================")
    if failed > 0:
        sys.exit(1)

if __name__ == "__main__":
    run_all()
