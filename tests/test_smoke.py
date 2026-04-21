"""Smoke tests: modules import cleanly and core pure-math functions work.

Network-dependent functions (pybaseball, yfinance, odds API) are exercised
in the notebooks rather than here so the test suite stays fast and offline.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest


def test_imports() -> None:
    from src import config  # noqa: F401
    from src.common import utils  # noqa: F401
    from src.mlb import analysis, data, odds  # noqa: F401
    from src.stocks import backtest, data as sdata, indicators  # noqa: F401


def test_implied_probability() -> None:
    from src.mlb.analysis import implied_probability

    assert implied_probability(-150) == pytest.approx(0.6, abs=1e-4)
    assert implied_probability(+150) == pytest.approx(0.4, abs=1e-4)
    assert implied_probability(+100) == pytest.approx(0.5, abs=1e-4)


def test_edge_and_kelly() -> None:
    from src.mlb.analysis import edge, kelly_fraction

    # Coin flip priced at +100: fair bet -> zero edge, zero Kelly
    assert edge(0.5, +100) == pytest.approx(0.0, abs=1e-9)
    assert kelly_fraction(0.5, +100) == pytest.approx(0.0, abs=1e-9)

    # We think it's 60/40 but market is +100: +EV, positive Kelly
    assert edge(0.6, +100) > 0
    assert kelly_fraction(0.6, +100) > 0

    # Negative-EV bet produces 0 Kelly (no short)
    assert kelly_fraction(0.4, +100) == 0.0


def test_indicators_shapes() -> None:
    from src.stocks.indicators import bollinger, ema, macd, rsi, sma

    idx = pd.date_range("2024-01-01", periods=200, freq="B")
    rng = np.random.default_rng(0)
    price = pd.Series(100 + rng.standard_normal(200).cumsum(), index=idx)

    assert len(sma(price, 20)) == 200
    assert len(ema(price, 20)) == 200

    r = rsi(price, 14)
    assert len(r) == 200
    assert r.between(0, 100).all()

    m = macd(price)
    assert set(m.columns) == {"macd", "signal", "hist"}
    assert len(m) == 200

    b = bollinger(price)
    assert set(b.columns) == {"mid", "upper", "lower"}


def test_backtest_sma_crossover() -> None:
    from src.stocks.backtest import run, sma_crossover_signals

    idx = pd.date_range("2022-01-01", periods=400, freq="B")
    rng = np.random.default_rng(42)
    # Trending series so the crossover actually trades
    price = pd.Series(100 + np.linspace(0, 30, 400) + rng.standard_normal(400), index=idx)

    signals = sma_crossover_signals(price, fast=10, slow=30)
    result = run(signals, price, fee_bps=1.0)

    assert len(result.equity) == 400
    assert len(result.returns) == 400
    assert result.stats["n_trades"] >= 1
    assert "cagr" in result.stats
    assert "sharpe" in result.stats
    assert result.stats["max_drawdown"] <= 0
