# Phase 15 Scalping — Cost Floor & Ambiguity (Task 0)

Computed on RTH 1m continuous bars. Round-trip = 2×(commission+exchange) + 2×slippage_ticks×tick×point_value.

## MNQ micro ($2/pt, tick 0.25)

| Metric | Value |
| --- | --- |
| Median 1m bar range | 9.0 pts ($18) |
| Round-trip cost (1 tick slip) | **$2.98** |
| Min stop for +EV @ 55% WR / 1R | **~$30 (15 pts)** |
| Recommended min stop | **≥15 pts ($30)** |

Ambiguity: stops ≪ 9 pts median bar range cause stop+target both hittable in one bar (pessimistic fills). Grids enforce **min_stop_points ≥ 10**.

## GC full-size ($100/pt, tick 0.10)

| Metric | Value |
| --- | --- |
| Median 1m bar range | 0.70 pts ($70) |
| Round-trip cost (1 tick slip) | **$28** |
| Min stop for +EV @ 55% WR / 1R | **~$280 (2.8 pts)** |
| Recommended min stop | **≥2.8 pts ($280)**; Lucid cap 3–5 pts ($300–500) |

GC scalps must clear ~$28/trade costs — structurally hostile vs MNQ. Cap `max_risk_points` at 3–5 for 50K/100K MLL.

## Implication

- MNQ: viable scalp bracket ≈ 15–40 pts stop, 1.0–1.5R target, holds of several 1m bars
- GC: only larger structure scalps (≈3–5 pts) clear cost floor; true tick-scalps are unprofitable after fees
