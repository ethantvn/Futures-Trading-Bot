# Phase 13 Prompt — Micro Gold (MGC) Thorough Eval Strategy Research

## Your task

Research and validate a **Micro Gold (MGC) futures** strategy that can
**reliably pass a Lucid Flex evaluation**. Full-size GC failed Phases 11–12
primarily because **$100/pt vs a $1,000–$2,000 MLL** is structurally hostile.
MGC is **1/10th the dollar risk** ($10/pt, $1/tick) — this is the correct
sizing vehicle for gold on Lucid.

Be **thorough and picky**. Prefer a strategy that **passes eval with high
probability** over a “simple” one. If the best candidate needs many filters /
parameters and still holds walk-forward + holdout + slippage stress, **ship it**.
Do **not** reject a winner just because the param count is high — reject it only
if it fails validation discipline (especially holdout / regime stability).

This is **not** a blind port of MNQ ORB params and **not** a copy of GC
full-size params. Re-derive on MGC’s own volatility and dollar risk. Reuse
engine, Lucid MC, walk-forward, and gold-native strategy *code* where useful;
re-grid everything.

---

## Read first (in order)

1. `docs/PROJECT_STATUS.md` — current recommendation (MNQ) + GC rejection
2. `docs/PHASE_11_REPORT.md` — why full-size GC failed sizing / families
3. `docs/PHASE_12_REPORT.md` — deep GC grids still failed 2026 holdout;
   lesson: more combos ≠ durable edge; holdout is decisive
4. `docs/PHASE_10_REPORT.md` — MES port failed (19% pass) — do not assume
   cross-instrument param transfer
5. `config/lucid_25k.yaml` and `config/lucid_50k.yaml` — test **both** account
   tiers; MGC may fit 25K better than 50K
6. Gold strategy modules already in repo (re-parameterize, don’t hardcode GC $):
   - `src/strategies/gc_session_orb.py`
   - `src/strategies/gc_macro_breakout.py`
   - `src/strategies/gc_nr_orb.py`
   - `src/strategies/gc_vwap.py`
7. Pipeline patterns: `scripts/run_phase11.py`, `scripts/run_phase12.py`,
   `scripts/build_bars.py --config …`

**Do not re-tune on 2026 holdout.** Touch holdout **once** at the end for
finalists only.

---

## Data (already purchased — ingest first)

**Source (on Desktop — copy into the project):**

```
/Users/ethannguyen/Desktop/GLBX-20260711-SJH7NNPY6M/
  glbx-mdp3-20210611-20260710.ohlcv-1m.csv.zst
  condition.json
  metadata.json
  manifest.json
```

- Databento `GLBX.MDP3`, schema `ohlcv-1m`, parent symbol **`MGC.FUT`**
- Range: **2021-06-11 → 2026-07-10** (~5 years, same window as GC)

**Contract specs (VERIFY in quality report / CME):**

| Spec | MGC (micro) | GC (full) for reference |
| --- | --- | --- |
| Multiplier | **10 troy oz** | 100 troy oz |
| Tick | **0.10** | 0.10 |
| Tick value | **$1** | $10 |
| Point value | **$10 / pt** | $100 / pt |
| vs Lucid MLL | ~10× more room than GC | structurally tight |

**Task 0 — ingest + roll calendar (do before any grids):**

1. Copy batch → `data/raw/GLBX-20260711-SJH7NNPY6M/`
2. Add `config/data_mgc.yaml` (mirror `config/data_gc.yaml`):
   - `tick_size: 0.10`
   - `point_value: 10.0`
   - `processed_dir: data/processed/mgc`
   - `reports_dir: data/reports/mgc`
   - `rollover.confirm_sessions: 2`
   - `rollover.liquid_month_codes: [G, J, M, Q, V, Z]` (same COMEX gold months)
3. Run: `.venv/bin/python scripts/build_bars.py --config config/data_mgc.yaml`
4. Verify roll calendar has **zero** non-liquid month codes; fix if needed
5. Write `data/reports/mgc/data_quality.md` (tick grid must be 0.10, not 0.25)

---

## Critical first check: sizing vs Lucid MLL

