from asyncio.futures import Future
from asyncio.tasks import FIRST_COMPLETED, create_task, wait
from itertools import chain
from typing import Awaitable, Set, Tuple, TypeVar

T = TypeVar("T")


async def race(aw: Awaitable[T], *aws: Awaitable[T]) -> Tuple[T, Set[Future[T]]]:
    futs = (create_task(aw) for aw in chain((aw,), aws))
    done, pending = await wait(futs, return_when=FIRST_COMPLETED)
    return done.pop().result(), pending
