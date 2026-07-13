# GC Sizing Check — 1 full-size contract vs Lucid 50K MLL

- MLL: $2,000; target risk band: 15–25% = **$300–$500** per trade
- Point value: **$100.0/pt** ($10/tick @ 0.10 tick)

| Timeframe | Med ATR(14) pts | Med ATR $ | 1.5×ATR $ | 2×ATR $ | Fits budget? |
| --- | --- | --- | --- | --- | --- |
| 5m | 1.40 | $140 | $209 | $279 | marginal/tight |
| 15m | 2.49 | $249 | $374 | $499 | yes (1.5×) |
| 30m | 3.69 | $369 | $553 | $738 | marginal/tight |

## Daily RTH range (1 contract, $/day)

- Median: **$1,930** (19.3 pts)
- P95: **$7,810** (78.1 pts)
- Max: **$44,190** (441.9 pts)

## Verdict

Per-trade caps (3–5 pts) can fit the $300–500 band, but **P95 daily RTH range ($7,810) exceeds the $2,000 MLL**. Strategies need 1 trade/day discipline and capped stops; blow risk remains elevated vs MNQ.
