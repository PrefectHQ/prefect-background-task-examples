from uuid import UUID

from flask import Flask, request
from prefect.client.orchestration import get_client
from prefect.client.schemas import TaskRun
from prefect.client.schemas.objects import State, StateType

from .tasks import get_help

app = Flask(__name__)


@app.route("/question", methods=["POST"])
async def ask_question():
    question = request.get_data().decode()
    answer: TaskRun = await get_help.submit(question)
    return "", 202, {"Location": f"/answer/{answer.id}"}


@app.route("/answer/<task_run_id>", methods=["GET"])
async def get_answer(task_run_id: str):
    async with get_client() as client:
        task_run = await client.read_task_run(UUID(task_run_id))

    if not task_run:
        return "", 404

    # avoid shenanigans by making sure that we are only being asked for get_help results
    if task_run.task_key != "flask_task_monitoring.tasks.get_help":
        return "", 404

    if not task_run.state:
        return {"state": "UNKNOWN"}, 404

    state: State = task_run.state

    if state.type == StateType.FAILED:
        return {"state": state.name, "message": state.message}, 500

    if state.type != StateType.COMPLETED:
        return {"state": state.name}, 202

    result = state.result()

    return await result.get(), 200, {"Content-Type": "audio/mp3"}
