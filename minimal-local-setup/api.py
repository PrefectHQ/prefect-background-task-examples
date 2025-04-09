from typing import Any

from fastapi import FastAPI
from pydantic import BaseModel

from tasks import some_work

app = FastAPI()


class SomeInput(BaseModel):
    value: Any


@app.post("/")
async def do_work(some_input: SomeInput):
    future = some_work.delay(some_input.value)
    return {"message": f"submitted task run {future.task_run_id!r}"}
