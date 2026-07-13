# MNQ Evaluation Research

Research and backtesting project for MNQ (Micro E-mini Nasdaq-100) futures
strategies, designed to estimate the probability of passing a Lucid Flex
25K/50K evaluation without breaching its drawdown rules. See
`PROJECT_SPEC.md` for the full brief and `docs/PHASE_1_PLAN.md` for the
approved research plan.

## Setup

Requires Python 3.12 (a `uv`-managed interpreter works well):

```bash
uv venv --python 3.12 .venv
uv pip install --python .venv/bin/python -e ".[dev]"
```

Place the Databento batch export folder under `data/raw/` (path configured in
`config/data.yaml`).

## Pipeline

```bash
.venv/bin/python scripts/inspect_data.py        # raw export schema/coverage report
.venv/bin/python scripts/build_bars.py          # parquet bars, quality report, rollover, resampling
.venv/bin/python scripts/compare_tradingview.py # compare vs a TradingView export
.venv/bin/pytest                                # test suite
```

Outputs land in `data/processed/` (parquet) and `data/reports/` (markdown/JSON).

## Layout

- `config/` — data pipeline + Lucid Flex 25K/50K rule configs (nothing hard-coded)
- `src/data/` — loader, validation, rollover, resampling, TradingView comparison
- `scripts/` — pipeline entry points
- `tests/` — pytest suite (timezone/DST, rollover look-ahead safety, resampling, comparison)

## Conventions

- All bar timestamps are **bar-open**. Original exchange timestamps (UTC) are
  preserved in `ts_utc`; `ts_ny` is America/New_York.
- A trading date follows CME convention: the session opening 18:00 ET belongs
  to the **next** trading date.
- Continuous series carry both raw prices (for fills/P&L) and back-adjusted
  `*_adj` prices (for indicators). Never compute dollar P&L on adjusted prices.
