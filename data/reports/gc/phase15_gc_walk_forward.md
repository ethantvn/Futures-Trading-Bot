# Phase 15 GC Walk-Forward

## gc_fvg_vol

- Params: `{'min_gap_points': 3.0, 'min_stop_points': 3.5, 'max_risk_points': 5.0, 'target_r': 1.5, 'expire_minutes': 40, 'z_threshold': 2.0, 'vol_lookback': 20, 'vwap_filter': True, 'tick': 0.1, 'entry_start_minute': 575, 'entry_end_minute': 960}`
- Fold+: 50%
- Ambiguity: 8.4%

| Fold | Train | Test | Chosen params | Train Sharpe | Train $ | Test $ | Test trades |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2021-06-11→2022-11-30 | 2022-12-01→2023-05-31 | min_gap_points=3.0, min_stop_points=3.5, max_risk_points=3.0, target_r=1.5, expire_minutes=40, z_threshold=1.5, vol_lookback=20, vwap_filter=True, tick=0.1, entry_start_minute=575, entry_end_minute=960 | 4.82 | $2,522 | $-388 | 6 |
| 2 | 2021-12-01→2023-05-31 | 2023-06-01→2023-11-30 | min_gap_points=3.0, min_stop_points=3.5, max_risk_points=3.0, target_r=1.5, expire_minutes=40, z_threshold=1.5, vol_lookback=20, vwap_filter=True, tick=0.1, entry_start_minute=575, entry_end_minute=960 | 1.94 | $1,126 | $1,132 | 6 |
| 3 | 2022-06-01→2023-11-30 | 2023-12-01→2024-05-31 | — | — | $0 | $0 | 0 |
| 4 | 2022-12-01→2024-05-31 | 2024-06-01→2024-11-30 | min_gap_points=3.0, min_stop_points=3.5, max_risk_points=3.0, target_r=1.5, expire_minutes=40, z_threshold=1.5, vol_lookback=20, vwap_filter=True, tick=0.1, entry_start_minute=575, entry_end_minute=960 | 4.38 | $2,000 | $212 | 11 |
| 5 | 2023-06-01→2024-11-30 | 2024-12-01→2025-05-31 | min_gap_points=3.0, min_stop_points=3.5, max_risk_points=5.0, target_r=1.5, expire_minutes=40, z_threshold=1.5, vol_lookback=20, vwap_filter=True, tick=0.1, entry_start_minute=575, entry_end_minute=960 | 9.71 | $5,950 | $-5,377 | 29 |
| 6 | 2023-12-01→2025-05-31 | 2025-06-01→2025-11-30 | min_gap_points=3.0, min_stop_points=3.5, max_risk_points=5.0, target_r=1.5, expire_minutes=40, z_threshold=2.0, vol_lookback=20, vwap_filter=True, tick=0.1, entry_start_minute=575, entry_end_minute=960 | 1.74 | $1,540 | $5,737 | 31 |

## gc_fvg_1m

- Params: `{'min_gap_points': 2.5, 'min_stop_points': 3.5, 'max_risk_points': 5.0, 'target_r': 1.5, 'expire_minutes': 40, 'entry_mode': 'mid', 'vwap_filter': True, 'tick': 0.1, 'entry_start_minute': 575, 'entry_end_minute': 960}`
- Fold+: 50%
- Ambiguity: 5.9%

| Fold | Train | Test | Chosen params | Train Sharpe | Train $ | Test $ | Test trades |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2021-06-11→2022-11-30 | 2022-12-01→2023-05-31 | min_gap_points=3.5, min_stop_points=2.8, max_risk_points=3.0, target_r=1.0, expire_minutes=20, entry_mode=mid, vwap_filter=False, tick=0.1, entry_start_minute=575, entry_end_minute=960 | 3.98 | $970 | $-321 | 7 |
| 2 | 2021-12-01→2023-05-31 | 2023-06-01→2023-11-30 | min_gap_points=2.5, min_stop_points=3.5, max_risk_points=3.0, target_r=1.5, expire_minutes=40, entry_mode=mid, vwap_filter=True, tick=0.1, entry_start_minute=575, entry_end_minute=960 | 0.42 | $589 | $1,294 | 17 |
| 3 | 2022-06-01→2023-11-30 | 2023-12-01→2024-05-31 | min_gap_points=2.5, min_stop_points=3.5, max_risk_points=3.0, target_r=1.5, expire_minutes=40, entry_mode=mid, vwap_filter=True, tick=0.1, entry_start_minute=575, entry_end_minute=960 | 1.28 | $1,731 | $759 | 32 |
| 4 | 2022-12-01→2024-05-31 | 2024-06-01→2024-11-30 | min_gap_points=2.5, min_stop_points=3.5, max_risk_points=3.0, target_r=1.5, expire_minutes=20, entry_mode=mid, vwap_filter=True, tick=0.1, entry_start_minute=575, entry_end_minute=960 | 2.51 | $2,988 | $3,070 | 35 |
| 5 | 2023-06-01→2024-11-30 | 2024-12-01→2025-05-31 | min_gap_points=3.5, min_stop_points=3.5, max_risk_points=5.0, target_r=1.5, expire_minutes=20, entry_mode=mid, vwap_filter=True, tick=0.1, entry_start_minute=575, entry_end_minute=960 | 5.88 | $4,281 | $-4,775 | 35 |
| 6 | 2023-12-01→2025-05-31 | 2025-06-01→2025-11-30 | min_gap_points=2.5, min_stop_points=3.5, max_risk_points=5.0, target_r=1.5, expire_minutes=40, entry_mode=mid, vwap_filter=True, tick=0.1, entry_start_minute=575, entry_end_minute=960 | 1.65 | $6,077 | $-622 | 129 |

