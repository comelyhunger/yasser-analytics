"""US equity OHLCV via yfinance."""
from __future__ import annotations

import pandas as pd

from src.common.utils import get_logger

log = get_logger(__name__)


def get_history(ticker: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
    """OHLCV history for `ticker`.

    period  : "1d","5d","1mo","3mo","6mo","1y","2y","5y","10y","ytd","max"
    interval: "1m","2m","5m","15m","30m","60m","90m","1h","1d","5d","1wk","1mo","3mo"
    """
    import yfinance as yf  # type: ignore

    log.info("Fetching %s %s/%s", ticker, period, interval)
    df = yf.Ticker(ticker).history(period=period, interval=interval, auto_adjust=True)
    if df.empty:
        raise ValueError(f"No data returned for {ticker}")
    df.index = pd.to_datetime(df.index)
    return df


def get_multiple(tickers: list[str], period: str = "1y") -> dict[str, pd.DataFrame]:
    return {t: get_history(t, period=period) for t in tickers}
