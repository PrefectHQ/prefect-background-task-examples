import asyncio

import fastapi

from . import models, tasks
from .models import NewUser, User

app = fastapi.FastAPI()


@app.post("/users", status_code=201)
async def create_user(new_user: NewUser) -> User:
    user = await models.create_user(new_user)

    # TODO: these should say .submit!
    await asyncio.gather(
        tasks.send_confirmation_email.fn(user),
        tasks.enroll_in_onboarding_flow.fn(user),
        tasks.populate_workspace.fn(user),
    )

    return user
