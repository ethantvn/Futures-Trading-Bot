You are acting as a quantitative futures researcher and senior Python engineer.

Build a research and backtesting project for MNQ futures strategies designed to maximize the probability of passing a Lucid Flex evaluation while minimizing the probability of breaching the account’s drawdown rules.

The system must support both 25K and 50K Lucid Flex evaluation accounts. Do not hard-code the rules. Create a configuration file where I can enter:

* Starting balance
* Profit target
* Maximum drawdown
* Daily loss limit, if applicable
* End-of-day or intraday trailing drawdown method
* Consistency rule
* Minimum trading days
* Maximum contracts
* Commission per side
* Exchange and platform fees
* Slippage
* Evaluation reset cost
* Monthly automation cost

Before using any Lucid rules, research the current official Lucid documentation and clearly cite the source and date checked. Do not rely on third-party summaries.

## Primary objective

Estimate the probability that each strategy can:

1. Pass the evaluation within 10 trading days
2. Pass within 15 trading days
3. Pass within 20 trading days
4. Avoid breaching the drawdown limit
5. Remain viable after commissions, fees, and realistic slippage

Do not optimize only for total profit, win rate, or a two-week passing result.

The main ranking metric should be:

* Probability of passing before failure

Secondary metrics should include:

* Median number of trading days required to pass
* Evaluation failure probability
* Expected profit per evaluation attempt
* Expected cost per successful funded account
* Maximum drawdown
* Profit factor
* Sharpe ratio
* Sortino ratio
* Win rate
* Average win
* Average loss
* Expectancy per trade
* Maximum consecutive losses
* Time in market
* Trades per day
* Sensitivity to slippage
* Sensitivity to commissions
* Consistency-rule compliance

## Data requirements

I currently have MNQ historical data from Databento.

First inspect the available data and report:

* Dataset schema
* Symbol format
* Contract months covered
* Date range
* Bar or tick resolution
* Time zone
* Whether trades, quotes, bid/ask, or OHLCV are available
* Missing periods
* Duplicate rows
* Bad ticks
* Session gaps
* Rollover behavior
* Whether the data is adjusted or unadjusted

Create a robust data pipeline that:

* Normalizes timestamps to America/New_York
* Preserves the original exchange timestamp
* Separates regular trading hours and overnight sessions
* Handles futures contract rollover
* Supports both individual contracts and continuous contracts
* Avoids artificial price jumps around rollover
* Creates 1-minute, 3-minute, 5-minute, 15-minute, and 30-minute bars
* Prevents look-ahead bias
* Prevents duplicate candles
* Validates OHLC relationships
* Produces a data-quality report

## TradingView alignment

I want the backtest results to align as closely as possible with TradingView.

Research and document the likely causes of differences between Databento and TradingView, including:

* Exchange time zone
* Session templates
* Extended-hours inclusion
* Continuous-contract construction
* Rollover dates
* Back adjustment
* Front-month selection
* Bar aggregation rules
* Missing ticks
* Bid/ask versus last-trade data
* Historical data vendor differences
* TradingView symbol selection, such as MNQ1! versus a dated contract
* Candle-close timing
* Daylight-saving-time handling

Build a TradingView comparison tool where I can export OHLCV candles from TradingView and compare them against the generated Databento candles.

The comparison should report:

* Timestamp mismatches
* Open differences
* High differences
* Low differences
* Close differences
* Volume differences
* Missing candles
* Percentage of matching candles
* Maximum price difference
* Average price difference

Do not claim exact TradingView matching unless the comparison proves it.

## Strategy research

Research and implement multiple strategy families instead of searching for one “perfect” strategy.

Include at least:

1. Opening-range breakout
2. Initial-balance breakout
3. VWAP pullback
4. VWAP mean reversion
5. Trend-following using EMA alignment
6. ATR trailing-stop strategy
7. UT Bot-inspired ATR strategy
8. Bollinger Band mean reversion
9. Bollinger Band squeeze breakout
10. Donchian-channel breakout
11. Previous-day high and low breakout
12. Overnight high and low breakout
13. Momentum continuation after market open
14. Failed breakout reversal
15. Relative-volume breakout
16. Time-of-day trend strategy
17. Higher-timeframe trend with lower-timeframe entry
18. RSI or stochastic mean reversion with trend filtering
19. ADX trend filter combined with breakout entries
20. Regime-switching strategy that distinguishes trending and ranging markets

For each strategy:

