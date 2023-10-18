from __future__ import annotations

import datetime
import decimal
import sqlite3
from typing import Annotated

import fastapi
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from . import _filters
from .transaction import Transaction
from .transactionstore import TransactionStore

# Setup TransactionStore
db = sqlite3.connect("transactions.db", check_same_thread=False)
transaction_store = TransactionStore(db)

# Setup API and templates
app = fastapi.FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
template = Jinja2Templates(directory="template")
_filters.apply_filters(template)

DEFAULT_TRANSACTION_RANGE = 7


def _get_valid_date(since: str | None, until: str | None) -> tuple[str, str]:
    now = datetime.datetime.now(tz=datetime.timezone.utc)
    default = DEFAULT_TRANSACTION_RANGE
    if not since:
        since = (now - datetime.timedelta(days=default)).strftime("%Y-%m-%d")

    if not until:
        until = now.strftime("%Y-%m-%d")

    return since, until


@app.get("/")
def index(request: fastapi.Request) -> fastapi.Response:
    return template.TemplateResponse("index.html", {"request": request})


@app.get("/favicon.ico", include_in_schema=False)
def favicon() -> fastapi.Response:
    return fastapi.responses.FileResponse("static/img/favicon.ico")


@app.get("/transactions")
def transactions(
    request: fastapi.Request,
    date_since: str | None = None,
    date_until: str | None = None,
) -> fastapi.Response:
    """Page view for transactions."""
    date_since, date_until = _get_valid_date(date_since, date_until)
    empty_transaction = Transaction(0, 0, "", date_until)
    context = {
        "request": request,
        "date_since": date_since,
        "date_until": date_until,
        "transactions": transaction_store.get(date_since, date_until),
        "total_amount": transaction_store.get_total(date_since, date_until),
        "total_displayed": transaction_store.get_count(date_since, date_until),
        "total_count": transaction_store.get_count_all(),
        "transaction": empty_transaction,
    }
    new_url = f"/transactions?date_since={date_since}&date_until={date_until}"
    headers = {
        "HX-Push-Url": new_url,
        "HX-Replace-Url": new_url,
    }

    return template.TemplateResponse("transaction/index.html", context, headers=headers)


@app.get("/transaction/table")
def transaction_table(
    request: fastapi.Request,
    date_since: str | None = None,
    date_until: str | None = None,
) -> fastapi.Response:
    """
    Return partial HTML for transactions between `since` and `until`.

    if `since` is None, default 90 days ago
    if `until` is None, default now
    """
    date_since, date_until = _get_valid_date(date_since, date_until)
    context = {
        "request": request,
        "transactions": transaction_store.get(date_since, date_until),
        "date_since": date_since,
        "date_until": date_until,
    }
    new_url = f"/transactions?date_since={date_since}&date_until={date_until}"
    headers = {
        "HX-Push-Url": new_url,
        "HX-Replace-Url": new_url,
    }

    return template.TemplateResponse(
        name="transaction/partial/table.html",
        context=context,
        headers=headers,
    )


@app.get("/transaction/amounttotal")
def amount_total(
    request: fastapi.Request,
    date_since: str | None = None,
    date_until: str | None = None,
) -> fastapi.Response:
    """
    Return partial HTML total amount between `since` and `until`.

    if `since` is None, default 90 days ago
    if `until` is None, default now
    """
    date_since, date_until = _get_valid_date(date_since, date_until)
    context = {
        "request": request,
        "total_amount": transaction_store.get_total(date_since, date_until),
    }

    return template.TemplateResponse("transaction/partial/amounttotal.html", context)


@app.get("/transaction/rowtotal")
def transaction_count(
    request: fastapi.Request,
    date_since: str | None = None,
    date_until: str | None = None,
) -> fastapi.Response:
    """
    Return partial HTML total number of transactions between `since` and `until`.

    if `since` is None, default 90 days ago
    if `until` is None, default now
    """
    date_since, date_until = _get_valid_date(date_since, date_until)
    context = {
        "request": request,
        "total_displayed": transaction_store.get_count(date_since, date_until),
        "total_count": transaction_store.get_count_all(),
    }

    return template.TemplateResponse("transaction/partial/rowtotal.html", context)


@app.get("/transaction/{transaction_id}")
def transaction(
    request: fastapi.Request,
    transaction_id: int,
) -> fastapi.Response:
    """
    Return partial HTML for a single transaction.
    """
    context = {
        "request": request,
        "transaction": transaction_store.get_by_id(transaction_id),
    }

    return template.TemplateResponse("transaction/partial/row.html", context)


@app.get("/transaction/{transaction_id}/edit")
def edit_transaction(request: fastapi.Request, transaction_id: int) -> fastapi.Response:
    """
    Return partial HTML for editing a single transaction.
    """
    row = transaction_store.get_by_id(transaction_id)

    context = {
        "request": request,
        "transaction": row,
    }

    return template.TemplateResponse("transaction/partial/row_edit.html", context)


@app.put("/transaction/{transaction_id}")
def update_transaction(
    request: fastapi.Request,
    transaction_id: int,
    date_time: Annotated[str, fastapi.Form()],
    description: Annotated[str, fastapi.Form()],
    amount: Annotated[str, fastapi.Form()],
) -> fastapi.Response:
    """
    Update a single transaction.
    """
    if not date_time:
        date_time = datetime.datetime.now(tz=datetime.timezone.utc).strftime("%Y-%m-%d")

    try:
        _amount = int(decimal.Decimal(amount) * 100)
    except ValueError:
        _amount = 0

    transaction = Transaction(transaction_id, _amount, description, date_time)

    transaction_store.update(transaction)

    context = {
        "request": request,
        "transaction": transaction,
    }
    headers = {"HX-Trigger": "tableUpdate"}

    return template.TemplateResponse(
        name="transaction/partial/row.html",
        context=context,
        headers=headers,
    )


@app.delete("/transaction/{transaction_id}")
def delete_transaction(
    request: fastapi.Request, transaction_id: int
) -> fastapi.Response:
    """
    Delete a single transaction.
    """
    transaction_store.delete(transaction_id)
    headers = {"HX-Trigger": "tableUpdate"}

    return fastapi.Response(status_code=200, headers=headers)


@app.post("/transaction")
def create_transaction(
    request: fastapi.Request,
    date_time: Annotated[str, fastapi.Form()],
    description: Annotated[str, fastapi.Form()],
    amount: Annotated[str, fastapi.Form()],
) -> fastapi.Response:
    """
    Create a transaction.
    """
    if not date_time:
        date_time = datetime.datetime.now(tz=datetime.timezone.utc).strftime("%Y-%m-%d")

    try:
        _amount = int(decimal.Decimal(amount) * 100)
    except ValueError:
        _amount = 0

    transaction = Transaction(0, _amount, description, date_time)

    transaction_store.add(transaction)

    context = {
        "request": request,
        "transaction": transaction,
    }
    headers = {"HX-Trigger": "tableUpdate"}

    return template.TemplateResponse(
        name="transaction/partial/newrow.html",
        context=context,
        headers=headers,
    )
