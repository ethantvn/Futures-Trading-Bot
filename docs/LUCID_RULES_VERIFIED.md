# Lucid Flex 25K — Verified Rules (2026-07-12)

Source: user confirmation + lucidtrading.com. Config: `config/lucid_25k.yaml`.

## Eval

| Rule | Value |
| --- | --- |
| Time limit | **None** — take as long as needed |
| Profit target | $1,250 |
| MLL | $1,000 below peak EOD balance; locks at $25,000 start |
| Consistency | 50% largest day / total profit (**eval only**) |
| Min trading days | 2 |
| Max size | 20 MNQ micros (2 minis) — can vary 1–20 day to day |
| Flat by | **4:45 PM ET** (our strategy uses 15:55 — conservative) |
| Overnight | Not allowed on Flex sim |

## Funded / payout

| Rule | Value |
| --- | --- |
| Consistency | **None** on Flex funded |
| Qualifying day | ≥ **$100** daily profit ($25K tier) |
| Days required | **5** qualifying days per payout cycle |
| Min payout | **$500** |
| Max payout | **50%** of profit, cap **$1,000** ($25K) |
| Buffer | **None** on Flex |
| Scaling | $0–$999 profit → 10 micros; $1,000+ → 20 micros (EOD update) |

## Costs

- MNQ micro: **$0.50/side** ($1.00 RT) per Lucid published rate
- Backtest engine updated to match (slippage unchanged @ 1 tick)

## Research impact

1. **No eval time limit** — remove artificial 60-day MC cap. Updated sim:
   - **60d cap (old):** 64.3% pass / 45.7% pass+payout
   - **No limit (correct):** **67.7% pass / 47.9% pass+payout** (10k MC, block, seed 42)
2. **Funded journey MC** updated: no consistency on funded; official payout thresholds.
3. **Phase 19 sizing conclusion unchanged** — still 1 micro optimal.
4. **Commission $0.50/side** — config updated; historical ledgers not re-backtested (small positive bias).

## Still platform-specific

- Tradovate vs Rithmic data fees (not commission)
- Exact auto-flatten timing (~10 sec before 4:45 PM)
