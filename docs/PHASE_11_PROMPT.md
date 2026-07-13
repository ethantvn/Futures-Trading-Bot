# Phase 11 Prompt — Gold (GC) Futures Strategy Research for Lucid Flex 50K

Copy everything below the line into Claude Code (or a new agent session) in the repo root:
`/Users/ethannguyen/Desktop/MNQ Strategy`

---

## Your task

Research and validate a **gold futures (GC, full-size COMEX) strategy** for a
**Lucid Flex 50K** evaluation, using the same backtest engine, Lucid rule
simulator, walk-forward, and Monte Carlo infrastructure already built for
MNQ. This is a **new instrument, new account tier, new strategy family** —
not a port of the MNQ ORB. Phase 10 already tried porting the MNQ edge to a
second instrument (MES) and it failed (19% pass vs 64% on MNQ); do not repeat
that mistake by assuming ORB-on-MNQ params transfer. Start from gold-native
hypotheses.

Read these first (in order):
1. `docs/PROJECT_STATUS.md` — current state of the MNQ track, for infra context only
2. `docs/PHASE_10_REPORT.md` — why the cross-instrument port failed; do not repeat the approach
3. `config/lucid_50k.yaml` — the account rules for THIS phase (50K, not 25K)
4. `config/data_gc.yaml` — GC data pipeline config (already built and run)
5. `data/reports/gc/data_quality.md` — GC data quality report (already generated)

**Do not read the MNQ-specific phase reports (7, 8, 9) for strategy ideas** —
skim them only for *methodology* (how walk-forward/MC/holdout discipline was
applied), not for parameters. Gold's volatility regime, session structure,
and macro drivers are different enough that MNQ params are not a starting
point.

---

## What already exists (do not redo)

**Data (already ingested, verified):**
- `data/processed/gc/{bars_1m,continuous_1m,continuous_3m,continuous_5m,continuous_15m,continuous_30m,roll_calendar}.parquet`
- Source: Databento `GLBX.MDP3` `GC.FUT` (parent), `ohlcv-1m`, 2021-06-11 → 2026-07-10 (~5 years, 1,312 trading days, 89 contracts, raw file in `data/raw/GLBX-20260711-8S93A73DEF/`)
- Quality: 0 duplicate bars, 0 OHLC violations, 0 non-tick-aligned prices (validated against `tick_size: 0.10`), 14 short days (all holiday/half-day, documented in the quality report)
- Contract specs (confirmed by user): **full-size GC**, tick `0.10` = **$10/tick**, point value **$100/pt** (100 troy oz)

**KNOWN ISSUE — fix before any strategy grid work:** the volume-based roll
calendar (`src/data/rollover.py`, `confirm_sessions=1`) flickers into
thin/illiquid contract months for ~5 days at a time around each roll
(month codes F/H/K/U/X each appear ~5 times — these are NOT among gold's six
standard liquid months G,J,M,Q,V,Z). This can inject phantom back-adjustment
gaps into the continuous series. **Task 0:** either (a) restrict roll
candidates to `{G,J,M,Q,V,Z}` contract months, or (b) raise
`confirm_sessions` to 2-3 for GC specifically, and re-verify the roll
calendar is clean (each roll lands on a G/J/M/Q/V/Z month, no round-trips)
before building any signal frames on top of it.

**Engine/evaluation infra (instrument-agnostic, reuse as-is):**
- `src/backtest/` — event-driven engine, 5m-signal/1m-fill discipline, pessimistic fills, cost model
- `src/evaluation/` — `lucid_rules.py`, `monte_carlo.py`, `consistency.py` (UPI, ulcer, recency windows, rolling 6m, p95 daily loss, worst-20d window — all built in Phase 7/8, reuse directly)
- `src/validation/walk_forward.py` — fold/grid/scoring machinery
- `src/data/macro_calendar.py` + `data/calendar/macro_events.csv` — NFP/CPI/FOMC dates (built Phase 9 for MNQ; gold is at least as macro-sensitive — reuse and extend if other gold-relevant events are missing, e.g. real-yield/DXY-moving releases)

**What you must build:**
- `config/strategies_gc.yaml` — GC engine costs (commission for full-size futures is NOT the MNQ micro placeholder currently in `config/strategies.yaml`; use a documented full-size futures placeholder, e.g. ~$2.50/side commission + exchange/NFA fees, and flag it VERIFY like every other cost placeholder in this project)
- New strategy modules under `src/strategies/` for gold-native hypotheses (below)
- A GC-specific validation config (`config/gc_phase11.yaml` or similar, mirroring `config/phase7.yaml`/`phase8.yaml` structure)

