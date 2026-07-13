# Phase 15 MNQ Walk-Forward

## mnq_fvg_vol

- Params: `{'min_gap_points': 30.0, 'min_stop_points': 20.0, 'target_r': 1.0, 'expire_minutes': 40, 'z_threshold': 1.5, 'vol_lookback': 20, 'vwap_filter': True, 'tick': 0.25, 'entry_start_minute': 575, 'entry_end_minute': 900}`
- Fold+: 11%
- Ambiguity: 0.0%

| Fold | Train | Test | Chosen params | Train Sharpe | Train $ | Test $ | Test trades |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2019-06-01→2021-05-31 | 2021-06-01→2021-11-30 | — | — | $0 | $0 | 0 |
| 2 | 2019-12-01→2021-11-30 | 2021-12-01→2022-05-31 | — | — | $0 | $0 | 0 |
| 3 | 2020-06-01→2022-05-31 | 2022-06-01→2022-11-30 | — | — | $0 | $0 | 0 |
| 4 | 2020-12-01→2022-11-30 | 2022-12-01→2023-05-31 | — | — | $0 | $0 | 0 |
| 5 | 2021-06-01→2023-05-31 | 2023-06-01→2023-11-30 | — | — | $0 | $0 | 0 |
| 6 | 2021-12-01→2023-11-30 | 2023-12-01→2024-05-31 | — | — | $0 | $0 | 0 |
| 7 | 2022-06-01→2024-05-31 | 2024-06-01→2024-11-30 | — | — | $0 | $0 | 0 |
| 8 | 2022-12-01→2024-11-30 | 2024-12-01→2025-05-31 | — | — | $0 | $0 | 0 |
| 9 | 2023-06-01→2025-05-31 | 2025-06-01→2025-11-30 | min_gap_points=30.0, min_stop_points=20.0, target_r=1.0, expire_minutes=40, z_threshold=1.5, vol_lookback=20, vwap_filter=True, tick=0.25, entry_start_minute=575, entry_end_minute=900 | 4.47 | $533 | $182 | 7 |

## mnq_vol_spike

- Params: `{'z_threshold': 3.0, 'vol_lookback': 20, 'range_mult': 1.5, 'target_r': 1.0, 'expire_minutes': 10, 'min_stop_points': 15.0, 'tick': 0.25, 'entry_start_minute': 575, 'entry_end_minute': 900}`
- Fold+: 33%
- Ambiguity: 7.7%

| Fold | Train | Test | Chosen params | Train Sharpe | Train $ | Test $ | Test trades |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2019-06-01→2021-05-31 | 2021-06-01→2021-11-30 | z_threshold=2.0, vol_lookback=20, range_mult=1.5, target_r=1.5, expire_minutes=10, min_stop_points=15.0, tick=0.25, entry_start_minute=575, entry_end_minute=900 | -1.75 | $-6,043 | $-3,124 | 897 |
| 2 | 2019-12-01→2021-11-30 | 2021-12-01→2022-05-31 | z_threshold=3.0, vol_lookback=40, range_mult=1.5, target_r=1.5, expire_minutes=10, min_stop_points=15.0, tick=0.25, entry_start_minute=575, entry_end_minute=900 | -1.89 | $-4,692 | $-28 | 361 |
| 3 | 2020-06-01→2022-05-31 | 2022-06-01→2022-11-30 | z_threshold=3.0, vol_lookback=40, range_mult=1.5, target_r=1.5, expire_minutes=10, min_stop_points=15.0, tick=0.25, entry_start_minute=575, entry_end_minute=900 | -1.21 | $-3,668 | $604 | 379 |
| 4 | 2020-12-01→2022-11-30 | 2022-12-01→2023-05-31 | z_threshold=3.0, vol_lookback=40, range_mult=1.5, target_r=1.5, expire_minutes=20, min_stop_points=15.0, tick=0.25, entry_start_minute=575, entry_end_minute=900 | -0.51 | $-1,697 | $-1,525 | 437 |
| 5 | 2021-06-01→2023-05-31 | 2023-06-01→2023-11-30 | z_threshold=3.0, vol_lookback=20, range_mult=1.5, target_r=1.5, expire_minutes=20, min_stop_points=15.0, tick=0.25, entry_start_minute=575, entry_end_minute=900 | -0.45 | $-1,418 | $-397 | 383 |
| 6 | 2021-12-01→2023-11-30 | 2023-12-01→2024-05-31 | z_threshold=3.0, vol_lookback=20, range_mult=1.5, target_r=1.5, expire_minutes=20, min_stop_points=15.0, tick=0.25, entry_start_minute=575, entry_end_minute=900 | -0.07 | $-248 | $1,644 | 436 |
| 7 | 2022-06-01→2024-05-31 | 2024-06-01→2024-11-30 | z_threshold=3.0, vol_lookback=20, range_mult=1.5, target_r=1.5, expire_minutes=20, min_stop_points=15.0, tick=0.25, entry_start_minute=575, entry_end_minute=900 | 0.65 | $1,922 | $-3,250 | 395 |
| 8 | 2022-12-01→2024-11-30 | 2024-12-01→2025-05-31 | z_threshold=3.0, vol_lookback=20, range_mult=1.5, target_r=1.5, expire_minutes=10, min_stop_points=15.0, tick=0.25, entry_start_minute=575, entry_end_minute=900 | -0.73 | $-2,320 | $1,560 | 323 |
| 9 | 2023-06-01→2025-05-31 | 2025-06-01→2025-11-30 | z_threshold=3.0, vol_lookback=20, range_mult=1.5, target_r=1.0, expire_minutes=10, min_stop_points=15.0, tick=0.25, entry_start_minute=575, entry_end_minute=900 | 0.12 | $381 | $-2,775 | 404 |

