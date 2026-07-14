# Phase 21 — Re-scoring audit: frozen ledgers under verified Lucid rules

Frozen WF-OOS ledgers (Phases 7/16/17/18), cost-corrected to the verified
$0.50/side ($1.00/RT; slippage unchanged in fill prices), re-scored with
10k MC block bootstrap seed 42, **no eval time limit**, and the verified
funded journey (no consistency rule, $100 qualifying day, $500/$1,000 payout).
**No new fitting. No param changes.** Audit of old conclusions only.

Bar (incumbent re-backtest): **69.8% pass / 51.6% pass+payout**. Flag rule: within 2pts on BOTH + density (>= 100 trades, >= 4 t/mo, fold+ >= 50%).

## WF-OOS re-scores (ranked by corrected pass rate)

| Candidate | Trades | t/mo | Fold+ | Old pass | **New pass** | **New pass+payout** | Med d | Net $ | Dense? | FLAG |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| p17_orb_only_inside | 12 | 1.5 | 11% | 98.1% | **98.3%** | **95.8%** | 11 | $1,384 | n | — |
| p16_structure_gated_orb | 169 | 3.1 | n/a | n/a | **70.1%** | **51.4%** | 23 | $6,002 | n | — |
| incumbent_rebacktest | 473 | 8.8 | 89% | 69.8% | **69.8%** | **51.6%** | 26 | $12,501 | Y | — |
| p17_orb_w_control | 473 | 8.8 | 89% | 64.5% | **69.8%** | **51.6%** | 26 | $12,501 | Y | **FLAG** |
| p17_orb_inside_day | 423 | 7.9 | 89% | 64.2% | **69.3%** | **50.4%** | 26 | $10,916 | Y | **FLAG** |
| p18_orb_tod | 421 | 7.8 | 78% | 59.2% | **68.9%** | **50.7%** | 30 | $10,053 | Y | **FLAG** |
| p9_orb_longonly (xcheck) | 473 | 8.8 | 89% | 64.3% | **68.8%** | **49.3%** | 24 | $14,194 | Y | — |
| p18_orb_w_control | 414 | 8.7 | 78% | 63.8% | **68.4%** | **49.0%** | 24 | $11,432 | Y | — |
| p17_orb_prior_regime | 147 | 2.7 | 78% | 61.6% | **66.2%** | **46.7%** | 25 | $3,518 | n | — |
| p7_nr7_orb | 181 | 3.4 | n/a | 63.5% | **65.1%** | **44.5%** | 18 | $6,272 | n | — |
| p17_orb_vix_on_stack | 356 | 6.6 | 89% | 58.3% | **64.5%** | **43.8%** | 27 | $8,541 | Y | — |
| p17_orb_vix_band | 357 | 6.6 | 89% | 52.2% | **64.1%** | **42.9%** | 34 | $6,020 | Y | — |
| p7_orb_width | 659 | 12.2 | n/a | 61.8% | **63.9%** | **44.2%** | 22 | $18,252 | Y | — |
| p17_orb_on_context | 426 | 7.9 | 78% | 57.4% | **63.6%** | **43.0%** | 26 | $9,577 | Y | — |
| p18_orb_risk_cap | 414 | 8.7 | 78% | 58.3% | **62.1%** | **41.3%** | 25 | $9,252 | Y | — |
| p18_mes_diverge_orb | 242 | 4.5 | 78% | 58.4% | **61.6%** | **40.3%** | 22 | $5,715 | Y | — |
| p18_orb_macro_skip | 414 | 7.7 | 78% | 56.9% | **61.5%** | **39.6%** | 24 | $10,196 | Y | — |

## 2026 holdout re-scores (frozen, cost-corrected, no time limit)

| Candidate | Trades | Net $ | Pass % | Pass+payout % |
| --- | --- | --- | --- | --- |
| p16_structure_gated_orb | 8 | $1,101 | 100.0% | 100.0% |
| incumbent_rebacktest | 52 | $2,836 | 67.8% | 47.7% |
| p17_orb_w_control | 52 | $2,836 | 67.8% | 47.7% |
| p17_orb_inside_day | 51 | $2,697 | 67.2% | 46.4% |
| p18_orb_tod | 44 | $2,628 | 92.8% | 84.4% |
| p9_orb_longonly (xcheck) | 50 | $2,020 | 60.5% | 38.9% |
| p18_orb_w_control | 52 | $2,836 | 67.8% | 47.7% |
| p17_orb_prior_regime | 24 | $420 | 61.8% | 35.2% |
| p7_nr7_orb | 15 | $148 | 34.0% | 11.5% |
| p17_orb_vix_on_stack | 50 | $3,874 | 90.6% | 81.2% |
| p7_orb_width | 76 | $1,945 | 54.6% | 32.1% |
| p18_orb_risk_cap | 52 | $1,834 | 60.2% | 37.6% |
| p18_mes_diverge_orb | 20 | $1,176 | 67.8% | 49.4% |

## Flagged candidates

- **p17_orb_w_control** — see table. 
- **p17_orb_inside_day** — see table. 
- **p18_orb_tod** — see table. 

## Notes

- Cost correction is exact for commission (a per-trade constant); fills and
  slippage are unchanged from the original engine runs.
- Fold+ shares carried from the original phase leaderboards (a property of
  the frozen WF runs, unaffected by re-scoring).
- p7 ledgers get skip-Monday post-hoc (matching their reported numbers);
  P17/P18 families already skip Monday in-grid.
