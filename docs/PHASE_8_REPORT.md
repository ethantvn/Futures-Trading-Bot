# Phase 8 Report — Tail Risk, Hold Time, and TV/Pine Alignment

Date: 2026-07-06. Follows Phase 7 (`docs/PHASE_7_REPORT.md`, winner:
width-filtered ORB + Skip Monday, WF OOS pass ~61.8% @ 1 micro).

## TL;DR

**The overnight/weekend holds were a TradingView script bug, not strategy
behavior — fixed in Pine. No exit overlay improves the Python-validated
system: keep ORB-W + Skip Monday exactly as recommended in Phase 7.**

1. **TV bug (fixed):** the 15:55 flat order was submitted at the last bar's
   *close* and filled at the **next session's open**, while the stop/target
   stayed working overnight. In the user's 2026-07-06 export, **101 of 540
   trades (18.7%) held overnight, 42 across weekends** — including the
   June 12 → 15 "+$2,260" trade and a −$1,104 weekend gap loss (May 14 → 18).
   Both Pine scripts now submit the flat on the bar **closing** at 15:55, so
   it fills **at 15:55 every day, Fridays included**, with an early-close
   fallback and a visible `FLAT 15:55` label.
2. **Python ledgers were never affected:** all 16 ledgers (16k+ trades) show
   **zero** multi-day holds and zero exits after 16:00 ET. Phase 7 validation
   stands unchanged. `friday_flat` is therefore a **no-op** in the engine.
3. **Time-capping holds destroys the edge** (monotonically): max_hold
   60/90/120/180 min → pass rate 27.7% / 45.7% / 49.6% / 54.3% (+skipMon)
   vs **61.8% baseline**. Confirms Phase 7's time-stop rejection from an
   entry-anchored angle: the afternoon drift *is* the profit engine.
4. **Dollar stop-caps are nearly free but strictly negative:** capping the
   stop at $500 (250 pts) costs 1.3 pass points (60.5%) to trim the worst
   single day −$593 → −$503 — and the **worst 20-day window is unchanged
   (−$2,319)**, so the cap does not reduce the streak risk that actually
   breaches the MLL. Not recommended (quantified below if you want it anyway).

---

## A. TV vs Python hold behavior — diagnosis and fix

### Root cause

Pine strategies process orders generated on bar *t* at bar *t+1*'s open. The
old flat block fired on the bar **opening** at 15:55; its `close_all()` was
processed at that bar's close (16:00), so the market order filled at the next
bar — **18:00 the same evening, or the next morning on RTH charts (Monday
after Fridays)**. Until that fill, `strategy.exit` stop/limit orders remained
live: the export shows exits at 18:00, 21:15, 22:25, 00:00, and next-day
10:05 (27 trades — overnight stop/target hits, including gap-throughs).

### Evidence from `ORB-W_25K_...csv` (copied to `data/tradingview_exports/`)

- 540 trades 2023-01 → 2026-07: **101 multi-day holds (18.7%), 42 over
  weekends**, net +$2,145 — luck, not edge (uncompensated gap risk).
- Worst artifact: #521 long May 14 → 18, **−$1,104** — larger than any loss
  the real strategy can take (worst Python day: −$593).
- Side-by-side, June 2026 (Python engine vs TV export):

| Day | Python (ground truth) | TV (buggy script) |
| --- | --- | --- |
| Jun 9 | +$425 target | **+$425** — identical |
| Jun 12 | **+$307**, flat 15:55 | held to **Sun Jun 14 18:00**, +$1,192 (another export of the same trade: Mon 09:30, +$2,260 — exit depends on session template!) |
| Jun 15 | +$82 eod | **no trade** — still stuck in the Jun 12 position |
| Jun 16 | +$274 target | **+$274** — identical |
| Jun 17 | −$393 stop | **−$393** — identical |
| Jun 18 | +$264, flat 15:55 | held to **Sun Jun 21 18:00**, **−$72** — gap flipped a winner into a loser |

Where both exited intraday, P&L matches **to the dollar**; every divergence
is the flat bug (multi-day gambles, blocked next-day entries). Overnight
exposure is symmetric gambling: Jun 12 got lucky, Jun 18 and May 14 paid.

### Fix (both `lucid_orb_width_25k.pine` and `lucid_orb_25k.pine`)

- Flat condition now keys on **bar-close time** (`nyModClose >= 15:55`),
  level-triggered: the order is submitted on the 15:50–15:55 bar and fills at
  the 15:55 bar open — same instant as the Python engine. Data gaps can't
  skip it, and a `newNyDay` fallback flattens after early-close holidays.
- Pending-order cancels moved to bar-close time too (pendings can no longer
  fill during the expiry bar).
- Visible **FLAT 15:55** label + alert; "Flat 15:55" comment in the trade list.

### Required chart settings (also in `tradingview/README.md`)

MNQ1! · **5 minutes** · chart timezone **America/New_York** · order size 1.
Session template (ETH or RTH-only) no longer matters — all logic is ET
wall-clock internal. **After re-adding the script, verify the trade list has
zero rows whose exit date ≠ entry date.**

## B. Exit overlays (Python engine, same 9 WF folds as Phase 7)

