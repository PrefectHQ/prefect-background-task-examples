import pytest
from fastapi.testclient import TestClient
from fastapi_user_signups import api
from fastapi_user_signups.models import User
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
