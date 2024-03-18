from prefect import task
from prefect.task_server import serve


@task(log_prints=True)
def my_fastapi_task(name: str):
    print(f"Hello, {name}!")


if __name__ == "__main__":
    serve(my_fastapi_task)
