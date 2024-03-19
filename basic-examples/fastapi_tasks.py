from prefect import task
from prefect.task_server import serve


@task(log_prints=True)
def my_fastapi_task(name: str):
    print(f"Hello, {name}!")


if __name__ == "__main__":
    # if on 2.16.4 or older add the following line
    # from fastapi_tasks import my_fastapi_task

    serve(my_fastapi_task)
