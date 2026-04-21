"""Fetch MLB sportsbook odds from The Odds API (https://the-odds-api.com)."""
from __future__ import annotations

import pandas as pd
import requests

from src.config import ODDS_API_BASE, ODDS_API_KEY


class OddsAPIError(RuntimeError):
    pass


def get_mlb_odds(
    regions: str = "us",
    markets: str = "h2h",
    odds_format: str = "american",
) -> pd.DataFrame:
    """Return a tidy DataFrame: one row per (game, bookmaker, team, price).

    Requires ODDS_API_KEY in .env. `markets="h2h"` is moneyline; you can also
    pass "spreads" or "totals".
    """
    if not ODDS_API_KEY:
        raise OddsAPIError(
            "ODDS_API_KEY not set. Copy .env.example to .env and add a key "
            "from https://the-odds-api.com"
        )

    url = f"{ODDS_API_BASE}/sports/baseball_mlb/odds"
    params = {
        "apiKey": ODDS_API_KEY,
        "regions": regions,
        "markets": markets,
        "oddsFormat": odds_format,
    }
    resp = requests.get(url, params=params, timeout=15)
    if resp.status_code != 200:
        raise OddsAPIError(f"{resp.status_code}: {resp.text}")

    rows: list[dict] = []
    for game in resp.json():
        for book in game.get("bookmakers", []):
            for market in book.get("markets", []):
                for outcome in market.get("outcomes", []):
                    rows.append(
                        {
                            "game_id": game["id"],
                            "commence_time": game["commence_time"],
                            "home_team": game["home_team"],
                            "away_team": game["away_team"],
                            "bookmaker": book["key"],
                            "market": market["key"],
                            "team": outcome["name"],
                            "price": outcome["price"],
                            "point": outcome.get("point"),
                        }
                    )
    return pd.DataFrame(rows)
