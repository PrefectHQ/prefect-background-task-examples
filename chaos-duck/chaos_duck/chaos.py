import asyncio
import random
from collections import defaultdict

import docker
from docker.models.containers import Container

from .tasks import crash_me

agents_of_chaos = []
scoreboard = defaultdict(int)


def agent_of_chaos(probability: float):
    def decorator(fn):
        agents_of_chaos.append(fn)
        fn.__annotations__.setdefault("probability", probability)
        return fn

    return decorator


async def wreak_havoc():
    while True:
        await asyncio.sleep(random.randint(1, 5))
        for agent in agents_of_chaos:
            if random.random() < agent.__annotations__.get("probability", 0.1):
                scoreboard[agent] += 1
                await agent()


@agent_of_chaos(probability=0.2)
async def send_a_crash_me_task():
    print("🦆 Sending a crash_me task")
    await crash_me.delay(42).wait_async()


@agent_of_chaos(probability=0.1)
async def kill_a_task_worker():
    client = docker.DockerClient()

    containers: list[Container] = client.containers.list()
    containers = [c for c in client.containers.list() if "chaos-duck-tasks" in c.name]
    if not containers:
        return

    container = random.choice(containers)
    print(f"🦆 Killing {container.name}")
    container.exec_run("kill 1")


@agent_of_chaos(probability=0.05)
async def hard_restart_the_prefect_server():
    client = docker.DockerClient()

    containers: list[Container] = client.containers.list()
    containers = [c for c in client.containers.list() if "chaos-duck-prefect" in c.name]
    if not containers:
        return

    container = random.choice(containers)
    print(f"🦆 Killing {container.name}")
    container.restart(timeout=1)
