"""Custom Jinja2 filters."""
from __future__ import annotations

import datetime

from fastapi.templating import Jinja2Templates


def _readable_timestamp(timestamp: int, tzoffset: int = 0) -> str:
    """Return a human-readable timestamp."""
    _tzoffset = datetime.timedelta(hours=tzoffset)
    dt = datetime.datetime.fromtimestamp(timestamp, tz=datetime.timezone.utc)
    dt = dt + _tzoffset
    return dt.strftime("%Y-%m-%d")


def apply_filters(template: Jinja2Templates) -> None:
    """Apply all defined filters to the template."""
    template.env.filters["readable_timestamp"] = _readable_timestamp
