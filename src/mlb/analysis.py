"""Betting-math primitives: implied probability, edge, Kelly sizing."""
from __future__ import annotations


def implied_probability(american_odds: float) -> float:
    """Convert American odds to implied probability (0-1).

    Examples
    --------
    >>> round(implied_probability(-150), 4)
    0.6
    >>> round(implied_probability(+150), 4)
    0.4
    """
    if american_odds == 0:
        raise ValueError("American odds cannot be 0")
    if american_odds > 0:
        return 100.0 / (american_odds + 100.0)
    return -american_odds / (-american_odds + 100.0)


def decimal_odds(american_odds: float) -> float:
    """Convert American to decimal odds (profit multiplier including stake)."""
    if american_odds > 0:
        return 1.0 + american_odds / 100.0
    return 1.0 + 100.0 / -american_odds


def edge(model_prob: float, american_odds: float) -> float:
    """Expected-value edge per $1 stake.

    Returns a fraction: +0.05 means +5% EV. Negative means -EV.
    """
    if not 0.0 <= model_prob <= 1.0:
        raise ValueError("model_prob must be in [0, 1]")
    dec = decimal_odds(american_odds)
    return model_prob * (dec - 1.0) - (1.0 - model_prob)


def kelly_fraction(model_prob: float, american_odds: float) -> float:
    """Full-Kelly stake as fraction of bankroll. Negative means no bet.

    Kelly: f = (bp - q) / b  where b = decimal_odds - 1, p = model_prob, q = 1-p.
    """
    b = decimal_odds(american_odds) - 1.0
    if b <= 0:
        return 0.0
    p = model_prob
    q = 1.0 - p
    f = (b * p - q) / b
    return max(f, 0.0)
