"""Model for a transaction."""
from __future__ import annotations

import dataclasses
import datetime


def _current_date() -> str:
    """Return the current date as YYYY-MM-DD."""
    return datetime.datetime.now(tz=datetime.timezone.utc).strftime("%Y-%m-%d")


@dataclasses.dataclass(frozen=True)
class Transaction:
    """Model for a transaction."""

    tid: int
    amount: int
    description: str
    date: str = _current_date()
