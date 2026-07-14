---
type: experiment
status: rejected
priority: P2
phase: 23
family: gold-user-override
next-action: none
verdict: ALL KILLED at Stage A. Every setup's BEST in-sample combo loses after costs on both GC and MGC (PF 0.80-0.91). The 65%-WR momentum reversal loses $45/trade — win rate is not edge. Fourth and final gold rejection.
updated: 2026-07-13
---

# Phase 23 — TradingSim article gold setups — REJECTED

**Explicit user override of [[gold-gc-mgc]]** (2026-07-13). Bounded test of the article's five setups on 4.5y GC/MGC (2021-06 → 2025-12; 2026 holdout never touched — no survivor reached Stage B). Report: `data/reports/gc/phase23_article_screen.md`. Code: `src/strategies/gold_article.py`, `scripts/run_phase23_gold_article.py`.

## Results (BEST in-sample combo per family — i.e., optimistic)

| Setup | GC exp/trade | MGC exp/trade | Note |
| --- | --- | --- | --- |
| #4 EMA 20/50 + Stoch pullback (+#2 daily gate) | **−$17.17** (1028 t) | −$3.83 | Daily-trend gate chosen by optimizer; still loses |
| #5 30m momentum reversal (50% counter-close) | **−$45.10** @ 65% WR | −$31.09 | The win-rate trap in one row: 2 of 3 trades win, expectancy deeply negative |
| #3 Round-number fade/break ($10/$25, raw-anchored) | **−$32.13** (960 t) | −$4.01 | Fade at $25 was the best variant; PF 0.80 |
| #1 Yen (6J) correlation | untestable | untestable | No yen futures data; the "80%" claim remains unverified marketing |
| Article's 8:00–12:00 ET window | — | — | Selected by the optimizer everywhere — liquidity is real, edge inside it is not |

Every kill bar was hit with room to spare; best-in-sample selection biases these numbers UP and they are still all negative. Stage B (WF/MC/holdout) never ran — nothing earned it.

## What this adds to the tombstone

Fourth independent gold rejection, first one testing *retail-article setups specifically*: P11–12 (session ORBs/VWAP/macro, GC), P13 (MGC), P15 (scalps), **P23 (article patterns)**. The pattern across all four: gold's cost floor ($28/RT GC) and intraday noise eat every bar-data entry signal tried so far. [[gold-gc-mgc]] stands, now with user-override provenance.

**Would reopen if:** new data class only (e.g., real order-flow), same as every other bar-data family.
