# Phase 9 — 2026 Holdout: orb_longonly (single confirmation run)

**Frozen params from walk-forward (last fold). Not used for tuning.**

Window: 2026-01-01 → 2026-06-28

```yaml
expire_minutes: 120
long_only: True
max_width_ratio: 0.7
min_width_ratio: 0.25
range_minutes: 30
target_r: 1.0
```

| Candidate | Trades | Pass@1 | Med d | Net $ | Sharpe | UPI | MaxDD | R² | ConsecL | Last90 $ | Last252 $ | 2023-25 $ | Neg 6m | Worst 6m |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| orb_longonly (holdout) | 66 | 57.4% | 13 | $1,813 | 1.54 | 12.85 | $-1,724 | 0.78 | 4 | $1,813 | $1,813 | $0 | — | $nan |
| orb_longonly +skipMon (holdout) | 50 | 58.8% | 13 | $1,970 | 2.20 | 23.55 | $-1,359 | 0.81 | 3 | $1,970 | $1,970 | $0 | — | $nan |

## Pass + payout (holdout ledger MC)

| Candidate | Pass@1 | Pass+Payout |
| --- | --- | --- |
| orb_longonly (holdout) | 57.4% | 37.5% |
| orb_longonly +skipMon (holdout) | 58.8% | 37.5% |

## vs Phase 7 orb_width +skipMon (same holdout window, prior run)

| Metric | Phase 7 width+skipMon | Phase 9 long-only+skipMon |
| --- | --- | --- |
| Trades | 76 | 50 |
| Net $ | $1,871 | $1,970 |
| Sharpe (daily) | 1.34 | 2.20 |
| Max DD | −$1,861 | $-1,359 |
| MC pass@1 | 54.2% | 58.8% |
| Worst day | — | $-639 |
| Best day | — | $457 |

## Monthly P&L (long-only + skipMon)

| Month | Net $ | Active days |
| --- | --- | --- |
| 2026-01 | $610 | 6 |
| 2026-02 | $-539 | 6 |
| 2026-03 | $-85 | 9 |
| 2026-04 | $1,306 | 10 |
| 2026-05 | $1,192 | 11 |
| 2026-06 | $-514 | 8 |

## Consistency check

- Total holdout profit: **$1,970**
- Largest single day: **$457** (23% of total)
- At $1,250 target, largest day ≤ 50% of profit → need largest ≤ half of total ✓

## Verdict
**PASS** — Holdout confirms Phase 9 long-only. No collapse; safe to commit to eval.
