# Phase 20 — Joint Multi-Account Monte Carlo (ORB-W + NR7 ORB)

Question: does opening a second Lucid 25K account (NR7 ORB, a compliant unique bot per
Lucid's no-copy-trading rule) meaningfully raise expected funded-account count / income,
or does correlation between the two long-only equity-index systems mean it's just paying
extra fees for duplicated risk?

Ledgers: `trades_phase9_orb_longonly_wf_oos.parquet` (473 trades, skip-Mon) +
`trades_phase7_nr7_orb_wf_oos.parquet` (181 trades, skip-Mon), shared calendar of 933
non-Monday trading days 2021-06-02 → 2025-11-28 (built from `continuous_5m.parquet`).
10,000 MC attempts, block bootstrap (block=5), 250-day budget, seed 42/43.

## Correlation

- Day-level net-PnL correlation, full calendar (0-fill on no-trade days): **0.187**
- Correlation restricted to the 80 days BOTH strategies fired: **0.725**

NR7 only trades ~19% of days, so the unconditional correlation is heavily diluted by
zeros — it is mostly a *dormant* second bot, not a *duplicate* one. On the days it does
fire alongside ORB-W, the two are meaningfully co-directional (both long-only breakout
systems on the same index), as expected.

## First-pass metric: P(at least one account passes) — MISLEADING, superseded below

Initial framing: joint MC (single attempt/account, same correlated day sequence) gave
P(≥1 pass)=85.7%, vs a **sequential single-account restart baseline** (ORB-W alone,
restarting on failure within the same 250-day budget) at **98.4%**. Read naively this
makes parallel accounts look worse than just restarting one account — but that
comparison is invalid: restarting one account gets ~10 independent attempts in a
250-day window (median ORB-W pass ≈24 days), while the parallel scenario only gave each
account a single un-restarted attempt. It measures "many tries at one thing" against
"one try at two things" — not the actual question.

## Correct metric: expected funded-account count, both accounts with restarts

The real decision isn't "which gets me *a* funded account" (restarting one account
already gets there ~98% of the time) — it's whether a **second, parallel** account
adds *additional* funded accounts (i.e. additional independent income streams) for its
marginal cost, given you're restarting each on failure until the budget runs out.

| Scenario | P(funded by day 250) | E[resets] | E[cost] |
| --- | --- | --- | --- |
| ORB-W alone (restarts) | **98.6%** | 0.52 | **$101** |
| NR7 alone (restarts) | **81.1%** | 0.44 | **$97** |

| | E[# accounts funded] | E[total cost] |
| --- | --- | --- |
| Account 1 only | 0.986 | $101 |
| **Accounts 1 + 2 in parallel** | **1.797** | **$198** |

- Marginal 2nd account: **+0.811 expected funded accounts for +$97 expected cost.**
- Cost per marginal expected funded account: **$102** (account 1) vs **$119** (account 2).

Despite the 0.725 conditional correlation, running both is **close to additive** — not
because the correlation is illusory, but because "restart until funded, no eval time
limit" already drives each account's own pass probability near-certain over a realistic
window; correlation mainly shapes *which specific days* are shared, not whether the slow
second bot eventually clears its own (lower, 81%) bar independently.

## Verdict

**Run both accounts.** The marginal cost of a second funded income stream ($119
cost-per-funded-account) is only ~17% worse than the first ($102), for roughly double
the expected funded-account count. The earlier "prefer sequential restarts" read was an
artifact of comparing the wrong quantities (single-shot parallel vs multi-shot solo) —
corrected here. Two caveats:

1. This models attempt economics only — it does **not** model correlated *drawdown risk*
   during a genuinely bad shared regime (e.g. both accounts failing on the same violent
   week). Fold-level clustering in the block bootstrap partially captures this, but a
   full regime-stress read (worst rolling-90-day window for both accounts jointly) is a
   natural follow-up if pursued further.
2. NR7 trades ~40/yr — its 81% "funded within 250 trading days" masks a much longer
   real-calendar wall clock than ORB-W's, since a 250-*trading*-day budget for a sparse
   strategy spans far more calendar time. Treat NR7 as a slow, low-maintenance second
   stream, not a fast second income source.

## Method notes

- Both accounts use skip-Monday, matching the standing scaling recommendation in
  `PROJECT_STATUS.md` ("NR7 ORB + skipMon").
- No eval time limit per [[lucid-25k-verified]]; 250-day budget is a practical cap for
  restart simulation, not a Lucid rule.
- Script: `scripts/run_phase20_joint_mc.py`.
