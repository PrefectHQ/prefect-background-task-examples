import random
from datetime import timedelta

import marvin
from prefect import task
from prefect.task_server import serve
from prefect.tasks import task_input_hash


@marvin.ai_fn
def answer(question: str) -> str:
    """
    Answer the given `question` in a truthful and helpful way, returning up to two
    lines of dialogue.  If the question includes a compliment, thank the asker in a
    sweet way before answering the question with a little more pep in your step.
    """


@marvin.ai_fn
def retort(question: str) -> str:
    """
    Return a retort to the given `question` in a sarcastic or otherwise unhelpful way,
    and optionally scold the person for being mean.  Definitely do not answer the
    question in any helpful way.
    """


class HostileQuestion(Exception):
    pass


@task(
    # This task will be retried up to 10 times, with a 1 second delay between retries.
    # https://docs.prefect.io/latest/concepts/tasks/#retries
    retries=10,
    retry_delay_seconds=1,
    # Results of this task will be cached for 60 seconds, and the cache key will be
    # determined by the parameters to the task.  This means that if the same question is
    # asked multiple times within a minute, the same results will be returned without
    # making API calls to the LLM.
    cache_key_fn=task_input_hash,
    cache_expiration=timedelta(seconds=60),
)
async def get_help(question: str) -> bytes:
    tone = await marvin.classify_async(question, labels=["nice", "neutral", "hostile"])
    if tone == "hostile":
        reply = retort(question)
    else:
        reply = answer(question)

    if random.random() < 0.2:
        raise ValueError("Randomly failing, this should be retried")

    # return text data response from Marvin
    return reply


if __name__ == "__main__":
    from . import tasks

    serve(tasks.get_help)
