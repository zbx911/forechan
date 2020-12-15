from asyncio.tasks import create_task
from typing import Callable, TypeVar

from .chan import chan
from .types import Chan, ChanClosed

T = TypeVar("T")


async def sub(predicate: Callable[[T], bool], pub: Chan[T]) -> Chan[T]:
    out: Chan[T] = chan()

    async def cont() -> None:
        async with out:
            while True:
                try:
                    await pub._on_recvable()
                except ChanClosed:
                    break
                else:
                    item = pub.try_peek()
                    if predicate(item):
                        item = pub.try_recv()
                        try:
                            await out.send(item)
                        except ChanClosed:
                            pass
                        break

    create_task(cont())

    return out
