---
type: rules
verified: 2026-07-12
source: user confirmation + lucidtrading.com
---

# Lucid Flex 25K — verified rules

Canonical copy: [[LUCID_RULES_VERIFIED]] + `config/lucid_25k.yaml`. Summary:

## Eval
| Rule | Value |
| --- | --- |
| Time limit | **None** |
| Target / MLL | $1,250 / $1,000 EOD-trailing, locks at $25,000 |
| Consistency | 50% largest-day/profit (**eval only**) |
| Min days / DLL | 2 / none |
| Max size | 20 micros, can vary daily |
| Flat by | 4:45 PM ET (we flat 15:55 — conservative) |

## Funded
| Rule | Value |
| --- | --- |
| Consistency | **None** |
| Qualifying day | ≥ $100 |
| Payout | 5 qualifying days; min $500; max 50% of profit cap $1,000/cycle (~$900 after 90/10) |
| Scaling | <$1,000 profit → 10 micros; ≥$1,000 → 20 |

## Costs
$0.50/side MNQ micro · eval ~$70 (discounted) · reset ~$60 · E[cost to funded] ~$90–100

## Open rule questions
- [[payout-mll-rule-check]] — does payout erode the MLL cushion?
- Exact auto-flatten timing (~10s before 4:45?)
