# Phase 12 Report — GC Deep Parameter Search (Lucid Flex 50K)

Date: 2026-07-10. Expanded grids on Phase 11 survivors; fold-stability ranking.

## TL;DR

Best deep-search candidate: `GC12 macro_nfp` — **57.5%** 50K pass, 67% positive WF folds, grid size 216. Compare to Phase 11 macro_nfp_cpi (53.9% pass, holdout failed).

## Method

- 6 folds, 18m/6m, grid through 2025-12-31
- Expanded axes: pre-range, post-delay, target R, expire, risk cap, min-range filter, long-only; NFP/CPI/FOMC split
- Rank: Lucid 50K pass → fold stability → UPI
- 2026 holdout: single run after selection (no re-tune)

- Total combos searched: **4932**

## Leaderboard (top)

| Candidate | Pass % | Fold+ % | Net $ | UPI | 2025 $ |
| --- | --- | --- | --- | --- | --- |
| GC12 macro_nfp | 57.5% | 67% | $4,430 | 14.8 | $-4,138 |
| GC12 macro_nfp_cpi | 40.4% | 67% | $4,599 | 5.7 | $-2,993 |
| GC12 macro_cpi | 36.8% | 50% | $1,354 | 4.6 | $-2,738 |
| GC12 comex_orb_deep | 28.1% | 67% | $13,936 | 2.3 | $9,038 |
| GC12 nr_comex_deep | 27.4% | 50% | $2,906 | 2.4 | $5,079 |
| GC12 ny_orb_deep | 21.7% | 50% | $-1,044 | -0.2 | $3,769 |
| GC12 macro_fomc | 19.1% | 50% | $-102 | -1.8 | $-766 |

## Selected params (last WF fold)

- **macro_nfp_cpi** (1296 combos): `{'macro_kind': 'nfp_cpi', 'release_minute': 510, 'pre_range_minutes': 15, 'post_delay_minutes': 5, 'target_r': 0.75, 'expire_minutes': 60, 'max_risk_points': 5.0, 'min_range_points': 0.0, 'long_only': True}`
- **macro_nfp** (216 combos): `{'macro_kind': 'nfp', 'release_minute': 510, 'pre_range_minutes': 15, 'post_delay_minutes': 5, 'target_r': 1.0, 'expire_minutes': 90, 'max_risk_points': 5.0, 'long_only': True}`
- **macro_cpi** (216 combos): `{'macro_kind': 'cpi', 'release_minute': 510, 'pre_range_minutes': 15, 'post_delay_minutes': 5, 'target_r': 1.0, 'expire_minutes': 60, 'max_risk_points': 5.0, 'long_only': True}`
- **macro_fomc** (324 combos): `{'macro_kind': 'fomc', 'release_minute': 840, 'pre_range_minutes': 45, 'post_delay_minutes': 5, 'target_r': 1.0, 'expire_minutes': 60, 'max_risk_points': 5.0, 'long_only': False}`
- **ny_orb_deep** (1296 combos): `{'anchor_minute': 570, 'range_minutes': 30, 'target_r': 1.5, 'expire_minutes': 60, 'min_width_ratio': 0.3, 'max_width_ratio': 0.7, 'max_risk_points': 5.0, 'long_only': True}`
- **comex_orb_deep** (1296 combos): `{'anchor_minute': 500, 'range_minutes': 15, 'target_r': 1.0, 'expire_minutes': 120, 'min_width_ratio': 0.25, 'max_width_ratio': 1000000000.0, 'max_risk_points': 5.0, 'long_only': True}`
- **nr_comex_deep** (288 combos): `{'anchor_minute': 500, 'range_minutes': 45, 'target_r': 1.5, 'expire_minutes': 120, 'nr_n': 10, 'mode': 'either', 'max_risk_points': 4.0, 'long_only': True}`

## 2026 holdout

# Phase 12 GC Holdout (2026)

Single run 2026-01-01 → 2026-07-10. Frozen Phase 12 params — no re-tune.

| Family | Trades | Net $ | Pass MC % |
| --- | --- | --- | --- |
| macro_fomc | 4 | $3,388 | 100.0% |
| macro_cpi | 8 | $-2,554 | 0.0% |
| macro_nfp | 4 | $-1,152 | 0.0% |
| comex_orb_deep | 39 | $-8,822 | 1.3% |


## Recommendation

Deep search cannot invent a durable edge if 2025–2026 regimes broke the macro release pattern. Prefer candidates with **high fold stability AND non-negative 2025**, then confirm holdout once. If none survive, stay on MNQ ORB-W; consider MGC micro for gold sizing.

## Artifacts

| File | Content |
| --- | --- |
| `data/reports/gc/phase12_leaderboard.md` | Ranking |
| `data/reports/gc/phase12_walk_forward.md` | Fold tables |
| `config/gc_phase12.yaml` | Grids |
