from asyncio.futures import Future
from asyncio.tasks import FIRST_COMPLETED, create_task, wait
from typing import Awaitable, Set, Tuple, TypeVar

T = TypeVar("T")


async def race(*aws: Awaitable[T]) -> Tuple[T, Set[Future[T]]]:
    futs = tuple(create_task(aw) for aw in aws)
    done, pending = await wait(futs, return_when=FIRST_COMPLETED)
    return done.pop().result(), pending