Each overlay re-ran the **full** orb_width grid + walk-forward with the
overlay fixed, so band selection stayed procedure-identical (all overlays
still picked band 0.25–0.70, target 1.0R). Full table:
`data/reports/phase8_leaderboard.md`.

| Overlay (+skipMon) | Pass@1 | Net $ | UPI | MaxDD | Worst day | Worst 20d |
| --- | --- | --- | --- | --- | --- | --- |
| **BASELINE (none)** | **61.8%** | $17,607 | **10.7** | −$2,533 | −$593 | −$2,319 |
| stopcap $500 (250 pts) | 60.5% | $16,124 | 9.8 | −$2,533 | −$503 | −$2,319 |
| stopcap $600 (300 pts) | 59.9% | $15,934 | 9.4 | −$2,533 | −$603 | −$2,319 |
| stopcap $400 (200 pts) | 58.8% | $15,193 | 8.8 | −$2,719 | −$403 | −$2,319 |
| max_hold 180m | 54.3% | $11,953 | 3.3 | −$3,936 | −$593 | −$3,382 |
| max_hold 120m | 49.6% | $10,143 | 3.8 | −$2,630 | −$535 | −$2,069 |
| max_hold 90m | 45.7% | $8,570 | 2.6 | −$3,846 | −$474 | −$2,961 |
| max_hold 60m | 27.7% | $3,596 | 0.7 | −$4,417 | −$660 | −$2,786 |

- **max_hold:** pass rate degrades monotonically as the cap tightens; even
  the loosest (180m) loses 7.5 points and *raises* max DD to −$3,936. The
  P&L that time-caps delete is exactly the target/EOD drift that pays for
  the stops. "Stopping trades at a certain time" **increases** eval risk.
- **Stop caps:** bind only on rare wide days (p95 daily loss unchanged at
  −$301), trim the worst single day, but convert some full-range recoveries
  into premature stopouts (net −$1,483 at $500 cap) and leave the
  MLL-relevant streak risk (worst 20d, max DD) untouched. If the user wants
  a hard "never lose more than $X on one trade" line for psychological
  comfort, **$500 (250 pts) costs ~1.3 pass points** — quantified, optional,
  and OFF by default (`max_risk_points` param in `orb_filtered`).
- **friday_flat:** no-op in Python (engine force-flats 15:55 daily —
  asserted in `run_phase8.py` and verified across all 16 ledgers). It was
  purely the TV bug.

## C. Tail / outlier profile of the current winner (WF OOS, live config)

- **Lottery dependence is real but inherent to breakout design:** the top 5%
  of winning days (33 days ≥ $371) carry ~90% of net P&L; removing them
  drops the MC pass rate 61.8% → 36.2%. The exit ledger shows why this is
  structural: targets +$49,004 (178 trades), EOD drift +$16,357, stops
  −$48,150. The stops *buy* the tail days; strategies without tail
  dependence (mean reversion) were all rejected on negative expectancy in
  Phases 3–5. Practical implication: **do not stop an eval attempt early
  after a string of small days — the plan's math requires being present for
  the outlier winners.**
- **Single-day blow-up risk is low:** worst day in 4.5 years = −$593 (59% of
  the $1,000 MLL); **zero** single-day breaches from a fresh $25k start in
  659 active days. Breaches require streaks: worst 2-day run −$869 (87%),
  worst 5-day run −$1,887 (189%) — this streak risk is what the 38.2% MC
  fail rate already prices in via 5-day block bootstrap.
- The worst-10-days table is dominated by Mar–Apr 2025 (tariff volatility):
  7 of 10. The width band already excludes the most extreme days; the
  residual cluster is regime risk, not a fixable exit problem.

## D. Recommendation

1. **Keep ORB-W + Skip Monday @ 1 micro exactly as configured in Phase 7**
   (band 0.25–0.70, target 1.0R, expire 120m, flat 15:55). No overlay earns
   its cost; every hold-time cap is harmful.
2. **The fix was TV-only.** Re-add the updated `lucid_orb_width_25k.pine`,
   confirm zero multi-day trades in the tester list, and treat TV as a
   levels/alerts tool — the Python ledgers remain the performance reference.
3. Optional, not default: `max_risk_points: 250` ($500/trade hard cap) if a
   single −$600 day would shake execution discipline — costs ~1.3 pass
   points and does not reduce drawdown/streak risk.
4. 2026 holdout was **not** touched in Phase 8 (already consumed by Phases 5
   and 7).

## Artifacts

| File | Content |
| --- | --- |
| `data/reports/phase8_leaderboard.md` | Overlay ranking + tail analysis tables |
| `data/reports/phase8_walk_forward.md` | Fold tables for all 7 overlays |
| `data/reports/phase8_metrics.json` | Full metric dump |
| `data/processed/trades_phase8_*_wf_oos.parquet` | Overlay OOS ledgers |
| `data/tradingview_exports/ORB-W_25K_*.csv` | User's TV exports (bug evidence) |
| `tradingview/lucid_orb_width_25k.pine`, `lucid_orb_25k.pine` | Fixed scripts (rev A) |
| `src/strategies/orb_filtered.py` (`max_risk_points`), `src/evaluation/consistency.py` (p95 loss, worst-20d) | New code (+6 tests; suite 116 green) |
| `config/phase8.yaml`, `scripts/run_phase8.py` | Reproducible pipeline |