* Explain the market hypothesis
* Define exact entry conditions
* Define exact exit conditions
* Define stop-loss logic
* Define profit-target logic
* Define time-based exits
* Define no-trade periods
* Define session restrictions
* Define news-event handling
* Define maximum trades per day
* Define daily profit lock
* Define daily personal stop-out
* Define contract sizing
* Identify parameters that could cause overfitting

Do not combine many indicators without a defensible reason.

## Evaluation-focused risk management

Test risk-management systems specifically designed for prop-firm evaluations:

* Fixed dollar risk per trade
* Fixed percentage of drawdown allowance
* Volatility-adjusted position sizing
* One-contract baseline
* Scaling only after accumulating a profit buffer
* Daily personal stop-out
* Maximum consecutive-loss cutoff
* Daily profit lock
* Maximum trades per session
* No trading after reaching a daily target
* Reduced size near the drawdown threshold
* Reduced size after a losing streak
* No overnight holding
* Avoiding high-impact economic releases
* Consistency-rule-aware daily profit limits

For each account size, calculate recommended:

* Starting contract size
* Maximum contract size
* Dollar risk per trade
* Maximum daily loss
* Maximum daily profit before stopping
* Required buffer before increasing size
* Maximum number of trades per day

The recommendations must be based on simulation results, not intuition.

## Backtesting standards

Use at least 3 to 5 years of MNQ data where available.

Split the data into:

* In-sample training period
* Validation period
* Out-of-sample test period
* Final untouched holdout period

Also perform:

* Anchored walk-forward testing
* Rolling walk-forward testing
* Monte Carlo trade-sequence simulation
* Bootstrap resampling
* Parameter sensitivity analysis
* Regime analysis
* Year-by-year analysis
* Month-by-month analysis
* Day-of-week analysis
* Time-of-day analysis
* Slippage stress testing
* Commission stress testing
* Delayed-entry testing
* Missed-trade testing
* Random signal-removal testing

Use realistic execution assumptions:

* Entries cannot occur before the signal is confirmed
* Market orders receive configurable slippage
* Stop orders can fill worse than the stop price
* Limit orders are not assumed filled merely because price touched them
* No same-bar perfect entry and exit unless tick data confirms the sequence
* Include commissions and fees on every trade
* Account for contract rollover
* Account for market holidays and shortened sessions

Reject any strategy that performs well only under one exact parameter combination.

## Pass-probability simulation

Build an evaluation simulator that replays trading days and checks the Lucid rules after every trade and every session.

For each strategy and parameter set, run at least 10,000 Monte Carlo evaluation attempts.

Report:

* Pass rate
* Failure rate
* Median days to pass
* 25th and 75th percentile days to pass
* Percentage passing within 10 days
* Percentage passing within 15 days
* Percentage passing within 20 days
* Percentage failing from drawdown
* Percentage failing from consistency rules
* Average profit before failure
* Average remaining drawdown at pass
* Expected number of resets before passing
* Expected total cost before passing

Run these separately for:

* 25K Lucid Flex
* 50K Lucid Flex
* One MNQ contract
* Two MNQ contracts
* Three MNQ contracts
* Any other permitted sizing levels

## Anti-overfitting requirements

Do not select a strategy merely because it has the highest historical return.

A strategy should only be considered viable if:

* It remains profitable out of sample
* It remains profitable after higher slippage
* It performs across multiple years
* It works across nearby parameter values
* It is not dependent on one month or one market event
* Its Monte Carlo pass rate remains acceptable
* Its drawdown fits comfortably within evaluation limits
* Its results are not driven by a small number of trades

Clearly label any result that may be overfit.

## Free and alternative data research

Research legitimate sources of historical MNQ or NQ futures data besides Databento.

For each source, report:

* Cost
* Free access limits
* Historical depth
* Tick, second, or minute availability
* Bid/ask availability
* Licensing restrictions
* API access
* Download limits
* Whether automated downloading is permitted
* Whether it is suitable for commercial use
* Expected alignment with TradingView

Investigate sources such as:

* CME DataMine
* Interactive Brokers
* Tradovate
* NinjaTrader
* Sierra Chart
* QuantConnect
* Polygon
* Alpaca, if futures data is available
* Yahoo Finance, while noting its limitations
* Kaggle datasets
* Dukascopy, if applicable
* FirstRate Data
* Barchart
* Nasdaq Data Link
* Other legitimate futures data vendors

