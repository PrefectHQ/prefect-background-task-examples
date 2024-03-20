from uuid import UUID

from flask import Flask, request
from prefect.client.orchestration import get_client
from prefect.client.schemas import TaskRun
from prefect.client.schemas.objects import State, StateType

from prefect.results import PersistedResult

from .tasks import get_help

app = Flask(__name__)


@app.route("/question", methods=["POST"])
async def ask_question():
    question = request.get_data().decode()

    # When a user asks a question, we submit a task to the Prefect API with Task.submit
    # in the same way that we would submit a task from a Prefect Flow.  In this case,
    # the return value will be an instance of a client-side `TaskRun` rather than a
    # `PrefectFuture`.  See https://docs.prefect.io/latest/concepts/tasks/#task-results
    # for a discussion of task results and submission.
    #
    # It's important to note the parameters you pass here will never be transmitted via
    # the Prefect API.  Instead, they are stored in the common result storage area that
    # the application and task servers share (in this example application, that is a
    # filesystem path).
    answer: TaskRun = await get_help.submit(question)

    # The ID of the task run is what we'll need to check the status of the task later,
    # so return it to the caller.  In other applications, you may store this ID in your
    # database along with other application objects.  This ID is not transient and will
    # exist on the Prefect API until the task run is deleted (either manually or via
    # the retention policies on Prefect Cloud).
    return "", 202, {"Location": f"/answer/{answer.id}"}


@app.route("/answer/<task_run_id>", methods=["GET"])
async def get_answer(task_run_id: str):
    async with get_client() as client:
        task_run = await client.read_task_run(UUID(task_run_id))

    # It's always possible that a task run has been removed
    if not task_run:
        return "", 404

    # Here we avoid shenanigans by making sure that we are only being asked for
    # the result of a `get_help` task run.  This is just a safety check to make sure
    # that the caller is not able to access the result of arbitrary task runs.  The
    # task_key of the task will correspond to the fully-qualified Python name of the
    # task function.
    if task_run.task_key != get_help.task_key:
        return "", 404

    state: State = task_run.state
    assert state

    # A task run may be in one of several states.  When it is first submitted, it will
    # be in a `SCHEDULED` state.  It will then transition to a `PENDING` state when a
    # `TaskServer` has received it (or `CRASHED` if something went wrong at this point)
    # The run will then move on to `RUNNING` while it is executing, arriving in the
    # final state of `COMPLETED` or `FAILED`.  If you are using
    # task retries (https://docs.prefect.io/latest/concepts/tasks/#retries), you may
    # see `FAILED` tasks transition back to `PENDING` as they are retried.

    if state.type == StateType.FAILED:
        return {"state": state.name, "message": state.message}, 500

    if state.type != StateType.COMPLETED:
        return {"state": state.name}, 202

    # If the task run has completed, we can retrieve the result from the common storage
    # that the application and task servers share (in this example application, that is
    # a filesystem path).  The result is a `PersistedResult` object, which exposes
    # access to the result data.
    #
    # As with task parameters, it's important to note that the result data will never
    # be stored or seen by the Prefect API.
    result: PersistedResult = state.result()

    return await result.get(), 200, {"Content-Type": "application/text"}
