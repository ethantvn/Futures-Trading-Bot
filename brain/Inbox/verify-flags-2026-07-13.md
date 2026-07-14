---
type: inbox
captured: 2026-07-13
source: Phase 21 re-scoring audit, step 6 (grep VERIFY across config/ + docs/)
---

# Remaining VERIFY-marked assumptions (logged, not chased)

Swept during the Phase 21 audit. None block the 25K path; all are dormant unless the linked decision reopens.

## Would matter only if [[tier-25k]] reopens
- `config/lucid_100k.yaml` — ALL 100K fees ($225 / $157.50 / $140) and rules are Phase 1 captures (2026-07-06), never dashboard-verified. Phase 14's tier comparison inherits this.
- `config/lucid_50k.yaml` — same status (costs, overnight rule).
- Phase 14 journey MC funded thresholds for 100K were "mirrored from 25K — VERIFY" (now partially superseded by [[lucid-25k-verified]], but 100K-specific payout numbers were never confirmed).

## Would matter only if [[gold-gc-mgc]] reopens (it shouldn't)
- `config/strategies_gc.yaml` — GC $2.50 + $1.50/side are placeholders.
- `config/strategies_mgc.yaml` — MGC $0.75 + $0.75/side are placeholders.

## Still-live small items (also tracked in [[lucid-25k-verified]])
- `allow_overnight` on 25K sim: strategy-level choice; firm rule never explicitly confirmed (moot — we flat 15:55).
- Exact auto-flatten timing (~10s before 16:45?).
- [[payout-mll-rule-check]] — the one that actually blocks work (funded sweep).

**Disposition:** file into Rules/ notes if any linked decision reopens; otherwise this is a tombstone.
