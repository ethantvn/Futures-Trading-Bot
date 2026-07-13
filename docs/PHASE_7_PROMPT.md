# Phase 7 Prompt — Consistency-Focused Strategy Research

Copy everything below the line into Claude Code (or a new agent session) in the repo root:
`/Users/ethannguyen/Desktop/MNQ Strategy`

---

## Your task

Continue the MNQ Lucid Flex evaluation research project. **Phases 1–6 are complete.** Your job is **Phase 7: find and validate a strategy (or ORB variant) with a smoother, more consistent equity curve** — especially strong recent performance — even if total 4-year profit is lower than current ORB.

Read these files first (in order):
1. `docs/PROJECT_STATUS.md`
2. `docs/PHASE_1_PLAN.md`
3. `data/reports/final_recommendation.md`
4. `data/reports/validation_summary.md`
5. `data/reports/validation_walk_forward.md`
6. `config/lucid_25k.yaml`, `config/strategies.yaml`, `config/data.yaml`

Then execute Phase 7 as described below. **Do not re-tune ORB on the 2026 holdout** (already used once). Extend the codebase; keep all existing tests passing.

---

## Project context (what already exists)

**Goal:** Maximize probability of passing a **Lucid Flex 25K** eval ($1,250 target, $1,000 EOD trailing MLL, no DLL, 50% consistency, 2 min days, 1 micro recommended).

**Stack:** Python 3.12, Polars, pytest, custom event-driven backtester (`src/backtest/`), Lucid rule engine + Monte Carlo (`src/evaluation/`), walk-forward validation (`src/validation/`).

**Data:** Databento MNQ 1m bars 2019-05-29 → 2026-06-28 in `data/raw/`. Processed continuous series in `data/processed/` (1m, 3m, 5m, 15m, 30m). TradingView alignment verified 99.9%+.

**Engine rules (non-negotiable):**
- Signals on bar *t*, fills on *t+1* (5m signals, 1m fills)
- Pessimistic fills (stop before target on ambiguous 1m bars)
- Flat by 15:55 ET, no entries after 15:30 ET
- Costs: ~$0.99/side/micro + 1 tick slippage (placeholder)

---

## What we already tested (Phase 3–6)

| Strategy | Verdict | WF OOS net | 2026 holdout |
|---|---|---|---|
| **Opening range breakout (ORB)** | ✅ **Only viable candidate** | +$18,377, Sharpe 1.16, PF 1.20 | +$948, PF 1.06 |
| EMA trend | ❌ Reject | +$1,391 (flat) | −$2,568 |
| VWAP pullback | ❌ Reject | negative | — |
| Prev day H/L breakout | ❌ Reject | negative | — |
| Bollinger mean reversion | ❌ Reject | negative | — |

**Validated ORB params:** `range_minutes=30`, `target_r=1.5`, `expire_minutes=120`, 5m signal, 1 micro.

**ORB + Skip Monday (Phase 6b):** On Python WF OOS ledger, skipping Mondays improved Lucid pass rate ~44% → ~52% and net P&L; held on 2026 holdout for Monday skip alone. Implemented in `tradingview/lucid_orb_25k.pine` (Skip Monday default ON). Wednesday skip failed holdout — do not use.

**Lucid MC (ORB conservative, WF OOS):** ~44% pass @1 micro, median ~22 days, E[cost] ~$146.

---

## Why Phase 7 (user request)

The user is concerned about **ORB’s equity curve shape**: long flat periods, spikes, and **negative P&L over the last ~90 days** in TradingView (and weak 2025 in backtests: roughly −$2k to −$2.8k depending on export window).

They want research into alternatives (or ORB modifications) that prioritize:

1. **Consistent upward equity curve** (smoothness, low drawdown variance) over maximum total P&L
2. **Strong recency:** may accept lower 4-year return if **last 3 years** and especially **last 1 year** are consistently profitable
3. **Lower eval risk:** fewer deep drawdowns / losing streaks → OK if eval takes **longer** (more calendar days) but **higher pass probability**
4. **Still must pass Lucid 25K rules** in Monte Carlo — primary metric is **pass rate**, not raw backtest profit

**Explicitly NOT asking for:** curve-fitting to last 90 days only, or abandoning walk-forward / holdout discipline.

---

## Phase 7 research methodology

### A. Define “consistency score” (implement in `src/backtest/metrics.py` or new `src/evaluation/consistency.py`)

Rank strategies on a composite, e.g.:

- **Lucid 25K pass rate** (10k MC, block bootstrap) — **primary**
- **Equity curve smoothness:** daily returns Sharpe/Sortino, max drawdown, max consecutive losing *days*, Ulcer index, or R² of cumulative P&L vs time
- **Recency windows** (report separately, do not optimize on all simultaneously):
  - Last 90 trading days
  - Last 252 trading days (~1 year)
  - 2023–2025 (3 years)
  - Full WF OOS 2021–2025
- **Regime stability:** rolling 6-month P&L — penalize strategies that only worked in one era

**Selection rule:** A candidate must beat ORB baseline on **pass rate OR smoothness** without failing holdout (2026 gets **one** final comparison at the end, same as Phase 5 — do not iterate on 2026).

### B. Strategy families to research (start simple, 2–4 params each)

Existing infrastructure supports new modules in `src/strategies/`. Consider **interpretable** families biased toward lower variance:

