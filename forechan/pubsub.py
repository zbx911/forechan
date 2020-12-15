from asyncio.tasks import create_task
from typing import Callable, Optional, Type, TypeVar

from .bufs import SlidingBuf
from .chan import chan
from .types import Chan, ChanClosed

T = TypeVar("T")


def pub(t: Optional[Type[T]]) -> Chan[T]:
    buf = SlidingBuf[T](maxlen=1)
    return chan(t, buf=buf)


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
