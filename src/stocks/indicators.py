"""Technical indicators on a price Series. All return same-length Series."""
from __future__ import annotations

import numpy as np
import pandas as pd


def sma(price: pd.Series, window: int) -> pd.Series:
    return price.rolling(window=window, min_periods=window).mean()


def ema(price: pd.Series, span: int) -> pd.Series:
    return price.ewm(span=span, adjust=False).mean()


def rsi(price: pd.Series, window: int = 14) -> pd.Series:
    """Relative Strength Index (Wilder's smoothing). Values in [0, 100]."""
    delta = price.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    # Wilder's smoothing == EMA with alpha=1/window
    avg_gain = gain.ewm(alpha=1 / window, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / window, adjust=False).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    out = 100.0 - (100.0 / (1.0 + rs))
    return out.fillna(50.0)


def macd(
    price: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9
) -> pd.DataFrame:
    """MACD line, signal line, and histogram."""
    macd_line = ema(price, fast) - ema(price, slow)
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    hist = macd_line - signal_line
    return pd.DataFrame({"macd": macd_line, "signal": signal_line, "hist": hist})


def bollinger(
    price: pd.Series, window: int = 20, num_std: float = 2.0
) -> pd.DataFrame:
    mid = sma(price, window)
    std = price.rolling(window=window, min_periods=window).std()
    return pd.DataFrame(
        {"mid": mid, "upper": mid + num_std * std, "lower": mid - num_std * std}
    )
