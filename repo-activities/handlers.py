from typing import Any

from devtools import debug
from gh_util.types import GitHubWebhookRequest
from marvin.utilities.redis import get_async_redis_client
from prefect import task
from prefect.task_worker import serve
from pydantic import BaseModel


# default handler
async def _default_handler(request: GitHubWebhookRequest) -> GitHubWebhookRequest:
    debug(request.model_dump(exclude_unset=True, exclude_none=True))
    print(f"got {request.headers.event} event for {request.event.repository.full_name}")
    return request


# handlers for specific repositories
HANDLERS = {
    "zzstoatzz/gh": _default_handler,
    "prefecthq/marvin": _default_handler,
    # add more handlers for specific repositories here
}


async def show_result_is_available_via_API(task, task_run, state):
    """the up-to-date `state` object is provided to this state hook
    but you could just as easily use `client.read_task_run(task_run.id)`
    to get the `task_run` object and then `state = task_run.state`
    if you have the task run ID (e.g. `some_task.delay(...).task_run_id`)
    and know that the task run is in a completed state.

    https://docs-3.prefect.io/3.0rc/develop/state-hooks#task-run-state-change-hooks
    """
    from prefect import get_run_logger

    get_run_logger().info(f"Actual result value: {await state.result().get()}")


# repo event handler task
@task(
    log_prints=True,
    task_run_name="Handle {request.headers.event} event for {request.event.repository.full_name}",
    on_completion=[show_result_is_available_via_API],
)
async def handle_repo_request(request: GitHubWebhookRequest) -> Any:
    full_repo_name = request.event.repository.full_name
    request_handler = HANDLERS.get(full_repo_name, _default_handler)
    handler_result = await request_handler(request)
    if isinstance(handler_result, BaseModel) and (
        serialized_result := handler_result.model_dump_json()
    ):
        redis = await get_async_redis_client()
        request_key = (
            f"{full_repo_name}:{request.headers.event}:{request.headers.delivery}"
        )
        await redis.set(request_key, serialized_result)
        print(f"serialized & saved to redis @ {request_key}")

    return handler_result


# serve the main task
if __name__ == "__main__":
    serve(handle_repo_request)