## gc_vol_spike

- Params: `{'z_threshold': 3.0, 'vol_lookback': 40, 'range_mult': 1.5, 'target_r': 1.0, 'expire_minutes': 15, 'min_stop_points': 2.8, 'max_risk_points': 5.0, 'tick': 0.1, 'entry_start_minute': 575, 'entry_end_minute': 960}`
- Fold+: 0%
- Ambiguity: 3.5%

| Fold | Train | Test | Chosen params | Train Sharpe | Train $ | Test $ | Test trades |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2021-06-11→2022-11-30 | 2022-12-01→2023-05-31 | z_threshold=2.5, vol_lookback=40, range_mult=1.5, target_r=1.5, expire_minutes=15, min_stop_points=2.8, max_risk_points=3.0, tick=0.1, entry_start_minute=575, entry_end_minute=960 | -1.59 | $-21,916 | $-305 | 495 |
| 2 | 2021-12-01→2023-05-31 | 2023-06-01→2023-11-30 | z_threshold=2.5, vol_lookback=40, range_mult=1.5, target_r=1.5, expire_minutes=30, min_stop_points=2.8, max_risk_points=3.0, tick=0.1, entry_start_minute=575, entry_end_minute=960 | -1.14 | $-16,380 | $-8,225 | 385 |
| 3 | 2022-06-01→2023-11-30 | 2023-12-01→2024-05-31 | z_threshold=3.0, vol_lookback=40, range_mult=1.5, target_r=1.5, expire_minutes=15, min_stop_points=2.8, max_risk_points=3.0, tick=0.1, entry_start_minute=575, entry_end_minute=960 | -0.61 | $-8,157 | $-3,859 | 408 |
| 4 | 2022-12-01→2024-05-31 | 2024-06-01→2024-11-30 | z_threshold=3.0, vol_lookback=40, range_mult=1.5, target_r=1.5, expire_minutes=15, min_stop_points=2.8, max_risk_points=5.0, tick=0.1, entry_start_minute=575, entry_end_minute=960 | -0.21 | $-3,215 | $-20,361 | 427 |
| 5 | 2023-06-01→2024-11-30 | 2024-12-01→2025-05-31 | z_threshold=3.0, vol_lookback=40, range_mult=1.5, target_r=1.5, expire_minutes=15, min_stop_points=2.8, max_risk_points=5.0, tick=0.1, entry_start_minute=575, entry_end_minute=960 | -1.55 | $-23,679 | $-20,174 | 448 |
| 6 | 2023-12-01→2025-05-31 | 2025-06-01→2025-11-30 | z_threshold=3.0, vol_lookback=40, range_mult=1.5, target_r=1.0, expire_minutes=15, min_stop_points=2.8, max_risk_points=5.0, tick=0.1, entry_start_minute=575, entry_end_minute=960 | -1.68 | $-25,222 | $-19,916 | 497 |

## gc_vwap_rev

- Params: `{'mode': 'reversion', 'band_k': 1.75, 'stop_atr': 1.0, 'target_r': 1.5, 'expire_minutes': 20, 'min_stop_points': 2.8, 'max_risk_points': 5.0, 'atr_n': 14, 'entry_start_minute': 585, 'entry_end_minute': 960}`
- Fold+: 17%
- Ambiguity: 18.2%

| Fold | Train | Test | Chosen params | Train Sharpe | Train $ | Test $ | Test trades |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2021-06-11→2022-11-30 | 2022-12-01→2023-05-31 | mode=reversion, band_k=1.25, stop_atr=0.75, target_r=1.5, expire_minutes=20, min_stop_points=2.8, max_risk_points=5.0, atr_n=14, entry_start_minute=585, entry_end_minute=960 | -2.23 | $-17,771 | $-8,323 | 221 |
| 2 | 2021-12-01→2023-05-31 | 2023-06-01→2023-11-30 | mode=reversion, band_k=2.25, stop_atr=1.0, target_r=1.5, expire_minutes=20, min_stop_points=2.8, max_risk_points=3.0, atr_n=14, entry_start_minute=585, entry_end_minute=960 | -2.58 | $-21,504 | $-2,701 | 236 |
| 3 | 2022-06-01→2023-11-30 | 2023-12-01→2024-05-31 | mode=reversion, band_k=2.25, stop_atr=1.0, target_r=1.5, expire_minutes=20, min_stop_points=2.8, max_risk_points=3.0, atr_n=14, entry_start_minute=585, entry_end_minute=960 | -1.26 | $-10,512 | $-7,784 | 263 |
| 4 | 2022-12-01→2024-05-31 | 2024-06-01→2024-11-30 | mode=reversion, band_k=1.75, stop_atr=1.0, target_r=1.5, expire_minutes=20, min_stop_points=2.8, max_risk_points=5.0, atr_n=14, entry_start_minute=585, entry_end_minute=960 | -1.73 | $-14,301 | $-6,534 | 280 |
| 5 | 2023-06-01→2024-11-30 | 2024-12-01→2025-05-31 | mode=reversion, band_k=1.75, stop_atr=1.0, target_r=1.5, expire_minutes=20, min_stop_points=2.8, max_risk_points=5.0, atr_n=14, entry_start_minute=585, entry_end_minute=960 | -1.41 | $-12,200 | $-5,297 | 241 |
| 6 | 2023-12-01→2025-05-31 | 2025-06-01→2025-11-30 | mode=reversion, band_k=1.75, stop_atr=1.0, target_r=1.5, expire_minutes=20, min_stop_points=2.8, max_risk_points=5.0, atr_n=14, entry_start_minute=585, entry_end_minute=960 | -2.05 | $-16,979 | $956 | 241 |

