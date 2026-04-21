"""MLB team/player stats and schedule."""
from __future__ import annotations

from datetime import date as _date
from typing import Any

import pandas as pd

from src.common.utils import disk_cache, get_logger

log = get_logger(__name__)


@disk_cache("mlb_team_batting", ttl_seconds=24 * 3600)
def get_team_batting(season: int) -> pd.DataFrame:
    """Team-level batting stats for a given season.

    Wraps pybaseball.team_batting. Imported lazily so the module is usable
    even before `pip install` runs.
    """
    from pybaseball import team_batting  # type: ignore

    log.info("Fetching MLB team batting for %d", season)
    return team_batting(season)


@disk_cache("mlb_team_pitching", ttl_seconds=24 * 3600)
def get_team_pitching(season: int) -> pd.DataFrame:
    from pybaseball import team_pitching  # type: ignore

    log.info("Fetching MLB team pitching for %d", season)
    return team_pitching(season)


def get_team_stats(season: int) -> dict[str, pd.DataFrame]:
    """Convenience: both batting and pitching frames for a season."""
    return {
        "batting": get_team_batting(season),
        "pitching": get_team_pitching(season),
    }


def get_schedule(on_date: _date | None = None) -> list[dict[str, Any]]:
    """MLB schedule for a date (defaults to today). Uses MLB-StatsAPI."""
    import statsapi  # type: ignore

    d = (on_date or _date.today()).strftime("%Y-%m-%d")
    log.info("Fetching MLB schedule for %s", d)
    return statsapi.schedule(date=d)
