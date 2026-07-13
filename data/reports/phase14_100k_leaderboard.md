# Phase 14 — Lucid Flex 100K Leaderboard (frozen ledgers, 10k MC)

Target/MLL ratio: 25K = 1.25x, 50K = 1.50x, **100K = 2.00x** — the 100K tier needs twice the edge-per-drawdown-dollar of the 25K.

Fees: discounted eval fee + reset fee per tier (25K $70/$60, 50K $98/$95, 100K $157.50/$140 — VERIFY).

## Part A — MNQ ORB-W long-only + skipMon (Phase 9 frozen WF OOS ledger)

| Ledger | Account | Micros | Pass % | Fail % | Timeout % | Med d | ≤10d | ≤15d | ≤20d | ≤40d | E[resets] | E[cost] |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| MNQ ORB-W | lucid_25k | 1 | **64.3%** | 31.3% | 4.4% | 23 | 7% | 16% | 27% | 54% | 0.6 | $103 |
| MNQ ORB-W | lucid_50k | 1 | **25.6%** | 6.2% | 68.2% | 45 | 0% | 0% | 1% | 10% | 2.9 | $374 |
| MNQ ORB-W | lucid_50k | 2 | **59.4%** | 33.1% | 7.5% | 28 | 3% | 9% | 17% | 46% | 0.7 | $163 |
| MNQ ORB-W | lucid_50k | 3 | **56.4%** | 43.1% | 0.5% | 16 | 14% | 27% | 36% | 54% | 0.8 | $171 |
| MNQ ORB-W | lucid_50k | 4 | **51.6%** | 48.2% | 0.1% | 11 | 24% | 37% | 44% | 51% | 0.9 | $187 |
| MNQ ORB-W | lucid_100k | 1 | **0.5%** | 0.7% | 98.9% | 53 | 0% | 0% | 0% | 0% | 203.1 | $28,589 |
| MNQ ORB-W | lucid_100k | 2 | **25.4%** | 16.0% | 58.5% | 45 | 0% | 0% | 1% | 10% | 2.9 | $568 |
| MNQ ORB-W | lucid_100k | 3 | **47.7%** | 34.5% | 17.8% | 35 | 1% | 3% | 7% | 31% | 1.1 | $311 |
| MNQ ORB-W | lucid_100k | 4 | **52.5%** | 43.5% | 4.0% | 26 | 3% | 9% | 17% | 43% | 0.9 | $284 |
| MNQ ORB-W | lucid_100k | 5 | **49.4%** | 49.7% | 0.8% | 19 | 8% | 18% | 27% | 46% | 1.0 | $301 |
| MNQ ORB-W | lucid_100k | 6 | **47.7%** | 52.0% | 0.3% | 15 | 14% | 26% | 34% | 46% | 1.1 | $311 |
| MNQ ORB-W | lucid_100k | 8 | **42.7%** | 57.2% | 0.1% | 10 | 23% | 33% | 38% | 42% | 1.3 | $345 |
| MNQ ORB-W | lucid_100k | 10 | **39.3%** | 60.6% | 0.1% | 8 | 27% | 35% | 37% | 39% | 1.5 | $374 |

## Journey MC — pass + first payout (funded rules mirrored from 25K; VERIFY)

| Account | Micros | Pass % | Pass+Payout % |
| --- | --- | --- | --- |
| lucid_25k | 1 | 64.4% | 45.6% |
| lucid_100k | 4 | 51.9% | 33.5% |
| lucid_50k | 2 | 59.1% | 41.9% |

### 2026 holdout (frozen params, single replay through tier MC)

| Ledger | Account | Micros | Pass % | Fail % | Timeout % | Med d | ≤10d | ≤15d | ≤20d | ≤40d | E[resets] | E[cost] |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| MNQ ORB-W holdout26 | lucid_25k | 1 | **58.8%** | 41.2% | 0.0% | 13 | 21% | 38% | 48% | 58% | 0.7 | $112 |
| MNQ ORB-W holdout26 | lucid_50k | 2 | **55.1%** | 44.8% | 0.1% | 16 | 12% | 27% | 39% | 54% | 0.8 | $176 |
| MNQ ORB-W holdout26 | lucid_100k | 4 | **48.0%** | 52.0% | 0.0% | 15 | 12% | 27% | 37% | 47% | 1.1 | $309 |

