---
type: experiment
status: open
priority: P2
phase: pre-live
family: operations
next-action: Re-export TV trade list for lucid_orb_width_25k.pine; compare vs Python ledger
verdict: null
updated: 2026-07-13
---

# TradingView ↔ Python ledger reconciliation (pre-live)

Operational gate before going live — validates execution, not edge.

## Checklist

1. Blank strategy tab, paste `tradingview/lucid_orb_width_25k.pine` (rev B). MNQ1! · 5m · America/New_York.
2. Verify **zero** trades with exit date ≠ entry date (flat-fix regression check).
3. Export trade list CSV → `data/tradingview_exports/`.
4. Compare trade count / dates / net vs Python ledger (`scripts/compare_tradingview.py`). Expect small fill-model differences (engine is pessimistic: stop-before-target on ambiguous bars, 1-tick slip); flag anything structural (missing days, wrong skips, overnight holds).
5. Confirm TV commission setting = $0.50/side to match verified costs.

## Pre-registered live monitoring rule (decide BEFORE live, hold to it)

- Log every live fill vs Python ledger from day 1 (Journal daily notes).
- **After 30 live trades:** if realized expectancy < −$10/trade or avg slippage > 2 ticks → halt, investigate, do not "trade through it."
- Deviation between signal and action (discretion) = logged in journal, target zero.
