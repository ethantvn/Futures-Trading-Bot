# Phase 8 Leaderboard — tail-risk exit overlays on orb_width

Each overlay re-runs the full Phase 7 orb_width grid + walk-forward (same 9 folds) with the overlay fixed; ledgers are stitched WF OOS 2021-06 → 2025-11. MC 10000 attempts @1 micro, seed 42. Stop caps in points: 200/250/300 pts = $400/$500/$600 max gross loss per trade (= per day at 1 trade/day). `friday_flat` is a **no-op in the engine** (flat 15:55 every day; 0 multi-day holds across all ledgers) — it was a TradingView bug, fixed in the Pine scripts.

| Candidate | Trades | Pass@1 | Med d | Net $ | UPI | MaxDD | Worst day | p95 loss | Worst 20d | Last252 $ | E[cost] |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| BASELINE orb_width +skipMon | 659 | 61.8% | 21 | $17,607 | 10.68 | $-2,533 | $-593 | $-301 | $-2,319 | $10,948 | $137 |
| stopcap_250pts +skipMon | 659 | 60.5% | 21 | $16,124 | 9.75 | $-2,533 | $-503 | $-301 | $-2,319 | $9,465 | $139 |
| stopcap_300pts +skipMon | 659 | 59.9% | 21 | $15,934 | 9.44 | $-2,533 | $-603 | $-301 | $-2,319 | $9,275 | $140 |
| stopcap_200pts +skipMon | 659 | 58.8% | 21 | $15,193 | 8.77 | $-2,719 | $-403 | $-304 | $-2,319 | $8,503 | $142 |
| BASELINE orb_width (Phase 7) | 802 | 55.0% | 22 | $17,057 | 6.63 | $-2,350 | $-593 | $-300 | $-2,196 | $5,305 | $149 |
| maxhold_180 +skipMon | 705 | 54.3% | 24 | $11,953 | 3.30 | $-3,936 | $-593 | $-274 | $-3,382 | $7,815 | $151 |
| stopcap_250pts | 802 | 54.0% | 22 | $15,574 | 6.05 | $-2,350 | $-503 | $-301 | $-2,196 | $3,822 | $151 |
| stopcap_300pts | 802 | 53.5% | 22 | $15,384 | 5.97 | $-2,350 | $-603 | $-301 | $-2,196 | $3,632 | $152 |
| stopcap_200pts | 802 | 52.8% | 22 | $14,643 | 5.55 | $-2,581 | $-403 | $-303 | $-2,196 | $2,860 | $154 |
| maxhold_120 +skipMon | 705 | 49.6% | 28 | $10,143 | 3.84 | $-2,630 | $-535 | $-254 | $-2,069 | $5,085 | $161 |
| maxhold_180 | 859 | 48.2% | 27 | $11,531 | 2.27 | $-4,781 | $-593 | $-291 | $-2,223 | $3,372 | $164 |
| maxhold_90 +skipMon | 695 | 45.7% | 32 | $8,570 | 2.64 | $-3,846 | $-474 | $-241 | $-2,961 | $5,338 | $171 |
| maxhold_120 | 857 | 40.3% | 31 | $8,122 | 2.62 | $-3,144 | $-535 | $-258 | $-1,599 | $1,594 | $189 |
| maxhold_90 | 847 | 36.8% | 34 | $7,877 | 2.05 | $-2,925 | $-474 | $-242 | $-2,684 | $3,086 | $203 |
| maxhold_60 +skipMon | 674 | 27.7% | 37 | $3,596 | 0.74 | $-4,417 | $-660 | $-224 | $-2,786 | $3,631 | $257 |
| maxhold_60 | 818 | 22.3% | 39 | $3,086 | 0.68 | $-3,336 | $-660 | $-224 | $-2,267 | $2,488 | $309 |

## Tail / outlier analysis (Phase 7 winner ledgers)

### orb_width (WF OOS, all days)

- Top 5% winning days: 40 days (>= $370) contribute **$18,850** of $17,057 net (111%).
- Lucid pass rate with those days REMOVED: **30.2%** (vs 55.0% full) — median 26 vs 22 days.

Worst 10 days (fresh-$25k MLL = $1,000; single-day breach needs <= -$1,000):

| Date | Day P&L | % of MLL |
| --- | --- | --- |
| 2025-04-11 | $-593 | 59% |
| 2025-03-07 | $-440 | 44% |
| 2022-05-12 | $-434 | 43% |
| 2025-03-11 | $-429 | 43% |
| 2025-04-23 | $-414 | 41% |
| 2025-04-08 | $-410 | 41% |
| 2025-03-04 | $-408 | 41% |
| 2025-04-30 | $-400 | 40% |
| 2025-11-21 | $-398 | 40% |
| 2025-03-05 | $-375 | 37% |

- Single-day MLL breaches from fresh start: **0** of 802 days.
- Worst 2-consecutive-active-day run: $-783 (78% of MLL).
- Worst 5-consecutive-active-day run: $-1,460 (146% of MLL).

| Exit | N | Net $ | Avg $ | Win rate |
| --- | --- | --- | --- | --- |
| target | 204 | $55,668 | $272.9 | 100% |
| eod | 313 | $20,286 | $64.8 | 68% |
| session_end | 4 | $355 | $88.8 | 50% |
| stop | 281 | $-59,252 | $-210.9 | 0% |

### orb_width +skipMon (live config)

- Top 5% winning days: 33 days (>= $371) contribute **$15,766** of $17,607 net (90%).
- Lucid pass rate with those days REMOVED: **36.2%** (vs 61.8% full) — median 26 vs 21 days.

Worst 10 days (fresh-$25k MLL = $1,000; single-day breach needs <= -$1,000):

| Date | Day P&L | % of MLL |
| --- | --- | --- |
| 2025-04-11 | $-593 | 59% |
| 2025-03-07 | $-440 | 44% |
| 2022-05-12 | $-434 | 43% |
| 2025-03-11 | $-429 | 43% |
| 2025-04-23 | $-414 | 41% |
| 2025-04-08 | $-410 | 41% |
| 2025-03-04 | $-408 | 41% |
| 2025-04-30 | $-400 | 40% |
| 2025-11-21 | $-398 | 40% |
| 2025-03-05 | $-375 | 37% |

- Single-day MLL breaches from fresh start: **0** of 659 days.
- Worst 2-consecutive-active-day run: $-869 (87% of MLL).
- Worst 5-consecutive-active-day run: $-1,887 (189% of MLL).

| Exit | N | Net $ | Avg $ | Win rate |
| --- | --- | --- | --- | --- |
| target | 178 | $49,004 | $275.3 | 100% |
| eod | 246 | $16,357 | $66.5 | 68% |
| session_end | 3 | $396 | $132.0 | 67% |
| stop | 232 | $-48,150 | $-207.5 | 0% |

