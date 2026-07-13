# Phase 9 Report — Profitable Future Strategy Research

Date: 2026-07-08. Builds on Phase 7 winner (ORB-W + Skip Monday, ~61.8% pass).

## TL;DR

**New candidate `orb_longonly +skipMon` beats Phase 7 baseline on pass rate (64.3% vs 61.8%).** See leaderboard for full metrics.

## What we tested

1. **Long-only ORB-W** — disable short breakouts (equity drift hypothesis).
2. **Macro-day skip** — stand aside on NFP / CPI / FOMC release days.
3. **Long-only + macro + skipMon** — combined filter stack.
4. **Portfolio baselines** — NR7 ORB as second-account diversifier.
5. **End-to-end journey MC** — pass eval AND first payout-eligible state.

## Top candidates (pass rate @1 micro)

| Candidate | Pass % | Pass+Payout % | Net $ | UPI |
| --- | --- | --- | --- | --- |
| orb_longonly +skipMon | 64.3% | 45.6% | $13,731 | 10.7 |
| orb_longonly_macro +skipMon | 63.6% | 46.4% | $9,883 | 11.8 |
| PHASE7 nr7_orb +skipMon | 63.5% | 42.9% | $6,095 | 12.9 |
| PHASE7 orb_width +skipMon | 61.8% | 41.7% | $17,607 | 10.7 |
| orb_macro_skip +skipMon | 55.9% | 35.7% | $12,589 | 3.6 |

## Macro-day analysis (Phase 7 winner)

- Phase 7 winner on macro days (108 sessions): net $3,274 (avg $30) vs non-macro net $14,333 (avg $26)

## Automation (live execution)

Lucid allows TradingView → TradersPost → Tradovate automation (no HFT). Each account must run a **unique** strategy — identical copy-trading across many Lucid accounts violates their automation policy.

Checklist:
1. Re-add fixed `lucid_orb_width_25k.pine` (Phase 8 flat-at-15:55 fix).
2. Chart: MNQ1!, 5m, America/New_York, 1 micro.
3. Connect TradersPost webhook alerts (entry, flat 15:55, skip badges).
4. Log every live fill vs Python ledger (slippage monitor).
5. Do NOT copy identical signals to multiple Lucid accounts.

## Multi-instrument expansion (MES / ES)

The pipeline is instrument-agnostic. To add MES:
1. Purchase Databento GLBX.MDP3 batch for `MES.FUT` (same schema as MNQ).
2. Add `config/data_mes.yaml` with `point_value: 5.0`, `tick_size: 0.25`.
3. Re-run Phases 3–7 grid on MES — **do not port MNQ params blindly**.
4. MES has smaller $/point → better fit for $1,000 MLL in high-vol regimes.
5. Run on a **different prop firm or Lucid account** as a genuinely unique bot.

## Scaling path (compliant)

| Account | Strategy | Role |
| --- | --- | --- |
| 1 | ORB-W + Skip Mon (MNQ) | Primary — ~62% pass |
| 2 | NR7 ORB (MNQ) | Slow diversifier — ~60% pass, ~40 trades/yr |
| 3+ | MES ORB-W (after validation) | Different instrument = unique bot |

## TradingView rev B flat fix (2026-07-08)

Phase 8 still left ~30% overnight holds in TV exports. **Rev B** stops re-arming
`strategy.exit("XL")` after 15:55, cancels brackets, and uses
`strategy.close("Flat 15:55")`. Removed midnight `newNyDay` fallback.
Update `lucid_orb_width_25k.pine` (shorttitle **ORB-W 25K B**) and verify
**zero** exit date ≠ entry date in the trade list.

## Recommendation

**Primary:** ORB-W + Skip Monday + **Long only** @ 1 micro (~64% pass).
See `data/reports/phase9_leaderboard.md`. Re-run walk-forward ~2026-12.

## Artifacts

| File | Content |
| --- | --- |
| `data/reports/phase9_leaderboard.md` | Full ranking + journey MC |
| `data/reports/phase9_walk_forward.md` | Fold tables |
| `data/calendar/macro_events.csv` | NFP/CPI/FOMC skip dates |
| `src/data/macro_calendar.py` | Calendar generator |
| `config/phase9.yaml`, `scripts/run_phase9.py` | Reproducible pipeline |
