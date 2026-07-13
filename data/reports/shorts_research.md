# Shorts research — ORB-W under verified Lucid 25K ($0.50/side)

Question: can we add shorts (raw or filtered) to raise trade density and speed pass/payout without hurting Lucid survival?

Core params: `{'range_minutes': 30, 'target_r': 1.0, 'expire_minutes': 120, 'min_width_ratio': 0.25, 'max_width_ratio': 0.7}` + skip Monday (post-hoc). Commission $0.50/side.

## Leaderboard (WF OOS, no eval time limit)

| Candidate | Trades | Pass% | Pass+payout% | Med d | Net $ | Sharpe | MaxDD | Long n/net | Short n/net | Short exp |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| long_only | 473 | 69.8% | 51.8% | 26 | $12,501 | 2.17 | $-2,594 | 473/$12,501 | 0/$0 | — |
| long_+_short_wide | 595 | 69.7% | 51.7% | 23 | $16,945 | 2.21 | $-4,377 | 450/$12,766 | 145/$4,179 | $28.8 |
| long_+_short_tight | 597 | 66.5% | 47.8% | 29 | $13,337 | 1.88 | $-2,862 | 431/$11,056 | 166/$2,280 | $13.7 |
| long_short_same | 759 | 65.8% | 47.4% | 26 | $17,958 | 1.87 | $-4,700 | 400/$11,314 | 359/$6,643 | $18.5 |
| long_+_short_midwidth | 618 | 63.9% | 42.2% | 27 | $12,851 | 1.64 | $-3,856 | 435/$11,582 | 183/$1,270 | $6.9 |
| long_+_short_tue_thu | 685 | 63.6% | 44.9% | 28 | $14,868 | 1.74 | $-3,992 | 418/$11,525 | 267/$3,342 | $12.5 |
| short_only | 436 | 48.6% | 27.2% | 23 | $5,910 | 1.05 | $-2,532 | 0/$0 | 436/$5,910 | $13.6 |
| short_only_midwidth | 226 | 37.6% | 15.6% | 26 | $946 | 0.31 | $-3,182 | 0/$0 | 226/$946 | $4.2 |

## Side diagnosis (any short trades in WF OOS)

- Short expectancy across short-enabled variants: **$14.04/trade** (control long expectancy $26.43/trade).
- `long_short_same`: 359 shorts, net $6,643, WR 54.6%, exp $18.50
- `short_only`: 436 shorts, net $5,910, WR 53.7%, exp $13.56
- `long_+_short_midwidth`: 183 shorts, net $1,270, WR 53.0%, exp $6.94
- `long_+_short_tight`: 166 shorts, net $2,280, WR 54.2%, exp $13.74
- `long_+_short_tue_thu`: 267 shorts, net $3,342, WR 52.8%, exp $12.52
- `long_+_short_wide`: 145 shorts, net $4,179, WR 56.6%, exp $28.82
- `short_only_midwidth`: 226 shorts, net $946, WR 51.8%, exp $4.18

## 2026 holdout (spot check)

| Candidate | Trades | Net $ | Shorts n/net |
| --- | --- | --- | --- |
| long_only | 52 | $2,836 | 0/$0 |
| long_+_short_wide | 67 | $2,028 | 19/$-313 |
| long_+_short_tight | 59 | $2,516 | 11/$54 |
| long_short_same | 79 | $2,192 | 35/$225 |
| long_+_short_midwidth | 72 | $2,678 | 24/$506 |
| long_+_short_tue_thu | 73 | $1,662 | 28/$-589 |
| short_only | 41 | $414 | 41/$414 |
| short_only_midwidth | 29 | $466 | 29/$466 |

## Verdict

**Keep long-only.** Best overall is `long_only` (pass 69.8% vs control 69.8%). Shorts add density but do not improve Lucid pass / pass+payout under verified rules. Do **not** flip `longOnly` in Pine.
Short edge remains weak (example `short_only_midwidth` exp $4.18/trade vs long $26.43).

Control: `long_only` pass=69.8% pap=51.8% med_days=26.
