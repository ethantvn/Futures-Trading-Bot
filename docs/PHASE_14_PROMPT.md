# Phase 14 Prompt — Lucid Flex 100K Account Research

## Your task

The user forgot to include **Lucid Flex 100K** in prior work. Phases 1–13 only
systematically ranked strategies on **25K** and **50K**. Run a dedicated
**100K tier study**: does a larger account (bigger MLL **and** bigger profit
target) change any recommendation — for the frozen **MNQ ORB-W** winner, and
for gold (GC / MGC) where sizing was the blocker?

**Do not invent a new MNQ strategy.** The Phase 9 MNQ params are frozen.
This phase is about **account tier + contract sizing**, plus a **re-check** of
gold under the 100K risk budget. Be picky: only recommend 100K if pass rate,
timeline, and holdout (where applicable) beat or clearly justify the jump from
25K.

---

## Read first (in order)

1. `docs/PROJECT_STATUS.md` — current live rec = MNQ ORB-W on **25K @ 1 micro**
2. `docs/PHASE_9_REPORT.md` — MNQ long-only ORB-W (~64% pass on 25K)
3. `docs/PHASE_11_REPORT.md` + `docs/PHASE_13_REPORT.md` — GC fails on **risk**,
   MGC fails on **reward/sparsity** at 25K/50K
4. `docs/PHASE_1_PLAN.md` §3 — 100K Flex numbers (captured 2026-07-06; VERIFY)
5. `config/lucid_25k.yaml`, `config/lucid_50k.yaml` — mirror structure for 100K
6. Ledgers (reuse, do not rebuild unless missing):
   - MNQ: `data/processed/trades_phase9_orb_longonly_wf_oos.parquet`
   - (optional holdout) `data/processed/trades_phase9_orb_longonly_holdout.parquet`
   - MGC / GC phase 11–13 WF OOS ledgers under `data/processed/mgc/` and
     `data/processed/gc/` if present

---

## Lucid Flex 100K rules (create config)

**There is no `config/lucid_100k.yaml` yet — create it.**

From Phase 1 capture (VERIFY against user’s dashboard before treating as final):

| Field | Value |
| --- | --- |
| Starting balance | **$100,000** |
| Profit target | **$6,000** |
| Max loss (MLL) | **$3,000** |
| Drawdown | EOD trailing, locks at start balance (same as 25K/50K) |
| Consistency | 50% at pass |
| Min trading days | 2 |
| Max micros | **60** (6 minis) |
| Eval fee | ~$225 ($157.50 discounted) — VERIFY |
| Reset fee | ~$140 — VERIFY |

Critical ratio:

| Tier | Target / MLL |
| --- | --- |
| 25K | $1,250 / $1,000 = **1.25×** |
| 50K | $3,000 / $2,000 = **1.50×** |
| 100K | $6,000 / $3,000 = **2.00×** |

100K is **harder per dollar of edge** even though raw MLL is larger — you need
**twice** the cushion in target vs drawdown room. Document this in the report.

Add costs placeholders (VERIFY) matching the style of other lucid_*.yaml files.

---

## Part A — MNQ ORB-W on 100K (PRIMARY)

Frozen strategy (do **not** re-grid params):

- Long-only width-filtered ORB + skip Monday
- Ledger: Phase 9 WF OOS (`trades_phase9_orb_longonly_wf_oos.parquet`)
- Same skip-Monday filter as Phase 9 MC

**Monte Carlo (10k, block bootstrap, max_days=60):**

Contract sweep on **100K**: `1, 2, 3, 4, 5, 6, 8, 10` micros (cap at
`max_contracts_micro`).

Also re-run **25K @ 1** and **50K @ best prior sizes** as side-by-side baselines
in the same report so the user can compare tiers apples-to-apples.

For each (account, contracts) report:

- Pass % / fail % / timeout %
- Median days to pass
- Pass within 10 / 15 / 20 / 40 days
- E[resets], E[cost] (use discounted fees if available)
- Optional: journey MC pass+payout if easy to extend (`_pass_and_payout_mc`
  currently hardcodes 25K — adapt or note limitation)

