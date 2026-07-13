# Phase 15 Report — Scalping Research (FVG / VWAP / Volume) on MNQ + GC

Date: 2026-07-11. Short-hold intraday families on **1m execution bars**
(1m / 3m signals), Lucid Flex discipline unchanged.

## TL;DR

**REJECT all Phase 15 scalpers — keep MNQ ORB-W long-only + skip Monday @ 1 micro
on Lucid 25K (~64% pass) as the live recommendation.**

Scalping is cost- and slippage-hostile. After Task 0 cost-floor math, **500**
grid combos across 10 families (6 MNQ + 4 GC), walk-forward + 10k MC + 0/1/2-tick
slippage stress, and a **one-shot 2026 holdout**:

| Best headline | Why it dies |
| --- | --- |
| MNQ `fvg_vol` **89.5%** pass @ 25K | **Sparsity trap**: 7 OOS trades, 11% positive folds, 1.4 trades/mo. Holdout collapses to **37.9%** pass and **12.9%** ambiguity |
| GC `fvg_vol` **38.1%** / **22.9%** (50K/100K) | Below ~50% bar; fold+ only 50%; holdout **−$4.1k**, **15.2%** / **3.7%** pass |
| MNQ / GC volume & VWAP families | Large negative expectancy after costs; several fail ambiguity >10% |

No candidate beats the incumbent on the full acceptance bar
(cost floor + fold stability + slippage + holdout + ambiguity + wall-clock).

## Task 0 — Cost floor & ambiguity

Full table: `data/reports/phase15_scalp_sizing.md`

| | MNQ micro | GC full-size |
| --- | --- | --- |
| Median 1m RTH bar range | 9.0 pts ($18) | 0.70 pts ($70) |
| Round-trip @ 1 tick slip | **$2.98** | **$28** |
| Min stop for +EV @ 55% WR / 1R | ~**15 pts ($30)** | ~**2.8 pts ($280)** |
| Grid floors | `min_stop_points ≥ 15` | `min_stop ≥ 2.8`, `max_risk ≤ 5` |

Ambiguous-bar rule: candidates with **>10%** ambiguous trades flagged REJECT
(engine resolves stop+target same-bar pessimistically).

## Method

- **MNQ:** WF 24m/6m folds on 2019–2025; MC Lucid **25K** @ 1 micro;
  `daily_loss_stop=$400`; holdout 2026-01-01 → 2026-06-28
- **GC:** WF 18m/6m on 2021–2025; MC Lucid **50K + 100K** @ 1 GC;
  `daily_loss_stop=$600`; holdout 2026-01-01 → 2026-07-10
- Selection on pre-2026 train Sharpe only; holdout frozen — **no re-tune**
- Slippage stress 0/1/2 ticks on 2025 for top eligible families

Strategies: `fvg_scalp`, `vwap_band_scalp` (reversion + pullback),
`volume_spike_scalp`, `fvg_volume_scalp` (stacked). Tests in
`tests/test_phase15_scalp.py` (no-lookahead green).

## MNQ leaderboard (25K @ 1 micro, WF OOS)

Full: `data/reports/phase15_mnq_leaderboard.md`

| Candidate | Combos | Trades | Pass 25K | Amb % | Fold+ % | Net $ | 2025 $ | t/mo |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| mnq_fvg_vol | 32 | 7 | **89.5%** | 0.0% | **11%** | $182 | $182 | 1.4 |
| mnq_vol_spike | 48 | 4015 | 5.3% | 7.7% | 33% | $-7,291 | $-1,123 | 74.4 |
| mnq_fvg_3m | 32 | 432 | 0.4% | 6.0% | 22% | $-1,652 | $-566 | 8.4 |
| mnq_vwap_rev ❌AMB | 24 | 4530 | 0.7% | 24.5% | 0% | $-10,653 | $-4,689 | 84.0 |
| mnq_fvg_1m ❌AMB | 48 | 314 | 0.1% | 21.0% | 33% | $-1,662 | $-600 | 6.1 |
| mnq_vwap_pb ❌AMB | 12 | 3774 | 0.0% | 17.0% | 0% | $-15,762 | $-2,108 | 70.0 |

`mnq_fvg_vol` is the Phase 13 sparsity trap again: MC loves a tiny lucky ledger;
fold stability and frequency fail the bar before holdout is even considered.

## GC leaderboard (50K primary / 100K, WF OOS)

