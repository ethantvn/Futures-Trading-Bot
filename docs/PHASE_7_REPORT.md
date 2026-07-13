# Phase 7 Report — Consistency-Focused Strategy Research

Date: 2026-07-06. Follows Phases 1–6 (`data/reports/final_recommendation.md`).
Goal: a smoother, more consistent equity curve than plain ORB, ranked by
**Lucid 25K pass rate first**, smoothness second — accepting lower total P&L
and a longer eval if recent years (especially the last one) are steadier.

## TL;DR — a variant beat the baseline on every Phase 7 criterion

**Recommended: width-filtered ORB + Skip Monday, 1 micro** (`orb_filtered`):

| Setting | Value |
| --- | --- |
| Range | First 30 min RTH (09:30–10:00 ET), stop entries ±1 tick (OCO) |
| **Width filter** | Trade only if OR width ∈ (**0.25, 0.70**] × 14-day EWM of daily RTH ranges |
| Skip Monday | ON |
| Target | **1.0R** (last-fold WF selection; 8/9 earlier folds chose 1.5R — both work, band matters more) |
| Stop / expire / flat | Opposite range side / 120 min / 15:55 ET |
| Size | 1 micro (2 micros = optional fast variant, see below) |

| Metric (WF OOS 2021-06 → 2025-11) | **orb_width +skipMon** | ORB +skipMon (old best) | Plain ORB |
| --- | --- | --- | --- |
| **Lucid pass @1 micro** | **61.8%** | 51.9% | 44.3% |
| Median days to pass (active) | 21 | 21 | 22 |
| E[cost] to funded | **$137** | $156 | $176 |
| Net P&L | $17,607 | $19,427 | $18,377 |
| Daily Sharpe | **1.89** | 1.52 | 1.16 |
| UPI (ann. P&L / ulcer) | **10.7** | 6.2 | 3.5 |
| Max drawdown | **−$2,533** | −$3,003 | −$3,458 |
| Worst single day | **−$593** | −$661 | −$661 |
| Last 12 cal months (2024-12→2025-11) | **+$5,222** (Sharpe 2.01) | +$2,890 (0.82) | +$5,432* |
| Last 6 cal months (2025-06→11) | **+$1,266** (Sharpe 1.30) | +$261 (0.17) | — |
| Negative rolling-6m windows | **0%** | 0% | 17% |
| **2026 holdout (single run)** | **+$1,871**, Sharpe 1.34 | — | +$948, PF 1.06 |

*plain-ORB column uses last-252-active-days (its density differs); calendar
windows shown for the skip-Monday variants are the like-for-like comparison.

It gives up ~$1,800 of 4.5-year P&L versus ORB+skipMon and trades ~18% fewer
days, in exchange for +10 points of pass rate, one-third smaller drawdowns,
and a far better recent year. That is exactly the trade-off Phase 7 asked for.

---

## 1. Baseline diagnosis (what actually hurts ORB)

Dissecting the Phase 5 ORB WF OOS ledger (993 trades) produced three findings
that drove the candidate design:

1. **Unnormalized opening-range width is the main variance source.** Risk per
   trade = OR width (stop at the far side), which ranged from 8 to 623 points
   ($16–$1,247 at 1 micro). Bucketing trades by *relative* width
   (OR width ÷ 14-day EWM of daily RTH ranges):
   - ratio ≤ 0.25: **−$2,218** over 112 trades — tiny ranges are noise
     breakouts (41% win rate)
   - ratio 0.25–0.50: **+$14,586** over 590 trades — the sweet spot
   - ratio > 0.50: +$4,704 over 291 trades but with 2× the daily variance and
     every worst day (−$477…−$661)
   Top-decile width days contributed 10% of profit but doubled daily σ. An
   *absolute* width cap fails (2022/2025 wide regimes made all their money on
   wide days); the *relative* band is regime-stable.
2. **EOD drift exits are the profit engine, not the problem.** `eod` exits:
   572 trades, **+$54,995**, 70% win rate. Stops: −$71,629. Targets: +$33,876.
   The Phase 7 prompt's time-stop hypothesis is inverted by the data — cutting
   at midday amputates the winners (confirmed below).
