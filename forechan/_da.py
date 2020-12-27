from asyncio.futures import Future
from asyncio.tasks import FIRST_COMPLETED, wait
from itertools import chain
from typing import Sequence, Tuple, TypeVar

T = TypeVar("T")


async def pure(item: T) -> T:
    return item


async def race(aw: Future[T], *aws: Future[T]) -> Tuple[T, Sequence[Future[T]]]:
    done, pending = await wait(tuple((aw, *aws)), return_when=FIRST_COMPLETED)
    ret = done.pop().result()
    return ret, tuple(chain(done, pending))
