import json
from datetime import date
from typing import Generator

import pytest
from fastapi.testclient import TestClient
from fastapi_user_signups import api, models, tasks
from fastapi_user_signups.models import User
from prefect.client.orchestration import PrefectClient, get_client
from prefect.client.schemas import StateType
from prefect.client.schemas.filters import (
    TaskRunFilter,
    TaskRunFilterState,
    TaskRunFilterStateType,
)
from prefect.task_server import TaskServer
from prefect.testing.utilities import prefect_test_harness
from pytest_httpx import HTTPXMock
from starlette.types import ASGIApp


@pytest.fixture
def app() -> ASGIApp:
    return api.app


@pytest.fixture
def client(app: ASGIApp) -> TestClient:
    return TestClient(app)


def test_creating_user_works(client: TestClient) -> None:
    response = client.post(
        "/users",
        json={"email": "foo@example.com", "name": "Foo Bar"},
    )
    assert response.status_code == 201
    user = User.model_validate(response.json())
    assert user.id
    assert user.email == "foo@example.com"
    assert user.name == "Foo Bar"
    assert user.is_active
    assert not user.is_superuser


@pytest.fixture
def prefect() -> Generator[PrefectClient, None, None]:
    with prefect_test_harness():
        yield get_client()


async def test_creating_user_schedules_onboarding_tasks(
    client: TestClient, prefect: PrefectClient
) -> None:
    response = client.post(
        "/users",
        json={"email": "foo@example.com", "name": "Foo Bar"},
    )
    assert response.status_code == 201

    task_runs = await prefect.read_task_runs(
        task_run_filter=TaskRunFilter(
            state=TaskRunFilterState(
                type=TaskRunFilterStateType(any_=[StateType.SCHEDULED])
            )
        )
    )
    assert len(task_runs) == 3

    assert {t.task_key for t in task_runs} == {
        "fastapi_user_signups.tasks.enroll_in_onboarding_flow",
        "fastapi_user_signups.tasks.populate_workspace",
        "fastapi_user_signups.tasks.send_confirmation_email",
    }, "Each of the onboarding tasks should be scheduled"


@pytest.fixture
async def onboarding_task_server(
    prefect: PrefectClient,
) -> Generator[TaskServer, None, None]:
    return TaskServer(
        tasks.enroll_in_onboarding_flow,
        tasks.populate_workspace,
        tasks.send_confirmation_email,
    )


@pytest.fixture
async def new_user(client: TestClient, prefect: PrefectClient) -> User:
    response = client.post(
        "/users",
        json={"email": "foo@example.com", "name": "Foo Bar"},
    )
    assert response.status_code == 201
    user = User.model_validate(response.json())
    return user


async def test_user_signup_populates_workspace(
    new_user: User, onboarding_task_server: TaskServer
):
    workspace_things = await models.get_things_in_user_workspace(new_user)
    assert len(workspace_things) == 0

    await onboarding_task_server.run_once()

    workspace_things = await models.get_things_in_user_workspace(new_user)
    assert len(workspace_things) == 10


async def test_user_signup_sends_confirmation_email(
    new_user: User, onboarding_task_server: TaskServer, httpx_mock: HTTPXMock
):
    httpx_mock.add_response(url="http://mailboi/send-mail", status_code=666)

    await onboarding_task_server.run_once()

    request = httpx_mock.get_request(url="http://mailboi/send-mail")
    assert request

    assert json.loads(request.content) == {
        "to": new_user.email,
        "subject": "Welcome to the app!",
        "body": "\nHi Foo Bar, welcome to the app!",
    }


async def test_user_signup_enrolls_user_in_onboarding_flow(
    new_user: User, onboarding_task_server: TaskServer, httpx_mock: HTTPXMock
):
    httpx_mock.add_response(url="http://marketito/enroll-user", status_code=666)

    await onboarding_task_server.run_once()

    request = httpx_mock.get_request(url="http://marketito/enroll-user")
    assert request

    assert json.loads(request.content) == {
        "flow": "onboarding",
        "user_id": str(new_user.id),
        "email": "foo@example.com",
        "name": "Foo Bar",
        "start_date": date.today().isoformat(),
    }
