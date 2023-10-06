"""Custom Jinja2 filters."""
from __future__ import annotations

import datetime

from fastapi.templating import Jinja2Templates


def _to_date(timestamp: int, tzoffset: int = 0) -> str:
    """Return a human-readable timestamp."""
    _tzoffset = datetime.timedelta(hours=tzoffset)
    dt = datetime.datetime.fromtimestamp(timestamp, tz=datetime.timezone.utc)
    dt = dt + _tzoffset
    return dt.strftime("%Y-%m-%d")


def _to_dollars(amount: int) -> str:
    """Return a human-readable amount."""
    return f"{amount / 100:.2f}"


def apply_filters(template: Jinja2Templates) -> None:
    """Apply all defined filters to the template."""
    template.env.filters["to_date"] = _to_date
    template.env.filters["to_dollars"] = _to_dollars
