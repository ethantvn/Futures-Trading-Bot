# Final Recommendation — Lucid Flex Evaluation

Date: 2026-07-06. Based on Phase 5 validated **opening-range breakout** only.
EMA trend and other families were rejected after walk-forward + 2026 holdout.

## Strategy (validated)

- **Family:** Opening-range breakout (ORB)
- **Params:** `{'expire_minutes': 120, 'range_minutes': 30, 'target_r': 1.5}`
- **Signal timeframe:** 5m; fills on 1m; flat by 15:55 ET
- **Evidence ledger:** `trades_opening_range_breakout_wf_oos.parquet` (993 trades, walk-forward OOS 2021–2025)
- **Walk-forward OOS:** net $18,377, Sharpe 1.16, PF 1.20
- **2026 holdout (single run):** +$948, PF 1.06 — supportive but not strong

## Recommended configs for your 25K eval

### Conservative (recommended)

- **Size:** 1 MNQ micro every session
- **Why:** Highest pass probability and lowest expected reset cost in every simulation
- **Rules discipline:** One ORB trade/day max; if largest day would exceed 50% of running profit near target, stop for the day or take a small second session another day
- **Do not:** Scale to 2+ micros on 25K unless you accept materially lower pass rate

### Moderate (optional — higher variance)

- **Size:** 2 MNQ micros every session (fixed)
- **Sim pass rate:** ~36% vs ~44% conservative; median pass ~10 days vs ~22
- **E[cost] to funded:** ~$178 (discounted eval + expected resets)
- **Dynamic downshift** (2→1 micro when cushion < $600) did **not** improve 25K pass rate vs fixed 2 micros
- **Only consider if** you prioritize speed over pass probability

## Sizing & account comparison (10k Monte Carlo each)

- Ledger: walk-forward OOS trades, block bootstrap (5-day blocks)
- Eval fees: discounted prices from lucid configs

| Policy | Account | Pass % | Fail % | Med days | <=15d % | <=20d % | E[resets] | E[cost] | E[profit/attempt] | Cushion@pass |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| conservative | LucidFlex 25K | 44.3% | 51.9% | 22 | 13.4% | 20.4% | 1.3 | $146 | $413 | $1,609 |
| moderate | LucidFlex 25K | 35.8% | 63.8% | 10 | 26.5% | 30.8% | 1.8 | $178 | $355 | $2,288 |
| downshift_400 | LucidFlex 25K | 32.7% | 66.9% | 10 | 24.4% | 27.9% | 2.1 | $193 | $300 | $2,257 |
| downshift_600 | LucidFlex 25K | 33.0% | 66.3% | 11 | 22.1% | 26.1% | 2.0 | $192 | $328 | $2,254 |
| conservative | LucidFlex 50K | 19.4% | 19.5% | 42 | 1.0% | 2.0% | 4.2 | $492 | $944 | $3,338 |
| moderate | LucidFlex 50K | 40.3% | 54.3% | 25 | 8.9% | 14.9% | 1.5 | $239 | $892 | $3,640 |
| downshift_400 | LucidFlex 50K | 38.5% | 56.4% | 25 | 8.8% | 14.7% | 1.6 | $250 | $840 | $3,644 |
| downshift_600 | LucidFlex 50K | 37.8% | 55.6% | 25 | 8.8% | 14.4% | 1.6 | $255 | $839 | $3,652 |

## Decision summary

**Best 25K policy in simulation:** `conservative` — 44.3% pass, median 22 days, E[cost] $146

### 25K vs 50K (same ORB edge)

- **conservative:** 25K pass 44.3% (E[cost] $146) vs 50K pass 19.4% (E[cost] $492)
- **moderate:** 25K pass 35.8% (E[cost] $178) vs 50K pass 40.3% (E[cost] $239)

- **50K is harder:** profit target is 2.4× larger ($3,000 vs $1,250) with only 2× drawdown room ($2,000 vs $1,000). Same strategy edge yields lower pass rates on 50K.
- **You own 25K:** stay on 25K; do not upgrade account size for this strategy.

## Execution checklist (live eval)

1. Trade **MNQ** only; **1 micro** default (20 micro max firm cap — irrelevant at 1).
2. ORB: 30-minute opening range (09:30–10:00 ET), stop entry 1 tick beyond range, stop at opposite side, target **1.5R**, pending expires 120 minutes.
3. Flat by **15:55 ET**; no new entries after **15:30 ET**.
4. **Consistency:** no single day > 50% of total profit at pass — plan 2+ balanced days.
5. **MLL:** EOD only — intraday dips below floor are OK if you close above it.
6. Verify your platform commission (placeholder $0.99/side/micro in backtests).

## Rejected strategies

| Strategy | Reason |
| --- | --- |
| ema_trend | WF OOS flat; 2026 holdout −$2,568 |
| vwap_pullback | Negative baseline expectancy |
| prev_day_hl_breakout | Negative baseline expectancy |
| bollinger_mean_reversion | Negative baseline expectancy |

## Caveats

- Past pass rates are **estimates** from historical bootstrap, not guarantees.
- Commission/slippage placeholders may differ from your live platform.
- 2026 holdout was run once; do not re-optimize on it.
- Lucid EOD session-close time assumed 17:00 ET (CME).