Do not scrape websites in violation of their terms of service. Prefer official APIs, licensed downloads, or user-provided exports.

## Claude Code project setup

Create a clean Python project with this structure:

mnq-evaluation-research/
├── README.md
├── pyproject.toml
├── .env.example
├── config/
│   ├── lucid_25k.yaml
│   ├── lucid_50k.yaml
│   ├── data.yaml
│   └── strategies.yaml
├── data/
│   ├── raw/
│   ├── processed/
│   ├── tradingview_exports/
│   └── reports/
├── src/
│   ├── data/
│   │   ├── databento_loader.py
│   │   ├── validation.py
│   │   ├── rollover.py
│   │   ├── resampling.py
│   │   └── tradingview_compare.py
│   ├── strategies/
│   │   ├── base.py
│   │   ├── opening_range.py
│   │   ├── vwap.py
│   │   ├── trend.py
│   │   ├── mean_reversion.py
│   │   └── breakout.py
│   ├── backtest/
│   │   ├── engine.py
│   │   ├── execution.py
│   │   ├── fees.py
│   │   └── metrics.py
│   ├── evaluation/
│   │   ├── lucid_rules.py
│   │   ├── simulator.py
│   │   └── monte_carlo.py
│   ├── optimization/
│   │   ├── walk_forward.py
│   │   ├── sensitivity.py
│   │   └── ranking.py
│   └── reporting/
│       ├── tables.py
│       ├── charts.py
│       └── html_report.py
├── tests/
├── scripts/
│   ├── inspect_data.py
│   ├── build_bars.py
│   ├── compare_tradingview.py
│   ├── run_backtest.py
│   ├── run_walk_forward.py
│   └── run_evaluation_simulation.py
└── notebooks/
└── exploratory_analysis.ipynb

Use:

* Python 3.12
* pandas or Polars
* NumPy
* DuckDB or Parquet
* vectorbt, backtesting.py, or a custom event-driven engine when appropriate
* Optuna only after a valid baseline is established
* pytest
* type hints
* structured logging
* reproducible random seeds

Do not introduce a database or cloud service unless necessary.

## MCP and external-tool research

Research whether any MCP servers would be useful for this project.

Consider:

* Filesystem MCP
* GitHub MCP
* PostgreSQL or DuckDB MCP
* Browser or Playwright MCP for official documentation research
* Fetch MCP for API documentation
* Jupyter or Python execution MCP
* Databento-specific integrations, if available

For each recommended MCP, explain:

* What it adds
* Whether it is necessary
* Security risks
* Installation steps
* Required credentials
* Whether Claude Code can complete the project without it

Do not recommend an MCP merely because it exists.

## Required workflow

Complete the work in phases.

### Phase 1: Research and plan

Before writing strategy code:

1. Inspect the repository
2. Inspect the Databento data
3. Verify current Lucid Flex rules
4. Write a data-quality report
5. Write a TradingView-alignment report
6. Write a strategy-research plan
7. Propose the backtesting architecture
8. Identify unresolved assumptions

Stop after Phase 1 and show me the findings before implementing the full system.

### Phase 2: Data pipeline

Build and test:

* Databento import
* Data validation
* Session handling
* Rollover handling
* Bar construction
* TradingView comparison

### Phase 3: Baseline strategies

Implement simple, interpretable strategies before combining indicators.

### Phase 4: Evaluation simulation

Add Lucid account-rule simulation and Monte Carlo pass-rate testing.

### Phase 5: Validation

Perform out-of-sample, walk-forward, sensitivity, and stress testing.

### Phase 6: Reporting

Produce:

* Strategy leaderboard
* Pass-rate comparison
* Risk-setting comparison
* 25K versus 50K comparison
* Recommended conservative configuration
* Recommended moderate configuration
* Reasons rejected strategies failed

## Final deliverables

Provide:

1. Working source code
2. Automated tests
3. Setup instructions
4. Data-quality report
5. TradingView-comparison report
6. Strategy-research report
7. Backtest report
8. Walk-forward report
9. Monte Carlo evaluation report
10. Ranked strategy table
11. Recommended 25K configuration
12. Recommended 50K configuration
13. Pine Script version of the final strategy
14. Instructions for validating the Pine Script in TradingView
15. A list of assumptions and limitations

Do not promise that any strategy will pass an evaluation. State results as historical and simulated probabilities.

Begin with Phase 1 only. Do not write the full implementation until the data and account rules have been validated.
