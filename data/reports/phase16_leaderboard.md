# Phase 16 Leaderboard — Structure / Levels / Profile / MES (MNQ 25K)

Sorted by 25K pass → fold stability → UPI. Incumbent ORB-W long-only + skipMon shown first for comparison.

| Candidate | Combos | Trades | Pass 25K | Fold+ % | Net $ | UPI | MaxDD | 2025 $ | t/mo |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **ORB-W long-only + skipMon (incumbent)** | 0 | 473 | 64.3% | — | $13,731 | 10.7 | $-2,500 | $4,201 | 8.8 |
| P16 overnight_fade | 16 | 697 | 96.5% | 100% | $28,105 | 76.9 | $-1,257 | $4,518 | 12.9 |
| P16 structure_gated_orb | 18 | 169 | 66.0% | 78% | $5,837 | 17.1 | $-1,542 | $1,229 | 3.1 |
| P16 mes_agree_orb | 4 | 337 | 62.0% | 78% | $8,620 | 8.5 | $-2,484 | $3,793 | 6.3 |
| P16 mes_diverge_orb | 4 | 227 | 57.8% | 78% | $4,992 | 8.5 | $-1,808 | $228 | 4.2 |
| P16 round_break | 16 | 2065 | 22.4% | 44% | $2,708 | 0.6 | $-2,840 | $1,847 | 38.3 |
| P16 round_fade | 16 | 507 | 19.2% | 44% | $2,889 | 2.6 | $-1,740 | $1,113 | 9.5 |
| P16 structure_gated_vwap | 32 | 919 | 18.8% | 56% | $242 | 0.1 | $-2,522 | $-290 | 17.0 |
| P16 prior_day_fade | 16 | 851 | 15.4% | 44% | $-78 | -0.0 | $-2,586 | $-375 | 15.9 |
| P16 poc_reversion | 24 | 2234 | 4.2% | 11% | $-7,546 | -0.3 | $-10,092 | $652 | 41.4 |
| P16 prior_day_break | 24 | 934 | 3.6% | 33% | $-4,141 | -0.5 | $-4,835 | $-931 | 17.3 |
| P16 poc_breakout | 24 | 1155 | 0.9% | 11% | $-7,166 | -0.4 | $-7,805 | $-2,526 | 21.4 |
| P16 overnight_break | 24 | 558 | 0.1% | 11% | $-9,452 | -0.6 | $-9,490 | $-797 | 10.3 |

## Slippage stress (2025, top 3 by pass rate)

## P16 overnight_fade — slippage stress (2025)

| Slippage (ticks) | Trades | Net $ | PF | Sharpe | Expectancy |
| --- | --- | --- | --- | --- | --- |
| 0 | 148 | $5,182 | 1.71 | 3.77 | $35.01 |
| 1 | 148 | $5,141 | 1.70 | 3.73 | $34.73 |
| 2 | 148 | $5,099 | 1.70 | 3.70 | $34.45 |

## P16 structure_gated_orb — slippage stress (2025)

| Slippage (ticks) | Trades | Net $ | PF | Sharpe | Expectancy |
| --- | --- | --- | --- | --- | --- |
| 0 | 19 | $969 | 1.45 | 2.23 | $51.02 |
| 1 | 19 | $952 | 1.44 | 2.19 | $50.13 |
| 2 | 19 | $935 | 1.43 | 2.15 | $49.23 |

## P16 mes_agree_orb — slippage stress (2025)

| Slippage (ticks) | Trades | Net $ | PF | Sharpe | Expectancy |
| --- | --- | --- | --- | --- | --- |
| 0 | 83 | $3,819 | 1.58 | 3.09 | $46.01 |
| 1 | 83 | $3,748 | 1.57 | 3.03 | $45.16 |
| 2 | 83 | $3,678 | 1.56 | 2.98 | $44.31 |


## Sparsity / wall-clock

| Family | Active days | Span days | Trades/mo |
| --- | --- | --- | --- |
| incumbent | 473 | 1639 | 8.8 |
| overnight_fade | 506 | 1642 | 12.9 |
| structure_gated_orb | 169 | 1639 | 3.1 |
| mes_agree_orb | 337 | 1638 | 6.3 |
| mes_diverge_orb | 227 | 1638 | 4.2 |
| round_break | 1098 | 1642 | 38.3 |
| round_fade | 433 | 1632 | 9.5 |
| structure_gated_vwap | 604 | 1642 | 17.0 |
| prior_day_fade | 540 | 1632 | 15.9 |
| poc_reversion | 1152 | 1642 | 41.4 |
| prior_day_break | 934 | 1642 | 17.3 |
| poc_breakout | 1155 | 1642 | 21.4 |
| overnight_break | 558 | 1642 | 10.3 |

## 2026 Holdout (one-shot, frozen params)

| Family | Trades | Net $ | Pass 25K |
| --- | --- | --- | --- |
| overnight_fade | 68 | $6,053 | 99.2% |
| structure_gated_orb | 8 | $1,093 | 100.0% |
| mes_agree_orb | 43 | $1,039 | 46.4% |
| mes_diverge_orb | 20 | $1,156 | 67.4% |
| round_break | 243 | $-780 | 28.2% |
| incumbent ORB-W +skipMon (Phase 9 holdout) | 50 | $1,970 | 58.8% |

**Verdict: Promote overnight_fade as primary; keep ORB-W as Account 2.**
