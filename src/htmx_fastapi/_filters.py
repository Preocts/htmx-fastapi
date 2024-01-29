"""Custom Jinja2 filters."""

from __future__ import annotations

from fastapi.templating import Jinja2Templates


def _to_dollars(amount: int) -> str:
    """Return a human-readable amount."""
    if amount:
        return f"{amount / 100:.2f}"
    else:
        return "0.00"


def apply_filters(template: Jinja2Templates) -> None:
    """Apply all defined filters to the template."""
    template.env.filters["to_dollars"] = _to_dollars
