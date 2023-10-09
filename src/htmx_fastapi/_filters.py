"""Custom Jinja2 filters."""
from __future__ import annotations

import datetime

from fastapi.templating import Jinja2Templates
from jinja2.runtime import Undefined


def _to_date(timestamp: int | Undefined, dayoffset: int = 0, tzoffset: int = 0) -> str:
    """
    Return a human-readable date in the format YYYY-MM-DD.

    If timestamp is not provided, the current time is used.

    Args:
        timestamp: A unix timestamp.
        dayoffset: The number of days to offset the timestamp by.
        tzoffset: The number of hours to offset the timestamp by.
    """
    if isinstance(timestamp, Undefined):
        now = datetime.datetime.now(tz=datetime.timezone.utc)
        timestamp = int((now - datetime.timedelta(days=dayoffset)).timestamp())

    _tzoffset = datetime.timedelta(hours=tzoffset)
    dt = datetime.datetime.fromtimestamp(int(timestamp), tz=datetime.timezone.utc)
    dt = dt + _tzoffset
    return dt.strftime("%Y-%m-%d")


def _to_dollars(amount: int) -> str:
    """Return a human-readable amount."""
    return f"{amount / 100:.2f}"


def apply_filters(template: Jinja2Templates) -> None:
    """Apply all defined filters to the template."""
    template.env.filters["to_date"] = _to_date
    template.env.filters["to_dollars"] = _to_dollars
