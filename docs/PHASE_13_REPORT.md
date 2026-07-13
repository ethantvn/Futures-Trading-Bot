# Phase 13 Report — Micro Gold (MGC) Lucid Flex Eval Research

Date: 2026-07-11. Micro COMEX gold (MGC, $10/pt), both Lucid tiers (25K primary, 50K secondary).

## TL;DR

**REJECT MGC — keep MNQ ORB-W as the live recommendation (~64% pass on 25K).**

Sizing is finally right (1/10th GC dollar risk fits both MLLs comfortably), but
after **6,340 combos** across 13 families in a two-stage walk-forward search,
no MGC candidate clears the picky acceptance bar:

- Best headline pass rate — `macro_nfp` **52.3%** on 25K — is a **lottery
  ticket**: 0.9 trades/month; MC "45 median days to pass" are *active NFP
  days* ≈ **4 calendar years**. Within a realistic 6-month eval window its
  wall-clock pass probability is **0%** (100% timeout).
- Best practical-frequency candidate — `comex_orb_deep` **30.4%** on 25K —
  sits at the junk floor (Phases 10–12: ~25–30%), has only 50% positive WF
  folds, and its **2026 holdout MC pass is 0%** (5 trades in 6 months; the
  width filter nearly stopped emitting in the 2026 vol regime).
- **50K @ 1 MGC is 0% everywhere** — a $3,000 target at $10/pt is unreachable.
  Sizing up to 2–3 MGC lifts in-sample MC but fails the same wall-clock and
  holdout tests, and the prompt forbids sizing up a weak edge.
- 2026 holdout (single run, frozen params): all three finalists ~$0 net,
  **0.0% MC pass on both tiers**.

Gold intraday breakout/momentum edges are simply too weak per-dollar-of-risk
for a Lucid eval at micro sizing — the failure mode differs from GC (blow
risk) but the conclusion is the same.

## Task 0 — Data ingest & roll calendar

- Databento `GLBX.MDP3` `MGC.FUT` ohlcv-1m, 2021-06-11 → 2026-07-10
  (`data/raw/GLBX-20260711-SJH7NNPY6M/`)
- 3,005,052 outright 1m bars, 42 contracts, 1,312 trading days, 29 rolls
- Roll calendar restricted to liquid months **{G,J,M,Q,V,Z}**,
  `confirm_sessions=2` — verified **zero** non-liquid codes
- Tick grid verified **0.10** (0 misaligned prices);
  `point_value: 10.0` (10 oz × $0.10 tick = $1/tick)
- Report: `data/reports/mgc/data_quality.md`

## Sizing check (the one thing MGC gets right)

Full table: `data/reports/mgc/phase13_sizing.md`

| Metric | MGC @ 1 micro | GC full-size (Phase 11) |
| --- | --- | --- |
| Median daily RTH range | **$193** | ~$1,930 |
| P95 daily RTH range | **$780** | ~$7,810 |
| 25K band ($150–250 / 15–25 pts) | fits | impossible |
| 50K band ($300–500 / 30–50 pts) | fits | tight |

Caveat: massive vol-regime shift — 2026 median daily range **$646** vs ~$140
in 2021–2023 (gold ~$4,700/oz in 2026 vs ~$1,800 in 2021). 2026 P95 days
($1,655) exceed the 25K MLL, so capped stops + 1 trade/day remain mandatory.

## Method

- Walk-forward: **6 folds**, 18m train / 6m test; grid through 2025-12-31;
  stitched OOS = 2022-12-01 → 2025-11-30
- Selection: train-window daily Sharpe (min-trades gated); tier MC never sees
  training choice
- MC: 10k block-bootstrap attempts on the stitched OOS ledger, **both**
  `lucid_25k` and `lucid_50k`, eval/reset costs included
- Costs: $0.75 commission + $0.75 exchange per side (**VERIFY**), 1-tick
  slippage ($1); stress 0/1/2/3 ticks
- Stage 1: 10 families / 5,004 combos. Stage 2 (pre-holdout, around stage-1
  stable regions): 3 families / 1,336 combos
- Holdout 2026-01-01 → 2026-07-10 touched **once**, finalists only, frozen params

## Leaderboard (25K pass @ 1 MGC, WF OOS)

Full table + slippage stress: `data/reports/mgc/phase13_leaderboard.md`

| Candidate | Combos | OOS trades | Pass 25K | Pass 50K | Fold+ % | OOS net | 2025 $ |
| --- | --- | --- | --- | --- | --- | --- | --- |
| macro_nfp | 324 | 32 | **52.3%** | 0.0% | 67% | $643 | $87 |
| macro_nfp_cpi | 648 | 76 | 31.2% | 0.4% | 50% | $938 | $275 |
| comex_orb_deep | 432 | 204 | 30.4% | 0.5% | 50% | $1,995 | $332 |
| comex_orb | 960 | 269 | 16.7% | 0.0% | 50% | $1,384 | $-245 |
| london_orb | 960 | 104 | 14.4% | 0.0% | 67% | $360 | $512 |
| macro_cpi | 324 | 56 | 6.3% | 0.0% | 67% | $40 | $-211 |
| ny_orb | 960 | 450 | 3.1% | 0.0% | 67% | $112 | $1,058 |
| overlap_orb | 256 | 102 | 1.8% | 0.0% | 33% | $-801 | $-1,046 |
| london_orb_deep | 648 | 60 | 1.1% | 0.0% | 50% | $-499 | $-663 |
| nr_orb | 384 | 98 | 0.2% | 0.0% | 33% | $-624 | $303 |
| vwap_trend | 72 | 663 | 0.1% | 0.0% | 0% | $-5,261 | $-1,825 |
| macro_fomc | 324 | 16 | 0.0% | 0.0% | 67% | $-16 | $-82 |
| vwap_reversion | 48 | 1407 | 0.0% | 0.0% | 0% | $-10,439 | $-4,152 |

