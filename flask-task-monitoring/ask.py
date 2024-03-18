import asyncio
import sys
from httpx import AsyncClient


async def ask(question: str):
    async with AsyncClient(base_url="http://localhost:8001") as client:
        response = await client.post("/question", data=question)
        response.raise_for_status()

        assert response.headers["Location"]

        answer_url = response.headers["Location"]

        while True:
            response = await client.get(answer_url)
            response.raise_for_status()

            if response.status_code == 202:
                print("Task is", response.json()["state"])
                await asyncio.sleep(0.25)
                continue
            elif response.status_code == 200:
                print("Completed!")
                break

        assert response.status_code == 200
        print(response.text)


if __name__ == "__main__":
    if len(sys.argv) == 1:
        question = "Tell me that I need to ask a question, please."
    else:
        question = " ".join(sys.argv[1:])

    asyncio.run(ask(question))
