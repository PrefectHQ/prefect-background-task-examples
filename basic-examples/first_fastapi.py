from fastapi import FastAPI
from prefect import task
from fastapi_tasks import my_fastapi_task

app = FastAPI()


@app.get("/")
def greet():
    print(f"Hello, world!")
    return f"Hello, world!"


@app.get("/task")
async def prefect_task():
    data = my_fastapi_task.submit(name="Trillian")
    return {"message": f"Prefect Task submitted: {data}"}
