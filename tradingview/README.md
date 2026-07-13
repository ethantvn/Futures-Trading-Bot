# TradingView — Lucid ORB 25K

Two scripts:

| Script | Strategy | Status |
| --- | --- | --- |
| `lucid_orb_width_25k.pine` | **Phase 9 long-only ORB-W** — width band 0.25–0.70, target 1.0R, Skip Monday ON, **Long only ON** | **Recommended** (WF OOS pass ~64%; see `docs/PHASE_9_REPORT.md`) |
| `lucid_orb_25k.pine` | Phase 5/6 plain ORB — range 30m, target 1.5R, expire 120m, Skip Monday ON | Superseded baseline (kept for reference) |

The width filter stands aside when the 09:30–10:00 range is under 25% of the
14-day EWM of daily RTH ranges (noise breakout) or over 70% (oversized $ risk
vs the $1,000 MLL). An orange tag explains every skipped day. The first ~14
sessions after adding the script have no vol reference and are skipped —
normal warmup.

> **Phase 9 rev B flat fix (2026-07-08):** Phase 8 still left ~30% overnight
> holds because `strategy.exit("XL")` was re-armed every bar after 15:55.
> Rev B: bracket orders only before 15:55; at 15:55 cancel XL/XS and
> `strategy.close("Flat 15:55")`. Removed the midnight `newNyDay` fallback.
> Re-add the script and confirm **zero** trades where exit date ≠ entry date.

## Setup

1. Open **Pine Editor** on TradingView → paste contents of `lucid_orb_width_25k.pine` (or the baseline script) → **Add to chart**
2. Chart settings (required):
   - **Symbol:** `MNQ1!` (CME MNQ continuous)
   - **Timeframe:** **5 minutes** (matches backtest signal bars)
   - **Chart timezone:** America/New_York
   - **Session template / extended hours:** either works — all session logic
     is ET wall-clock internal. On RTH-only charts the last bar is
     15:55–16:00; the flat order fills at that bar's open (15:55). On ETH
     charts behavior is identical.
3. Strategy settings → **Properties** → confirm **Order size = 1** contract (1 micro)
4. After adding: check the trade list — every trade must show **entry and
   exit on the same date**, with "Flat 15:55" comments on end-of-day exits.

## What you'll see on chart

| Visual | Meaning |
| --- | --- |
| Light blue shaded box | Opening range (only before entry) |
| **Green ↑ arrow** | Long entry fill |
| **Red ↓ arrow** | Short entry fill |
| **Red horizontal line** | Stop loss (from entry until exit) |
| **Green horizontal line** | Take profit (from entry until exit) |
| Orange **SKIP MON** tag | Monday — no trade (if Skip Monday ON) |
| Top-right table | Live SL / TP / 1R / status |

## Rules (matches Python backtest)

- **Range:** High/low of first 30 minutes RTH (09:30–10:00 ET)
- **Skip Monday:** ON by default (research: ~52% vs ~44% Lucid pass rate on WF OOS)
- **Long entry:** Stop at OR high + $0.25
- **Short entry:** Stop at OR low − $0.25 (OCO — one cancels other)
- **Long SL:** OR low − $0.25 | **Long TP:** entry + 1.5 × (OR high − OR low)
- **Short SL:** OR high + $0.25 | **Short TP:** entry − 1.5 × (OR high − OR low)
- **Expire:** Unfilled orders cancelled 120 min after range (12:00 ET)
- **No entries after:** 15:30 ET
- **Force flat:** 15:55 ET
- **Max:** 1 trade per day

## Important

TradingView's strategy tester uses its own fill model (bar OHLC). Results will **not** match our Python backtest exactly. Use this script for **levels, alerts, and discipline** — not to re-validate the edge.

For Lucid eval: trade **1 micro**, watch the 50% consistency rule manually (not coded here).
