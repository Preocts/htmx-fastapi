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


@app.get("/")
def index(request: fastapi.Request) -> fastapi.Response:
    return template.TemplateResponse("index.html", {"request": request})


@app.get("/transactions")
def transactions(
    request: fastapi.Request,
    since: int | None = None,
    until: int | None = None,
) -> fastapi.Response:
    """
    Return partial HTML for transactions between `since` and `until`.

    if `since` is None, default one year ago
    if `until` is None, default now
    """
    now = datetime.datetime.now(tz=datetime.timezone.utc)
    if not since:
        since = int((now - datetime.timedelta(days=365)).timestamp())
    if not until:
        until = int(now.timestamp())

    context = {
        "request": request,
        "transactions": transaction_store.get(since, until),
    }

    return template.TemplateResponse("partial/transactions.html", context)


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

    return template.TemplateResponse("partial/transaction_row.html", context)


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

    return template.TemplateResponse("partial/transaction_form.html", context)


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
    try:
        timestamp = int(datetime.datetime.strptime(date_time, "%Y-%m-%d").timestamp())
    except ValueError:
        timestamp = int(datetime.datetime.now(tz=datetime.timezone.utc).timestamp())

    try:
        _amount = int(decimal.Decimal(amount) * 100)
    except ValueError:
        _amount = 0

    transaction = Transaction(transaction_id, _amount, description, timestamp)

    transaction_store.update(transaction)

    context = {
        "request": request,
        "transaction": transaction,
    }

    return template.TemplateResponse("partial/transaction_row.html", context)


@app.delete("/transaction/{transaction_id}")
def delete_transaction(
    request: fastapi.Request, transaction_id: int
) -> fastapi.Response:
    """
    Delete a single transaction.
    """
    transaction_store.delete(transaction_id)

    return fastapi.Response(status_code=200)


# @app.post("/transaction")
# def create_transaction(
#     request: fastapi.Request,
#     date_time: str,
#     description: str,
#     amount: int,
# ) -> fastapi.Response:
#     """
#     Create a transaction.
#     """
#     try:
#         timestamp = int(datetime.datetime.fromisoformat(date_time).timestamp())
#     except ValueError:
#         timestamp = int(datetime.datetime.now(tz=datetime.timezone.utc).timestamp())

#     transaction = Transaction(0, amount, description, timestamp)

#     transaction_store.add(transaction)

#     context = {
#         "request": request,
#         "transaction": transaction,
#     }

#     return template.TemplateResponse("partial/transaction_row.html", context)
