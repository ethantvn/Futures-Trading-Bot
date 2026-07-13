# Phase 14 Report — Lucid Flex 100K Tier Study

Date: 2026-07-11. Frozen ledgers only — no strategy re-optimization.
Full MC tables: `data/reports/phase14_100k_leaderboard.md`.

## TL;DR

**Stay on 25K @ 1 micro.** The 100K tier is strictly worse per dollar for the
frozen MNQ ORB-W edge, and gold remains rejected on 100K after applying the
sparsity and holdout guards that its headline numbers hide behind.

- Best 100K MNQ sizing is **4 micros: 52.5% pass** vs **64.3%** on 25K @ 1 —
  and it costs **$284 expected** vs **$103** to reach a funded account.
- The structural reason: 100K's **target/MLL ratio is 2.0×** ($6,000/$3,000)
  vs 1.25× on 25K. Bigger MLL does not mean easier — you need twice the edge
  per drawdown dollar, so you must size up, which converts timeouts into
  blowups (fail rate 31% → 44% at 4 micros, 61% at 10).
- Gold on 100K: GC macro ledgers post 55–60% headline MC pass but are
  **sparse-event lotteries** (0–11.5% pass within a realistic 6-month window)
  whose **2026 holdouts collapse (12.0% / 0.0%)**. MGC at 8 micros hits 40.5%
  WF but **0% holdout (100% fail)**. GC sizing is still unsound: **25% of all
  days** have a daily range above the $3,000 MLL at 1 contract.

## 100K rules used (`config/lucid_100k.yaml` — VERIFY against dashboard)

| Field | Value |
| --- | --- |
| Balance / target / MLL | $100,000 / $6,000 / $3,000 (EOD trailing, locks at start) |
| Consistency / min days | 50% / 2 |
| Max micros | 60 |
| Eval fee / reset | $225 ($157.50 discounted) / $140 |

**Target/MLL ratio by tier: 25K = 1.25×, 50K = 1.50×, 100K = 2.00×.**
Phase 1 capture 2026-07-06; all fees marked VERIFY. If your dashboard shows
different 100K numbers, re-run `scripts/run_phase14_100k.py` after editing the
config.

## Part A — MNQ ORB-W (frozen Phase 9 ledger, 473 OOS trades, skipMon)

Contract sweep highlights (10k MC, block bootstrap, 60-day cap, discounted fees):

| Account | Micros | Pass % | Fail % | Timeout % | Med days | ≤20d | E[cost] |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 25K | 1 | **64.3%** | 31.3% | 4.4% | 23 | 27% | **$103** |
| 50K | 2 | 59.4% | 33.1% | 7.5% | 28 | 17% | $163 |
| 100K | 1 | 0.5% | 0.7% | 98.9% | 53 | 0% | $28,589 |
| 100K | 3 | 47.7% | 34.5% | 17.8% | 35 | 7% | $311 |
| 100K | **4** | **52.5%** | 43.5% | 4.0% | 26 | 17% | $284 |
| 100K | 5 | 49.4% | 49.7% | 0.8% | 19 | 27% | $301 |
| 100K | 8 | 42.7% | 57.2% | 0.1% | 10 | 38% | $345 |
| 100K | 10 | 39.3% | 60.6% | 0.1% | 8 | 37% | $374 |

The sizing intuition from the prompt is confirmed with formal numbers:
1 micro on 100K times out 98.9% of attempts; ~3–5 micros are needed to make
the $6,000 target reachable; the prior ad-hoc "~49% @ 5 micros" reproduces
exactly (49.4%). Sizing past 5 only trades pass probability for speed —
fail rate crosses 50% at 5 micros and 60% at 10.

**Journey MC** (pass + first payout; funded-phase structure mirrored from the
25K implementation — dollar thresholds beyond the MLL distance are VERIFY):

| Account | Micros | Pass % | Pass+Payout % |
| --- | --- | --- | --- |
| 25K | 1 | 64.4% | **45.6%** |
| 50K | 2 | 59.1% | 41.9% |
| 100K | 4 | 51.9% | 33.5% |

