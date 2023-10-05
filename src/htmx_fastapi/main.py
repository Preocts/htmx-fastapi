from __future__ import annotations

import datetime
import sqlite3

import fastapi
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from . import _filters
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
