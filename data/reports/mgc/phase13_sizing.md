# MGC Sizing Check — 1 micro contract vs Lucid MLL (25K & 50K)

- Point value: **$10/pt** ($1.00/tick @ 0.10 tick)

| Tier | MLL | Risk band (15–25%) | Stop pts @ $10/pt |
| --- | --- | --- | --- |
| lucid_25k | $1,000 | $150–$250 | 15–25 pts |
| lucid_50k | $2,000 | $300–$500 | 30–50 pts |

## ATR(14) $ risk at 1 MGC

| Timeframe | Med ATR pts | Med ATR $ | 1.5×ATR $ | 2×ATR $ |
| --- | --- | --- | --- | --- |
| 5m | 1.38 | $14 | $21 | $28 |
| 15m | 2.48 | $25 | $37 | $50 |
| 30m | 3.68 | $37 | $55 | $74 |

## Daily RTH range at 1 MGC ($/day)

- Median: **$193** (19.3 pts) — GC full-size was ~$1,930
- P95: **$780** (78.0 pts) — GC full-size was ~$7,810
- Max: **$4,456** (445.6 pts)

### By year (regime shift matters)

| Year | Median $ | P95 $ |
| --- | --- | --- |
| 2021 | $129 | $276 |
| 2022 | $145 | $309 |
| 2023 | $141 | $305 |
| 2024 | $191 | $385 |
| 2025 | $301 | $787 |
| 2026 | $646 | $1,655 |

## Verdict

1 MGC fits both tiers: median daily RTH range $193 is well inside both MLLs (vs GC full-size where P95 $7,800 broke the $2,000 MLL). Per-trade caps: use ~15–25 pts on 25K, ~30–50 pts on 50K. Caveat: 2025–2026 volatility is 3–4× the 2021–2023 regime (2026 median daily range $646); vol-normalized filters are preferred over absolute point thresholds, and P95 2026 days approach the 25K MLL — capped stops + 1 trade/day discipline required.
