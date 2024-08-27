from typing import Any

from prefect import task
from prefect.task_worker import serve


@task(log_prints=True)
def some_work(some_input: Any) -> None:
    print(f"doing some work with {some_input=!r}")


if __name__ == "__main__":
    # i could pass more like `serve(some_work, some_other_task)` or `serve(*list_of_tasks)`
    serve(some_work)
