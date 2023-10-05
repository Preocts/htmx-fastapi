from __future__ import annotations

import fastapi
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = fastapi.FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
template = Jinja2Templates(directory="template")


@app.get("/")
def index(request: fastapi.Request) -> fastapi.Response:
    return template.TemplateResponse("index.html", {"request": request})
