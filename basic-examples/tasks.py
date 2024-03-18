from prefect import task
from prefect.task_server import serve


@task
def my_b_task(name: str):
    print(f"Hello, {name}!")
    return f"Hello, {name}!"


if __name__ == "__main__":
    # following line is not necessary if on prefect 2.16.5 or newer
    from tasks import my_background_task

    serve(my_background_task)