**2026 holdout** (frozen params, single replay through tier MC — no re-tune):

| Account | Micros | Pass % | Med days |
| --- | --- | --- | --- |
| 25K | 1 | **58.8%** | 13 |
| 50K | 2 | 55.1% | 16 |
| 100K | 4 | 48.0% | 15 |

Holdout ordering matches WF ordering (no tier-specific surprise); 25K stays
on top.

## Part B — Gold under the $3,000 MLL

### B1: full-size GC — still structurally unsound

- Median daily RTH range **$1,930**, P95 **$7,810**, max $44,190 at 1 GC
- **25% of all days** exceed the entire $3,000 MLL in open-to-close range
- Deep grids NOT reopened (per prompt: only if a frozen ledger cleared
  ~45–50% with practical timeline *and* live holdout — none did, see below)

### B2: frozen gold ledgers on 100K MC — headline vs guards

| Ledger | Micros | WF pass | 6-mo wall-clock pass | 2026 holdout pass |
| --- | --- | --- | --- | --- |
| GC11 macro_nfp_cpi | 1 | 59.7% | 11.5% (2.7 trades/mo) | **12.0%** |
| GC12 macro_nfp | 1 | 55.4% | 0.0% (1.0 trade/mo) | **0.0%** |
| GC12 comex_orb_deep | 1 | 29.7% | 27.7% | n/a (junk floor) |
| MGC13 comex_orb_deep | 8 | 40.5% | 32.3% | **0.0%** (100% fail) |
| MGC13 comex_orb_deep | 10 | 39.8% | — | — |

The bigger 100K MLL does make GC macro ledgers *look* strong (59.7%!), but
both Phase 13 guards kill them, same as before:

1. **Sparsity** — NFP/CPI events arrive ~1–2.7/month; "28 median days to
   pass" means 1–2+ calendar years inside an eval.
2. **Holdout** — the 2025–2026 regime broke the gold macro-release edge
   (Phases 11–12 conclusion), and it stays broken at a $3,000 MLL.

MGC at 8–10 micros ($80–100/pt ≈ full GC exposure) inherits GC's problem and
adds a 0%-pass 2026 holdout. **Gold remains closed on every tier.**

## Part C — Decision table

| Option | Pass % | Med days | E[cost] | Holdout | Pass+Payout | Recommend? |
| --- | --- | --- | --- | --- | --- | --- |
| **25K MNQ @ 1 micro** | **64.3%** | 23 | **$103** | **58.8%** | **45.6%** | ✅ **primary — unchanged** |
| 50K MNQ @ 2 | 59.4% | 28 | $163 | 55.1% | 41.9% | No — dominated by 25K |
| 100K MNQ @ 4 | 52.5% | 26 | $284 | 48.0% | 33.5% | Only if you explicitly want the larger funded base and accept −12pp pass, 2.8× cost |
| 100K GC macro @ 1 | 59.7%* | 28* | $252* | 12.0% / 0.0% | — | ❌ sparse lottery + holdout collapse |
| 100K MGC @ 8 | 40.5% | 22 | $364 | 0.0% | — | ❌ holdout collapse |

\* headline WF numbers that fail the sparsity/holdout guards — shown to
document the trap, not as candidates.

**Answer to the user's question:** buy the 25K, not the 100K. The 100K only
makes sense if the payout base of a funded $100K account (larger contract
caps, bigger drawdown cushion once funded) is worth ~12 points of pass
probability and ~$180 of extra expected eval cost to you — and even then run
it at **4 micros**, not 1, not 10. Gold justifies no tier.

## Artifacts

| File | Content |
| --- | --- |
| `config/lucid_100k.yaml` | 100K rules + fees (VERIFY) |
| `data/reports/phase14_100k_leaderboard.md` | Full MC tables (all tiers/sizes) |
| `scripts/run_phase14_100k.py` | Reproducible sweeps + guards |
| `src/evaluation/monte_carlo.py` | `pass_within_days` now configurable (default unchanged) |
