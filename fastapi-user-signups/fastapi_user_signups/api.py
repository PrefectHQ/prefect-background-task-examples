# web api imports from tasks
# can post to users endpoint with name and body and then fans out 3 bg tasks
# fire and forget, no dependency on each other
# not prefect not imported
# but needs to be in the env b/c tasks are imported

import fastapi

from . import models, tasks
from .models import NewUser, User

app = fastapi.FastAPI()


@app.post("/users", status_code=201)
async def create_user(new_user: NewUser) -> User:
    user = await models.create_user(new_user)

    # TODO: no reason this shouldn't work, but we get `database is locked` errors on
    # SQLite when we try to run all three tasks concurrently
    # await asyncio.gather(
    #     tasks.send_confirmation_email.submit(user),
    #     tasks.enroll_in_onboarding_flow.submit(user),
    #     tasks.populate_workspace.submit(user),
    # )

    tasks.send_confirmation_email.apply_async(args=(user,))
    tasks.enroll_in_onboarding_flow.apply_async(args=(user,))
    tasks.populate_workspace.apply_async(args=(user,))

    return user