## mnq_fvg_3m

- Params: `{'min_gap_points': 30.0, 'min_stop_points': 25.0, 'target_r': 1.0, 'expire_minutes': 60, 'entry_mode': 'mid', 'vwap_filter': False, 'tick': 0.25, 'entry_start_minute': 575, 'entry_end_minute': 900}`
- Fold+: 22%
- Ambiguity: 6.0%

| Fold | Train | Test | Chosen params | Train Sharpe | Train $ | Test $ | Test trades |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2019-06-01→2021-05-31 | 2021-06-01→2021-11-30 | min_gap_points=30.0, min_stop_points=15.0, target_r=1.0, expire_minutes=30, entry_mode=mid, vwap_filter=False, tick=0.25, entry_start_minute=575, entry_end_minute=900 | -2.68 | $-561 | $-136 | 9 |
| 2 | 2019-12-01→2021-11-30 | 2021-12-01→2022-05-31 | min_gap_points=30.0, min_stop_points=25.0, target_r=1.0, expire_minutes=30, entry_mode=mid, vwap_filter=False, tick=0.25, entry_start_minute=575, entry_end_minute=900 | -3.26 | $-807 | $-6 | 95 |
| 3 | 2020-06-01→2022-05-31 | 2022-06-01→2022-11-30 | min_gap_points=30.0, min_stop_points=25.0, target_r=1.5, expire_minutes=30, entry_mode=mid, vwap_filter=False, tick=0.25, entry_start_minute=575, entry_end_minute=900 | -0.53 | $-225 | $-237 | 35 |
| 4 | 2020-12-01→2022-11-30 | 2022-12-01→2023-05-31 | min_gap_points=30.0, min_stop_points=25.0, target_r=1.0, expire_minutes=30, entry_mode=mid, vwap_filter=False, tick=0.25, entry_start_minute=575, entry_end_minute=900 | -0.02 | $-9 | $36 | 19 |
| 5 | 2021-06-01→2023-05-31 | 2023-06-01→2023-11-30 | min_gap_points=30.0, min_stop_points=25.0, target_r=1.5, expire_minutes=60, entry_mode=mid, vwap_filter=True, tick=0.25, entry_start_minute=575, entry_end_minute=900 | 1.12 | $583 | $-254 | 20 |
| 6 | 2021-12-01→2023-11-30 | 2023-12-01→2024-05-31 | min_gap_points=30.0, min_stop_points=25.0, target_r=1.0, expire_minutes=60, entry_mode=mid, vwap_filter=True, tick=0.25, entry_start_minute=575, entry_end_minute=900 | 1.35 | $620 | $-396 | 21 |
| 7 | 2022-06-01→2024-05-31 | 2024-06-01→2024-11-30 | min_gap_points=30.0, min_stop_points=25.0, target_r=1.0, expire_minutes=60, entry_mode=mid, vwap_filter=False, tick=0.25, entry_start_minute=575, entry_end_minute=900 | 0.95 | $339 | $29 | 57 |
| 8 | 2022-12-01→2024-11-30 | 2024-12-01→2025-05-31 | min_gap_points=30.0, min_stop_points=25.0, target_r=1.0, expire_minutes=60, entry_mode=mid, vwap_filter=False, tick=0.25, entry_start_minute=575, entry_end_minute=900 | 0.04 | $14 | $-642 | 111 |
| 9 | 2023-06-01→2025-05-31 | 2025-06-01→2025-11-30 | min_gap_points=30.0, min_stop_points=25.0, target_r=1.0, expire_minutes=60, entry_mode=mid, vwap_filter=False, tick=0.25, entry_start_minute=575, entry_end_minute=900 | -1.33 | $-712 | $-46 | 65 |