3. **The TV-vs-Python 2025 discrepancy is a platform artifact.** Fixed-param
   ORB (30/1.5/120) in our engine: 2025 = **+$4,621** (+$1,629 with skip-Mon);
   the WF ledger 2025 = +$4,084. The negative 2025 the user sees in
   TradingView does not reproduce under our pessimistic-fill engine, which is
   the project's ground truth (bars verified 99.9% vs TV; fill models differ).
   The user's "last ~90 days negative" corresponds to the 2026 holdout window
   — addressed in §5.

## 2. New consistency toolkit

`src/evaluation/consistency.py` (+10 tests): daily Sharpe/Sortino, max
drawdown, **ulcer index** and **UPI** (annualized P&L ÷ ulcer — the smoothness
ranking scalar), equity-vs-time R², max consecutive losing days, win-day rate,
recency windows (90/252/756 **active** days), per-year P&L, and rolling
6-month windows (share negative + worst window) for regime stability.
Ranking rule everywhere: **pass rate first, UPI second**.

## 3. Candidates tested (walk-forward, same 9 folds as Phase 5)

New strategies (`src/strategies/`, 13 tests): `orb_filtered.py` (width band /
skip-weekday / time-exit gates, all default-off), `nr_compression.py`
(NR-n / inside-day gate), `afternoon.py` (13:00–14:00 range breakout,
optional VWAP side filter). Grids in `config/phase7.yaml`; runner
`scripts/run_phase7.py`; full table in `data/reports/phase7_leaderboard.md`.

| Family | Pass@1 (+skipMon) | Verdict |
| --- | --- | --- |
| **orb_width** — band (min,max] on relative OR width | 55.0% / **61.8%** | **Winner.** Chosen band nearly identical in all 9 folds (0.25–0.3 / 0.55–0.7); 8/9 test windows positive; re-selecting folds by UPI instead of Sharpe lands on the same band (scorer-robust). |
| **nr7_orb** — trade only after NR-5/inside days | 59.6% / 63.5% | Real effect (nr_n=5, mode=nr picked 7–9/9 folds) but only ~40 trades/yr → median pass ≈ 18 active days ≈ **23 calendar weeks**. Holdout: +$749 (20 trades); its skip-Mon overlay collapsed (+$134). Keep as optional diversifier, not primary. |
| orb_target — 1.0/1.25/2.5/none | 46.7% / 53.8% | No pass-rate edge over baseline skip-Mon; target choice unstable across folds (999→2.5→1.25); worse maxDD (−$3,998). Rejected. |
| orb_timestop — force flat 12:00/13:30/14:30 | 44.9% / 49.4% | **Folds themselves chose "no exit" 8/9 times.** Confirms §1.2: time-stops hurt. Rejected. |
| afternoon_breakout | 23.0% / 24.5% | No edge (negative recent windows). Rejected. |

Re-scored Phase 3–5 rejects with the new metrics (fixed params, full window):
ema_trend 29.9% pass / 48% negative 6-m windows / maxDD −$7,063;
vwap_pullback 9.3%; prev_day_hl 6.0%; bollinger 3.9% — all confirm rejection
on consistency grounds too, not just expectancy.

## 4. Validation of the winner

- **Fold stability:** min_ratio ∈ {0.25, 0.3}, max_ratio ∈ {0.55, 0.7} in all
  9 folds — the band is not a single-era artifact. Every year 2021–2025
  positive (skip-Mon: $1,601 / $2,802 / $1,962 / $7,321 / $3,921).