---

## Critical first check: is 1 GC contract even viable for a 50K account?

Full-size GC is **50x MNQ's dollar sensitivity per point** ($100/pt vs $2/pt).
The Lucid 50K max drawdown (MLL) is **$2,000**. A typical GC daily range is
roughly $15-30/oz historically (150-300 ticks), i.e. **$1,500-3,000 of
movement per contract per day** — a single adverse full-day move on 1
contract can approach or exceed the entire account's loss budget.

**Before running any strategy grid, compute:**
1. Realistic ATR-based stop distances (in ticks and dollars) at several
   timeframes (5m, 15m, 1h) using the GC continuous series.
2. What stop distance keeps a single trade's risk at a sane fraction of the
   $2,000 MLL (e.g. 15-25%, i.e. $300-500/trade) at **1 contract**.
3. Whether a structurally sound stop (not an artificially tightened one that
   guarantees whipsaw) fits inside that budget for the strategy families
   below, at 1 contract.

**If 1 full-size GC contract cannot fit a sound stop inside a reasonable
fraction of the 50K's risk budget, say so explicitly and present the
tradeoff back to the user (e.g. recommend Micro Gold MGC — $10/pt, $1/tick,
1/10th the risk — as a sizing fallback) rather than silently shrinking stops
to fit.** This mirrors the Phase 6 finding that the same MNQ edge yielded
19% pass on 50K vs 44% on 25K purely from target/drawdown ratio — get the
sizing math right before spending grid-search budget on parameters.

---

## Strategy families to research (gold-native, start simple)

Gold has no NYSE-anchored cash session the way equity index futures do; it
trades COMEX-hours-through-Globex nearly 24h. Re-derive session logic instead
of reusing `RTH_OPEN_MIN = 9:30` from `src/strategies/opening_range.py`.
Consider:

1. **Session-open range breakout, gold-native anchors** — test range windows
   anchored to: COMEX pit-legacy open (~8:20 ET), NY equity open (09:30 ET,
   for comparison only), London AM gold fix (~05:30 ET), Asia/Globex open
   (~18:00 ET / 6:00 ET Asia afternoon). Same OCO stop-entry structure as
   MNQ ORB is fine to reuse (`src/strategies/opening_range.py` is
   parameterized on window) — the anchor time and width filter need
   gold-specific re-derivation, not the 09:30 default.
2. **Macro-release volatility strategy** — gold is highly sensitive to
   CPI (8:30 ET), FOMC (14:00 ET), NFP (8:30 ET first Friday). Use
   `src/data/macro_calendar.py` to build a breakout/straddle around these
   releases, sized to keep the single-event risk bounded (see sizing check
   above). Compare release days vs non-release days for baseline
   expectancy before building a dedicated strategy.
3. **NR7 / inside-day compression breakout** — same pattern class validated
   for MNQ (`src/strategies/nr_compression.py`), re-parameterized and
   re-tested on gold's own volatility distribution — do not reuse MNQ's
   `nr_n`/width thresholds.
4. **Trend/momentum on macro drivers** — gold trends on real-yield/USD/
   geopolitical flows over days, but the Lucid eval assumption is
   **intraday flat** (no overnight risk carried, per existing engine
   constraint — keep this). Test same-day trend-continuation entries (e.g.
   price above/below session VWAP with a momentum filter) rather than
   multi-day holds.
5. **Session mean reversion** — fade extended intraday moves back to VWAP in
   low-realized-vol regimes, as tested (and rejected) for MNQ — re-test on
   gold since the volatility regime differs; do not assume the MNQ
   rejection transfers.

For each candidate: causal `prepare()`, no-lookahead test (mirror the
pattern in `tests/test_phase7_strategies.py`), full-period backtest, small
walk-forward grid (fewer, robust params — 2-4 per family), slippage stress.

---

## Validation discipline (same rigor as MNQ Phases 5-8, adapted for 5 years of data)

- **Data splits:** grid/train through ~2025-12-31; **holdout Jan 2026 →
  most recent data (2026-07-10), touched ONCE at the end**, same discipline
  as the MNQ holdout (no re-tuning after looking at it).
