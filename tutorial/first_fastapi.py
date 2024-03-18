from fastapi import FastAPI
from prefect import task
from ff_prefect_task_server import my_fastapi_task

app = FastAPI()


@task
def my_b_task(name: str):
    print(f"Hello, {name}!")
    return f"Hello, {name}!"


@app.get("/task")
async def prefect_task():
    val = my_fastapi_task.submit(name="Marvin")
    return {"message": f"Prefect Task submitted: {val}"}
