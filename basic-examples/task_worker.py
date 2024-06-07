from prefect import task
from prefect.task_worker import serve


@task
def my_background_task(name: str):
    print(f"Hello, {name}!")
    return f"Hello, {name}!"


if __name__ == "__main__":
    serve(my_background_task)
