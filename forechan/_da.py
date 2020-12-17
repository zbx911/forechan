from asyncio.coroutines import iscoroutine
from asyncio.futures import Future
from asyncio.tasks import FIRST_COMPLETED, create_task, wait
from itertools import chain
from typing import Awaitable, Sequence, Tuple, TypeVar

T = TypeVar("T")


async def race(aw: Awaitable[T], *aws: Awaitable[T]) -> Tuple[T, Sequence[Future[T]]]:
    futs = tuple(create_task(a) if iscoroutine(a) else a for a in chain((aw,), aws))
    done, pending = await wait(futs, return_when=FIRST_COMPLETED)
    ret = done.pop().result()
    return ret, tuple(chain(done, pending))