- **2025 shape:** 7/11 months positive, worst month −$925 (baseline ORB
  skip-Mon: worst −$1,008, Nov −$1,008 vs width's +$121).
- **Slippage stress (2025, final params):** +$4,909 / +$4,756 / +$4,602 at
  0/1/2 ticks — robust.
- **Monte Carlo (10k, block bootstrap):** 61.8% pass, 2.8% timeout,
  E[resets] 0.6, E[cost] $137. At **2 micros**: 50.7% pass, median 9 active
  days — a legitimate "fast" option that still nearly matches the old
  baseline's 1-micro pass rate.
- **Trade density:** 659 active days / ~1,172 weekdays ≈ 56% → median pass
  ≈ 21 active days ≈ **7–8 calendar weeks** (vs ~6 for baseline skip-Mon).
  Slower, as accepted in the Phase 7 goal.

## 5. 2026 holdout — single run (2026-01-01 → 2026-06-28)

Run once for the two finalists via `run_phase7.py --holdout orb_width nr7_orb`
(`data/reports/phase7_holdout.md`). Not used for tuning.

| | Jan | Feb | Mar | Apr | May | Jun | Total |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **orb_width +skipMon** | +1,087 | +937 | −11 | +349 | +33 | −524 | **+$1,871** |
| Baseline ORB (Phase 5 holdout) | +803 | +2,185 | +148 | +290 | −583 | −1,895 | +$948 |

The user's pain window (≈ Apr–Jun 2026): baseline **−$2,188** vs width+skipMon
**−$142**. The filter turned the recent bleed into roughly flat while keeping
H1 solidly positive. Max DD on holdout: −$1,861 vs Sharpe 1.34; MC pass rate
on the holdout ledger alone: 54.2%. **No collapse — criterion 5 met.**

## 6. Success criteria scorecard (orb_width + skipMon)

1. Pass rate ≥ ORB skip-Mon (52%): **61.8% ✓**
2. Smoother than ORB: UPI 10.7 vs 6.2, maxDD −$2,533 vs −$3,003, Sharpe 1.89
   vs 1.52, worst day −$593 vs −$661 **✓**
3. Profitable in last 252 trading days: **+$10,948** (and +$5,222 over the
   last 12 *calendar* months) **✓**
4. Slippage stress 0/1/2 ticks 2025: **profitable at all levels ✓**
5. 2026 holdout: **+$1,871, no collapse ✓**

## 7. Execution plan (live eval)

1. TradingView: `tradingview/lucid_orb_width_25k.pine` (5m MNQ1! chart,
   1 micro). Skip-Monday ON, width band 0.25–0.70, target 1.0R. Orange tags
   explain every skipped day; first ~14 sessions after adding are warmup.
2. Expect to **stand aside ~4 of 10 non-Monday sessions** (narrow/wide skips).
   Do not "make up" skipped days with discretionary trades — the skips ARE
   the edge refinement.
3. Consistency rule: at $1,250 target, no day > $625. Worst historical win
   day ≈ +$700 (rare); if a huge day puts you over 50%, trade the next
   qualifying day small or stop early — same discipline as Phase 6.
4. Sizing: 1 micro (61.8%). If you explicitly prefer speed over pass odds:
   2 micros ≈ 50.7% pass, median ≈ 9 active days.
5. Re-selection cadence: WF re-picks params every 6 months; re-run the
   pipeline around 2026-12 with data through 2026-11.

## 8. Caveats

- Commission still the $0.99/side placeholder — verify platform rate.
- TV fills ≠ engine fills (engine is deliberately pessimistic: stop-before-
  target on ambiguous bars, 1-tick slippage). Use TV for levels/alerts.
- The 0.25/0.70 band edges are grid points, not magic numbers; fold stability
  (0.25–0.3 / 0.55–0.7) suggests the *region* is what matters.
- MC pass rates are historical-bootstrap estimates, not guarantees; block
  bootstrap preserves 5-day clustering but not longer regime shifts.
- nr7_orb (59.6% standalone) remains a valid low-frequency diversifier for a
  second account, but ~23-week median evals make it impractical as primary.
- Holdout was touched once for the two finalists. **Do not re-run it.**

## Artifacts

| File | Content |
| --- | --- |
| `data/reports/phase7_leaderboard.md` | Full ranking + rejected re-scores + stress |
| `data/reports/phase7_walk_forward.md` | Fold-by-fold tables, all families |
| `data/reports/phase7_holdout.md` / `phase7_metrics.json` | Holdout + full metric dump |
| `data/processed/trades_phase7_*_wf_oos.parquet` | Candidate OOS ledgers |
| `data/processed/trades_phase7_*_holdout.parquet` | Finalist holdout ledgers |
| `src/evaluation/consistency.py`, `src/strategies/{orb_filtered,nr_compression,afternoon}.py` | New code (+23 tests; suite 110 green) |
| `config/phase7.yaml`, `scripts/run_phase7.py` | Reproducible pipeline |
| `tradingview/lucid_orb_width_25k.pine` | Live script for the winner |
