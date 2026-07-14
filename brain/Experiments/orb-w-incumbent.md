---
type: experiment
status: live-candidate
phase: 7-9
family: opening-range-breakout
verdict: Incumbent. ~69.8% pass / ~51.6% pass+payout, median ~26 days.
updated: 2026-07-13
---

# ORB-W long-only + skip Monday @ 1 micro (incumbent)

## Spec

| Param | Value |
| --- | --- |
| Range | first **30m** RTH (09:30–10:00 ET), stop entries ±1 tick |
| Width filter | OR width / 14-day EWM of daily RTH ranges ∈ **(0.25, 0.70]** |
| Direction | **long only** ([[long-only]]) |
| Skip | **Monday** ([[skip-monday]]) |
| Target / stop | **1.0R** / opposite side of range |
| Expire / flat | 120m pending expiry / flat 15:55 ET (Lucid allows 16:45 — conservative) |
| Size | **1 micro, fixed** ([[fixed-1-micro]]) |

Pine: `tradingview/lucid_orb_width_25k.pine` (rev B flat fix — zero overnight holds).
Python: `src/strategies/orb_filtered.py` (`FilteredOrb`).

## Numbers (verified rules, $0.50/side, no eval time limit)

| Metric | WF OOS | 2026 holdout |
| --- | --- | --- |
| Pass 25K @ 1 micro | **69.8%** | 67.8% |
| Pass + first payout | **51.6%** | 47.7% |
| Median days to pass | 26 | 12 |
| Trades / net | 473 / $12,501 | 52 / +$2,836 |

Source: `data/reports/rebacktest_commission050.md`.

## Why it works (Phase 7 diagnosis, [[PHASE_7_REPORT]])

1. Relative OR width is the main variance source; the (0.25, 0.70] band cuts noise breakouts (≤0.25 net −$2.2k) and fat-tail wide days.
2. **EOD drift exits are the profit engine** — 70% WR on eod exits; time-stops amputate winners ([[time-stops-target-grids]]).
3. Skips are the edge refinement — stand aside ~4 of 10 non-Monday sessions.

## Standing risks

- Bootstrap MC ≠ regime guarantee; re-select params ~every 6 months ([[wf-reselection-2026-12]]).
- Live fills vs pessimistic engine unverified until live ([[tv-python-reconciliation]]).