## Part B — Gold under the $3,000 100K MLL

### B1: full-size GC sizing check

- Median daily RTH range: **$1,930**; P95: **$7,810**; max: $44,190 (at $100/pt, 1 GC)
- **25% of all days** have a full range above the $3,000 100K MLL — one adverse open-to-close move can still end the eval
- Verdict: structurally unsound at 1 GC even on 100K; deep grids not reopened

### B2: frozen gold ledgers on 100K

| Ledger | Account | Micros | Pass % | Fail % | Timeout % | Med d | ≤10d | ≤15d | ≤20d | ≤40d | E[resets] | E[cost] |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| GC11 macro_nfp_cpi | lucid_100k | 1 | **59.7%** | 33.4% | 6.9% | 28 | 3% | 9% | 18% | 47% | 0.7 | $252 |
| GC12 macro_nfp | lucid_100k | 1 | **55.4%** | 42.9% | 1.8% | 23 | 2% | 12% | 24% | 50% | 0.8 | $270 |
| GC12 comex_orb_deep | lucid_100k | 1 | **29.7%** | 66.8% | 3.5% | 23 | 4% | 9% | 13% | 25% | 2.4 | $489 |
| MGC13 comex_orb_deep | lucid_100k | 2 | **0.5%** | 2.4% | 97.1% | 54 | 0% | 0% | 0% | 0% | 195.1 | $27,468 |
| MGC13 comex_orb_deep | lucid_100k | 3 | **7.9%** | 14.8% | 77.3% | 49 | 0% | 0% | 0% | 2% | 11.7 | $1,794 |
| MGC13 comex_orb_deep | lucid_100k | 5 | **30.9%** | 41.4% | 27.6% | 37 | 0% | 2% | 4% | 18% | 2.2 | $470 |
| MGC13 comex_orb_deep | lucid_100k | 8 | **40.5%** | 57.1% | 2.4% | 22 | 6% | 12% | 19% | 35% | 1.5 | $364 |
| MGC13 comex_orb_deep | lucid_100k | 10 | **39.8%** | 59.8% | 0.3% | 15 | 11% | 20% | 27% | 38% | 1.5 | $369 |

GC macro wall-clock reality (sparse-event families):

- GC11 macro_nfp_cpi: 2.7 trades/mo — 6-month wall-clock (~16 active days): pass 11.5%, timeout 74.6%
- GC12 macro_nfp: 1.0 trades/mo — 6-month wall-clock (~6 active days): pass 0.0%, timeout 92.6%
- GC12 comex_orb_deep: 9.0 trades/mo — 6-month wall-clock (~54 active days): pass 27.7%, timeout 5.0%

### GC 2026 holdout ledgers on 100K (frozen, single replay)

| Ledger | Account | Micros | Pass % | Fail % | Timeout % | Med d | ≤10d | ≤15d | ≤20d | ≤40d | E[resets] | E[cost] |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| GC11 macro_nfp_cpi holdout26 | lucid_100k | 1 | **12.0%** | 87.9% | 0.0% | 12 | 4% | 8% | 10% | 12% | 7.3 | $1,179 |
| GC12 macro_nfp holdout26 | lucid_100k | 1 | **0.0%** | 100.0% | 0.0% | — | 0% | 0% | 0% | 0% | — | — |

MGC comex_orb_deep OOS frequency: 5.9 trades/month — wall-clock reality at best contract count:

- 2-month wall-clock (~12 active days) @ 8 MGC: pass 8.5%, fail 24.7%, timeout 66.8%
- 6-month wall-clock (~35 active days) @ 8 MGC: pass 32.3%, fail 52.9%, timeout 14.8%

### MGC 2026 holdout @ best k (frozen)

| Ledger | Account | Micros | Pass % | Fail % | Timeout % | Med d | ≤10d | ≤15d | ≤20d | ≤40d | E[resets] | E[cost] |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| MGC13 c_o_d holdout26 | lucid_100k | 8 | **0.0%** | 100.0% | 0.0% | — | 0% | 0% | 0% | 0% | — | — |

