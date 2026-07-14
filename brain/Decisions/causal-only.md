---
type: decision
decided: 2026-07-12
status: locked
---

# Causal only — no lookahead, ever

Every feature must be computable at signal time. Enforced by no-lookahead tests. Standing audit trigger: **TradingView export diverging from the Python ledger** — that mismatch is how the [[overnight-fade]] 96% lookahead bug was caught after it had been promoted.

Rules: overnight = 18:00–09:30 ET only; vol refs use completed days only; VIX = prior close; holdout is touched once and never re-tuned.