- **Walk-forward folds:** only 5 years available (vs MNQ's 7) — use a
  smaller train window than MNQ's 24m/6m (e.g. 18m train / 6m test) so you
  get enough folds to trust the OOS stitch; document the fold count and
  window choice, don't just copy MNQ's.
- **Ranking:** Lucid **50K** pass rate (10k MC, block bootstrap) is
  PRIMARY — use `config/lucid_50k.yaml`, not 25k. Consistency/smoothness
  (UPI, max DD, recency windows, rolling 6m stability from
  `src/evaluation/consistency.py`) is the tie-breaker, same as Phase 7.
- **Slippage stress:** 0/1/2 ticks on the most recent full year, same
  pattern as `src/validation/stress.py` — but note 1 tick on GC = $10,
  materially larger than MNQ's $0.50/tick, so re-check whether the edge
  survives proportionally larger slippage.
- Keep `.venv/bin/pytest -q` green throughout; run it before and after.

---

## Deliverables

1. `docs/PHASE_11_REPORT.md` — findings, sizing-check results, ranked
   candidates, final recommendation (or explicit "nothing clears the bar"
   verdict with the sizing/MGC fallback discussion if applicable)
2. `data/reports/gc_leaderboard.md` — sortable by pass rate, then smoothness
3. New strategy modules in `src/strategies/` + tests (keep suite green)
4. `config/strategies_gc.yaml`, `config/gc_phase11.yaml` (or similar),
   `scripts/run_phase11.py` (mirror `run_phase7.py`/`run_phase8.py` patterns)
5. If a strategy passes: optional `tradingview/` Pine script for GC,
   following the Phase 8 lesson — flat-order logic must key on bar-**close**
   time, not bar-open time, from the start (don't reintroduce that bug)
6. Update `docs/PROJECT_STATUS.md` with the Phase 11 outcome

---

## Constraints

- **Do not re-tune on the 2026 holdout** once touched
- Keep strategies **intraday flat** (Lucid eval assumption — no overnight
  gold exposure, consistent with the existing engine's flat-by-session-close
  design)
- Prefer **fewer, robust params** over large grids
- Document every cost/spec placeholder as VERIFY (commission, exchange fees)
  — full-size GC commission is genuinely different from the MNQ micro
  numbers already in the repo; do not silently reuse them
- Fix the roll-calendar noise (Task 0) before trusting any backtest numbers
- If the sizing check says 1 GC contract is unsound for the 50K's risk
  budget, **surface that finding clearly** rather than forcing a fit

---

## Key file paths

```
src/backtest/engine.py                  # event-driven engine (instrument-agnostic)
src/strategies/opening_range.py         # ORB reference implementation (re-parameterize, don't reuse params)
src/strategies/nr_compression.py        # NR-n reference (re-parameterize)
src/evaluation/lucid_rules.py           # Lucid rule engine (config-driven — point at lucid_50k.yaml)
src/evaluation/monte_carlo.py           # pass probability
src/evaluation/consistency.py           # smoothness/recency metrics (Phase 7/8)
src/validation/walk_forward.py          # WF validation
src/data/macro_calendar.py              # NFP/CPI/FOMC dates (Phase 9)
data/processed/gc/continuous_{1,3,5,15,30}m.parquet
data/reports/gc/data_quality.md
config/lucid_50k.yaml                   # THIS phase's account rules
config/data_gc.yaml                     # GC data pipeline config (already run)
```

**Run tests:** `.venv/bin/pytest -q`

---

## Success criteria

Recommend a gold strategy only if it meets **all**:

1. Passes the sizing check (Task above) at the tested contract count
2. Lucid **50K** pass rate materially above the ~20-30% range you'd expect
   from an under-researched cross-instrument port (Phase 10's MES result is
   the cautionary floor, not a target)
3. Positive expectancy holds walk-forward OOS across the full period, not
   just one regime (check the rolling-6m stability metric)
4. Survives slippage stress at 0/1/2 ticks (remember: 1 tick = $10 on GC)
5. Does not collapse on the single 2026 holdout run

If nothing clears the bar, say so explicitly, report what was tried and why
each family failed (mirror the rejected-strategy tables in
`data/reports/phase7_leaderboard.md` for the documentation pattern), and
give a recommendation (e.g. MGC micro sizing study, or defer gold and stay
on the validated MNQ track).

---

## Optional first commands for Claude Code

```bash
cd "/Users/ethannguyen/Desktop/MNQ Strategy"
.venv/bin/pytest -q
# Confirm the roll-calendar issue before anything else:
.venv/bin/python -c "
import polars as pl
rc = pl.read_parquet('data/processed/gc/roll_calendar.parquet')
rc = rc.with_columns(pl.col('symbol').str.slice(-2,1).alias('month_code'))
print(rc.group_by('month_code').agg(pl.len()).sort('month_code'))
"
# Then run the sizing check (ATR-based $ risk per contract) before any strategy grids.
```

Begin Phase 11. Ask the user only blocking questions (e.g. commission
confirmation, or if the sizing check says GC full-size doesn't fit the 50K
risk budget). Otherwise proceed autonomously.