Full: `data/reports/gc/phase15_gc_leaderboard.md`

| Candidate | Combos | Trades | Pass 50K | Pass 100K | Amb % | Fold+ % | Net $ | 2025 $ |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| gc_fvg_vol | 64 | 83 | **38.1%** | 22.9% | 8.4% | 50% | $1,316 | $728 |
| gc_fvg_1m | 96 | 255 | 23.9% | 7.3% | 5.9% | 50% | $-595 | $-5,029 |
| gc_vol_spike | 96 | 2660 | 9.6% | 3.2% | 3.5% | 0% | $-72,840 | $-39,286 |
| gc_vwap_rev ❌AMB | 48 | 1482 | 10.2% | 2.1% | 18.2% | 17% | $-29,683 | $-3,341 |

GC scalps must clear ~$28/round-trip. Even the best family never reaches the
~50% Lucid bar, and 2025 is weak or deeply negative for non-sparse families.

## Slippage (2025) — top eligible

| Family | 0 tick | 1 tick | 2 tick |
| --- | --- | --- | --- |
| mnq_fvg_vol | +$195 | +$188 | +$181 |
| mnq_vol_spike | $-346 | $-916 | $-1,486 |
| gc_fvg_vol | +$878 | +$508 | +$138 |
| gc_fvg_1m | $-8.8k | $-10.4k | $-12.1k |

Volume/VWAP families die under 2-tick stress (scalping-critical). Sparse FVG+vol
survives dollar-wise on tiny samples but fails other gates.

## 2026 holdout (one-shot, frozen params)

| Family | Trades | Net $ | Amb % | MC pass |
| --- | --- | --- | --- | --- |
| mnq_fvg_vol | 31 | +$423 | 12.9% | **37.9%** 25K |
| mnq_vol_spike | 323 | $-2,872 | 9.6% | 4.7% |
| mnq_fvg_3m | 127 | $-196 | 4.7% | 0.5% |
| gc_fvg_vol | 105 | $-4,148 | 16.2% | **15.2%** 50K / 3.7% 100K |
| gc_fvg_1m | 331 | $-24,958 | 18.1% | 6.7% / 1.3% |

Holdout confirms: the only MNQ “pretty” backtest was a sparse mirage; GC
scalps bleed once costs and 2026 regime meet the frozen params.

## Acceptance bar checklist

| Gate | Result |
| --- | --- |
| +EV after full costs + 1 tick | Fail for dense families; sparse FVG+vol only in-sample |
| Lucid pass ≥ ~50% on recommended tier | Fail (honest dense ≤5%; sparse 89% invalid) |
| ≥60% positive WF folds + positive 2025 | Fail (best dense fold+ 33%; GC 50%) |
| Survive 2-tick slippage | Fail for dense; sparse OK but irrelevant |
| 2026 holdout net + MC | Fail (best holdout 37.9% MNQ / 15% GC) |
| Ambiguity < ~10%; ≤ ~45 active days to pass | Amb fails several; sparsity fails wall-clock |

## Verdict

Phase 15 does **not** replace or augment MNQ ORB-W. Short-hold FVG / VWAP /
volume families on 1m bars do not clear Lucid economics on MNQ or GC.

- **MNQ:** cheap ticks help but scalp edges evaporate after commission +
  ambiguity + fold instability.
- **GC:** ~$28 round-trip makes true scalping structurally unattractive; echoes
  Phases 11–13 gold rejection under a different strategy class.

Live recommendation unchanged: **ORB-W long-only + skip Monday, 1 MNQ micro,
Lucid Flex 25K** (`tradingview/lucid_orb_width_25k.pine`).

## Artifacts

- Config / runner: `config/phase15_scalp.yaml`, `scripts/run_phase15_scalp.py`
- Strategies: `src/strategies/{fvg_scalp,vwap_band_scalp,volume_spike_scalp,fvg_volume_scalp}.py`
- Tests: `tests/test_phase15_scalp.py`
- Sizing: `data/reports/phase15_scalp_sizing.md`
- Leaderboards: `data/reports/phase15_scalp_leaderboard.md`,
  `phase15_mnq_leaderboard.md`, `data/reports/gc/phase15_gc_leaderboard.md`
- Holdouts: `data/reports/phase15_mnq_holdout.md`,
  `data/reports/gc/phase15_gc_holdout.md`
