---
type: moc
updated: 2026-07-13
---

# 🧠 MNQ Lucid Eval — Home

> **Mission:** maximize Lucid Flex 25K eval **pass rate** and **pass → first payout**, then scale funded income.

## Current state (2026-07-13)

| | |
| --- | --- |
| Mode | **Research** (pre-live) |
| Incumbent | [[orb-w-incumbent|ORB-W long-only + skip Monday @ 1 micro]] |
| Expected | **~69.8% pass / ~51.6% pass+payout**, median ~26 active days (no eval time limit, $0.50/side) |
| Pine | `tradingview/lucid_orb_width_25k.pine` |
| Rules | [[lucid-25k-verified]] |
| Ledger | `data/processed/trades_phase9_orb_longonly_wf_oos.parquet` (473 trades) + 2026 holdout (52 trades, +$2,836) |

## The bar for any challenger

See [[picky-bar]]. Short version: beat **~70% pass / ~52% pass+payout** on WF + 10k MC **and** holdout, with ≥4 trades/month, ≥50% positive folds, ≥100 OOS trades. No sparsity traps. Causal only ([[causal-only]]).

## Open research

```dataview
TABLE status, priority, next-action AS "Next action"
FROM "brain/Experiments"
WHERE status = "open"
SORT priority ASC
```

*(Static fallback if Dataview isn't installed yet:)*

1. [[orderflow-delta-gate]] — the one remaining alpha bet; Stage 0 cost estimate in [[databento-trades-quote]]; needs YOUR go/no-go on buying data — **P2**
2. [[tv-python-reconciliation]] — pre-live operational check — **P2**
3. [[payout-mll-rule-check]] — ask Lucid when convenient; only affects multi-cycle income modeling now — **P3**
4. [[wf-reselection-2026-12]] — scheduled refresh + orb_tod/NR7 watch list — **P3 (December)**

**Closed 2026-07-13:** [[joint-multiaccount-mc]] (→ [[run-both-accounts]]) · [[rescore-frozen-ledgers]] (verified-rules audit: **incumbent stands**, orb_tod → Dec watch) · [[funded-phase-sizing]] (**rejected** — every funded upshift loses 7–18pts; [[fixed-1-micro]] now covers both phases). **All solo-runnable research is done — remaining items need user action or December data.**

## Rejected — do not reopen without new data class

```dataview
TABLE phase, verdict
FROM "brain/Experiments"
WHERE status = "rejected"
SORT phase ASC
```

*(Static index: [[mes-as-primary]] · [[gold-gc-mgc]] · [[tier-50k-100k]] · [[scalping-families]] · [[overnight-fade]] · [[structure-levels-poc-rounds]] · [[vix-on-regime-gates]] · [[p18-mean-reversion-fades]] · [[p18-trend-momentum]] · [[orb-filter-variants]] · [[mes-divergence-gate]] · [[eval-sizing-policies]] · [[shorts-research]] · [[time-stops-target-grids]] · [[portfolio-near-clones]])*

## Locked decisions

[[long-only]] · [[skip-monday]] · [[fixed-1-micro]] · [[tier-25k]] · [[causal-only]] · [[no-more-ohlcv-grids]] · [[picky-bar]] · [[run-both-accounts]]

## Key project artifacts (outside brain/)

- [[PROJECT_STATUS]] — phase-by-phase outcomes
- [[PHASE_18_REPORT]] — the definitive OHLCV sweep (~442 combos, nothing beats ORB-W)
- [[PHASE_19_REPORT]] — sizing policies all rejected
- [[LUCID_RULES_VERIFIED]] — verified account rules
- `data/reports/rebacktest_commission050.md` — current headline numbers
- `data/reports/shorts_research.md` — shorts rejected under verified rules

## Workflow

- New idea? Create a note from [[experiment-template]] in `Experiments/` **before** running anything. Check the rejected list first.
- Result in? Update the note's `status` + `verdict`, link the report.
- Big call made? One note in `Decisions/` from [[decision-template]].
- Going live? Daily note from [[daily-journal-template]] in `Journal/`.
- Raw material (Lucid support replies, data quotes, articles) → `Inbox/`, file weekly.
