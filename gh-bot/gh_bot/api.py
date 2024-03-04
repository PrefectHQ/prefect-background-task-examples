from contextlib import asynccontextmanager

from devtools import debug
from fastapi import FastAPI, Request
from gh_util.types import GitHubWebhookEvent
from rich.console import Console
from prefect.settings import get_current_settings
from .tasks import process_event

console = Console(log_time=False)

@asynccontextmanager
async def lifespan(app: FastAPI):
    console.log("👾 welcome to the app 👾")
    try:
        yield
    finally:
        console.log("👾 goodbye 👾")

app = FastAPI(lifespan=lifespan)

@app.post("/webhook")
async def webhook(request: Request) -> dict:
    console.log("📬 you've got one!")
    debug(get_current_settings())
    await process_event.submit(e := GitHubWebhookEvent.model_validate(await request.json()))
    debug(e)
    return {"message": "ok"}