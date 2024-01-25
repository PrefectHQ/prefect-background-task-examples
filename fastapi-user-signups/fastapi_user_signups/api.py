import asyncio

import fastapi

from . import models, tasks
from .models import NewUser, User

app = fastapi.FastAPI()


@app.post("/users", status_code=201)
async def create_user(new_user: NewUser) -> User:
    user = await models.create_user(new_user)

    await asyncio.gather(
        tasks.send_confirmation_email.submit(user),
        tasks.enroll_in_onboarding_flow.submit(user),
        tasks.populate_workspace.submit(user),
    )

    return user
