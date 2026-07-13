# Project Status — MNQ Lucid Flex Evaluation Research

Last updated: 2026-07-12 (Phase 19 complete).

## Status: Phases 1–19 COMPLETE

| Phase | Status | Output |
| --- | --- | --- |
| 1–6 | Done | Baseline + validation infra |
| 7–8 | Done | ORB-W width filter, tail risk |
| 9 | Done | ORB-W long-only (~64% pass) — **live primary** |
| 10 | Done | MES port rejected (19% pass) |
| 11–13 | Done | GC / MGC rejected |
| 14 | Done | 100K tier rejected as primary |
| 15 | Done | Scalping rejected |
| 16 | Done | Structure/levels; overnight fade revoked (lookahead) |
| 17 | Done | VIX / ON / regime gates — no lift |
| 18 | Done | Deep multi-family sweep (~442 combos) — **nothing beats ORB-W** |
| 19 | Done | Eval-policy sizing — **fixed 1 micro still best** |

## Final answer for your 25K eval (unchanged)

**Trade long-only width-filtered ORB + Skip Monday, 1 MNQ micro.**

| Setting | Value |
| --- | --- |
| Script | `tradingview/lucid_orb_width_25k.pine` |
| Range | 30m RTH; width ∈ (0.25, 0.70] × vol_ref |
| Long only + skip Monday | ON |
| Target | 1.0R |
| Size | 1 micro |

**Expected (10k MC, WF OOS, $0.50/side, no eval time limit):** ~**70%** pass eval, ~**52%** pass+first payout.
(Re-backtest: `data/reports/rebacktest_commission050.md`)

## Phase 18 (brief)

Fades (ORB/VWAP/BB/RSI/Stoch/prior-day/overnight), Donchian, EMA, ATR break,
MACD, ROC+vol, TOD/macro/risk-cap ORB variants, MES diverge — **best challenger
`orb_tod` at 59% pass**, still below control. Full write-up:
**`docs/PHASE_18_REPORT.md`**.

## Scaling (compliant)

| Account | Strategy | Pass@1 |
| --- | --- | --- |
| 1 | ORB-W long-only + skipMon (MNQ) | ~64% |
| 2 | NR7 ORB + skipMon (MNQ) | ~64% (slow) |
| P15–P18 alternatives | **Rejected** | — |

## Phase 19 (brief)

State-dependent sizing (upshift, post-lock, cushion-skip, downshift) on frozen
ORB-W — **no lift**; fixed 1 micro remains optimal. See **`docs/PHASE_19_REPORT.md`**.

## Remaining manual items

1. Verify live platform MNQ commission
2. Confirm Lucid EOD cutoff with support
3. Re-run MNQ WF re-selection ~2026-12
4. Re-backtest at **$0.50/side** complete — see `data/reports/rebacktest_commission050.md`
