from typing import Generator

import pytest
from fastapi.testclient import TestClient
from fastapi_user_signups import api
from fastapi_user_signups.models import User
from prefect.client.orchestration import PrefectClient, get_client
from prefect.client.schemas import StateType
from prefect.client.schemas.filters import (
    TaskRunFilter,
    TaskRunFilterState,
    TaskRunFilterStateType,
)
from prefect.testing.utilities import prefect_test_harness
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
