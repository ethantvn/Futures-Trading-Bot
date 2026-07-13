# Phase 11 Report — Gold (GC) Lucid Flex 50K Research

Date: 2026-07-10. Full-size COMEX GC, gold-native strategy families.

## TL;DR

**No GC strategy clears all success criteria for Lucid 50K eval.** Best walk-forward OOS was `GC macro_nfp_cpi` (53.9% pass) but **2026 holdout collapsed** (17 trades, −$1,366, 11.3% MC pass). **Stay on validated MNQ ORB-W (~64% pass on 25K).** Optional next step: **MGC micro** sizing study.

## Task 0 — Roll calendar

Restricted to liquid months {G,J,M,Q,V,Z} with `confirm_sessions=2`. Rebuilt via `build_bars.py --config config/data_gc.yaml`.

## Sizing check (1 full-size GC vs $2,000 MLL)

Per-trade caps (3–5 pts) can fit the $300–500 band, but **P95 daily RTH range ($7,810) exceeds the $2,000 MLL**. Strategies need 1 trade/day discipline and capped stops; blow risk remains elevated vs MNQ.

- Median daily RTH range: ~$1,930
- P95 daily RTH range: ~$7,810

## Walk-forward

- 6 folds, 18m train / 6m test, grid through 2025-12-31
- Holdout 2026: run once via `--holdout` on finalists

## Macro-day baseline (COMEX ORB, capped 4pt stop)

- Macro release days: 173 trades, net $-3,394 (avg $-20)
- Non-macro: 958 trades, net $-22,704 (avg $-24)

## Top candidates (50K pass @1 GC)

| Candidate | Pass % | Net $ | UPI | MaxDD |
| --- | --- | --- | --- | --- |
| GC macro_nfp_cpi | 53.9% | $12,124 | 15.1 | $-5,566 |
| GC ny_orb | 25.6% | $2,104 | 0.1 | $-17,918 |
| GC comex_orb | 21.2% | $-3,554 | -0.1 | $-19,014 |
| GC nr_comex | 15.0% | $-8,294 | -1.6 | $-13,768 |
| GC london_orb | 12.8% | $-35,756 | -0.8 | $-37,498 |
| GC vwap_trend | 10.0% | $-35,806 | -1.2 | $-39,002 |
| GC vwap_reversion | 2.1% | $-58,535 | -0.6 | $-61,277 |

## Rejected / failed families

- **globex_orb**: no OOS trades after walk-forward
- **macro_fomc**: no OOS trades after walk-forward
- **GC ny_orb**: 25.6% pass — below 30% bar
- **GC comex_orb**: 21.2% pass — below 30% bar
- **GC nr_comex**: 15.0% pass — below 30% bar
- **GC london_orb**: 12.8% pass — below 30% bar
- **GC vwap_trend**: 10.0% pass — below 30% bar
- **GC vwap_reversion**: 2.1% pass — below 30% bar

## Selected params (last WF fold)

- **comex_orb**: `{'anchor_minute': 500, 'range_minutes': 30, 'target_r': 1.0, 'expire_minutes': 120, 'min_width_ratio': 0.25, 'max_width_ratio': 1000000000.0, 'max_risk_points': 5.0}`
- **ny_orb**: `{'anchor_minute': 570, 'range_minutes': 30, 'target_r': 1.5, 'expire_minutes': 120, 'min_width_ratio': 0.25, 'max_width_ratio': 0.7, 'max_risk_points': 5.0}`
- **london_orb**: `{'anchor_minute': 330, 'range_minutes': 30, 'target_r': 1.5, 'expire_minutes': 120, 'min_width_ratio': 0.0, 'max_width_ratio': 1000000000.0, 'max_risk_points': 5.0}`
- **globex_orb**: `{}`
- **nr_comex**: `{'anchor_minute': 500, 'range_minutes': 30, 'target_r': 1.0, 'expire_minutes': 120, 'nr_n': 7, 'mode': 'either', 'max_risk_points': 4.0}`
- **macro_nfp_cpi**: `{'macro_kind': 'nfp_cpi', 'release_minute': 510, 'pre_range_minutes': 30, 'target_r': 1.0, 'expire_minutes': 90, 'max_risk_points': 5.0}`
- **macro_fomc**: `{}`
- **vwap_trend**: `{'stop_atr': 1.5, 'target_r': 1.5, 'expire_minutes': 60, 'entry_start_minute': 540, 'max_risk_points': 4.0}`
- **vwap_reversion**: `{'extension_atr': 2.0, 'stop_atr': 1.0, 'target_r': 1.0, 'expire_minutes': 45, 'entry_start_minute': 540, 'max_risk_points': 3.0}`

## 2026 holdout (single run, frozen params)

# Phase 11 GC Holdout (2026)

Single run 2026-01-01 → 2026-07-10. Frozen params from walk-forward.

| Family | Trades | Net $ | Pass MC % |
| --- | --- | --- | --- |
| macro_nfp_cpi | 17 | $-1,366 | 11.3% |

## Recommendation

1. **Do not deploy full-size GC on Lucid 50K** — holdout failed. 2. **Primary eval:** MNQ ORB-W long-only + skipMon @ 1 micro (~64% pass). 3. **If pursuing gold:** ingest MGC micro data and re-run with $10/pt sizing.

## Artifacts

| File | Content |
| --- | --- |
| `data/reports/gc/phase11_leaderboard.md` | Full ranking |
| `data/reports/gc/phase11_sizing.md` | ATR / MLL sizing check |
| `data/reports/gc/phase11_walk_forward.md` | Fold tables |
| `config/gc_phase11.yaml`, `config/strategies_gc.yaml` | Reproducible config |
