# Pen Asset Dependency & Portability Report

## 1. Overview
This report documents external image asset dependencies in all `.pen` design templates,
identifies legacy `assets/raw_batch/` paths, and provides portable fallbacks to canonical assets.

| Pen Template | Total Refs | Unique URLs | Direct Local | Resolved via Repo / Fallback | Unresolved |
|---|---|---|---|---|---|
| `psd2pen/character_cards_5slot_template.pen` | 2053 | 166 | 55 | 46 | 65 |
| `psd2pen/character_cards_5slot.pen` | 288 | 55 | 55 | 0 | 0 |
| `psd2pen/character_cards_8slot.pen` | 156 | 55 | 55 | 0 | 0 |
| `psd2pen/character_card_components.pen` | 4 | 3 | 3 | 0 | 0 |

## 2. Raw Batch (`assets/raw_batch/char_*_1.png`) Mapping
Total unique operators referenced via legacy raw_batch paths: **111**.

| Operator ID | Name | Resolution Type | Resolved Local Path | Upstream Remote URL |
|---|---|---|---|---|
| `char_003_kalts` | Unknown | `hero_art` | `assets/operators/char_003_kalts/full.png` | [Source](https://raw.githubusercontent.com/ArknightsAssets/ArknightsAssets2/cn/assets/dyn/arts/characters/char_003_kalts/char_003_kalts_1.png) |
| `char_010_chen` | Unknown | `hero_art` | `assets/operators/char_010_chen/full.png` | [Source](https://raw.githubusercontent.com/ArknightsAssets/ArknightsAssets2/cn/assets/dyn/arts/characters/char_010_chen/char_010_chen_1.png) |
| `char_017_huang` | Unknown | `hero_art` | `assets/operators/char_017_huang/full.png` | [Source](https://raw.githubusercontent.com/ArknightsAssets/ArknightsAssets2/cn/assets/dyn/arts/characters/char_017_huang/char_017_huang_1.png) |
| `char_1012_skadi2` | Unknown | `hero_art` | `assets/operators/char_1012_skadi2/full.png` | [Source](https://raw.githubusercontent.com/ArknightsAssets/ArknightsAssets2/cn/assets/dyn/arts/characters/char_1012_skadi2/char_1012_skadi2_1.png) |
| `char_1013_chen2` | Unknown | `hero_art` | `assets/operators/char_1013_chen2/full.png` | [Source](https://raw.githubusercontent.com/ArknightsAssets/ArknightsAssets2/cn/assets/dyn/arts/characters/char_1013_chen2/char_1013_chen2_1.png) |
| `char_1014_nearl2` | Unknown | `hero_art` | `assets/operators/char_1014_nearl2/full.png` | [Source](https://raw.githubusercontent.com/ArknightsAssets/ArknightsAssets2/cn/assets/dyn/arts/characters/char_1014_nearl2/char_1014_nearl2_1.png) |
| `char_1015_aglna2` | Unknown | `unresolved` | *None (Fallback Mode)* | [Source](https://raw.githubusercontent.com/ArknightsAssets/ArknightsAssets2/cn/assets/dyn/arts/characters/char_1015_aglna2/char_1015_aglna2_1.png) |
| `char_1016_agoat2` | Unknown | `unresolved` | *None (Fallback Mode)* | [Source](https://raw.githubusercontent.com/ArknightsAssets/ArknightsAssets2/cn/assets/dyn/arts/characters/char_1016_agoat2/char_1016_agoat2_1.png) |
| `char_1019_siege2` | Unknown | `unresolved` | *None (Fallback Mode)* | [Source](https://raw.githubusercontent.com/ArknightsAssets/ArknightsAssets2/cn/assets/dyn/arts/characters/char_1019_siege2/char_1019_siege2_1.png) |
| `char_1020_reed2` | Unknown | `unresolved` | *None (Fallback Mode)* | [Source](https://raw.githubusercontent.com/ArknightsAssets/ArknightsAssets2/cn/assets/dyn/arts/characters/char_1020_reed2/char_1020_reed2_1.png) |
| `char_1023_ghost2` | Unknown | `hero_art` | `assets/operators/char_1023_ghost2/full.png` | [Source](https://raw.githubusercontent.com/ArknightsAssets/ArknightsAssets2/cn/assets/dyn/arts/characters/char_1023_ghost2/char_1023_ghost2_1.png) |
| `char_1026_gvial2` | Unknown | `unresolved` | *None (Fallback Mode)* | [Source](https://raw.githubusercontent.com/ArknightsAssets/ArknightsAssets2/cn/assets/dyn/arts/characters/char_1026_gvial2/char_1026_gvial2_1.png) |
| `char_1028_texas2` | Unknown | `unresolved` | *None (Fallback Mode)* | [Source](https://raw.githubusercontent.com/ArknightsAssets/ArknightsAssets2/cn/assets/dyn/arts/characters/char_1028_texas2/char_1028_texas2_1.png) |
| `char_1029_yato2` | Unknown | `unresolved` | *None (Fallback Mode)* | [Source](https://raw.githubusercontent.com/ArknightsAssets/ArknightsAssets2/cn/assets/dyn/arts/characters/char_1029_yato2/char_1029_yato2_1.png) |
| `char_1031_slent2` | Unknown | `unresolved` | *None (Fallback Mode)* | [Source](https://raw.githubusercontent.com/ArknightsAssets/ArknightsAssets2/cn/assets/dyn/arts/characters/char_1031_slent2/char_1031_slent2_1.png) |
| `char_1032_excu2` | Unknown | `unresolved` | *None (Fallback Mode)* | [Source](https://raw.githubusercontent.com/ArknightsAssets/ArknightsAssets2/cn/assets/dyn/arts/characters/char_1032_excu2/char_1032_excu2_1.png) |
| `char_1033_swire2` | Unknown | `unresolved` | *None (Fallback Mode)* | [Source](https://raw.githubusercontent.com/ArknightsAssets/ArknightsAssets2/cn/assets/dyn/arts/characters/char_1033_swire2/char_1033_swire2_1.png) |
| `char_1034_jesca2` | Unknown | `unresolved` | *None (Fallback Mode)* | [Source](https://raw.githubusercontent.com/ArknightsAssets/ArknightsAssets2/cn/assets/dyn/arts/characters/char_1034_jesca2/char_1034_jesca2_1.png) |
| `char_1035_wisdel` | Unknown | `unresolved` | *None (Fallback Mode)* | [Source](https://raw.githubusercontent.com/ArknightsAssets/ArknightsAssets2/cn/assets/dyn/arts/characters/char_1035_wisdel/char_1035_wisdel_1.png) |
| `char_1038_whitw2` | Unknown | `unresolved` | *None (Fallback Mode)* | [Source](https://raw.githubusercontent.com/ArknightsAssets/ArknightsAssets2/cn/assets/dyn/arts/characters/char_1038_whitw2/char_1038_whitw2_1.png) |
| `char_1039_thorn2` | Unknown | `unresolved` | *None (Fallback Mode)* | [Source](https://raw.githubusercontent.com/ArknightsAssets/ArknightsAssets2/cn/assets/dyn/arts/characters/char_1039_thorn2/char_1039_thorn2_1.png) |
| `char_103_angel` | Unknown | `hero_art` | `assets/operators/char_103_angel/full.png` | [Source](https://raw.githubusercontent.com/ArknightsAssets/ArknightsAssets2/cn/assets/dyn/arts/characters/char_103_angel/char_103_angel_1.png) |
| `char_1040_blaze2` | Unknown | `unresolved` | *None (Fallback Mode)* | [Source](https://raw.githubusercontent.com/ArknightsAssets/ArknightsAssets2/cn/assets/dyn/arts/characters/char_1040_blaze2/char_1040_blaze2_1.png) |
| `char_1041_angel2` | Unknown | `unresolved` | *None (Fallback Mode)* | [Source](https://raw.githubusercontent.com/ArknightsAssets/ArknightsAssets2/cn/assets/dyn/arts/characters/char_1041_angel2/char_1041_angel2_1.png) |
| `char_1042_phatm2` | Unknown | `unresolved` | *None (Fallback Mode)* | [Source](https://raw.githubusercontent.com/ArknightsAssets/ArknightsAssets2/cn/assets/dyn/arts/characters/char_1042_phatm2/char_1042_phatm2_1.png) |
| `char_1043_leizi2` | Unknown | `unresolved` | *None (Fallback Mode)* | [Source](https://raw.githubusercontent.com/ArknightsAssets/ArknightsAssets2/cn/assets/dyn/arts/characters/char_1043_leizi2/char_1043_leizi2_1.png) |
| `char_1044_hsgma2` | Unknown | `unresolved` | *None (Fallback Mode)* | [Source](https://raw.githubusercontent.com/ArknightsAssets/ArknightsAssets2/cn/assets/dyn/arts/characters/char_1044_hsgma2/char_1044_hsgma2_1.png) |
| `char_1045_svash2` | Unknown | `unresolved` | *None (Fallback Mode)* | [Source](https://raw.githubusercontent.com/ArknightsAssets/ArknightsAssets2/cn/assets/dyn/arts/characters/char_1045_svash2/char_1045_svash2_1.png) |
| `char_1046_sbell2` | Unknown | `unresolved` | *None (Fallback Mode)* | [Source](https://raw.githubusercontent.com/ArknightsAssets/ArknightsAssets2/cn/assets/dyn/arts/characters/char_1046_sbell2/char_1046_sbell2_1.png) |
| `char_1047_halo2` | Unknown | `unresolved` | *None (Fallback Mode)* | [Source](https://raw.githubusercontent.com/ArknightsAssets/ArknightsAssets2/cn/assets/dyn/arts/characters/char_1047_halo2/char_1047_halo2_1.png) |
| `char_1048_orchd2` | Unknown | `unresolved` | *None (Fallback Mode)* | [Source](https://raw.githubusercontent.com/ArknightsAssets/ArknightsAssets2/cn/assets/dyn/arts/characters/char_1048_orchd2/char_1048_orchd2_1.png) |
| `char_1052_kalts2` | Unknown | `unresolved` | *None (Fallback Mode)* | [Source](https://raw.githubusercontent.com/ArknightsAssets/ArknightsAssets2/cn/assets/dyn/arts/characters/char_1052_kalts2/char_1052_kalts2_1.png) |
| `char_112_siege` | Unknown | `hero_art` | `assets/operators/char_112_siege/full.png` | [Source](https://raw.githubusercontent.com/ArknightsAssets/ArknightsAssets2/cn/assets/dyn/arts/characters/char_112_siege/char_112_siege_1.png) |
| `char_134_ifrit` | Unknown | `hero_art` | `assets/operators/char_134_ifrit/full.png` | [Source](https://raw.githubusercontent.com/ArknightsAssets/ArknightsAssets2/cn/assets/dyn/arts/characters/char_134_ifrit/char_134_ifrit_1.png) |
| `char_136_hsguma` | Unknown | `hero_art` | `assets/operators/char_136_hsguma/full.png` | [Source](https://raw.githubusercontent.com/ArknightsAssets/ArknightsAssets2/cn/assets/dyn/arts/characters/char_136_hsguma/char_136_hsguma_1.png) |
| `char_1502_crosly` | Unknown | `unresolved` | *None (Fallback Mode)* | [Source](https://raw.githubusercontent.com/ArknightsAssets/ArknightsAssets2/cn/assets/dyn/arts/characters/char_1502_crosly/char_1502_crosly_1.png) |
| `char_172_svrash` | Unknown | `hero_art` | `assets/operators/char_172_svrash/full.png` | [Source](https://raw.githubusercontent.com/ArknightsAssets/ArknightsAssets2/cn/assets/dyn/arts/characters/char_172_svrash/char_172_svrash_1.png) |
| `char_179_cgbird` | Unknown | `hero_art` | `assets/operators/char_179_cgbird/full.png` | [Source](https://raw.githubusercontent.com/ArknightsAssets/ArknightsAssets2/cn/assets/dyn/arts/characters/char_179_cgbird/char_179_cgbird_1.png) |
| `char_180_amgoat` | Unknown | `hero_art` | `assets/operators/char_180_amgoat/full.png` | [Source](https://raw.githubusercontent.com/ArknightsAssets/ArknightsAssets2/cn/assets/dyn/arts/characters/char_180_amgoat/char_180_amgoat_1.png) |
| `char_188_helage` | Unknown | `hero_art` | `assets/operators/char_188_helage/full.png` | [Source](https://raw.githubusercontent.com/ArknightsAssets/ArknightsAssets2/cn/assets/dyn/arts/characters/char_188_helage/char_188_helage_1.png) |
| `char_197_poca` | Unknown | `hero_art` | `assets/operators/char_197_poca/full.png` | [Source](https://raw.githubusercontent.com/ArknightsAssets/ArknightsAssets2/cn/assets/dyn/arts/characters/char_197_poca/char_197_poca_1.png) |
| `char_2012_typhon` | Unknown | `unresolved` | *None (Fallback Mode)* | [Source](https://raw.githubusercontent.com/ArknightsAssets/ArknightsAssets2/cn/assets/dyn/arts/characters/char_2012_typhon/char_2012_typhon_1.png) |
| `char_2013_cerber` | Unknown | `hero_art` | `assets/operators/char_2013_cerber/full.png` | [Source](https://raw.githubusercontent.com/ArknightsAssets/ArknightsAssets2/cn/assets/dyn/arts/characters/char_2013_cerber/char_2013_cerber_1.png) |
| `char_2023_ling` | Unknown | `hero_art` | `assets/operators/char_2023_ling/full.png` | [Source](https://raw.githubusercontent.com/ArknightsAssets/ArknightsAssets2/cn/assets/dyn/arts/characters/char_2023_ling/char_2023_ling_1.png) |
| `char_2024_chyue` | Unknown | `unresolved` | *None (Fallback Mode)* | [Source](https://raw.githubusercontent.com/ArknightsAssets/ArknightsAssets2/cn/assets/dyn/arts/characters/char_2024_chyue/char_2024_chyue_1.png) |
| `char_2025_shu` | Unknown | `unresolved` | *None (Fallback Mode)* | [Source](https://raw.githubusercontent.com/ArknightsAssets/ArknightsAssets2/cn/assets/dyn/arts/characters/char_2025_shu/char_2025_shu_1.png) |
| `char_2026_yu` | Unknown | `unresolved` | *None (Fallback Mode)* | [Source](https://raw.githubusercontent.com/ArknightsAssets/ArknightsAssets2/cn/assets/dyn/arts/characters/char_2026_yu/char_2026_yu_1.png) |
| `char_202_demkni` | Unknown | `hero_art` | `assets/operators/char_202_demkni/full.png` | [Source](https://raw.githubusercontent.com/ArknightsAssets/ArknightsAssets2/cn/assets/dyn/arts/characters/char_202_demkni/char_202_demkni_1.png) |
| `char_206_gnosis` | Unknown | `hero_art` | `assets/operators/char_206_gnosis/full.png` | [Source](https://raw.githubusercontent.com/ArknightsAssets/ArknightsAssets2/cn/assets/dyn/arts/characters/char_206_gnosis/char_206_gnosis_1.png) |
| `char_213_mostma` | Unknown | `hero_art` | `assets/operators/char_213_mostma/full.png` | [Source](https://raw.githubusercontent.com/ArknightsAssets/ArknightsAssets2/cn/assets/dyn/arts/characters/char_213_mostma/char_213_mostma_1.png) |
| `char_222_bpipe` | Unknown | `unresolved` | *None (Fallback Mode)* | [Source](https://raw.githubusercontent.com/ArknightsAssets/ArknightsAssets2/cn/assets/dyn/arts/characters/char_222_bpipe/char_222_bpipe_1.png) |
| `char_225_haak` | Unknown | `hero_art` | `assets/operators/char_225_haak/full.png` | [Source](https://raw.githubusercontent.com/ArknightsAssets/ArknightsAssets2/cn/assets/dyn/arts/characters/char_225_haak/char_225_haak_1.png) |
| `char_248_mgllan` | Unknown | `hero_art` | `assets/operators/char_248_mgllan/full.png` | [Source](https://raw.githubusercontent.com/ArknightsAssets/ArknightsAssets2/cn/assets/dyn/arts/characters/char_248_mgllan/char_248_mgllan_1.png) |
| `char_249_mlyss` | Unknown | `unresolved` | *None (Fallback Mode)* | [Source](https://raw.githubusercontent.com/ArknightsAssets/ArknightsAssets2/cn/assets/dyn/arts/characters/char_249_mlyss/char_249_mlyss_1.png) |
| `char_250_phatom` | Unknown | `hero_art` | `assets/operators/char_250_phatom/full.png` | [Source](https://raw.githubusercontent.com/ArknightsAssets/ArknightsAssets2/cn/assets/dyn/arts/characters/char_250_phatom/char_250_phatom_1.png) |
| `char_264_f12yin` | Unknown | `hero_art` | `assets/operators/char_264_f12yin/full.png` | [Source](https://raw.githubusercontent.com/ArknightsAssets/ArknightsAssets2/cn/assets/dyn/arts/characters/char_264_f12yin/char_264_f12yin_1.png) |
| `char_291_aglina` | Unknown | `hero_art` | `assets/operators/char_291_aglina/full.png` | [Source](https://raw.githubusercontent.com/ArknightsAssets/ArknightsAssets2/cn/assets/dyn/arts/characters/char_291_aglina/char_291_aglina_1.png) |
| `char_293_thorns` | Unknown | `hero_art` | `assets/operators/char_293_thorns/full.png` | [Source](https://raw.githubusercontent.com/ArknightsAssets/ArknightsAssets2/cn/assets/dyn/arts/characters/char_293_thorns/char_293_thorns_1.png) |
| `char_300_phenxi` | Unknown | `hero_art` | `assets/operators/char_300_phenxi/full.png` | [Source](https://raw.githubusercontent.com/ArknightsAssets/ArknightsAssets2/cn/assets/dyn/arts/characters/char_300_phenxi/char_300_phenxi_1.png) |
| `char_311_mudrok` | Unknown | `hero_art` | `assets/operators/char_311_mudrok/full.png` | [Source](https://raw.githubusercontent.com/ArknightsAssets/ArknightsAssets2/cn/assets/dyn/arts/characters/char_311_mudrok/char_311_mudrok_1.png) |
| `char_322_lmlee` | Unknown | `hero_art` | `assets/operators/char_322_lmlee/full.png` | [Source](https://raw.githubusercontent.com/ArknightsAssets/ArknightsAssets2/cn/assets/dyn/arts/characters/char_322_lmlee/char_322_lmlee_1.png) |
| `char_332_archet` | Unknown | `hero_art` | `assets/operators/char_332_archet/full.png` | [Source](https://raw.githubusercontent.com/ArknightsAssets/ArknightsAssets2/cn/assets/dyn/arts/characters/char_332_archet/char_332_archet_1.png) |
| `char_350_surtr` | Unknown | `hero_art` | `assets/operators/char_350_surtr/full.png` | [Source](https://raw.githubusercontent.com/ArknightsAssets/ArknightsAssets2/cn/assets/dyn/arts/characters/char_350_surtr/char_350_surtr_1.png) |
| `char_358_lisa` | Unknown | `hero_art` | `assets/operators/char_358_lisa/full.png` | [Source](https://raw.githubusercontent.com/ArknightsAssets/ArknightsAssets2/cn/assets/dyn/arts/characters/char_358_lisa/char_358_lisa_1.png) |
| `char_362_saga` | Unknown | `hero_art` | `assets/operators/char_362_saga/full.png` | [Source](https://raw.githubusercontent.com/ArknightsAssets/ArknightsAssets2/cn/assets/dyn/arts/characters/char_362_saga/char_362_saga_1.png) |
| `char_377_gdglow` | Unknown | `hero_art` | `assets/operators/char_377_gdglow/full.png` | [Source](https://raw.githubusercontent.com/ArknightsAssets/ArknightsAssets2/cn/assets/dyn/arts/characters/char_377_gdglow/char_377_gdglow_1.png) |
| `char_391_rosmon` | Unknown | `hero_art` | `assets/operators/char_391_rosmon/full.png` | [Source](https://raw.githubusercontent.com/ArknightsAssets/ArknightsAssets2/cn/assets/dyn/arts/characters/char_391_rosmon/char_391_rosmon_1.png) |
| `char_400_weedy` | Unknown | `hero_art` | `assets/operators/char_400_weedy/full.png` | [Source](https://raw.githubusercontent.com/ArknightsAssets/ArknightsAssets2/cn/assets/dyn/arts/characters/char_400_weedy/char_400_weedy_1.png) |
| `char_4010_etlchi` | Unknown | `unresolved` | *None (Fallback Mode)* | [Source](https://raw.githubusercontent.com/ArknightsAssets/ArknightsAssets2/cn/assets/dyn/arts/characters/char_4010_etlchi/char_4010_etlchi_1.png) |
| `char_4011_lessng` | Unknown | `unresolved` | *None (Fallback Mode)* | [Source](https://raw.githubusercontent.com/ArknightsAssets/ArknightsAssets2/cn/assets/dyn/arts/characters/char_4011_lessng/char_4011_lessng_1.png) |
| `char_4039_horn` | Unknown | `hero_art` | `assets/operators/char_4039_horn/full.png` | [Source](https://raw.githubusercontent.com/ArknightsAssets/ArknightsAssets2/cn/assets/dyn/arts/characters/char_4039_horn/char_4039_horn_1.png) |
| `char_4042_lumen` | Unknown | `hero_art` | `assets/operators/char_4042_lumen/full.png` | [Source](https://raw.githubusercontent.com/ArknightsAssets/ArknightsAssets2/cn/assets/dyn/arts/characters/char_4042_lumen/char_4042_lumen_1.png) |
| `char_4046_ebnhlz` | Unknown | `hero_art` | `assets/operators/char_4046_ebnhlz/full.png` | [Source](https://raw.githubusercontent.com/ArknightsAssets/ArknightsAssets2/cn/assets/dyn/arts/characters/char_4046_ebnhlz/char_4046_ebnhlz_1.png) |
| `char_4048_doroth` | Unknown | `unresolved` | *None (Fallback Mode)* | [Source](https://raw.githubusercontent.com/ArknightsAssets/ArknightsAssets2/cn/assets/dyn/arts/characters/char_4048_doroth/char_4048_doroth_1.png) |
| `char_4055_bgsnow` | Unknown | `unresolved` | *None (Fallback Mode)* | [Source](https://raw.githubusercontent.com/ArknightsAssets/ArknightsAssets2/cn/assets/dyn/arts/characters/char_4055_bgsnow/char_4055_bgsnow_1.png) |
| `char_4058_pepe` | Unknown | `unresolved` | *None (Fallback Mode)* | [Source](https://raw.githubusercontent.com/ArknightsAssets/ArknightsAssets2/cn/assets/dyn/arts/characters/char_4058_pepe/char_4058_pepe_1.png) |
| `char_4064_mlynar` | Unknown | `unresolved` | *None (Fallback Mode)* | [Source](https://raw.githubusercontent.com/ArknightsAssets/ArknightsAssets2/cn/assets/dyn/arts/characters/char_4064_mlynar/char_4064_mlynar_1.png) |
| `char_4065_judge` | Unknown | `unresolved` | *None (Fallback Mode)* | [Source](https://raw.githubusercontent.com/ArknightsAssets/ArknightsAssets2/cn/assets/dyn/arts/characters/char_4065_judge/char_4065_judge_1.png) |
| `char_4072_ironmn` | Unknown | `unresolved` | *None (Fallback Mode)* | [Source](https://raw.githubusercontent.com/ArknightsAssets/ArknightsAssets2/cn/assets/dyn/arts/characters/char_4072_ironmn/char_4072_ironmn_1.png) |
| `char_4080_lin` | Unknown | `unresolved` | *None (Fallback Mode)* | [Source](https://raw.githubusercontent.com/ArknightsAssets/ArknightsAssets2/cn/assets/dyn/arts/characters/char_4080_lin/char_4080_lin_1.png) |
| `char_4082_qiubai` | Unknown | `unresolved` | *None (Fallback Mode)* | [Source](https://raw.githubusercontent.com/ArknightsAssets/ArknightsAssets2/cn/assets/dyn/arts/characters/char_4082_qiubai/char_4082_qiubai_1.png) |
| `char_4087_ines` | Unknown | `unresolved` | *None (Fallback Mode)* | [Source](https://raw.githubusercontent.com/ArknightsAssets/ArknightsAssets2/cn/assets/dyn/arts/characters/char_4087_ines/char_4087_ines_1.png) |
| `char_4088_hodrer` | Unknown | `unresolved` | *None (Fallback Mode)* | [Source](https://raw.githubusercontent.com/ArknightsAssets/ArknightsAssets2/cn/assets/dyn/arts/characters/char_4088_hodrer/char_4088_hodrer_1.png) |
| `char_4098_vvana` | Unknown | `unresolved` | *None (Fallback Mode)* | [Source](https://raw.githubusercontent.com/ArknightsAssets/ArknightsAssets2/cn/assets/dyn/arts/characters/char_4098_vvana/char_4098_vvana_1.png) |
| `char_4116_blkkgt` | Unknown | `unresolved` | *None (Fallback Mode)* | [Source](https://raw.githubusercontent.com/ArknightsAssets/ArknightsAssets2/cn/assets/dyn/arts/characters/char_4116_blkkgt/char_4116_blkkgt_1.png) |
| `char_4117_ray` | Unknown | `unresolved` | *None (Fallback Mode)* | [Source](https://raw.githubusercontent.com/ArknightsAssets/ArknightsAssets2/cn/assets/dyn/arts/characters/char_4117_ray/char_4117_ray_1.png) |
| `char_4121_zuole` | Unknown | `unresolved` | *None (Fallback Mode)* | [Source](https://raw.githubusercontent.com/ArknightsAssets/ArknightsAssets2/cn/assets/dyn/arts/characters/char_4121_zuole/char_4121_zuole_1.png) |
| `char_4123_ela` | Unknown | `unresolved` | *None (Fallback Mode)* | [Source](https://raw.githubusercontent.com/ArknightsAssets/ArknightsAssets2/cn/assets/dyn/arts/characters/char_4123_ela/char_4123_ela_1.png) |
| `char_4133_logos` | Unknown | `unresolved` | *None (Fallback Mode)* | [Source](https://raw.githubusercontent.com/ArknightsAssets/ArknightsAssets2/cn/assets/dyn/arts/characters/char_4133_logos/char_4133_logos_1.png) |
| `char_4134_cetsyr` | Unknown | `unresolved` | *None (Fallback Mode)* | [Source](https://raw.githubusercontent.com/ArknightsAssets/ArknightsAssets2/cn/assets/dyn/arts/characters/char_4134_cetsyr/char_4134_cetsyr_1.png) |
| `char_4141_marcil` | Unknown | `unresolved` | *None (Fallback Mode)* | [Source](https://raw.githubusercontent.com/ArknightsAssets/ArknightsAssets2/cn/assets/dyn/arts/characters/char_4141_marcil/char_4141_marcil_1.png) |
| `char_4145_ulpia` | Unknown | `unresolved` | *None (Fallback Mode)* | [Source](https://raw.githubusercontent.com/ArknightsAssets/ArknightsAssets2/cn/assets/dyn/arts/characters/char_4145_ulpia/char_4145_ulpia_1.png) |
| `char_4146_nymph` | Unknown | `unresolved` | *None (Fallback Mode)* | [Source](https://raw.githubusercontent.com/ArknightsAssets/ArknightsAssets2/cn/assets/dyn/arts/characters/char_4146_nymph/char_4146_nymph_1.png) |
| `char_416_zumama` | Unknown | `hero_art` | `assets/operators/char_416_zumama/full.png` | [Source](https://raw.githubusercontent.com/ArknightsAssets/ArknightsAssets2/cn/assets/dyn/arts/characters/char_416_zumama/char_416_zumama_1.png) |
| `char_4179_monstr` | Unknown | `unresolved` | *None (Fallback Mode)* | [Source](https://raw.githubusercontent.com/ArknightsAssets/ArknightsAssets2/cn/assets/dyn/arts/characters/char_4179_monstr/char_4179_monstr_1.png) |
| `char_4182_oblvns` | Unknown | `unresolved` | *None (Fallback Mode)* | [Source](https://raw.githubusercontent.com/ArknightsAssets/ArknightsAssets2/cn/assets/dyn/arts/characters/char_4182_oblvns/char_4182_oblvns_1.png) |
| `char_4193_lemuen` | Unknown | `unresolved` | *None (Fallback Mode)* | [Source](https://raw.githubusercontent.com/ArknightsAssets/ArknightsAssets2/cn/assets/dyn/arts/characters/char_4193_lemuen/char_4193_lemuen_1.png) |
| `char_4194_rmixer` | Unknown | `unresolved` | *None (Fallback Mode)* | [Source](https://raw.githubusercontent.com/ArknightsAssets/ArknightsAssets2/cn/assets/dyn/arts/characters/char_4194_rmixer/char_4194_rmixer_1.png) |
| `char_4195_radian` | Unknown | `unresolved` | *None (Fallback Mode)* | [Source](https://raw.githubusercontent.com/ArknightsAssets/ArknightsAssets2/cn/assets/dyn/arts/characters/char_4195_radian/char_4195_radian_1.png) |
| `char_4202_haruka` | Unknown | `unresolved` | *None (Fallback Mode)* | [Source](https://raw.githubusercontent.com/ArknightsAssets/ArknightsAssets2/cn/assets/dyn/arts/characters/char_4202_haruka/char_4202_haruka_1.png) |
| `char_4212_nasti` | Unknown | `unresolved` | *None (Fallback Mode)* | [Source](https://raw.githubusercontent.com/ArknightsAssets/ArknightsAssets2/cn/assets/dyn/arts/characters/char_4212_nasti/char_4212_nasti_1.png) |
| `char_4217_makoto` | Unknown | `unresolved` | *None (Fallback Mode)* | [Source](https://raw.githubusercontent.com/ArknightsAssets/ArknightsAssets2/cn/assets/dyn/arts/characters/char_4217_makoto/char_4217_makoto_1.png) |
| `char_4226_veen` | Unknown | `unresolved` | *None (Fallback Mode)* | [Source](https://raw.githubusercontent.com/ArknightsAssets/ArknightsAssets2/cn/assets/dyn/arts/characters/char_4226_veen/char_4226_veen_1.png) |
| `char_4228_closur` | Unknown | `unresolved` | *None (Fallback Mode)* | [Source](https://raw.githubusercontent.com/ArknightsAssets/ArknightsAssets2/cn/assets/dyn/arts/characters/char_4228_closur/char_4228_closur_1.png) |
| `char_423_blemsh` | Unknown | `hero_art` | `assets/operators/char_423_blemsh/full.png` | [Source](https://raw.githubusercontent.com/ArknightsAssets/ArknightsAssets2/cn/assets/dyn/arts/characters/char_423_blemsh/char_423_blemsh_1.png) |
| `char_427_vigil` | Unknown | `unresolved` | *None (Fallback Mode)* | [Source](https://raw.githubusercontent.com/ArknightsAssets/ArknightsAssets2/cn/assets/dyn/arts/characters/char_427_vigil/char_427_vigil_1.png) |
| `char_430_fartth` | Unknown | `hero_art` | `assets/operators/char_430_fartth/full.png` | [Source](https://raw.githubusercontent.com/ArknightsAssets/ArknightsAssets2/cn/assets/dyn/arts/characters/char_430_fartth/char_430_fartth_1.png) |
| `char_437_mizuki` | Unknown | `hero_art` | `assets/operators/char_437_mizuki/full.png` | [Source](https://raw.githubusercontent.com/ArknightsAssets/ArknightsAssets2/cn/assets/dyn/arts/characters/char_437_mizuki/char_437_mizuki_1.png) |
| `char_450_necras` | Unknown | `unresolved` | *None (Fallback Mode)* | [Source](https://raw.githubusercontent.com/ArknightsAssets/ArknightsAssets2/cn/assets/dyn/arts/characters/char_450_necras/char_450_necras_1.png) |
| `char_474_glady` | Unknown | `hero_art` | `assets/operators/char_474_glady/full.png` | [Source](https://raw.githubusercontent.com/ArknightsAssets/ArknightsAssets2/cn/assets/dyn/arts/characters/char_474_glady/char_474_glady_1.png) |
| `char_479_sleach` | Unknown | `hero_art` | `assets/operators/char_479_sleach/full.png` | [Source](https://raw.githubusercontent.com/ArknightsAssets/ArknightsAssets2/cn/assets/dyn/arts/characters/char_479_sleach/char_479_sleach_1.png) |

## 3. Downstream Consumption & Portability Policy
1. **Never mutate .pen binary/JSON files directly** without Pencil MCP / editor verification.
2. **Downstream consumers** should read `reports/pen_asset_dependencies.json` to map any `assets/raw_batch/` URL to `resolved_local_path`.
3. If a hero art is missing in `assets/operators/`, consumers gracefully fall back to Rhine's card art specimen or metadata-only render mode.