## mnq_vwap_rev

- Params: `{'mode': 'reversion', 'band_k': 1.25, 'stop_atr': 1.0, 'target_r': 1.5, 'expire_minutes': 30, 'min_stop_points': 15.0, 'atr_n': 14, 'entry_start_minute': 585, 'entry_end_minute': 900}`
- Fold+: 0%
- Ambiguity: 24.5%

| Fold | Train | Test | Chosen params | Train Sharpe | Train $ | Test $ | Test trades |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2019-06-01→2021-05-31 | 2021-06-01→2021-11-30 | mode=reversion, band_k=2.25, stop_atr=1.0, target_r=1.5, expire_minutes=15, min_stop_points=15.0, atr_n=14, entry_start_minute=585, entry_end_minute=900 | -1.73 | $-3,489 | $-1,247 | 483 |
| 2 | 2019-12-01→2021-11-30 | 2021-12-01→2022-05-31 | mode=reversion, band_k=2.25, stop_atr=1.0, target_r=1.0, expire_minutes=30, min_stop_points=15.0, atr_n=14, entry_start_minute=585, entry_end_minute=900 | -1.93 | $-3,528 | $-1,281 | 538 |
| 3 | 2020-06-01→2022-05-31 | 2022-06-01→2022-11-30 | mode=reversion, band_k=2.25, stop_atr=1.0, target_r=1.5, expire_minutes=30, min_stop_points=15.0, atr_n=14, entry_start_minute=585, entry_end_minute=900 | -1.90 | $-4,770 | $-1,423 | 492 |
| 4 | 2020-12-01→2022-11-30 | 2022-12-01→2023-05-31 | mode=reversion, band_k=2.25, stop_atr=1.0, target_r=1.5, expire_minutes=30, min_stop_points=15.0, atr_n=14, entry_start_minute=585, entry_end_minute=900 | -1.91 | $-4,824 | $-646 | 504 |
| 5 | 2021-06-01→2023-05-31 | 2023-06-01→2023-11-30 | mode=reversion, band_k=1.75, stop_atr=1.0, target_r=1.5, expire_minutes=15, min_stop_points=15.0, atr_n=14, entry_start_minute=585, entry_end_minute=900 | -1.53 | $-3,671 | $-923 | 514 |
| 6 | 2021-12-01→2023-11-30 | 2023-12-01→2024-05-31 | mode=reversion, band_k=1.75, stop_atr=1.0, target_r=1.5, expire_minutes=15, min_stop_points=15.0, atr_n=14, entry_start_minute=585, entry_end_minute=900 | -1.25 | $-3,001 | $-382 | 535 |
| 7 | 2022-06-01→2024-05-31 | 2024-06-01→2024-11-30 | mode=reversion, band_k=1.75, stop_atr=1.0, target_r=1.5, expire_minutes=15, min_stop_points=15.0, atr_n=14, entry_start_minute=585, entry_end_minute=900 | -1.06 | $-2,424 | $-218 | 524 |
| 8 | 2022-12-01→2024-11-30 | 2024-12-01→2025-05-31 | mode=reversion, band_k=1.75, stop_atr=1.0, target_r=1.5, expire_minutes=15, min_stop_points=15.0, atr_n=14, entry_start_minute=585, entry_end_minute=900 | -1.29 | $-2,947 | $-2,665 | 498 |
| 9 | 2023-06-01→2025-05-31 | 2025-06-01→2025-11-30 | mode=reversion, band_k=1.25, stop_atr=1.0, target_r=1.5, expire_minutes=30, min_stop_points=15.0, atr_n=14, entry_start_minute=585, entry_end_minute=900 | -1.23 | $-3,183 | $-1,867 | 442 |

