from devtools import debug
from prefect import task
from prefect.task_server import serve

from gh_util.types import GitHubWebhookEvent

@task
async def process_event(event: GitHubWebhookEvent) -> None:
    debug(event)

if __name__ == "__main__":    
    serve(process_event)