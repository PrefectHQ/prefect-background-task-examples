# web api imports from tasks
# can post to users endpoint with name and body and then fans out 3 bg tasks
# fire and forget, no dependency on each other
# not prefect not imported
# but needs to be in the env b/c tasks are imported

import asyncio

import fastapi

from . import models, tasks
from .models import NewUser, User

app = fastapi.FastAPI()


@app.post("/users", status_code=201)
async def create_user(new_user: NewUser) -> User:
    user = await models.create_user(new_user)

    await asyncio.gather(
        tasks.send_confirmation_email.delay(user),
        tasks.enroll_in_onboarding_flow.delay(user),
        tasks.populate_workspace.delay(user),
    )

    return user
