from __future__ import annotations

import random

import fastapi
from fastapi import Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

incremental = 0
highest = 0

app = fastapi.FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
template = Jinja2Templates(directory="template")


@app.get("/")
def index(request: fastapi.Request) -> fastapi.Response:
    return template.TemplateResponse("index.html", {"request": request})


@app.get("/increment")
def increment(request: Request) -> fastapi.Response:
    global incremental
    global highest

    random_number = random.randint(1, 100)
    if random_number < incremental:
        highest = max([incremental, highest])
        incremental = 0
    else:
        incremental += 1

    return template.TemplateResponse(
        name="partial/increment.html",
        context={"request": request, "incremental": incremental, "highest": highest},
    )