1. **ORB variants:** lower target (1.0R), tighter range (15–20m), skip Mon (already), skip high-vol days (ATR filter), limit entry instead of stop entry
2. **Session mean reversion:** fade extended moves back to VWAP / session mid in **low ADX** regimes only (opposite hypothesis to ORB; may be smoother in chop)
3. **Afternoon trend / power hour:** single trade 14:00–15:30 with trend filter (different time window than ORB — diversifies)
4. **NR7 / inside day breakout:** trade only when prior day range is narrowest in 7 days (compression → expansion, fewer signals)
5. **Dual-threshold ORB:** only trade if OR width is between min/max (filter noise and huge ranges)
6. **Time-stop ORB:** same ORB but exit at 12:00 if not at target (reduce EOD drift losses visible in ORB exit_reasons: many `eod` exits)

Also re-score **existing rejected strategies** with the new consistency metrics — they may fail pass rate but document why.

### C. Validation pipeline (reuse existing scripts)

For each candidate:
1. Baseline backtest 2019–2025 (`scripts/run_backtest.py` pattern)
2. Walk-forward param grid (`scripts/run_validation.py` pattern, smaller grids)
3. Slippage stress 0/1/2 ticks on 2025
4. Lucid MC pass rate @1 micro (`src/evaluation/monte_carlo.py`)
5. Compare equity curve plots → save summary tables to `data/reports/phase7_*.md`

**Data splits (same as Phase 5):**
- Train/grid: 2019-06-01 → 2025-12-31
- WF OOS stitched: 2021–2025
- **Holdout 2026:** touch once at the very end for the winner(s) only

### D. Deliverables

1. `docs/PHASE_7_REPORT.md` — findings, charts-as-tables, recommendation vs ORB
2. `data/reports/phase7_leaderboard.md` — sortable by pass rate, smoothness, recency P&L
3. New/updated strategy modules + tests (keep `pytest` green)
4. If a winner beats ORB on pass rate **and** smoothness: optional `tradingview/` Pine script
5. Update `docs/PROJECT_STATUS.md`

---

## Key file paths

```
src/backtest/engine.py          # event-driven engine
src/strategies/opening_range.py # current best ORB
src/evaluation/lucid_rules.py   # Lucid 25K state machine
src/evaluation/monte_carlo.py   # pass probability
src/validation/walk_forward.py  # WF validation
scripts/run_backtest.py
scripts/run_validation.py
scripts/run_recommendation.py
data/processed/trades_opening_range_breakout_wf_oos.parquet
data/processed/continuous_{1,5}m.parquet
config/lucid_25k.yaml
tradingview/lucid_orb_25k.pine  # TV reference (5m chart, Skip Mon ON)
```

**Run tests:** `.venv/bin/pytest -q`

---

## ORB baseline numbers (for comparison)

| Metric | ORB WF OOS |
|---|---|
| Trades | 993 |
| Net P&L | $18,377 |
| Sharpe (daily) | 1.16 |
| Max DD | $3,458 |
| Lucid pass @1 micro | ~44% (skip Mon ~52% on same ledger) |
| 2026 holdout | +$948, 122 trades |

**ORB pain points to address:**
- Many exits at `eod` / session end (not hitting target or stop)
- 2025 weak in TV exports
- Equity curve spiky; user reports last ~90 days negative in live TV backtest

---

## Constraints

- Do **not** remove or break existing ORB validation artifacts
- Do **not** re-run 2026 holdout repeatedly for tuning
- Keep strategies **intraday flat** (Lucid eval assumption)
- Max **1–2 trades/day** unless explicitly justified
- Document all new YAML params in `config/strategies.yaml`
- Prefer **fewer, robust params** over large grids
- Commission remains placeholder until user confirms platform

---

## User account (for simulation)

- **LucidFlex 25K** ($70 eval / $60 reset with coupon)
- **1 MNQ micro** default sizing
- EOD trailing MLL $1,000, target $1,250, 50% consistency, 2 min days

---

## Success criteria for Phase 7

Recommend a strategy (or ORB variant) only if it meets **all**:

1. Lucid 25K pass rate **≥ ORB baseline** (or ≥ ORB skip-Monday ~52%) in MC on WF OOS ledger
2. **Smoother equity** than ORB (define metric; e.g. lower max DD or higher daily Sharpe)
3. **Profitable in last 252 trading days** on WF OOS slice (not just all-time)
4. Holds up in slippage stress (2025, 0–2 ticks)
5. Does not collapse on single 2026 holdout run (need not beat ORB, but must not be strongly negative)

If nothing beats ORB on pass rate + consistency, say so explicitly and recommend **ORB + Skip Monday + lower size** as the conservative eval plan.

---

## Optional first command for Claude Code

```bash
cd "/Users/ethannguyen/Desktop/MNQ Strategy"
.venv/bin/pytest -q
# Then analyze ORB last-90-day P&L from WF OOS ledger before building new strategies
.venv/bin/python -c "
import polars as pl
from datetime import date, timedelta
t = pl.read_parquet('data/processed/trades_opening_range_breakout_wf_oos.parquet')
cut = t['trading_date'].max() - timedelta(days=90)
recent = t.filter(pl.col('trading_date') >= cut)
print('Last ~90 calendar days:', recent.height, 'trades, net', recent['net_pnl'].sum())
"
```

Begin Phase 7. Ask the user only blocking questions (e.g. platform commission). Otherwise proceed autonomously.
