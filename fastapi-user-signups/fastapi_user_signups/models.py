# just example, don't need redis for prefect tasks etc.

from uuid import UUID, uuid4

from pydantic import BaseModel, Field
from redis.asyncio import StrictRedis


class User(BaseModel):
    id: UUID
    email: str
    name: str
    is_active: bool = Field(default=True)
    is_superuser: bool


class NewUser(BaseModel):
    email: str
    name: str


async def read_user(user_id: UUID) -> User:
    async with StrictRedis(host="redis") as redis:
        user_json = await redis.get(f"user:{user_id}")
    if not user_json:
        raise ValueError(f"User {user_id} not found")
    return User.model_validate_json(user_json)


async def create_user(new_user: NewUser) -> User:
    user = User(
        id=uuid4(),
        email=new_user.email,
        name=new_user.name,
        is_active=True,
        is_superuser=False,
    )

    async with StrictRedis(host="redis") as redis:
        async with redis.pipeline() as p:
            p.set(f"user:{user.id}", user.model_dump_json())
            p.sadd("users", str(user.id))
            await p.execute()

    return user


async def add_thing_to_user_workspace(user: User, thing: str) -> None:
    async with StrictRedis(host="redis") as redis:
        await redis.sadd(f"user:{user.id}:workspace", thing)


async def get_things_in_user_workspace(user: User) -> set[str]:
    async with StrictRedis(host="redis") as redis:
        return await redis.smembers(f"user:{user.id}:workspace")
