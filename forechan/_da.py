from asyncio import gather
from asyncio.coroutines import iscoroutine
from asyncio.futures import Future
from asyncio.tasks import FIRST_COMPLETED, wait
from itertools import chain
from typing import Awaitable, Sequence, Tuple, TypeVar

from ._sched import go

T = TypeVar("T")


async def pure(item: T) -> T:
    return item


async def race(aw: Awaitable[T], *aws: Awaitable[T]) -> Tuple[T, Sequence[Future[T]]]:
    futs = gather((go(a) if iscoroutine(a) else pure(a) for a in chain((aw,), aws)))
    done, pending = await wait(futs, return_when=FIRST_COMPLETED)
    ret = done.pop().result()
    return ret, tuple(chain(done, pending))