**Sizing intuition to test (not assume):**

- 1 micro on 100K → almost never hits $6,000 in 60 days (timeout)
- Need roughly **~3–5+ micros** to match 25K@1 speed — at the cost of blow risk
- Prior ad-hoc MC (conversation) suggested ~49% pass @5 micros / worse
  pass+payout — **re-run formally and cite numbers from this phase**

**Also:** one frozen-params run of the Phase 9 **2026 holdout ledger** through
100K MC at the recommended contract count (no param re-tune).

---

## Part B — Gold re-check under $3,000 MLL (SECONDARY)

Do **not** restart 6,000-combo gold research from scratch unless Part A shows
100K is hopeless for MNQ *and* gold sizing suddenly looks viable.

### B1 — Full-size GC @ 100K

Phase 11 rejected GC on 50K because P95 daily range ~$7,800 ≫ $2,000 MLL.
On 100K, MLL = **$3,000** — still often below P95, but re-run the **sizing
check** and MC the **best prior GC WF OOS ledgers** (e.g. macro / comex from
phase11/12) at **1 GC contract** (and optionally 1 only — do not size up GC).

If still structurally unsound (worst/P95 day ≫ MLL), say so and skip deep grids.

### B2 — MGC @ 100K

Phase 13: 50K @ 1 MGC = **0%** pass ($3,000 target unreachable at $10/pt).
100K target is **$6,000** — even harder at 1 MGC.

Sweep **contracts 2, 3, 5, 8, 10** on the best practical MGC ledger
(`comex_orb_deep` or similar — **not** sparse macro_nfp lottery) under 100K MC.
Apply the same **wall-clock / sparsity** and **holdout** guards as Phase 13:

- Reject if median calendar time to pass is years
- Reject if 2026 holdout MC collapses
- Reject if sizing up only inflates fail %

Only reopen a gold grid if a frozen ledger already clears ≥ ~45–50% pass on
100K with practical days-to-pass **and** holdout doesn’t die.

---

## Part C — Decision table (REQUIRED)

Produce a clear recommendation:

| Option | Pass % | Med days | E[cost] | Holdout | Recommend? |
| --- | --- | --- | --- | --- | --- |
| 25K MNQ @ 1 micro | … | … | … | … | … |
| 50K MNQ @ N | … | … | … | … | … |
| 100K MNQ @ N* | … | … | … | … | … |
| 100K GC / MGC (if any) | … | … | … | … | … |

Default expectation (to confirm or refute with data): **25K @ 1 micro remains
best**; 100K only wins if the user explicitly prioritizes speed/payout size and
accepts materially lower pass probability.

---

## Deliverables

1. `config/lucid_100k.yaml`
2. `docs/PHASE_14_REPORT.md` — sizing ratios, full MC tables, decision
3. `data/reports/phase14_100k_leaderboard.md` (or under `data/reports/`)
4. `scripts/run_phase14_100k.py` — reproducible MC sweeps (MNQ primary; gold
   secondary if ledgers exist)
5. Update `docs/PROJECT_STATUS.md` with 100K verdict

---

## Constraints

- **Do not re-optimize MNQ ORB-W params** on any 2026 data
- Do not claim 100K is “safer” just because MLL is $3,000 — check target/MLL
  ratio and contract-scaled worst days
- Prefer pass rate + practical timeline over max theoretical payout
- Keep `.venv/bin/pytest -q` green
- Ask the user only if 100K fee/MLL numbers on their dashboard disagree with
  Phase 1 capture

---

## First commands

```bash
cd "/Users/ethannguyen/Desktop/MNQ Strategy"
.venv/bin/pytest -q
# Confirm MNQ Phase 9 ledger exists:
ls data/processed/trades_phase9_orb_longonly_wf_oos.parquet
# Then create lucid_100k.yaml and run Phase 14 MC sweeps.
```

Begin Phase 14. Goal: tell the user clearly whether **Lucid Flex 100K** is
worth buying for MNQ (and at how many micros), or whether to **stay on 25K**.