## mnq_fvg_1m

- Params: `{'min_gap_points': 35.0, 'min_stop_points': 15.0, 'target_r': 1.5, 'expire_minutes': 40, 'entry_mode': 'mid', 'vwap_filter': True, 'tick': 0.25, 'entry_start_minute': 575, 'entry_end_minute': 900}`
- Fold+: 33%
- Ambiguity: 21.0%

| Fold | Train | Test | Chosen params | Train Sharpe | Train $ | Test $ | Test trades |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2019-06-01→2021-05-31 | 2021-06-01→2021-11-30 | min_gap_points=25.0, min_stop_points=15.0, target_r=1.5, expire_minutes=40, entry_mode=mid, vwap_filter=True, tick=0.25, entry_start_minute=575, entry_end_minute=900 | -1.07 | $-186 | $148 | 5 |
| 2 | 2019-12-01→2021-11-30 | 2021-12-01→2022-05-31 | min_gap_points=25.0, min_stop_points=15.0, target_r=1.5, expire_minutes=40, entry_mode=mid, vwap_filter=True, tick=0.25, entry_start_minute=575, entry_end_minute=900 | 0.08 | $15 | $-730 | 87 |
| 3 | 2020-06-01→2022-05-31 | 2022-06-01→2022-11-30 | min_gap_points=25.0, min_stop_points=20.0, target_r=1.0, expire_minutes=20, entry_mode=mid, vwap_filter=True, tick=0.25, entry_start_minute=575, entry_end_minute=900 | 0.74 | $194 | $-342 | 32 |
| 4 | 2020-12-01→2022-11-30 | 2022-12-01→2023-05-31 | min_gap_points=35.0, min_stop_points=15.0, target_r=1.0, expire_minutes=20, entry_mode=mid, vwap_filter=False, tick=0.25, entry_start_minute=575, entry_end_minute=900 | -0.22 | $-27 | $13 | 2 |
| 5 | 2021-06-01→2023-05-31 | 2023-06-01→2023-11-30 | min_gap_points=25.0, min_stop_points=20.0, target_r=1.0, expire_minutes=20, entry_mode=mid, vwap_filter=False, tick=0.25, entry_start_minute=575, entry_end_minute=900 | 0.70 | $246 | $-48 | 7 |
| 6 | 2021-12-01→2023-11-30 | 2023-12-01→2024-05-31 | min_gap_points=35.0, min_stop_points=15.0, target_r=1.0, expire_minutes=40, entry_mode=mid, vwap_filter=False, tick=0.25, entry_start_minute=575, entry_end_minute=900 | 1.34 | $186 | $-46 | 3 |
| 7 | 2022-06-01→2024-05-31 | 2024-06-01→2024-11-30 | min_gap_points=25.0, min_stop_points=20.0, target_r=1.0, expire_minutes=40, entry_mode=mid, vwap_filter=False, tick=0.25, entry_start_minute=575, entry_end_minute=900 | -0.69 | $-172 | $-88 | 67 |
| 8 | 2022-12-01→2024-11-30 | 2024-12-01→2025-05-31 | min_gap_points=25.0, min_stop_points=15.0, target_r=1.5, expire_minutes=40, entry_mode=mid, vwap_filter=True, tick=0.25, entry_start_minute=575, entry_end_minute=900 | 0.60 | $136 | $-820 | 98 |
| 9 | 2023-06-01→2025-05-31 | 2025-06-01→2025-11-30 | min_gap_points=35.0, min_stop_points=15.0, target_r=1.5, expire_minutes=40, entry_mode=mid, vwap_filter=True, tick=0.25, entry_start_minute=575, entry_end_minute=900 | -0.25 | $-48 | $251 | 13 |

