# Phase 10 Report — MES ORB-W Validation

Date: 2026-07-08. Second-instrument validation for Lucid Flex 25K @ 1 MES micro.

## TL;DR

**MNQ remains primary.** Best MES `MES orb_longonly +skipMon` (19.4% pass) trails MNQ Phase 9 (64.3%). Use MES only if you need a compliant second account and accept lower pass rate.

## Method

- Data: Databento GLBX.MDP3 `MES.FUT` ohlcv-1m, 2019-05-29 → 2026-06-29
- Point value: $5/pt (MES micro), same ORB engine as MNQ
- Walk-forward: 24m train / 6m test, grid_end 2025-12-31
- MC: 10k Lucid 25K eval attempts @ 1 micro, block bootstrap

## Results (@1 micro, skipMon overlay)

| Candidate | Pass % | Pass+Payout % | Net $ | UPI |
| --- | --- | --- | --- | --- |
| MNQ orb_longonly +skipMon (Phase 9) | 64.3% | 45.6% | $13,731 | 10.7 |
| MES orb_longonly +skipMon | 19.4% | 7.6% | $973 | 0.9 |
| MES orb_width +skipMon | 12.3% | 3.8% | $-994 | -0.4 |

## Selected params (last WF fold)

- **orb_width**: `{'range_minutes': 30, 'target_r': 1.0, 'expire_minutes': 120, 'min_width_ratio': 0.2, 'max_width_ratio': 1000000000.0}`
- **orb_longonly**: `{'range_minutes': 30, 'target_r': 1.5, 'expire_minutes': 120, 'min_width_ratio': 0.25, 'max_width_ratio': 0.7, 'long_only': True}`

**MNQ remains primary.** Do not run MES ORB-W for Lucid eval unless you accept ~19% pass rate for a compliant second bot.

## Recommendation

**Do not deploy MES ORB-W for Lucid eval.** Stick with MNQ long-only ORB-W (~64% pass).
MES long-only + skipMon scored **19.4% pass / 7.6% pass+payout** — not viable as account #2.
If you need a second Lucid account, NR7 ORB on MNQ (~64% pass, slower) is the better diversifier.

## Artifacts

| File | Content |
| --- | --- |
| `data/reports/mes/phase10_leaderboard.md` | Full ranking |
| `data/reports/mes/phase10_walk_forward.md` | Fold tables |
| `data/processed/mes/trades_phase10_*.parquet` | OOS ledgers |
| `config/data_mes.yaml`, `config/phase10.yaml` | Reproducible config |