Before strategy grids, compute ATR / daily-range **dollar** risk at 1 MGC
contract for **both** 25K ($1,000 MLL) and 50K ($2,000 MLL).

Target per-trade risk band: **15–25% of MLL**

| Account | MLL | Comfortable stop $ | Comfortable stop pts @ $10/pt |
| --- | --- | --- | --- |
| 25K | $1,000 | $150–$250 | **15–25 pts** |
| 50K | $2,000 | $300–$500 | **30–50 pts** |

Also report median / P95 **daily RTH range in $** at 1 MGC. Compare explicitly
to Phase 11 GC (median ~$1,930/day, P95 ~$7,810/day on full-size) — MGC should
be ~1/10th those dollar figures.

**Contract count:** start grids at **1 MGC**. After a survivor exists, optionally
MC-sweep **1 / 2 / 3** contracts — but only if 1-contract pass rate is already
strong. Do not size up to “force” a weak edge.

If even 1 MGC cannot fit a structural stop inside the band, say so and stop —
but that is unlikely given 1/10th GC risk.

---

## Account tier decision

Run Lucid MC for **both**:

- `config/lucid_25k.yaml` — primary candidate (same tier as validated MNQ)
- `config/lucid_50k.yaml` — secondary (higher target $3,000; may need more
  contracts or a stronger edge)

**Primary ranking metric:** pass rate on the tier you recommend for live use.
If 25K @ 1 MGC clears ≥ ~50–55% pass with stable holdout, prefer that over a
fragile 50K setup. Document the tradeoff.

---

## Strategy families (gold-native, thorough grids)

Reuse / extend Phase 11–12 gold families with **MGC point value and costs**.
Be willing to run **large grids** (hundreds–low thousands of combos per family
is OK if tractable; stage coarse → fine if needed).

### 1. Session-open range breakout (priority)

Anchors to grid (ET):

- COMEX ~**8:20** (`anchor_minute=500`)
- NY equity **9:30** (`570`)
- London AM ~**5:30** (`330`)
- Optional: Globex/Asia if you can define a causal window that actually emits

Axes (deep):

- `range_minutes`: 10, 15, 30, 45, 60
- `target_r`: 0.75, 1.0, 1.25, 1.5, 2.0
- `expire_minutes`: 45, 60, 90, 120
- width band: `min_width_ratio` × `max_width_ratio` (include “off”)
- `max_risk_points`: sized to MGC $ band (e.g. 15–40 pts on 25K; wider on 50K)
- `long_only`: true / false
- optional `skip_weekdays` (test Monday skip — don’t assume MNQ result)

### 2. Macro-release breakout (Phase 11/12 almost-winner on GC)

NFP / CPI / FOMC / combinations. Axes:

- `pre_range_minutes`, `post_delay_minutes`, `target_r`, `expire_minutes`
- `max_risk_points`, `min_range_points`, `long_only`
- Separate **nfp**, **cpi**, **nfp_cpi**, **fomc** families
- Lower `min_trades_train` for sparse FOMC — but **reject** if too few trades
  for a practical eval timeline (e.g. can’t reasonably hit target in ~60 days)

**Picky rule:** a 70%+ MC pass on &lt;30 OOS trades / year is **not** enough
unless holdout also works **and** median days-to-pass is realistic.

### 3. NR-n / inside-day compression ORB

Re-grid `nr_n`, mode, anchors, risk caps on MGC — do not reuse GC thresholds.

### 4. Session VWAP trend + mean reversion

Re-test on MGC; MNQ/GC rejection does not automatically transfer.

### 5. Optional extras if time

- Afternoon / London–NY overlap breakout
- Skip-macro vs trade-macro expectancy baseline (like Phase 9/11)
- Combined filter stacks (width + long_only + delay) — **allowed** if OOS +
  holdout survive

Keep **intraday flat** (engine `flat_time` ~16:55 ET or documented gold
session cutoff). No overnight holds.

---

## Costs (VERIFY placeholders)

Create `config/strategies_mgc.yaml` — **do not** reuse MNQ micro or GC
full-size commission blindly.

Suggested placeholders (document as VERIFY):

- Commission + exchange all-in: on the order of **~$1–2 / side / MGC**
  (micros are cheaper than full-size; confirm later)
