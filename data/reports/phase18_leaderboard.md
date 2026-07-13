# Phase 18 Leaderboard — Deep Multi-Family (MNQ 25K)

Train scorer = **UPI** (Lucid-survival proxy). Ranked by MC pass, then pass+payout.
Dense = ≥100 OOS trades, ≥4 t/mo, ≥50% positive folds.

| Candidate | Combos | Dense? | Trades | Pass % | Pass+payout % | Fold+ % | Net $ | t/mo |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **ORB-W long-only + skipMon (incumbent)** | 0 | n | 473 | 64.3% | 45.6% | — | $13,731 | 8.8 |
| P18 orb_w_control ★ | 1 | Y | 414 | 63.8% | 46.7% | 78% | $11,026 | 8.6 |
| P18 orb_tod ★ | 16 | Y | 421 | 59.2% | 43.5% | 78% | $9,640 | 7.8 |
| P18 mes_diverge_orb ★ | 4 | Y | 242 | 58.4% | 38.3% | 78% | $5,478 | 4.5 |
| P18 orb_risk_cap ★ | 4 | Y | 414 | 58.3% | 38.5% | 78% | $8,847 | 8.6 |
| P18 orb_macro_skip ★ | 6 | Y | 414 | 56.9% | 35.3% | 78% | $9,791 | 7.7 |
| P18 ema_trend | 16 | Y | 1617 | 32.6% | 16.0% | 78% | $5,797 | 30.0 |
| P18 roc_vol_mom | 32 | Y | 1343 | 26.1% | 10.9% | 56% | $1,445 | 24.9 |
| P18 prior_day_fade | 8 | Y | 651 | 20.0% | 9.3% | 56% | $2,754 | 12.1 |
| P18 macd_mom | 12 | n | 748 | 15.5% | 3.7% | 11% | $-3,858 | 17.8 |
| P18 vwap_reversion | 48 | Y | 578 | 15.0% | 4.8% | 56% | $-525 | 12.1 |
| P18 stoch_fade | 4 | n | 879 | 14.7% | 4.2% | 22% | $-3,237 | 21.0 |
| P18 donchian | 72 | n | 821 | 6.6% | 0.8% | 22% | $-6,355 | 22.8 |
| P18 overnight_fade | 8 | Y | 672 | 5.5% | 1.5% | 67% | $239 | 14.0 |
| P18 bollinger_mr | 27 | n | 165 | 3.3% | 0.4% | 11% | $-1,779 | 3.1 |
| P18 rsi_fade | 32 | n | 88 | 1.0% | 0.0% | 0% | $-1,101 | 1.8 |
| P18 overnight_break | 8 | n | 98 | 0.7% | 0.1% | 11% | $352 | 16.6 |
| P18 orb_fade | 64 | n | 627 | 0.0% | 0.0% | 22% | $-1,911 | 11.6 |
| P18 prior_day_break | 8 | n | 106 | 0.0% | 0.0% | 0% | $-1,136 | 17.7 |

## Challengers (≥ incumbent−2pts, dense)

_No dense challenger within 2pts of incumbent._

## Slippage stress (2025, top dense)

## P18 orb_w_control — slippage stress (2025)

| Slippage (ticks) | Trades | Net $ | PF | Sharpe | Expectancy |
| --- | --- | --- | --- | --- | --- |
| 0 | 93 | $3,499 | 1.43 | 2.46 | $37.62 |
| 1 | 93 | $3,422 | 1.42 | 2.40 | $36.80 |
| 2 | 93 | $3,346 | 1.41 | 2.35 | $35.98 |

## P18 orb_tod — slippage stress (2025)

| Slippage (ticks) | Trades | Net $ | PF | Sharpe | Expectancy |
| --- | --- | --- | --- | --- | --- |
| 0 | 92 | $3,854 | 1.67 | 3.20 | $41.89 |
| 1 | 92 | $3,781 | 1.65 | 3.14 | $41.10 |
| 2 | 92 | $3,707 | 1.64 | 3.07 | $40.30 |

## P18 mes_diverge_orb — slippage stress (2025)

| Slippage (ticks) | Trades | Net $ | PF | Sharpe | Expectancy |
| --- | --- | --- | --- | --- | --- |
| 0 | 28 | $454 | 1.16 | 1.03 | $16.20 |
| 1 | 28 | $432 | 1.15 | 0.98 | $15.41 |
| 2 | 28 | $410 | 1.14 | 0.93 | $14.63 |

