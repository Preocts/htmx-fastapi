"""Model for a transaction."""
from __future__ import annotations

import dataclasses
import datetime


def _current_timestamp() -> int:
    """Return the current timestamp."""
    return int(datetime.datetime.now(datetime.timezone.utc).timestamp())


@dataclasses.dataclass(frozen=True)
class Transaction:
    """Model for a transaction."""

    tid: int
    amount: int
    description: str
    timestamp: int = _current_timestamp()
