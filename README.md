# Yasser Analytics

Analysis & research toolkit for **MLB betting** and **US equities trading**.

**Important:** this is a decision-support tool. It fetches data, computes stats,
and surfaces signals — but a human always makes and places the actual bet or
trade. No auto-execution of wagers or financial transactions.

## Quickstart

```bash
cd ~/Desktop/yasser-analytics
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Copy the env template and (optionally) fill in an Odds API key:

```bash
cp .env.example .env
# then edit .env and set ODDS_API_KEY=...  (free tier at https://the-odds-api.com)
```

Run the smoke test:

```bash
pytest tests/test_smoke.py
```

## What's in here

```
src/
  mlb/         # MLB data, sportsbook odds, betting-math primitives
  stocks/      # OHLCV data, technical indicators, vectorized backtester
  common/      # shared helpers
notebooks/
  mlb_explore.ipynb      # pull team stats, compute edge vs a market line
  stocks_explore.ipynb   # pull prices, compute RSI/SMA, backtest a strategy
tests/
  test_smoke.py          # imports + basic shape checks
```

## Core functions

### MLB (`src/mlb/`)
- `data.get_team_stats(season)` — team batting + pitching from pybaseball
- `data.get_schedule(date)` — today's games via MLB-StatsAPI
- `odds.get_mlb_odds()` — sportsbook moneylines (needs `ODDS_API_KEY`)
- `analysis.implied_probability(american_odds)`
- `analysis.edge(model_prob, american_odds)`
- `analysis.kelly_fraction(edge_frac, american_odds)`

### Stocks (`src/stocks/`)
- `data.get_history(ticker, period)` — OHLCV via yfinance
- `indicators.sma / ema / rsi / macd / bollinger`
- `backtest.run(signals, prices)` — long/flat vectorized backtest with equity curve + stats

## Data sources

| Source | Covers | Key? |
|---|---|---|
| pybaseball | MLB stats, Statcast | No |
| MLB-StatsAPI | Schedule, live games | No |
| yfinance | US equity OHLCV | No |
| The Odds API | MLB sportsbook lines | Yes (free tier) |

## Not in v0

Live streaming, ML models, web dashboard, options/crypto/other sports,
broker/sportsbook execution. Easy to add later on top of this foundation.
