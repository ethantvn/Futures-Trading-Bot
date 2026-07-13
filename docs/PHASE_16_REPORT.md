# Phase 16 Report — Structure / Levels / Profile / MES Divergence (MNQ)

Date: 2026-07-12. **Updated same day after overnight-level lookahead fix.**

## TL;DR (corrected)

**Do not trade overnight fade as a Lucid primary.** An earlier draft of this
report promoted it after a **lookahead bug** in `overnight_levels()`: same-day
afternoon ETH (16:00–17:00) was folded into “overnight” high/low, so morning
signals could see post-RTH extremes that were not knowable at 09:30.

After restricting overnight to **18:00–09:30 ET only** and re-running walk-forward:

| Strategy | WF Pass 25K | Holdout Pass | Verdict |
| --- | --- | --- | --- |
| overnight_fade (causal) | **~14%** | ~53% | **REJECT** |
| ORB-W long-only + skipMon | **64.3%** | 58.8% | **stays primary** |
| structure_gated_orb / MES / POC / rounds | ≤66% sparse or weak | mixed | no promote |

Your TradingView export (~+$1.7k / ~42% WR over the past year) was **closer to
the causal truth** than the inflated Python ledger. That mismatch is what
triggered the audit.

## What went wrong

```text
Bug: overnight_levels() = max/min of ALL session=="eth" bars on trading_date
     → includes 16:00–17:00 afternoon Globex on the same day
Fix: eth bars with minute ∈ [18:00, 24:00) ∪ [00:00, 09:30) only; lock at RTH
```

~355/517 sample days (2024–2025) had different ON high/low under the fix.

## Causal overnight_fade (post-fix)

Frozen old params (1.75 ATR / 1.5R) on 2019–2025: **−$5.6k**, WR 35%, MC pass
**12.7%**. Re-selected WF params (`stop_atr=1.25`, `target_r=1.0`):

| Ledger | Trades | Net | Pass 25K | Pass+payout |
| --- | --- | --- | --- | --- |
| WF OOS | 1151 | +$512 | **13.9%** | 5.0% |
| 2026 holdout | 121 | +$1.2k | ~53% | ~36% |
| TV-like window Jul25–Jul26 | 238 | +$1.9k | — | — |

Survives as a mild research curiosity on holdout only; **fails the picky bar**
vs ORB-W (need ≥~50% WF pass with fold stability and durable edge).

## Other Phase 16 families (unchanged qualitative ranking)

| Family | Idea | Verdict |
| --- | --- | --- |
| structure_gated_orb | ORB-W only in up/range | Modest; too sparse to replace |
| structure_gated_vwap | VWAP × regime | Reject |
| prior_day_break/fade | PDH/PDL | Reject |
| poc_reversion/breakout | Session POC / VA | Reject |
| mes_agree / diverge ORB | MES OR-mid gate | Agree fails holdout |
| round_fade / round_break | Round magnets | Reject |
| overnight_break | Break ON H/L | Reject |

## Live recommendation (restored)

**Account 1:** ORB-W long-only + skip Monday — `tradingview/lucid_orb_width_25k.pine`  
(~64% pass / ~46% pass+payout on WF)

**Account 2:** NR7 ORB + skip Monday (prior research), or leave empty.

Overnight fade Pine **rev C** (`tradingview/lucid_overnight_fade_25k.pine`) is
kept as a **causal reference implementation only** — not a promoted eval
strategy.

## Pine / TV checklist (rev C)

1. New blank strategy tab; paste entire file (one `strategy()` only)
2. MNQ1! · 5m · America/New_York · **ETH / extended** session
3. Expect results in the ballpark of causal Python (~flat to modest), **not**
   the old 96% figures
4. Re-export CSV and compare trade count / net to
   `trades_phase16_overnight_fade_wf_oos.parquet` if auditing

## Artifacts

- Causal fix: `overnight_levels()` in `src/strategies/indicators.py`
- Pine rev C: `tradingview/lucid_overnight_fade_25k.pine`
- Params after re-WF: `data/processed/phase16_params_overnight_fade.yaml`