Stage-2 note: deepening COMEX helped (16.7% → 30.4%, all four OOS years
positive) but deepening London **hurt** (14.4% → 1.1%) — the Phase 12 lesson
(more combos ≠ durable edge) reproduced on MGC.

## The sparsity trap (why 52.3% is not a pass)

MC "days" are *active trading days*. Converting to wall-clock at each
strategy's observed OOS trade frequency, 25K tier:

| Candidate | Trades/mo | Pass within ~2 mo | Pass within ~6 mo |
| --- | --- | --- | --- |
| macro_nfp @ 2 MGC | 0.9 | 0.0% (100% timeout) | **0.0%** (100% timeout) |
| macro_nfp_cpi @ 2 MGC | 2.2 | 0.0% | 12.7% |
| comex_orb_deep/comex @ 2 MGC | ~6–8 | 12.2% | 38.8% (fail 49.5%) |

MNQ ORB-W passes ~64% with median ~20 active days ≈ 6 calendar weeks.
Nothing on MGC is in the same universe.

## Contract-count sweep (25K, WF OOS ledger)

`macro_nfp` @2 = 89.6% / @3 = 87.5% "pass" — but the wall-clock table above
shows these are timeout-dominated fantasies inside any real eval window.
`comex_orb` @2 = 42.9% pass with **53.0% fail** (risk-of-ruin explodes).
Sizing up cannot rescue a weak edge — confirmed.

## Slippage stress (2025, 0/1/2/3 ticks)

- macro families: expectancy stays positive through 3 ticks (tiny samples)
- `comex_orb`: expectancy $2.78 → **negative at 2 ticks** — fragile edge
  even before holdout

## 2026 holdout (single run, frozen params — touched once)

| Family | Trades | Net $ | Pass 25K % | Pass 50K % |
| --- | --- | --- | --- | --- |
| macro_nfp | 5 | $86 | **0.0%** | 0.0% |
| macro_nfp_cpi | 11 | $-289 | **0.0%** | 0.0% |
| comex_orb_deep | 5 | $-58 | **0.0%** | 0.0% |

Not a GC-style blowup — a **starvation** failure: filters tuned on 2021–2025
barely emit trades in the 2026 regime, so the eval can never reach target.
Overfit guard also triggers: WF pass (30–52%) ≫ holdout pass (0%).

## Picky acceptance bar — scorecard

| # | Bar | Best result | Verdict |
| --- | --- | --- | --- |
| 1 | Sizing fits tested contract count | Yes (both tiers) | ✅ |
| 2 | Pass materially above ~25–30% junk floor, aim ≥50% | 52.3% but sparse; 30.4% practical | ❌ |
| 3 | Stable walk-forward (not one lucky fold) | 50–67% positive folds | ❌ |
| 4 | Survives slippage stress | comex negative at 2 ticks | ❌ |
| 5 | 2026 holdout does not collapse | 0% MC pass, trade starvation | ❌ |
| 6 | Practical eval timeline (≲45–60 active days) | 0–39% within 6 months wall-clock | ❌ |
| 7 | Param count not a reject reason | n/a | — |

## Recommendation

1. **Do not buy a Lucid eval for MGC.** Neither tier; neither 1 nor 2–3
   contracts.
2. **Stay on MNQ ORB-W long-only + skip-Monday @ 1 micro on 25K** (~64% pass,
   ~46% pass+payout) — `tradingview/lucid_orb_width_25k.pine` unchanged.
3. Gold is now researched at both sizings: GC fails on **risk** (Phases
   11–12), MGC fails on **reward** (this phase). Close the gold line of
   inquiry unless a fundamentally different strategy class (not intraday
   breakout/momentum) is proposed.
4. No TradingView Pine for MGC (nothing passed — deliverable intentionally
   skipped).

## Artifacts

| File | Content |
| --- | --- |
| `data/reports/mgc/phase13_leaderboard.md` | Full ranking + slippage stress |
| `data/reports/mgc/phase13_sizing.md` | ATR / MLL sizing, both tiers |
| `data/reports/mgc/phase13_walk_forward.md` | Fold tables, all 13 families |
| `data/reports/mgc/phase13_holdout.md` | One-shot 2026 holdout |
| `data/reports/mgc/phase13_metrics.json` | Machine-readable results |
| `data/reports/mgc/data_quality.md` | Ingest quality report |
| `config/data_mgc.yaml`, `config/strategies_mgc.yaml`, `config/mgc_phase13.yaml` | Reproducible config |
| `scripts/run_phase13_mgc.py` | Pipeline (shardable; dual-tier MC; holdout; contract sweep) |
