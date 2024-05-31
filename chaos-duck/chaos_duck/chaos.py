import asyncio
import random

import docker
from docker.models.containers import Container

from .tasks import crash_me


async def wreak_havoc():
    while True:
        await asyncio.sleep(random.randint(3, 10))

        if random.random() < 0.05:
            #
            # Agent of chaos #4: randomly restart the Prefect server
            #
            await hard_restart_the_prefect_server()
        elif random.random() < 0.1:
            #
            # Agent of chaos #3: randomly kill a task server
            #
            await kill_a_task_server()
        elif random.random() < 0.2:
            #
            # Agent of chaos #2: send a task to crash the task server
            #
            print("🦆 Sending a crash_me task")
            await crash_me.delay(42)


async def kill_a_task_server():
    client = docker.DockerClient()

    containers: list[Container] = client.containers.list()
    containers = [c for c in client.containers.list() if "chaos-duck-tasks" in c.name]
    if not containers:
        return

    container = random.choice(containers)
    print(f"🦆 Killing {container.name}")
    container.exec_run("kill 1")


async def hard_restart_the_prefect_server():
    client = docker.DockerClient()

    containers: list[Container] = client.containers.list()
    containers = [c for c in client.containers.list() if "chaos-duck-prefect" in c.name]
    if not containers:
        return

    container = random.choice(containers)
    print(f"🦆 Killing {container.name}")
    container.restart(timeout=1)
