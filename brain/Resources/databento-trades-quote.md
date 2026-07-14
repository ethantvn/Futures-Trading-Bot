---
type: resource
status: todo
---

# Databento trades-schema quote (Stage 0 of [[orderflow-delta-gate]])

## What to quote
- Dataset: **GLBX.MDP3**, schema: **`trades`** (has aggressor side flag)
- Symbols: **MNQ.FUT** and **NQ.FUT** (parent, all expirations — match existing bars order `data/raw/GLBX-20260630-99GU63VXQL`)
- Range: 2019-06-01 → present
- Batch download, zstd CSV or dbn

## Budget
**KILL if total > ~$300.** That's MBP-1 pricing and not justified before Stage 1 evidence exists.

## Notes
- Existing loader pipeline (`src/data/databento_loader.py`) handles GLBX batch exports; trades schema needs a small loader extension + delta aggregation to OR window.
- NQ flow may lead MNQ (big-contract participants) — that's why both.

## Public-pricing estimate (2026-07-13, Stage 0 partial)
- Databento's own blog example: ES `trades`, ~5 trading days ≈ **$2.17** → ~$0.43/day. Naive scale to 7 years (~1,750 days) ≈ **$760 for ES-class volume**; MNQ record counts are comparable-or-higher (huge retail flow), NQ lower.
- **Implication: full 2019–2026 MNQ+NQ trades likely lands ABOVE the $300 kill line.** Options before killing: (a) restrict requests to 09:25–10:05 ET windows (Databento prices by data pulled — time-sliced daily requests cut cost ~25×), (b) 2022→present only (~4 yrs, still ≥2 WF folds + holdout), (c) MNQ only.
- Exact number needs the account API key (free metadata call, no purchase): `Historical.metadata.get_cost(dataset="GLBX.MDP3", schema="trades", symbols=["MNQ.FUT","NQ.FUT"], stype_in="parent", start=..., end=...)`.
- $125 free credits on new team accounts may offset part.
