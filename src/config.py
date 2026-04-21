"""Central configuration: loads .env and exposes constants."""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

ODDS_API_KEY: str | None = os.getenv("ODDS_API_KEY") or None
BANKROLL: float = float(os.getenv("BANKROLL", "1000"))

ODDS_API_BASE = "https://api.the-odds-api.com/v4"
