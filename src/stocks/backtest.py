"""Simple vectorized long/flat backtester.

Signals are in {0, 1} (flat / long). We trade on the next bar's open-ish by
shifting positions forward one bar, so a signal generated on day t drives
returns on day t+1. Returns an equity curve and summary stats.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass
class BacktestResult:
    equity: pd.Series            # cumulative equity (starts at 1.0)
    returns: pd.Series           # per-bar strategy return
    stats: dict[str, float]      # CAGR, Sharpe, MaxDD, hit_rate, n_trades


def _annualization_factor(index: pd.DatetimeIndex) -> float:
    """Guess bars-per-year from the index spacing (daily -> ~252, weekly -> 52)."""
    if len(index) < 2:
        return 252.0
    deltas = np.diff(index.values.astype("datetime64[s]").astype(np.int64))
    med_seconds = float(np.median(deltas))
    bars_per_year = (365.25 * 24 * 3600) / max(med_seconds, 1.0)
    # Snap to common cadences
    for candidate in (252.0, 52.0, 12.0, 365.0):
        if abs(bars_per_year - candidate) / candidate < 0.25:
            return candidate
    return bars_per_year


def run(signals: pd.Series, prices: pd.Series, fee_bps: float = 1.0) -> BacktestResult:
    """Long/flat backtest.

    signals : 0 or 1 per bar (1 = fully long next bar)
    prices  : close price, same index as signals
    fee_bps : one-way transaction cost in basis points (1 bp = 0.01%)
    """
    if not signals.index.equals(prices.index):
        signals = signals.reindex(prices.index).fillna(0)
    signals = signals.clip(0, 1).astype(float)

    # Position driving today's return was decided yesterday
    position = signals.shift(1).fillna(0)

    bar_returns = prices.pct_change().fillna(0)
    trades = position.diff().abs().fillna(position.iloc[0])
    fee = trades * (fee_bps / 10_000.0)
    strat_returns = position * bar_returns - fee

    equity = (1.0 + strat_returns).cumprod()

    af = _annualization_factor(prices.index)
    total_return = float(equity.iloc[-1] - 1.0) if len(equity) else 0.0
    years = len(equity) / af if af > 0 else 1.0
    cagr = (1.0 + total_return) ** (1.0 / max(years, 1e-9)) - 1.0 if years > 0 else 0.0
    sharpe = (
        float(strat_returns.mean() / strat_returns.std() * np.sqrt(af))
        if strat_returns.std() > 0
        else 0.0
    )
    running_max = equity.cummax()
    drawdown = equity / running_max - 1.0
    max_dd = float(drawdown.min()) if len(drawdown) else 0.0

    n_trades = int(trades.gt(0).sum())
    # Hit rate: fraction of trading days with positive strat return (when in market)
    in_market = strat_returns[position > 0]
    hit_rate = float((in_market > 0).mean()) if len(in_market) else 0.0

    stats = {
        "total_return": total_return,
        "cagr": cagr,
        "sharpe": sharpe,
        "max_drawdown": max_dd,
        "n_trades": float(n_trades),
        "hit_rate": hit_rate,
        "bars_per_year": af,
    }
    return BacktestResult(equity=equity, returns=strat_returns, stats=stats)


def sma_crossover_signals(
    prices: pd.Series, fast: int = 20, slow: int = 50
) -> pd.Series:
    """Convenience: generate long-when-fast-above-slow signals."""
    from src.stocks.indicators import sma

    return (sma(prices, fast) > sma(prices, slow)).astype(int)
