from datetime import date

import httpx
import jinja2
from prefect import task
from prefect.task_server import serve

from . import models
from .models import User

mail_templates = jinja2.Environment(enable_async=True)
welcome_mail = mail_templates.from_string(
    """
    Hi {{ user.name }}, welcome to the app!
    """
)


@task
async def send_confirmation_email(user: User) -> None:
    async with httpx.AsyncClient(base_url="http://mailboi") as mailboi:
        response = await mailboi.post(
            "/send-mail",
            json={
                "to": user.email,
                "subject": "Welcome to the app!",
                "body": await welcome_mail.render_async(user=user),
            },
        )
        assert response.status_code == 666


@task
async def enroll_in_onboarding_flow(user: User) -> None:
    async with httpx.AsyncClient(base_url="http://marketito") as onboarding:
        response = await onboarding.post(
            "/enroll-user",
            json={
                "flow": "onboarding",
                "user_id": str(user.id),
                "email": user.email,
                "name": user.name,
                "start_date": date.today().isoformat(),
            },
        )
        assert response.status_code == 666


@task
async def populate_workspace(user: User) -> None:
    user = await models.read_user(user.id)
    for i in range(10):
        await models.add_thing_to_user_workspace(user, f"thing-{i}")


if __name__ == "__main__":
    serve(
        send_confirmation_email,
        enroll_in_onboarding_flow,
        populate_workspace,
    )