## mnq_vwap_pb

- Params: `{'mode': 'pullback', 'band_k': 1.0, 'stop_atr': 1.0, 'target_r': 1.0, 'expire_minutes': 15, 'min_stop_points': 15.0, 'atr_n': 14, 'entry_start_minute': 585, 'entry_end_minute': 900}`
- Fold+: 0%
- Ambiguity: 17.0%

| Fold | Train | Test | Chosen params | Train Sharpe | Train $ | Test $ | Test trades |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2019-06-01→2021-05-31 | 2021-06-01→2021-11-30 | mode=pullback, band_k=1.0, stop_atr=0.75, target_r=1.5, expire_minutes=15, min_stop_points=15.0, atr_n=14, entry_start_minute=585, entry_end_minute=900 | -2.08 | $-3,249 | $-1,893 | 327 |
| 2 | 2019-12-01→2021-11-30 | 2021-12-01→2022-05-31 | mode=pullback, band_k=1.0, stop_atr=0.75, target_r=1.5, expire_minutes=30, min_stop_points=15.0, atr_n=14, entry_start_minute=585, entry_end_minute=900 | -2.61 | $-4,367 | $-3,087 | 467 |
| 3 | 2020-06-01→2022-05-31 | 2022-06-01→2022-11-30 | mode=pullback, band_k=1.0, stop_atr=1.25, target_r=1.5, expire_minutes=15, min_stop_points=15.0, atr_n=14, entry_start_minute=585, entry_end_minute=900 | -2.04 | $-4,633 | $-2,009 | 398 |
| 4 | 2020-12-01→2022-11-30 | 2022-12-01→2023-05-31 | mode=pullback, band_k=1.0, stop_atr=1.25, target_r=1.5, expire_minutes=15, min_stop_points=15.0, atr_n=14, entry_start_minute=585, entry_end_minute=900 | -2.33 | $-5,340 | $-2,596 | 386 |
| 5 | 2021-06-01→2023-05-31 | 2023-06-01→2023-11-30 | mode=pullback, band_k=1.0, stop_atr=1.0, target_r=1.5, expire_minutes=30, min_stop_points=15.0, atr_n=14, entry_start_minute=585, entry_end_minute=900 | -2.66 | $-5,774 | $-2,300 | 437 |
| 6 | 2021-12-01→2023-11-30 | 2023-12-01→2024-05-31 | mode=pullback, band_k=1.0, stop_atr=1.25, target_r=1.0, expire_minutes=15, min_stop_points=15.0, atr_n=14, entry_start_minute=585, entry_end_minute=900 | -2.70 | $-5,756 | $-1,080 | 457 |
| 7 | 2022-06-01→2024-05-31 | 2024-06-01→2024-11-30 | mode=pullback, band_k=1.0, stop_atr=1.0, target_r=1.0, expire_minutes=15, min_stop_points=15.0, atr_n=14, entry_start_minute=585, entry_end_minute=900 | -2.61 | $-4,430 | $-1,056 | 464 |
| 8 | 2022-12-01→2024-11-30 | 2024-12-01→2025-05-31 | mode=pullback, band_k=1.0, stop_atr=0.75, target_r=1.0, expire_minutes=15, min_stop_points=15.0, atr_n=14, entry_start_minute=585, entry_end_minute=900 | -2.12 | $-3,581 | $-1,448 | 455 |
| 9 | 2023-06-01→2025-05-31 | 2025-06-01→2025-11-30 | mode=pullback, band_k=1.0, stop_atr=1.0, target_r=1.0, expire_minutes=15, min_stop_points=15.0, atr_n=14, entry_start_minute=585, entry_end_minute=900 | -2.01 | $-4,064 | $-294 | 383 |

