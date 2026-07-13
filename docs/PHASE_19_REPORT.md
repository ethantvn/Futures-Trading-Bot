# Phase 19 Report — Eval Policy Optimization (Frozen ORB-W)

Date: 2026-07-12.

## TL;DR

**No sizing policy beats fixed 1 micro.** State-dependent upshift, post-lock
aggression, cushion-skip, downshift, and consistency-cap all **hurt or fail to
lift** Lucid 25K pass / pass+payout vs the incumbent on the same ORB-W ledger.

| Policy | WF Pass (avg) | WF Pass+payout | vs fixed_1 |
| --- | --- | --- | --- |
| **fixed_1 (keep)** | **62.9%** | **43.8%** | — |
| post_lock_2 | 58.7% | 41.0% | worse |
| upshift + cap | 54.8% | 38.6% | worse |
| fixed_2 | 51.6% | 36.5% | worse |

Primary reference (block, seed 42, max_days=60): **fixed_1 = 64.3% / 45.6%**
matches Phase 9 incumbent.

## What we tested

Same trades as Phase 9 ORB-W (`trades_phase9_orb_longonly_wf_oos.parquet` +
2026 holdout), **only contract policy changed**:

- Fixed 1 / 2 micro
- Upshift 1→2 when cushion ≥ $400–800
- Downshift 2→1 near MLL
- Post-lock upshift (2–3 micros after MLL locks)
- Cushion skip (stand aside when cushion low)
- Upshift + consistency cap near target

Harness: 10k MC × 3 seeds × 2 sample modes × max_days {60,90,120} × 2 ledgers.

## Findings

1. **Dynamic sizing adds variance without improving the eval game** — upshift
   and post-lock policies increase drawdown-fail share; cushion-skip adds
   timeouts without enough DD protection.
2. **Fixed 2 micro is strictly worse** than fixed 1 (51.6% vs 63% avg pass).
3. **max_days sensitivity**: raising analyst timeout to 90/120 days converts
   some timeouts to passes (fixed_1 → 68% at 120d) — **verify whether Lucid
   Flex eval has a calendar deadline** before treating this as real edge.
4. **Funded-phase policy** not separately swept here; journey MC used 1 micro
   post-pass (conservative).

## Decision

**Keep trading 1 MNQ micro every session.** Do not upshift, downshift, or skip
based on cushion on this ledger.

## Deliverables

- `src/evaluation/sizing.py` — Upshift, PostLock, CushionSkip, ConsistencyCap
- `src/evaluation/journey.py` — sized journey MC
- `config/phase19_eval_policy.yaml`, `scripts/run_phase19.py`
- `data/reports/phase19_leaderboard.md`

## Next (if still pursuing higher pass)

1. **19B** — Confirm Lucid rules (eval time limit, payout thresholds)
2. **19C** — Databento `trades` schema opening-range delta gate (new alpha)
3. Parallel eval attempts (account economics, not sizing research)
