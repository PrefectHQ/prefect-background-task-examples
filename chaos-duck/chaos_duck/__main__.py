import asyncio
import sys
import time
from collections import Counter
from uuid import UUID

from prefect.client.orchestration import get_client
from prefect.client.schemas import TaskRun
from prefect.client.schemas.filters import TaskRunFilter, TaskRunFilterId
from prefect.states import StateType

from . import chaos, tasks

FINAL_STATES = {StateType.COMPLETED, StateType.FAILED, StateType.CRASHED}


async def main(iterations: int):
    havoc = asyncio.create_task(chaos.wreak_havoc())

    start = time.monotonic()

    submission_failures = 0

    task_runs: dict[UUID, int] = {}
    for i in range(iterations):
        try:
            run: TaskRun = await tasks.ping.submit(i)
        except Exception as exc:
            print(f"Failed to submit task run {i}: {exc}")
            submission_failures += 1
            continue
        if (i + 1) % 10 == 0:
            if i == iterations - 1:
                submission_duration = time.monotonic() - start
                print(
                    "Submitted run", i + 1, "tasks in", submission_duration, "seconds"
                )
            else:
                print("Submitted run", i + 1, "tasks")
        task_runs[run.id] = i

    submission_duration = time.monotonic() - start

    if iterations % 10 != 0:
        print("Submitted", iterations, "tasks in", submission_duration, "seconds")

    task_results: Counter[StateType] = Counter()
    observed_retries: Counter[UUID] = Counter()
    polling_failures, result_failures = 0, 0

    async with get_client() as client:
        while task_runs:
            await asyncio.sleep(1)

            try:
                runs = await client.read_task_runs(
                    task_run_filter=TaskRunFilter(
                        id=TaskRunFilterId(
                            any_=[id for id in task_runs.keys()],
                        )
                    )
                )
            except Exception as exc:
                print(f"Failed to poll task runs: {exc}")
                polling_failures += 1
                continue

            summary: Counter[StateType] = Counter(
                run.state.type for run in runs if run.state.type not in FINAL_STATES
            )

            for run in runs:
                sequence = task_runs[run.id]

                if "Retry" in run.state.name:
                    observed_retries[run.id] += 1

                if run.state.type == StateType.COMPLETED:
                    result = run.state.result()
                    try:
                        reply, result_sequence = await result.get()
                    except Exception as exc:
                        print(f"Failed to fetch result for task run {sequence}: {exc}")
                        result_failures += 1
                        continue

                    assert (
                        sequence == result_sequence
                    ), f"Expected {sequence}, got {result_sequence}"
                    assert reply == "pong", f"Expected 'pong', got {reply}"

                if run.state.type in FINAL_STATES:
                    task_results[run.state.type] += 1
                    del task_runs[run.id]

            summary_report = ", ".join(
                f"{count} {state.name}" for state, count in sorted(summary.items())
            )
            print(f"{len(task_runs)} task runs remaining, {summary_report}")

    duration = time.monotonic() - start

    print("Submission failures:", submission_failures)
    print("Polling failures:", polling_failures)
    print("Tasks that retried:", len(observed_retries))
    print("Task results:", task_results)
    print("Submission rate:", iterations / submission_duration, "tasks per second")
    print("Total rate:", iterations / duration, "tasks per second")

    havoc.cancel()
    try:
        await havoc
    except asyncio.CancelledError:
        pass


iterations = int(sys.argv[1]) if len(sys.argv) > 1 else 100
asyncio.run(main(iterations))
