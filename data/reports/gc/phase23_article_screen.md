# Phase 23 Stage A — TradingSim article gold setups screen

Full period 2021-06-11 -> 2025-12-31 (2026 = frozen holdout, untouched).
Costs: GC $2.50+$1.50/side + 1 tick ($10) slip; MGC $0.75+$0.75/side + 1 tick ($1) slip.
Kill bar: best-combo expectancy <= $0 (GC) / < $2 (MGC), or < 1.5 t/mo.

| Family | Instrument | Best combo | Trades | t/mo | WR | PF | Exp $/trade | Net $ | Verdict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ema_stoch | GC | `{'touch_bars': 6, 'stop_atr': 1.5, 'target_r': 1.0, 'entry_start_minute': 480, 'daily_gate': True}` | 1028 | 18.9 | 48% | 0.91 | $-17.17 | $-17,650 | KILL |
| mom_rev_50 | GC | `{'body_atr_frac': 0.5, 'entry_start_minute': 480}` | 80 | 1.5 | 65% | 0.82 | $-45.10 | $-3,608 | KILL |
| round_magnet | GC | `{'mode': 'fade', 'round_step': 25.0, 'stop_atr': 1.0, 'target_r': 1.0, 'entry_start_minute': 480}` | 960 | 17.6 | 49% | 0.80 | $-32.13 | $-30,848 | KILL |
| ema_stoch | MGC | `{'touch_bars': 6, 'stop_atr': 1.5, 'target_r': 1.5, 'entry_start_minute': 480, 'daily_gate': True}` | 1011 | 18.6 | 39% | 0.84 | $-3.83 | $-3,876 | KILL |
| mom_rev_50 | MGC | `{'body_atr_frac': 0.8, 'entry_start_minute': 480}` | 23 | 0.5 | 48% | 0.31 | $-31.09 | $-715 | KILL |
| round_magnet | MGC | `{'mode': 'fade', 'round_step': 25.0, 'stop_atr': 1.5, 'target_r': 1.0, 'entry_start_minute': 480}` | 937 | 17.2 | 48% | 0.82 | $-4.01 | $-3,760 | KILL |

## Notes
- Article #1 (yen 6J correlation) untestable: no yen futures data in repo.
- Best-combo selection is in-sample by construction (screen only); any
  survivor must clear WF 18m/6m + MC + frozen 2026 holdout in Stage B
  before being called anything.
- 'Highest odds of winning' is judged by expectancy, not win rate.
