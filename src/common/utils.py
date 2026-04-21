"""Shared utilities: logging setup and a tiny on-disk cache."""
from __future__ import annotations

import hashlib
import json
import logging
import pickle
import time
from pathlib import Path
from typing import Any, Callable

from src.config import PROJECT_ROOT

CACHE_DIR = PROJECT_ROOT / "data" / "cache"


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        h = logging.StreamHandler()
        h.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))
        logger.addHandler(h)
        logger.setLevel(logging.INFO)
    return logger


def _cache_key(name: str, args: tuple, kwargs: dict) -> str:
    payload = json.dumps({"args": args, "kwargs": kwargs}, sort_keys=True, default=str)
    digest = hashlib.sha1(payload.encode()).hexdigest()[:16]
    return f"{name}_{digest}.pkl"


def disk_cache(name: str, ttl_seconds: int = 3600) -> Callable:
    """Decorator: cache return value to disk for `ttl_seconds`.

    Use for slow network calls (e.g. pybaseball). Cache invalidates after TTL.
    """
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    def wrapper(fn: Callable) -> Callable:
        def inner(*args: Any, **kwargs: Any) -> Any:
            path = CACHE_DIR / _cache_key(name, args, kwargs)
            if path.exists() and (time.time() - path.stat().st_mtime) < ttl_seconds:
                with path.open("rb") as f:
                    return pickle.load(f)
            result = fn(*args, **kwargs)
            with path.open("wb") as f:
                pickle.dump(result, f)
            return result

        return inner

    return wrapper
