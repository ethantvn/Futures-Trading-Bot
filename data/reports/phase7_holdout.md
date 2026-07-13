# Phase 7 — 2026 Holdout (single run)

**Run once for the Phase 7 finalists. Do not re-run for tuning.**

| Candidate | Trades | Pass@1 | Med d | Net $ | Sharpe | UPI | MaxDD | R² | ConsecL | Last90 $ | Last252 $ | 2023-25 $ | Neg 6m | Worst 6m |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| orb_width (holdout) | 96 | 51.0% | 14 | $2,073 | 1.15 | 6.65 | $-2,845 | 0.61 | 4 | $1,790 | $2,073 | $0 | — | $nan |
| orb_width +skipMon (holdout) | 76 | 54.2% | 15 | $1,871 | 1.34 | 9.93 | $-1,861 | 0.68 | 5 | $1,871 | $1,871 | $0 | — | $nan |
| nr7_orb (holdout) | 20 | 55.8% | 17 | $749 | 1.63 | 40.21 | $-732 | 0.74 | 3 | $749 | $749 | $0 | — | $nan |
| nr7_orb +skipMon (holdout) | 15 | 32.2% | 21 | $134 | 0.39 | 6.47 | $-732 | 0.14 | 2 | $134 | $134 | $0 | — | $nan |

Final params per family:

- `orb_width (holdout)`: `{'expire_minutes': 120, 'max_width_ratio': 0.7, 'min_width_ratio': 0.25, 'range_minutes': 30, 'target_r': 1.0}`
- `orb_width +skipMon (holdout)`: `{'expire_minutes': 120, 'max_width_ratio': 0.7, 'min_width_ratio': 0.25, 'range_minutes': 30, 'target_r': 1.0, 'skip_weekdays': [1]}`
- `nr7_orb (holdout)`: `{'expire_minutes': 120, 'mode': 'nr', 'nr_n': 5, 'range_minutes': 30, 'target_r': 1.5}`
- `nr7_orb +skipMon (holdout)`: `{'expire_minutes': 120, 'mode': 'nr', 'nr_n': 5, 'range_minutes': 30, 'target_r': 1.5, 'skip_weekdays': [1]}`
