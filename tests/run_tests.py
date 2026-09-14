"""
轻量级无依赖测试套件运行器
"""

import sys
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
    test_asset_resolver_validation,
    test_group_stats_computation,
)

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

    tests_with_fixtures = [
        ("test_registry_resolution", lambda: test_registry_resolution(reg)),
        ("test_asset_resolver_validation", lambda: test_asset_resolver_validation(cfg, reg)),
        ("test_group_stats_computation", lambda: test_group_stats_computation(cfg, reg)),
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
