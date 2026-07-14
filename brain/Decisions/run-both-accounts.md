---
type: decision
decided: 2026-07-13
status: locked
---

# Run both accounts (ORB-W + NR7, parallel)

Open a second Lucid 25K account on **NR7 ORB + skipMon** alongside the primary ORB-W account, rather than running one account sequentially and restarting on failure. Evidence: [[joint-multiaccount-mc]].

Marginal 2nd account: **+0.81 expected funded accounts for +$97 expected cost** ($119 cost-per-funded-account vs $102 for account 1 alone) over a 250-trading-day restart-until-funded model. Despite real correlation (0.725 on the ~80 days/933 both fire), the two are close to additive because each account restarts independently until funded — correlation shapes which days are shared, not whether the slower bot eventually clears its own bar.

**Caveats carried forward, not fully modeled:**
- Correlated drawdown risk in a genuinely bad shared week (both accounts failing together) isn't isolated from the average-case restart economics.
- NR7 trades ~40/yr — "funded within 250 trading days" is a much longer real calendar span than for ORB-W. Treat it as a slow second stream, not a second fast payout.
- Must remain a genuinely unique bot per Lucid's no-identical-copy-trading policy — see `Resources/lucid-links.md`.
- **Phase 21 audit (2026-07-13):** NR7's 2026 H1 holdout re-scored weak — 34% pass / 11.5% pap on a sparse 15-trade window (WF still 65.1/44.5). Too noisy to flip this decision, but **check NR7 at the [[wf-reselection-2026-12]] refresh before paying account 2's eval fee** if that decision point hasn't arrived yet.

**Would reopen if:** a joint worst-case regime stress test (not yet run) shows both accounts failing together at a rate that erodes the $119/acct marginal economics, or NR7's live params drift from the frozen Phase 7 ledger enough to invalidate the correlation estimate.
