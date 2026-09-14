"""
测试 arknightsclip 核心数据模型与契约验证
"""

# 测试核心数据模型与契约验证
from src.arknightsclip.models.operator import OperatorRegistryEntry, OperatorState, ConfidenceScore, RecognitionMethod
from src.arknightsclip.models.scene import PlayerSlotState, SceneManifest
from src.arknightsclip.models.timeline import SequenceEntry, TimelineSequence
from src.arknightsclip.models.player import PlayerProfile, PlayerDataSet, FivePlayersDataset

def test_operator_registry_entry():
    entry = OperatorRegistryEntry(
        char_id="char_103_angel",
        canonical_name_zh="能天使",
        rarity=6,
        profession="SNIPER",
        aliases=["阿能", "Exusiai"]
    )
    assert entry.matches("能天使")
    assert entry.matches("char_103_angel")
    assert entry.matches("阿能")
    assert entry.matches("Exusiai")
    assert not entry.matches("银灰")

def test_player_slot_state_own():
    # own=True 正常状态
    slot = PlayerSlotState(own=True, elite=2, level=83, potential=4, no_info=False)
    assert slot.validate() is True
    assert slot.no_info is False

def test_player_slot_state_not_own():
    # own=False 时必须为 no_info=True
    slot = PlayerSlotState(own=False)
    assert slot.no_info is True
    assert slot.validate() is True

def test_player_slot_state_invalid_level():
    # 等级超过 90
    slot = PlayerSlotState(own=True, elite=2, level=99, potential=4, no_info=False)
    assert slot.validate() is False

def test_player_slot_state_invalid_elite():
    # 精英度超过 2
    slot = PlayerSlotState(own=True, elite=3, level=80, potential=4, no_info=False)
    assert slot.validate() is False

def test_player_slot_state_invalid_potential():
    # 潜能超过 6
    slot = PlayerSlotState(own=True, elite=2, level=80, potential=7, no_info=False)
    assert slot.validate() is False

def test_scene_manifest_consistency():
    manifest = SceneManifest(
        operator_id="char_103_angel",
        operator_name="能天使",
        rarity=6,
        players={
            "P1": PlayerSlotState(own=True, elite=2, level=90, potential=6, no_info=False),
            "P2": PlayerSlotState(own=False, no_info=True),
        }
    )
    assert manifest.validate() is True

def test_timeline_sequence_derived_duration():
    # 总帧数必须由 entries 动态求和推导，严禁硬编码
    entries = [
        SequenceEntry(operator_id="char_103_angel", start_frame=0, duration_frames=24),
        SequenceEntry(operator_id="char_112_siege", start_frame=24, duration_frames=24),
        SequenceEntry(operator_id="char_350_surtr", start_frame=48, duration_frames=48),
    ]
    seq = TimelineSequence(fps=24.0, entries=entries)
    assert seq.total_frames == 96
    assert seq.duration_seconds == 4.0
