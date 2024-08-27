import random
import sys

from prefect import get_run_logger, task
from prefect.task_worker import serve


@task(retries=10, retry_delay_seconds=1)
async def ping(sequence: int) -> tuple[str, int]:
    #
    # Agent of chaos #1: 20% of the time, the task itself will fail
    #
    if random.random() < 0.2:
        raise ValueError("woops")

    return ("pong", sequence)


@task
async def crash_me(exit_code: int):
    #
    # Agent of chaos #2: occasionally, the task server will crash from within
    #
    get_run_logger().warning("Crashing the task server with %s!", exit_code)
    sys.exit(exit_code)


if __name__ == "__main__":
    serve(ping, crash_me)