- `slippage_ticks: 1` default (1 tick = **$1** on MGC — much kinder than GC’s $10)
- Stress slippage at **0 / 1 / 2 / 3** ticks

---

## Validation discipline

| Item | Requirement |
| --- | --- |
| Grid / train | through **2025-12-31** |
| Holdout | **2026-01-01 → 2026-07-10**, touched **ONCE** for finalists |
| Walk-forward | ~**18m train / 6m test** (5 years of data; document fold count) |
| Primary rank | Lucid **pass rate** (10k MC, block bootstrap) on chosen account |
| Tie-breakers | fold stability (% positive OOS folds), UPI, max DD, **2025 $**, median days to pass |
| Slippage | stress on 2025 for top candidates |
| Overfit guard | if best WF pass ≫ holdout MC pass, **reject** even if params are pretty |
| Tests | `.venv/bin/pytest -q` green; no-lookahead tests for any new strategy code |

**Picky acceptance bar (all must pass):**

1. Sizing check OK at tested contract count  
2. Lucid pass rate **materially above** junk floor (~25–30%); aim **≥ 50%** on
   recommended tier, ideally competitive with MNQ’s ~64% on 25K if possible  
3. Positive / stable walk-forward OOS (not one lucky fold)  
4. Survives slippage stress  
5. **2026 holdout does not collapse** (net not deeply negative; holdout MC
   pass not near zero)  
6. Enough trades for a practical eval (median days-to-pass ≲ ~45–60 active days)  
7. Param count is **not** a reject reason if 1–6 hold  

If nothing clears: say so explicitly, table what failed, and recommend staying
on MNQ — do **not** force a weak MGC bot.

---

## Deliverables

1. `docs/PHASE_13_REPORT.md` — sizing, leaderboard, holdout, final recommend
   (or explicit reject)
2. `data/reports/mgc/phase13_leaderboard.md`
3. `data/reports/mgc/phase13_sizing.md`
4. `data/reports/mgc/phase13_walk_forward.md`
5. `data/reports/mgc/phase13_holdout.md` (finalists only)
6. `config/data_mgc.yaml`, `config/strategies_mgc.yaml`, `config/mgc_phase13.yaml`
7. `scripts/run_phase13_mgc.py` (mirror phase11/12 patterns; MC both 25K & 50K)
8. Update `docs/PROJECT_STATUS.md`
9. If a strategy **passes all bars**: optional TradingView Pine for MGC with
   **bar-close** flat logic (Phase 8 lesson — don’t reintroduce overnight bug)

---

## Constraints

- Intraday flat only  
- No re-tune after looking at 2026 holdout  
- Liquid-month roll filter for gold  
- Document every cost as VERIFY  
- Prefer robust survivors over max in-sample Sharpe  
- Many parameters OK **if** holdout + slippage + fold stability agree  
- Sparse “lottery” strategies (e.g. 4 FOMC trades) — reject for eval use  
- Ask the user only for blocking questions (e.g. which Lucid tier they will
  buy if both look viable)

---

## Key paths

```
Raw (copy from):  /Users/ethannguyen/Desktop/GLBX-20260711-SJH7NNPY6M/
Project raw:      data/raw/GLBX-20260711-SJH7NNPY6M/
Processed:        data/processed/mgc/
Reports:          data/reports/mgc/
GC reference:     config/data_gc.yaml, scripts/run_phase11.py, run_phase12.py
Lucid rules:      config/lucid_25k.yaml, config/lucid_50k.yaml
MNQ champion:     tradingview/lucid_orb_width_25k.pine (do not replace unless MGC wins)
```

**First commands:**

```bash
cd "/Users/ethannguyen/Desktop/MNQ Strategy"
.venv/bin/pytest -q
mkdir -p data/raw
cp -R "/Users/ethannguyen/Desktop/GLBX-20260711-SJH7NNPY6M" data/raw/
# then create config/data_mgc.yaml and:
.venv/bin/python scripts/build_bars.py --config config/data_mgc.yaml
```

Begin Phase 13. Goal: find a **picky, holdout-validated MGC eval passer** —
or prove MGC also fails and keep MNQ as primary.
