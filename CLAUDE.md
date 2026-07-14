# MNQ Lucid Flex Eval Research

Goal: maximize Lucid Flex 25K eval **pass rate** and **pass → first payout** — not Sharpe, not trade count.

**Incumbent (do not rediscover):** MNQ ORB-W long-only + skip Monday @ 1 micro — ~69.8% pass / ~51.6% pass+payout (verified rules, $0.50/side, no eval time limit). Pine: `tradingview/lucid_orb_width_25k.pine`.

## The knowledge base: `brain/`

This repo doubles as an Obsidian vault; `brain/` is the curated second brain. **Start every research session at `brain/00 Home.md`** — it indexes open work, rejected experiments, and locked decisions.

Maintenance conventions (binding for Claude Code sessions):

1. **Before proposing or running any experiment**, check `brain/Experiments/` — if a note with `status: rejected` covers it, do not reopen without a new data class or explicit user override.
2. **Every experiment gets a note** in `brain/Experiments/` from `brain/Templates/experiment-template.md`, with kill criteria written **before** running. On completion: update `status` + `verdict`, link the report.
3. **Every locked call** gets a note in `brain/Decisions/` with a falsifiable "would reopen if".
4. Update the static indexes in `brain/00 Home.md` when notes are added (Dataview blocks handle it live, but static lists are the no-plugin fallback).
5. File naming: kebab-case. Link with `[[wikilinks]]` (phase reports in `docs/` resolve by basename).
6. Process `brain/Inbox/` items into the right folder when asked to do a review.

## Hard research rules (evidence-backed, see brain/Decisions/)

- **Causal only.** No lookahead. TV-vs-Python ledger divergence = audit trigger (this caught the overnight-fade bug).
- **The picky bar** (`brain/Decisions/picky-bar.md`): challengers must beat ~70%/~52% on WF + 10k MC **and** frozen holdout, with ≥4–5 t/mo, ≥100 OOS trades, ≥50% positive folds. Never promote on holdout alone. Reject sparsity traps.
- **No more OHLCV grids.** Phases 1–18 exhausted bar-data families. New edges need new data (order flow) or are eval-mechanics/economics work.
- Holdout (2026+) is touched once per study and never re-tuned against.

## Repo map

- `docs/PHASE_*_REPORT.md` — full research history (Phases 1–19)
- `data/reports/` — leaderboards, holdouts, rebacktests
- `config/` — Lucid rules (`lucid_25k.yaml`), phase grids
- `src/` — engine (pessimistic fills), strategies, Lucid rule state machine, MC
- `scripts/run_phase*.py` — reproducible pipelines
- Python: `.venv/bin/python`, tests via `.venv/bin/pytest`

## Conventions

- Bar timestamps are bar-open; `ts_utc` canonical, `ts_ny` for sessions. CME trading date: ≥18:00 ET belongs to next date.
- Dollar P&L on raw prices, indicators on back-adjusted `*_adj` — never mix.
- Costs: $0.50/side MNQ micro + 1 tick slip.
